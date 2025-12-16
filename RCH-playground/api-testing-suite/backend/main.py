"""
FastAPI Main Application
RightCareHome API Testing Suite
"""
import sys
import os
from pathlib import Path

# Add RCH-data src to Python path if not already there
project_root = Path(__file__).parent.parent.parent.parent.parent
rch_data_src_path = project_root / "RCH-data" / "src"
if str(rch_data_src_path) not in sys.path:
    sys.path.insert(0, str(rch_data_src_path))

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import asyncio
import json
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime
from copy import deepcopy

from api_clients.cqc_client import CQCAPIClient
from api_clients.fsa_client import FSAAPIClient
from api_clients.companies_house_client import CompaniesHouseAPIClient
from api_clients.google_places_client import GooglePlacesAPIClient
from api_clients.perplexity_client import PerplexityAPIClient
from api_clients.besttime_client import BestTimeClient
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

# Import from core module (refactored)
from core.dependencies import (
    get_cqc_client,
    get_google_places_client as _get_google_places_client,
    credentials_store,
    active_connections,
    test_results_store
)
from core.lifespan import lifespan
from core.error_handlers import handle_cqc_error


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


# RCH-data routes
try:
    from api_clients.rch_data_routes import router as rch_data_router
    app.include_router(rch_data_router)
    print("✅ RCH-data routes registered")
except ImportError:
    print("⚠️ RCH-data routes not available (modules not installed)")

# Health check routes
try:
    from api_clients.health_check import router as health_check_router
    app.include_router(health_check_router)
    print("✅ Health check routes registered")
except ImportError:
    print("⚠️ Health check routes not available")

# Data Integrations routes (OS Places, ONS, OSM, NHSBSA)
try:
    from routers.os_places_routes import router as os_places_router
    app.include_router(os_places_router)
    print("✅ OS Places routes registered")
except ImportError as e:
    print(f"⚠️ OS Places routes not available: {e}")

try:
    from routers.ons_routes import router as ons_router
    app.include_router(ons_router)
    print("✅ ONS routes registered")
except ImportError as e:
    print(f"⚠️ ONS routes not available: {e}")

try:
    from routers.osm_routes import router as osm_router
    app.include_router(osm_router)
    print("✅ OSM routes registered")
except ImportError as e:
    print(f"⚠️ OSM routes not available: {e}")

try:
    from routers.nhsbsa_routes import router as nhsbsa_router
    app.include_router(nhsbsa_router)
    print("✅ NHSBSA routes registered")
except ImportError as e:
    print(f"⚠️ NHSBSA routes not available: {e}")

# Professional Report Job Routes (for async report generation)
try:
    from routers.professional_report_job_routes import router as professional_report_job_router
    app.include_router(professional_report_job_router)
    print("✅ Professional Report Job routes registered")
except ImportError as e:
    print(f"⚠️ Professional Report Job routes not available: {e}")

# Professional Report Retry Routes
try:
    from routers.report_retry_routes import router as report_retry_router
    app.include_router(report_retry_router)
    print("✅ Professional Report Retry routes registered")
except ImportError as e:
    print(f"⚠️ Professional Report Retry routes not available: {e}")

# Cron routes (for Vercel Cron - also works locally as regular endpoints)
try:
    from cron.retry_missing_data import router as cron_router
    app.include_router(cron_router)
    print("✅ Cron routes registered")
except ImportError as e:
    print(f"⚠️ Cron routes not available: {e}")

try:
    from routers.neighbourhood_routes import router as neighbourhood_router
    app.include_router(neighbourhood_router)
    print("✅ Neighbourhood Analysis routes registered")
except ImportError as e:
    print(f"⚠️ Neighbourhood routes not available: {e}")

# Staff Quality routes
try:
    from routers.staff_quality_routes import router as staff_quality_router
    app.include_router(staff_quality_router)
    print("✅ Staff Quality routes registered")
except ImportError as e:
    print(f"⚠️ Staff Quality routes not available: {e}")

# FSA FHRS routes
try:
    from routers.fsa_routes import router as fsa_router
    app.include_router(fsa_router)
    print("✅ FSA FHRS routes registered")
except ImportError as e:
    print(f"⚠️ FSA routes not available: {e}")

# CareHome.co.uk Reviews routes
try:
    from routers.carehome_reviews_routes import router as carehome_reviews_router
    app.include_router(carehome_reviews_router)
    print("✅ CareHome.co.uk Reviews routes registered")
except ImportError as e:
    print(f"⚠️ CareHome.co.uk Reviews routes not available: {e}")

# Report routes (professional report, free report, cost analysis)
try:
    from routers.report_routes import router as report_router
    app.include_router(report_router)
    print("✅ Report routes registered (professional-report, free-report)")
except ImportError as e:
    print(f"⚠️ Report routes not available: {e}")

# Google Places routes
try:
    from routers.google_places_routes import router as google_places_router
    app.include_router(google_places_router)
    print("✅ Google Places routes registered")
except ImportError as e:
    print(f"⚠️ Google Places routes not available: {e}")

# Companies House routes
try:
    from routers.companies_house_routes import router as companies_house_router
    app.include_router(companies_house_router)
    print("✅ Companies House routes registered")
except ImportError as e:
    print(f"⚠️ Companies House routes not available: {e}")

# CQC routes
try:
    from routers.cqc_routes import router as cqc_router
    app.include_router(cqc_router)
    print("✅ CQC routes registered")
