"""
MSIF (Market Sustainability and Improvement Fund) Fair Cost Routes
"""
import asyncio
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/msif", tags=["MSIF Fair Cost"])


@router.get("/fair-cost/{local_authority}")
async def get_msif_fair_cost(
    local_authority: str,
    care_type: str = Query(default="nursing", description="Care type: residential, nursing, residential_dementia, nursing_dementia")
):
    """Get MSIF fair cost lower bound for a local authority and care type"""
    try:
        # Try using RCH-data pricing calculator
        try:
            from pricing_calculator import PricingService, CareType
            pricing_service = PricingService()
            
            # Convert care_type string to enum
            care_type_enum = CareType.NURSING
            if care_type == "residential":
                care_type_enum = CareType.RESIDENTIAL
            elif care_type == "residential_dementia":
                care_type_enum = CareType.RESIDENTIAL_DEMENTIA
            elif care_type == "nursing_dementia":
                care_type_enum = CareType.NURSING_DEMENTIA
            
            # Get fair cost for local authority from fair_cost_data
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: None)  # Ensure service is initialized
            
            # Access fair_cost_data directly
            care_type_key = care_type_enum.value
            if local_authority in pricing_service.fair_cost_data:
                la_data = pricing_service.fair_cost_data[local_authority]
                result = la_data.get(care_type_key)
                
                if result:
                    return {
                        "fair_cost_gbp_week": float(result),
                        "local_authority": local_authority,
                        "care_type": care_type
                    }
        except ImportError:
            pass  # PricingService not available, use fallback
        
        # Fallback to default values if PricingService not available
        default_msif = {
            'residential': 700,
            'nursing': 1048,
            'residential_dementia': 800,
            'nursing_dementia': 1048
        }
        fallback_value = default_msif.get(care_type, 700)
        
        return {
            "fair_cost_gbp_week": float(fallback_value),
            "local_authority": local_authority,
            "care_type": care_type,
            "note": "Using fallback value - PricingService not available"
        }
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"MSIF fair cost lookup error: {error_detail}")
        
        # Return fallback value even on error
        default_msif = {
            'residential': 700,
            'nursing': 1048,
            'residential_dementia': 800,
            'nursing_dementia': 1048
        }
        fallback_value = default_msif.get(care_type, 700)
        
        return {
            "fair_cost_gbp_week": float(fallback_value),
            "local_authority": local_authority,
            "care_type": care_type,
            "note": f"Using fallback value - error: {str(e)}"
        }
