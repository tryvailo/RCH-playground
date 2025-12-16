"""
Indeed Search Routes
API endpoints for searching and scraping Indeed UK company reviews
Based on staff-analysis documentation approach
"""
import os
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime

from utils.client_factory import get_firecrawl_client, get_openai_client

router = APIRouter(prefix="/api/indeed", tags=["Indeed Search"])


class IndeedSearchRequest(BaseModel):
    """Request model for Indeed company search"""
    search_term: str
    expected_city: Optional[str] = None
    expected_postcode: Optional[str] = None
    country: str = "UK"
    scrape_reviews: bool = True
    max_reviews: int = 30


class IndeedSearchResponse(BaseModel):
    """Response model for Indeed search"""
    found: bool
    search_term: str
    indeed_slug: Optional[str] = None
    indeed_url: Optional[str] = None
    title: Optional[str] = None
    snippet: Optional[str] = None
    review_count: Optional[int] = None
    validation: Optional[Dict[str, Any]] = None
    reviews: Optional[List[Dict[str, Any]]] = None
    company_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


def _get_indeed_search_service():
    """Get configured Indeed Search Service"""
    from services.indeed_search_service import IndeedSearchService
    from utils.auth import credentials_store
    
    google_api_key = None
    google_search_engine_id = None
    
    # Method 1: From credentials store (config.json)
    creds = credentials_store.get("default")
    if creds and hasattr(creds, 'google_places') and creds.google_places:
        google_api_key = getattr(creds.google_places, 'api_key', None)
        google_search_engine_id = getattr(creds.google_places, 'search_engine_id', None)
    
    # Method 2: From environment variables (fallback)
    if not google_api_key:
        google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
    if not google_search_engine_id:
        google_search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID") or os.getenv("GOOGLE_CSE_ID")
    
    if not google_api_key or not google_search_engine_id:
        raise HTTPException(
            status_code=503,
            detail="Indeed Search not configured. Add 'search_engine_id' to google_places in config.json. See INDEED_SEARCH_SETUP.md for instructions."
        )
    
    firecrawl_client = None
    openai_client = None
    
    try:
        firecrawl_client = get_firecrawl_client()
    except Exception as e:
        print(f"Warning: Firecrawl not available: {e}")
    
    try:
        openai_client = get_openai_client()
    except Exception as e:
        print(f"Warning: OpenAI not available: {e}")
    
    return IndeedSearchService(
        google_api_key=google_api_key,
        google_search_engine_id=google_search_engine_id,
        firecrawl_client=firecrawl_client,
        openai_client=openai_client
    )


@router.post("/search", response_model=IndeedSearchResponse)
async def search_indeed_company(request: IndeedSearchRequest = Body(...)):
    """
    Search for a company on Indeed UK using Google Custom Search.
    
    This endpoint implements the exact algorithm from staff-analysis documentation:
    1. Google Custom Search with site:uk.indeed.com "{search_term}" reviews
    2. Extract Indeed slug from URL
    3. Validate result against expected city/postcode
    4. Optionally scrape reviews using Firecrawl
    
    Environment variables required:
    - GOOGLE_API_KEY: Google Cloud API key with Custom Search API enabled
    - GOOGLE_SEARCH_ENGINE_ID: Custom Search Engine ID configured for uk.indeed.com
    
    Optional:
    - FIRECRAWL_API_KEY: For scraping Indeed reviews
    - OPENAI_API_KEY: For structured extraction of review data
    """
    try:
        service = _get_indeed_search_service()
        
        result = await service.search_and_scrape(
            search_term=request.search_term,
            expected_city=request.expected_city,
            expected_postcode=request.expected_postcode,
            scrape_reviews=request.scrape_reviews,
            max_reviews=request.max_reviews
        )
        
        return IndeedSearchResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Indeed search failed: {str(e)}"
        )


@router.get("/search/{search_term}")
async def search_indeed_company_get(
    search_term: str,
    expected_city: Optional[str] = None,
    expected_postcode: Optional[str] = None,
    scrape_reviews: bool = False
):
    """
    GET endpoint for Indeed company search (without review scraping by default).
    Use POST /search for full search with review scraping.
    """
    try:
        service = _get_indeed_search_service()
        
        result = await service.find_indeed_company(
            search_term=search_term,
            expected_city=expected_city,
            expected_postcode=expected_postcode
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Indeed search failed: {str(e)}"
        )


@router.post("/scrape")
async def scrape_indeed_reviews(
    indeed_url: str = Body(..., embed=True),
    max_reviews: int = Body(50, embed=True)
):
    """
    Scrape reviews from an Indeed company page using Firecrawl.
    
    Requires Indeed reviews URL (e.g., https://uk.indeed.com/cmp/Company-Name/reviews)
    """
    try:
        service = _get_indeed_search_service()
        
        if not service.firecrawl_client:
            raise HTTPException(
                status_code=503,
                detail="Firecrawl not configured. Set FIRECRAWL_API_KEY."
            )
        
        result = await service.scrape_indeed_reviews(
            indeed_url=indeed_url,
            max_reviews=max_reviews
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Indeed scraping failed: {str(e)}"
        )


@router.get("/health")
async def indeed_search_health():
    """Health check for Indeed search service"""
    google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
    google_search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID") or os.getenv("GOOGLE_CSE_ID")
    
    status = {
        "status": "ok" if google_api_key and google_search_engine_id else "degraded",
        "service": "indeed-search",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "google_custom_search": "configured" if google_api_key and google_search_engine_id else "not configured",
            "firecrawl": "unknown",
            "openai": "unknown"
        },
        "required_env_vars": {
            "GOOGLE_API_KEY": "set" if google_api_key else "missing",
            "GOOGLE_SEARCH_ENGINE_ID": "set" if google_search_engine_id else "missing"
        }
    }
    
    try:
        get_firecrawl_client()
        status["components"]["firecrawl"] = "configured"
    except:
        status["components"]["firecrawl"] = "not configured"
    
    try:
        get_openai_client()
        status["components"]["openai"] = "configured"
    except:
        status["components"]["openai"] = "not configured"
    
    return status
