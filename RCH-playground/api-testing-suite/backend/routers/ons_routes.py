"""
ONS (Office for National Statistics) API Routes
Endpoints for UK statistical data access
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from data_integrations.ons_loader import ONSLoader
from data_integrations.cache_manager import get_cache_manager


router = APIRouter(prefix="/api/ons", tags=["ONS Statistics"])


@router.get("/status")
async def get_ons_status():
    """Check ONS integration status"""
    cache = get_cache_manager()
    cache_stats = cache.get_stats()
    ons_cache = cache_stats.get('by_source', {}).get('ons', {'count': 0, 'total_hits': 0})
    
    return {
        "api_name": "ONS (Office for National Statistics)",
        "status": "available",
        "requires_auth": False,
        "cache": {
            "cached_entries": ons_cache.get('count', 0),
            "cache_hits": ons_cache.get('total_hits', 0)
        },
        "endpoints": {
            "lsoa": "/api/ons/lsoa/{postcode}",
            "wellbeing": "/api/ons/wellbeing/{postcode}",
            "economic": "/api/ons/economic-profile/{postcode}",
            "demographics": "/api/ons/demographics/{postcode}",
            "full_profile": "/api/ons/area-profile/{postcode}"
        },
        "data_sources": [
            "Postcodes.io (LSOA lookup)",
            "ONS Personal Well-being Estimates",
            "ONS Labour Market Statistics",
            "Census 2021"
        ],
        "documentation": "https://developer.ons.gov.uk/"
    }


@router.get("/lsoa/{postcode}")
async def get_lsoa(postcode: str):
    """
    Get LSOA (Lower Layer Super Output Area) for a postcode
    
    LSOA is used to link postcodes to statistical data.
    Also returns MSOA, Local Authority, and coordinates.
    """
    async with ONSLoader() as loader:
        result = await loader.postcode_to_lsoa(postcode)
        
        if result.get('error'):
            if 'not found' in result['error']:
                raise HTTPException(status_code=404, detail=f"Postcode not found: {postcode}")
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result


@router.get("/wellbeing/{postcode}")
async def get_wellbeing(postcode: str):
    """
    Get wellbeing data for a postcode area
    
    Returns:
    - Happiness score (0-10)
    - Life satisfaction (0-10)
    - Anxiety levels (0-10, lower is better)
    - Sense of worthwhile activities (0-10)
    - Social Wellbeing Index (0-100)
    """
    async with ONSLoader() as loader:
        # First get LSOA
        lsoa_data = await loader.postcode_to_lsoa(postcode)
        
        if lsoa_data.get('error'):
            if 'not found' in lsoa_data['error']:
                raise HTTPException(status_code=404, detail=f"Postcode not found: {postcode}")
            raise HTTPException(status_code=500, detail=lsoa_data['error'])
        
        # Get wellbeing data
        result = await loader.get_wellbeing_data(
            lsoa_code=lsoa_data.get('lsoa_code'),
            local_authority=lsoa_data.get('local_authority')
        )
        
        return {
            'postcode': postcode,
            'geography': {
                'lsoa_code': lsoa_data.get('lsoa_code'),
                'lsoa_name': lsoa_data.get('lsoa_name'),
                'local_authority': lsoa_data.get('local_authority')
            },
            **result
        }


@router.get("/economic-profile/{postcode}")
async def get_economic_profile(postcode: str):
    """
    Get economic profile for a postcode area
    
    Returns:
    - Employment rate
    - Median income
    - Index of Multiple Deprivation (IMD) decile
    - Economic stability index
    """
    async with ONSLoader() as loader:
        result = await loader.get_economic_profile(postcode=postcode)
        
        if result.get('error'):
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result


@router.get("/demographics/{postcode}")
async def get_demographics(postcode: str):
    """
    Get demographic data for a postcode area
    
    Returns:
    - Population and density
    - Age structure
    - Elderly population statistics (important for care homes)
    - Household composition
    """
    async with ONSLoader() as loader:
        result = await loader.get_demographics(postcode=postcode)
        
        if result.get('error'):
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result


@router.get("/area-profile/{postcode}")
async def get_full_area_profile(postcode: str):
    """
    Get comprehensive area profile combining all data sources
    
    Returns complete profile including:
    - Geography (LSOA, MSOA, Local Authority)
    - Wellbeing indicators
    - Economic profile
    - Demographics
    - Overall area rating for care home suitability
    """
    async with ONSLoader() as loader:
        result = await loader.get_full_area_profile(postcode)
        
        if result.get('error'):
            if 'not found' in result['error']:
                raise HTTPException(status_code=404, detail=f"Postcode not found: {postcode}")
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result


@router.get("/cache/stats")
async def get_cache_stats():
    """Get ONS cache statistics"""
    cache = get_cache_manager()
    stats = cache.get_stats()
    
    return {
        "source": "ons",
        "stats": stats.get('by_source', {}).get('ons', {'count': 0, 'total_hits': 0}),
        "total_cache_size_mb": stats.get('db_size_mb', 0)
    }


@router.post("/cache/clear")
async def clear_cache():
    """Clear ONS cache"""
    cache = get_cache_manager()
    cleared = cache.clear_source('ons')
    
    return {
        "message": f"Cleared {cleared} cached entries",
        "source": "ons"
    }
