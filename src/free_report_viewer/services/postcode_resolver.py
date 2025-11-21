"""
Postcode Resolver Service
Resolves postcode to local_authority and region
"""
import httpx
from typing import Dict, Optional
import os


class PostcodeResolver:
    """Resolve postcode to local authority and region"""
    
    def __init__(self):
        self.base_url = "https://api.postcodes.io"
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def resolve(self, postcode: str) -> Dict[str, str]:
        """
        Resolve postcode to local_authority and region
        
        Args:
            postcode: UK postcode
            
        Returns:
            Dict with 'local_authority' and 'region'
        """
        try:
            # Normalize postcode
            postcode_clean = postcode.upper().strip().replace(" ", "")
            
            # Try postcodes.io API
            response = await self.client.get(
                f"{self.base_url}/postcodes/{postcode_clean}"
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == 200 and data.get("result"):
                    result = data["result"]
                    return {
                        "local_authority": result.get("admin_district") or result.get("admin_county", "Unknown"),
                        "region": result.get("region") or result.get("country", "Unknown"),
                        "postcode": result.get("postcode", postcode),
                        "latitude": result.get("latitude"),
                        "longitude": result.get("longitude")
                    }
        except Exception as e:
            print(f"Postcode API error: {e}")
        
        # Fallback to pattern matching
        return self._fallback_resolve(postcode)
    
    def _fallback_resolve(self, postcode: str) -> Dict[str, str]:
        """Fallback resolution using postcode patterns"""
        postcode_upper = postcode.upper().strip()
        
        # London postcodes
        if postcode_upper.startswith(('SW', 'SE', 'NW', 'NE', 'E', 'W', 'N', 'WC', 'EC')):
            return {
                "local_authority": "Westminster",
                "region": "London",
                "postcode": postcode
            }
        
        # Manchester
        if postcode_upper.startswith('M'):
            return {
                "local_authority": "Manchester",
                "region": "North West",
                "postcode": postcode
            }
        
        # Birmingham
        if postcode_upper.startswith('B'):
            return {
                "local_authority": "Birmingham",
                "region": "West Midlands",
                "postcode": postcode
            }
        
        # Liverpool
        if postcode_upper.startswith('L'):
            return {
                "local_authority": "Liverpool",
                "region": "North West",
                "postcode": postcode
            }
        
        # Leeds
        if postcode_upper.startswith('LS'):
            return {
                "local_authority": "Leeds",
                "region": "Yorkshire and the Humber",
                "postcode": postcode
            }
        
        # Default
        return {
            "local_authority": "Unknown",
            "region": "Unknown",
            "postcode": postcode
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

