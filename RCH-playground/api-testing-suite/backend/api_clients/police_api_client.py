"""
Police API Client
UK Police Data API integration for crime statistics

FREE API: https://data.police.uk/api/
No authentication required
Rate limit: Reasonable use (not specified, but be respectful)
"""
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PoliceAPIClient:
    """Client for UK Police Data API"""
    
    BASE_URL = "https://data.police.uk/api"
    
    def __init__(self):
        """Initialize Police API client"""
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def get_crimes_nearby(
        self,
        lat: float,
        lon: float,
        radius_m: int = 1609,  # 1 mile in meters (API uses 1 mile radius)
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get crimes within 1 mile radius of location
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_m: Radius in meters (API uses 1 mile, but we accept meters for consistency)
            date: Optional date in YYYY-MM format (defaults to last month)
            
        Returns:
            Dict with crime statistics and breakdown
        """
        # API uses 1 mile radius, so we'll use that
        # If radius_m is specified, we'll note it but API only supports 1 mile
        
        # Default to last month if not specified
        if not date:
            last_month = datetime.now() - timedelta(days=30)
            date = last_month.strftime("%Y-%m")
        
        try:
            # API endpoint: /crimes-street/all-crime
            url = f"{self.BASE_URL}/crimes-street/all-crime"
            params = {
                "lat": lat,
                "lng": lon,
                "date": date
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            crimes = response.json()
            
            # Analyze crimes
            crime_stats = self._analyze_crimes(crimes, lat, lon)
            
            return {
                "location": {"lat": lat, "lon": lon},
                "date": date,
                "radius_m": 1609,  # API uses 1 mile
                "total_crimes": len(crimes),
                "crimes": crimes,
                "statistics": crime_stats,
                "data_source": "UK Police Data API",
                "data_quality": "official" if crimes else "no_data"
            }
        except httpx.HTTPStatusError as e:
            logger.warning(f"Police API HTTP error: {e.response.status_code} - {e.response.text}")
            return self._get_fallback_response(lat, lon, date)
        except Exception as e:
            logger.warning(f"Police API error: {str(e)}")
            return self._get_fallback_response(lat, lon, date)
    
    def _analyze_crimes(self, crimes: List[Dict], lat: float, lon: float) -> Dict[str, Any]:
        """Analyze crime data and calculate statistics"""
        if not crimes:
            return {
                "total_crimes": 0,
                "crime_rate_per_1000": 0,
                "crime_level": "Very Low",
                "crime_categories": {},
                "most_common_category": None,
                "safety_score": 100  # No crimes = safest
            }
        
        # Count by category
        categories = {}
        for crime in crimes:
            category = crime.get("category", "Unknown")
            categories[category] = categories.get(category, 0) + 1
        
        # Calculate crime rate (per 1000 population estimate)
        # Using rough estimate: 1 mile radius ≈ 2.6 km² ≈ 5000-10000 people (urban)
        # We'll use 7500 as average
        estimated_population = 7500
        crime_rate = (len(crimes) / estimated_population) * 1000
        
        # Determine crime level
        if crime_rate < 10:
            crime_level = "Very Low"
            safety_score = 90
        elif crime_rate < 30:
            crime_level = "Low"
            safety_score = 75
        elif crime_rate < 60:
            crime_level = "Moderate"
            safety_score = 60
        elif crime_rate < 100:
            crime_level = "High"
            safety_score = 40
        else:
            crime_level = "Very High"
            safety_score = 20
        
        # Find most common category
        most_common = max(categories.items(), key=lambda x: x[1])[0] if categories else None
        
        return {
            "total_crimes": len(crimes),
            "crime_rate_per_1000": round(crime_rate, 1),
            "crime_level": crime_level,
            "crime_categories": categories,
            "most_common_category": most_common,
            "safety_score": safety_score,
            "estimated_population": estimated_population
        }
    
    def _get_fallback_response(self, lat: float, lon: float, date: Optional[str]) -> Dict[str, Any]:
        """Return fallback response when API is unavailable"""
        return {
            "location": {"lat": lat, "lon": lon},
            "date": date or datetime.now().strftime("%Y-%m"),
            "radius_m": 1609,
            "total_crimes": None,
            "crimes": [],
            "statistics": {
                "total_crimes": None,
                "crime_rate_per_1000": None,
                "crime_level": "Unknown",
                "crime_categories": {},
                "most_common_category": None,
                "safety_score": None
            },
            "data_source": "UK Police Data API (unavailable)",
            "data_quality": "unavailable"
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

