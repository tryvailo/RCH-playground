"""
API Routes for RCH-data modules integration
Data Ingestion, Funding Calculator, Price Calculator
"""
from fastapi import APIRouter, HTTPException, Body, Query
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Add RCH-data src to Python path if not already there
project_root = Path(__file__).parent.parent.parent.parent.parent
rch_data_src_path = project_root / "RCH-data" / "src"
if str(rch_data_src_path) not in sys.path:
    sys.path.insert(0, str(rch_data_src_path))

# Try to import RCH-data modules
try:
    from data_ingestion import DataIngestionService
    from data_ingestion.database import init_database
    DATA_INGESTION_AVAILABLE = True
except ImportError:
    DATA_INGESTION_AVAILABLE = False

try:
    from funding_calculator import (
        FundingEligibilityCalculator,
        PatientProfile,
        PropertyDetails,
        Domain,
        DomainLevel
    )
    FUNDING_CALCULATOR_AVAILABLE = True
except ImportError:
    FUNDING_CALCULATOR_AVAILABLE = False

try:
    from pricing_calculator import PricingService, CareType
    PRICING_CALCULATOR_AVAILABLE = True
except ImportError:
    PRICING_CALCULATOR_AVAILABLE = False

try:
    from postcode_resolver import PostcodeResolver as RCHPostcodeResolver, BatchPostcodeResolver
    POSTCODE_RESOLVER_AVAILABLE = True
except ImportError:
    POSTCODE_RESOLVER_AVAILABLE = False
    RCHPostcodeResolver = None
    BatchPostcodeResolver = None

router = APIRouter(prefix="/api/rch-data", tags=["RCH-data"])

# Get backend data directory path
backend_dir = Path(__file__).parent.parent
data_dir = backend_dir / "data"

# Import Local Authority service
try:
    from services.local_authority_service import LocalAuthorityService
    LA_SERVICE_AVAILABLE = True
except ImportError:
    LA_SERVICE_AVAILABLE = False
    LocalAuthorityService = None


# ============================================================================
# Data Ingestion Admin Endpoints
# ============================================================================

