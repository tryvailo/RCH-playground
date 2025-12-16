"""
Staff Quality Routes
Handles staff quality analysis endpoints based on CQC ratings, employee reviews, and sentiment analysis
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime

from utils.client_factory import get_cqc_client
from services.staff_quality_service import StaffQualityService
from utils.error_handler import handle_api_error

router = APIRouter(prefix="/api/staff-quality", tags=["Staff Quality"])


class CareHomeRequest(BaseModel):
    """Request model for staff quality analysis"""
    name: Optional[str] = None
    location_id: Optional[str] = None
    postcode: Optional[str] = None
    address: Optional[str] = None


class StaffQualityAnalyzeResponse(BaseModel):
    """Response model for staff quality analysis"""
    care_home: Dict[str, Any]
    cqc_data: Dict[str, Any]
    reviews: List[Dict[str, Any]]
    staff_quality_score: Dict[str, Any]
    carehome_co_uk: Optional[Dict[str, Any]] = None
    indeed: Optional[Dict[str, Any]] = None
    perplexity_research: Optional[Dict[str, Any]] = None
    key_findings_summary: Optional[Dict[str, Any]] = None
    # Enhanced signals for improved accuracy
    enforcement_signals: Optional[Dict[str, Any]] = None  # CQC enforcement actions
    company_signals: Optional[Dict[str, Any]] = None  # Companies House director/financial data


@router.post("/analyze", response_model=StaffQualityAnalyzeResponse)
async def analyze_staff_quality(request: CareHomeRequest = Body(...)):
    """
    Analyze staff quality for a care home based on CQC ratings, employee reviews, and sentiment analysis.
    
    Algorithm based on staff-quality.md specification:
    - CQC Well-Led rating (40-45% weight)
    - CQC Effective rating (20-25% weight)
    - CQC Staff Sentiment from reports (10-30% weight)
    - Employee Reviews Sentiment (30% weight, or 0% if insufficient data)
    
    Returns overall score 0-100 with category (EXCELLENT/GOOD/ADEQUATE/CONCERNING/POOR)
    """
    try:
        service = StaffQualityService()
        
        # If location_id is provided, try CQC first, fallback to CareHome.co.uk
        if request.location_id:
            try:
                analysis = await service.analyze_by_location_id(request.location_id)
            except (ValueError, Exception) as e:
                # CQC failed - fallback to CareHome.co.uk if name is provided
                if request.name:
                    try:
                        print(f"CQC failed for {request.location_id}, falling back to CareHome.co.uk for {request.name}")
                        analysis = await service.analyze_carehome_reviews(
                            name=request.name,
                            postcode=request.postcode
                        )
                    except Exception as fallback_error:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Care home not found in CQC ({str(e)}) or CareHome.co.uk ({str(fallback_error)})"
                        )
                else:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Care home not found: {str(e)}"
                    )
        elif request.name or request.postcode:
            # Use CareHome.co.uk directly (faster than CQC search)
            # CQC search is slow and often times out
            try:
                analysis = await service.analyze_carehome_reviews(
                    name=request.name,
                    postcode=request.postcode
                )
            except ValueError as e:
                raise HTTPException(
                    status_code=404,
                    detail=f"Care home not found on CareHome.co.uk: {str(e)}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error analyzing care home: {str(e)}"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Either location_id, name, or postcode must be provided"
            )
        
        # Validate that we have at least some data
        if not analysis:
            raise HTTPException(
                status_code=500,
                detail="Analysis returned no data"
            )
        
        if not analysis.get('care_home'):
            raise HTTPException(
                status_code=500,
                detail="Analysis completed but no care home data was returned"
            )
        
        # Validate required fields in response
        try:
            response = StaffQualityAnalyzeResponse(**analysis)
            return response
        except Exception as e:
            print(f"Error validating response: {e}")
            print(f"Analysis data keys: {analysis.keys() if isinstance(analysis, dict) else 'Not a dict'}")
            raise HTTPException(
                status_code=500,
                detail=f"Error validating response data: {str(e)}"
            )
        
    except HTTPException:
        raise
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Staff Quality Analysis Error: {str(e)}")
        print(f"Traceback: {error_trace}")
        
        # Try to get more detailed error info
        try:
            error_detail = handle_api_error(e, "Staff Quality", "analyze", {"request": request.dict()})
            error_message = error_detail.get('error_message', str(e))
        except:
            error_message = str(e)
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze staff quality: {error_message}"
        )


@router.get("/health")
async def staff_quality_health():
    """Health check for staff quality service"""
    return {
        "status": "ok",
        "service": "staff-quality",
        "timestamp": datetime.now().isoformat()
    }

