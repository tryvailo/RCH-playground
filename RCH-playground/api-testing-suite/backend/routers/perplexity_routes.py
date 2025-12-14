"""
Perplexity API Routes
Handles all Perplexity API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from api_clients.perplexity_client import PerplexityAPIClient
from models.schemas import (
    PerplexitySearchRequest,
    PerplexityResearchRequest,
    PerplexityAcademicResearchRequest
)
from utils.client_factory import get_perplexity_client

router = APIRouter(prefix="/api/perplexity", tags=["Perplexity"])


@router.post("/search")
async def perplexity_search(request: PerplexitySearchRequest):
    """Search with Perplexity API for care home related information"""
    try:
        # Validate request
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="query is required")
        
        client = get_perplexity_client()
        
        result = await client.search(
            query=request.query,
            model=request.model,
            max_tokens=request.max_tokens,
            search_recency_filter=request.search_recency_filter
        )
        
        cost = 0.005 if request.model == "sonar-pro" else 0.001  # Approximate cost per request
        
        return {
            "status": "success",
            "content": result.get("content", ""),
            "citations": result.get("citations", []),
            "cost": cost
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Perplexity search error: {error_detail}")
        error_msg = str(e)
        if "validation" in error_msg.lower() or "pydantic" in error_msg.lower() or "field required" in error_msg.lower():
            raise HTTPException(status_code=400, detail=f"Invalid request data: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Perplexity API error: {error_msg}")


@router.post("/reputation")
async def perplexity_reputation(request: PerplexityResearchRequest):
    """Monitor care home reputation using Perplexity"""
    try:
        client = get_perplexity_client()
        
        # Support both formats: separate fields or single location string
        if request.location:
            location_str = request.location
        else:
            location_str = f"{request.address}, {request.city}, {request.postcode}" if request.address else f"{request.city}, {request.postcode}" if request.city else request.postcode or ""
        
        result = await client.monitor_care_home_reputation(
            home_name=request.home_name,
            location=location_str
        )
        
        return {
            "status": "success",
            "home_name": request.home_name,
            "location": location_str,
            "content": result.get("content", ""),
            "citations": result.get("citations", []),
            "cost": 0.005  # sonar-pro cost
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Perplexity reputation error: {error_detail}")
        raise HTTPException(status_code=500, detail=f"Perplexity API error: {str(e)}")


@router.post("/comprehensive-research")
async def perplexity_comprehensive_research(request: PerplexityResearchRequest):
    """Comprehensive research about a care home"""
    try:
        # Validate request
        if not request.home_name or not request.home_name.strip():
            raise HTTPException(status_code=400, detail="home_name is required")
        
        client = get_perplexity_client()
        
        # Build location string from available fields
        location_parts = []
        if request.address and request.address.strip():
            location_parts.append(request.address.strip())
        if request.city and request.city.strip():
            location_parts.append(request.city.strip())
        if request.postcode and request.postcode.strip():
            location_parts.append(request.postcode.strip())
        location_str = ", ".join(location_parts) if location_parts else ""
        
        query = f"""Provide comprehensive information about {request.home_name} {location_str} care home:
        
        1. Recent news and media coverage (last 6 months)
        2. Awards, certifications, or recognition received
        3. Any complaints, issues, or regulatory actions
        4. Community reputation and reviews summary
        5. Key personnel or management changes
        6. Facility improvements or expansions
        7. Any partnerships or affiliations
        
        Focus on factual, verifiable information with sources."""
        
        result = await client.search(
            query=query,
            model="sonar-pro",
            max_tokens=2000,
            search_recency_filter="month"
        )
        
        return {
            "status": "success",
            "home_name": request.home_name,
            "location": location_str,
            "content": result.get("content", ""),
            "citations": result.get("citations", []),
            "cost": 0.005  # sonar-pro cost
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Perplexity comprehensive research error: {error_detail}")
        error_msg = str(e)
        if "validation" in error_msg.lower() or "pydantic" in error_msg.lower() or "field required" in error_msg.lower():
            raise HTTPException(status_code=400, detail=f"Invalid request data: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Perplexity API error: {error_msg}")


@router.post("/advanced-monitoring")
async def perplexity_advanced_monitoring(request: PerplexityResearchRequest):
    """Advanced monitoring with RED FLAGS detection and domain filtering"""
    try:
        if not request.home_name or not request.home_name.strip():
            raise HTTPException(status_code=400, detail="home_name is required")
        
        client = get_perplexity_client()
        
        # Build location string
        location_parts = []
        if request.location and request.location.strip():
            location_str = request.location.strip()
        else:
            if request.address and request.address.strip():
                location_parts.append(request.address.strip())
            if request.city and request.city.strip():
                location_parts.append(request.city.strip())
            if request.postcode and request.postcode.strip():
                location_parts.append(request.postcode.strip())
            location_str = ", ".join(location_parts) if location_parts else ""
        
        # Get date_range from request if available, default to last_7_days
        date_range = request.date_range or 'last_7_days'
        
        result = await client.monitor_care_homes_advanced(
            home_name=request.home_name,
            location=location_str,
            date_range=date_range
        )
        
        return {
            "status": "success",
            "home_name": request.home_name,
            "location": location_str,
            "content": result.get("content", ""),
            "citations": result.get("citations", []),
            "red_flags": result.get("red_flags", []),
            "alert_level": result.get("alert_level", "LOW"),
            "red_flags_count": result.get("red_flags_count", 0),
            "high_severity_count": result.get("high_severity_count", 0),
            "date_range": result.get("date_range", date_range),
            "search_query": result.get("search_query", ""),
            "cost": 0.005  # sonar-pro cost
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Perplexity advanced monitoring error: {error_detail}")
        raise HTTPException(status_code=500, detail=f"Perplexity API error: {str(e)}")


@router.post("/academic-research")
async def perplexity_academic_research(request: PerplexityAcademicResearchRequest):
    """Find academic research on care home topics"""
    try:
        topics = request.topics
        if not topics or len(topics) == 0:
            raise HTTPException(status_code=400, detail="topics must be a non-empty list")
        
        client = get_perplexity_client()
        
        result = await client.find_academic_research(topics=topics)
        
        return {
            "status": "success",
            "research_results": result,
            "topics_searched": topics,
            "cost": 0.005 * len(topics)  # sonar-pro cost per topic
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Perplexity academic research error: {error_detail}")
        raise HTTPException(status_code=500, detail=f"Perplexity API error: {str(e)}")

