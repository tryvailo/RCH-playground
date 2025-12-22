"""Pydantic models for Funding Eligibility Calculator 2025-2026."""

from typing import Optional, Dict, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from .constants import Domain, DomainLevel


class DomainAssessment(BaseModel):
    """Assessment for a single DST domain."""
    domain: Domain = Field(..., description="Domain name")
    level: DomainLevel = Field(..., description="Assessment level")
    description: str = Field(..., description="Description of assessment")
    evidence: Optional[str] = Field(None, description="Supporting evidence")


class PropertyDetails(BaseModel):
    """Property details for means test."""
    value: float = Field(..., ge=0, description="Property value in GBP")
    is_main_residence: bool = Field(True, description="Is main residence")
    has_qualifying_relative: bool = Field(False, description="Has qualifying relative living there")
    qualifying_relative_details: Optional[str] = Field(None, description="Details of qualifying relative")
    has_partner_residing: bool = Field(False, description="Has spouse/civil partner/unmarried partner residing")
    has_relative_60plus_residing: bool = Field(False, description="Has relative 60+ residing (must have lived there before care)")
    has_incapacitated_relative: bool = Field(False, description="Has incapacitated relative (receiving AA/DLA/PIP) residing")
    has_child_under_18: bool = Field(False, description="Has child under 18 residing as main/only home")
    is_non_residential_care: bool = Field(False, description="Is receiving non-residential care (property never counted)")
    has_third_party_occupation: bool = Field(False, description="Has third party occupation (discretionary disregard)")
    third_party_occupation_details: Optional[str] = Field(None, description="Details of third party occupation")


class PatientProfile(BaseModel):
    """Enhanced patient profile for funding calculation."""
    
    # Basic info
    age: int = Field(..., ge=0, le=120, description="Patient age")
    
    # DST Domain assessments (12 domains)
    domain_assessments: Dict[Domain, DomainAssessment] = Field(
        default_factory=dict,
        description="Domain assessments"
    )
    
    # Additional health indicators
    has_primary_health_need: bool = Field(False, description="Has primary health need")
    requires_nursing_care: bool = Field(False, description="Requires nursing care")
    
    # Complex therapies
    has_peg_feeding: bool = Field(False, description="Has PEG/PEJ/NJ feeding")
    has_tracheostomy: bool = Field(False, description="Has tracheostomy")
    requires_injections: bool = Field(False, description="Requires regular injections")
    requires_ventilator: bool = Field(False, description="Requires ventilator support")
    requires_dialysis: bool = Field(False, description="Requires dialysis")
    
    # Unpredictability indicators
    has_unpredictable_needs: bool = Field(False, description="Has unpredictable needs")
    has_fluctuating_condition: bool = Field(False, description="Has fluctuating condition")
    has_high_risk_behaviours: bool = Field(False, description="Has high risk behaviours")
    
    # Financial
    capital_assets: float = Field(0.0, ge=0, description="Capital assets in GBP (excluding property and disregards)")
    weekly_income: float = Field(0.0, ge=0, description="Weekly income in GBP (before disregards)")
    property: Optional[PropertyDetails] = Field(None, description="Property details")
    
    # Asset Disregards - Mandatory (fully disregarded)
    asset_personal_possessions: float = Field(0.0, ge=0, description="Personal possessions value (furniture, clothing, jewelry)")
    asset_life_insurance: float = Field(0.0, ge=0, description="Life insurance surrender value")
    asset_investment_bonds_life: float = Field(0.0, ge=0, description="Investment bonds with life element (surrender value)")
    asset_personal_injury_trust: float = Field(0.0, ge=0, description="Personal injury trust value")
    asset_personal_injury_compensation: float = Field(0.0, ge=0, description="Personal injury compensation (disregarded for 52 weeks)")
    asset_infected_blood_compensation: float = Field(0.0, ge=0, description="Infected blood compensation (IBCA, Macfarlane Trust, etc.)")
    
    # Asset Disregards - Discretionary
    asset_business_assets: float = Field(0.0, ge=0, description="Business assets (disregarded while being disposed)")
    
    # Temporary disregards
    weeks_in_care: int = Field(0, ge=0, description="Weeks since entering permanent residential care (for 12-week property disregard)")
    personal_injury_compensation_weeks: int = Field(0, ge=0, description="Weeks since receiving personal injury compensation (for 52-week disregard)")
    
    # Income Disregards (fully disregarded - 100%)
    income_dla_mobility: float = Field(0.0, ge=0, description="DLA Mobility Component (fully disregarded)")
    income_pip_mobility: float = Field(0.0, ge=0, description="PIP Mobility Component (fully disregarded)")
    income_war_disablement_pension: float = Field(0.0, ge=0, description="War Disablement Pension (fully disregarded)")
    income_war_widow_pension: float = Field(0.0, ge=0, description="War Widow's/Widower's Pension (fully disregarded)")
    income_afip: float = Field(0.0, ge=0, description="Armed Forces Independence Payment (fully disregarded)")
    income_afcs_guaranteed: float = Field(0.0, ge=0, description="Guaranteed Income Payments (AFCS) (fully disregarded)")
    income_earnings: float = Field(0.0, ge=0, description="Earnings from Employment (fully disregarded)")
    income_direct_payments: float = Field(0.0, ge=0, description="Direct Payments (fully disregarded)")
    income_child_benefit: float = Field(0.0, ge=0, description="Child Benefit (fully disregarded)")
    income_child_tax_credit: float = Field(0.0, ge=0, description="Child Tax Credit (fully disregarded)")
    income_housing_benefit: float = Field(0.0, ge=0, description="Housing Benefit (fully disregarded)")
    income_council_tax_reduction: float = Field(0.0, ge=0, description="Council Tax Reduction (fully disregarded)")
    income_winter_fuel_payment: float = Field(0.0, ge=0, description="Winter Fuel Payments (fully disregarded)")
    
    # Income Disregards (partially disregarded or with DRE deductions)
    income_attendance_allowance: float = Field(0.0, ge=0, description="Attendance Allowance (assessable with DRE deductions)")
    income_dla_care: float = Field(0.0, ge=0, description="DLA Care Component (assessable with DRE deductions)")
    income_pip_daily_living: float = Field(0.0, ge=0, description="PIP Daily Living Component (assessable with DRE deductions)")
    income_constant_attendance_allowance: float = Field(0.0, ge=0, description="Constant Attendance Allowance (not disregarded for care home)")
    income_savings_credit: float = Field(0.0, ge=0, description="Savings Credit (Pension Credit) - partial disregard")
    
    # Disability-Related Expenditure (DRE) - deducted from assessable disability benefits
    disability_related_expenditure: float = Field(0.0, ge=0, description="Disability-Related Expenditure (DRE) in GBP/week")
    
    # Care context
    care_type: Literal["residential", "nursing", "residential_dementia", "nursing_dementia", "respite"] = Field(
        "residential",
        description="Type of care"
    )
    is_permanent_care: bool = Field(True, description="Is permanent care (not respite)")
    
    @field_validator("capital_assets", "weekly_income")
    @classmethod
    def validate_financial(cls, v: float) -> float:
        """Validate financial values."""
        if v < 0:
            raise ValueError("Financial values cannot be negative")
        return v


