"""
Financial Enrichment Routes
Simple endpoint for financial data enrichment (Companies House)
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional

from api_clients.companies_house_client import CompaniesHouseAPIClient
from utils.client_factory import get_companies_house_client

router = APIRouter(prefix="/api/financial", tags=["Financial"])


@router.get("")
@router.get("/")
async def financial_enrichment(
    name: Optional[str] = Query(None),
    postcode: Optional[str] = Query(None),
    cache: Optional[bool] = Query(True)
):
    """
    Simple financial enrichment endpoint for professional report
    Accepts name and postcode, searches Companies House and returns financial data
    """
    try:
        if not name:
            raise HTTPException(status_code=400, detail="Name is required")
        
        # ✅ FIX: Check if Companies House client is available before attempting enrichment
        try:
            client = get_companies_house_client()
        except ValueError as e:
            # API key not configured or is placeholder
            error_msg = str(e)
            if "not configured" in error_msg.lower() or "placeholder" in error_msg.lower():
                return {
                    "status": "not_available",
                    "data": {},
                    "message": "Companies House API is not configured. Please configure API key in API Configuration."
                }
            # Re-raise other ValueErrors
            raise HTTPException(
                status_code=500,
                detail=f"Companies House API configuration error: {error_msg}"
            )
        
        # Search for companies matching the name
        search_query = name
        if "care" not in name.lower() and "home" not in name.lower():
            search_query = f"{name} care home"
        
        try:
            companies = await client.search_companies(search_query, items_per_page=5)
        except Exception as e:
            error_msg = str(e)
            # ✅ FIX: Handle authentication errors gracefully
            if "authentication failed" in error_msg.lower() or "401" in error_msg or "unauthorized" in error_msg.lower():
                return {
                    "status": "not_available",
                    "data": {},
                    "message": "Companies House API authentication failed. Please verify your API key is correct and active."
                }
            # For other errors, return not_found (search failed)
            print(f"Warning: Companies House search failed for '{name}': {e}")
            return {
                "status": "not_found",
                "data": {},
                "message": f"Companies House search failed for '{name}'"
            }
        
        if not companies:
            return {
                "status": "not_found",
                "data": {},
                "message": f"No company found matching '{name}'"
            }
        
        # Get detailed data for first match
        best_match = companies[0]
        company_number = best_match.get("company_number")
        
        if not company_number:
            return {
                "status": "not_found",
                "data": {},
                "message": f"Company number not found for '{name}'"
            }
        
        # Get comprehensive company data
        try:
            profile = await client.get_company_profile(company_number)
            officers = await client.get_company_officers(company_number)
            charges = await client.get_charges(company_number)
            stability_score = await client.calculate_financial_stability_score(company_number)
        except Exception as e:
            error_msg = str(e)
            # ✅ FIX: Handle authentication errors gracefully
            if "authentication failed" in error_msg.lower() or "401" in error_msg or "unauthorized" in error_msg.lower():
                return {
                    "status": "not_available",
                    "data": {},
                    "message": "Companies House API authentication failed. Please verify your API key is correct and active."
                }
            # For other errors, re-raise
            raise
        
        return {
            "status": "success",
            "data": {
                "profile": profile,
                "officers": officers,
                "charges": charges,
                "financial_stability": stability_score,
                "company_number": company_number
            }
        }
    except HTTPException:
        raise
    except ValueError as e:
        # ✅ FIX: Handle ValueError from get_companies_house_client gracefully
        error_msg = str(e)
        if "not configured" in error_msg.lower() or "placeholder" in error_msg.lower():
            return {
                "status": "not_available",
                "data": {},
                "message": "Companies House API is not configured. Please configure API key in API Configuration."
            }
        raise HTTPException(status_code=500, detail=f"Companies House API configuration error: {error_msg}")
    except Exception as e:
        error_msg = str(e)
        if "authentication failed" in error_msg.lower() or "401" in error_msg or "unauthorized" in error_msg.lower():
            return {
                "status": "not_available",
                "data": {},
                "message": "Companies House API authentication failed. Please verify your API key is correct and active."
            }
        raise HTTPException(status_code=500, detail=f"Financial enrichment error: {error_msg}")

