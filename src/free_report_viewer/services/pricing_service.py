"""
Pricing Service
Gets market average pricing and band for postcode
"""
from typing import Dict, Optional
import httpx
import os


class PricingService:
    """Service for getting pricing data"""
    
    def __init__(self):
        # In production, this would connect to Lottie API or pricing database
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def get_pricing_for_postcode(
        self,
        postcode: str,
        care_type: str
    ) -> Dict[str, float]:
        """
        Get market average pricing and band for postcode
        
        Args:
            postcode: UK postcode
            care_type: 'residential', 'nursing', or 'dementia'
            
        Returns:
            Dict with 'market_avg' (weekly GBP) and 'band' (1-5)
        """
        # TODO: In production, integrate with Lottie API or pricing database
        # For now, return mock data based on postcode and care_type
        
        # Mock pricing bands (weekly GBP)
        base_prices = {
            "residential": 800.0,
            "nursing": 1100.0,
            "dementia": 1200.0,
            "respite": 900.0
        }
        
        # Adjust by postcode area (London = higher)
        postcode_upper = postcode.upper().strip()
        multiplier = 1.0
        
        if postcode_upper.startswith(('SW', 'SE', 'NW', 'NE', 'E', 'W', 'N', 'WC', 'EC')):
            multiplier = 1.5  # London premium
        elif postcode_upper.startswith(('M', 'B', 'L')):
            multiplier = 1.2  # Major cities
        
        market_avg = base_prices.get(care_type, 900.0) * multiplier
        
        # Determine band (1 = cheapest, 5 = most expensive)
        if market_avg < 700:
            band = 1
        elif market_avg < 900:
            band = 2
        elif market_avg < 1200:
            band = 3
        elif market_avg < 1500:
            band = 4
        else:
            band = 5
        
        return {
            "market_avg": round(market_avg, 2),
            "band": band
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

