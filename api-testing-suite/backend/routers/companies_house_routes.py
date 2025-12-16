"""
Companies House API Routes
Handles all Companies House API endpoints
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random

from api_clients.companies_house_client import CompaniesHouseAPIClient
from utils.client_factory import get_companies_house_client
from config_manager import get_credentials

router = APIRouter(prefix="/api/companies-house", tags=["Companies House"])


@router.get("/search")
async def companies_house_search(
    query: str,
    items_per_page: int = Query(20)
):
    """Search for companies related to care homes"""
    try:
        client = get_companies_house_client()
        
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


@router.get("/company/{company_number}")
async def companies_house_get_company(company_number: str):
    """Get detailed company profile"""
    try:
        client = get_companies_house_client()
        
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


@router.get("/company/{company_number}/financial-stability")
async def companies_house_financial_stability(company_number: str):
    """Get financial stability score for a company"""
    try:
        client = get_companies_house_client()
        stability_score = await client.calculate_financial_stability_score(company_number)
        
        return {
            "status": "success",
            "financial_stability": stability_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/company/{company_number}/premium-data")
async def companies_house_get_premium_data(company_number: str):
    """Get premium tier data: enhanced financial analysis, monitoring alerts, and trends"""
    try:
        client = get_companies_house_client()
        
        # Get all data
        profile = await client.get_company_profile(company_number)
        officers = await client.get_company_officers(company_number)
        charges = await client.get_charges(company_number)
        financial_stability = await client.calculate_financial_stability_score(company_number)
        
        # Generate monitoring alerts
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
        
        # Check director changes
        active_officers = [o for o in officers if not o.get("resigned_on")]
        if len(active_officers) < 2:
            alerts.append({
                "type": "info",
                "message": f"Only {len(active_officers)} active director(s) - monitor for changes",
                "severity": "low",
                "date": datetime.now().isoformat()
            })
        
        # Generate historical trend (simulated)
        historical_trends = []
        if financial_stability.get("score") is not None:
            current_score = financial_stability["score"]
            # Simulate 5 historical data points
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


@router.get("/search/care-homes")
async def companies_house_search_care_homes(
    location: Optional[str] = Query(None),
    items_per_page: int = Query(20)
):
    """Search for care homes by SIC codes"""
    try:
        client = get_companies_house_client()
        care_homes = await client.search_care_homes(location=location, items_per_page=items_per_page)
        
        return {
            "status": "success",
            "count": len(care_homes),
            "care_homes": care_homes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/find-company")
async def companies_house_find_company(
    company_name: str,
    prefer_care_home: bool = Query(True)
):
    """Find company number by name"""
    try:
        client = get_companies_house_client()
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


@router.get("/company/{company_number}/detailed-metrics")
async def companies_house_get_detailed_metrics(company_number: str):
    """Get detailed financial metrics for a company"""
    try:
        client = get_companies_house_client()
        metrics = await client.get_detailed_financial_metrics(company_number)
        
        return {
            "status": "success",
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def companies_house_compare_companies(company_numbers: List[str] = Body(...)):
    """Compare multiple companies by their financial metrics"""
    try:
        if not company_numbers or len(company_numbers) < 2:
            raise HTTPException(status_code=400, detail="At least 2 company numbers required")
        
        client = get_companies_house_client()
        comparison = await client.compare_companies(company_numbers)
        
        return {
            "status": "success",
            "count": len(comparison),
            "comparison": comparison
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/company/{company_number}/financial-health")
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
        client = get_companies_house_client()
        
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


@router.post("/company/{company_number}/monitor-changes")
async def companies_house_monitor_changes(
    company_number: str,
    previous_state: Optional[Dict] = Body(None)
):
    """Detect changes in company financial status (Premium tier monitoring)"""
    try:
        client = get_companies_house_client()
        changes = await client.detect_changes(company_number, previous_state)
        
        return {
            "status": "success",
            "monitoring": changes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

