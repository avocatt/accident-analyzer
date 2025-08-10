from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class PartyInfo(BaseModel):
    name: str
    id_number: Optional[str] = None
    driver_license: Optional[str] = None
    vehicle_plate: str
    vehicle_type: str
    insurance_company: Optional[str] = None
    insurance_policy: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class AccidentDetails(BaseModel):
    date: str
    time: str
    location: str
    weather_conditions: Optional[str] = None
    road_conditions: Optional[str] = None
    visibility: Optional[str] = None
    traffic_signs: Optional[List[str]] = []
    speed_limit: Optional[str] = None


class FaultAssessment(BaseModel):
    party_a_fault_percentage: Optional[int] = None
    party_b_fault_percentage: Optional[int] = None
    preliminary_fault_party: Optional[str] = None
    fault_indicators: List[str] = []
    contested_points: List[str] = []


class FormCheckboxes(BaseModel):
    section_12_selections: List[int] = []  # Araç hasar bölgeleri
    section_13_selections: List[int] = []  # Kaza şekilleri
    section_14_initial_impact: Optional[str] = None
    section_15_visible_damages: List[str] = []
    section_16_observations: List[str] = []


class PhotoAnalysis(BaseModel):
    photo_id: int
    description: str
    relevant_damages: List[str] = []
    consistency_with_report: bool = True
    notes: Optional[str] = None


class AnalysisResult(BaseModel):
    session_id: str
    analysis_timestamp: datetime
    
    # Case summary
    case_summary: str
    
    # Extracted party information
    party_a: PartyInfo
    party_b: PartyInfo
    
    # Accident details
    accident_details: AccidentDetails
    
    # Form analysis
    form_checkboxes: FormCheckboxes
    
    # Fault assessment
    fault_assessment: FaultAssessment
    
    # Photo analysis
    photo_analyses: List[PhotoAnalysis] = []
    
    # Additional findings
    witness_statements: List[str] = []
    police_notes: Optional[str] = None
    
    # Legal considerations
    legal_considerations: List[str] = []
    recommended_actions: List[str] = []
    
    # Data quality
    extraction_confidence: float = 0.0  # 0-1 scale
    missing_information: List[str] = []
    data_inconsistencies: List[str] = []
    
    # Raw AI response (for debugging)
    raw_ai_response: Optional[Dict[Any, Any]] = None