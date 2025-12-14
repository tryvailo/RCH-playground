"""
OS Places API Routes
Endpoints for Ordnance Survey Places API integration
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from data_integrations.os_places_loader import OSPlacesLoader
from data_integrations.cache_manager import get_cache_manager


router = APIRouter(prefix="/api/os-places", tags=["OS Places"])


# Request/Response Models
class PostcodeRequest(BaseModel):
    postcode: str = Field(..., description="UK postcode (e.g., B1 1BB)")


class BatchPostcodeRequest(BaseModel):
    postcodes: List[str] = Field(..., description="List of UK postcodes", max_items=50)


class AddressSearchRequest(BaseModel):
    query: str = Field(..., description="Address search query")
    max_results: int = Field(default=25, ge=1, le=100)


class CoordinatesResponse(BaseModel):
    postcode: str
    latitude: Optional[float]
    longitude: Optional[float]
    error: Optional[str] = None


class AddressResponse(BaseModel):
    uprn: Optional[str]
    address: Optional[str]
    building_name: Optional[str]
    building_number: Optional[str]
    street: Optional[str]
    locality: Optional[str]
    town: Optional[str]
    postcode: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    local_authority: Optional[str]


# Endpoints

@router.get("/status")
async def get_os_places_status():
    """Check OS Places API status and configuration"""
    loader = OSPlacesLoader()
    
    has_key = bool(loader.api_key)
    
    # Test API if key exists
    api_status = "unconfigured"
    if has_key:
        try:
            result = await loader.get_address_by_postcode("SW1A 1AA", max_results=1)
            if result.get('error'):
                api_status = f"error: {result['error']}"
            else:
                api_status = "connected"
        except Exception as e:
            api_status = f"error: {str(e)}"
        finally:
            await loader.close()
    
    # Get cache stats
    cache = get_cache_manager()
    cache_stats = cache.get_stats()
    os_places_cache = cache_stats.get('by_source', {}).get('os_places', {'count': 0, 'total_hits': 0})
    
    return {
        "api_name": "OS Places (AddressBase Premium)",
        "status": api_status,
        "has_api_key": has_key,
        "cache": {
            "cached_entries": os_places_cache.get('count', 0),
            "cache_hits": os_places_cache.get('total_hits', 0)
        },
        "endpoints": {
            "postcode": "/api/os-places/address/{postcode}",
            "coordinates": "/api/os-places/coordinates/{postcode}",
            "uprn": "/api/os-places/uprn/{uprn}",
            "search": "/api/os-places/search",
            "batch": "/api/os-places/batch"
        },
        "documentation": "https://osdatahub.os.uk/docs/places/overview"
    }


@router.get("/address/{postcode}")
async def get_address_by_postcode(
    postcode: str,
    max_results: int = Query(default=100, ge=1, le=1000)
):
    """
    Get addresses for a UK postcode
    
    Returns all addresses at the given postcode with full details
    including UPRN, coordinates, and classification.
    """
    loader = OSPlacesLoader()
    
    try:
        result = await loader.get_address_by_postcode(postcode, max_results)
        
        if result.get('error'):
            if 'not configured' in result['error']:
                raise HTTPException(
                    status_code=503,
                    detail="OS Places API not configured. Please add API key to config."
                )
            elif 'Invalid API key' in result['error']:
                raise HTTPException(status_code=401, detail="Invalid OS Places API key")
            elif 'not found' in result['error']:
                raise HTTPException(status_code=404, detail=f"Postcode not found: {postcode}")
            else:
                raise HTTPException(status_code=500, detail=result['error'])
        
        return result
        
    finally:
        await loader.close()


@router.get("/coordinates/{postcode}")
async def get_coordinates(postcode: str):
    """
    Get coordinates for a UK postcode
    
    Returns latitude and longitude for the postcode centroid.
    Useful for distance calculations and map plotting.
    """
    loader = OSPlacesLoader()
    
    try:
        coords = await loader.get_coordinates(postcode)
        
        if coords:
            return {
                "postcode": postcode.upper().strip(),
                "latitude": coords['latitude'],
                "longitude": coords['longitude']
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Could not find coordinates for postcode: {postcode}"
            )
    finally:
        await loader.close()


@router.get("/uprn/{uprn}")
async def get_address_by_uprn(uprn: str):
    """
    Get address details by UPRN (Unique Property Reference Number)
    
    UPRN is the unique identifier for every addressable location in Great Britain.
    """
    loader = OSPlacesLoader()
    
    try:
        result = await loader.get_address_details(uprn)
        
        if result:
            return result
        else:
            raise HTTPException(
                status_code=404,
                detail=f"UPRN not found: {uprn}"
            )
    finally:
        await loader.close()


@router.post("/search")
async def search_address(request: AddressSearchRequest):
    """
    Free-text address search
    
    Search for addresses using natural language query.
    Returns matched addresses with relevance scores.
    """
    loader = OSPlacesLoader()
    
    try:
        result = await loader.search_address(request.query, request.max_results)
        
        if result.get('error'):
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result
        
    finally:
        await loader.close()


@router.post("/batch")
async def batch_get_coordinates(request: BatchPostcodeRequest):
    """
    Get coordinates for multiple postcodes
    
    Batch processing for up to 50 postcodes at once.
    Returns coordinates for each postcode.
    """
    loader = OSPlacesLoader()
    
    try:
        results = await loader.batch_get_coordinates(request.postcodes)
        
        # Format response
        formatted = []
        for postcode, coords in results.items():
            entry = {"postcode": postcode}
            if coords:
                entry["latitude"] = coords['latitude']
                entry["longitude"] = coords['longitude']
                entry["found"] = True
            else:
                entry["found"] = False
            formatted.append(entry)
        
        return {
            "total_requested": len(request.postcodes),
            "total_found": sum(1 for r in formatted if r.get('found')),
            "results": formatted
        }
        
    finally:
        await loader.close()


@router.get("/cache/stats")
async def get_cache_stats():
    """Get OS Places cache statistics"""
    cache = get_cache_manager()
    stats = cache.get_stats()
    
    return {
        "source": "os_places",
        "stats": stats.get('by_source', {}).get('os_places', {'count': 0, 'total_hits': 0}),
        "total_cache_size_mb": stats.get('db_size_mb', 0)
    }


@router.post("/cache/clear")
async def clear_cache():
    """Clear OS Places cache"""
    cache = get_cache_manager()
    cleared = cache.clear_source('os_places')
    
    return {
        "message": f"Cleared {cleared} cached entries",
        "source": "os_places"
    }
