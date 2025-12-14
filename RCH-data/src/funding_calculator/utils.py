"""Utility functions for funding eligibility calculations."""

from typing import Dict, List
try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
from .constants import Domain, DomainLevel, CHC_WEIGHTS, CHC_BONUSES, DOMAIN_GROUPS
from .models import DomainAssessment, PatientProfile


def count_domain_levels(
    assessments: Dict[Domain, DomainAssessment],
    level: DomainLevel,
    domains: List[Domain] = None
) -> int:
    """
    Count domains with specific level.
    
    Args:
        assessments: Domain assessments
        level: Level to count
        domains: Optional list of domains to check (None = all)
        
    Returns:
        Count of domains with specified level
    """
    if domains is None:
        domains = list(assessments.keys())
    
    return sum(
        1 for domain in domains
        if domain in assessments and assessments[domain].level == level
    )


def calculate_chc_base_score(assessments: Dict[Domain, DomainAssessment]) -> int:
    """
    Calculate base CHC score from domain assessments.
    
    Args:
        assessments: Domain assessments
        
    Returns:
        Base score (before bonuses)
    """
    score = 0
    
    # Count levels
    priority_count = count_domain_levels(assessments, DomainLevel.PRIORITY)
    severe_count = count_domain_levels(assessments, DomainLevel.SEVERE)
    high_count = count_domain_levels(assessments, DomainLevel.HIGH)
    
    # Apply weights
    if priority_count > 0:
        score += CHC_WEIGHTS[DomainLevel.PRIORITY]
    
    score += severe_count * CHC_WEIGHTS[DomainLevel.SEVERE]
    score += high_count * CHC_WEIGHTS[DomainLevel.HIGH]
    
    return score


def calculate_chc_bonuses(
    assessments: Dict[Domain, DomainAssessment],
    profile: PatientProfile
) -> Dict[str, int]:
    """
    Calculate CHC bonus scores.
    
    Args:
        assessments: Domain assessments
        profile: Patient profile
        
    Returns:
        Dictionary of bonus name -> bonus score
    """
    bonuses = {}
    
    # Multiple Severe bonus (≥2 Severe in critical domains)
    critical_domains = DOMAIN_GROUPS["critical_domains"]
    severe_critical = count_domain_levels(assessments, DomainLevel.SEVERE, critical_domains)
    if severe_critical >= 2:
        bonuses["multiple_severe"] = CHC_BONUSES["multiple_severe"]
    
    # Unpredictability bonus
    if (profile.has_unpredictable_needs or 
        profile.has_fluctuating_condition or 
        profile.has_high_risk_behaviours):
        bonuses["unpredictability"] = CHC_BONUSES["unpredictability"]
    
    # Multiple High bonus (≥3 High in behavioural domains)
    behavioural_domains = DOMAIN_GROUPS["behavioural_domains"]
    high_behavioural = count_domain_levels(assessments, DomainLevel.HIGH, behavioural_domains)
    if high_behavioural >= 3:
        bonuses["multiple_high"] = CHC_BONUSES["multiple_high"]
    
    # Complex therapies bonus
    if (profile.has_peg_feeding or 
        profile.has_tracheostomy or 
        profile.requires_injections or 
        profile.requires_ventilator or 
        profile.requires_dialysis):
        bonuses["complex_therapies"] = CHC_BONUSES["complex_therapies"]
    
    return bonuses


