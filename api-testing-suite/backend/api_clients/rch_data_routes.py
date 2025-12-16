"""
API Routes for RCH-data modules integration
Data Ingestion, Funding Calculator, Price Calculator
"""
from fastapi import APIRouter, HTTPException, Body, Query
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import asyncio
import sys
from pathlib import Path

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


@router.post("/funding/calculate")
async def calculate_funding_eligibility(request: PatientProfileRequest):
    """Calculate funding eligibility"""
    if not FUNDING_CALCULATOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="Funding calculator module not available")
    
    try:
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
            property_obj = PropertyDetails(**request.property)
        
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
            is_permanent_care=request.is_permanent_care
        )
        
        # Get pricing if postcode provided
        pricing_result = None
        if request.postcode and PRICING_CALCULATOR_AVAILABLE:
            try:
                pricing_service = PricingService()
                care_type_enum = CareType(request.care_type)
                loop = asyncio.get_event_loop()
                pricing_result = await loop.run_in_executor(
                    None,
                    pricing_service.get_pricing_for_postcode,
                    request.postcode,
                    care_type_enum
                )
            except Exception:
                pass  # Continue without pricing
        
        # Calculate eligibility
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            calculator.calculate_full_eligibility,
            profile,
            pricing_result
        )
        
        # Convert to dict for JSON response
        return result.model_dump()
        
    except Exception as e:
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

