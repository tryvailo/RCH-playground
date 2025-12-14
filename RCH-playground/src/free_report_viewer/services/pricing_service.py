"""
Pricing Service
Gets market average pricing and band for postcode
Uses RCH-data pricing_calculator module
"""
from typing import Dict, Optional
import asyncio
import os

# Try to import from RCH-data module
try:
    from pricing_calculator import PricingService as RCHPricingService, CareType
    RCH_DATA_AVAILABLE = True
except ImportError:
    RCH_DATA_AVAILABLE = False
    # Fallback to mock implementation
    import httpx


class PricingService:
    """Service for getting pricing data using RCH-data module"""
    
    def __init__(self):
        if RCH_DATA_AVAILABLE:
            # Use RCH-data PricingService
            self._rch_service = RCHPricingService()
            self.client = None
        else:
            # Fallback to mock implementation
            import httpx
            self.client = httpx.AsyncClient(timeout=10.0)
            self._rch_service = None
    
    async def get_pricing_for_postcode(
        self,
        postcode: str,
        care_type: str
    ) -> Dict[str, float]:
        """
        Get market average pricing and band for postcode
        
        Args:
            postcode: UK postcode
            care_type: 'residential', 'nursing', 'dementia', 'respite', 
                      'residential_dementia', or 'nursing_dementia'
            
        Returns:
            Dict with 'market_avg' (weekly GBP) and 'band' (1-5)
        """
        if RCH_DATA_AVAILABLE and self._rch_service:
            # Use RCH-data module (synchronous, run in executor)
            try:
                # Map care_type string to CareType enum
                care_type_map = {
                    "residential": CareType.RESIDENTIAL,
                    "nursing": CareType.NURSING,
                    "dementia": CareType.RESIDENTIAL_DEMENTIA,  # Default dementia type
                    "respite": CareType.RESPITE,
                    "residential_dementia": CareType.RESIDENTIAL_DEMENTIA,
                    "nursing_dementia": CareType.NURSING_DEMENTIA,
                }
                
                rch_care_type = care_type_map.get(care_type.lower(), CareType.RESIDENTIAL)
                
                # Run synchronous call in executor
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self._rch_service.get_pricing_for_postcode,
                    postcode,
                    rch_care_type
                )
                
                # Convert PricingResult to Dict format
                # Map affordability_band (A-E) to numeric band (1-5)
                band_map = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}
                band = band_map.get(result.affordability_band, 3)
                
                return {
                    "market_avg": round(result.private_average_gbp, 2),
                    "band": band
                }
            except Exception as e:
                # Fallback to mock if RCH-data fails
                print(f"RCH-data pricing service error: {e}, falling back to mock")
                return self._get_mock_pricing(postcode, care_type)
        else:
            # Fallback to mock implementation
            return self._get_mock_pricing(postcode, care_type)
    
    def _get_mock_pricing(self, postcode: str, care_type: str) -> Dict[str, float]:
        """Fallback mock pricing implementation"""
        # Mock pricing bands (weekly GBP)
        base_prices = {
            "residential": 800.0,
            "nursing": 1100.0,
            "dementia": 1200.0,
            "respite": 900.0,
            "residential_dementia": 1200.0,
            "nursing_dementia": 1400.0,
        }
        
        # Adjust by postcode area (London = higher)
        postcode_upper = postcode.upper().strip()
        multiplier = 1.0
        
        if postcode_upper.startswith(('SW', 'SE', 'NW', 'NE', 'E', 'W', 'N', 'WC', 'EC')):
            multiplier = 1.5  # London premium
        elif postcode_upper.startswith(('M', 'B', 'L')):
            multiplier = 1.2  # Major cities
        
        market_avg = base_prices.get(care_type.lower(), 900.0) * multiplier
        
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
        """Close HTTP client if using fallback"""
        if self.client:
            await self.client.aclose()

