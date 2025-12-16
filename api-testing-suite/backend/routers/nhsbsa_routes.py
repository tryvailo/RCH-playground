"""
NHSBSA (NHS Business Services Authority) API Routes
Endpoints for prescribing data and health profiles
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel, Field

from data_integrations.nhsbsa_loader import NHSBSALoader
from data_integrations.cache_manager import get_cache_manager


router = APIRouter(prefix="/api/nhsbsa", tags=["NHSBSA Prescribing"])


class CareHomeLocationRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    max_distance_km: float = Field(default=5.0, ge=0.5, le=20)


@router.get("/status")
async def get_nhsbsa_status():
    """Check NHSBSA integration status"""
    cache = get_cache_manager()
    cache_stats = cache.get_stats()
    nhsbsa_cache = cache_stats.get('by_source', {}).get('nhsbsa', {'count': 0, 'total_hits': 0})
    
    return {
        "api_name": "NHSBSA (English Prescribing Dataset)",
        "status": "available",
        "requires_auth": False,
        "data_freshness": "Monthly (2-3 months lag)",
        "cache": {
            "cached_entries": nhsbsa_cache.get('count', 0),
            "cache_hits": nhsbsa_cache.get('total_hits', 0)
        },
        "endpoints": {
            "health_profile": "/api/nhsbsa/health-profile/{postcode}",
            "top_medications": "/api/nhsbsa/top-medications/{postcode}",
            "vs_national": "/api/nhsbsa/vs-national-average/{postcode}",
            "nearest_practices": "/api/nhsbsa/nearest-practices",
            "gp_practices": "/api/nhsbsa/gp-practices/{postcode}"
        },
        "bnf_categories": [
            "dementia", "pain", "diabetes", "cardiovascular",
            "respiratory", "mental_health", "antibiotics", "nutrition"
        ],
        "documentation": "https://opendata.nhsbsa.net/pages/api-docs"
    }


@router.get("/health-profile/{postcode}")
async def get_health_profile(
    postcode: str,
    radius_km: float = Query(default=5.0, ge=1.0, le=20.0)
):
    """
    Get health profile for an area based on GP prescribing data
    
    Analyzes prescribing patterns from nearby GP practices to build
    a health profile showing:
    - Chronic disease prevalence indicators
    - Mental health indicators
    - Area health index
    - Care home considerations
    """
    async with NHSBSALoader() as loader:
        result = await loader.get_area_health_profile(postcode, radius_km)
        
        if result.get('error'):
            if 'resolve postcode' in result['error']:
                raise HTTPException(status_code=404, detail=f"Postcode not found: {postcode}")
            if 'No GP practices' in result['error']:
                raise HTTPException(status_code=404, detail=result['error'])
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result


@router.get("/top-medications/{postcode}")
async def get_top_medications(
    postcode: str,
    radius_km: float = Query(default=5.0, ge=1.0, le=20.0),
    limit: int = Query(default=10, ge=5, le=50)
):
    """
    Get top prescribed medications in an area
    
    Returns list of most commonly prescribed medications
    from GP practices near the postcode.
    """
    async with NHSBSALoader() as loader:
        profile = await loader.get_area_health_profile(postcode, radius_km)
        
        if profile.get('error'):
            if 'resolve postcode' in profile['error']:
                raise HTTPException(status_code=404, detail=f"Postcode not found: {postcode}")
            raise HTTPException(status_code=500, detail=profile['error'])
        
        return {
            'postcode': postcode,
            'radius_km': radius_km,
            'practices_analyzed': profile.get('practices_analyzed', 0),
            'top_medications': profile.get('top_medications', [])[:limit],
            'data_period': profile.get('data_period'),
            'methodology': 'Based on GP practice prescribing in the area'
        }


@router.get("/vs-national-average/{postcode}")
async def get_vs_national_average(
    postcode: str,
    radius_km: float = Query(default=5.0, ge=1.0, le=20.0)
):
    """
    Compare area prescribing to national averages
    
    Shows how local prescribing patterns compare to national
    averages for key medication categories relevant to care homes.
    """
    async with NHSBSALoader() as loader:
        profile = await loader.get_area_health_profile(postcode, radius_km)
        
        if profile.get('error'):
            if 'resolve postcode' in profile['error']:
                raise HTTPException(status_code=404, detail=f"Postcode not found: {postcode}")
            raise HTTPException(status_code=500, detail=profile['error'])
        
        # Extract comparison data
        comparisons = []
        for category, data in profile.get('health_indicators', {}).items():
            comparisons.append({
                'category': category.replace('_', ' ').title(),
                'local_per_1000': data.get('items_per_1000_patients'),
                'national_per_1000': data.get('national_average'),
                'difference_percent': data.get('vs_national_percent'),
                'status': data.get('significance'),
                'trend': data.get('trend')
            })
        
        # Sort by absolute difference
        comparisons.sort(key=lambda x: abs(x.get('difference_percent', 0)), reverse=True)
        
        return {
            'postcode': postcode,
            'radius_km': radius_km,
            'health_index': profile.get('health_index'),
            'comparisons': comparisons,
            'care_home_considerations': profile.get('care_home_considerations', []),
            'data_period': profile.get('data_period')
        }


@router.get("/gp-practices/{postcode}")
async def get_gp_practices(
    postcode: str,
    limit: int = Query(default=20, ge=5, le=50)
):
    """
    Get GP practices near a postcode
    
    Returns list of GP practices with location and basic info.
    """
    async with NHSBSALoader() as loader:
        practices = await loader.get_gp_practices(postcode, limit=limit)
        
        if not practices:
            raise HTTPException(
                status_code=404,
                detail=f"No GP practices found near {postcode}"
            )
        
        return {
            'postcode': postcode,
            'practices_found': len(practices),
            'practices': practices
        }


@router.post("/nearest-practices")
async def find_nearest_practices(request: CareHomeLocationRequest):
    """
    Find nearest GP practices to a care home location
    
    Useful for assessing healthcare access for care home residents.
    Returns practices within specified radius with distance.
    """
    async with NHSBSALoader() as loader:
        result = await loader.find_nearest_practices_to_care_home(
            request.latitude,
            request.longitude,
            max_distance_km=request.max_distance_km
        )
        
        if result.get('error'):
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result


@router.get("/care-home-considerations/{postcode}")
async def get_care_home_considerations(
    postcode: str,
    radius_km: float = Query(default=5.0, ge=1.0, le=20.0)
):
    """
    Get care home specific health considerations for an area
    
    Analyzes local health patterns to provide recommendations
    for what care capabilities may be needed.
    """
    async with NHSBSALoader() as loader:
        profile = await loader.get_area_health_profile(postcode, radius_km)
        
        if profile.get('error'):
            if 'resolve postcode' in profile['error']:
                raise HTTPException(status_code=404, detail=f"Postcode not found: {postcode}")
            raise HTTPException(status_code=500, detail=profile['error'])
        
        considerations = profile.get('care_home_considerations', [])
        
        # Group by priority
        high_priority = [c for c in considerations if c.get('priority') == 'high']
        medium_priority = [c for c in considerations if c.get('priority') == 'medium']
        low_priority = [c for c in considerations if c.get('priority') == 'low']
        
        return {
            'postcode': postcode,
            'radius_km': radius_km,
            'health_index': profile.get('health_index'),
            'high_priority_considerations': high_priority,
            'medium_priority_considerations': medium_priority,
            'low_priority_considerations': low_priority,
            'summary': f"Found {len(high_priority)} high-priority and {len(medium_priority)} medium-priority considerations",
            'recommendation': _generate_recommendation(high_priority, medium_priority)
        }


def _generate_recommendation(high: list, medium: list) -> str:
    """Generate care home recommendation based on considerations"""
    if not high and not medium:
        return "Standard residential care should meet area health needs"
    
    categories = set()
    for c in high + medium:
        categories.add(c.get('category', ''))
    
    if 'Dementia Care' in categories:
        return "Consider care homes with specialist dementia care capabilities"
    elif 'Mental Health Support' in categories:
        return "Look for homes with mental health trained staff"
    elif 'Cardiovascular Care' in categories or 'Diabetes Management' in categories:
        return "Nursing homes may be more appropriate for complex health needs"
    else:
        return "Ensure care home can manage identified health conditions"


@router.get("/cache/stats")
async def get_cache_stats():
    """Get NHSBSA cache statistics"""
    cache = get_cache_manager()
    stats = cache.get_stats()
    
    return {
        "source": "nhsbsa",
        "stats": stats.get('by_source', {}).get('nhsbsa', {'count': 0, 'total_hits': 0}),
        "total_cache_size_mb": stats.get('db_size_mb', 0)
    }


@router.post("/cache/clear")
async def clear_cache():
    """Clear NHSBSA cache"""
    cache = get_cache_manager()
    cleared = cache.clear_source('nhsbsa')
    
    return {
        "message": f"Cleared {cleared} cached entries",
        "source": "nhsbsa"
    }
