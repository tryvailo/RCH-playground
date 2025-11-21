"""
FSA Enrichment Service
Enriches care homes with FSA FHRS (Food Hygiene Rating Scheme) data
"""
import asyncio
from typing import List, Dict, Optional, Any
from api_clients.fsa_client import FSAAPIClient
from utils.cache import get_cache_manager


class FSAEnrichmentService:
    """Service to enrich care homes with FSA FHRS data"""
    
    def __init__(self, use_cache: bool = True, cache_ttl: int = 604800):
        """
        Initialize FSA Enrichment Service
        
        Args:
            use_cache: Whether to use Redis cache
            cache_ttl: Cache TTL in seconds (default 7 days for FSA)
        """
        self.fsa_client = FSAAPIClient()
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        self.cache = get_cache_manager() if use_cache else None
    
    def _get_cache_key(self, home_name: str, postcode: str) -> str:
        """Generate cache key for FSA data"""
        if self.cache:
            return self.cache._generate_cache_key("fsa_enrichment", home_name, postcode)
        return f"fsa:{home_name}:{postcode}"
    
    def _score_to_label(self, score: Optional[int]) -> Optional[str]:
        """Convert numeric score to label (for FSA sub-scores)"""
        if score is None:
            return None
        try:
            # Ensure score is an integer
            score_int = int(score)
            # FSA scores are penalty points (lower is better)
            if score_int <= 5:
                return "Excellent"
            elif score_int <= 10:
                return "Good"
            elif score_int <= 15:
                return "Satisfactory"
            elif score_int <= 20:
                return "Needs Improvement"
            else:
                return "Needs Significant Improvement"
        except (ValueError, TypeError):
            return None
    
    def _rating_to_color(self, rating_value: Optional[Any]) -> Optional[str]:
        """
        Convert FSA rating to color (green/yellow/red)
        
        FSA Ratings:
        - 5: Pass (Green)
        - 4: Pass (Green)
        - 3: Pass (Yellow)
        - 2: Improvement Required (Yellow)
        - 1: Improvement Required (Red)
        - 0: Awaiting Inspection (Yellow)
        """
        if rating_value is None:
            return None
        
        try:
            # Handle both string and int ratings
            if isinstance(rating_value, str):
                rating_value = rating_value.strip()
                if rating_value == "Exempt":
                    return "green"  # Exempt establishments are considered safe
                try:
                    rating_int = int(rating_value)
                except ValueError:
                    return None
            else:
                try:
                    rating_int = int(rating_value)
                except (ValueError, TypeError):
                    return None
            
            # rating_int is guaranteed to be an int at this point (or we would have returned None)
            if rating_int >= 4:
                return "green"
            elif rating_int >= 3:
                return "yellow"
            elif rating_int >= 1:
                return "red"
            else:
                return "yellow"  # Awaiting inspection
        except (ValueError, TypeError):
            return None
    
    async def _fetch_fsa_data_for_home(
        self,
        home_name: str,
        postcode: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch FSA data for a single care home
        
        Args:
            home_name: Name of the care home
            postcode: Postcode of the care home
            latitude: Latitude coordinate
            longitude: Longitude coordinate
        
        Returns:
            FSA data dict or None if not found
        """
        cache_key = self._get_cache_key(home_name, postcode or "")
        
        # Check cache first
        if self.use_cache and self.cache:
            cached_data = await self.cache.get(cache_key)
            if cached_data is not None:
                print(f"✅ FSA cache hit for {home_name}")
                return cached_data
        
        try:
            # Try searching by name first
            establishments = await self.fsa_client.search_by_business_name(
                name=home_name,
                local_authority_id=None
            )
            
            # Filter by postcode if available
            if postcode and establishments:
                postcode_prefix = postcode.split()[0] if postcode else None
                establishments = [
                    e for e in establishments
                    if postcode_prefix and postcode_prefix in e.get("PostCode", "")
                ]
            
            # If no results by name, try by location
            if not establishments and latitude and longitude:
                establishments = await self.fsa_client.search_by_location(
                    latitude=latitude,
                    longitude=longitude,
                    max_distance=0.5  # 0.5 km radius
                )
            
            # If still no results, try business type search
            if not establishments:
                establishments = await self.fsa_client.search_by_business_type(
                    business_type_id=7835,  # Hospitals/Childcare/Caring Premises
                    name=home_name
                )
            
            # Find best match by name similarity
            best_match = None
            if establishments:
                home_name_lower = home_name.lower()
                for est in establishments:
                    est_name = est.get("BusinessName", "").lower()
                    # Simple matching: check if care home name contains establishment name or vice versa
                    if home_name_lower in est_name or est_name in home_name_lower:
                        best_match = est
                        break
                
                # If no exact match, use first result
                if not best_match and establishments:
                    best_match = establishments[0]
            
            if best_match:
                # Get detailed information
                fhrs_id = best_match.get("FHRSID")
                if fhrs_id:
                    try:
                        details = await self.fsa_client.get_establishment_details(fhrs_id)
                        
                        # Extract key information
                        rating_value = details.get("RatingValue")
                        rating_key = details.get("RatingKey")
                        
                        # Calculate health score
                        health_score = self.fsa_client.calculate_fsa_health_score(details)
                        
                        # Get historical ratings (if available)
                        historical_ratings = []
                        try:
                            history = await self.fsa_client.get_inspection_history(fhrs_id)
                            if history:
                                historical_ratings = history
                        except Exception as e:
                            print(f"Could not fetch FSA history for {home_name}: {e}")
                        
                        # Analyze trends if we have historical data
                        trend_analysis = None
                        if len(historical_ratings) > 1:
                            try:
                                trend_analysis = await self.fsa_client.analyze_fsa_trends(fhrs_id)
                            except Exception as e:
                                print(f"Could not analyze FSA trends for {home_name}: {e}")
                        
                        # Extract detailed sub-scores
                        breakdown_scores = details.get("breakdown_scores", {})
                        scores = details.get("scores", {})
                        
                        # Normalize sub-scores structure
                        hygiene_score = breakdown_scores.get("hygiene") or scores.get("Hygiene")
                        structural_score = breakdown_scores.get("structural") or scores.get("Structural")
                        management_score = breakdown_scores.get("confidence_in_management") or scores.get("ConfidenceInManagement")
                        
                        # Ensure scores are integers or None
                        try:
                            hygiene_score = int(hygiene_score) if hygiene_score is not None else None
                        except (ValueError, TypeError):
                            hygiene_score = None
                        
                        try:
                            structural_score = int(structural_score) if structural_score is not None else None
                        except (ValueError, TypeError):
                            structural_score = None
                        
                        try:
                            management_score = int(management_score) if management_score is not None else None
                        except (ValueError, TypeError):
                            management_score = None
                        
                        # Calculate normalized scores (0-100, higher is better)
                        # FSA scores are penalty points (lower is better), so we invert them
                        hygiene_normalized = round((20 - (hygiene_score or 20)) / 20 * 100, 1) if hygiene_score is not None else None
                        structural_normalized = round((20 - (structural_score or 20)) / 20 * 100, 1) if structural_score is not None else None
                        management_normalized = round((30 - (management_score or 30)) / 30 * 100, 1) if management_score is not None else None
                        
                        fsa_data = {
                            "fhrs_id": fhrs_id,
                            "rating_value": rating_value,
                            "rating_key": rating_key,
                            "rating_date": details.get("RatingDate"),
                            "business_name": details.get("BusinessName"),
                            "address": details.get("AddressLine1"),
                            "postcode": details.get("PostCode"),
                            "local_authority": details.get("LocalAuthorityName"),
                            "breakdown_scores": breakdown_scores,
                            "health_score": health_score,
                            "color": self._rating_to_color(rating_value),
                            # Historical ratings for Professional Report
                            "historical_ratings": historical_ratings,
                            "trend_analysis": trend_analysis,
                            # Detailed sub-scores for Professional Report
                            "detailed_sub_scores": {
                                "hygiene": {
                                    "raw_score": hygiene_score,
                                    "normalized_score": hygiene_normalized,
                                    "max_score": 20,
                                    "label": breakdown_scores.get("hygiene_label") or self._score_to_label(hygiene_score),
                                    "weight": 0.40
                                },
                                "cleanliness": {  # Structural = Cleanliness
                                    "raw_score": structural_score,
                                    "normalized_score": structural_normalized,
                                    "max_score": 20,
                                    "label": breakdown_scores.get("structural_label") or self._score_to_label(structural_score),
                                    "weight": 0.30
                                },
                                "management": {
                                    "raw_score": management_score,
                                    "normalized_score": management_normalized,
                                    "max_score": 30,
                                    "label": breakdown_scores.get("confidence_label") or self._score_to_label(management_score),
                                    "weight": 0.30
                                }
                            }
                        }
                        
                        # Cache the result
                        if self.use_cache and self.cache:
                            await self.cache.set(cache_key, fsa_data, ttl=self.cache_ttl)
                        
                        return fsa_data
                    except Exception as e:
                        print(f"Error fetching FSA details for {home_name}: {e}")
                        return None
            
            # Cache negative result (not found) for shorter time
            if self.use_cache and self.cache:
                await self.cache.set(cache_key, None, ttl=86400)  # 1 day for negative results
            
            return None
            
        except Exception as e:
            print(f"Error fetching FSA data for {home_name}: {e}")
            return None
    
    async def enrich_care_home(
        self,
        home: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enrich a single care home with FSA data
        
        Args:
            home: Care home dict
        
        Returns:
            Enriched care home dict
        """
        home_name = home.get("name") or home.get("Name")
        postcode = home.get("postcode") or home.get("Postcode")
        latitude = home.get("latitude") or home.get("Latitude")
        longitude = home.get("longitude") or home.get("Longitude")
        
        if not home_name:
            return home
        
        fsa_data = await self._fetch_fsa_data_for_home(
            home_name=home_name,
            postcode=postcode,
            latitude=latitude,
            longitude=longitude
        )
        
        if fsa_data:
            # Add FSA data to home
            home["fsa_rating"] = fsa_data.get("rating_value")
            home["fsa_rating_key"] = fsa_data.get("rating_key")
            home["fsa_rating_date"] = fsa_data.get("rating_date")
            home["fsa_color"] = fsa_data.get("color")
            home["fsa_health_score"] = fsa_data.get("health_score")
            home["fsa_breakdown"] = fsa_data.get("breakdown_scores")
            home["fsa_fhrs_id"] = fsa_data.get("fhrs_id")
            # Add historical data for Professional Report
            home["fsa_historical_ratings"] = fsa_data.get("historical_ratings", [])
            home["fsa_trend_analysis"] = fsa_data.get("trend_analysis")
        else:
            # Set defaults if no FSA data found
            home["fsa_rating"] = None
            home["fsa_color"] = None
        
        return home
    
    async def enrich_care_homes_batch(
        self,
        homes: List[Dict[str, Any]],
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Enrich multiple care homes with FSA data (with rate limiting)
        
        Args:
            homes: List of care home dicts
            max_concurrent: Maximum concurrent requests
        
        Returns:
            List of enriched care home dicts
        """
        if not homes:
            return homes
        
        # Process in batches to respect rate limits
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def enrich_with_semaphore(home: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                return await self.enrich_care_home(home)
        
        # Process all homes concurrently (with semaphore limiting)
        enriched_homes = await asyncio.gather(
            *[enrich_with_semaphore(home) for home in homes],
            return_exceptions=True
        )
        
        # Filter out exceptions and return valid results
        result = []
        for i, enriched in enumerate(enriched_homes):
            if isinstance(enriched, Exception):
                print(f"Error enriching home {i}: {enriched}")
                result.append(homes[i])  # Return original home if enrichment failed
            else:
                result.append(enriched)
        
        return result
    
    async def close(self):
        """Close FSA client"""
        await self.fsa_client.close()

