"""
Firecrawl API Routes
Handles all Firecrawl API endpoints
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime

from api_clients.firecrawl_client import FirecrawlAPIClient
from api_clients.google_places_client import GooglePlacesAPIClient
from models.schemas import (
    FirecrawlAnalyzeRequest,
    FirecrawlUnifiedAnalysisRequest,
    FirecrawlSearchRequest,
    FirecrawlBatchAnalyzeRequest
)
from utils.client_factory import get_firecrawl_client
from utils.error_handler import handle_api_error
from config_manager import get_credentials

router = APIRouter(prefix="/api/firecrawl", tags=["Firecrawl"])


def get_firecrawl_client_with_creds():
    """Get Firecrawl client with credentials"""
    creds = get_credentials()
    return get_firecrawl_client(creds)


@router.post("/analyze")
async def firecrawl_analyze_care_home(request: FirecrawlAnalyzeRequest):
    """Analyze care home website using Firecrawl v2.5 4-phase universal semantic crawling"""
    try:
        url = request.url
        care_home_name = request.care_home_name
        
        client = get_firecrawl_client_with_creds()
        
        # Ensure URL has protocol
        if not url.startswith("http"):
            url = f"https://{url}"
        
        # Use the FULL extraction method (recommended)
        result = await client.extract_care_home_data_full(url, care_home_name)
        
        return {
            "status": "success",
            "data": result,
            "cost_estimate": 0.10  # Approximate per care home
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Firecrawl analyze error: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Firecrawl analysis error: {str(e)}"
        )


@router.post("/dementia-care-analysis")
async def firecrawl_dementia_care_analysis(request: FirecrawlAnalyzeRequest):
    """Extract and evaluate dementia care quality from care home website"""
    try:
        url = request.url
        care_home_name = request.care_home_name
        
        client = get_firecrawl_client_with_creds()
        
        # Ensure URL has protocol
        if not url.startswith("http"):
            url = f"https://{url}"
        
        # Use dementia care quality extraction method with timeout (5 minutes)
        try:
            result = await asyncio.wait_for(
                client.extract_dementia_care_quality(url, care_home_name),
                timeout=300.0  # 5 minutes timeout
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail="Dementia care analysis timed out after 5 minutes. The website may be too large or complex. Please try again or use a different URL."
            )
        
        return {
            "status": "success",
            "data": result,
            "cost_estimate": 0.05  # Approximate cost for dementia analysis
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Firecrawl dementia care analysis error: {error_trace}")
        error_msg = str(e)
        
        # Provide more helpful error messages
        if "No content extracted" in error_msg or "Could not extract" in error_msg:
            raise HTTPException(
                status_code=400,
                detail=f"Could not extract content from the website. Please check if the URL is correct and accessible. Error: {error_msg}"
            )
        elif "timeout" in error_msg.lower():
            raise HTTPException(
                status_code=504,
                detail=f"Request timed out. The website may be too large or slow. Error: {error_msg}"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Firecrawl dementia care analysis error: {error_msg}"
            )


@router.post("/extract-pricing")
async def firecrawl_extract_pricing(request: FirecrawlAnalyzeRequest):
    """Extract pricing information from care home website using Firecrawl + Claude AI"""
    try:
        url = request.url
        care_home_name = request.care_home_name
        
        client = get_firecrawl_client_with_creds()
        
        # Ensure URL has protocol
        if not url.startswith("http"):
            url = f"https://{url}"
        
        # Extract postcode from request if available
        postcode = getattr(request, 'postcode', None)
        
        # Use pricing extraction method with timeout (3 minutes)
        try:
            result = await asyncio.wait_for(
                client.extract_pricing(url, care_home_name, postcode),
                timeout=180.0  # 3 minutes timeout
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail="Pricing extraction timed out after 3 minutes. The website may be too large or complex. Please try again."
            )
        
        return {
            "status": "success",
            "data": result,
            "cost_estimate": 0.03  # Approximate cost for pricing extraction
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Firecrawl pricing extraction error: {error_trace}")
        error_msg = str(e)
        
        if "No content extracted" in error_msg or "Could not extract" in error_msg:
            raise HTTPException(
                status_code=400,
                detail=f"Could not extract content from the website. Please check if the URL is correct and accessible. Error: {error_msg}"
            )
        elif "timeout" in error_msg.lower():
            raise HTTPException(
                status_code=504,
                detail=f"Request timed out. The website may be too large or slow. Error: {error_msg}"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Firecrawl pricing extraction error: {error_msg}"
            )


@router.post("/scrape")
async def firecrawl_scrape_url(
    url: str = Body(..., embed=True),
    formats: Optional[List[str]] = Body(None)
):
    """Scrape a single URL using Firecrawl API v2"""
    try:
        client = get_firecrawl_client_with_creds()
        
        # Ensure URL has protocol
        if not url.startswith("http"):
            url = f"https://{url}"
        
        # Convert string formats to format objects for API v2
        format_objects = None
        if formats:
            format_objects = [{"type": fmt} if isinstance(fmt, str) else fmt for fmt in formats]
        
        result = await client.scrape_url(url, formats=format_objects)
        
        return {
            "status": "success",
            "data": result,
            "cost": 0.0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firecrawl API error: {str(e)}")


@router.post("/crawl")
async def firecrawl_crawl_website(
    url: str = Body(..., embed=True),
    limit: int = Body(50),
    include_paths: Optional[List[str]] = Body(None),
    exclude_paths: Optional[List[str]] = Body(None),
    formats: Optional[List[str]] = Body(None)
):
    """Crawl a website using Firecrawl API v2"""
    try:
        client = get_firecrawl_client_with_creds()
        
        # Ensure URL has protocol
        if not url.startswith("http"):
            url = f"https://{url}"
        
        # Convert string formats to format objects for API v2
        format_objects = None
        if formats:
            format_objects = [{"type": fmt} if isinstance(fmt, str) else fmt for fmt in formats]
        
        result = await client.crawl_website(
            url=url,
            limit=limit,
            include_paths=include_paths,
            exclude_paths=exclude_paths,
            formats=format_objects
        )
        
        return {
            "status": "success",
            "data": result,
            "cost": 0.0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firecrawl API error: {str(e)}")


@router.post("/extract")
async def firecrawl_extract(
    urls: List[str] = Body(...),
    prompt: str = Body(...),
    schema: Optional[Dict[str, Any]] = Body(None)
):
    """Extract structured data from URLs using Firecrawl API v2 extract endpoint"""
    try:
        client = get_firecrawl_client_with_creds()
        
        # Ensure URLs have protocol
        normalized_urls = []
        for url in urls:
            if not url.startswith("http"):
                normalized_urls.append(f"https://{url}")
            else:
                normalized_urls.append(url)
        
        result = await client.extract(
            urls=normalized_urls,
            prompt=prompt,
            schema=schema
        )
        
        return {
            "status": "success",
            "data": result,
            "cost": 0.0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firecrawl API error: {str(e)}")


@router.post("/unified-analysis")
async def firecrawl_unified_analysis(request: FirecrawlUnifiedAnalysisRequest):
    """Unified analysis combining Firecrawl website scraping with Google Places data"""
    try:
        creds = get_credentials()
        
        # Check Firecrawl credentials
        if not creds or not hasattr(creds, 'firecrawl') or not creds.firecrawl:
            raise HTTPException(status_code=400, detail="Firecrawl credentials not configured")
        
        # Check Google Places credentials
        google_places_api_key = None
        if creds and hasattr(creds, 'google_places') and creds.google_places:
            google_places_api_key = getattr(creds.google_places, 'api_key', None)
        
        # Ensure URL has protocol
        website_url = request.website_url
        if not website_url.startswith("http"):
            website_url = f"https://{website_url}"
        
        # Step 1: Analyze website with Firecrawl
        firecrawl_client = get_firecrawl_client(creds)
        try:
            firecrawl_data = await asyncio.wait_for(
                firecrawl_client.extract_care_home_data_full(website_url, request.care_home_name),
                timeout=600.0  # 10 minutes timeout
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail="Firecrawl analysis timed out after 10 minutes. The website may be too large or complex. Try using Firecrawl Only mode instead."
            )
        
        # Step 2: Get Google Places data if available
        google_places_data = None
        google_places_error = None
        if google_places_api_key:
            try:
                google_client = GooglePlacesAPIClient(api_key=google_places_api_key)
                
                # Build search query
                search_query = request.care_home_name
                if request.city:
                    search_query += f", {request.city}"
                if request.postcode:
                    search_query += f" {request.postcode}"
                
                place = await google_client.find_place(search_query)
                
                if place and place.get("place_id"):
                    place_details = await google_client.get_place_details(
                        place["place_id"],
                        fields=["rating", "user_ratings_total", "reviews", "formatted_address", "formatted_phone_number", "website"]
                    )
                    google_places_data = {"place_details": place_details}
                else:
                    google_places_error = "Place not found in Google Places"
            except Exception as e:
                error_detail = handle_api_error(e, "Google Places", "unified_analysis", {"care_home_name": request.care_home_name})
                google_places_error = f"Google Places API error: {error_detail.get('error_message', str(e))}"
                google_places_data = None
        else:
            google_places_error = "Google Places API key not configured"
        
        # Step 3: Combine data
        unified_result = {
            "care_home_name": request.care_home_name,
            "website_url": website_url,
            "address": request.address,
            "city": request.city,
            "postcode": request.postcode,
            "firecrawl_analysis": firecrawl_data,
            "google_places_data": google_places_data,
            "google_places_error": google_places_error if google_places_error else None,
            "analysis_timestamp": datetime.now().isoformat(),
            "data_sources": {
                "firecrawl": True,
                "google_places": google_places_data is not None
            }
        }
        
        return {
            "status": "success",
            "data": unified_result,
            "cost": 0.0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unified analysis error: {str(e)}")


@router.post("/search")
async def firecrawl_search(request: FirecrawlSearchRequest):
    """Perform web search using Firecrawl Search API"""
    try:
        creds = get_credentials()
        client = get_firecrawl_client(creds)
        
        result = await client.web_search(
            query=request.query,
            limit=request.limit,
            sources=request.sources,
            categories=request.categories,
            location=request.location,
            tbs=request.tbs,
            timeout=request.timeout,
            scrape_options=request.scrape_options
        )
        
        return {
            "status": "success",
            "data": result,
            "cost": 0.0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firecrawl search error: {str(e)}")


@router.post("/search/extract-pricing")
async def firecrawl_search_extract_pricing(request: FirecrawlSearchRequest):
    """Search and extract pricing from care home websites"""
    try:
        creds = get_credentials()
        client = get_firecrawl_client(creds)
        
        result = await client.search_and_extract_pricing(
            query=request.query,
            limit=request.limit
        )
        
        return {
            "status": "success",
            "data": result,
            "cost": 0.0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firecrawl search extract pricing error: {str(e)}")


@router.post("/batch-analyze")
async def firecrawl_batch_analyze(request: FirecrawlBatchAnalyzeRequest):
    """Batch analyze multiple care home websites"""
    try:
        creds = get_credentials()
        client = get_firecrawl_client(creds)
        
        results = await client.batch_extract_care_homes(
            urls=request.urls,
            care_home_names=request.care_home_names
        )
        
        return {
            "status": "success",
            "count": len(results),
            "results": results,
            "cost_estimate": 0.10 * len(request.urls)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firecrawl batch analyze error: {str(e)}")

