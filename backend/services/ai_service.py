import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from openai import OpenAI

from models.analysis_result import (
    AnalysisResult, PartyInfo, AccidentDetails, 
    FaultAssessment, FormCheckboxes, PhotoAnalysis
)


class AIService:
    """
    Service for interacting with OpenAI GPT-5 for document analysis using the Responses API
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-5"  # Using GPT-5 with Responses API
        
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
        Prepare input for GPT-5 Responses API call
        """
        # GPT-5 Responses API uses a different format - array of message objects
        input_messages = []
        
        # Add developer message with master prompt (system instructions)
        input_messages.append({
            "role": "developer",
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
        
        # Add main report content
        if report_content["type"] == "pdf":
            # Add extracted text if available
            if report_content.get("text_content"):
                user_content.append({
                    "type": "input_text",
                    "text": f"Extracted text from PDF:\n{report_content['text_content'][:3000]}"
                })
            
            # Add page images
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
        
        # Add additional photos
        for idx, photo in enumerate(photo_contents[:5]):  # Limit to 5 photos
            user_content.append({
                "type": "input_text",
                "text": f"Photo {idx + 1}:"
            })
            user_content.append({
                "type": "input_image",
                "image_url": f"data:{photo['mime_type']};base64,{photo['base64']}"
            })
        
        # Add the main analysis request
        user_content.append({
            "type": "input_text",
            "text": "Please analyze this Turkish traffic accident report and provide a structured analysis in the required format."
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
        Call GPT-5 Responses API with guaranteed structured output
        """
        for attempt in range(max_retries):
            try:
                # Use GPT-5 Responses API with structured outputs
                response = self.client.responses.parse(
                    model=self.model,
                    input=input_messages,
                    reasoning={"effort": "high"},  # High reasoning for legal analysis
                    text={"verbosity": "medium"},  # Medium verbosity for detailed analysis
                    text_format=AnalysisResult     # Pydantic model for guaranteed structure
                )
                
                # Get the parsed structured output directly
                if hasattr(response, 'output_parsed') and response.output_parsed:
                    analysis_result = response.output_parsed
                    
                    # Set session ID and timestamp
                    analysis_result.session_id = additional_context.get("session_id", str(datetime.now().timestamp()))
                    analysis_result.analysis_timestamp = datetime.utcnow()
                    
                    # Set default confidence if not provided
                    if not hasattr(analysis_result, 'extraction_confidence') or not analysis_result.extraction_confidence:
                        analysis_result.extraction_confidence = 0.95
                    
                    return analysis_result
                
                # Check for refusal
                if hasattr(response, 'output') and response.output:
                    for output_item in response.output:
                        if hasattr(output_item, 'content'):
                            for content_item in output_item.content:
                                if hasattr(content_item, 'type') and content_item.type == 'refusal':
                                    # Model refused to respond - create a proper response indicating this
                                    return AnalysisResult(
                                        session_id=additional_context.get("session_id", str(datetime.now().timestamp())),
                                        analysis_timestamp=datetime.utcnow(),
                                        case_summary=f"Analysis could not be completed: {content_item.refusal}",
                                        party_a=PartyInfo(name="Unable to extract", vehicle_plate="N/A", vehicle_type="N/A"),
                                        party_b=PartyInfo(name="Unable to extract", vehicle_plate="N/A", vehicle_type="N/A"),
                                        accident_details=AccidentDetails(date="Unknown", time="Unknown", location="Unknown"),
                                        form_checkboxes=FormCheckboxes(),
                                        fault_assessment=FaultAssessment(),
                                        extraction_confidence=0.0,
                                        missing_information=["Valid Turkish traffic accident report required"],
                                        data_inconsistencies=["Model refusal or invalid input provided"]
                                    )
                
                # If no valid structured output found, raise an error
                raise Exception("GPT-5 did not return valid structured output")
                
            except Exception as e:
                print(f"GPT-5 API call attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(f"GPT-5 API failed after {max_retries} attempts: {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
