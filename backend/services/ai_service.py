import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from openai import OpenAI
import asyncio

from models.analysis_result import (
    AnalysisResult, PartyInfo, AccidentDetails, 
    FaultAssessment, FormCheckboxes, PhotoAnalysis
)


class AIService:
    """
    Service for interacting with OpenAI GPT-5 for document analysis using the new Responses API
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-5"  # Using GPT-5 flagship model
        
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
        Analyze accident report and photos using GPT-5 with Responses API
        """
        try:
            # Prepare input for API call
            input_content = self._prepare_input(report_content, photo_contents, additional_context)
            
            # Make API call with Pydantic model for structured output
            response = await self._call_openai_with_structured_output(input_content, additional_context)
            
            return response
            
        except Exception as e:
            raise Exception(f"AI analysis failed: {str(e)}")
    
    def _prepare_input(
        self,
        report_content: Dict[str, Any],
        photo_contents: List[Dict[str, Any]],
        additional_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Prepare input for OpenAI Responses API call with new format
        """
        input_messages = []
        
        # Add system message with master prompt
        input_messages.append({
            "role": "system",
            "content": self.master_prompt
        })
        
        # Prepare user message content array
        user_content = []
        
        # Add context if provided
        if additional_context:
            context_text = "Additional Context:\n"
            if additional_context.get("client_name"):
                context_text += f"Client Name: {additional_context['client_name']}\n"
            if additional_context.get("additional_notes"):
                context_text += f"Notes: {additional_context['additional_notes']}\n"
            user_content.append({"type": "input_text", "text": context_text})
        
        # Add main report content with new input format
        if report_content["type"] == "pdf":
            # Add extracted text if available
            if report_content.get("text_content"):
                user_content.append({
                    "type": "input_text",
                    "text": f"Extracted text from PDF:\n{report_content['text_content'][:3000]}"
                })
            
            # Add page images with new format
            for page_data in report_content.get("page_images", [])[:2]:  # Limit to first 2 pages
                user_content.append({
                    "type": "input_image",
                    "image_url": f"data:{page_data['mime_type']};base64,{page_data['base64']}"
                })
        elif report_content["type"] == "image":
            user_content.append({
                "type": "input_image",
                "image_url": f"data:{report_content['mime_type']};base64,{report_content['base64']}"
            })
        
        # Add photo contents with new format
        for idx, photo in enumerate(photo_contents[:5]):  # Limit to 5 photos
            user_content.append({
                "type": "input_text",
                "text": f"\nPhoto {idx + 1}:"
            })
            user_content.append({
                "type": "input_image",
                "image_url": f"data:{photo['mime_type']};base64,{photo['base64']}"
            })
        
        input_messages.append({
            "role": "user",
            "content": user_content
        })
        
        return input_messages
    
    async def _call_openai_with_structured_output(
        self, 
        input_messages: List[Dict[str, Any]], 
        additional_context: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ) -> AnalysisResult:
        """
        Call OpenAI Responses API with Pydantic structured output
        """
        for attempt in range(max_retries):
            try:
                # Use the new parse method with Pydantic model directly
                response = self.client.beta.chat.completions.parse(
                    model=self.model,
                    messages=input_messages,
                    response_format=AnalysisResult,
                    reasoning_effort="high",  # Maximum reasoning for legal analysis
                    temperature=0.1,  # Low temperature for consistent extraction
                    max_completion_tokens=8000  # Increased for high verbosity
                )
                
                # Check for refusal
                if response.choices[0].message.refusal:
                    raise Exception(f"Model refused: {response.choices[0].message.refusal}")
                
                # Get parsed result directly
                analysis_result = response.choices[0].message.parsed
                
                # Set session ID and timestamp
                if analysis_result:
                    analysis_result.session_id = additional_context.get("session_id", str(datetime.now().timestamp()))
                    analysis_result.analysis_timestamp = datetime.utcnow()
                    
                    # Set default confidence if not provided
                    if not analysis_result.extraction_confidence:
                        analysis_result.extraction_confidence = 0.95
                
                return analysis_result
                
            except Exception as e:
                if attempt == max_retries - 1:
                    # On final attempt, return a fallback result
                    return self._create_fallback_result(str(e), additional_context)
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    def _create_fallback_result(self, error_message: str, additional_context: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """
        Create a fallback result when API call fails
        """
        return AnalysisResult(
            session_id=additional_context.get("session_id", str(datetime.now().timestamp())),
            analysis_timestamp=datetime.utcnow(),
            case_summary=f"Analysis failed: {error_message}",
            party_a=PartyInfo(
                name="Error - Unable to extract",
                vehicle_plate="Unknown",
                vehicle_type="Unknown"
            ),
            party_b=PartyInfo(
                name="Error - Unable to extract",
                vehicle_plate="Unknown",
                vehicle_type="Unknown"
            ),
            accident_details=AccidentDetails(
                date="Unknown",
                time="Unknown",
                location="Unknown"
            ),
            form_checkboxes=FormCheckboxes(),
            fault_assessment=FaultAssessment(),
            extraction_confidence=0.0,
            missing_information=["Complete analysis failed"],
            data_inconsistencies=[error_message]
        )