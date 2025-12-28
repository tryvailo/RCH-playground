"""
CQC API Routes
Handles all CQC (Care Quality Commission) API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from typing import Dict, Any, Optional
from datetime import datetime

from api_clients.cqc_client import CQCAPIClient
from models.schemas import TestRequest, ApiTestResult
from utils.client_factory import get_cqc_client
from utils.auth import credentials_store
from utils.error_handler import handle_api_error

router = APIRouter(prefix="/api/cqc", tags=["CQC"])


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


def handle_cqc_error(e: Exception) -> HTTPException:
    """Handle CQC API errors and return appropriate HTTPException"""
    import traceback
    error_message = str(e)
    error_detail = f"{error_message}\n{traceback.format_exc()}"
    print(f"CQC API error: {error_detail}")
    
    # Provide more helpful error messages
    if "403" in error_message or "Forbidden" in error_message:
        return HTTPException(
            status_code=403,
            detail="CQC API access denied. Please configure CQC subscription keys in API Configuration. Register at https://api-portal.service.cqc.org.uk/"
        )
    elif "401" in error_message or "Unauthorized" in error_message:
        return HTTPException(
            status_code=401,
            detail="CQC API authentication failed. Please check your subscription keys in API Configuration."
        )
    elif "429" in error_message or "rate limit" in error_message.lower():
        return HTTPException(
            status_code=429,
            detail="CQC API rate limit exceeded. Please wait before retrying."
        )
    else:
        return HTTPException(status_code=500, detail=f"CQC API error: {error_message}")


@router.get("/status")
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


@router.get("/locations/search")
async def cqc_search_locations(
    care_home: Optional[str] = Query(None),
    local_authority: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    postcode: Optional[str] = Query(None),
    overall_rating: Optional[str] = Query(None),
    inspection_directorate: Optional[str] = Query(None),
    constituency: Optional[str] = Query(None),
    onspd_ccg_code: Optional[str] = Query(None),
    onspd_ccg_name: Optional[str] = Query(None),
    ods_ccg_code: Optional[str] = Query(None),
    ods_ccg_name: Optional[str] = Query(None),
    gac_service_type_description: Optional[str] = Query(None),
    primary_inspection_category_code: Optional[str] = Query(None),
    primary_inspection_category_name: Optional[str] = Query(None),
    non_primary_inspection_category_code: Optional[str] = Query(None),
    non_primary_inspection_category_name: Optional[str] = Query(None),
    regulated_activity: Optional[str] = Query(None),
    report_type: Optional[str] = Query(None),
    page_size: int = Query(100)
):
    """Enhanced CQC location search with advanced filtering"""
    try:
        client = get_cqc_client()
        
        # Convert care_home string to boolean
        care_home_bool = None
        if care_home is not None:
            if isinstance(care_home, bool):
                care_home_bool = care_home
            elif isinstance(care_home, str):
                care_home_bool = care_home.lower() == 'true'
        
        # Limit to max 10 pages (5000 results) to prevent timeout/hanging
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
        raise handle_cqc_error(e)


@router.get("/locations/{location_id}")
async def cqc_get_location(location_id: str):
    """Get detailed information for a CQC location"""
    try:
        client = get_cqc_client()
        location = await client.get_location(location_id)
        
        return {
            "status": "success",
            "location": location
        }
    except HTTPException:
        raise
    except Exception as e:
        raise handle_cqc_error(e)


@router.get("/locations/{location_id}/inspection-areas")
async def cqc_get_location_inspection_areas(location_id: str):
    """Get inspection areas for a CQC location"""
    try:
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


@router.get("/locations/{location_id}/reports")
async def cqc_get_location_reports(location_id: str):
    """Get reports metadata for a CQC location"""
    try:
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


@router.get("/reports/{report_id}")
async def cqc_get_report(report_id: str, plain_text: bool = Query(True)):
    """Get an inspection report (plain text or PDF)"""
    try:
        client = get_cqc_client()
        report = await client.get_report(report_id, plain_text=plain_text)
        
        if plain_text:
            return {
                "status": "success",
                "format": "plain_text",
                "content": report
            }
        else:
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


@router.get("/providers/search")
async def cqc_search_providers(
    local_authority: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    overall_rating: Optional[str] = Query(None),
    inspection_directorate: Optional[str] = Query(None),
    page_size: int = Query(100)
):
    """Search for CQC providers"""
    try:
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
        raise handle_cqc_error(e)


@router.get("/providers/{provider_id}")
async def cqc_get_provider(provider_id: str):
    """Get detailed information for a CQC provider"""
    try:
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


@router.get("/providers/{provider_id}/locations")
async def cqc_get_provider_locations(provider_id: str):
    """Get all locations for a CQC provider"""
    try:
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


@router.get("/inspection-areas")
async def cqc_get_inspection_areas():
    """Get all CQC inspection areas"""
    try:
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


@router.get("")
@router.get("/")
async def cqc_enrichment(
    name: Optional[str] = Query(None),
    postcode: Optional[str] = Query(None),
    location_id: Optional[str] = Query(None),
    cache: Optional[bool] = Query(True)
):
    """
    Simple CQC enrichment endpoint for professional report
    Accepts name, postcode, or location_id and returns enriched CQC data
    """
    try:
        # ✅ FIX: Check if CQC client is available before attempting enrichment
        try:
            client = get_cqc_client()
        except ValueError as e:
            # API key not configured or is placeholder
            error_msg = str(e)
            if "not configured" in error_msg.lower() or "placeholder" in error_msg.lower():
                return {
                    "status": "not_available",
                    "data": {},
                    "message": "CQC API is not configured. Please configure CQC subscription keys in API Configuration."
                }
            raise
        
        # If location_id is provided, use it directly (most efficient)
        if location_id:
            try:
                location = await client.get_location(location_id)
                if location:
                    return {
                        "status": "success",
                        "data": location
                    }
            except Exception as e:
                # ✅ FIX: If location_id lookup fails with 404, return not_found immediately
                # Don't fall through to search - it's too slow and may timeout
                error_msg = str(e)
                # Check for 404 in various formats: "404", "CQC API error: 404", "No Locations found"
                if ("404" in error_msg or 
                    "not found" in error_msg.lower() or 
                    "No Locations found" in error_msg or
                    "No Locations found on the given Location ID" in error_msg):
                    return {
                        "status": "not_found",
                        "data": {},
                        "message": f"CQC location not found for location_id: {location_id}"
                    }
                # For other errors (like 401, 403, 500), return not_available
                if "401" in error_msg or "403" in error_msg or "Unauthorized" in error_msg or "Forbidden" in error_msg:
                    return {
                        "status": "not_available",
                        "data": {},
                        "message": "CQC API authentication failed. Please check your subscription keys."
                    }
                # For other errors, log and fall through to search by name (if available)
                print(f"Warning: CQC location lookup failed for location_id {location_id}: {e}")
        
        # Otherwise, search by name and postcode
        if name:
            # ✅ FIX: Use more efficient search - limit results to avoid timeout
            # Note: CQC API doesn't support postcode filtering, so we filter in memory
            try:
                # Search with limited results for better performance
                locations = await client.search_locations(
                    care_home=True,
                    page_size=20,  # Reduced from 50 for better performance
                    verbose=False,
                    max_pages=1  # Only first page to avoid timeout
                )
            except Exception as e:
                # ✅ FIX: Return graceful error instead of empty list
                error_msg = str(e)
                if "403" in error_msg or "Forbidden" in error_msg:
                    return {
                        "status": "not_available",
                        "data": {},
                        "message": "CQC API access denied. Please configure CQC subscription keys."
                    }
                elif "401" in error_msg or "Unauthorized" in error_msg:
                    return {
                        "status": "not_available",
                        "data": {},
                        "message": "CQC API authentication failed. Please check your subscription keys."
                    }
                # For other errors, return not_found (search failed, not necessarily no results)
                print(f"Warning: CQC search failed: {e}")
                return {
                    "status": "not_found",
                    "data": {},
                    "message": f"CQC search failed. Please try with location_id if available."
                }
            
            # Filter by name if we got results
            matching_locations = []
            if locations:
                name_lower = name.lower()
                postcode_normalized = postcode.replace(" ", "").upper() if postcode else None
                
                for loc in locations:
                    loc_name = loc.get("name", "").lower()
                    loc_postcode = loc.get("postalCode", "").replace(" ", "").upper() if loc.get("postalCode") else ""
                    
                    # Match by name (partial match)
                    if name_lower in loc_name or loc_name in name_lower:
                        # If postcode provided, also match by postcode
                        if postcode_normalized:
                            if postcode_normalized in loc_postcode or loc_postcode in postcode_normalized:
                                matching_locations.append(loc)
                        else:
                            matching_locations.append(loc)
            
            if matching_locations:
                # Get detailed data for first match
                best_match = matching_locations[0]
                location_id = best_match.get("locationId")
                if location_id:
                    try:
                        location = await client.get_location(location_id)
                        if location:
                            return {
                                "status": "success",
                                "data": location
                            }
                    except Exception as e:
                        print(f"Warning: Failed to get detailed CQC data for location_id {location_id}: {e}")
            
            return {
                "status": "not_found",
                "data": {},
                "message": f"No CQC location found for name: {name}, postcode: {postcode}"
            }
        
        raise HTTPException(
            status_code=400,
            detail="Either location_id or name must be provided"
        )
    except HTTPException:
        raise
    except ValueError as e:
        # ✅ FIX: Handle ValueError from get_cqc_client gracefully
        error_msg = str(e)
        if "not configured" in error_msg.lower() or "placeholder" in error_msg.lower():
            return {
                "status": "not_available",
                "data": {},
                "message": "CQC API is not configured. Please configure CQC subscription keys in API Configuration."
            }
        raise HTTPException(status_code=500, detail=f"CQC API configuration error: {error_msg}")
    except Exception as e:
        # ✅ FIX: Handle all exceptions gracefully - return not_available or not_found instead of 500
        import traceback
        error_msg = str(e)
        error_detail = f"{error_msg}\n{traceback.format_exc()}"
        print(f"CQC enrichment error: {error_detail}")
        
        # Check for specific error types
        if "403" in error_msg or "Forbidden" in error_msg:
            return {
                "status": "not_available",
                "data": {},
                "message": "CQC API access denied. Please configure CQC subscription keys."
            }
        elif "401" in error_msg or "Unauthorized" in error_msg:
            return {
                "status": "not_available",
                "data": {},
                "message": "CQC API authentication failed. Please check your subscription keys."
            }
        elif "404" in error_msg or "not found" in error_msg.lower():
            return {
                "status": "not_found",
                "data": {},
                "message": f"CQC location not found. {error_msg}"
            }
        elif "429" in error_msg or "rate limit" in error_msg.lower():
            return {
                "status": "not_available",
                "data": {},
                "message": "CQC API rate limit exceeded. Please wait before retrying."
            }
        else:
            # For other errors, return not_found (graceful degradation)
            return {
                "status": "not_found",
                "data": {},
                "message": f"CQC enrichment failed: {error_msg}"
            }


@router.get("/changes")
async def cqc_get_changes(
    organisation_type: str = Query("location"),
    start_date: str = Query("2000-01-01"),
    end_date: Optional[str] = Query(None)
):
    """Get changes for providers or locations in a date range"""
    try:
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