@router.get("/data-ingestion/status")
async def get_data_ingestion_status():
    """Get data ingestion update status"""
    if not DATA_INGESTION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Data ingestion module not available")
    
    try:
        service = DataIngestionService()
        updates = service.get_update_status()
        return {
            "status": "success",
            "updates": updates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")


@router.post("/data-ingestion/init-db")
async def init_data_ingestion_db():
    """Initialize database tables for data ingestion"""
    if not DATA_INGESTION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Data ingestion module not available")
    
    try:
        init_database()
        return {"status": "success", "message": "Database tables initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing database: {str(e)}")


@router.post("/data-ingestion/refresh-msif")
async def refresh_msif_data(year: int = Body(..., embed=True)):
    """Refresh MSIF data for specified year"""
    if not DATA_INGESTION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Data ingestion module not available")
    
    try:
        service = DataIngestionService()
        # Run in executor since it's synchronous
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            service.refresh_msif_data,
            year
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing MSIF data: {str(e)}")


@router.post("/data-ingestion/refresh-lottie")
async def refresh_lottie_data():
    """Refresh Lottie regional averages data"""
    if not DATA_INGESTION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Data ingestion module not available")
    
    try:
        service = DataIngestionService()
        # Run in executor since it's synchronous
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            service.refresh_lottie_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing Lottie data: {str(e)}")


# ============================================================================
# Funding Calculator Endpoints
# ============================================================================

class DomainAssessmentRequest(BaseModel):
    domain: str
    level: str
    description: Optional[str] = None


class PatientProfileRequest(BaseModel):
    age: int
    domain_assessments: Dict[str, Dict[str, Any]]
    has_primary_health_need: bool = False
    requires_nursing_care: bool = False
    has_peg_feeding: bool = False
    has_tracheostomy: bool = False
    requires_injections: bool = False
    requires_ventilator: bool = False
    requires_dialysis: bool = False
    has_unpredictable_needs: bool = False
    has_fluctuating_condition: bool = False
    has_high_risk_behaviours: bool = False
    capital_assets: float = 0.0
    weekly_income: float = 0.0
    property: Optional[Dict[str, Any]] = None
    care_type: str = "residential"
    is_permanent_care: bool = True
    postcode: Optional[str] = None
    # Asset disregards - Mandatory
    asset_personal_possessions: float = 0.0
    asset_life_insurance: float = 0.0
    asset_investment_bonds_life: float = 0.0
    asset_personal_injury_trust: float = 0.0
    asset_personal_injury_compensation: float = 0.0
    asset_infected_blood_compensation: float = 0.0
    # Asset disregards - Discretionary
    asset_business_assets: float = 0.0
    # Temporary disregards
    weeks_in_care: int = 0
    personal_injury_compensation_weeks: int = 0
    # Income disregards - Fully disregarded (100%)
    income_dla_mobility: float = 0.0
    income_pip_mobility: float = 0.0
    income_war_disablement_pension: float = 0.0
    income_war_widow_pension: float = 0.0
    income_afip: float = 0.0
    income_afcs_guaranteed: float = 0.0
    income_earnings: float = 0.0
    income_direct_payments: float = 0.0
    income_child_benefit: float = 0.0
    income_child_tax_credit: float = 0.0
    income_housing_benefit: float = 0.0
    income_council_tax_reduction: float = 0.0
    income_winter_fuel_payment: float = 0.0
    # Income disregards - Partially disregarded or with DRE
    income_attendance_allowance: float = 0.0
    income_pip_daily_living: float = 0.0
    income_dla_care: float = 0.0
    income_constant_attendance_allowance: float = 0.0
    income_savings_credit: float = 0.0
    # Disability-Related Expenditure (DRE)
    disability_related_expenditure: float = 0.0


@router.post("/funding/calculate")
async def calculate_funding_eligibility(request: PatientProfileRequest):
    """Calculate funding eligibility"""
    import time
    start_time = time.time()
    
    if not FUNDING_CALCULATOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="Funding calculator module not available")
    
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Starting funding calculation for age {request.age}, postcode: {request.postcode}")
        calculator = FundingEligibilityCalculator()
        
        # Convert domain assessments
        domain_assessments = {}
        for domain_str, assessment_data in request.domain_assessments.items():
            try:
                domain = Domain(domain_str)
                level = DomainLevel(assessment_data["level"])
                from funding_calculator.models import DomainAssessment
                domain_assessments[domain] = DomainAssessment(
                    domain=domain,
                    level=level,
                    description=assessment_data.get("description", "")
                )
            except (ValueError, KeyError):
                continue
        
        # Create property details
        property_obj = None
        if request.property:
            property_data = dict(request.property)
            property_obj = PropertyDetails(**property_data)
        
        # Create patient profile
        profile = PatientProfile(
            age=request.age,
            domain_assessments=domain_assessments,
            has_primary_health_need=request.has_primary_health_need,
            requires_nursing_care=request.requires_nursing_care,
            has_peg_feeding=request.has_peg_feeding,
            has_tracheostomy=request.has_tracheostomy,
            requires_injections=request.requires_injections,
            requires_ventilator=request.requires_ventilator,
            requires_dialysis=request.requires_dialysis,
            has_unpredictable_needs=request.has_unpredictable_needs,
            has_fluctuating_condition=request.has_fluctuating_condition,
            has_high_risk_behaviours=request.has_high_risk_behaviours,
            capital_assets=request.capital_assets,
            weekly_income=request.weekly_income,
            property=property_obj,
            care_type=request.care_type,
            is_permanent_care=request.is_permanent_care,
            # Income disregards - Fully disregarded
            income_dla_mobility=getattr(request, 'income_dla_mobility', 0.0),
            income_pip_mobility=getattr(request, 'income_pip_mobility', 0.0),
            income_war_disablement_pension=getattr(request, 'income_war_disablement_pension', 0.0),
            income_war_widow_pension=getattr(request, 'income_war_widow_pension', 0.0),
            income_afip=getattr(request, 'income_afip', 0.0),
            income_afcs_guaranteed=getattr(request, 'income_afcs_guaranteed', 0.0),
            income_earnings=getattr(request, 'income_earnings', 0.0),
            income_direct_payments=getattr(request, 'income_direct_payments', 0.0),
            income_child_benefit=getattr(request, 'income_child_benefit', 0.0),
            income_child_tax_credit=getattr(request, 'income_child_tax_credit', 0.0),
            income_housing_benefit=getattr(request, 'income_housing_benefit', 0.0),
            income_council_tax_reduction=getattr(request, 'income_council_tax_reduction', 0.0),
            income_winter_fuel_payment=getattr(request, 'income_winter_fuel_payment', 0.0),
            # Income disregards - Partially disregarded
            income_attendance_allowance=getattr(request, 'income_attendance_allowance', 0.0),
            income_pip_daily_living=getattr(request, 'income_pip_daily_living', 0.0),
            income_dla_care=getattr(request, 'income_dla_care', 0.0),
            income_constant_attendance_allowance=getattr(request, 'income_constant_attendance_allowance', 0.0),
            income_savings_credit=getattr(request, 'income_savings_credit', 0.0),
            # Disability-Related Expenditure
            disability_related_expenditure=getattr(request, 'disability_related_expenditure', 0.0),
            # Asset disregards - Mandatory
            asset_personal_possessions=getattr(request, 'asset_personal_possessions', 0.0),
            asset_life_insurance=getattr(request, 'asset_life_insurance', 0.0),
            asset_investment_bonds_life=getattr(request, 'asset_investment_bonds_life', 0.0),
            asset_personal_injury_trust=getattr(request, 'asset_personal_injury_trust', 0.0),
            asset_personal_injury_compensation=getattr(request, 'asset_personal_injury_compensation', 0.0),
            asset_infected_blood_compensation=getattr(request, 'asset_infected_blood_compensation', 0.0),
            # Asset disregards - Discretionary
            asset_business_assets=getattr(request, 'asset_business_assets', 0.0),
            # Temporary disregards
            weeks_in_care=getattr(request, 'weeks_in_care', 0),
            personal_injury_compensation_weeks=getattr(request, 'personal_injury_compensation_weeks', 0),
        )
        
        # Get pricing if postcode provided (with timeout to avoid blocking)
        # NOTE: Pricing is optional - calculation works without it
        # WARNING: Pricing lookup makes external HTTP call to postcodes.io API
        # This can cause timeouts if API is slow/unavailable
        pricing_result = None
        if request.postcode and PRICING_CALCULATOR_AVAILABLE:
            try:
                logger.info(f"Attempting pricing lookup for postcode: {request.postcode} (may take up to 5s)")
                pricing_service = PricingService()
                care_type_enum = CareType(request.care_type)
                loop = asyncio.get_event_loop()
                # Use asyncio.wait_for to add timeout for pricing lookup
                # This makes HTTP call to postcodes.io API which can be slow
                pricing_result = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        pricing_service.get_pricing_for_postcode,
                        request.postcode,
                        care_type_enum
                    ),
                    timeout=3.0  # Reduced to 3 seconds - external API can be slow
                )
                logger.info(f"Pricing lookup successful for {request.postcode}")
            except asyncio.TimeoutError:
                # Pricing lookup timed out, continue without pricing
                logger.warning(f"Pricing lookup timed out for {request.postcode} (external API slow), continuing without pricing")
                pass
            except Exception as e:
                # Log but continue without pricing
                logger.warning(f"Pricing lookup failed for {request.postcode}: {str(e)} (external API error), continuing without pricing")
                pass  # Continue without pricing - calculation works fine without it
        
        # Calculate eligibility (with timeout protection)
        logger.info(f"Starting funding calculation (age={request.age}, domains={len(domain_assessments)})")
        
        # Convert PatientProfile to dict for calculate_full_eligibility
        # The method expects dict but we have PatientProfile object
        profile_dict = {
            "age": profile.age,
            "domain_assessments": {
                str(domain.value): {
                    "level": assessment.level.value,
                    "description": assessment.description or ""
                }
                for domain, assessment in profile.domain_assessments.items()
            },
            "has_primary_health_need": profile.has_primary_health_need,
            "requires_nursing_care": profile.requires_nursing_care,
            "has_peg_feeding": profile.has_peg_feeding,
            "has_tracheostomy": profile.has_tracheostomy,
            "requires_injections": profile.requires_injections,
            "requires_ventilator": profile.requires_ventilator,
            "requires_dialysis": profile.requires_dialysis,
            "has_unpredictable_needs": profile.has_unpredictable_needs,
            "has_fluctuating_condition": profile.has_fluctuating_condition,
            "has_high_risk_behaviours": profile.has_high_risk_behaviours,
            "capital_assets": profile.capital_assets,
            "weekly_income": profile.weekly_income,
            "care_type": profile.care_type,
            "is_permanent_care": profile.is_permanent_care,
            # Income disregards - Fully disregarded
            "income_dla_mobility": profile.income_dla_mobility,
            "income_pip_mobility": profile.income_pip_mobility,
            "income_war_disablement_pension": profile.income_war_disablement_pension,
            "income_war_widow_pension": profile.income_war_widow_pension,
            "income_afip": profile.income_afip,
            "income_afcs_guaranteed": profile.income_afcs_guaranteed,
            "income_earnings": profile.income_earnings,
            "income_direct_payments": profile.income_direct_payments,
            "income_child_benefit": profile.income_child_benefit,
            "income_child_tax_credit": profile.income_child_tax_credit,
            "income_housing_benefit": profile.income_housing_benefit,
            "income_council_tax_reduction": profile.income_council_tax_reduction,
            "income_winter_fuel_payment": profile.income_winter_fuel_payment,
            # Income disregards - Partially disregarded
            "income_attendance_allowance": profile.income_attendance_allowance,
            "income_pip_daily_living": profile.income_pip_daily_living,
            "income_dla_care": profile.income_dla_care,
            "income_constant_attendance_allowance": profile.income_constant_attendance_allowance,
            "income_savings_credit": profile.income_savings_credit,
            # Disability-Related Expenditure
            "disability_related_expenditure": profile.disability_related_expenditure,
            # Asset disregards - Mandatory
            "asset_personal_possessions": profile.asset_personal_possessions,
            "asset_life_insurance": profile.asset_life_insurance,
            "asset_investment_bonds_life": profile.asset_investment_bonds_life,
            "asset_personal_injury_trust": profile.asset_personal_injury_trust,
            "asset_personal_injury_compensation": profile.asset_personal_injury_compensation,
            "asset_infected_blood_compensation": profile.asset_infected_blood_compensation,
            # Asset disregards - Discretionary
            "asset_business_assets": profile.asset_business_assets,
            # Temporary disregards
            "weeks_in_care": profile.weeks_in_care,
            "personal_injury_compensation_weeks": profile.personal_injury_compensation_weeks,
        }
        if profile.property:
            profile_dict["property"] = {
                "value": profile.property.value,
                "is_main_residence": profile.property.is_main_residence,
                "has_qualifying_relative": profile.property.has_qualifying_relative,
                "qualifying_relative_details": profile.property.qualifying_relative_details
            }
        
        loop = asyncio.get_event_loop()
        try:
            # Run calculation in executor with timeout
            # NOTE: This is pure local calculation - no external API calls
            result = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    calculator.calculate_full_eligibility,
                    profile_dict,  # Pass dict, not PatientProfile object
                    pricing_result
                ),
                timeout=10.0  # 10 seconds should be enough for local calculations
            )
            
            # Convert to dict for JSON response (use mode='json' to serialize datetime properly)
            result_dict = result.model_dump(mode='json')
            # Ensure result_dict is a mutable dict
            result_dict = dict(result_dict)
            
            # ========================================================================
            # VALIDATE SAVINGS - EDGE CASE HANDLING
            # ========================================================================
            print("🔍 STEP 0: Validating savings for edge cases...")
            savings = result_dict.get('savings', {})
            
            # Clamp all savings to >= 0 (no negative values)
            savings['weekly_savings'] = max(0, savings.get('weekly_savings', 0))
            savings['annual_gbp'] = max(0, savings.get('annual_gbp', 0))
            savings['five_year_gbp'] = max(0, savings.get('five_year_gbp', 0))
            savings['lifetime_gbp'] = max(0, savings.get('lifetime_gbp', 0))
            
            # Validate ratios (weekly * 52 = annual, etc.)
            if savings['weekly_savings'] > 0:
                expected_annual = savings['weekly_savings'] * 52
                if abs(savings['annual_gbp'] - expected_annual) > 0.01:
                    logger.warning(f"Correcting annual savings: {savings['annual_gbp']} → {expected_annual}")
                    savings['annual_gbp'] = expected_annual
                
                expected_five_year = savings['weekly_savings'] * 260
                if abs(savings['five_year_gbp'] - expected_five_year) > 0.01:
                    logger.warning(f"Correcting 5-year savings: {savings['five_year_gbp']} → {expected_five_year}")
                    savings['five_year_gbp'] = expected_five_year
            
            result_dict['savings'] = savings
            
            elapsed_time = time.time() - start_time
            logger.info(f"Funding calculation completed successfully in {elapsed_time:.2f}s")
            logger.info(f"✅ Savings validated: weekly=£{savings['weekly_savings']:.2f}, annual=£{savings['annual_gbp']:.2f}")
            logger.info(f"📦 Result dict keys before insights: {list(result_dict.keys())}")
            
            # ========================================================================
            # Generate LLM Insights - SIMPLE: just explain the results in plain language
            # IMPORTANT: This happens AFTER calculation but BEFORE return
            # ========================================================================
            logger.info("🤖 Generating LLM insights to explain results...")
            print("🔍 STEP 1: Starting LLM insights generation")
            
            # Always generate insights - use fallback if OpenAI fails
            llm_insights = None
            try:
                from services.funding_llm_insights_service import FundingLLMInsightsService
                from config_manager import get_credentials
                
                # Get OpenAI API key
                creds = get_credentials()
                openai_api_key = None
                if creds and hasattr(creds, 'openai') and creds.openai:
                    openai_api_key = getattr(creds.openai, 'api_key', None)
                
                # Generate insights (with or without OpenAI)
                insights_service = FundingLLMInsightsService(openai_api_key=openai_api_key)
                
                try:
                    llm_insights = await asyncio.wait_for(
                        insights_service.generate_funding_insights(
                            calculation_result=result_dict,
                            patient_profile=profile_dict
                        ),
                        timeout=30.0  # Увеличенный таймаут для OpenAI API (было 5.0)
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Async insights failed: {e}, using fallback")
                    llm_insights = insights_service._generate_fallback_insights(result_dict)
            except Exception as e:
                logger.warning(f"⚠️ Insights service error: {e}, using fallback")
                try:
                    from services.funding_llm_insights_service import FundingLLMInsightsService
                    insights_service = FundingLLMInsightsService(openai_api_key=None)
                    llm_insights = insights_service._generate_fallback_insights(result_dict)
                except Exception as fallback_error:
                    logger.warning(f"⚠️ Fallback service error: {fallback_error}, creating basic insights")
                    # Last resort: create basic insights directly
                    chc_prob = result_dict.get('chc_eligibility', {}).get('probability_percent', 0)
                    la_support = result_dict.get('la_support', {})
                    dpa = result_dict.get('dpa_eligibility', {})
                    llm_insights = {
                        "generated_at": datetime.now().isoformat(),
                        "model": "fallback",
                        "method": "direct_fallback",
                        "insights": {
                            "overall_explanation": {
                                "summary": f"Your funding calculation shows a CHC probability of {chc_prob}% and LA funding support availability.",
                                "key_findings": [
                                    f"CHC eligibility: {chc_prob}%",
                                    f"LA funding: {'Available' if la_support.get('is_fully_funded') else 'Partial support'}",
                                    f"DPA eligible: {'Yes' if dpa.get('is_eligible') else 'No'}"
                                ],
                                "confidence_level": "medium"
                            },
                            "chc_explanation": {
                                "what_it_means": f"A {chc_prob}% probability means you have a {'strong' if chc_prob >= 50 else 'moderate' if chc_prob >= 30 else 'low'} chance of qualifying for NHS Continuing Healthcare funding.",
                                "eligibility_factors": result_dict.get('chc_eligibility', {}).get('key_factors', [])[:3] or ["Health needs", "Care requirements", "Primary health need assessment"],
                                "next_steps": ["Contact your local ICB to request a CHC assessment", "Gather medical evidence", "Consider professional advice"]
                            },
                            "la_funding_explanation": {
                                "what_it_means": "Local Authority funding is means-tested based on your capital and income.",
                                "means_test_summary": f"Your capital assessed: £{la_support.get('capital_assessed', 0):,.0f}",
                                "contribution_explanation": f"Weekly contribution: £{la_support.get('weekly_contribution', 0):,.0f}" if la_support.get('weekly_contribution') else "You may be eligible for full LA support"
                            },
                            "dpa_explanation": {
                                "what_it_means": "Deferred Payment Agreement allows you to delay selling your property.",
                                "property_status": "Your property may be disregarded in certain circumstances"
                            },
                            "expert_advice": {
                                "funding_strategy": "Review all three funding options (CHC, LA, DPA) to determine the best approach for your situation."
                            },
                            "actionable_next_steps": [
                                {"step": "Review all calculation results", "priority": "high", "timeline": "Now"},
                                {"step": "Contact your Local Authority", "priority": "high", "timeline": "Within 1 week"},
                                {"step": "Consider CHC assessment", "priority": "medium", "timeline": "Within 2 weeks"}
                            ]
                        }
                    }
            
            # CRITICAL: Ensure llm_insights is NEVER None
            if not llm_insights:
                # Emergency fallback - should never happen, but just in case
                chc_prob = result_dict.get('chc_eligibility', {}).get('probability_percent', 0)
                llm_insights = {
                    "generated_at": datetime.now().isoformat(),
                    "model": "emergency",
                    "method": "emergency_fallback",
                    "insights": {
                        "overall_explanation": {
                            "summary": f"Your funding calculation shows a CHC probability of {chc_prob}%.",
                            "key_findings": [f"CHC eligibility: {chc_prob}%"],
                            "confidence_level": "medium"
                        },
                        "chc_explanation": {
                            "what_it_means": f"Your CHC eligibility probability is {chc_prob}%.",
                            "eligibility_factors": ["See calculation results above"]
                        },
                        "la_funding_explanation": {
                            "what_it_means": "See Local Authority funding section above.",
                            "means_test_summary": "See means test breakdown above"
                        },
                        "dpa_explanation": {
                            "what_it_means": "See DPA eligibility section above.",
                            "property_status": "See DPA section for details"
                        },
                        "expert_advice": {
                            "funding_strategy": "Review all funding options to determine the best approach."
                        },
                        "actionable_next_steps": [
                            {"step": "Review calculation results", "priority": "high", "timeline": "Now"}
                        ]
                    }
                }
            
            # ========================================================================
            # CRITICAL: Add llmInsights to result_dict - MUST happen before return
            # ========================================================================
            print(f"🔍 STEP 2: About to add llmInsights to result_dict")
            print(f"🔍 STEP 2: llm_insights type = {type(llm_insights)}")
            print(f"🔍 STEP 2: llm_insights is None = {llm_insights is None}")
            
            # Create fresh dict to ensure it's fully mutable
            result_dict = dict(result_dict)
            result_dict['llmInsights'] = llm_insights
            
            # Verify it was added (without assert to avoid exceptions)
            if 'llmInsights' not in result_dict:
                logger.error("❌ CRITICAL: Failed to add llmInsights! Force adding...")
                result_dict['llmInsights'] = llm_insights
            
            logger.info(f"✅ llmInsights added to result_dict")
            logger.info(f"   Total keys: {len(result_dict)}")
            logger.info(f"   Keys: {list(result_dict.keys())}")
            print(f"🔍 STEP 3: After adding - result_dict keys = {list(result_dict.keys())}")
            print(f"🔍 STEP 3: llmInsights in result_dict = {'llmInsights' in result_dict}")
            
            # Get Local Authority contact information if postcode provided
            # This should NOT affect llmInsights
            if request.postcode and LA_SERVICE_AVAILABLE:
                try:
                    logger.info(f"Fetching LA contact info for postcode: {request.postcode}")
                    la_service = LocalAuthorityService()
                    la_contact = await la_service.get_la_by_postcode(request.postcode)
                    if la_contact:
                        result_dict['local_authority_contact'] = la_contact
                        logger.info(f"✅ LA contact info added for {la_contact.get('council_name', 'Unknown')}")
                    else:
                        logger.warning(f"⚠️ No LA contact found for postcode: {request.postcode}")
                except Exception as e:
                    logger.warning(f"⚠️ Error fetching LA contact info: {e} (continuing without LA contact)")
                    # Don't fail the whole request if LA lookup fails
            
            # ========================================================================
            # FINAL VERIFICATION: Ensure llmInsights is still there before return
            # ========================================================================
            print(f"🔍 STEP 4: Before final check - result_dict keys = {list(result_dict.keys())}")
            print(f"🔍 STEP 4: llmInsights in result_dict = {'llmInsights' in result_dict}")
            
            if 'llmInsights' not in result_dict:
                logger.error("❌ CRITICAL: llmInsights missing before return! Re-adding...")
                result_dict['llmInsights'] = llm_insights
            
            # Final check - ensure we have a clean dict with llmInsights
            final_result = dict(result_dict)
            if 'llmInsights' not in final_result:
                logger.error("❌ CRITICAL: llmInsights missing in final_result! Re-adding...")
                final_result['llmInsights'] = llm_insights
            
            logger.info(f"📤 Returning result with {len(final_result)} keys: {list(final_result.keys())}")
            logger.info(f"   llmInsights present: {'llmInsights' in final_result}")
            print(f"🔍 STEP 5: FINAL RETURN - final_result keys = {list(final_result.keys())}")
            print(f"🔍 STEP 5: FINAL RETURN - llmInsights in final_result = {'llmInsights' in final_result}")
            print(f"🔍 STEP 5: FINAL RETURN - llmInsights value type = {type(final_result.get('llmInsights'))}")
            
            # Use JSONResponse to ensure all fields are included (including llmInsights)
            # FastAPI may filter out fields not in response_model if we return dict directly
            return JSONResponse(content=final_result)
        except asyncio.TimeoutError:
            elapsed_time = time.time() - start_time
            logger.error(f"Funding calculation timed out after {elapsed_time:.2f}s")
            raise HTTPException(
                status_code=504,
                detail=f"Calculation timed out after {elapsed_time:.1f} seconds. The calculation is taking longer than expected. Please try again or contact support."
            )
        
    except HTTPException:
        raise
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"Funding calculation error after {elapsed_time:.2f}s: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error calculating funding: {str(e)}")


