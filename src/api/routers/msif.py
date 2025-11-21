from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from msif.loader import get_fair_cost, get_msif_data, calculate_fair_cost_gap

router = APIRouter(prefix="/api/msif", tags=["MSIF"])


@router.get("/fair-cost/{local_authority}")
async def fair_cost(
    local_authority: str,
    care_type: str = Query(default="nursing", description="Care type: residential, nursing, residential_dementia, nursing_dementia")
):
    """
    Get MSIF fair cost lower bound for a local authority
    
    Example:
        GET /api/msif/fair-cost/Camden?care_type=nursing
    """
    try:
        cost = get_fair_cost(local_authority, care_type)
        return {
            "local_authority": local_authority,
            "care_type": care_type,
            "fair_cost_gbp_week": cost
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching MSIF data: {str(e)}")


@router.get("/fair-cost-gap")
async def gap(
    market_price: float = Query(..., description="Market price per week in GBP"),
    local_authority: str = Query(..., description="Local authority name"),
    care_type: str = Query(default="nursing", description="Care type")
):
    """
    Calculate Fair Cost Gap between market price and MSIF lower bound
    
    Example:
        GET /api/msif/fair-cost-gap?market_price=1912&local_authority=Camden&care_type=nursing_dementia
    
    Returns gap_weekly, gap_annual, gap_5year
    """
    try:
        gap_data = calculate_fair_cost_gap(market_price, local_authority, care_type)
        return gap_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating gap: {str(e)}")


@router.get("/data")
async def get_all_msif_data():
    """
    Get all MSIF data (for debugging/admin purposes)
    
    Returns complete dataset of all local authorities
    """
    try:
        data = get_msif_data()
        return {
            "total_authorities": len(data),
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading MSIF data: {str(e)}")


@router.get("/authorities")
async def list_authorities():
    """
    List all available local authorities in MSIF data
    """
    try:
        data = get_msif_data()
        return {
            "total": len(data),
            "authorities": sorted(list(data.keys()))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading authorities: {str(e)}")

