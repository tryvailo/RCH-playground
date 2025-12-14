"""
Health check endpoint for funding calculator
"""
from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(prefix="/api/rch-data", tags=["health"])

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "rch-data-api"
    }

@router.get("/funding/health")
async def funding_health_check() -> Dict[str, Any]:
    """Health check for funding calculator"""
    try:
        # Try to import funding calculator
        import sys
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent.parent.parent.parent
        rch_data_src_path = project_root / "RCH-data" / "src"
        if str(rch_data_src_path) not in sys.path:
            sys.path.insert(0, str(rch_data_src_path))
        
        try:
            from funding_calculator import FundingEligibilityCalculator
            calculator = FundingEligibilityCalculator()
            return {
                "status": "healthy",
                "funding_calculator": "available",
                "module_loaded": True
            }
        except ImportError as e:
            return {
                "status": "degraded",
                "funding_calculator": "not_available",
                "error": str(e),
                "module_loaded": False
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