class CHCEligibilityResult(BaseModel):
    """CHC eligibility calculation result."""
    
    probability_percent: int = Field(..., ge=0, le=98, description="CHC eligibility probability (max 98%)")
    is_likely_eligible: bool = Field(..., description="Whether likely eligible")
    reasoning: str = Field(..., description="Detailed reasoning")
    key_factors: List[str] = Field(default_factory=list, description="Key factors")
    domain_scores: Dict[str, int] = Field(default_factory=dict, description="Scores by domain")
    bonuses_applied: List[str] = Field(default_factory=list, description="Bonuses applied")
    threshold_category: Literal["very_high", "high", "moderate", "low"] = Field(
        ..., description="Threshold category"
    )


class LASupportResult(BaseModel):
    """Local Authority support calculation result."""
    
    top_up_probability_percent: int = Field(..., ge=0, le=100, description="Top-up probability")
    full_support_probability_percent: int = Field(..., ge=0, le=100, description="Full support probability")
    tariff_income_gbp_week: float = Field(..., ge=0, description="Tariff income per week")
    weekly_contribution: Optional[float] = Field(None, ge=0, description="Weekly contribution required")
    capital_assessed: float = Field(..., ge=0, description="Assessed capital (after property disregard)")
    is_fully_funded: bool = Field(..., description="Is fully funded by LA")
    reasoning: str = Field(..., description="Reasoning for LA support")


class DPAResult(BaseModel):
    """Deferred Payment Agreement eligibility result."""
    
    is_eligible: bool = Field(..., description="Is eligible for DPA")
    reasoning: str = Field(..., description="Reasoning for DPA eligibility")
    property_disregarded: bool = Field(..., description="Is property disregarded")
    weekly_charge: Optional[float] = Field(None, ge=0, description="Weekly charge if DPA")


class SavingsResult(BaseModel):
    """Savings calculation result."""
    
    annual_gbp: float = Field(..., ge=0, description="Annual savings in GBP")
    five_year_gbp: float = Field(..., ge=0, description="5-year savings in GBP")
    lifetime_gbp: Optional[float] = Field(None, ge=0, description="Lifetime savings estimate")
    weekly_savings: float = Field(..., ge=0, description="Weekly savings in GBP")
    breakdown: Dict[str, float] = Field(default_factory=dict, description="Savings breakdown by source")
    # New fields to distinguish between real and hypothetical savings
    is_hypothetical: bool = Field(default=False, description="Whether savings are hypothetical (low probability) or real (high probability)")
    highest_probability: float = Field(default=0.0, ge=0, le=1.0, description="Highest probability among all funding sources")
    hypothetical_weekly_savings: Optional[float] = Field(None, ge=0, description="Hypothetical weekly savings if funding were received (only if is_hypothetical=True)")


class FundingEligibilityResult(BaseModel):
    """Complete funding eligibility calculation result."""
    
    # Input
    patient_profile: PatientProfile = Field(..., description="Input patient profile")
    calculation_date: datetime = Field(default_factory=datetime.now, description="Calculation date")
    
    # CHC eligibility
    chc_eligibility: CHCEligibilityResult = Field(..., description="CHC eligibility assessment")
    
    # LA support
    la_support: LASupportResult = Field(..., description="LA support assessment")
    
    # DPA
    dpa_eligibility: DPAResult = Field(..., description="DPA eligibility")
    
    # Savings
    savings: SavingsResult = Field(..., description="Potential savings")
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list, description="Funding recommendations")
    
    # Report generation
    report_text: Optional[str] = Field(None, description="Generated report text")
    
    def as_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return self.model_dump(mode='json', exclude_none=True)
