"""
Pydantic Models for Free Report Viewer
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class CareType(str, Enum):
    """Care Type Enum"""
    RESIDENTIAL = "residential"
    NURSING = "nursing"
    DEMENTIA = "dementia"
    RESPITE = "respite"


class QuestionnaireResponse(BaseModel):
    """Questionnaire Response Model"""
    postcode: str = Field(..., description="Postcode")
    budget: Optional[float] = Field(None, ge=0, description="Weekly budget in GBP")
    care_type: Optional[CareType] = Field(None, description="Type of care needed")
    chc_probability: Optional[float] = Field(None, ge=0, le=100, description="CHC probability percentage")
    
    # Additional optional fields
    address: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class CareHome(BaseModel):
    """Care Home Model"""
    name: str
    address: str
    postcode: str
    city: Optional[str] = None
    weekly_cost: float = Field(..., ge=0, description="Weekly cost in GBP")
    care_types: List[str] = Field(default_factory=list)
    rating: Optional[str] = None
    distance_km: Optional[float] = Field(None, ge=0, description="Distance in kilometers")
    features: Optional[List[str]] = Field(default_factory=list)
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    # New fields for matching
    band: Optional[int] = Field(None, ge=1, le=5, description="Price band (1-5)")
    photo_url: Optional[str] = Field(None, description="Photo URL from database")
    fsa_color: Optional[str] = Field(None, description="FSA rating color (green/yellow/red)")
    match_type: Optional[str] = Field(None, description="Match type: Safe Bet, Best Value, or Premium")
    location_id: Optional[str] = Field(None, description="CQC location ID")


class FairCostGap(BaseModel):
    """Fair Cost Gap Model
    
    Fair Cost Gap = разница между рыночной ценой (Lottie average или scraped) 
    и MSIF fair cost lower bound (из БД msif_fees_2025)
    """
    gap_week: float = Field(..., description="Weekly cost gap in GBP (market_price - msif_lower)")
    gap_year: float = Field(..., description="Annual cost gap in GBP (gap_week * 52)")
    gap_5year: float = Field(..., description="5-year cost gap in GBP (gap_year * 5)")
    market_price: float = Field(..., ge=0, description="Market price (Lottie average or scraped) in GBP per week")
    msif_lower_bound: float = Field(..., ge=0, description="MSIF fair cost lower bound from msif_fees_2025")
    local_authority: str = Field(..., description="Local authority name")
    care_type: str = Field(..., description="Care type (residential or nursing)")
    explanation: str = Field(..., description="Explanation of the gap")
    gap_text: str = Field(..., description="ОБЯЗАТЕЛЬНЫЙ текст: 'Переплата £X в год = £Y за 5 лет'")
    recommendations: List[str] = Field(default_factory=list)


class FreeReportResponse(BaseModel):
    """Free Report Response Model"""
    questionnaire: QuestionnaireResponse
    care_homes: List[CareHome] = Field(..., min_items=1)
    fair_cost_gap: FairCostGap
    generated_at: str = Field(..., description="Report generation timestamp")
    report_id: str = Field(..., description="Unique report ID")

