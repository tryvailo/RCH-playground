"""
OpenStreetMap API Routes
Endpoints for Walk Score and POI data
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, List
from pydantic import BaseModel, Field

from data_integrations.osm_loader import OSMLoader
from data_integrations.cache_manager import get_cache_manager


router = APIRouter(prefix="/api/osm", tags=["OpenStreetMap"])


# Request Models
class LocationRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")


class AmenitySearchRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    radius_m: int = Field(default=1600, ge=100, le=5000)
    categories: Optional[List[str]] = Field(
        default=None,
        description="Filter by categories: grocery, restaurants, healthcare, parks, etc."
    )


@router.get("/status")
async def get_osm_status():
    """Check OpenStreetMap integration status"""
    cache = get_cache_manager()
    cache_stats = cache.get_stats()
    osm_cache = cache_stats.get('by_source', {}).get('osm', {'count': 0, 'total_hits': 0})
    
    return {
        "api_name": "OpenStreetMap (Overpass API)",
        "status": "available",
        "requires_auth": False,
        "rate_limits": "Fair use policy - avoid excessive requests",
        "cache": {
            "cached_entries": osm_cache.get('count', 0),
            "cache_hits": osm_cache.get('total_hits', 0)
        },
        "endpoints": {
            "walk_score": "/api/osm/walk-score/{lat}/{lon}",
            "amenities": "/api/osm/nearby-amenities/{lat}/{lon}",
            "infrastructure": "/api/osm/infrastructure-report/{lat}/{lon}",
            "pois": "/api/osm/pois"
        },
        "available_categories": [
            "grocery", "restaurants", "shopping", "coffee",
            "banks", "parks", "schools", "healthcare", "entertainment"
        ],
        "documentation": "https://wiki.openstreetmap.org/wiki/Overpass_API"
    }


@router.get("/walk-score/{lat}/{lon}")
async def get_walk_score(
    lat: float,
    lon: float
):
    """
    Calculate Walk Score for a location
    
    Walk Score (0-100) indicates walkability:
    - 90-100: Walker's Paradise
    - 70-89: Very Walkable
    - 50-69: Somewhat Walkable
    - 25-49: Car-Dependent
    - 0-24: Almost All Errands Require a Car
    
    Also includes Care Home Relevance score assessing
    healthcare access, parks, and dining options.
    """
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Invalid coordinates")
    
    async with OSMLoader() as loader:
        result = await loader.calculate_walk_score(lat, lon)
        
        if result.get('error'):
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result


@router.get("/nearby-amenities/{lat}/{lon}")
async def get_nearby_amenities(
    lat: float,
    lon: float,
    radius_m: int = Query(default=1600, ge=100, le=5000),
    categories: Optional[str] = Query(
        default=None,
        description="Comma-separated categories: grocery,healthcare,parks"
    )
):
    """
    Get nearby amenities/Points of Interest
    
    Returns categorized list of amenities with distances.
    Default radius: 1600m (~20 min walk)
    """
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Invalid coordinates")
    
    # Parse categories
    category_list = None
    if categories:
        category_list = [c.strip() for c in categories.split(',')]
    
    async with OSMLoader() as loader:
        result = await loader.get_nearby_amenities(
            lat, lon,
            radius_m=radius_m,
            categories=category_list
        )
        
        if result.get('error'):
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result


@router.get("/infrastructure-report/{lat}/{lon}")
async def get_infrastructure_report(
    lat: float,
    lon: float
):
    """
    Get infrastructure report for a location
    
    Includes:
    - Public transport (bus stops, rail stations)
    - Pedestrian safety (crossings, lit roads, footways)
    - Accessibility (benches, rest points)
    - Safety score
    """
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Invalid coordinates")
    
    async with OSMLoader() as loader:
        result = await loader.get_infrastructure_report(lat, lon)
        
        if result.get('error'):
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result


@router.post("/pois")
async def search_pois(request: AmenitySearchRequest):
    """
    Search for Points of Interest
    
    POST endpoint for more flexible POI searches with category filtering.
    """
    async with OSMLoader() as loader:
        result = await loader.get_nearby_amenities(
            request.lat,
            request.lon,
            radius_m=request.radius_m,
            categories=request.categories
        )
        
        if result.get('error'):
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result


@router.get("/healthcare/{lat}/{lon}")
async def get_nearby_healthcare(
    lat: float,
    lon: float,
    radius_m: int = Query(default=1600, ge=100, le=5000)
):
    """
    Get nearby healthcare facilities
    
    Specifically queries for:
    - Pharmacies
    - GP surgeries
    - Dentists
    - Hospitals
    - Clinics
    """
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Invalid coordinates")
    
    async with OSMLoader() as loader:
        result = await loader.get_nearby_amenities(
            lat, lon,
            radius_m=radius_m,
            categories=['healthcare']
        )
        
        if result.get('error'):
            raise HTTPException(status_code=500, detail=result['error'])
        
        healthcare = result.get('by_category', {}).get('healthcare', [])
        
        return {
            'location': {'lat': lat, 'lon': lon},
            'radius_m': radius_m,
            'healthcare_facilities': healthcare,
            'count': len(healthcare),
            'nearest': healthcare[0] if healthcare else None,
            'summary': {
                'within_400m': sum(1 for h in healthcare if h['distance_m'] <= 400),
                'within_800m': sum(1 for h in healthcare if h['distance_m'] <= 800),
                'within_1600m': len(healthcare)
            }
        }


@router.get("/parks/{lat}/{lon}")
async def get_nearby_parks(
    lat: float,
    lon: float,
    radius_m: int = Query(default=1600, ge=100, le=5000)
):
    """
    Get nearby parks and green spaces
    
    Important for care home residents' outdoor activities.
    """
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Invalid coordinates")
    
    async with OSMLoader() as loader:
        result = await loader.get_nearby_amenities(
            lat, lon,
            radius_m=radius_m,
            categories=['parks']
        )
        
        if result.get('error'):
            raise HTTPException(status_code=500, detail=result['error'])
        
        parks = result.get('by_category', {}).get('parks', [])
        
        return {
            'location': {'lat': lat, 'lon': lon},
            'radius_m': radius_m,
            'parks': parks,
            'count': len(parks),
            'nearest': parks[0] if parks else None,
            'outdoor_access_rating': 'Excellent' if parks and parks[0]['distance_m'] <= 400 else 'Good' if parks else 'Limited'
        }


@router.get("/cache/stats")
async def get_cache_stats():
    """Get OSM cache statistics"""
    cache = get_cache_manager()
    stats = cache.get_stats()
    
    return {
        "source": "osm",
        "stats": stats.get('by_source', {}).get('osm', {'count': 0, 'total_hits': 0}),
        "total_cache_size_mb": stats.get('db_size_mb', 0)
    }


@router.post("/cache/clear")
async def clear_cache():
    """Clear OSM cache"""
    cache = get_cache_manager()
    cleared = cache.clear_source('osm')
    
    return {
        "message": f"Cleared {cleared} cached entries",
        "source": "osm"
    }
