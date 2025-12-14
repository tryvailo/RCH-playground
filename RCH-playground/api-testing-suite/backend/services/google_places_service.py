"""
Google Places Service
Service для обогащения данных домов престарелых Google Places данными
"""
from typing import Dict, List, Optional, Any
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from api_clients.google_places_client import GooglePlacesAPIClient
from utils.cache import get_cache_manager
from config_manager import get_credentials


class GooglePlacesService:
    """Service для обогащения данных Google Places"""
    
    def __init__(self, use_cache: bool = True, cache_ttl: int = 86400):
        """
        Initialize Google Places Service
        
        Args:
            use_cache: Use Redis cache for Google Places data
            cache_ttl: Cache TTL in seconds (default 24 hours)
        """
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        self.cache = get_cache_manager() if use_cache else None
        self._client = None
    
    def _get_client(self) -> GooglePlacesAPIClient:
        """Get or create Google Places API client"""
        if self._client is None:
            creds = get_credentials()
            if not creds.google_places or not creds.google_places.api_key:
                raise ValueError("Google Places API key not configured")
            self._client = GooglePlacesAPIClient(
                api_key=creds.google_places.api_key,
                use_cache=self.use_cache,
                cache_ttl=self.cache_ttl
            )
        return self._client
    
    async def enrich_care_home(
        self,
        home: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Обогатить данные дома Google Places данными
        
        Args:
            home: Care home dict with name, postcode, address, etc.
        
        Returns:
            Enriched care home dict with google_rating, review_count, etc.
        """
        home_name = home.get('name')
        home_postcode = home.get('postcode')
        home_address = home.get('address') or home.get('postalAddress', '')
        
        if not home_name:
            return home
        
        # Check if already enriched
        if home.get('google_rating') is not None and home.get('review_count') is not None:
            return home
        
        # Check cache
        if self.use_cache and self.cache:
            cache_key = f"google_places_enrich:{home_name}:{home_postcode}"
            cached = await self.cache.get(cache_key)
            if cached:
                home['google_rating'] = cached.get('rating')
                home['review_count'] = cached.get('review_count')
                home['user_ratings_total'] = cached.get('review_count')
                return home
        
        try:
            client = self._get_client()
            
            # Build query: "Care Home Name, Postcode, UK"
            query_parts = [home_name]
            if home_postcode:
                query_parts.append(home_postcode)
            if home_address:
                # Extract city/town from address if available
                address_parts = home_address.split(',')
                if len(address_parts) > 1:
                    query_parts.append(address_parts[-1].strip())
            query_parts.append("UK")
            
            query = ", ".join(query_parts)
            
            # Find place
            place_result = await client.find_place(
                query=query,
                input_type="TEXT_QUERY"
            )
            
            if place_result and place_result.get('candidates'):
                place_id = place_result['candidates'][0].get('place_id')
                
                if place_id:
                    # Get place details
                    details = await client.get_place_details(
                        place_id=place_id,
                        fields=['rating', 'user_ratings_total', 'reviews', 'photos']
                    )
                    
                    if details:
                        # Extract rating and review count
                        rating = details.get('rating')
                        review_count = details.get('user_ratings_total', 0)
                        
                        if rating is not None:
                            home['google_rating'] = float(rating)
                            home['review_count'] = int(review_count) if review_count else 0
                            home['user_ratings_total'] = home['review_count']
                            
                            # Cache for 24 hours
                            if self.use_cache and self.cache:
                                cache_key = f"google_places_enrich:{home_name}:{home_postcode}"
                                await self.cache.set(
                                    cache_key,
                                    {
                                        'rating': rating,
                                        'review_count': review_count
                                    },
                                    ttl=self.cache_ttl
                                )
                        
                        # Extract photo URL if available
                        photos = details.get('photos', [])
                        if photos and len(photos) > 0:
                            photo_reference = photos[0].get('photo_reference')
                            if photo_reference:
                                # Generate photo URL from photo_reference
                                # Use our backend endpoint or direct Google API URL
                                try:
                                    creds = get_credentials()
                                    api_key = creds.google_places.api_key if creds.google_places else None
                                    if api_key:
                                        # Generate Google Places photo URL
                                        photo_url = (
                                            f"https://maps.googleapis.com/maps/api/place/photo"
                                            f"?maxwidth=800"
                                            f"&photo_reference={photo_reference}"
                                            f"&key={api_key}"
                                        )
                                        home['photo_url'] = photo_url
                                        home['google_photo_reference'] = photo_reference
                                    else:
                                        # Fallback: use backend endpoint
                                        home['photo_url'] = f"/api/google-places/photo/{photo_reference}"
                                        home['google_photo_reference'] = photo_reference
                                except Exception as e:
                                    print(f"Error generating photo URL: {e}")
                                    home['google_photo_reference'] = photo_reference
        except Exception as e:
            # Log error but don't fail - return home without enrichment
            print(f"Error enriching care home '{home_name}' with Google Places: {e}")
        
        return home
    
    async def enrich_care_homes_batch(
        self,
        homes: List[Dict[str, Any]],
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Обогатить список домов Google Places данными (batch)
        
        Args:
            homes: List of care home dicts
            max_concurrent: Maximum concurrent API calls (to avoid rate limits)
        
        Returns:
            List of enriched care home dicts
        """
        import asyncio
        
        # Process in batches to avoid rate limits
        enriched_homes = []
        for i in range(0, len(homes), max_concurrent):
            batch = homes[i:i + max_concurrent]
            tasks = [self.enrich_care_home(home) for home in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    print(f"Error in batch enrichment: {result}")
                    # Add original home if enrichment failed
                    enriched_homes.append(homes[i + batch_results.index(result)])
                else:
                    enriched_homes.append(result)
        
        return enriched_homes
    
    async def close(self):
        """Close Google Places API client"""
        if self._client:
            await self._client.close()
            self._client = None

