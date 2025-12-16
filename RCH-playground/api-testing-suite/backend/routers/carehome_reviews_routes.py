"""
CareHome.co.uk Reviews API Routes
Endpoints for scraping and analyzing reviews from carehome.co.uk
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime

from utils.client_factory import get_firecrawl_client, get_openai_client

router = APIRouter(prefix="/api/carehome-reviews", tags=["CareHome.co.uk Reviews"])


class CareHomeSearchRequest(BaseModel):
    """Request model for care home search"""
    name: str
    postcode: Optional[str] = None
    city: Optional[str] = None


class CareHomeAnalysisRequest(BaseModel):
    """Request model for full analysis"""
    name: str
    postcode: Optional[str] = None
    city: Optional[str] = None
    max_reviews: int = 50


class CareHomeDirectRequest(BaseModel):
    """Request model for direct scraping by searchazref"""
    searchazref: str
    max_reviews: int = 50


def _get_carehome_reviews_service():
    """Get configured CareHome Reviews Service"""
    from services.carehome_reviews_service import CareHomeReviewsService
    from utils.auth import credentials_store
    from config_manager import get_credentials
    import os
    
    google_api_key = None
    google_search_engine_id = None
    
    # Method 1: From credentials store (config.json)
    creds = credentials_store.get("default")
    
    # If not in store, load from config
    if not creds:
        creds = get_credentials()
        credentials_store["default"] = creds
    
    if creds and hasattr(creds, 'google_places') and creds.google_places:
        google_api_key = getattr(creds.google_places, 'api_key', None)
        google_search_engine_id = getattr(creds.google_places, 'search_engine_id', None)
    
    # Method 2: From environment variables (fallback)
    if not google_api_key:
        google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_search_engine_id:
        google_search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
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
    
    return CareHomeReviewsService(
        google_api_key=google_api_key or "",
        google_search_engine_id=google_search_engine_id or "",
        firecrawl_client=firecrawl_client,
        openai_client=openai_client
    )


@router.post("/search")
async def search_care_home(request: CareHomeSearchRequest = Body(...)):
    """
    Search for a care home on carehome.co.uk
    
    Returns searchazref ID and URL if found.
    """
    try:
        service = _get_carehome_reviews_service()
        
        result = await service.find_care_home(
            name=request.name,
            postcode=request.postcode,
            city=request.city
        )
        
        return result or {"found": False, "error": "No result"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/analyze")
async def analyze_care_home_reviews(request: CareHomeAnalysisRequest = Body(...)):
    """
    Full analysis pipeline:
    1. Find care home on carehome.co.uk
    2. Scrape all reviews (with pagination)
    3. Extract structured data (reviewer, rating, text)
    4. Perform semantic analysis (aspect-based sentiment)
    5. Calculate staff quality score
    
    Returns:
        - care_home: Basic info
        - carehome_co_uk: CareHome.co.uk profile data
        - reviews: List of extracted reviews
        - analysis: Semantic analysis results including staff_quality_score
    """
    try:
        service = _get_carehome_reviews_service()
        
        result = await service.get_reviews_with_analysis(
            name=request.name,
            postcode=request.postcode,
            city=request.city,
            max_reviews=request.max_reviews
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/scrape-direct")
async def scrape_reviews_direct(request: CareHomeDirectRequest = Body(...)):
    """
    Directly scrape reviews by searchazref ID (skip search step)
    
    Use this if you already know the carehome.co.uk ID.
    """
    try:
        service = _get_carehome_reviews_service()
        
        reviews = await service.scrape_all_reviews(
            searchazref=request.searchazref,
            max_reviews=request.max_reviews
        )
        
        # Analyze scraped reviews
        analysis = service.analyze_reviews_semantically(reviews)
        
        return {
            "searchazref": request.searchazref,
            "url": f"https://www.carehome.co.uk/carehome.cfm/searchazref/{request.searchazref}",
            "reviews": reviews,
            "analysis": analysis,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@router.get("/health")
async def carehome_reviews_health():
    """Health check for CareHome reviews service"""
    from utils.auth import credentials_store
    import os
    
    creds = credentials_store.get("default")
    
    google_api_key = None
    google_search_engine_id = None
    
    if creds and hasattr(creds, 'google_places') and creds.google_places:
        google_api_key = getattr(creds.google_places, 'api_key', None)
        google_search_engine_id = getattr(creds.google_places, 'search_engine_id', None)
    
    firecrawl_available = False
    openai_available = False
    
    try:
        get_firecrawl_client()
        firecrawl_available = True
    except:
        pass
    
    try:
        get_openai_client()
        openai_available = True
    except:
        pass
    
    status = "ok" if firecrawl_available else "degraded"
    
    return {
        "status": status,
        "service": "carehome-reviews",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "google_api_key": "configured" if google_api_key else "not configured",
            "search_engine_id": "configured" if google_search_engine_id else "not configured",
            "firecrawl": "configured" if firecrawl_available else "not configured",
            "openai": "configured" if openai_available else "not configured"
        },
        "capabilities": {
            "search": firecrawl_available,
            "scrape_reviews": firecrawl_available,
            "llm_extraction": firecrawl_available and openai_available,
            "semantic_analysis": True  # Always available (keyword-based)
        }
    }