# ============================================================================
# Price Calculator Endpoints
# ============================================================================

class PricingRequest(BaseModel):
    postcode: str
    care_type: str
    cqc_rating: Optional[str] = None
    facilities_score: Optional[int] = None
    bed_count: Optional[int] = None
    is_chain: bool = False
    scraped_price: Optional[float] = None


@router.post("/pricing/calculate")
async def calculate_pricing(request: PricingRequest):
    """Calculate pricing and affordability band"""
    if not PRICING_CALCULATOR_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Pricing calculator module not available. Please install RCH-data package: pip install -e ../RCH-data"
        )
    
    try:
        service = PricingService()
        
        # Convert care_type string to enum
        try:
            care_type_enum = CareType(request.care_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid care_type: {request.care_type}")
        
        # Run in executor since it's synchronous
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            service.get_pricing_for_postcode,
            request.postcode,
            care_type_enum,
            request.cqc_rating,
            request.facilities_score,
            request.bed_count,
            request.is_chain
        )
        
        # Convert to dict for JSON response
        return result.model_dump()
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Pricing calculation error: {error_detail}")
        raise HTTPException(status_code=500, detail=f"Error calculating pricing: {str(e)}")


@router.get("/pricing/postcode/{postcode}")
async def get_pricing_for_postcode(
    postcode: str,
    care_type: str = Query(..., description="Type of care"),
    cqc_rating: Optional[str] = Query(None, description="CQC rating"),
    facilities_score: Optional[int] = Query(None, ge=0, le=20, description="Facilities score"),
    bed_count: Optional[int] = Query(None, gt=0, description="Number of beds"),
    is_chain: bool = Query(False, description="Is part of a chain")
):
    """Get pricing for a specific postcode (simpler version for Postcode Calculator)"""
    if not PRICING_CALCULATOR_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Pricing calculator module not available. Please install RCH-data package: pip install -e ../RCH-data"
        )
    
    try:
        service = PricingService()
        
        # Convert care_type string to enum
        try:
            care_type_enum = CareType(care_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid care_type: {care_type}")
        
        # Run in executor since it's synchronous
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            service.get_pricing_for_postcode,
            postcode,
            care_type_enum,
            cqc_rating,
            facilities_score,
            bed_count,
            is_chain
        )
        
        # Convert to dict for JSON response
        return result.model_dump()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating pricing: {str(e)}")


