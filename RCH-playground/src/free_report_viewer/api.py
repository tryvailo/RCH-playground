"""
API Client for Free Report Viewer
"""
import httpx
from typing import Optional
from .models import QuestionnaireResponse, FreeReportResponse


class FreeReportAPIClient:
    """Client for Free Report API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.endpoint = f"{self.base_url}/api/free-report"
    
    def generate_report(
        self, 
        questionnaire: QuestionnaireResponse,
        timeout: float = 30.0
    ) -> FreeReportResponse:
        """
        Generate free report from questionnaire
        
        Args:
            questionnaire: QuestionnaireResponse object
            timeout: Request timeout in seconds
            
        Returns:
            FreeReportResponse object
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        with httpx.Client(timeout=timeout) as client:
            response = client.post(
                self.endpoint,
                json=questionnaire.dict(exclude_none=True)
            )
            response.raise_for_status()
            return FreeReportResponse(**response.json())