def calculate_income_disregards(profile: PatientProfile) -> Dict[str, float]:
    """
    Calculate total income disregards from patient profile.
    
    Args:
        profile: Patient profile
        
    Returns:
        Dictionary with:
        - fully_disregarded: Total fully disregarded income
        - partially_disregarded: Total partially disregarded income (after DRE)
        - total_disregarded: Total disregarded income
        - breakdown: Breakdown by type
    """
    # Fully disregarded income (100%)
    fully_disregarded = (
        profile.income_dla_mobility +
        profile.income_pip_mobility +
        profile.income_war_disablement_pension +
        profile.income_war_widow_pension +
        profile.income_afip +
        profile.income_afcs_guaranteed +
        profile.income_earnings +
        profile.income_direct_payments +
        profile.income_child_benefit +
        profile.income_child_tax_credit +
        profile.income_housing_benefit +
        profile.income_council_tax_reduction +
        profile.income_winter_fuel_payment
    )
    
    # Partially disregarded income (with DRE deductions)
    # Attendance Allowance, DLA Care, PIP Daily Living are assessable but DRE is deducted
    disability_benefits_assessable = (
        profile.income_attendance_allowance +
        profile.income_dla_care +
        profile.income_pip_daily_living
    )
    
    # DRE is deducted from assessable disability benefits
    disability_benefits_after_dre = max(0, disability_benefits_assessable - profile.disability_related_expenditure)
    
    # Constant Attendance Allowance is NOT disregarded for care home residents
    # (but may be disregarded for non-residential care - this is context-dependent)
    constant_attendance_assessable = profile.income_constant_attendance_allowance
    
    # Savings Credit has partial disregard (£6.95/week single, £10.40/week couple)
    # For simplicity, we'll use single rate - this could be made configurable
    savings_credit_disregard = 6.95  # Single rate
    savings_credit_after_disregard = max(0, profile.income_savings_credit - savings_credit_disregard)
    
    # Total assessable income from partially disregarded sources (what remains after deductions)
    partially_assessable = disability_benefits_after_dre + constant_attendance_assessable + savings_credit_after_disregard
    
    # Total disregarded income (fully disregarded + what was deducted from partially disregarded)
    total_disregarded = fully_disregarded + (disability_benefits_assessable - disability_benefits_after_dre) + savings_credit_disregard
    
    breakdown = {
        "fully_disregarded": fully_disregarded,
        "disability_benefits_before_dre": disability_benefits_assessable,
        "disability_related_expenditure": profile.disability_related_expenditure,
        "disability_benefits_after_dre": disability_benefits_after_dre,
        "constant_attendance_allowance": constant_attendance_assessable,
        "savings_credit_before_disregard": profile.income_savings_credit,
        "savings_credit_disregard": savings_credit_disregard,
        "savings_credit_after_disregard": savings_credit_after_disregard,
        "total_partially_assessable": partially_assessable,
        "total_disregarded": total_disregarded
    }
    
    return {
        "fully_disregarded": fully_disregarded,
        "partially_assessable": partially_assessable,
        "total_disregarded": total_disregarded,
        "breakdown": breakdown
    }