@router.get("/pricing/locations")
async def get_pricing_locations(
    care_type: Optional[str] = None,
    region: Optional[str] = None,
    min_fair_cost: Optional[float] = None,
    max_fair_cost: Optional[float] = None,
    band: Optional[str] = None
):
    """Get pricing data for all locations"""
    if not PRICING_CALCULATOR_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Pricing calculator module not available. Please install RCH-data package: pip install -e ../RCH-data"
        )
    
    try:
        service = PricingService()
        
        # Convert care_type string to enum
        care_type_enum = None
        if care_type:
            try:
                care_type_enum = CareType(care_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid care_type: {care_type}")
        
        # Run in executor since it's synchronous
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None,
            service.get_all_locations_pricing,
            care_type_enum
        )
        
        # Apply filters
        if region:
            data = [row for row in data if row.get("region", "").lower() == region.lower()]
        
        if min_fair_cost is not None:
            data = [row for row in data if row.get("fair_cost_lower_bound_gbp") and row["fair_cost_lower_bound_gbp"] >= min_fair_cost]
        
        if max_fair_cost is not None:
            data = [row for row in data if row.get("fair_cost_lower_bound_gbp") and row["fair_cost_lower_bound_gbp"] <= max_fair_cost]
        
        if band:
            data = [row for row in data if row.get("affordability_band", "").upper() == band.upper()]
        
        # Get unique care types and regions
        care_types = list(set(row.get("care_type", "") for row in data if row.get("care_type")))
        regions = list(set(row.get("region", "") for row in data if row.get("region")))
        
        return {
            "total_locations": len(data),
            "care_types": sorted(care_types),
            "regions": sorted(regions),
            "data": data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting locations: {str(e)}")


@router.get("/pricing/regions")
async def get_pricing_regions():
    """Get list of all available regions"""
    if not PRICING_CALCULATOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="Pricing calculator module not available")
    
    return {
        "regions": [
            "London",
            "South East",
            "South West",
            "West Midlands",
            "East Midlands",
            "Yorkshire and the Humber",
            "North West",
            "North East",
            "East of England"
        ]
    }


