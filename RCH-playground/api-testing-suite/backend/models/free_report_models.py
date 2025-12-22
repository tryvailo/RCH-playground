"""Pydantic models for Free Report API"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from enum import Enum


class CareTypeEnum(str, Enum):
    """Care type enumeration"""

    RESIDENTIAL = "residential"
    NURSING = "nursing"
    DEMENTIA = "dementia"
    RESPITE = "respite"


class FreeReportRequest(BaseModel):
    """Request model for free report generation"""

    postcode: str = Field(
        ..., min_length=6, max_length=7, description="UK postcode (e.g., SW1A 1AA)"
    )
    budget: float = Field(
        default=0, ge=0, le=10000, description="Weekly budget in GBP (0 = no limit)"
    )
    care_type: CareTypeEnum = Field(
        default=CareTypeEnum.RESIDENTIAL, description="Type of care needed"
    )
    chc_probability: float = Field(
        default=35,
        ge=0,
        le=100,
        description="CHC eligibility probability (0-100)",
    )

    # Optional fields
    location_postcode: Optional[str] = Field(
        default=None, description="Alternative postcode for location"
    )
    timeline: Optional[str] = Field(
        default=None, description="When care is needed (e.g., 'immediate', '3_months')"
    )
    medical_conditions: List[str] = Field(
        default_factory=list,
        description="Medical conditions requiring specialized care",
    )
    max_distance_km: Optional[float] = Field(
        default=30, ge=0, le=100, description="Maximum distance from postcode (km)"
    )
    priority_order: List[str] = Field(
        default_factory=lambda: ["quality", "cost", "proximity"],
        description="Priority order for matching",
    )
    priority_weights: List[float] = Field(
        default_factory=lambda: [40, 35, 25],
        description="Weights for priorities (must sum to 100)",
    )

    class Config:
        """Pydantic config"""

        use_enum_values = True

    @field_validator("postcode")
    @classmethod
    def validate_postcode(cls, v):
        """Validate UK postcode format"""
        # Basic UK postcode validation
        v = v.upper().strip()
        if not v or len(v) < 6 or len(v) > 7:
            raise ValueError("Invalid UK postcode")
        return v

    @field_validator("priority_weights")
    @classmethod
    def validate_weights(cls, v, info):
        """Validate that weights sum to ~100"""
        if not v:
            return [40, 35, 25]  # Default
        total = sum(v)
        if abs(total - 100) > 1:  # Allow 1% tolerance
            raise ValueError(f"Priority weights must sum to 100 (got {total})")
        return v


class FreeReportResponse(BaseModel):
    """Response model for free report"""

    questionnaire: dict
    care_homes: list
    fair_cost_gap: dict
    area_profile: Optional[dict] = None
    area_map: Optional[dict] = None
    llm_insights: Optional[dict] = None
    generated_at: str
    report_id: str

    class Config:
        """Config for response"""

        json_encoders = {
            float: lambda v: round(v, 2) if isinstance(v, float) else v
        }
