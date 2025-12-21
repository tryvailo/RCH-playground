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


@router.get("/photo/{photo_reference:path}")
async def google_places_photo(photo_reference: str, maxwidth: int = Query(400)):
    """Get photo for a place
    
    Note: photo_reference can be in format:
    - Places API (New): "places/{place_id}/photos/{photo_id}"
    - Legacy API: just the photo reference ID
    """
    try:
        # URL decode the photo_reference in case it was encoded
        from urllib.parse import unquote
        photo_reference = unquote(photo_reference)
        
        client = get_google_places_client()
        
        photo_data = await client.get_photo(photo_reference, maxwidth=maxwidth)
        
        # Generate a safe filename from photo_reference
        safe_filename = photo_reference.split("/")[-1] if "/" in photo_reference else photo_reference
        safe_filename = safe_filename[:50]  # Limit filename length
        
        return Response(
            content=photo_data,
            media_type="image/jpeg",
            headers={"Content-Disposition": f"inline; filename={safe_filename}.jpg"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Places API error: {str(e)}")


@router.get("/{place_id}/popular-times")
async def google_places_popular_times(place_id: str):
    """Get popular times for a place using Google Places New API"""
    try:
        if not place_id:
            raise HTTPException(status_code=400, detail="Place ID is required")
        
        client = get_google_places_client()
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
    """Get average dwell time for a place using Google Places New API"""
    try:
        if not place_id:
            raise HTTPException(status_code=400, detail="Place ID is required")
        
        client = get_google_places_client()
        dwell_time = await client.calculate_dwell_time(place_id)
        
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
    """Get repeat visitor rate for a place using Google Places New API"""
    try:
        if not place_id:
            raise HTTPException(status_code=400, detail="Place ID is required")
        
        client = get_google_places_client()
        repeat_visitors = await client.calculate_repeat_visitor_rate(place_id)
        
        return {
            "status": "success",
            "place_id": place_id,
            "repeat_visitor_rate": repeat_visitors
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Repeat visitors API error: {str(e)}")


@router.get("/{place_id}/visitor-geography")
async def google_places_visitor_geography(place_id: str):
    """Get visitor geography data for a place using Google Places New API"""
    try:
        if not place_id:
            raise HTTPException(status_code=400, detail="Place ID is required")
        
        client = get_google_places_client()
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
    """Get footfall trends for a place using Google Places New API"""
    try:
        if not place_id:
            raise HTTPException(status_code=400, detail="Place ID is required")
        
        client = get_google_places_client()
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
    """Get comprehensive insights for a place using Google Places New API"""
    try:
        if not place_id:
            raise HTTPException(status_code=400, detail="Place ID is required")
        
        client = get_google_places_client()
        insights = await client.get_places_insights(place_id)
        
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
    """Analyze and summarize insights for a place using Google Places New API"""
    try:
        if not place_id:
            raise HTTPException(status_code=400, detail="Place ID is required")
        
        client = get_google_places_client()
        insights = await client.get_places_insights(place_id)
        
        # Generate analysis from insights
        summary = insights.get("summary", {})
        analysis = {
            "place_id": place_id,
            "family_engagement_score": summary.get("family_engagement_score"),
            "quality_indicator": summary.get("quality_indicator"),
            "recommendations": summary.get("recommendations", []),
            "key_insights": [
                f"Dwell time: {insights.get('dwell_time', {}).get('average_dwell_time_minutes', 0)} minutes",
                f"Repeat visitor rate: {insights.get('repeat_visitor_rate', {}).get('repeat_visitor_rate_percent', 0)}%",
                f"Footfall trend: {insights.get('footfall_trends', {}).get('trend_direction', 'Unknown')}"
            ]
        }
        
        return {
            "status": "success",
            "place_id": place_id,
            "analysis": analysis
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

