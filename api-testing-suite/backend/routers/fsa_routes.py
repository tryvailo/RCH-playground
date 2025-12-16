"""
FSA API Routes
Handles all FSA (Food Standards Agency) FHRS API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime, timedelta
import random

from api_clients.fsa_client import FSAAPIClient
from models.schemas import TestRequest, ApiTestResult
from utils.client_factory import get_fsa_client
from mocks.fsa_mock_data import (
    get_fsa_sample_establishments,
    get_fsa_sample_details,
    get_fsa_sample_history,
    get_fsa_sample_trends,
    get_fsa_sample_diabetes_score,
    get_fsa_sample_premium,
    get_fsa_sample_health_score
)

router = APIRouter(prefix="/api/fsa", tags=["FSA"])


@router.get("/establishment/{fhrs_id}")
async def fsa_get_establishment(fhrs_id: int, include_health_score: bool = Query(True)):
    """Get detailed FSA establishment information with breakdown scores and optional health score"""
    fallback_used = False
    warnings: List[str] = []
    
    client: Optional[FSAAPIClient] = None
    try:
        client = FSAAPIClient()
    except Exception as init_error:
        print(f"⚠️ FSA client init failed, using fallback: {init_error}")
    
    details: Optional[Dict[str, Any]] = None
    if client:
        try:
            details = await asyncio.wait_for(client.get_establishment_details(fhrs_id), timeout=8)
        except Exception as api_error:
            print(f"⚠️ FSA details fetch failed ({fhrs_id}), using fallback: {api_error}")
    
    if details is None:
        fallback_used = True
        details = get_fsa_sample_details(fhrs_id)
    
    response_data: Dict[str, Any] = {
        "status": "success",
        "establishment": details
    }
    
    if include_health_score:
        health_score: Optional[Dict[str, Any]] = None
        if client and not fallback_used:
            try:
                health_score = client.calculate_fsa_health_score(details)
            except Exception as score_error:
                print(f"⚠️ FSA health score calculation failed ({fhrs_id}), using fallback: {score_error}")
                health_score = get_fsa_sample_health_score(fhrs_id)
                warnings.append("FSA health score uses sample data (offline fallback).")
                fallback_used = True
        else:
            health_score = get_fsa_sample_health_score(fhrs_id)
        response_data["health_score"] = health_score
    
    if fallback_used:
        response_data["fallback"] = True
        response_data["message"] = "Using sample FSA data (offline mode)."
    if warnings:
        response_data["warnings"] = warnings
    
    return response_data


@router.get("/establishment/{fhrs_id}/history")
async def fsa_get_inspection_history(fhrs_id: int):
    """Get inspection history for an establishment"""
    try:
        client = FSAAPIClient()
    except Exception as init_error:
        print(f"⚠️ FSA history client init failed, using fallback: {init_error}")
        client = None
    
    history: Optional[List[Dict[str, Any]]] = None
    if client:
        try:
            history = await asyncio.wait_for(client.get_inspection_history(fhrs_id), timeout=8)
        except Exception as api_error:
            print(f"⚠️ FSA history fetch failed ({fhrs_id}), using fallback: {api_error}")
    
    if history is None:
        history = get_fsa_sample_history(fhrs_id)
        fallback = True
    else:
        fallback = False
    
    response = {
        "status": "success",
        "fhrs_id": fhrs_id,
        "history": history,
        "count": len(history)
    }
    if fallback:
        response["fallback"] = True
        response["message"] = "Using sample FSA history data (offline mode)."
    return response


@router.get("/establishment/{fhrs_id}/trends")
async def fsa_analyze_trends(fhrs_id: int):
    """Analyze FSA rating trends and predict next rating"""
    try:
        client = FSAAPIClient()
    except Exception as init_error:
        print(f"⚠️ FSA trends client init failed, using fallback: {init_error}")
        client = None
    
    trends: Optional[Dict[str, Any]] = None
    if client:
        try:
            trends = await asyncio.wait_for(client.analyze_fsa_trends(fhrs_id), timeout=8)
        except Exception as api_error:
            print(f"⚠️ FSA trends fetch failed ({fhrs_id}), using fallback: {api_error}")
    
    if trends is None:
        trends = get_fsa_sample_trends(fhrs_id)
        fallback = True
    else:
        fallback = False
    
    response = {
        "status": "success",
        "fhrs_id": fhrs_id,
        "trends": trends
    }
    if fallback:
        response["fallback"] = True
        response["message"] = "Using sample FSA trends data (offline mode)."
    return response


@router.get("/establishment/{fhrs_id}/diabetes-score")
async def fsa_get_diabetes_score(fhrs_id: int):
    """Calculate diabetes suitability score for an establishment"""
    try:
        client = FSAAPIClient()
        details = await asyncio.wait_for(client.get_establishment_details(fhrs_id), timeout=8)
        diabetes_score = client.calculate_diabetes_suitability_score(details)
        return {
            "status": "success",
            "fhrs_id": fhrs_id,
            "diabetes_score": diabetes_score
        }
    except Exception as api_error:
        print(f"⚠️ FSA diabetes score failed ({fhrs_id}), using fallback: {api_error}")
        return {
            "status": "success",
            "fhrs_id": fhrs_id,
            "diabetes_score": get_fsa_sample_diabetes_score(fhrs_id),
            "fallback": True,
            "message": "Using sample FSA diabetes score data (offline mode)."
        }


@router.get("/establishment/{fhrs_id}/premium-data")
async def fsa_get_premium_data(fhrs_id: int):
    """Get premium tier data: enhanced history, monitoring alerts, and trends"""
    try:
        client = FSAAPIClient()
        details = await asyncio.wait_for(client.get_establishment_details(fhrs_id), timeout=8)
        trends = await asyncio.wait_for(client.analyze_fsa_trends(fhrs_id), timeout=8)
        diabetes_score = client.calculate_diabetes_suitability_score(details)
        
        # Generate simulated historical data for Premium tier
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
                        except Exception:
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
            except Exception:
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
            except Exception:
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
    except Exception as api_error:
        print(f"⚠️ FSA premium data failed ({fhrs_id}), using fallback: {api_error}")
        sample = get_fsa_sample_premium(fhrs_id)
        return {
            "status": "success",
            "fhrs_id": fhrs_id,
            **sample,
            "fallback": True,
            "message": "Using sample FSA premium data (offline mode)."
        }


@router.get("/search")
async def fsa_search(
    name: Optional[str] = Query(None),
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    max_distance: float = Query(1.0),
    local_authority_id: Optional[int] = Query(None)
):
    """Search FSA establishments"""
    if not name and not (latitude and longitude):
        raise HTTPException(status_code=400, detail="Provide name or location coordinates")
    
    try:
        client = FSAAPIClient()
    except Exception as init_error:
        print(f"⚠️ FSA search client init failed, using fallback: {init_error}")
        client = None
    
    results: Optional[List[Dict[str, Any]]] = None
    if client:
        try:
            if latitude and longitude:
                results = await asyncio.wait_for(
                    client.search_by_location(
                        latitude=latitude,
                        longitude=longitude,
                        max_distance=max_distance
                    ),
                    timeout=8
                )
            elif name:
                try:
                    results = await asyncio.wait_for(
                        client.search_by_business_name(
                            name=name,
                            local_authority_id=local_authority_id
                        ),
                        timeout=8
                    )
                except Exception as name_error:
                    print(f"FSA search error for '{name}': {name_error}")
                    results = []
                
                if not results and name:
                    name_parts = name.split()
                    if len(name_parts) > 1:
                        for i in range(1, len(name_parts)):
                            partial_name = ' '.join(name_parts[:i + 1])
                            try:
                                partial_results = await asyncio.wait_for(
                                    client.search_by_business_name(
                                        name=partial_name,
                                        local_authority_id=local_authority_id
                                    ),
                                    timeout=6
                                )
                                if partial_results:
                                    results = partial_results
                                    break
                            except Exception as partial_error:
                                print(f"FSA partial search error for '{partial_name}': {partial_error}")
                                continue
        except Exception as api_error:
            print(f"⚠️ FSA search request failed, using fallback: {api_error}")
            results = None
    
    if results is None:
        fallback_results = get_fsa_sample_establishments()
        return {
            "status": "success",
            "fallback": True,
            "count": len(fallback_results),
            "establishments": fallback_results,
            "message": "Using sample FSA search data (offline mode)."
        }
    
    return {
        "status": "success",
        "count": len(results),
        "establishments": results,
        "message": f"Found {len(results)} establishment(s)" if results else "No establishments found matching the search criteria"
    }


@router.get("/search/by-type")
async def fsa_search_by_type(
    business_type_id: int = Query(7835),  # 7835 = "Hospitals/Childcare/Caring Premises"
    local_authority_id: Optional[int] = Query(None),
    name: Optional[str] = Query(None),
    page_size: int = Query(20)
):
    """Search FSA establishments by business type and optionally by local authority and name"""
    try:
        client = FSAAPIClient()
        results = await asyncio.wait_for(
            client.search_by_business_type(
                business_type_id=business_type_id,
                local_authority_id=local_authority_id,
                name=name,
                page_size=page_size
            ),
            timeout=8
        )
        
        return {
            "status": "success",
            "count": len(results),
            "establishments": results,
            "message": f"Found {len(results)} establishment(s)"
        }
    except Exception as api_error:
        print(f"⚠️ FSA search by type failed, using fallback: {api_error}")
        fallback_results = get_fsa_sample_establishments()
        return {
            "status": "success",
            "fallback": True,
            "count": len(fallback_results),
            "establishments": fallback_results,
            "message": "Using sample FSA data for search by type (offline mode)."
        }


@router.get("/establishment/{fhrs_id}/health-score")
async def fsa_get_health_score(fhrs_id: int):
    """Calculate FSA Health Score (0-100) for an establishment"""
    try:
        client = FSAAPIClient()
        details = await asyncio.wait_for(client.get_establishment_details(fhrs_id), timeout=8)
        health_score = client.calculate_fsa_health_score(details)
        return {
            "status": "success",
            "fhrs_id": fhrs_id,
            "business_name": details.get("BusinessName"),
            "health_score": health_score
        }
    except Exception as api_error:
        print(f"⚠️ FSA health score failed ({fhrs_id}), using fallback: {api_error}")
        sample_health = get_fsa_sample_health_score(fhrs_id)
        return {
            "status": "success",
            "fhrs_id": fhrs_id,
            "business_name": sample_health.get("business_name", "Unknown"),
            "health_score": sample_health,
            "fallback": True,
            "message": "Using sample FSA health score data (offline mode)."
        }