@router.get("/pricing/care-types")
async def get_pricing_care_types():
    """Get list of all available care types"""
    if not PRICING_CALCULATOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="Pricing calculator module not available")
    
    return {
        "care_types": [ct.value for ct in CareType]
    }


# ============================================================================
# Postcode Resolver Endpoints
# ============================================================================

@router.post("/postcode/resolve")
async def resolve_postcode(postcode: str = Body(..., embed=True)):
    """Resolve a single postcode to Local Authority and Region"""
    if not POSTCODE_RESOLVER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Postcode resolver module not available")
    
    try:
        resolver = RCHPostcodeResolver()
        # Run in executor since it's synchronous
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            resolver.resolve,
            postcode
        )
        
        # Convert to dict for JSON response
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resolving postcode: {str(e)}")


@router.post("/postcode/batch")
async def resolve_postcodes_batch(postcodes: List[str] = Body(..., embed=True)):
    """Resolve multiple postcodes in batch"""
    if not POSTCODE_RESOLVER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Postcode resolver module not available")
    
    try:
        batch_resolver = BatchPostcodeResolver()
        # Run in executor since it's synchronous
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            batch_resolver.resolve_batch,
            postcodes
        )
        
        # Convert to dict for JSON response
        result_dict = result.model_dump()
        # Ensure we return results in expected format
        if isinstance(result_dict, dict) and 'results' not in result_dict:
            # If result is a list or has different structure, wrap it
            if isinstance(result_dict, list):
                return {"results": result_dict}
            # If it's a dict with other keys, check if it has a results field
            return result_dict
        return result_dict
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Postcode batch resolver error: {error_detail}")
        raise HTTPException(status_code=500, detail=f"Error resolving postcodes: {str(e)}")


