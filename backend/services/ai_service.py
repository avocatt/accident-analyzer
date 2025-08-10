import os
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from datetime import datetime
import openai
from openai import OpenAI
import asyncio

from models.analysis_result import (
    AnalysisResult, PartyInfo, AccidentDetails, 
    FaultAssessment, FormCheckboxes, PhotoAnalysis
)


class AIService:
    """
    Service for interacting with OpenAI GPT-4o for document analysis
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o"  # Using GPT-4o for multimodal capabilities
        
        # Load master prompt
        prompt_path = os.path.join(os.path.dirname(__file__), "../prompts/master_prompt.txt")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.master_prompt = f.read()
    
    async def analyze_accident(
        self, 
        report_content: Dict[str, Any],
        photo_contents: List[Dict[str, Any]],
        additional_context: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """
        Analyze accident report and photos using GPT-4o
        """
        try:
            # Prepare messages for API call
            messages = self._prepare_messages(report_content, photo_contents, additional_context)
            
            # Make API call with retry logic
            response = await self._call_openai_with_retry(messages)
            
            # Parse the response
            analysis_result = self._parse_ai_response(response, additional_context)
            
            return analysis_result
            
        except Exception as e:
            raise Exception(f"AI analysis failed: {str(e)}")
    
    def _prepare_messages(
        self,
        report_content: Dict[str, Any],
        photo_contents: List[Dict[str, Any]],
        additional_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Prepare messages for OpenAI API call
        """
        messages = [
            {
                "role": "system",
                "content": self.master_prompt
            }
        ]
        
        # Prepare content array for user message
        content_parts = []
        
        # Add context if provided
        if additional_context:
            context_text = "Additional Context:\n"
            if additional_context.get("client_name"):
                context_text += f"Client Name: {additional_context['client_name']}\n"
            if additional_context.get("additional_notes"):
                context_text += f"Notes: {additional_context['additional_notes']}\n"
            content_parts.append({"type": "text", "text": context_text})
        
        # Add main report content
        if report_content["type"] == "pdf":
            # Add text content if available
            if report_content.get("text_content"):
                content_parts.append({
                    "type": "text",
                    "text": f"Extracted text from PDF:\n{report_content['text_content'][:3000]}"
                })
            
            # Add page images
            for page_data in report_content.get("page_images", [])[:2]:  # Limit to first 2 pages
                content_parts.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{page_data['mime_type']};base64,{page_data['base64']}"
                    }
                })
        elif report_content["type"] == "image":
            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{report_content['mime_type']};base64,{report_content['base64']}"
                }
            })
        
        # Add photo contents
        for idx, photo in enumerate(photo_contents[:5]):  # Limit to 5 photos
            content_parts.append({
                "type": "text",
                "text": f"\nPhoto {idx + 1}:"
            })
            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{photo['mime_type']};base64,{photo['base64']}"
                }
            })
        
        messages.append({
            "role": "user",
            "content": content_parts
        })
        
        return messages
    
    async def _call_openai_with_retry(self, messages: List[Dict[str, Any]], max_retries: int = 3):
        """
        Call OpenAI API with retry logic
        """
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=4000,
                    temperature=0.1,  # Low temperature for consistent extraction
                    response_format={"type": "text"}
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    def _parse_ai_response(self, response_text: str, additional_context: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """
        Parse the XML response from AI into AnalysisResult model
        """
        try:
            # Extract XML content
            xml_start = response_text.find("<analysis>")
            xml_end = response_text.find("</analysis>") + len("</analysis>")
            
            if xml_start == -1 or xml_end == -1:
                raise ValueError("Invalid XML response format")
            
            xml_content = response_text[xml_start:xml_end]
            root = ET.fromstring(xml_content)
            
            # Helper function to get text safely
            def get_text(element, path, default=""):
                elem = element.find(path)
                return elem.text if elem is not None and elem.text else default
            
            # Parse party information with new fields
            party_a = PartyInfo(
                name=get_text(root, "parties/party_a/name", "Unknown"),
                id_number=get_text(root, "parties/party_a/tc_kimlik"),
                driver_license=get_text(root, "parties/party_a/license_no"),
                vehicle_plate=get_text(root, "parties/party_a/vehicle_plate", "Unknown"),
                vehicle_type=get_text(root, "parties/party_a/vehicle_model", "Unknown"),
                insurance_company=get_text(root, "parties/party_a/insurance_company"),
                insurance_policy=get_text(root, "parties/party_a/policy_no")
            )
            
            party_b = PartyInfo(
                name=get_text(root, "parties/party_b/name", "Unknown"),
                id_number=get_text(root, "parties/party_b/tc_kimlik"),
                driver_license=get_text(root, "parties/party_b/license_no"),
                vehicle_plate=get_text(root, "parties/party_b/vehicle_plate", "Unknown"),
                vehicle_type=get_text(root, "parties/party_b/vehicle_model", "Unknown"),
                insurance_company=get_text(root, "parties/party_b/insurance_company"),
                insurance_policy=get_text(root, "parties/party_b/policy_no")
            )
            
            # Parse accident details with location subfields
            location_elem = root.find("accident_details/location")
            if location_elem is not None:
                location_text = f"{get_text(location_elem, 'il')} {get_text(location_elem, 'ilce')} {get_text(location_elem, 'mahalle_cadde_sokak')}"
            else:
                location_text = get_text(root, "accident_details/location", "Unknown")
                
            accident_details = AccidentDetails(
                date=get_text(root, "accident_details/date", "Unknown"),
                time=get_text(root, "accident_details/time", "Unknown"),
                location=location_text.strip() if location_text.strip() else "Unknown",
                weather_conditions=get_text(root, "accident_details/conditions")
            )
            
            # Parse form checkboxes with updated section numbers
            form_checkboxes = FormCheckboxes(
                section_12_selections=self._parse_checkbox_text(get_text(root, "form_analysis/section_7_checkboxes_a")),
                section_13_selections=self._parse_checkbox_text(get_text(root, "form_analysis/section_7_checkboxes_b")),
                section_14_initial_impact=get_text(root, "form_analysis/section_9_damage_diagram"),
                section_15_visible_damages=[get_text(root, "form_analysis/section_10_scene_sketch")],
                section_16_observations=self._parse_driver_statements(get_text(root, "form_analysis/section_11_driver_statements"))
            )
            
            # Parse fault assessment
            fault_assessment = FaultAssessment(
                preliminary_fault_party=get_text(root, "fault_assessment/preliminary_fault_party"),
                fault_indicators=[get_text(root, "fault_assessment/fault_indicators")],
                contested_points=[get_text(root, "legal_analysis/contested_points")]
            )
            
            # Parse percentages if available
            percentages_text = get_text(root, "fault_assessment/estimated_percentages")
            if percentages_text:
                # Try to extract percentages from text
                import re
                numbers = re.findall(r'\d+', percentages_text)
                if len(numbers) >= 2:
                    fault_assessment.party_a_fault_percentage = int(numbers[0])
                    fault_assessment.party_b_fault_percentage = int(numbers[1])
            
            # Parse photo analyses
            photo_analyses = []
            photo_findings = root.find("photo_findings")
            if photo_findings:
                for idx, photo_elem in enumerate(photo_findings):
                    if photo_elem.text:
                        photo_analyses.append(PhotoAnalysis(
                            photo_id=idx + 1,
                            description=photo_elem.text,
                            consistency_with_report=True
                        ))
            
            # Parse legal considerations
            legal_considerations = []
            recommendations_text = get_text(root, "legal_analysis/recommendations")
            if recommendations_text:
                legal_considerations = [rec.strip() for rec in recommendations_text.split(",")]
            
            # Parse data quality
            missing_info_text = get_text(root, "data_quality/missing_information")
            missing_information = [info.strip() for info in missing_info_text.split(",") if info.strip()]
            
            confidence_text = get_text(root, "data_quality/extraction_confidence", "0.8")
            try:
                extraction_confidence = float(confidence_text.strip('%')) / 100 if '%' in confidence_text else float(confidence_text)
            except:
                extraction_confidence = 0.8
            
            # Create analysis result
            result = AnalysisResult(
                session_id=additional_context.get("session_id", str(datetime.now().timestamp())),
                analysis_timestamp=datetime.utcnow(),
                case_summary=get_text(root, "case_summary", "Analysis completed"),
                party_a=party_a,
                party_b=party_b,
                accident_details=accident_details,
                form_checkboxes=form_checkboxes,
                fault_assessment=fault_assessment,
                photo_analyses=photo_analyses,
                legal_considerations=legal_considerations,
                recommended_actions=legal_considerations,
                extraction_confidence=extraction_confidence,
                missing_information=missing_information,
                raw_ai_response={"response": response_text[:1000]}  # Store truncated for debugging
            )
            
            return result
            
        except Exception as e:
            # Fallback to basic result if parsing fails
            return AnalysisResult(
                session_id=additional_context.get("session_id", str(datetime.now().timestamp())),
                analysis_timestamp=datetime.utcnow(),
                case_summary="Analysis completed with parsing errors",
                party_a=PartyInfo(name="Parse Error", vehicle_plate="Unknown", vehicle_type="Unknown"),
                party_b=PartyInfo(name="Parse Error", vehicle_plate="Unknown", vehicle_type="Unknown"),
                accident_details=AccidentDetails(date="Unknown", time="Unknown", location="Unknown"),
                form_checkboxes=FormCheckboxes(),
                fault_assessment=FaultAssessment(),
                extraction_confidence=0.5,
                missing_information=["Parsing error occurred"],
                raw_ai_response={"error": str(e), "response": response_text[:500]}
            )
    
    def _parse_numbers(self, text: str) -> List[int]:
        """
        Extract numbers from text
        """
        if not text:
            return []
        
        import re
        numbers = re.findall(r'\d+', text)
        return [int(n) for n in numbers]
    
    def _parse_checkbox_text(self, text: str) -> List[int]:
        """
        Parse checkbox descriptions or numbers from Section 7
        """
        if not text:
            return []
        
        # Map Turkish checkbox descriptions to numbers if needed
        checkbox_map = {
            "kırmızı ışık": 1,
            "taşıt girmesi yasağı": 2,
            "karşı yönden": 3,
            "geçme yasağı": 4,
            "öncelik": 5,
            "sağından gitmeme": 6,
            "arkadan": 7,
            "şerit değiştir": 8,
            "geri manevra": 9,
            "geçiş önceliği": 10,
            "park": 11,
            "durakla": 12,
        }
        
        # First try to extract numbers directly
        numbers = self._parse_numbers(text)
        if numbers:
            return numbers
            
        # Otherwise try to match keywords
        found_items = []
        text_lower = text.lower()
        for key, value in checkbox_map.items():
            if key in text_lower:
                found_items.append(value)
        
        return found_items
    
    def _parse_driver_statements(self, text: str) -> List[str]:
        """
        Parse driver statements from Section 11
        """
        if not text:
            return []
        
        # Split by common delimiters
        statements = []
        if "Driver A:" in text and "Driver B:" in text:
            parts = text.split("Driver B:")
            if len(parts) > 0:
                driver_a = parts[0].replace("Driver A:", "").strip()
                if driver_a:
                    statements.append(f"Driver A: {driver_a}")
            if len(parts) > 1:
                driver_b = parts[1].strip()
                if driver_b:
                    statements.append(f"Driver B: {driver_b}")
        elif text.strip():
            statements.append(text.strip())
            
        return statements