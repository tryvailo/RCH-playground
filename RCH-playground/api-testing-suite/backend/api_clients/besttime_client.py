"""
BestTime.app API Client
"""
import httpx
from typing import Dict, Optional


class BestTimeClient:
    """BestTime.app API Client"""
    
    def __init__(self, private_key: str, public_key: str):
        self.private_key = private_key
        self.public_key = public_key
        self.base_url = "https://besttime.app/api/v1"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def create_forecast(self, venue_name: str, venue_address: str) -> Optional[Dict]:
        """Create new forecast for a venue"""
        params = {
            "api_key_private": self.private_key,
            "venue_name": venue_name,
            "venue_address": venue_address
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/forecasts",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "OK":
                return data
            return None
        except Exception as e:
            # BestTime may return errors for venues without data
            return None
    
    async def get_venue_forecast(self, venue_id: str) -> Optional[Dict]:
        """Get existing forecast data"""
        params = {
            "api_key_public": self.public_key
        }
        
        try:
            response = await self.client.get(
                f"{self.base_url}/forecasts/{venue_id}",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None
    
    async def analyze_footfall(self, forecast_data: Dict) -> Dict:
        """Extract key metrics from BestTime response"""
        if not forecast_data or forecast_data.get("status") != "OK":
            return {
                "data_available": False,
                "venue_id": None,
                "activity_score": 0
            }
        
        analysis = forecast_data.get("analysis", {})
        venue_info = forecast_data.get("venue_info", {})
        
        # Calculate activity score
        activity_score = 0
        peak_hours = analysis.get("peak_hours", [])
        hour_analysis = analysis.get("hour_analysis", [])
        
        # Weekend activity (40 points)
        weekend_peaks = [h for h in peak_hours if h.get("day_int", 0) in [5, 6]]
        if weekend_peaks:
            activity_score += 40
        
        # Evening visits (30 points)
        evening_peaks = [h for h in peak_hours if 17 <= h.get("hour", 0) <= 20]
        if evening_peaks:
            activity_score += 30
        
        # Consistency (30 points)
        if hour_analysis:
            intensities = [h.get("intensity_nr", 0) for h in hour_analysis]
            if intensities:
                avg = sum(intensities) / len(intensities)
                variance = sum((x - avg) ** 2 for x in intensities) / len(intensities)
                consistency = max(0, 100 - variance)
                activity_score += consistency * 0.3
        
        return {
            "data_available": True,
            "venue_id": venue_info.get("venue_id"),
            "venue_name": venue_info.get("venue_name"),
            "busy_hours": analysis.get("busy_hours", []),
            "peak_hours": peak_hours,
            "quiet_hours": analysis.get("quiet_hours", []),
            "hour_analysis": hour_analysis,
            "week_analysis": analysis.get("week_analysis", {}),
            "activity_score": min(100, activity_score),
            "has_weekend_activity": len(weekend_peaks) > 0,
            "has_evening_visits": len(evening_peaks) > 0
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