# ============================================================================
# Local Authority Contacts Endpoints
# ============================================================================

@router.get("/funding/la/{postcode}")
async def get_local_authority_contact(postcode: str):
    """
    Get Local Authority contact information by postcode
    
    Returns contact details for the Local Authority responsible for the given postcode.
    Includes phone, email, website, assessment URL, office address, and opening hours.
    """
    if not LA_SERVICE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Local Authority service not available"
        )
    
    try:
        service = LocalAuthorityService()
        la_contact = await service.get_la_by_postcode(postcode)
        
        if not la_contact:
            raise HTTPException(
                status_code=404,
                detail=f"Local Authority not found for postcode: {postcode}"
            )
        
        return {
            "status": "success",
            "postcode": postcode,
            "local_authority": la_contact
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting LA contact for postcode {postcode}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving Local Authority contact: {str(e)}"
        )


@router.get("/funding/data-sources")
async def get_funding_calculator_data_sources():
    """
    Get Funding Calculator Data Sources & References document
    Returns the markdown content of funding_calculator_data_sources.md
    """
    try:
        funding_sources_path = data_dir / "funding_calculator_data_sources.md"
        
        if not funding_sources_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Funding Calculator Data Sources document not found"
            )
        
        with open(funding_sources_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "status": "success",
            "content": content,
            "last_updated": datetime.fromtimestamp(funding_sources_path.stat().st_mtime).isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading Funding Calculator Data Sources: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error loading data sources document: {str(e)}"
        )