def calculate_tariff_income(capital_assets: float) -> float:
    """
    Calculate tariff income from capital assets.
    
    Args:
        capital_assets: Capital assets (excluding property)
        
    Returns:
        Tariff income per week in GBP
    """
    from .constants import MEANS_TEST
    
    lower_limit = MEANS_TEST["lower_capital_limit"]
    rate = MEANS_TEST["tariff_income_rate"]
    
    if capital_assets <= lower_limit:
        return 0.0
    
    excess = capital_assets - lower_limit
    tariff_income = (excess // rate) + (1 if excess % rate > 0 else 0)
    
    return float(tariff_income)


def assess_property_for_means_test(property_details, dpa_eligible: bool, weeks_in_care: int = 0) -> Dict[str, any]:
    """
    Assess property for means test with all disregard rules.
    
    Args:
        property_details: PropertyDetails object
        dpa_eligible: Whether DPA eligible
        weeks_in_care: Weeks since entering permanent residential care
        
    Returns:
        Dictionary with property assessment
    """
    if not property_details:
        return {
            "disregarded": True,
            "reason": "No property",
            "value_counted": 0.0
        }
    
    # Property NEVER counted for non-residential care
    if property_details.is_non_residential_care:
        return {
            "disregarded": True,
            "reason": "Non-residential care (property never counted)",
            "value_counted": 0.0
        }
    
    # Property disregarded if DPA eligible
    if dpa_eligible:
        return {
            "disregarded": True,
            "reason": "DPA eligible",
            "value_counted": 0.0
        }
    
    # Property disregarded if partner/spouse residing
    if property_details.has_partner_residing:
        return {
            "disregarded": True,
            "reason": "Partner/spouse residing",
            "value_counted": 0.0
        }
    
    # Property disregarded if qualifying relative (60+) lives there
    if property_details.has_qualifying_relative or property_details.has_relative_60plus_residing:
        return {
            "disregarded": True,
            "reason": "Qualifying relative (60+) in residence",
            "value_counted": 0.0
        }
    
    # Property disregarded if incapacitated relative lives there
    if property_details.has_incapacitated_relative:
        return {
            "disregarded": True,
            "reason": "Incapacitated relative in residence",
            "value_counted": 0.0
        }
    
    # Property disregarded if child under 18 lives there
    if property_details.has_child_under_18:
        return {
            "disregarded": True,
            "reason": "Child under 18 in residence",
            "value_counted": 0.0
        }
    
    # 12-week property disregard for permanent residential care
    if weeks_in_care < 12:
        return {
            "disregarded": True,
            "reason": f"12-week property disregard (week {weeks_in_care + 1} of 12)",
            "value_counted": 0.0
        }
    
    # Discretionary disregard for third party occupation
    if property_details.has_third_party_occupation:
        return {
            "disregarded": True,
            "reason": "Third party occupation (discretionary disregard)",
            "value_counted": 0.0
        }
    
    return {
        "disregarded": False,
        "reason": "Property counted",
        "value_counted": property_details.value
    }


def calculate_asset_disregards(profile: PatientProfile) -> Dict[str, float]:
    """
    Calculate total asset disregards from patient profile.
    
    Args:
        profile: Patient profile
        
    Returns:
        Dictionary with:
        - mandatory_disregards: Total mandatory asset disregards
        - discretionary_disregards: Total discretionary asset disregards
        - temporary_disregards: Total temporary asset disregards
        - total_disregarded: Total disregarded assets
        - breakdown: Breakdown by type
    """
    # Mandatory disregards (fully disregarded)
    mandatory_disregards = (
        profile.asset_personal_possessions +
        profile.asset_life_insurance +
        profile.asset_investment_bonds_life +
        profile.asset_personal_injury_trust +
        profile.asset_infected_blood_compensation
    )
    
    # Personal injury compensation - disregarded for 52 weeks
    personal_injury_disregarded = 0.0
    if profile.personal_injury_compensation_weeks < 52 and profile.asset_personal_injury_compensation > 0:
        personal_injury_disregarded = profile.asset_personal_injury_compensation
        mandatory_disregards += personal_injury_disregarded
    
    # Discretionary disregards
    discretionary_disregards = profile.asset_business_assets
    
    # Total disregarded
    total_disregarded = mandatory_disregards + discretionary_disregards
    
    breakdown = {
        "personal_possessions": profile.asset_personal_possessions,
        "life_insurance": profile.asset_life_insurance,
        "investment_bonds_life": profile.asset_investment_bonds_life,
        "personal_injury_trust": profile.asset_personal_injury_trust,
        "personal_injury_compensation": personal_injury_disregarded,
        "personal_injury_compensation_weeks": profile.personal_injury_compensation_weeks,
        "infected_blood_compensation": profile.asset_infected_blood_compensation,
        "business_assets": profile.asset_business_assets,
        "mandatory_disregards": mandatory_disregards,
        "discretionary_disregards": discretionary_disregards,
        "total_disregarded": total_disregarded
    }
    
    return {
        "mandatory_disregards": mandatory_disregards,
        "discretionary_disregards": discretionary_disregards,
        "temporary_disregards": personal_injury_disregarded,
        "total_disregarded": total_disregarded,
        "breakdown": breakdown
    }


def calculate_chc_probability_range(
    priority_count: int,
    severe_count: int,
    high_count: int
) -> tuple[int, int, str]:
    """
    Calculate CHC probability range based on domain levels.
    
    Args:
        priority_count: Number of PRIORITY domains
        severe_count: Number of SEVERE domains
        high_count: Number of HIGH domains
        
    Returns:
        Tuple of (min_probability, max_probability, category)
    """
    from .constants import CHC_THRESHOLDS
    
    # Very high: ≥1 Priority OR ≥2 Severe OR (1 Severe + ≥4 High)
    if (priority_count >= 1 or 
        severe_count >= 2 or 
        (severe_count >= 1 and high_count >= 4)):
        threshold = CHC_THRESHOLDS["very_high"]
        return threshold["min"], threshold["max"], "very_high"
    
    # High: 1 Severe + 2-3 High
    if severe_count >= 1 and 2 <= high_count <= 3:
        threshold = CHC_THRESHOLDS["high"]
        return threshold["min"], threshold["max"], "high"
    
    # Moderate: ≥5 High
    if high_count >= 5:
        threshold = CHC_THRESHOLDS["moderate"]
        return threshold["min"], threshold["max"], "moderate"
    
    # Low: all other cases
    threshold = CHC_THRESHOLDS["low"]
    return threshold["min"], threshold["max"], "low"

