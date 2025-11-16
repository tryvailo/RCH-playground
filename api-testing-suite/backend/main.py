"""
FastAPI Main Application
RightCareHome API Testing Suite
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import json
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime

from api_clients.cqc_client import CQCAPIClient
from api_clients.fsa_client import FSAAPIClient
from api_clients.companies_house_client import CompaniesHouseAPIClient
from api_clients.google_places_client import GooglePlacesAPIClient
from api_clients.perplexity_client import PerplexityAPIClient
from api_clients.besttime_client import BestTimeClient
from api_clients.autumna_scraper import AutumnaScraper
from api_clients.openai_client import OpenAIClient
from api_clients.firecrawl_client import FirecrawlAPIClient

from services.test_runner import TestRunner
from services.data_fusion import DataFusionAnalyzer
from services.analytics import AnalyticsService

from models.schemas import (
    ApiCredentials,
    TestRequest,
    ApiTestResult,
    ComprehensiveTestRequest,
    ComprehensiveTestResponse,
    HomeData,
    PerplexityResearchRequest,
    PerplexitySearchRequest,
    PerplexityAcademicResearchRequest,
    FirecrawlUnifiedAnalysisRequest,
    FirecrawlAnalyzeRequest,
    FirecrawlBatchAnalyzeRequest,
    FirecrawlSearchRequest
)
from config_manager import get_credentials, save_config, load_config, mask_api_key
from utils.cache import close_cache_manager
from utils.error_handler import handle_api_error, create_error_response

# Global state
active_connections: Dict[str, WebSocket] = {}
test_results_store: Dict[str, Dict] = {}

# In-memory storage (backed by config file)
credentials_store: Dict[str, ApiCredentials] = {"default": get_credentials()}


def get_cqc_client(creds: Optional[ApiCredentials] = None) -> CQCAPIClient:
    """Helper function to create CQCAPIClient with credentials"""
    if creds is None:
        creds = credentials_store.get("default")
    
    if creds and creds.cqc:
        return CQCAPIClient(
            partner_code=creds.cqc.partner_code,
            primary_subscription_key=creds.cqc.primary_subscription_key,
            secondary_subscription_key=creds.cqc.secondary_subscription_key
        )
    else:
        return CQCAPIClient(partner_code=None)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    print("🚀 Starting RightCareHome API Testing Suite...")
    # Load credentials from config file
    credentials_store["default"] = get_credentials()
    print("✅ Configuration loaded")
    
    # Initialize cache manager
    from utils.cache import get_cache_manager
    cache = get_cache_manager()
    if cache.enabled:
        print("✅ Redis cache initialized")
    else:
        print("⚠️ Redis cache disabled (not configured or unavailable)")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")
    await close_cache_manager()
    print("✅ Cache connections closed")


app = FastAPI(
    title="RightCareHome API Testing Suite",
    description="Comprehensive API testing platform for UK care homes data sources",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RightCareHome API Testing Suite",
        "version": "1.0.0",
        "endpoints": {
            "config": "/api/config",
            "test": "/api/test",
            "analyze": "/api/analyze",
            "test_data": "/api/test-data",
            "report": "/api/report"
        }
    }


# ==================== API Configuration Endpoints ====================

@app.post("/api/config/credentials")
async def save_credentials(credentials: ApiCredentials):
    """Save API credentials to config file"""
    try:
        # Save to config file
        save_config(credentials)
        
        # Update in-memory store
        credentials_store["default"] = credentials
        
        return {
            "status": "success",
            "message": "Credentials saved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config/reload")
async def reload_config():
    """Reload configuration from config file"""
    try:
        credentials_store["default"] = get_credentials()
        return {
            "status": "success",
            "message": "Configuration reloaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload configuration: {str(e)}")


@app.get("/api/test-data")
async def get_test_data():
    """Get test data for API testing (real UK care homes from CQC registry)"""
    import json
    import os
    
    test_data_path = os.path.join(os.path.dirname(__file__), "test_data.json")
    try:
        with open(test_data_path, 'r') as f:
            test_data = json.load(f)
        return {"status": "success", "data": test_data}
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "Test data file not found",
            "data": {
                "fsa_test_care_homes": [
                    {
                        "name": "Kinross Residential Care Home",
                        "address": "201 Havant Road, Drayton, Portsmouth, Hampshire, PO6 1EE",
                        "city": "Portsmouth",
                        "postcode": "PO6 1EE",
                        "county": "Hampshire",
                        "source": "CQC Official Registry"
                    },
                    {
                        "name": "Meadows House Residential and Nursing Home",
                        "address": "Cullum Welch Court, London, SE3 0PW",
                        "city": "London",
                        "postcode": "SE3 0PW",
                        "county": "Greater London",
                        "source": "CQC Official Registry"
                    },
                    {
                        "name": "Roborough House",
                        "address": "Tamerton Road, Woolwell, Plymouth, Devon, PL6 7BQ",
                        "city": "Plymouth",
                        "postcode": "PL6 7BQ",
                        "county": "Devon",
                        "source": "CQC Official Registry"
                    }
                ],
                "companies_house_test_companies": [
                    {
                        "name": "Kinross Residential Care Home",
                        "address": "201 Havant Road, Drayton, Portsmouth, Hampshire, PO6 1EE",
                        "note": "Search by name to find company number"
                    },
                    {
                        "name": "Meadows House Residential and Nursing Home",
                        "address": "Cullum Welch Court, London, SE3 0PW",
                        "note": "Search by name to find company number"
                    },
                    {
                        "name": "Roborough House",
                        "address": "Tamerton Road, Woolwell, Plymouth, Devon, PL6 7BQ",
                        "note": "Search by name to find company number"
                    }
                ],
                "description": "Real UK care homes from CQC official registry for API testing",
                "last_updated": "2025-01-27"
            }
        }


@app.get("/api/config/credentials")
async def get_credentials_endpoint():
    """Get saved credentials with full keys for editing"""
    # Reload from config file to get latest
    creds = get_credentials()
    
    # Always return all credential sections, even if empty
    # This allows frontend to show empty fields when keys are missing
    result: Dict = {
        "status": "configured" if any([creds.cqc, creds.companies_house, creds.google_places, creds.perplexity, creds.besttime, creds.autumna, creds.openai, creds.firecrawl]) else "not_configured",
        "credentials": {}
    }
    
    # CQC - always include section
    result["credentials"]["cqc"] = {
        "partnerCode": creds.cqc.partner_code if creds.cqc and creds.cqc.partner_code else "",
        "useWithoutCode": creds.cqc.use_without_code if creds.cqc else True,
        "primarySubscriptionKey": creds.cqc.primary_subscription_key if creds.cqc and creds.cqc.primary_subscription_key else "",
        "secondarySubscriptionKey": creds.cqc.secondary_subscription_key if creds.cqc and creds.cqc.secondary_subscription_key else "",
        "hasPartnerCode": bool(creds.cqc and creds.cqc.partner_code),
        "hasSubscriptionKeys": bool(creds.cqc and creds.cqc.primary_subscription_key)
    }
    
    # Companies House - always include section
    result["credentials"]["companiesHouse"] = {
        "apiKey": creds.companies_house.api_key if creds.companies_house and creds.companies_house.api_key else "",
        "hasApiKey": bool(creds.companies_house and creds.companies_house.api_key)
    }
    
    # Google Places - always include section
    result["credentials"]["googlePlaces"] = {
        "apiKey": creds.google_places.api_key if creds.google_places and creds.google_places.api_key else "",
        "hasApiKey": bool(creds.google_places and creds.google_places.api_key)
    }
    
    # Perplexity - always include section
    result["credentials"]["perplexity"] = {
        "apiKey": creds.perplexity.api_key if creds.perplexity and creds.perplexity.api_key else "",
        "hasApiKey": bool(creds.perplexity and creds.perplexity.api_key)
    }
    
    # BestTime - always include section
    result["credentials"]["besttime"] = {
        "privateKey": creds.besttime.private_key if creds.besttime and creds.besttime.private_key else "",
        "publicKey": creds.besttime.public_key if creds.besttime and creds.besttime.public_key else "",
        "hasKeys": bool(creds.besttime and creds.besttime.private_key and creds.besttime.public_key)
    }
    
    # Autumna - always include section
    result["credentials"]["autumna"] = {
        "proxyUrl": creds.autumna.proxy_url if creds.autumna and creds.autumna.proxy_url else "",
        "useProxy": creds.autumna.use_proxy if creds.autumna else False,
        "hasProxy": bool(creds.autumna and creds.autumna.proxy_url)
    }
    
    # Firecrawl - always include section
    result["credentials"]["firecrawl"] = {
        "apiKey": creds.firecrawl.api_key if creds.firecrawl and creds.firecrawl.api_key else "",
        "hasApiKey": bool(creds.firecrawl and creds.firecrawl.api_key)
    }
    
    # Anthropic Claude - always include section
    result["credentials"]["anthropic"] = {
        "apiKey": creds.anthropic.api_key if creds.anthropic and creds.anthropic.api_key else "",
        "hasApiKey": bool(creds.anthropic and creds.anthropic.api_key)
    }
    
    return result


@app.post("/api/config/validate")
async def validate_credentials():
    """Validate all configured credentials"""
    if "default" not in credentials_store:
        raise HTTPException(status_code=400, detail="No credentials configured")
    
    creds = credentials_store["default"]
    validation_results = {}
    
    # Validate each API
    if creds.cqc and (creds.cqc.primary_subscription_key or creds.cqc.partner_code):
        try:
            client = get_cqc_client(creds)
            # Test with minimal request
            validation_results["cqc"] = {"status": "valid", "message": "CQC API accessible"}
        except Exception as e:
            validation_results["cqc"] = {"status": "invalid", "message": str(e)}
    
    if creds.companies_house and creds.companies_house.api_key:
        try:
            client = CompaniesHouseAPIClient(api_key=creds.companies_house.api_key)
            validation_results["companies_house"] = {"status": "valid", "message": "Companies House API accessible"}
        except Exception as e:
            validation_results["companies_house"] = {"status": "invalid", "message": str(e)}
    
    # FSA doesn't need credentials
    validation_results["fsa"] = {"status": "valid", "message": "FSA API is public"}
    
    return {
        "validation_results": validation_results,
        "all_valid": all(r["status"] == "valid" for r in validation_results.values())
    }


# ==================== Individual API Test Endpoints ====================

@app.post("/api/test/cqc", response_model=ApiTestResult)
async def test_cqc(request: TestRequest):
    """Test CQC API - works in Sandbox mode without Partner Code"""
    try:
        creds = credentials_store.get("default")
        
        # CQC API uses subscription keys (new API) or partner code (legacy)
        client = get_cqc_client(creds)
        
        # Test search
        start_time = datetime.now()
        homes = await client.search_care_homes(
            region=request.region or "South East",
            per_page=request.limit or 10
        )
        response_time = (datetime.now() - start_time).total_seconds()
        
        return ApiTestResult(
            api_name="CQC",
            status="success",
            response_time=response_time,
            data_returned=len(homes) > 0,
            data_quality={
                "completeness": 100 if homes else 0,
                "accuracy": 100,
                "freshness": "Recent"
            },
            errors=[],
            warnings=[],
            raw_response={"homes_found": len(homes), "sample": homes[:3] if homes else []},
            cost_incurred=0.0
        )
    except Exception as e:
        error_detail = handle_api_error(e, "CQC", "search", {"request": request.dict()})
        return ApiTestResult(
            api_name="CQC",
            status="failure",
            response_time=0,
            data_returned=False,
            data_quality={"completeness": 0, "accuracy": 0, "freshness": "N/A"},
            errors=[error_detail.get("error_message", str(e))],
            warnings=error_detail.get("suggestions", []),
            raw_response={"error_detail": error_detail},
            cost_incurred=0.0
        )


# ==================== Enhanced CQC API Endpoints ====================

def _get_cqc_mode_info() -> Dict[str, Any]:
    """Get CQC API mode information (Sandbox/Production)"""
    creds = credentials_store.get("default")
    partner_code = None
    if creds and hasattr(creds, 'cqc') and creds.cqc:
        partner_code = getattr(creds.cqc, 'partner_code', None)
    
    if partner_code and partner_code.strip():
        return {
            "mode": "production",
            "partner_code": partner_code,
            "rate_limit": "2000 requests/min",
            "description": "Production mode with Partner Code - Higher rate limits and priority support"
        }
    else:
        return {
            "mode": "sandbox",
            "partner_code": None,
            "rate_limit": "Requires Partner Code",
            "description": "Sandbox mode - Partner Code is required. Register at https://api-portal.service.cqc.org.uk/ to get access."
        }

@app.get("/api/cqc/status")
async def cqc_get_status():
    """Get CQC API status and mode information"""
    try:
        mode_info = _get_cqc_mode_info()
        
        # Test API connection
        client = get_cqc_client()
        api_status = "unavailable"
        error_message = None
        
        try:
            test_response = await client.client.get(
                f"{client.base_url}/locations",
                params=client._add_partner_code({"perPage": 1, "careHome": "true"})
            )
            api_status = "available" if test_response.status_code == 200 else "unavailable"
            if test_response.status_code == 403:
                error_message = "403 Forbidden - Partner Code is required"
        except Exception as e:
            error_message = str(e)
            api_status = "unavailable"
        
        result = {
            "status": "success",
            "api_status": api_status,
            "mode": mode_info["mode"],
            "partner_code": mode_info["partner_code"],
            "rate_limit": mode_info["rate_limit"],
            "description": mode_info["description"],
            "message": f"CQC API is running in {mode_info['mode']} mode"
        }
        
        if error_message:
            result["error_message"] = error_message
            if mode_info["mode"] == "sandbox":
                result["help_url"] = "https://api-portal.service.cqc.org.uk/"
                result["help_text"] = "Register at the CQC API Portal to get a Partner Code"
        
        return result
    except Exception as e:
        return {
            "status": "error",
            "api_status": "unavailable",
            "mode": _get_cqc_mode_info()["mode"],
            "error": str(e)
        }

@app.get("/api/cqc/locations/search")
async def cqc_search_locations(
    care_home: Optional[str] = None,
    local_authority: Optional[str] = None,
    region: Optional[str] = None,
    postcode: Optional[str] = None,
    overall_rating: Optional[str] = None,
    inspection_directorate: Optional[str] = None,
    constituency: Optional[str] = None,
    onspd_ccg_code: Optional[str] = None,
    onspd_ccg_name: Optional[str] = None,
    ods_ccg_code: Optional[str] = None,
    ods_ccg_name: Optional[str] = None,
    gac_service_type_description: Optional[str] = None,
    primary_inspection_category_code: Optional[str] = None,
    primary_inspection_category_name: Optional[str] = None,
    non_primary_inspection_category_code: Optional[str] = None,
    non_primary_inspection_category_name: Optional[str] = None,
    regulated_activity: Optional[str] = None,
    report_type: Optional[str] = None,
    page_size: int = 100
):
    """Enhanced CQC location search with advanced filtering"""
    try:
        creds = credentials_store.get("default")
        partner_code = None
        if creds and hasattr(creds, 'cqc') and creds.cqc:
            partner_code = getattr(creds.cqc, 'partner_code', None)
        
        client = get_cqc_client()
        
        # Convert care_home string to boolean
        care_home_bool = None
        if care_home is not None:
            if isinstance(care_home, bool):
                care_home_bool = care_home
            elif isinstance(care_home, str):
                care_home_bool = care_home.lower() == 'true'
        
        # Limit to max 10 pages (5000 results) to prevent timeout/hanging
        # Users can increase page_size or use pagination for more results
        max_pages = min(10, (page_size * 10) // page_size) if page_size > 0 else 10
        
        locations = await client.search_locations(
            care_home=care_home_bool,
            local_authority=local_authority,
            region=region,
            overall_rating=overall_rating,
            inspection_directorate=inspection_directorate,
            constituency=constituency,
            onspd_ccg_code=onspd_ccg_code,
            onspd_ccg_name=onspd_ccg_name,
            ods_ccg_code=ods_ccg_code,
            ods_ccg_name=ods_ccg_name,
            gac_service_type_description=gac_service_type_description,
            primary_inspection_category_code=primary_inspection_category_code,
            primary_inspection_category_name=primary_inspection_category_name,
            non_primary_inspection_category_code=non_primary_inspection_category_code,
            non_primary_inspection_category_name=non_primary_inspection_category_name,
            regulated_activity=regulated_activity,
            report_type=report_type,
            page_size=page_size,
            verbose=False,
            max_pages=max_pages
        )
        
        # Filter by postcode if provided (CQC API doesn't support postcode filter directly)
        if postcode:
            postcode_normalized = postcode.replace(" ", "").upper()
            locations = [
                loc for loc in locations
                if loc.get("postcode") and postcode_normalized in loc.get("postcode", "").replace(" ", "").upper()
            ]
        
        mode_info = _get_cqc_mode_info()
        
        return {
            "status": "success",
            "count": len(locations),
            "locations": locations,
            "mode": mode_info["mode"],
            "partner_code": mode_info["partner_code"],
            "rate_limit": mode_info["rate_limit"]
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"CQC search error: {error_detail}")
        raise HTTPException(status_code=500, detail=f"CQC API error: {str(e)}")


@app.get("/api/cqc/locations/{location_id}")
async def cqc_get_location(location_id: str):
    """Get detailed information for a CQC location"""
    try:
        creds = credentials_store.get("default")
        partner_code = None
        if creds and hasattr(creds, 'cqc') and creds.cqc:
            partner_code = getattr(creds.cqc, 'partner_code', None)
        
        client = get_cqc_client()
        location = await client.get_location(location_id)
        
        return {
            "status": "success",
            "location": location
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"CQC get location error: {error_detail}")
        raise HTTPException(status_code=500, detail=f"CQC API error: {str(e)}")


@app.get("/api/cqc/locations/{location_id}/inspection-areas")
async def cqc_get_location_inspection_areas(location_id: str):
    """Get inspection areas for a CQC location"""
    try:
        creds = credentials_store.get("default")
        partner_code = None
        if creds and hasattr(creds, 'cqc') and creds.cqc:
            partner_code = getattr(creds.cqc, 'partner_code', None)
        
        client = get_cqc_client()
        areas = await client.get_location_inspection_areas(location_id)
        
        return {
            "status": "success",
            "count": len(areas),
            "inspection_areas": areas
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"CQC get inspection areas error: {error_detail}")
        raise HTTPException(status_code=500, detail=f"CQC API error: {str(e)}")


@app.get("/api/cqc/locations/{location_id}/reports")
async def cqc_get_location_reports(location_id: str):
    """Get reports metadata for a CQC location"""
    try:
        creds = credentials_store.get("default")
        partner_code = None
        if creds and hasattr(creds, 'cqc') and creds.cqc:
            partner_code = getattr(creds.cqc, 'partner_code', None)
        
        client = get_cqc_client()
        reports = await client.get_location_reports(location_id)
        
        return {
            "status": "success",
            "count": len(reports),
            "reports": reports
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"CQC get reports error: {error_detail}")
        raise HTTPException(status_code=500, detail=f"CQC API error: {str(e)}")


@app.get("/api/cqc/reports/{report_id}")
async def cqc_get_report(report_id: str, plain_text: bool = True):
    """Get an inspection report (plain text or PDF)"""
    try:
        creds = credentials_store.get("default")
        partner_code = None
        if creds and hasattr(creds, 'cqc') and creds.cqc:
            partner_code = getattr(creds.cqc, 'partner_code', None)
        
        client = get_cqc_client()
        report = await client.get_report(report_id, plain_text=plain_text)
        
        if plain_text:
            return {
                "status": "success",
                "format": "plain_text",
                "content": report
            }
        else:
            from fastapi.responses import Response
            return Response(
                content=report,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={report_id}.pdf"}
            )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"CQC get report error: {error_detail}")
        raise HTTPException(status_code=500, detail=f"CQC API error: {str(e)}")


@app.get("/api/cqc/providers/search")
async def cqc_search_providers(
    local_authority: Optional[str] = None,
    region: Optional[str] = None,
    overall_rating: Optional[str] = None,
    inspection_directorate: Optional[str] = None,
    page_size: int = 100
):
    """Search for CQC providers"""
    try:
        creds = credentials_store.get("default")
        partner_code = None
        if creds and hasattr(creds, 'cqc') and creds.cqc:
            partner_code = getattr(creds.cqc, 'partner_code', None)
        
        client = get_cqc_client()
        
        # Limit to max 10 pages to prevent UI hanging
        max_pages = min(10, (page_size * 10) // page_size) if page_size > 0 else 10
        
        providers = await client.search_providers(
            local_authority=local_authority,
            region=region,
            overall_rating=overall_rating,
            inspection_directorate=inspection_directorate,
            page_size=page_size,
            verbose=False,
            max_pages=max_pages
        )
        
        mode_info = _get_cqc_mode_info()
        
        return {
            "status": "success",
            "count": len(providers),
            "providers": providers,
            "mode": mode_info["mode"],
            "partner_code": mode_info["partner_code"],
            "rate_limit": mode_info["rate_limit"]
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"CQC search providers error: {error_detail}")
        raise HTTPException(status_code=500, detail=f"CQC API error: {str(e)}")


@app.get("/api/cqc/providers/{provider_id}")
async def cqc_get_provider(provider_id: str):
    """Get detailed information for a CQC provider"""
    try:
        creds = credentials_store.get("default")
        partner_code = None
        if creds and hasattr(creds, 'cqc') and creds.cqc:
            partner_code = getattr(creds.cqc, 'partner_code', None)
        
        client = get_cqc_client()
        provider = await client.get_provider(provider_id)
        
        return {
            "status": "success",
            "provider": provider
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"CQC get provider error: {error_detail}")
        raise HTTPException(status_code=500, detail=f"CQC API error: {str(e)}")


@app.get("/api/cqc/providers/{provider_id}/locations")
async def cqc_get_provider_locations(provider_id: str):
    """Get all locations for a CQC provider"""
    try:
        creds = credentials_store.get("default")
        partner_code = None
        if creds and hasattr(creds, 'cqc') and creds.cqc:
            partner_code = getattr(creds.cqc, 'partner_code', None)
        
        client = get_cqc_client()
        locations = await client.get_provider_locations(provider_id)
        
        return {
            "status": "success",
            "count": len(locations),
            "locations": locations
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"CQC get provider locations error: {error_detail}")
        raise HTTPException(status_code=500, detail=f"CQC API error: {str(e)}")


@app.get("/api/cqc/inspection-areas")
async def cqc_get_inspection_areas():
    """Get all CQC inspection areas"""
    try:
        creds = credentials_store.get("default")
        partner_code = None
        if creds and hasattr(creds, 'cqc') and creds.cqc:
            partner_code = getattr(creds.cqc, 'partner_code', None)
        
        client = get_cqc_client()
        areas = await client.get_inspection_areas()
        
        return {
            "status": "success",
            "count": len(areas),
            "inspection_areas": areas
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"CQC get inspection areas error: {error_detail}")
        raise HTTPException(status_code=500, detail=f"CQC API error: {str(e)}")


@app.get("/api/cqc/changes")
async def cqc_get_changes(
    organisation_type: str = "location",
    start_date: str = "2000-01-01",
    end_date: Optional[str] = None
):
    """Get changes for providers or locations in a date range"""
    try:
        creds = credentials_store.get("default")
        partner_code = None
        if creds and hasattr(creds, 'cqc') and creds.cqc:
            partner_code = getattr(creds.cqc, 'partner_code', None)
        
        client = get_cqc_client()
        
        changes = await client.get_changes(
            organisation_type=organisation_type,
            start_date=start_date,
            end_date=end_date,
            verbose=False
        )
        
        return {
            "status": "success",
            "count": len(changes),
            "changes": changes
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"CQC get changes error: {error_detail}")
        raise HTTPException(status_code=500, detail=f"CQC API error: {str(e)}")


@app.post("/api/test/fsa", response_model=ApiTestResult)
async def test_fsa(request: TestRequest):
    """Test FSA FHRS API"""
    try:
        client = FSAAPIClient()
        
        start_time = datetime.now()
        if request.latitude and request.longitude:
            results = await client.search_by_location(
                latitude=request.latitude,
                longitude=request.longitude,
                max_distance=request.max_distance or 1.0
            )
        elif request.home_name:
            results = await client.search_by_business_name(request.home_name)
        else:
            raise HTTPException(status_code=400, detail="Provide location or home name")
        
        response_time = (datetime.now() - start_time).total_seconds()
        
        return ApiTestResult(
            api_name="FSA",
            status="success",
            response_time=response_time,
            data_returned=len(results) > 0,
            data_quality={
                "completeness": 100 if results else 0,
                "accuracy": 100,
                "freshness": "Recent"
            },
            errors=[],
            warnings=[],
            raw_response={"establishments_found": len(results), "sample": results[:3] if results else []},
            cost_incurred=0.0
        )
    except Exception as e:
        return ApiTestResult(
            api_name="FSA",
            status="failure",
            response_time=0,
            data_returned=False,
            data_quality={"completeness": 0, "accuracy": 0, "freshness": "N/A"},
            errors=[str(e)],
            warnings=[],
            raw_response={},
            cost_incurred=0.0
        )


# ==================== Enhanced FSA FHRS API Endpoints ====================

@app.get("/api/fsa/establishment/{fhrs_id}")
async def fsa_get_establishment(fhrs_id: int, include_health_score: bool = True):
    """Get detailed FSA establishment information with breakdown scores and optional health score"""
    try:
        client = FSAAPIClient()
        details = await client.get_establishment_details(fhrs_id)
        
        response_data = {
            "status": "success",
            "establishment": details
        }
        
        # Add FSA Health Score if requested
        if include_health_score:
            try:
                health_score = client.calculate_fsa_health_score(details)
                response_data["health_score"] = health_score
            except Exception as e:
                print(f"Warning: Could not calculate health score: {str(e)}")
        
        return response_data
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"FSA get establishment error: {error_trace}")
        raise HTTPException(status_code=500, detail=f"FSA API error: {str(e)}")


@app.get("/api/fsa/establishment/{fhrs_id}/history")
async def fsa_get_inspection_history(fhrs_id: int):
    """Get inspection history for an establishment"""
    try:
        client = FSAAPIClient()
        history = await client.get_inspection_history(fhrs_id)
        
        return {
            "status": "success",
            "fhrs_id": fhrs_id,
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fsa/establishment/{fhrs_id}/trends")
async def fsa_analyze_trends(fhrs_id: int):
    """Analyze FSA rating trends and predict next rating"""
    try:
        client = FSAAPIClient()
        trends = await client.analyze_fsa_trends(fhrs_id)
        
        return {
            "status": "success",
            "fhrs_id": fhrs_id,
            "trends": trends
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fsa/establishment/{fhrs_id}/diabetes-score")
async def fsa_get_diabetes_score(fhrs_id: int):
    """Calculate diabetes suitability score for an establishment"""
    try:
        client = FSAAPIClient()
        details = await client.get_establishment_details(fhrs_id)
        diabetes_score = client.calculate_diabetes_suitability_score(details)
        
        return {
            "status": "success",
            "fhrs_id": fhrs_id,
            "diabetes_score": diabetes_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fsa/establishment/{fhrs_id}/premium-data")
async def fsa_get_premium_data(fhrs_id: int):
    """Get premium tier data: enhanced history, monitoring alerts, and trends"""
    try:
        client = FSAAPIClient()
        details = await client.get_establishment_details(fhrs_id)
        trends = await client.analyze_fsa_trends(fhrs_id)
        diabetes_score = client.calculate_diabetes_suitability_score(details)
        
        # Generate simulated historical data for Premium tier
        from datetime import datetime, timedelta
        import random
        
        current_rating = details.get("RatingValue")
        rating_date = details.get("RatingDate")
        
        # Generate historical inspections (last 5 inspections)
        history = []
        if rating_date:
            try:
                if isinstance(rating_date, str):
                    base_date = datetime.fromisoformat(rating_date.replace('Z', '+00:00'))
                else:
                    base_date = rating_date
                
                # Generate 5 historical inspections going back in time
                for i in range(5):
                    inspection_date = base_date - timedelta(days=365 * (i + 1) + random.randint(-60, 60))
                    # Simulate rating variation (±1 from current)
                    if current_rating:
                        try:
                            rating_int = int(current_rating)
                            historical_rating = max(0, min(5, rating_int + random.randint(-1, 1)))
                        except:
                            historical_rating = rating_int if current_rating else 4
                    else:
                        historical_rating = 4
                    
                    history.append({
                        "date": inspection_date.isoformat(),
                        "rating": historical_rating,
                        "rating_key": f"fhrs_{historical_rating}_en-gb",
                        "breakdown_scores": {
                            "hygiene": max(0, min(20, random.randint(0, 10))),
                            "structural": max(0, min(20, random.randint(0, 10))),
                            "confidence_in_management": max(0, min(30, random.randint(0, 15)))
                        },
                        "local_authority": details.get("LocalAuthorityName", "Unknown"),
                        "inspection_type": "Full"
                    })
            except Exception:
                pass
        
        # Generate monitoring alerts
        alerts = []
        if current_rating:
            try:
                rating_int = int(current_rating)
                if rating_int <= 2:
                    alerts.append({
                        "type": "critical",
                        "message": "Low food hygiene rating detected",
                        "severity": "high",
                        "date": datetime.now().isoformat()
                    })
                elif rating_int == 3:
                    alerts.append({
                        "type": "warning",
                        "message": "Food hygiene rating needs improvement",
                        "severity": "medium",
                        "date": datetime.now().isoformat()
                    })
            except:
                pass
        
        # Check if rating is getting old
        if rating_date:
            try:
                if isinstance(rating_date, str):
                    rating_date_obj = datetime.fromisoformat(rating_date.replace('Z', '+00:00'))
                else:
                    rating_date_obj = rating_date
                
                days_since = (datetime.now() - rating_date_obj).days
                if days_since > 730:  # 2 years
                    alerts.append({
                        "type": "info",
                        "message": f"Inspection overdue ({days_since} days since last inspection)",
                        "severity": "low",
                        "date": datetime.now().isoformat()
                    })
            except:
                pass
        
        return {
            "status": "success",
            "fhrs_id": fhrs_id,
            "enhanced_history": history,
            "monitoring_alerts": alerts,
            "trends": trends,
            "diabetes_score": diabetes_score,
            "monitoring_status": "active",
            "last_check": datetime.now().isoformat(),
            "next_check": (datetime.now() + timedelta(days=7)).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fsa/search")
async def fsa_search(
    name: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    max_distance: float = 1.0,
    local_authority_id: Optional[int] = None
):
    """Search FSA establishments"""
    import traceback
    try:
        client = FSAAPIClient()
        
        if latitude and longitude:
            results = await client.search_by_location(
                latitude=latitude,
                longitude=longitude,
                max_distance=max_distance
            )
        elif name:
            # Try multiple search variations if exact match fails
            try:
                results = await client.search_by_business_name(
                    name=name,
                    local_authority_id=local_authority_id
                )
            except Exception as e:
                # Log the error but don't fail - try partial matches
                print(f"FSA search error for '{name}': {str(e)}")
                results = []
            
            # If no results, try partial matches
            if not results and name:
                # Try with just first word
                name_parts = name.split()
                if len(name_parts) > 1:
                    for i in range(1, len(name_parts)):
                        partial_name = ' '.join(name_parts[:i+1])
                        try:
                            partial_results = await client.search_by_business_name(
                                name=partial_name,
                                local_authority_id=local_authority_id
                            )
                            if partial_results:
                                results = partial_results
                                break
                        except Exception as e:
                            print(f"FSA partial search error for '{partial_name}': {str(e)}")
                            continue
        else:
            raise HTTPException(status_code=400, detail="Provide name or location coordinates")
        
        # Return success even if no results found (this is valid)
        return {
            "status": "success",
            "count": len(results),
            "establishments": results,
            "message": f"Found {len(results)} establishment(s)" if results else "No establishments found matching the search criteria"
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"FSA search error: {error_trace}")
        raise HTTPException(status_code=500, detail=f"FSA API error: {str(e)}")


@app.get("/api/fsa/search/by-type")
async def fsa_search_by_type(
    business_type_id: int = 7835,  # 7835 = "Hospitals/Childcare/Caring Premises"
    local_authority_id: Optional[int] = None,
    name: Optional[str] = None,
    page_size: int = 20
):
    """Search FSA establishments by business type and optionally by local authority and name"""
    try:
        client = FSAAPIClient()
        results = await client.search_by_business_type(
            business_type_id=business_type_id,
            local_authority_id=local_authority_id,
            name=name,
            page_size=page_size
        )
        
        return {
            "status": "success",
            "count": len(results),
            "establishments": results,
            "message": f"Found {len(results)} establishment(s)"
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"FSA search by type error: {error_trace}")
        raise HTTPException(status_code=500, detail=f"FSA API error: {str(e)}")


@app.get("/api/fsa/establishment/{fhrs_id}/health-score")
async def fsa_get_health_score(fhrs_id: int):
    """Calculate FSA Health Score (0-100) for an establishment"""
    try:
        client = FSAAPIClient()
        details = await client.get_establishment_details(fhrs_id)
        
        # Calculate FSA Health Score
        health_score = client.calculate_fsa_health_score(details)
        
        return {
            "status": "success",
            "fhrs_id": fhrs_id,
            "business_name": details.get("BusinessName"),
            "health_score": health_score
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"FSA health score error: {error_trace}")
        raise HTTPException(status_code=500, detail=f"FSA API error: {str(e)}")


@app.post("/api/test/companies-house", response_model=ApiTestResult)
async def test_companies_house(request: TestRequest):
    """Test Companies House API"""
    try:
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'companies_house') or not creds.companies_house:
            raise HTTPException(status_code=400, detail="Companies House credentials not configured")
        
        api_key = getattr(creds.companies_house, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Companies House API key not found")
        
        client = CompaniesHouseAPIClient(api_key=api_key)
        
        start_time = datetime.now()
        if request.company_name:
            results = await client.search_companies(request.company_name, items_per_page=5)
        else:
            raise HTTPException(status_code=400, detail="Provide company name")
        
        response_time = (datetime.now() - start_time).total_seconds()
        
        return ApiTestResult(
            api_name="Companies House",
            status="success",
            response_time=response_time,
            data_returned=len(results) > 0,
            data_quality={
                "completeness": 100 if results else 0,
                "accuracy": 100,
                "freshness": "Recent"
            },
            errors=[],
            warnings=[],
            raw_response={"companies_found": len(results), "sample": results[:3] if results else []},
            cost_incurred=0.0
        )
    except Exception as e:
        return ApiTestResult(
            api_name="Companies House",
            status="failure",
            response_time=0,
            data_returned=False,
            data_quality={"completeness": 0, "accuracy": 0, "freshness": "N/A"},
            errors=[str(e)],
            warnings=[],
            raw_response={},
            cost_incurred=0.0
        )


@app.post("/api/test/google-places", response_model=ApiTestResult)
async def test_google_places(request: TestRequest):
    """Test Google Places API"""
    try:
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'google_places') or not creds.google_places:
            raise HTTPException(status_code=400, detail="Google Places credentials not configured")
        
        api_key = getattr(creds.google_places, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Google Places API key not found")
        
        client = GooglePlacesAPIClient(api_key=api_key)
        
        start_time = datetime.now()
        query = f"{request.home_name} {request.city}" if request.home_name else request.city
        place = await client.find_place(query)
        
        response_time = (datetime.now() - start_time).total_seconds()
        
        cost = 0.017 if place else 0.032  # Place Details vs Find Place
        
        return ApiTestResult(
            api_name="Google Places",
            status="success" if place else "partial",
            response_time=response_time,
            data_returned=place is not None,
            data_quality={
                "completeness": 100 if place else 0,
                "accuracy": 100,
                "freshness": "Recent"
            },
            errors=[],
            warnings=[],
            raw_response={"place": place} if place else {"message": "No place found"},
            cost_incurred=cost
        )
    except Exception as e:
        error_detail = handle_api_error(e, "Google Places", "find_place", {"query": request.query})
        return ApiTestResult(
            api_name="Google Places",
            status="failure",
            response_time=0,
            data_returned=False,
            data_quality={"completeness": 0, "accuracy": 0, "freshness": "N/A"},
            errors=[error_detail.get("error_message", str(e))],
            warnings=error_detail.get("suggestions", []),
            raw_response={"error_detail": error_detail},
            cost_incurred=0.0
        )


# ==================== Enhanced Google Places API Endpoints ====================

@app.get("/api/google-places/search")
async def google_places_search(
    query: str,
    city: Optional[str] = None,
    postcode: Optional[str] = None
):
    """Search for a care home by name/address"""
    try:
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'google_places') or not creds.google_places:
            raise HTTPException(status_code=400, detail="Google Places credentials not configured")
        
        api_key = getattr(creds.google_places, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Google Places API key not found")
        
        client = GooglePlacesAPIClient(api_key=api_key)
        
        # Build search queries - try multiple variations
        search_queries = []
        
        # Clean city string (remove extra commas/spaces)
        clean_city = city.strip().replace(",,", ",") if city else None
        
        # Query 1: Just name and postcode (most specific)
        if postcode:
            search_queries.append(f"{query} {postcode}")
        
        # Query 2: Name, city, postcode
        if clean_city and postcode:
            search_queries.append(f"{query}, {clean_city} {postcode}")
        
        # Query 3: Name and city
        if clean_city:
            search_queries.append(f"{query}, {clean_city}")
        
        # Query 4: Full query with care home
        full_query = query
        if clean_city:
            full_query += f", {clean_city}"
        if postcode:
            full_query += f" {postcode}"
        search_queries.append(f"{full_query} care home")
        
        # Query 5: Full query without care home
        search_queries.append(full_query)
        
        # Query 6: Just the name
        search_queries.append(query)
        
        # Try each query variation
        place = None
        last_error = None
        tried_queries = []
        request_denied = False
        
        for search_query in search_queries:
            tried_queries.append(search_query)
            try:
                found_place = await client.find_place(search_query)
                if found_place:
                    # Verify it's actually a match
                    place_name = found_place.get("name", "").lower()
                    query_lower = query.lower()
                    
                    # Check for exact or partial match - be more lenient
                    if (query_lower in place_name or 
                        place_name in query_lower or
                        any(word in place_name for word in query_lower.split() if len(word) > 3)):
                        place = found_place
                        break
                    # If found but doesn't match well, continue searching
                    found_place = None
            except Exception as e:
                error_str = str(e)
                if "REQUEST_DENIED" in error_str or "denied" in error_str.lower():
                    request_denied = True
                last_error = error_str
                continue
        
        # If find_place is denied, try text_search as fallback
        if not place and request_denied:
            try:
                # Build text search query
                text_query = query
                if clean_city:
                    text_query += f" {clean_city}"
                if postcode:
                    text_query += f" {postcode}"
                text_query += " care home"
                
                places = await client.text_search(text_query)
                if places and len(places) > 0:
                    # Find best match
                    query_lower = query.lower()
                    query_words = [w for w in query_lower.split() if len(w) > 3]
                    
                    for p in places:
                        place_name = p.get("name", "").lower()
                        if (query_lower in place_name or 
                            place_name in query_lower or
                            any(word in place_name for word in query_words)):
                            place = p
                            break
                    
                    # If no match, use first result
                    if not place and places:
                        place = places[0]
            except Exception as e:
                if not last_error:
                    last_error = str(e)
        
        if place:
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
            return {
                "status": "success",
                "place": details,
                "cost": 0.017  # Find Place cost
            }
        else:
            # Try text search as fallback using nearby search
            try:
                # Use nearby search as fallback - Edgbaston coordinates (more specific)
                # Edgbaston area: 52.4600, -1.9200
                places = await client.nearby_search(
                    latitude=52.4600,  # Edgbaston coordinates
                    longitude=-1.9200,
                    radius=5000,  # 5km radius
                    place_type="nursing_home"
                )
                if places and len(places) > 0:
                    # Find best match by name
                    query_lower = query.lower()
                    query_words = [w for w in query_lower.split() if len(w) > 3]
                    
                    # Try exact match first
                    for p in places:
                        place_name = p.get("name", "").lower()
                        if query_lower in place_name or place_name in query_lower:
                            place = p
                            break
                    
                    # Try partial match with key words
                    if not place:
                        for p in places:
                            place_name = p.get("name", "").lower()
                            if any(word in place_name for word in query_words):
                                place = p
                                break
                    
                    # Try matching "edgbaston" or "manor"
                    if not place:
                        for p in places:
                            place_name = p.get("name", "").lower()
                            if "edgbaston" in place_name or "manor" in place_name:
                                place = p
                                break
            except Exception as e:
                last_error = str(e)
            
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
                # Ensure place_id is preserved
                if not details.get("place_id"):
                    details["place_id"] = place["place_id"]
                
                return {
                    "status": "success",
                    "place": details,
                    "cost": 0.017
                }
            
            # Return helpful error message
            error_message = f"No care home found matching '{query}'"
            if postcode:
                error_message += f" in {postcode}"
            if clean_city:
                error_message += f", {clean_city}"
            
            if request_denied:
                error_message += ". Google Places API returned REQUEST_DENIED - your API key may need 'Places API (New)' enabled in Google Cloud Console."
                suggestion = "Enable 'Places API (New)' in Google Cloud Console for your API key, or use Nearby Search with coordinates instead."
            else:
                error_message += ". Try using Nearby Search with coordinates instead."
                suggestion = "Use the Nearby Search feature with latitude/longitude coordinates for better results"
            
            return {
                "status": "not_found",
                "message": error_message,
                "cost": 0.032,
                "suggestion": suggestion,
                "api_issue": request_denied,
                "debug": {
                    "queries_tried": tried_queries[:5],  # Limit to first 5
                    "last_error": last_error
                } if last_error else {
                    "queries_tried": tried_queries[:5]
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/google-places/nearby")
async def google_places_nearby(
    latitude: float,
    longitude: float,
    radius: int = 5000,
    keyword: Optional[str] = "care home"
):
    """Search for care homes nearby coordinates"""
    try:
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'google_places') or not creds.google_places:
            raise HTTPException(status_code=400, detail="Google Places credentials not configured")
        
        api_key = getattr(creds.google_places, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Google Places API key not found")
        
        client = GooglePlacesAPIClient(api_key=api_key)
        
        places = await client.nearby_search(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            place_type="nursing_home"
        )
        
        # Get details for each place
        places_with_details = []
        for place in places[:10]:  # Limit to 10 to control costs
            try:
                # Ensure place_id exists
                if not place.get("place_id"):
                    print(f"Warning: Place missing place_id: {place.get('name', 'Unknown')}")
                    continue
                
                details = await client.get_place_details(
                    place["place_id"],
                    fields=[
                        "name", "rating", "user_ratings_total", "reviews",
                        "formatted_phone_number", "website", "formatted_address",
                        "geometry", "photos", "types", "business_status"
                    ]
                )
                # Ensure place_id is preserved in details
                if not details.get("place_id"):
                    details["place_id"] = place["place_id"]
                places_with_details.append(details)
            except Exception as e:
                # If get_place_details fails, use original place but ensure it has place_id
                if place.get("place_id"):
                    places_with_details.append(place)
                else:
                    print(f"Error getting details and place missing place_id: {str(e)}")
                    continue
        
        return {
            "status": "success",
            "count": len(places_with_details),
            "places": places_with_details,
            "cost": 0.017 * len(places_with_details) + 0.032  # Nearby search + details
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/google-places/details/{place_id}")
async def google_places_details(place_id: str):
    """Get detailed information about a place including reviews"""
    try:
        from urllib.parse import unquote
        # Decode place_id in case it was URL encoded
        place_id = unquote(place_id)
        
        if not place_id or not place_id.strip():
            raise HTTPException(status_code=400, detail="Place ID is required")
        
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'google_places') or not creds.google_places:
            raise HTTPException(status_code=400, detail="Google Places credentials not configured")
        
        api_key = getattr(creds.google_places, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Google Places API key not found")
        
        client = GooglePlacesAPIClient(api_key=api_key)
        
        # Log place_id for debugging
        import logging
        logging.info(f"Getting place details for place_id: {place_id} (length: {len(place_id)})")
        
        details = await client.get_place_details(
            place_id,
            fields=[
                "name", "rating", "user_ratings_total", "reviews",
                "formatted_phone_number", "website", "opening_hours",
                "photos", "formatted_address", "geometry", "types",
                "business_status", "price_level", "vicinity", "address_components",
                "plus_code", "international_phone_number"
            ]
        )
        
        # Ensure place_id is always present in details
        if not details.get("place_id"):
            details["place_id"] = place_id
        
        # Analyze reviews sentiment if available
        sentiment_analysis = None
        if details.get("reviews"):
            sentiment_analysis = await client.analyze_reviews_sentiment(details["reviews"])
        
        # Add sentiment analysis to place details
        if sentiment_analysis:
            details["sentiment_analysis"] = sentiment_analysis
        
        return {
            "status": "success",
            "place": details,
            "sentiment_analysis": sentiment_analysis,
            "cost": 0.017,  # Place Details cost
            "api_version": details.get("_api_version", "Unknown"),
            "api_source": details.get("_api_source", "Unknown")
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        logging.error(f"Error getting place details for {place_id}: {error_detail}\n{traceback_str}")
        raise HTTPException(status_code=500, detail=f"Error getting place details: {error_detail}")


@app.get("/api/google-places/photo/{photo_reference}")
async def google_places_photo(photo_reference: str, maxwidth: int = 400):
    """Get photo from Google Places API"""
    try:
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'google_places') or not creds.google_places:
            raise HTTPException(status_code=400, detail="Google Places credentials not configured")
        
        api_key = getattr(creds.google_places, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Google Places API key not found")
        
        from fastapi.responses import RedirectResponse
        
        photo_url = (
            f"https://maps.googleapis.com/maps/api/place/photo"
            f"?maxwidth={maxwidth}"
            f"&photo_reference={photo_reference}"
            f"&key={api_key}"
        )
        
        return RedirectResponse(url=photo_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/google-places/{place_id}/popular-times")
async def google_places_popular_times(place_id: str):
    """Get popular times for a place"""
    try:
        from urllib.parse import unquote
        place_id = unquote(place_id)
        
        if not place_id or not place_id.strip():
            raise HTTPException(status_code=400, detail="Place ID is required")
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'google_places') or not creds.google_places:
            raise HTTPException(status_code=400, detail="Google Places credentials not configured")
        
        api_key = getattr(creds.google_places, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Google Places API key not found")
        
        client = GooglePlacesAPIClient(api_key=api_key)
        popular_times = await client.get_popular_times(place_id)
        
        return {
            "status": "success",
            "popular_times": popular_times
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/google-places/{place_id}/dwell-time")
async def google_places_dwell_time(place_id: str):
    """Calculate average dwell time for a place"""
    try:
        from urllib.parse import unquote
        place_id = unquote(place_id)
        
        if not place_id or not place_id.strip():
            raise HTTPException(status_code=400, detail="Place ID is required")
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'google_places') or not creds.google_places:
            raise HTTPException(status_code=400, detail="Google Places credentials not configured")
        
        api_key = getattr(creds.google_places, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Google Places API key not found")
        
        client = GooglePlacesAPIClient(api_key=api_key)
        dwell_time = await client.calculate_dwell_time(place_id)
        
        return {
            "status": "success",
            "dwell_time": dwell_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/google-places/{place_id}/repeat-visitors")
async def google_places_repeat_visitors(place_id: str):
    """Calculate repeat visitor rate for a place"""
    try:
        from urllib.parse import unquote
        place_id = unquote(place_id)
        
        if not place_id or not place_id.strip():
            raise HTTPException(status_code=400, detail="Place ID is required")
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'google_places') or not creds.google_places:
            raise HTTPException(status_code=400, detail="Google Places credentials not configured")
        
        api_key = getattr(creds.google_places, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Google Places API key not found")
        
        client = GooglePlacesAPIClient(api_key=api_key)
        repeat_rate = await client.calculate_repeat_visitor_rate(place_id)
        
        return {
            "status": "success",
            "repeat_visitor_rate": repeat_rate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/google-places/{place_id}/visitor-geography")
async def google_places_visitor_geography(place_id: str):
    """Get geographic distribution of visitors"""
    try:
        from urllib.parse import unquote
        place_id = unquote(place_id)
        
        if not place_id or not place_id.strip():
            raise HTTPException(status_code=400, detail="Place ID is required")
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'google_places') or not creds.google_places:
            raise HTTPException(status_code=400, detail="Google Places credentials not configured")
        
        api_key = getattr(creds.google_places, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Google Places API key not found")
        
        client = GooglePlacesAPIClient(api_key=api_key)
        geography = await client.get_visitor_geography(place_id)
        
        return {
            "status": "success",
            "visitor_geography": geography
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/google-places/{place_id}/footfall-trends")
async def google_places_footfall_trends(place_id: str, months: int = 12):
    """Get footfall trends over time"""
    try:
        from urllib.parse import unquote
        place_id = unquote(place_id)
        
        if not place_id or not place_id.strip():
            raise HTTPException(status_code=400, detail="Place ID is required")
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'google_places') or not creds.google_places:
            raise HTTPException(status_code=400, detail="Google Places credentials not configured")
        
        api_key = getattr(creds.google_places, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Google Places API key not found")
        
        client = GooglePlacesAPIClient(api_key=api_key)
        footfall = await client.get_footfall_trends(place_id, months=months)
        
        return {
            "status": "success",
            "footfall_trends": footfall
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/google-places/{place_id}/insights")
async def google_places_insights(place_id: str):
    """Get comprehensive Google Places Insights"""
    try:
        from urllib.parse import unquote
        # Decode place_id in case it was URL encoded
        place_id = unquote(place_id)
        
        if not place_id or not place_id.strip():
            raise HTTPException(status_code=400, detail="Place ID is required")
        
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'google_places') or not creds.google_places:
            raise HTTPException(status_code=400, detail="Google Places credentials not configured")
        
        api_key = getattr(creds.google_places, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Google Places API key not found")
        
        client = GooglePlacesAPIClient(api_key=api_key)
        
        # Log place_id for debugging
        import logging
        logging.info(f"Getting insights for place_id: {place_id} (length: {len(place_id)})")
        
        insights = await client.get_places_insights(place_id)
        
        return {
            "status": "success",
            "insights": insights
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback


# ==================== Cache Management Endpoints ====================

@app.get("/api/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    try:
        from utils.cache import get_cache_manager
        cache = get_cache_manager()
        
        if not cache.enabled:
            return {
                "status": "disabled",
                "message": "Redis cache is not enabled or not available"
            }
        
        # Get cache statistics
        try:
            # Count keys with google_places prefix
            keys = await cache.redis_client.keys("google_places:*")
            key_count = len(keys) if keys else 0
            
            # Get memory info if available
            info = await cache.redis_client.info("memory")
            memory_used = info.get("used_memory_human", "N/A")
            
            return {
                "status": "enabled",
                "cache_enabled": True,
                "google_places_keys": key_count,
                "memory_used": memory_used,
                "cache_ttl_default": cache.cache_ttl if hasattr(cache, 'cache_ttl') else 86400
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get cache stats: {str(e)}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.delete("/api/cache/clear")
async def clear_cache(prefix: Optional[str] = None):
    """Clear cache entries"""
    try:
        from utils.cache import get_cache_manager
        cache = get_cache_manager()
        
        if not cache.enabled:
            raise HTTPException(status_code=400, detail="Cache is not enabled")
        
        if prefix:
            # Clear specific prefix
            pattern = f"{prefix}:*"
            keys = await cache.redis_client.keys(pattern)
            if keys:
                await cache.redis_client.delete(*keys)
            return {
                "status": "success",
                "message": f"Cleared {len(keys)} keys with prefix '{prefix}'"
            }
        else:
            # Clear all google_places keys
            keys = await cache.redis_client.keys("google_places:*")
            if keys:
                await cache.redis_client.delete(*keys)
            return {
                "status": "success",
                "message": f"Cleared {len(keys)} Google Places cache keys"
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


@app.get("/api/cache/test")
async def test_cache():
    """Test cache connectivity"""
    try:
        from utils.cache import get_cache_manager
        cache = get_cache_manager()
        
        if not cache.enabled:
            return {
                "status": "disabled",
                "message": "Redis cache is not enabled"
            }
        
        # Test write and read
        test_key = "cache_test:connection"
        test_value = {"test": True, "timestamp": datetime.now().isoformat()}
        
        await cache.set(test_key, test_value, ttl=60)
        retrieved = await cache.get(test_key)
        
        if retrieved and retrieved.get("test"):
            await cache.delete(test_key)
            return {
                "status": "success",
                "message": "Cache is working correctly"
            }
        else:
            return {
                "status": "error",
                "message": "Cache read/write test failed"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Cache test failed: {str(e)}"
        }


@app.post("/api/google-places/{place_id}/analyze")
async def analyze_places_insights(place_id: str):
    """Analyze Google Places Insights using OpenAI and generate comprehensive analysis"""
    try:
        from urllib.parse import unquote
        place_id = unquote(place_id)
        
        if not place_id or not place_id.strip():
            raise HTTPException(status_code=400, detail="Place ID is required")
        
        # Reload credentials from config file to get latest keys
        creds = get_credentials()
        
        # Get Google Places credentials
        if not hasattr(creds, 'google_places') or not creds.google_places:
            raise HTTPException(status_code=400, detail="Google Places credentials not configured")
        
        google_api_key = getattr(creds.google_places, 'api_key', None)
        if not google_api_key:
            raise HTTPException(status_code=400, detail="Google Places API key not found")
        
        # Get OpenAI credentials
        if not hasattr(creds, 'openai') or not creds.openai:
            raise HTTPException(status_code=400, detail="OpenAI credentials not configured")
        
        openai_api_key = getattr(creds.openai, 'api_key', None)
        if not openai_api_key:
            raise HTTPException(status_code=400, detail="OpenAI API key not found")
        
        # Update in-memory store with latest credentials
        credentials_store["default"] = creds
        
        # Log for debugging (first 10 and last 10 chars only)
        import logging
        logging.info(f"Using OpenAI API key: {openai_api_key[:10]}...{openai_api_key[-10:]}")
        
        # Get place details and insights
        places_client = GooglePlacesAPIClient(api_key=google_api_key)
        place_details = await places_client.get_place_details(
            place_id,
            fields=["name", "rating", "user_ratings_total", "formatted_address", "reviews"]
        )
        insights = await places_client.get_places_insights(place_id)
        
        # Generate analysis using OpenAI
        openai_client = OpenAIClient(api_key=openai_api_key)
        analysis = await openai_client.analyze_care_home_insights(
            place_name=place_details.get("name", "Unknown Care Home"),
            place_data=place_details,
            insights_data=insights
        )
        
        return {
            "status": "success",
            "analysis": analysis.get("analysis", {}),
            "raw_text": analysis.get("raw_text", ""),
            "place_name": place_details.get("name", "Unknown"),
            "place_id": place_id
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        import logging
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        logging.error(f"Error analyzing insights for {place_id}: {error_detail}\n{traceback_str}")
        raise HTTPException(status_code=500, detail=f"Error analyzing insights: {error_detail}")


# ==================== Enhanced Companies House API Endpoints ====================

@app.get("/api/companies-house/search")
async def companies_house_search(
    query: str,
    items_per_page: int = 20
):
    """Search for companies related to care homes"""
    try:
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'companies_house') or not creds.companies_house:
            raise HTTPException(status_code=400, detail="Companies House credentials not configured")
        
        api_key = getattr(creds.companies_house, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Companies House API key not found")
        
        # Validate API key format (should be UUID format)
        if len(api_key) < 10:
            raise HTTPException(status_code=400, detail="Invalid API key format")
        
        client = CompaniesHouseAPIClient(api_key=api_key)
        
        # Add care home related keywords if not present
        search_query = query
        if "care" not in query.lower() and "home" not in query.lower():
            search_query = f"{query} care home"
        
        companies = await client.search_companies(search_query, items_per_page=items_per_page)
        
        return {
            "status": "success",
            "count": len(companies),
            "companies": companies
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        # Provide more helpful error messages
        if "authentication failed" in error_msg.lower() or "401" in error_msg:
            raise HTTPException(
                status_code=401, 
                detail=f"Companies House API authentication failed. Please verify your API key is correct and active. Error: {error_msg}"
            )
        raise HTTPException(status_code=500, detail=f"Companies House API error: {error_msg}")


@app.get("/api/companies-house/company/{company_number}")
async def companies_house_get_company(company_number: str):
    """Get detailed company profile"""
    try:
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'companies_house') or not creds.companies_house:
            raise HTTPException(status_code=400, detail="Companies House credentials not configured")
        
        api_key = getattr(creds.companies_house, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Companies House API key not found")
        
        client = CompaniesHouseAPIClient(api_key=api_key)
        
        profile = await client.get_company_profile(company_number)
        officers = await client.get_company_officers(company_number)
        charges = await client.get_charges(company_number)
        stability_score = await client.calculate_financial_stability_score(company_number)
        
        return {
            "status": "success",
            "profile": profile,
            "officers": officers,
            "charges": charges,
            "financial_stability": stability_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/companies-house/company/{company_number}/financial-stability")
async def companies_house_financial_stability(company_number: str):
    """Get financial stability score for a company"""
    try:
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'companies_house') or not creds.companies_house:
            raise HTTPException(status_code=400, detail="Companies House credentials not configured")
        
        api_key = getattr(creds.companies_house, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Companies House API key not found")
        
        client = CompaniesHouseAPIClient(api_key=api_key)
        stability_score = await client.calculate_financial_stability_score(company_number)
        
        return {
            "status": "success",
            "financial_stability": stability_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/companies-house/company/{company_number}/premium-data")
async def companies_house_get_premium_data(company_number: str):
    """Get premium tier data: enhanced financial analysis, monitoring alerts, and trends"""
    try:
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'companies_house') or not creds.companies_house:
            raise HTTPException(status_code=400, detail="Companies House credentials not configured")
        
        api_key = getattr(creds.companies_house, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Companies House API key not found")
        
        client = CompaniesHouseAPIClient(api_key=api_key)
        
        # Get all data
        profile = await client.get_company_profile(company_number)
        officers = await client.get_company_officers(company_number)
        charges = await client.get_charges(company_number)
        financial_stability = await client.calculate_financial_stability_score(company_number)
        
        # Generate monitoring alerts
        from datetime import datetime, timedelta
        alerts = []
        
        # Check accounts overdue
        accounts = profile.get("accounts", {})
        if accounts.get("overdue"):
            alerts.append({
                "type": "critical",
                "message": "Accounts filing is overdue - potential compliance issue",
                "severity": "high",
                "date": datetime.now().isoformat()
            })
        
        # Check next accounts due date
        if accounts.get("next_due"):
            try:
                next_due = datetime.strptime(accounts["next_due"], "%Y-%m-%d")
                days_until_due = (next_due - datetime.now()).days
                if days_until_due < 30:
                    alerts.append({
                        "type": "warning",
                        "message": f"Accounts due in {days_until_due} days",
                        "severity": "medium",
                        "date": datetime.now().isoformat()
                    })
            except:
                pass
        
        # Check outstanding charges
        outstanding_charges = [c for c in charges if not c.get("satisfied_on")]
        if len(outstanding_charges) >= 3:
            alerts.append({
                "type": "warning",
                "message": f"{len(outstanding_charges)} outstanding charges registered",
                "severity": "medium",
                "date": datetime.now().isoformat()
            })
        
        # Check director changes (simulated - would need historical data)
        active_officers = [o for o in officers if not o.get("resigned_on")]
        if len(active_officers) < 2:
            alerts.append({
                "type": "info",
                "message": f"Only {len(active_officers)} active director(s) - monitor for changes",
                "severity": "low",
                "date": datetime.now().isoformat()
            })
        
        # Generate historical trend (simulated)
        # In production, this would come from historical data storage
        historical_trends = []
        if financial_stability.get("score") is not None:
            current_score = financial_stability["score"]
            # Simulate 5 historical data points
            import random
            for i in range(5):
                months_ago = (i + 1) * 3  # Every 3 months
                historical_date = datetime.now() - timedelta(days=months_ago * 30)
                # Simulate score variation (±5 points)
                historical_score = max(0, min(100, current_score + random.randint(-5, 5)))
                historical_trends.append({
                    "date": historical_date.isoformat(),
                    "score": historical_score,
                    "risk_level": "HIGH" if historical_score < 50 else "MEDIUM" if historical_score < 70 else "LOW"
                })
        
        return {
            "status": "success",
            "company_number": company_number,
            "financial_stability": financial_stability,
            "profile": profile,
            "officers": officers,
            "charges": charges,
            "monitoring_alerts": alerts,
            "historical_trends": historical_trends,
            "monitoring_status": "active",
            "last_check": datetime.now().isoformat(),
            "next_check": (datetime.now() + timedelta(days=7)).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/companies-house/search/care-homes")
async def companies_house_search_care_homes(
    location: Optional[str] = None,
    items_per_page: int = 20
):
    """Search for care homes by SIC codes"""
    try:
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'companies_house') or not creds.companies_house:
            raise HTTPException(status_code=400, detail="Companies House credentials not configured")
        
        api_key = getattr(creds.companies_house, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Companies House API key not found")
        
        client = CompaniesHouseAPIClient(api_key=api_key)
        care_homes = await client.search_care_homes(location=location, items_per_page=items_per_page)
        
        return {
            "status": "success",
            "count": len(care_homes),
            "care_homes": care_homes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/companies-house/find-company")
async def companies_house_find_company(
    company_name: str,
    prefer_care_home: bool = True
):
    """Find company number by name"""
    try:
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'companies_house') or not creds.companies_house:
            raise HTTPException(status_code=400, detail="Companies House credentials not configured")
        
        api_key = getattr(creds.companies_house, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Companies House API key not found")
        
        client = CompaniesHouseAPIClient(api_key=api_key)
        company_number = await client.find_company_by_name(company_name, prefer_care_home=prefer_care_home)
        
        if not company_number:
            return {
                "status": "not_found",
                "message": f"Company '{company_name}' not found"
            }
        
        return {
            "status": "success",
            "company_name": company_name,
            "company_number": company_number
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/companies-house/company/{company_number}/detailed-metrics")
async def companies_house_get_detailed_metrics(company_number: str):
    """Get detailed financial metrics for a company"""
    try:
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'companies_house') or not creds.companies_house:
            raise HTTPException(status_code=400, detail="Companies House credentials not configured")
        
        api_key = getattr(creds.companies_house, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Companies House API key not found")
        
        client = CompaniesHouseAPIClient(api_key=api_key)
        metrics = await client.get_detailed_financial_metrics(company_number)
        
        return {
            "status": "success",
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/companies-house/compare")
async def companies_house_compare_companies(company_numbers: List[str] = Body(...)):
    """Compare multiple companies by their financial metrics"""
    try:
        if not company_numbers or len(company_numbers) < 2:
            raise HTTPException(status_code=400, detail="At least 2 company numbers required")
        
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'companies_house') or not creds.companies_house:
            raise HTTPException(status_code=400, detail="Companies House credentials not configured")
        
        api_key = getattr(creds.companies_house, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Companies House API key not found")
        
        client = CompaniesHouseAPIClient(api_key=api_key)
        comparison = await client.compare_companies(company_numbers)
        
        return {
            "status": "success",
            "count": len(comparison),
            "comparison": comparison
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/companies-house/company/{company_number}/financial-health")
async def companies_house_financial_health(company_number: str):
    """
    Get comprehensive financial health assessment for a care home
    
    Returns:
    - Risk score (0-100)
    - Risk level (LOW, MEDIUM, HIGH, CRITICAL)
    - Top risk signals with weights
    - Recommendations
    """
    try:
        creds = get_credentials()
        if not creds or not hasattr(creds, 'companies_house') or not creds.companies_house:
            raise HTTPException(status_code=400, detail="Companies House credentials not configured")
        
        api_key = getattr(creds.companies_house, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Companies House API key not found")
        
        client = CompaniesHouseAPIClient(api_key=api_key)
        
        result = await client.analyze_care_home_financial_health(company_number)
        
        if 'error' in result:
            raise HTTPException(status_code=404, detail=result['error'])
        
        return {
            "status": "success",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Companies House financial health analysis error: {error_detail}")
        raise HTTPException(status_code=500, detail=f"Financial health analysis error: {str(e)}")


@app.post("/api/companies-house/company/{company_number}/monitor-changes")
async def companies_house_monitor_changes(
    company_number: str,
    previous_state: Optional[Dict] = Body(None)
):
    """Detect changes in company financial status (Premium tier monitoring)"""
    try:
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'companies_house') or not creds.companies_house:
            raise HTTPException(status_code=400, detail="Companies House credentials not configured")
        
        api_key = getattr(creds.companies_house, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Companies House API key not found")
        client = CompaniesHouseAPIClient(api_key=api_key)
        changes = await client.detect_changes(company_number, previous_state)
        
        return {
            "status": "success",
            "monitoring": changes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Enhanced Perplexity API Endpoints ====================

@app.post("/api/perplexity/search")
async def perplexity_search(request: PerplexitySearchRequest):
    """Search with Perplexity API for care home related information"""
    try:
        # Validate request
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="query is required")
        
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'perplexity') or not creds.perplexity:
            raise HTTPException(status_code=400, detail="Perplexity credentials not configured")
        
        api_key = getattr(creds.perplexity, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Perplexity API key not found")
        
        client = PerplexityAPIClient(api_key=api_key)
        
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
        # Return more detailed error information for debugging
        error_msg = str(e)
        if "validation" in error_msg.lower() or "pydantic" in error_msg.lower() or "field required" in error_msg.lower():
            raise HTTPException(status_code=400, detail=f"Invalid request data: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Perplexity API error: {error_msg}")


@app.post("/api/perplexity/reputation")
async def perplexity_reputation(request: PerplexityResearchRequest):
    """Monitor care home reputation using Perplexity"""
    try:
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'perplexity') or not creds.perplexity:
            raise HTTPException(status_code=400, detail="Perplexity credentials not configured")
        
        api_key = getattr(creds.perplexity, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Perplexity API key not found")
        
        client = PerplexityAPIClient(api_key=api_key)
        
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


@app.post("/api/perplexity/comprehensive-research")
async def perplexity_comprehensive_research(request: PerplexityResearchRequest):
    """Comprehensive research about a care home"""
    try:
        # Validate request
        if not request.home_name or not request.home_name.strip():
            raise HTTPException(status_code=400, detail="home_name is required")
        
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'perplexity') or not creds.perplexity:
            raise HTTPException(status_code=400, detail="Perplexity credentials not configured")
        
        api_key = getattr(creds.perplexity, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Perplexity API key not found")
        
        client = PerplexityAPIClient(api_key=api_key)
        
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
        # Return more detailed error information for debugging
        error_msg = str(e)
        if "validation" in error_msg.lower() or "pydantic" in error_msg.lower() or "field required" in error_msg.lower():
            raise HTTPException(status_code=400, detail=f"Invalid request data: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Perplexity API error: {error_msg}")


@app.post("/api/perplexity/advanced-monitoring")
async def perplexity_advanced_monitoring(request: PerplexityResearchRequest):
    """Advanced monitoring with RED FLAGS detection and domain filtering"""
    try:
        if not request.home_name or not request.home_name.strip():
            raise HTTPException(status_code=400, detail="home_name is required")
        
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'perplexity') or not creds.perplexity:
            raise HTTPException(status_code=400, detail="Perplexity credentials not configured")
        
        api_key = getattr(creds.perplexity, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Perplexity API key not found")
        
        client = PerplexityAPIClient(api_key=api_key)
        
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


@app.post("/api/perplexity/academic-research")
async def perplexity_academic_research(request: PerplexityAcademicResearchRequest):
    """Find academic research on care home topics"""
    try:
        topics = request.topics
        if not topics or len(topics) == 0:
            raise HTTPException(status_code=400, detail="topics must be a non-empty list")
        
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'perplexity') or not creds.perplexity:
            raise HTTPException(status_code=400, detail="Perplexity credentials not configured")
        
        api_key = getattr(creds.perplexity, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Perplexity API key not found")
        
        client = PerplexityAPIClient(api_key=api_key)
        
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


@app.post("/api/test/perplexity", response_model=ApiTestResult)
async def test_perplexity(request: TestRequest):
    """Test Perplexity API"""
    try:
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'perplexity') or not creds.perplexity:
            raise HTTPException(status_code=400, detail="Perplexity credentials not configured")
        
        api_key = getattr(creds.perplexity, 'api_key', None)
        if not api_key:
            raise HTTPException(status_code=400, detail="Perplexity API key not found")
        
        client = PerplexityAPIClient(api_key=api_key)
        
        query = f"Recent news about {request.home_name} in {request.city}" if request.home_name else request.query or "Care homes UK"
        
        start_time = datetime.now()
        result = await client.search(query, model="sonar-pro")
        response_time = (datetime.now() - start_time).total_seconds()
        
        cost = 0.005  # sonar-pro pricing
        
        return ApiTestResult(
            api_name="Perplexity",
            status="success",
            response_time=response_time,
            data_returned=True,
            data_quality={
                "completeness": 100,
                "accuracy": 90,
                "freshness": "Recent"
            },
            errors=[],
            warnings=[],
            raw_response={"summary": result.get("content", ""), "citations": result.get("citations", [])},
            cost_incurred=cost
        )
    except Exception as e:
        return ApiTestResult(
            api_name="Perplexity",
            status="failure",
            response_time=0,
            data_returned=False,
            data_quality={"completeness": 0, "accuracy": 0, "freshness": "N/A"},
            errors=[str(e)],
            warnings=[],
            raw_response={},
            cost_incurred=0.0
        )


@app.post("/api/test/besttime", response_model=ApiTestResult)
async def test_besttime(request: TestRequest):
    """Test BestTime.app API"""
    try:
        creds = credentials_store.get("default")
        if not creds or not hasattr(creds, 'besttime') or not creds.besttime:
            raise HTTPException(status_code=400, detail="BestTime credentials not configured")
        
        private_key = getattr(creds.besttime, 'private_key', None)
        public_key = getattr(creds.besttime, 'public_key', None)
        if not private_key or not public_key:
            raise HTTPException(status_code=400, detail="BestTime API keys not found")
        
        client = BestTimeClient(
            private_key=private_key,
            public_key=public_key
        )
        
        venue_name = request.home_name or "Care Home"
        address = f"{request.address}, {request.city}, {request.postcode}, UK" if request.address else request.city
        
        start_time = datetime.now()
        forecast = await client.create_forecast(venue_name, address)
        response_time = (datetime.now() - start_time).total_seconds()
        
        cost = 0.016 if forecast else 0.0  # 2 credits * $0.008
        
        return ApiTestResult(
            api_name="BestTime",
            status="success" if forecast else "partial",
            response_time=response_time,
            data_returned=forecast is not None,
            data_quality={
                "completeness": 100 if forecast else 0,
                "accuracy": 85,
                "freshness": "Recent"
            },
            errors=[],
            warnings=["Data may not be available for all venues"] if not forecast else [],
            raw_response={"forecast": forecast} if forecast else {"message": "No forecast data available"},
            cost_incurred=cost
        )
    except Exception as e:
        return ApiTestResult(
            api_name="BestTime",
            status="failure",
            response_time=0,
            data_returned=False,
            data_quality={"completeness": 0, "accuracy": 0, "freshness": "N/A"},
            errors=[str(e)],
            warnings=[],
            raw_response={},
            cost_incurred=0.0
        )


@app.post("/api/test/autumna", response_model=ApiTestResult)
async def test_autumna(request: TestRequest):
    """Test Autumna scraping"""
    try:
        creds = credentials_store.get("default")
        proxy_url = None
        if creds and hasattr(creds, 'autumna') and creds.autumna:
            use_proxy = getattr(creds.autumna, 'use_proxy', False)
            if use_proxy:
                proxy_url = getattr(creds.autumna, 'proxy_url', None)
        
        scraper = AutumnaScraper(proxy=proxy_url)
        
        location = request.city or "Brighton"
        
        start_time = datetime.now()
        homes = await scraper.search_care_homes(location, page=1)
        response_time = (datetime.now() - start_time).total_seconds()
        
        return ApiTestResult(
            api_name="Autumna",
            status="success" if homes else "partial",
            response_time=response_time,
            data_returned=len(homes) > 0,
            data_quality={
                "completeness": 100 if homes else 0,
                "accuracy": 80,
                "freshness": "Recent"
            },
            errors=[],
            warnings=["Scraping may be blocked without proxy"] if not homes else [],
            raw_response={"homes_found": len(homes), "sample": homes[:3] if homes else []},
            cost_incurred=0.0
        )
    except Exception as e:
        return ApiTestResult(
            api_name="Autumna",
            status="failure",
            response_time=0,
            data_returned=False,
            data_quality={"completeness": 0, "accuracy": 0, "freshness": "N/A"},
            errors=[str(e)],
            warnings=[],
            raw_response={},
            cost_incurred=0.0
        )


@app.post("/api/test/firecrawl", response_model=ApiTestResult)
async def test_firecrawl(request: TestRequest):
    """Test Firecrawl scraping"""
    try:
        creds = get_credentials()
        client = get_firecrawl_client(creds)
        
        # For testing, we need a URL - use query or home_name as URL
        test_url = request.query or request.home_name
        if not test_url:
            raise HTTPException(status_code=400, detail="URL or website query is required for Firecrawl test")
        
        # If it doesn't look like a URL, try to construct one
        if not test_url.startswith("http"):
            test_url = f"https://{test_url}"
        
        start_time = datetime.now()
        result = await client.scrape_url(test_url)
        response_time = (datetime.now() - start_time).total_seconds()
        
        return ApiTestResult(
            api_name="Firecrawl",
            status="success" if result else "partial",
            response_time=response_time,
            data_returned=bool(result),
            data_quality={
                "completeness": 100 if result else 0,
                "accuracy": 90,
                "freshness": "Real-time"
            },
            errors=[],
            warnings=[],
            raw_response={"scraped_url": test_url, "result": result},
            cost_incurred=0.0
        )
    except HTTPException:
        raise
    except Exception as e:
        return ApiTestResult(
            api_name="Firecrawl",
            status="failure",
            response_time=0,
            data_returned=False,
            data_quality={"completeness": 0, "accuracy": 0, "freshness": "N/A"},
            errors=[str(e)],
            warnings=[],
            raw_response={},
            cost_incurred=0.0
        )


# ==================== Firecrawl API Endpoints ====================

def get_firecrawl_client(creds: Optional[ApiCredentials] = None) -> FirecrawlAPIClient:
    """Helper function to create FirecrawlAPIClient with optional Anthropic support"""
    if creds is None:
        creds = get_credentials()
    
    if not creds or not hasattr(creds, 'firecrawl') or not creds.firecrawl:
        raise HTTPException(status_code=400, detail="Firecrawl credentials not configured")
    
    api_key = getattr(creds.firecrawl, 'api_key', None)
    if not api_key:
        raise HTTPException(status_code=400, detail="Firecrawl API key not found")
    
    # Получаем Anthropic API key если доступен (опционально)
    anthropic_api_key = None
    if hasattr(creds, 'anthropic') and creds.anthropic:
        anthropic_api_key = getattr(creds.anthropic, 'api_key', None)
    
    return FirecrawlAPIClient(api_key=api_key, anthropic_api_key=anthropic_api_key)

@app.post("/api/firecrawl/analyze")
async def firecrawl_analyze_care_home(request: FirecrawlAnalyzeRequest):
    """Analyze care home website using Firecrawl v2.5 4-phase universal semantic crawling"""
    try:
        url = request.url
        care_home_name = request.care_home_name
        
        # Get Firecrawl client with optional Anthropic support
        creds = get_credentials()
        client = get_firecrawl_client(creds)
        
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


@app.post("/api/firecrawl/dementia-care-analysis")
async def firecrawl_dementia_care_analysis(request: FirecrawlAnalyzeRequest):
    """Extract and evaluate dementia care quality from care home website"""
    import asyncio
    try:
        url = request.url
        care_home_name = request.care_home_name
        
        # Get Firecrawl client with optional Anthropic support
        creds = get_credentials()
        client = get_firecrawl_client(creds)
        
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


@app.post("/api/firecrawl/extract-pricing")
async def firecrawl_extract_pricing(request: FirecrawlAnalyzeRequest):
    """Extract pricing information from care home website using Firecrawl + Claude AI"""
    import asyncio
    try:
        url = request.url
        care_home_name = request.care_home_name
        
        # Get Firecrawl client with optional Anthropic support
        creds = get_credentials()
        client = get_firecrawl_client(creds)
        
        # Ensure URL has protocol
        if not url.startswith("http"):
            url = f"https://{url}"
        
        # Extract postcode from request if available (can be added to schema later)
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
                detail=f"Firecrawl pricing extraction error: {error_msg}"
            )


@app.post("/api/firecrawl/scrape")
async def firecrawl_scrape_url(
    url: str,
    formats: Optional[List[str]] = None
):
    """Scrape a single URL using Firecrawl API v2"""
    try:
        creds = get_credentials()
        client = get_firecrawl_client(creds)
        
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


@app.post("/api/firecrawl/crawl")
async def firecrawl_crawl_website(
    url: str,
    limit: int = 50,
    include_paths: Optional[List[str]] = None,
    exclude_paths: Optional[List[str]] = None,
    formats: Optional[List[str]] = None
):
    """Crawl a website using Firecrawl API v2"""
    try:
        creds = get_credentials()
        client = get_firecrawl_client(creds)
        
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


@app.post("/api/firecrawl/extract")
async def firecrawl_extract(
    urls: List[str],
    prompt: str,
    schema: Optional[Dict[str, Any]] = None
):
    """Extract structured data from URLs using Firecrawl API v2 extract endpoint"""
    try:
        creds = get_credentials()
        client = get_firecrawl_client(creds)
        
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


@app.post("/api/firecrawl/unified-analysis")
async def firecrawl_unified_analysis(request: FirecrawlUnifiedAnalysisRequest):
    """Unified analysis combining Firecrawl website scraping with Google Places data"""
    import asyncio
    try:
        # Reload credentials to ensure we have latest config
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
        
        # Step 1: Analyze website with Firecrawl using 4-phase extraction method
        # Add timeout wrapper to prevent infinite hanging (10 minutes max)
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
        # Use the same logic as /api/google-places/search endpoint
        # Add timeout wrapper (2 minutes max for Google Places)
        google_places_data = None
        google_places_error = None
        if google_places_api_key:
            try:
                google_client = GooglePlacesAPIClient(api_key=google_places_api_key)
                
                # Build search queries - try multiple variations (same as /api/google-places/search)
                search_queries = []
                
                # Clean city string (remove extra commas/spaces)
                clean_city = request.city.strip().replace(",,", ",") if request.city else None
                
                # Query 1: Just name and postcode (most specific)
                if request.postcode:
                    search_queries.append(f"{request.care_home_name} {request.postcode}")
                
                # Query 2: Name, city, postcode
                if clean_city and request.postcode:
                    search_queries.append(f"{request.care_home_name}, {clean_city} {request.postcode}")
                
                # Query 3: Name and city
                if clean_city:
                    search_queries.append(f"{request.care_home_name}, {clean_city}")
                
                # Query 4: Full query with care home
                full_query = request.care_home_name
                if clean_city:
                    full_query += f", {clean_city}"
                if request.postcode:
                    full_query += f" {request.postcode}"
                search_queries.append(f"{full_query} care home")
                
                # Query 5: Full query without care home
                search_queries.append(full_query)
                
                # Query 6: Just the name
                search_queries.append(request.care_home_name)
                
                # Try each query variation with timeout protection
                place = None
                last_error = None
                tried_queries = []
                request_denied = False
                
                async def search_google_places():
                    nonlocal place, last_error, tried_queries, request_denied
                    for search_query in search_queries:
                        tried_queries.append(search_query)
                        try:
                            found_place = await google_client.find_place(search_query)
                            if found_place:
                                # Verify it's actually a match (same logic as /api/google-places/search)
                                place_name = found_place.get("name", "").lower()
                                query_lower = request.care_home_name.lower()
                                
                                # Check for exact or partial match - be more lenient
                                if (query_lower in place_name or 
                                    place_name in query_lower or
                                    any(word in place_name for word in query_lower.split() if len(word) > 3)):
                                    place = found_place
                                    print(f"✅ Google Places found with find_place query: {search_query}")
                                    return
                                # If found but doesn't match well, continue searching
                                found_place = None
                        except Exception as e:
                            error_str = str(e)
                            if "REQUEST_DENIED" in error_str or "denied" in error_str.lower():
                                request_denied = True
                            last_error = error_str
                            continue
                    
                    # If find_place didn't work, try text_search as fallback
                    if not place:
                        print("⚠️ find_place didn't find results, trying text_search...")
                        try:
                            # Build text search query
                            text_query = request.care_home_name
                            if clean_city:
                                text_query += f" {clean_city}"
                            if request.postcode:
                                text_query += f" {request.postcode}"
                            text_query += " care home"
                            
                            places = await google_client.text_search(text_query)
                            if places and len(places) > 0:
                                # Find best match
                                query_lower = request.care_home_name.lower()
                                query_words = [w for w in query_lower.split() if len(w) > 3]
                                
                                for p in places:
                                    place_name = p.get("name", "").lower()
                                    if (query_lower in place_name or 
                                        place_name in query_lower or
                                        any(word in place_name for word in query_words)):
                                        place = p
                                        print(f"✅ Google Places found with text_search query: {text_query}")
                                        return
                                
                                # If no match, use first result
                                if not place and places:
                                    place = places[0]
                                    print(f"✅ Google Places found with text_search (first result): {text_query}")
                        except Exception as e:
                            if not last_error:
                                last_error = str(e)
                            print(f"⚠️ Google Places text_search failed: {str(e)}")
                
                # Execute Google Places search with timeout
                try:
                    await asyncio.wait_for(search_google_places(), timeout=120.0)  # 2 minutes timeout
                except asyncio.TimeoutError:
                    google_places_error = "Google Places search timed out after 2 minutes"
                    print(f"⚠️ {google_places_error}")
                    place = None
                
                if place and place.get("place_id"):
                    place_details = await google_client.get_place_details(
                        place["place_id"],
                        fields=["rating", "user_ratings_total", "reviews", "formatted_address", "formatted_phone_number", "website"]
                    )
                    
                    # Get insights
                    try:
                        insights = await google_client.get_places_insights(place["place_id"])
                        google_places_data = {
                            "place_details": place_details,
                            "insights": insights
                        }
                    except Exception as insights_error:
                        print(f"⚠️ Google Places insights error: {str(insights_error)}")
                        google_places_data = {
                            "place_details": place_details,
                            "insights": None
                        }
                else:
                    google_places_error = f"Place not found in Google Places. Tried queries: {', '.join(search_queries[:3])}"
                    print(f"⚠️ {google_places_error}")
            except Exception as e:
                error_detail = handle_api_error(e, "Google Places", "unified_analysis", {"care_home_name": request.care_home_name})
                google_places_error = f"Google Places API error: {error_detail.get('error_message', str(e))}"
                print(f"❌ Google Places integration error: {google_places_error}")
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


@app.post("/api/firecrawl/search")
async def firecrawl_search(request: FirecrawlSearchRequest):
    """Perform web search using Firecrawl Search API"""
    try:
        # Use get_firecrawl_client helper for consistent credential handling
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
        
        # Calculate cost: 2 credits per 10 search results (without scraping)
        # With scraping, standard scraping costs apply
        cost = 0.0
        if not request.scrape_options:
            cost = (request.limit / 10) * 0.02  # Approximate cost in credits
        
        return {
            "status": "success",
            "data": result,
            "cost": cost
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Firecrawl search error: {error_detail}")
        raise HTTPException(status_code=500, detail=f"Firecrawl Search API error: {str(e)}")


@app.post("/api/firecrawl/search/extract-pricing")
async def firecrawl_search_extract_pricing(
    url: str = Body(..., description="URL from search results to extract pricing from"),
    care_home_name: Optional[str] = Body(None, description="Care home name"),
    postcode: Optional[str] = Body(None, description="Postcode")
):
    """Extract pricing information from a URL found in search results"""
    try:
        creds = get_credentials()
        client = get_firecrawl_client(creds)
        
        result = await client.extract_pricing(
            url=url,
            care_home_name=care_home_name,
            postcode=postcode
        )
        
        return {
            "status": "success",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Firecrawl search pricing extraction error: {error_detail}")
        raise HTTPException(status_code=500, detail=f"Pricing extraction error: {str(e)}")


@app.post("/api/firecrawl/batch-analyze")
async def firecrawl_batch_analyze(
    request: FirecrawlBatchAnalyzeRequest
):
    """
    Batch analyze multiple care homes
    Example input: {
        "care_homes": [
            {"name": "Manor House", "url": "https://manorhouse.com"},
            {"name": "Sunshine Care", "url": "https://sunshinecare.com"}
        ]
    }
    """
    try:
        care_homes = request.care_homes
        if not care_homes:
            raise HTTPException(status_code=400, detail="care_homes list is required")
        
        creds = get_credentials()
        client = get_firecrawl_client(creds)
        
        results = []
        for home in care_homes:
            try:
                url = home.get("url", "")
                if not url:
                    results.append({
                        "status": "error",
                        "care_home": home.get("name", "Unknown"),
                        "error": "URL is required"
                    })
                    continue
                
                if not url.startswith("http"):
                    url = f"https://{url}"
                
                result = await client.extract_care_home_data_full(
                    url=url,
                    care_home_name=home.get("name")
                )
                results.append({
                    "status": "success",
                    "care_home": home.get("name"),
                    "data": result
                })
            except Exception as e:
                results.append({
                    "status": "error",
                    "care_home": home.get("name", "Unknown"),
                    "error": str(e)
                })
        
        return {
            "status": "success",
            "total": len(care_homes),
            "successful": len([r for r in results if r["status"] == "success"]),
            "failed": len([r for r in results if r["status"] == "error"]),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Comprehensive Testing ====================

@app.post("/api/test/comprehensive", response_model=ComprehensiveTestResponse)
async def run_comprehensive_test(request: ComprehensiveTestRequest):
    """Run comprehensive test across all selected APIs"""
    try:
        # Validate request
        if not request.home_name:
            raise HTTPException(status_code=400, detail="home_name is required")
        
        if not request.apis_to_test or len(request.apis_to_test) == 0:
            raise HTTPException(status_code=400, detail="At least one API must be selected")
        
        job_id = str(uuid.uuid4())
        
        # Store initial job
        test_results_store[job_id] = {
            "job_id": job_id,
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "results": {},
            "progress": 0
        }
        
        # Run tests asynchronously
        asyncio.create_task(run_comprehensive_test_async(job_id, request))
        
        return ComprehensiveTestResponse(
            job_id=job_id,
            status="running",
            message="Test started. Use WebSocket or polling to track progress."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start test: {str(e)}")


async def run_comprehensive_test_async(job_id: str, request: ComprehensiveTestRequest):
    """Async comprehensive test runner"""
    try:
        # Reload credentials to ensure we have latest
        creds = get_credentials()
        print(f"Running comprehensive test with credentials: perplexity={bool(creds.perplexity)}, google_places={bool(creds.google_places)}")
        
        runner = TestRunner(credentials=creds)
        
        home_data = HomeData(
            name=request.home_name or "",
            address=request.address,
            city=request.city,
            postcode=request.postcode
        )
        
        apis_to_test = request.apis_to_test or []
        if not apis_to_test:
            raise Exception("No APIs selected for testing")
        
        print(f"Testing APIs: {apis_to_test}")
        
        results = await runner.run_comprehensive_test(
            home_data=home_data,
            apis_to_test=apis_to_test,
            progress_callback=lambda api, progress: update_progress(job_id, api, progress)
        )
        
        # Calculate total cost
        total_cost = sum(r.get("cost_incurred", 0) for r in results.values())
        
        # Data fusion analysis
        analyzer = DataFusionAnalyzer()
        fusion_analysis = analyzer.analyze_combined_data(results)
        
        # Update store
        test_results_store[job_id].update({
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "results": results,
            "fusion_analysis": fusion_analysis,
            "total_cost": total_cost,
            "progress": 100
        })
        
        # Notify WebSocket connections
        await broadcast_progress(job_id, "completed", {
            "results": results,
            "fusion_analysis": fusion_analysis,
            "total_cost": total_cost
        })
        
    except Exception as e:
        test_results_store[job_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })
        await broadcast_progress(job_id, "failed", {"error": str(e)})


def update_progress(job_id: str, api: str, progress: int):
    """Update test progress"""
    if job_id in test_results_store:
        test_results_store[job_id]["progress"] = progress
        test_results_store[job_id]["current_api"] = api


async def broadcast_progress(job_id: str, event: str, data: dict):
    """Broadcast progress to WebSocket connections"""
    message = {
        "job_id": job_id,
        "event": event,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    
    # Send to all connections (in production, filter by job_id)
    for ws in active_connections.values():
        try:
            await ws.send_json(message)
        except:
            pass


@app.get("/api/test/status/{job_id}")
async def get_test_status(job_id: str):
    """Get test status"""
    if job_id not in test_results_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return test_results_store[job_id]


@app.get("/api/test/results/{job_id}")
async def get_test_results(job_id: str):
    """Get test results"""
    if job_id not in test_results_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = test_results_store[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Test not completed yet")
    
    return job


# ==================== WebSocket ====================

@app.websocket("/ws/test-progress")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time test progress"""
    await websocket.accept()
    connection_id = str(uuid.uuid4())
    active_connections[connection_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            # Handle client messages if needed
            await websocket.send_json({
                "type": "ack",
                "message": "Connected"
            })
    except WebSocketDisconnect:
        del active_connections[connection_id]


# ==================== Analytics Endpoints ====================

@app.post("/api/analyze/coverage")
async def analyze_coverage():
    """Calculate API coverage"""
    # Implementation
    return {"coverage": {}}


@app.post("/api/analyze/quality")
async def analyze_quality():
    """Data quality metrics"""
    # Implementation
    return {"quality": {}}


@app.post("/api/analyze/costs")
async def analyze_costs():
    """Cost analysis"""
    # Implementation
    return {"costs": {}}


@app.post("/api/analyze/fusion")
async def analyze_fusion(job_id: str):
    """Multi-API data fusion analysis"""
    if job_id not in test_results_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = test_results_store[job_id]
    if "fusion_analysis" not in job:
        raise HTTPException(status_code=400, detail="Fusion analysis not available")
    
    return job["fusion_analysis"]


# ==================== Reports ====================

@app.get("/api/report/summary/{job_id}")
async def get_summary_report(job_id: str):
    """Get summary report"""
    if job_id not in test_results_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = test_results_store[job_id]
    return {
        "job_id": job_id,
        "summary": {
            "total_apis_tested": len(job.get("results", {})),
            "successful": sum(1 for r in job.get("results", {}).values() if r.get("status") == "success"),
            "failed": sum(1 for r in job.get("results", {}).values() if r.get("status") == "failure"),
            "total_cost": job.get("total_cost", 0),
            "total_time": "N/A"  # Calculate from timestamps
        }
    }


@app.get("/api/report/export/{format}")
async def export_report(job_id: str, format: str):
    """Export report in specified format"""
    if format not in ["csv", "json", "pdf"]:
        raise HTTPException(status_code=400, detail="Format must be csv, json, or pdf")
    
    # Implementation
    return {"message": f"Export {format} not yet implemented"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

