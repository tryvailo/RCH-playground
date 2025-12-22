"""
Test Runner Service
Orchestrates comprehensive API testing
"""
from typing import Dict, List, Optional, Callable
from models.schemas import ApiCredentials, HomeData
from api_clients.cqc_client import CQCAPIClient
from api_clients.fsa_client import FSAAPIClient
from api_clients.companies_house_client import CompaniesHouseAPIClient
from api_clients.google_places_client import GooglePlacesAPIClient
from api_clients.perplexity_client import PerplexityAPIClient
import asyncio


class TestRunner:
    """Test Runner for comprehensive API testing"""
    
    def __init__(self, credentials: Optional[ApiCredentials] = None):
        self.credentials = credentials
        self.clients = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize API clients based on credentials"""
        # CQC (uses subscription keys for new API)
        if self.credentials and self.credentials.cqc:
            self.clients["cqc"] = CQCAPIClient(
                partner_code=self.credentials.cqc.partner_code,
                primary_subscription_key=self.credentials.cqc.primary_subscription_key,
                secondary_subscription_key=self.credentials.cqc.secondary_subscription_key
            )
        else:
            # CQC can work without credentials (legacy mode)
            self.clients["cqc"] = CQCAPIClient(partner_code=None)
        
        # FSA (no credentials needed)
        self.clients["fsa"] = FSAAPIClient()
        
        # Companies House
        if self.credentials and self.credentials.companies_house:
            self.clients["companies_house"] = CompaniesHouseAPIClient(
                api_key=self.credentials.companies_house.api_key
            )
        
        # Google Places
        if self.credentials and self.credentials.google_places:
            self.clients["google_places"] = GooglePlacesAPIClient(
                api_key=self.credentials.google_places.api_key
            )
        
        # Perplexity
        if self.credentials and self.credentials.perplexity:
            self.clients["perplexity"] = PerplexityAPIClient(
                api_key=self.credentials.perplexity.api_key
            )
        
    
    async def run_comprehensive_test(
        self,
        home_data: HomeData,
        apis_to_test: List[str],
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Dict[str, Dict]:
        """Run comprehensive test across selected APIs"""
        results = {}
        total_apis = len(apis_to_test)
        
        # Phase 1: Official APIs (free, fast)
        if "cqc" in apis_to_test and "cqc" in self.clients:
            if progress_callback:
                progress_callback("cqc", int(10 / total_apis * 100))
            results["cqc"] = await self._test_cqc(home_data)
        
        if "fsa" in apis_to_test and "fsa" in self.clients:
            if progress_callback:
                progress_callback("fsa", int(20 / total_apis * 100))
            results["fsa"] = await self._test_fsa(home_data, results.get("cqc"))
        
        if "companies_house" in apis_to_test and "companies_house" in self.clients:
            if progress_callback:
                progress_callback("companies_house", int(30 / total_apis * 100))
            results["companies_house"] = await self._test_companies_house(
                results.get("cqc")
            )
        
        # Phase 2: Paid APIs (with cost warnings)
        if "google_places" in apis_to_test and "google_places" in self.clients:
            if progress_callback:
                progress_callback("google_places", int(50 / total_apis * 100))
            results["google_places"] = await self._test_google_places(home_data)
        
        if "perplexity" in apis_to_test and "perplexity" in self.clients:
            if progress_callback:
                progress_callback("perplexity", int(65 / total_apis * 100))
            results["perplexity"] = await self._test_perplexity(home_data)
        
        if progress_callback:
            progress_callback("complete", 100)
        
        return results
    
    async def _test_cqc(self, home_data: HomeData) -> Dict:
        """Test CQC API"""
        try:
            if "cqc" not in self.clients:
                return {
                    "status": "failure",
                    "error": "CQC client not initialized. Check credentials.",
                    "cost_incurred": 0.0
                }
            client = self.clients["cqc"]
            homes = await client.search_care_homes(
                region="South East",
                per_page=10
            )
            
            # Find matching home
            matching_home = None
            if home_data.name:
                for home in homes:
                    if home_data.name.lower() in home.get("name", "").lower():
                        matching_home = home
                        break
            
            return {
                "status": "success",
                "data_returned": len(homes) > 0,
                "homes_found": len(homes),
                "matching_home": matching_home,
                "cost_incurred": 0.0
            }
        except Exception as e:
            return {
                "status": "failure",
                "error": str(e),
                "cost_incurred": 0.0
            }
    
    async def _test_fsa(self, home_data: HomeData, cqc_result: Optional[Dict] = None) -> Dict:
        """Test FSA API"""
        try:
            client = self.clients["fsa"]
            
            if home_data.latitude and home_data.longitude:
                results = await client.search_by_location(
                    latitude=home_data.latitude,
                    longitude=home_data.longitude,
                    max_distance=1.0
                )
            elif home_data.name:
                results = await client.search_by_business_name(home_data.name)
            else:
                return {
                    "status": "failure",
                    "error": "No location or name provided",
                    "cost_incurred": 0.0
                }
            
            return {
                "status": "success",
                "data_returned": len(results) > 0,
                "establishments_found": len(results),
                "sample": results[:3] if results else [],
                "cost_incurred": 0.0
            }
        except Exception as e:
            return {
                "status": "failure",
                "error": str(e),
                "cost_incurred": 0.0
            }
    
    async def _test_companies_house(self, cqc_result: Optional[Dict] = None) -> Dict:
        """Test Companies House API"""
        try:
            if "companies_house" not in self.clients:
                return {
                    "status": "failure",
                    "error": "Companies House client not initialized. Check credentials.",
                    "cost_incurred": 0.0
                }
            client = self.clients["companies_house"]
            
            # Try to extract provider name from CQC result
            provider_name = None
            if cqc_result and cqc_result.get("matching_home"):
                provider_name = cqc_result["matching_home"].get("provider", {}).get("name")
            
            if not provider_name:
                provider_name = "HC-One"  # Default test
            
            companies = await client.search_companies(provider_name, items_per_page=5)
            
            return {
                "status": "success",
                "data_returned": len(companies) > 0,
                "companies_found": len(companies),
                "sample": companies[:2] if companies else [],
                "cost_incurred": 0.0
            }
        except Exception as e:
            return {
                "status": "failure",
                "error": str(e),
                "cost_incurred": 0.0
            }
    
    async def _test_google_places(self, home_data: HomeData) -> Dict:
        """Test Google Places API"""
        try:
            if "google_places" not in self.clients:
                return {
                    "status": "failure",
                    "error": "Google Places client not initialized. Check credentials.",
                    "cost_incurred": 0.0
                }
            client = self.clients["google_places"]
            query = f"{home_data.name} {home_data.city}" if home_data.name else home_data.city or ""
            
            place = await client.find_place(query)
            cost = 0.017 if place else 0.032
            
            if place:
                details = await client.get_place_details(place["place_id"])
                cost += 0.017
                
                return {
                    "status": "success",
                    "data_returned": True,
                    "place": place,
                    "details": details,
                    "cost_incurred": cost
                }
            
            return {
                "status": "partial",
                "data_returned": False,
                "cost_incurred": cost
            }
        except Exception as e:
            return {
                "status": "failure",
                "error": str(e),
                "cost_incurred": 0.0
            }
    
    async def _test_perplexity(self, home_data: HomeData) -> Dict:
        """Test Perplexity API"""
        try:
            if "perplexity" not in self.clients:
                return {
                    "status": "failure",
                    "error": "Perplexity client not initialized. Check credentials.",
                    "cost_incurred": 0.0
                }
            client = self.clients["perplexity"]
            query = f"Recent news about {home_data.name} in {home_data.city}" if home_data.name else "Care homes UK"
            
            result = await client.search(query, model="sonar-pro")
            
            return {
                "status": "success",
                "data_returned": True,
                "summary": result.get("content", ""),
                "citations": result.get("citations", []),
                "cost_incurred": 0.005
            }
        except Exception as e:
            return {
                "status": "failure",
                "error": str(e),
                "cost_incurred": 0.0
            }
    
    async def cleanup(self):
        """Cleanup all clients"""
        for client in self.clients.values():
            if hasattr(client, "close"):
                await client.close()

