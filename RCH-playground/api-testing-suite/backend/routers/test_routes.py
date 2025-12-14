"""
Test Routes
Handles API testing endpoints for all services
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Body
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import uuid

from models.schemas import (
    TestRequest,
    ApiTestResult,
    ComprehensiveTestRequest,
    ComprehensiveTestResponse,
    HomeData
)
from api_clients.fsa_client import FSAAPIClient
from api_clients.companies_house_client import CompaniesHouseAPIClient
from api_clients.google_places_client import GooglePlacesAPIClient
from api_clients.perplexity_client import PerplexityAPIClient
from api_clients.besttime_client import BestTimeClient
from api_clients.autumna_scraper import AutumnaScraper
from api_clients.firecrawl_client import FirecrawlAPIClient
from services.test_runner import TestRunner
from services.data_fusion import DataFusionAnalyzer
from utils.client_factory import get_cqc_client
from utils.error_handler import handle_api_error
from utils.auth import credentials_store
from utils.state_manager import active_connections, test_results_store
from config_manager import get_credentials

router = APIRouter(prefix="/api/test", tags=["Testing"])


@router.post("/cqc", response_model=ApiTestResult)
async def test_cqc(request: TestRequest):
    """Test CQC API - works in Sandbox mode without Partner Code"""
    try:
        client = get_cqc_client()
        
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


@router.post("/fsa", response_model=ApiTestResult)
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


@router.post("/companies-house", response_model=ApiTestResult)
async def test_companies_house(request: TestRequest):
    """Test Companies House API"""
    try:
        from utils.client_factory import get_companies_house_client
        client = get_companies_house_client()
        
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


@router.post("/google-places", response_model=ApiTestResult)
async def test_google_places(request: TestRequest):
    """Test Google Places API"""
    try:
        from utils.client_factory import get_google_places_client
        client = get_google_places_client()
        
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
        return ApiTestResult(
            api_name="Google Places",
            status="failure",
            response_time=0,
            data_returned=False,
            data_quality={"completeness": 0, "accuracy": 0, "freshness": "N/A"},
            errors=[str(e)],
            warnings=[],
            raw_response={},
            cost_incurred=0.0
        )


@router.post("/perplexity", response_model=ApiTestResult)
async def test_perplexity(request: TestRequest):
    """Test Perplexity API"""
    try:
        from utils.client_factory import get_perplexity_client
        client = get_perplexity_client()
        
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


@router.post("/besttime", response_model=ApiTestResult)
async def test_besttime(request: TestRequest):
    """Test BestTime.app API"""
    try:
        from utils.client_factory import get_besttime_client
        client = get_besttime_client()
        
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


@router.post("/autumna", response_model=ApiTestResult)
async def test_autumna(request: TestRequest):
    """Test Autumna scraping"""
    try:
        from utils.client_factory import get_autumna_scraper
        
        scraper = get_autumna_scraper()
        
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


@router.post("/firecrawl", response_model=ApiTestResult)
async def test_firecrawl(request: TestRequest):
    """Test Firecrawl scraping"""
    try:
        from utils.client_factory import get_firecrawl_client
        
        client = get_firecrawl_client()
        
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


@router.post("/comprehensive", response_model=ComprehensiveTestResponse)
async def run_comprehensive_test(request: ComprehensiveTestRequest):
    """Run comprehensive test across all selected APIs"""
    try:
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
            "progress": 0,
            "current_api": None
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
        creds = get_credentials()
        runner = TestRunner(credentials=creds)
        
        home_data = HomeData(
            name=request.home_name or "",
            address=request.address,
            city=request.city,
            postcode=request.postcode
        )
        
        results = await runner.run_comprehensive_test(
            home_data=home_data,
            apis_to_test=request.apis_to_test or [],
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
    
    for ws in active_connections.values():
        try:
            await ws.send_json(message)
        except:
            pass


@router.get("/status/{job_id}")
async def get_test_status(job_id: str):
    """Get test status"""
    if job_id not in test_results_store:
        return {
            "job_id": job_id,
            "status": "pending",
            "progress": 0,
            "message": "Job is being initialized, please wait..."
        }
    
    return test_results_store[job_id]


@router.get("/results/{job_id}")
async def get_test_results(job_id: str):
    """Get test results"""
    if job_id not in test_results_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = test_results_store[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Test not completed yet")
    
    return job


@router.websocket("/ws/test-progress")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time test progress"""
    await websocket.accept()
    connection_id = str(uuid.uuid4())
    active_connections[connection_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back or handle commands
            await websocket.send_json({"message": "connected", "connection_id": connection_id})
    except WebSocketDisconnect:
        del active_connections[connection_id]