except ImportError as e:
    print(f"⚠️ CQC routes not available: {e}")

# Firecrawl routes
try:
    from routers.firecrawl_routes import router as firecrawl_router
    app.include_router(firecrawl_router)
    print("✅ Firecrawl routes registered")
except ImportError as e:
    print(f"⚠️ Firecrawl routes not available: {e}")

# Perplexity routes
try:
    from routers.perplexity_routes import router as perplexity_router
    app.include_router(perplexity_router)
    print("✅ Perplexity routes registered")
except ImportError as e:
    print(f"⚠️ Perplexity routes not available: {e}")

# Test routes
try:
    from routers.test_routes import router as test_router
    app.include_router(test_router)
    print("✅ Test routes registered")
except ImportError as e:
    print(f"⚠️ Test routes not available: {e}")

# Config routes
try:
    from routers.config_routes import router as config_router
    app.include_router(config_router)
    print("✅ Config routes registered")
except ImportError as e:
    print(f"⚠️ Config routes not available: {e}")

# Cache routes (refactored from main.py)
try:
    from routers.cache_routes import router as cache_router
    app.include_router(cache_router)
    print("✅ Cache routes registered")
except ImportError as e:
    print(f"⚠️ Cache routes not available: {e}")

# WebSocket routes (refactored from main.py)
try:
    from routers.websocket_routes import router as websocket_router
    app.include_router(websocket_router)
    print("✅ WebSocket routes registered")
except ImportError as e:
    print(f"⚠️ WebSocket routes not available: {e}")

# MSIF routes (refactored from main.py)
try:
    from routers.msif_routes import router as msif_router
    app.include_router(msif_router)
    print("✅ MSIF routes registered")
except ImportError as e:
    print(f"⚠️ MSIF routes not available: {e}")

# Proxy routes (refactored from main.py)
try:
    from routers.proxy_routes import router as proxy_router
    app.include_router(proxy_router)
    print("✅ Proxy routes registered")
except ImportError as e:
    print(f"⚠️ Proxy routes not available: {e}")

# Free Report routes (refactored from main.py)
try:
    from routers.free_report_routes import router as free_report_router
    app.include_router(free_report_router)
    print("✅ Free Report routes registered")
except ImportError as e:
    print(f"⚠️ Free Report routes not available: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RightCareHome API Testing Suite",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "config": "/api/config",
            "test": "/api/test",
            "analyze": "/api/analyze",
            "test_data": "/api/test-data",
            "report": "/api/report"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint to verify API status"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "message": "RightCareHome API Testing Suite is running"
    }


# ==================== API Configuration Endpoints ====================
# Config endpoints moved to routers/config_routes.py


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
                        "source": "Regulatory Registry"
                    },
                    {
                        "name": "Meadows House Residential and Nursing Home",
                        "address": "Cullum Welch Court, London, SE3 0PW",
                        "city": "London",
                        "postcode": "SE3 0PW",
                        "county": "Greater London",
                        "source": "Regulatory Registry"
                    },
                    {
                        "name": "Roborough House",
                        "address": "Tamerton Road, Woolwell, Plymouth, Devon, PL6 7BQ",
                        "city": "Plymouth",
                        "postcode": "PL6 7BQ",
                        "county": "Devon",
                        "source": "Regulatory Registry"
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



# ==================== Individual API Test Endpoints ====================
# Test endpoints moved to routers/test_routes.py

# ==================== Comprehensive Testing ====================
# Comprehensive test endpoints moved to routers/test_routes.py

# ==================== WebSocket ====================
# WebSocket endpoints moved to routers/websocket_routes.py

# ==================== Analytics Endpoints ====================
# Analytics endpoints moved to routers/analytics_routes.py

# ==================== Reports ====================
# Report endpoints moved to routers/report_routes.py

# ==================== Test Endpoint for Mock Data ====================

@app.get("/api/test-mock-data")
async def test_mock_data():
    """Test endpoint to verify mock data loading works in async context"""
    try:
        from services.mock_care_homes import load_mock_care_homes
        # Test synchronous call
        all_mock_sync = load_mock_care_homes()
        print(f"✅ Synchronous load: {len(all_mock_sync) if all_mock_sync else 0} homes")
        
        # Test async call
        import asyncio
        try:
            all_mock_async = await asyncio.to_thread(load_mock_care_homes)
            print(f"✅ Async to_thread load: {len(all_mock_async) if all_mock_async else 0} homes")
        except AttributeError:
            loop = asyncio.get_event_loop()
            all_mock_async = await loop.run_in_executor(None, load_mock_care_homes)
            print(f"✅ Async executor load: {len(all_mock_async) if all_mock_async else 0} homes")
        
        return {
            "status": "success",
            "sync_count": len(all_mock_sync) if all_mock_sync else 0,
            "async_count": len(all_mock_async) if all_mock_async else 0,
            "first_home": all_mock_sync[0].get('name', 'N/A') if all_mock_sync and len(all_mock_sync) > 0 else None
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

# ==================== MSIF Fair Cost Endpoint ====================
# MSIF endpoints moved to routers/msif_routes.py

# ==================== Free Report Endpoint ====================
# ==================== Free Report Endpoint ====================
# Free Report endpoint moved to routers/free_report_routes.py

# ==================== Proxy Endpoint for CORS ====================
# Proxy endpoints moved to routers/proxy_routes.py


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

