"""
Postcode Resolver Service
Resolves postcode to local_authority and region
Uses RCH-data postcode_resolver module
"""
from typing import Dict, Optional
import asyncio
import os

# Try to import from RCH-data module
try:
    from postcode_resolver import PostcodeResolver as RCHPostcodeResolver
    RCH_DATA_AVAILABLE = True
except ImportError:
    RCH_DATA_AVAILABLE = False
    # Fallback to mock implementation
    import httpx


class PostcodeResolver:
    """Resolve postcode to local authority and region using RCH-data module"""
    
    def __init__(self):
        if RCH_DATA_AVAILABLE:
            # Use RCH-data PostcodeResolver
            self._rch_resolver = RCHPostcodeResolver()
            self.client = None
        else:
            # Fallback to mock implementation
            import httpx
            self.base_url = "https://api.postcodes.io"
            self.client = httpx.AsyncClient(timeout=10.0)
            self._rch_resolver = None
    
    async def resolve(self, postcode: str) -> Dict[str, str]:
        """
        Resolve postcode to local_authority and region
        
        Args:
            postcode: UK postcode
            
        Returns:
            Dict with 'local_authority', 'region', 'postcode', 'latitude', 'longitude'
        """
        if RCH_DATA_AVAILABLE and self._rch_resolver:
            # Use RCH-data module (synchronous, run in executor)
            try:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self._rch_resolver.resolve,
                    postcode
                )
                
                # Convert PostcodeInfo to Dict format
                return {
                    "local_authority": result.local_authority,
                    "region": result.region,
                    "postcode": result.postcode,
                    "latitude": None,  # RCH-data resolver doesn't return coordinates
                    "longitude": None
                }
            except Exception as e:
                # Fallback to mock if RCH-data fails
                print(f"RCH-data postcode resolver error: {e}, falling back to API")
                return await self._resolve_via_api(postcode)
        else:
            # Fallback to API implementation
            return await self._resolve_via_api(postcode)
    
    async def _resolve_via_api(self, postcode: str) -> Dict[str, str]:
        """Fallback API-based resolution"""
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
                "postcode": postcode,
                "latitude": None,
                "longitude": None
            }
        
        # Manchester
        if postcode_upper.startswith('M'):
            return {
                "local_authority": "Manchester",
                "region": "North West",
                "postcode": postcode,
                "latitude": None,
                "longitude": None
            }
        
        # Birmingham
        if postcode_upper.startswith('B'):
            return {
                "local_authority": "Birmingham",
                "region": "West Midlands",
                "postcode": postcode,
                "latitude": None,
                "longitude": None
            }
        
        # Liverpool
        if postcode_upper.startswith('L'):
            return {
                "local_authority": "Liverpool",
                "region": "North West",
                "postcode": postcode,
                "latitude": None,
                "longitude": None
            }
        
        # Leeds
        if postcode_upper.startswith('LS'):
            return {
                "local_authority": "Leeds",
                "region": "Yorkshire and the Humber",
                "postcode": postcode,
                "latitude": None,
                "longitude": None
            }
        
        # Default
        return {
            "local_authority": "Unknown",
            "region": "Unknown",
            "postcode": postcode,
            "latitude": None,
            "longitude": None
        }
    
    async def close(self):
        """Close HTTP client if using fallback"""
        if self.client:
            await self.client.aclose()

