"""
Google Places API Routes
Handles all Google Places API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from typing import Dict, Any, Optional
import asyncio

from api_clients.google_places_client import GooglePlacesAPIClient
from utils.client_factory import get_google_places_client

router = APIRouter(prefix="/api/google-places", tags=["Google Places"])


@router.get("/search")
async def google_places_search(
    query: str,
    city: Optional[str] = Query(None),
    postcode: Optional[str] = Query(None)
):
    """Search for a care home by name/address"""
    try:
        client = get_google_places_client()
        
        # Build search query
        search_query = query
        if city:
            search_query += f", {city}"
        if postcode:
            search_query += f" {postcode}"
        
        # Try find_place first
        place = None
        try:
            place = await asyncio.wait_for(client.find_place(search_query), timeout=8)
        except Exception:
            # Fallback to text_search
            try:
                places = await client.text_search(f"{search_query} care home")
                if places and len(places) > 0:
                    place = places[0]
            except Exception:
                pass
        
        if place:
            # Ensure place_id exists
            if not place.get("place_id"):
                return {
                    "status": "error",
                    "message": "Place ID is missing from search result",
                    "cost": 0.032
                }
            
            # Get detailed information
            details = await client.get_place_details(
                place["place_id"],
                fields=[
                    "name", "rating", "user_ratings_total", "reviews",
                    "formatted_phone_number", "website", "opening_hours",
                    "photos", "formatted_address", "geometry", "types",
                    "business_status", "price_level", "vicinity"
                ]
            )
            
            # Ensure place_id is preserved in details
            if not details.get("place_id"):
                details["place_id"] = place["place_id"]
            
            return {
                "status": "success",
                "place": details,
                "cost": 0.017
            }
        else:
            return {
                "status": "not_found",
                "message": f"No care home found matching '{query}'",
                "cost": 0.032
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Places API error: {str(e)}")


@router.get("/nearby")
async def google_places_nearby(
    latitude: float,
    longitude: float,
    radius: int = Query(1000),
    place_type: Optional[str] = Query(None)
):
    """Search for care homes near a location"""
    try:
        client = get_google_places_client()
        
        places = await client.nearby_search(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            place_type=place_type or "nursing_home"
        )
        
        return {
            "status": "success",
            "count": len(places),
            "places": places,
            "cost": 0.032 * len(places)  # Approximate cost
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Places API error: {str(e)}")


@router.get("/details/{place_id}")
async def google_places_details(place_id: str):
    """Get detailed information for a place"""
    try:
        if not place_id:
            raise HTTPException(status_code=400, detail="Place ID is required")
        
        client = get_google_places_client()
        
        details = await client.get_place_details(
            place_id,
            fields=[
                "name", "rating", "user_ratings_total", "reviews",
                "formatted_phone_number", "website", "opening_hours",
                "photos", "formatted_address", "geometry", "types",
                "business_status", "price_level", "vicinity"
            ]
        )
        
        # Ensure place_id is always present in details
        if not details.get("place_id"):
            details["place_id"] = place_id
        
        return {
            "status": "success",
            "place": details,
            "cost": 0.017
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Places API error: {str(e)}")


@router.get("/photo/{photo_reference}")
async def google_places_photo(photo_reference: str, maxwidth: int = Query(400)):
    """Get photo for a place"""
    try:
        client = get_google_places_client()
        
        photo_data = await client.get_photo(photo_reference, maxwidth=maxwidth)
        
        return Response(
            content=photo_data,
            media_type="image/jpeg",
            headers={"Content-Disposition": f"inline; filename={photo_reference}.jpg"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Places API error: {str(e)}")


@router.get("/{place_id}/popular-times")
async def google_places_popular_times(place_id: str):
    """Get popular times for a place (BestTime API integration)"""
    try:
        if not place_id:
            raise HTTPException(status_code=400, detail="Place ID is required")
        
        from utils.client_factory import get_besttime_client
        from utils.auth import credentials_store
        
        # Check if BestTime credentials are configured
        # BestTime uses private_key and public_key, not api_key, so we check directly
        creds = credentials_store.get("default")
        if not creds:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        besttime_creds = getattr(creds, 'besttime', None)
        if not besttime_creds:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        private_key = getattr(besttime_creds, 'private_key', None)
        public_key = getattr(besttime_creds, 'public_key', None)
        if not private_key or not public_key:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        client = get_besttime_client()
        popular_times = await client.get_popular_times(place_id)
        
        return {
            "status": "success",
            "place_id": place_id,
            "popular_times": popular_times
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Popular times API error: {str(e)}")


@router.get("/{place_id}/dwell-time")
async def google_places_dwell_time(place_id: str):
    """Get average dwell time for a place"""
    try:
        if not place_id:
            raise HTTPException(status_code=400, detail="Place ID is required")
        
        from utils.client_factory import get_besttime_client
        from utils.auth import credentials_store
        
        # Check if BestTime credentials are configured
        # BestTime uses private_key and public_key, not api_key, so we check directly
        creds = credentials_store.get("default")
        if not creds:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        besttime_creds = getattr(creds, 'besttime', None)
        if not besttime_creds:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        private_key = getattr(besttime_creds, 'private_key', None)
        public_key = getattr(besttime_creds, 'public_key', None)
        if not private_key or not public_key:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        client = get_besttime_client()
        dwell_time = await client.get_dwell_time(place_id)
        
        return {
            "status": "success",
            "place_id": place_id,
            "dwell_time": dwell_time
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dwell time API error: {str(e)}")


@router.get("/{place_id}/repeat-visitors")
async def google_places_repeat_visitors(place_id: str):
    """Get repeat visitor rate for a place"""
    try:
        if not place_id:
            raise HTTPException(status_code=400, detail="Place ID is required")
        
        from utils.client_factory import get_besttime_client
        from utils.auth import credentials_store
        
        # Check if BestTime credentials are configured
        # BestTime uses private_key and public_key, not api_key, so we check directly
        creds = credentials_store.get("default")
        if not creds:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        besttime_creds = getattr(creds, 'besttime', None)
        if not besttime_creds:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        private_key = getattr(besttime_creds, 'private_key', None)
        public_key = getattr(besttime_creds, 'public_key', None)
        if not private_key or not public_key:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        client = get_besttime_client()
        repeat_visitors = await client.get_repeat_visitor_rate(place_id)
        
        return {
            "status": "success",
            "place_id": place_id,
            "repeat_visitors": repeat_visitors
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Repeat visitors API error: {str(e)}")


@router.get("/{place_id}/visitor-geography")
async def google_places_visitor_geography(place_id: str):
    """Get visitor geography data for a place"""
    try:
        if not place_id:
            raise HTTPException(status_code=400, detail="Place ID is required")
        
        from utils.client_factory import get_besttime_client
        from utils.auth import credentials_store
        
        # Check if BestTime credentials are configured
        # BestTime uses private_key and public_key, not api_key, so we check directly
        creds = credentials_store.get("default")
        if not creds:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        besttime_creds = getattr(creds, 'besttime', None)
        if not besttime_creds:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        private_key = getattr(besttime_creds, 'private_key', None)
        public_key = getattr(besttime_creds, 'public_key', None)
        if not private_key or not public_key:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        client = get_besttime_client()
        geography = await client.get_visitor_geography(place_id)
        
        return {
            "status": "success",
            "place_id": place_id,
            "visitor_geography": geography
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visitor geography API error: {str(e)}")


@router.get("/{place_id}/footfall-trends")
async def google_places_footfall_trends(place_id: str, months: int = Query(12)):
    """Get footfall trends for a place"""
    try:
        if not place_id:
            raise HTTPException(status_code=400, detail="Place ID is required")
        
        from utils.client_factory import get_besttime_client
        from utils.auth import credentials_store
        
        # Check if BestTime credentials are configured
        # BestTime uses private_key and public_key, not api_key, so we check directly
        creds = credentials_store.get("default")
        if not creds:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        besttime_creds = getattr(creds, 'besttime', None)
        if not besttime_creds:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        private_key = getattr(besttime_creds, 'private_key', None)
        public_key = getattr(besttime_creds, 'public_key', None)
        if not private_key or not public_key:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        client = get_besttime_client()
        trends = await client.get_footfall_trends(place_id, months=months)
        
        return {
            "status": "success",
            "place_id": place_id,
            "footfall_trends": trends
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Footfall trends API error: {str(e)}")


@router.get("/{place_id}/insights")
async def google_places_insights(place_id: str):
    """Get comprehensive insights for a place"""
    try:
        if not place_id:
            raise HTTPException(status_code=400, detail="Place ID is required")
        
        from utils.client_factory import get_besttime_client
        from utils.auth import credentials_store
        
        # Check if BestTime credentials are configured before attempting to get client
        # BestTime uses private_key and public_key, not api_key, so we check directly
        creds = credentials_store.get("default")
        if not creds:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        besttime_creds = getattr(creds, 'besttime', None)
        if not besttime_creds:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        private_key = getattr(besttime_creds, 'private_key', None)
        public_key = getattr(besttime_creds, 'public_key', None)
        if not private_key or not public_key:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        client = get_besttime_client()
        insights = await client.get_all_insights(place_id)
        
        return {
            "status": "success",
            "place_id": place_id,
            "insights": insights
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights API error: {str(e)}")


@router.post("/{place_id}/analyze")
async def analyze_places_insights(place_id: str):
    """Analyze and summarize insights for a place"""
    try:
        if not place_id:
            raise HTTPException(status_code=400, detail="Place ID is required")
        
        from utils.client_factory import get_besttime_client
        from utils.auth import credentials_store
        
        # Check if BestTime credentials are configured
        # BestTime uses private_key and public_key, not api_key, so we check directly
        creds = credentials_store.get("default")
        if not creds:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        besttime_creds = getattr(creds, 'besttime', None)
        if not besttime_creds:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        private_key = getattr(besttime_creds, 'private_key', None)
        public_key = getattr(besttime_creds, 'public_key', None)
        if not private_key or not public_key:
            raise HTTPException(
                status_code=400,
                detail="BestTime credentials not configured. Please configure BestTime API credentials (private_key and public_key) in the settings."
            )
        
        client = get_besttime_client()
        analysis = await client.analyze_place_insights(place_id)
        
        return {
            "status": "success",
            "place_id": place_id,
            "analysis": analysis
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

