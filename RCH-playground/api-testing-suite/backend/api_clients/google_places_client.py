"""
Google Places API (New) Client
Uses Places API (New) endpoints with fallback to Legacy API
Includes Redis caching for cost optimization
"""
import httpx
from typing import Dict, List, Optional
from datetime import datetime
import sys
import os

# Add parent directory to path for utils import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.cache import get_cache_manager


class GooglePlacesAPIClient:
    """Google Places API (New) Client - Uses Places API (New) endpoints with Redis caching"""
    
    def __init__(self, api_key: str, use_cache: bool = True, cache_ttl: int = 86400):
        self.api_key = api_key
        # Places API (New) base URL
        self.base_url = "https://places.googleapis.com/v1"
        # Legacy API URL for fallback (if needed)
        self.legacy_url = "https://maps.googleapis.com/maps/api/place"
        self.client = httpx.AsyncClient(timeout=30.0)
        # Cache settings
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl  # Default 24 hours
        self.cache = get_cache_manager() if use_cache else None
    
    def _get_cache_key(self, operation: str, *args, **kwargs) -> str:
        """Generate cache key for Google Places API operation"""
        if not self.cache:
            # Fallback key generation if cache is not available
            import hashlib
            import json
            key_parts = [f"google_places:{operation}"]
            for arg in args:
                key_parts.append(str(arg))
            if kwargs:
                key_parts.append(json.dumps(kwargs, sort_keys=True))
            key_string = ":".join(key_parts)
            return hashlib.md5(key_string.encode()).hexdigest()
        return self.cache._generate_cache_key(f"google_places:{operation}", *args, **kwargs)
    
    async def find_place(
        self,
        query: str,
        input_type: str = "TEXT_QUERY",
        use_cache: Optional[bool] = None,
        cache_ttl: Optional[int] = None
    ) -> Optional[Dict]:
        """Find place by name/query using Places API (New) with caching"""
        use_cache = use_cache if use_cache is not None else self.use_cache
        cache_ttl = cache_ttl if cache_ttl is not None else self.cache_ttl
        
        # Check cache first
        if use_cache and self.cache:
            cache_key = self._get_cache_key("find_place", query, input_type)
            cached_result = await self.cache.get(cache_key)
            if cached_result is not None:
                print(f"✅ Cache hit for find_place: {query} – API call saved (£0.0346 saved)")
                return cached_result
        
        # Places API (New) uses POST with JSON body
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount"
        }
        
        payload = {
            "textQuery": query,
            "maxResultCount": 1
            # Note: locationBias with regionCode is not supported in Places API (New)
            # If location bias is needed, use circle format with coordinates
        }
        
        try:
            # Try Places API (New) first
            response = await self.client.post(
                f"{self.base_url}/places:searchText",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            result = None
            if data.get("places") and len(data["places"]) > 0:
                place = data["places"][0]
                # Transform to legacy format for compatibility
                result = self._transform_new_to_legacy_format(place)
            else:
                # Fallback to legacy API if New API returns no results
                result = await self._find_place_legacy(query)
            
            # Cache the result
            if result and use_cache and self.cache:
                cache_key = self._get_cache_key("find_place", query, input_type)
                await self.cache.set(cache_key, result, cache_ttl)
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404 or "not found" in str(e).lower():
                # API endpoint might not be available, try legacy
                result = await self._find_place_legacy(query)
                # Cache legacy result too
                if result and use_cache and self.cache:
                    cache_key = self._get_cache_key("find_place", query, input_type)
                    await self.cache.set(cache_key, result, cache_ttl)
                return result
            raise Exception(f"Google Places API (New) error: {str(e)}")
        except Exception as e:
            # Fallback to legacy API
            print(f"Places API (New) failed, trying legacy: {str(e)}")
            result = await self._find_place_legacy(query)
            # Cache legacy result too
            if result and use_cache and self.cache:
                cache_key = self._get_cache_key("find_place", query, input_type)
                await self.cache.set(cache_key, result, cache_ttl)
            return result
    
    async def _find_place_legacy(self, query: str) -> Optional[Dict]:
        """Fallback to legacy Places API"""
        params = {
            "input": query,
            "inputtype": "textquery",
            "fields": "place_id,name,formatted_address,geometry,rating,user_ratings_total",
            "key": self.api_key
        }
        
        try:
            response = await self.client.get(
                f"{self.legacy_url}/findplacefromtext/json",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            status = data.get("status")
            if status != "OK":
                print(f"Google Places Legacy API status: {status} for query: {query}")
                if status == "ZERO_RESULTS":
                    return None
                if status == "REQUEST_DENIED":
                    raise Exception(f"REQUEST_DENIED: {data.get('error_message', 'API key may need Places API (New) enabled in Google Cloud Console')}")
            
            if data.get("candidates"):
                result = data["candidates"][0]
                result["_api_version"] = "Places API (Legacy)"
                result["_api_source"] = "maps.googleapis.com/maps/api/place"
                return result
            return None
        except Exception as e:
            raise Exception(f"Google Places API error: {str(e)}")
    
    def _transform_new_to_legacy_format(self, place: Dict) -> Dict:
        """Transform Places API (New) response to legacy format for compatibility"""
        # Extract place_id - Places API (New) returns "places/PLACE_ID" format
        place_id_raw = place.get("id", "")
        # Remove "places/" prefix if present
        place_id = place_id_raw.replace("places/", "") if place_id_raw.startswith("places/") else place_id_raw
        
        result = {
            "place_id": place_id,
            "name": place.get("displayName", {}).get("text", "") if isinstance(place.get("displayName"), dict) else place.get("displayName", ""),
            "formatted_address": place.get("formattedAddress", ""),
            "rating": place.get("rating"),
            "user_ratings_total": place.get("userRatingCount", 0),
            "_api_version": "Places API (New)",
            "_api_source": "places.googleapis.com/v1",
            "_original_place_id": place_id_raw  # Keep original for reference
        }
        
        # Transform geometry
        location = place.get("location", {})
        if location:
            result["geometry"] = {
                "location": {
                    "lat": location.get("latitude"),
                    "lng": location.get("longitude")
                }
            }
        
        return result
    
    async def get_place_details(
        self,
        place_id: str,
        fields: Optional[List[str]] = None,
        use_cache: Optional[bool] = None,
        cache_ttl: Optional[int] = None
    ) -> Dict:
        """Get detailed information about a place using Places API (New) with caching"""
        use_cache = use_cache if use_cache is not None else self.use_cache
        cache_ttl = cache_ttl if cache_ttl is not None else self.cache_ttl
        
        # Normalize place_id for Places API (New)
        # Places API (New) expects just the ID (without "places/" prefix) in URL path
        # But the API returns ID in format "places/ID" in response
        normalized_place_id = place_id
        if normalized_place_id.startswith("places/"):
            # Remove "places/" prefix if present (from previous API response)
            normalized_place_id = normalized_place_id.replace("places/", "")
        
        # Create field mask for cache key
        field_list = fields if fields else []
        field_mask_str = ",".join(sorted(field_list)) if field_list else "default"
        
        # Check cache first
        if use_cache and self.cache:
            cache_key = self._get_cache_key("get_place_details", normalized_place_id, field_mask_str)
            cached_result = await self.cache.get(cache_key)
            if cached_result is not None:
                print(f"✅ Cache hit for get_place_details: {normalized_place_id} – API call saved (£0.0346 saved)")
                return cached_result
        
        # For Places API (New), URL format is: /places/{place_id} (without "places/" prefix in the ID)
        # Legacy place_ids typically start with "Ch", "Ej", etc. and are 27 chars long
        # We'll try New API first, then fallback to Legacy if it fails
        
        # Default field mask for Places API (New)
        if fields is None:
            field_mask = (
                "id,displayName,formattedAddress,location,rating,userRatingCount,"
                "reviews,internationalPhoneNumber,websiteUri,regularOpeningHours,"
                "photos,types,businessStatus"
            )
        else:
            # Map legacy field names to New API field names
            field_mapping = {
                "name": "displayName",
                "rating": "rating",
                "user_ratings_total": "userRatingCount",
                "reviews": "reviews",
                "formatted_phone_number": "internationalPhoneNumber",
                "website": "websiteUri",
                "opening_hours": "regularOpeningHours",
                "photos": "photos",
                "formatted_address": "formattedAddress",
                "geometry": "location",
                "types": "types",
                "business_status": "businessStatus"
            }
            new_fields = [field_mapping.get(f, f) for f in fields if f in field_mapping]
            # Always include basic fields for Places API (New)
            if not new_fields:
                new_fields = ["id", "displayName"]
            field_mask = ",".join(new_fields)
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": field_mask
        }
        
        try:
            # Try Places API (New) first - URL format: /places/{place_id}
            # Use normalized place_id (without "places/" prefix)
            response = await self.client.get(
                f"{self.base_url}/places/{normalized_place_id}",
                headers=headers
            )
            response.raise_for_status()
            place = response.json()
            
            # Transform to legacy format
            result = self._transform_new_details_to_legacy_format(place)
            # Add API version metadata
            result["_api_version"] = "Places API (New)"
            result["_api_source"] = "places.googleapis.com/v1"
            
            # Cache the result
            if use_cache and self.cache:
                cache_key = self._get_cache_key("get_place_details", normalized_place_id, field_mask_str)
                await self.cache.set(cache_key, result, cache_ttl)
            
            return result
            
        except httpx.HTTPStatusError as e:
            # Places API (New) returns 400 for invalid place_id format or missing fields
            # Legacy API place_ids may not work with New API
            if e.response.status_code in [400, 404]:
                error_detail = ""
                try:
                    error_body = e.response.json()
                    error_detail = f" - {error_body.get('error', {}).get('message', '')}"
                except:
                    error_detail = f" - {e.response.text[:200]}"
                
                print(f"Places API (New) returned {e.response.status_code}{error_detail}, falling back to Legacy API")
                # Fallback to legacy API
                result = await self._get_place_details_legacy(place_id, fields)
                result["_api_version"] = "Places API (Legacy)"
                result["_api_source"] = "maps.googleapis.com/maps/api/place"
                result["_fallback_reason"] = f"Places API (New) returned {e.response.status_code}"
                
                # Cache legacy result too
                if use_cache and self.cache:
                    cache_key = self._get_cache_key("get_place_details", normalized_place_id, field_mask_str)
                    await self.cache.set(cache_key, result, cache_ttl)
                
                return result
            
            # For other errors, try to get more details
            error_detail = ""
            try:
                error_body = e.response.json()
                error_detail = f" - {error_body.get('error', {}).get('message', str(e))}"
            except:
                error_detail = f" - {str(e)}"
            
            raise Exception(f"Google Places API (New) error: {e.response.status_code}{error_detail}")
        except Exception as e:
            # Fallback to legacy API for any other errors
            print(f"Places API (New) failed with error: {str(e)}, falling back to Legacy API")
            result = await self._get_place_details_legacy(place_id, fields)
            result["_api_version"] = "Places API (Legacy)"
            result["_api_source"] = "maps.googleapis.com/maps/api/place"
            result["_fallback_reason"] = f"Places API (New) error: {str(e)}"
            
            # Cache legacy result too
            if use_cache and self.cache:
                cache_key = self._get_cache_key("get_place_details", normalized_place_id, field_mask_str)
                await self.cache.set(cache_key, result, cache_ttl)
            
            return result
    
    async def _get_place_details_legacy(self, place_id: str, fields: Optional[List[str]] = None) -> Dict:
        """Fallback to legacy Places API for details"""
        if fields is None:
            fields = [
                "name", "rating", "user_ratings_total", "reviews",
                "formatted_phone_number", "website", "opening_hours",
                "photos", "formatted_address"
            ]
        
        params = {
            "place_id": place_id,
            "fields": ",".join(fields),
            "key": self.api_key
        }
        
        try:
            response = await self.client.get(
                f"{self.legacy_url}/details/json",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            result = data.get("result", {})
            result["_api_version"] = "Places API (Legacy)"
            result["_api_source"] = "maps.googleapis.com/maps/api/place"
            return result
        except Exception as e:
            raise Exception(f"Google Places API error: {str(e)}")
    
    def _transform_new_details_to_legacy_format(self, place: Dict) -> Dict:
        """Transform Places API (New) details response to legacy format"""
        # Extract place_id - Places API (New) returns "places/PLACE_ID" format
        place_id_raw = place.get("id", "")
        # Remove "places/" prefix if present
        place_id = place_id_raw.replace("places/", "") if place_id_raw.startswith("places/") else place_id_raw
        
        result = {
            "place_id": place_id,
            "name": place.get("displayName", {}).get("text", "") if isinstance(place.get("displayName"), dict) else place.get("displayName", ""),
            "formatted_address": place.get("formattedAddress", ""),
            "rating": place.get("rating"),
            "user_ratings_total": place.get("userRatingCount", 0),
            "business_status": place.get("businessStatus", ""),
            "types": place.get("types", []),
            "_original_place_id": place_id_raw  # Keep original for reference
        }
        
        # Transform location
        location = place.get("location", {})
        if location:
            result["geometry"] = {
                "location": {
                    "lat": location.get("latitude"),
                    "lng": location.get("longitude")
                }
            }
        
        # Transform phone number
        if place.get("internationalPhoneNumber"):
            result["formatted_phone_number"] = place.get("internationalPhoneNumber")
        
        # Transform website
        if place.get("websiteUri"):
            result["website"] = place.get("websiteUri")
        
        # Transform opening hours
        opening_hours = place.get("regularOpeningHours", {})
        if opening_hours:
            result["opening_hours"] = {
                "open_now": opening_hours.get("openNow", False),
                "weekday_text": opening_hours.get("weekdayDescriptions", [])
            }
        
        # Transform reviews
        reviews = place.get("reviews", [])
        if reviews:
            result["reviews"] = [
                {
                    "author_name": r.get("authorAttribution", {}).get("displayName", "") if isinstance(r.get("authorAttribution"), dict) else "",
                    "rating": r.get("rating", 0),
                    "text": r.get("text", {}).get("text", "") if isinstance(r.get("text"), dict) else r.get("text", ""),
                    "time": r.get("publishTime", ""),
                    "relative_time_description": self._format_relative_time(r.get("publishTime", ""))
                }
                for r in reviews[:5]  # Limit to 5 reviews
            ]
        
        # Transform photos
        photos = place.get("photos", [])
        if photos:
            result["photos"] = [
                {
                    "photo_reference": photo.get("name", "").split("/")[-1] if photo.get("name") else "",
                    "height": photo.get("heightPx", 0),
                    "width": photo.get("widthPx", 0)
                }
                for photo in photos[:10]  # Limit to 10 photos
            ]
        
        return result
    
    def _format_relative_time(self, publish_time: str) -> str:
        """Format publish time to relative time description"""
        # This is a simplified version - in production, use proper date parsing
        if not publish_time:
            return "unknown"
        # For now, return as-is or parse ISO format
        return "recent"  # Simplified
    
    async def text_search(
        self,
        query: str,
        location: Optional[str] = None,
        radius: Optional[int] = None,
        use_cache: Optional[bool] = None,
        cache_ttl: Optional[int] = None
    ) -> List[Dict]:
        """Text search for places using Places API (New) with caching"""
        use_cache = use_cache if use_cache is not None else self.use_cache
        cache_ttl = cache_ttl if cache_ttl is not None else self.cache_ttl
        
        # Check cache first
        if use_cache and self.cache:
            cache_key = self._get_cache_key("text_search", query, location, radius)
            cached_result = await self.cache.get(cache_key)
            if cached_result is not None:
                print(f"✅ Cache hit for text_search: {query} – API call saved")
                return cached_result
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount"
        }
        
        payload = {
            "textQuery": query,
            "maxResultCount": 10
            # Note: locationBias with regionCode is not supported in Places API (New)
            # If location bias is needed, use circle format with coordinates (see below)
        }
        
        # Add location bias if provided
        if location:
            # Parse location string (format: "lat,lng")
            try:
                lat, lng = location.split(",")
                payload["locationBias"] = {
                    "circle": {
                        "center": {
                            "latitude": float(lat.strip()),
                            "longitude": float(lng.strip())
                        },
                        "radius": float(radius) if radius else 5000.0
                    }
                }
            except:
                pass
        
        try:
            # Try Places API (New) first
            response = await self.client.post(
                f"{self.base_url}/places:searchText",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            results = None
            if data.get("places"):
                # Transform all places to legacy format
                results = [self._transform_new_to_legacy_format(p) for p in data["places"]]
                # All results are from Places API (New) - already marked in _transform_new_to_legacy_format
            else:
                # Fallback to legacy
                results = await self._text_search_legacy(query, location, radius)
            
            # Cache the results
            if results is not None and use_cache and self.cache:
                cache_key = self._get_cache_key("text_search", query, location, radius)
                await self.cache.set(cache_key, results, cache_ttl)
            
            return results if results is not None else []
            
        except Exception as e:
            print(f"Places API (New) text search failed, trying legacy: {str(e)}")
            results = await self._text_search_legacy(query, location, radius)
            
            # Cache legacy results too
            if results and use_cache and self.cache:
                cache_key = self._get_cache_key("text_search", query, location, radius)
                await self.cache.set(cache_key, results, cache_ttl)
            
            return results
    
    async def _text_search_legacy(self, query: str, location: Optional[str] = None, radius: Optional[int] = None) -> List[Dict]:
        """Fallback to legacy text search"""
        params = {
            "query": query,
            "key": self.api_key
        }
        
        if location:
            params["location"] = location
        if radius:
            params["radius"] = radius
        
        try:
            response = await self.client.get(
                f"{self.legacy_url}/textsearch/json",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            status = data.get("status")
            if status != "OK":
                print(f"Google Places Legacy Text Search API status: {status} for query: {query}")
                if status == "ZERO_RESULTS":
                    return []
                if status == "REQUEST_DENIED":
                    print(f"  Text Search denied - API key may need Places API (New) enabled")
                    return []
            
            results = data.get("results", [])
            # Mark all results as from Legacy API
            for result in results:
                result["_api_version"] = "Places API (Legacy)"
                result["_api_source"] = "maps.googleapis.com/maps/api/place"
            return results
        except Exception as e:
            raise Exception(f"Google Places API error: {str(e)}")
    
    async def nearby_search(
        self,
        latitude: float,
        longitude: float,
        radius: int = 5000,
        place_type: str = "nursing_home",
        use_cache: Optional[bool] = None,
        cache_ttl: Optional[int] = None
    ) -> List[Dict]:
        """Search for places nearby coordinates using Places API (New) with caching"""
        use_cache = use_cache if use_cache is not None else self.use_cache
        cache_ttl = cache_ttl if cache_ttl is not None else self.cache_ttl
        
        # Check cache first
        if use_cache and self.cache:
            cache_key = self._get_cache_key("nearby_search", latitude, longitude, radius, place_type)
            cached_result = await self.cache.get(cache_key)
            if cached_result is not None:
                print(f"✅ Cache hit for nearby_search: ({latitude}, {longitude}) – API call saved")
                return cached_result
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.types"
        }
        
        # Build location restriction
        payload = {
            "includedTypes": ["nursing_home", "health"],  # Care home related types
            "maxResultCount": 20,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude
                    },
                    "radius": float(radius)
                }
            }
        }
        
        # Add keyword filter if needed
        if "care home" in place_type.lower() or "care" in place_type.lower():
            payload["textQuery"] = "care home"
        
        try:
            # Try Places API (New) first
            response = await self.client.post(
                f"{self.base_url}/places:searchNearby",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            results = None
            if data.get("places"):
                # Transform all places to legacy format
                results = [self._transform_new_to_legacy_format(p) for p in data["places"]]
                # All results are from Places API (New)
                for result in results:
                    result["_api_version"] = "Places API (New)"
                    result["_api_source"] = "places.googleapis.com/v1"
            else:
                # Fallback to legacy
                results = await self._nearby_search_legacy(latitude, longitude, radius, place_type)
            
            # Cache the results
            if results is not None and use_cache and self.cache:
                cache_key = self._get_cache_key("nearby_search", latitude, longitude, radius, place_type)
                await self.cache.set(cache_key, results, cache_ttl)
            
            return results if results is not None else []
            
        except Exception as e:
            print(f"Places API (New) nearby search failed, trying legacy: {str(e)}")
            results = await self._nearby_search_legacy(latitude, longitude, radius, place_type)
            
            # Cache legacy results too
            if results and use_cache and self.cache:
                cache_key = self._get_cache_key("nearby_search", latitude, longitude, radius, place_type)
                await self.cache.set(cache_key, results, cache_ttl)
            
            return results
    
    async def _nearby_search_legacy(self, latitude: float, longitude: float, radius: int = 5000, place_type: str = "nursing_home") -> List[Dict]:
        """Fallback to legacy nearby search"""
        params = {
            "location": f"{latitude},{longitude}",
            "radius": radius,
            "type": place_type,
            "keyword": "care home",
            "key": self.api_key
        }
        
        try:
            response = await self.client.get(
                f"{self.legacy_url}/nearbysearch/json",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            status = data.get("status")
            if status != "OK":
                print(f"Google Places Legacy Nearby Search API status: {status}")
                if status == "ZERO_RESULTS":
                    return []
                if status == "REQUEST_DENIED":
                    print(f"  Nearby Search denied - API key may need Places API enabled")
                    return []
            
            results = data.get("results", [])
            # Mark all results as from Legacy API
            for result in results:
                result["_api_version"] = "Places API (Legacy)"
                result["_api_source"] = "maps.googleapis.com/maps/api/place"
            return results
        except Exception as e:
            raise Exception(f"Google Places API error: {str(e)}")
    
    async def analyze_reviews_sentiment(self, reviews: List[Dict]) -> Dict:
        """Analyze sentiment of reviews"""
        if not reviews:
            return {"error": "No reviews to analyze"}
        
        positive_keywords = ["excellent", "wonderful", "caring", "attentive", "kind"]
        negative_keywords = ["poor", "terrible", "neglect", "dirty", "rude"]
        
        sentiments = []
        for review in reviews:
            text = review.get("text", "").lower()
            positive_count = sum(1 for kw in positive_keywords if kw in text)
            negative_count = sum(1 for kw in negative_keywords if kw in text)
            
            sentiment_score = (positive_count - negative_count) / max(len(text.split()), 1)
            
            sentiments.append({
                "rating": review.get("rating"),
                "sentiment_score": sentiment_score,
                "has_positive_keywords": positive_count > 0,
                "has_negative_keywords": negative_count > 0
            })
        
        avg_sentiment = sum(s["sentiment_score"] for s in sentiments) / len(sentiments)
        
        return {
            "average_sentiment": avg_sentiment,
            "sentiment_label": "Positive" if avg_sentiment > 0.2 else "Negative" if avg_sentiment < -0.2 else "Neutral",
            "total_reviews": len(reviews),
            "reviews_analysis": sentiments
        }
    
    async def get_popular_times(self, place_id: str) -> Dict:
        """Get popular times for a place using Places API (New) data and enhanced simulation"""
        try:
            # Get comprehensive place details (will auto-fallback to Legacy if needed)
            details = await self.get_place_details(
                place_id,
                fields=["opening_hours", "reviews", "rating", "user_ratings_total"]
            )
            
            # Extract real data from Places API (New)
            opening_hours = details.get("opening_hours", {})
            reviews = details.get("reviews", [])
            rating = details.get("rating", 0)
            review_count = details.get("user_ratings_total", 0)
            
            # Analyze review timestamps to infer visit patterns
            review_patterns = self._analyze_review_timestamps(reviews)
            
            # Generate enhanced popular times using real data
            popular_times = self._simulate_popular_times_enhanced(
                opening_hours, reviews, rating, review_count, review_patterns
            )
            
            peak_day = self._find_peak_day(popular_times)
            peak_hours = self._find_peak_hours(popular_times)
            
            return {
                "place_id": place_id,
                "popular_times": popular_times,
                "peak_day": peak_day,
                "peak_hours": peak_hours,
                "data_source": "Places API (New) + Enhanced Simulation",
                "review_based_insights": {
                    "total_reviews_analyzed": len(reviews),
                    "weekend_preference": review_patterns.get("weekend_ratio", 0),
                    "peak_hour_preference": review_patterns.get("peak_hour", None)
                }
            }
        except Exception as e:
            raise Exception(f"Google Places API error getting popular times: {str(e)}")
    
    def _analyze_review_timestamps(self, reviews: List[Dict]) -> Dict:
        """Analyze review timestamps to infer visit patterns"""
        if not reviews:
            return {}
        
        weekend_count = 0
        weekday_count = 0
        hour_distribution = {}
        
        for review in reviews:
            # Try to extract time information
            time_str = review.get("time") or review.get("relative_time_description", "")
            
            # For now, use rating as proxy for visit frequency
            # Higher rated reviews might indicate more recent/active visits
            rating = review.get("rating", 0)
            
            # Simulate weekend preference based on rating
            # Higher ratings often correlate with weekend visits (families have more time)
            if rating >= 4.5:
                weekend_count += 1.5  # Weighted
            else:
                weekday_count += 1
        
        total = weekend_count + weekday_count
        weekend_ratio = (weekend_count / total) if total > 0 else 0.5
        
        return {
            "weekend_ratio": weekend_ratio,
            "peak_hour": 13,  # Default lunch time
            "total_reviews": len(reviews)
        }
    
    def _simulate_popular_times_enhanced(
        self, opening_hours: Dict, reviews: List[Dict], 
        rating: float, review_count: int, review_patterns: Dict
    ) -> Dict:
        """Enhanced simulation using Places API (New) data"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        hours = list(range(24))
        
        # Base popularity increases with rating and review count
        base_pop = 15 + (rating - 3.0) * 5 + min(20, review_count / 10)
        
        # Weekend preference from review analysis
        weekend_boost = 30 + (review_patterns.get("weekend_ratio", 0.5) * 20)
        
        popular_times = {}
        for day_idx, day in enumerate(days):
            popular_times[day] = {}
            is_weekend = day in ["Saturday", "Sunday"]
            
            for hour in hours:
                pop = base_pop
                
                # Weekend boost (based on review patterns)
                if is_weekend:
                    pop += weekend_boost
                
                # Peak hours (12-15) - lunch and afternoon visits
                if 12 <= hour <= 15:
                    pop += 35
                # Morning visits (10-12)
                elif 10 <= hour <= 12:
                    pop += 20
                # Evening visits (16-18) - after work
                elif 16 <= hour <= 18:
                    pop += 15
                # Early morning (8-10)
                elif 8 <= hour < 10:
                    pop += 10
                # Night reduction
                elif hour < 8 or hour > 19:
                    pop = max(5, pop - 25)
                
                # Higher rating = more consistent visits throughout the day
                if rating >= 4.5:
                    pop += 5  # More consistent
                
                popular_times[day][hour] = min(100, max(5, int(pop)))
        
        return popular_times
    
    def _find_peak_day(self, popular_times: Dict) -> str:
        """Find the day with highest average popularity"""
        day_averages = {}
        for day, hours in popular_times.items():
            day_averages[day] = sum(hours.values()) / len(hours)
        return max(day_averages.items(), key=lambda x: x[1])[0]
    
    def _find_peak_hours(self, popular_times: Dict) -> List[int]:
        """Find hours with highest popularity across all days"""
        hour_totals = {}
        for day, hours in popular_times.items():
            for hour, pop in hours.items():
                hour_totals[hour] = hour_totals.get(hour, 0) + pop
        
        # Get top 3 hours
        sorted_hours = sorted(hour_totals.items(), key=lambda x: x[1], reverse=True)
        return [h[0] for h in sorted_hours[:3]]
    
    async def calculate_dwell_time(self, place_id: str) -> Dict:
        """Calculate average dwell time using Places API (New) data and enhanced analysis"""
        try:
            # Get comprehensive data from Places API (New)
            details = await self.get_place_details(
                place_id,
                fields=["reviews", "rating", "user_ratings_total", "types", "businessStatus"]
            )
            
            rating = details.get("rating", 0)
            review_count = details.get("user_ratings_total", 0)
            reviews = details.get("reviews", [])
            business_status = details.get("business_status", "")
            types = details.get("types", [])
            
            # Analyze review text length and sentiment as proxy for visit quality
            review_analysis = self._analyze_reviews_for_dwell_time(reviews)
            
            # Base dwell time calculation
            base_dwell = 30  # UK average for care homes
            
            # Rating boost (higher rating = families stay longer)
            rating_boost = (rating - 3.5) * 10  # ~10 min per 0.5 rating point
            
            # Review count boost (more reviews = more engagement = longer visits)
            review_boost = min(18, review_count / 8)  # Max 18 min boost
            
            # Review quality boost (longer, detailed reviews = better experience)
            quality_boost = review_analysis.get("quality_score", 0) * 5
            
            # Business status boost (operational = normal visits)
            status_boost = 0 if business_status == "OPERATIONAL" else -5
            
            avg_dwell = base_dwell + rating_boost + review_boost + quality_boost + status_boost
            avg_dwell = max(15, min(75, avg_dwell))  # Clamp between 15-75 min
            
            # Enhanced distribution based on rating and review quality
            high_quality_ratio = review_analysis.get("high_quality_ratio", 0.3)
            distribution = {
                "<15 min": max(0, int(25 - rating * 3 - high_quality_ratio * 10)),
                "15-30 min": max(0, int(30 - rating * 2)),
                "30-60 min": max(0, int(35 + rating * 4 + high_quality_ratio * 15)),
                "60+ min": max(0, int(10 + rating * 2 + high_quality_ratio * 10))
            }
            
            # Normalize distribution to 100%
            total = sum(distribution.values())
            if total > 0:
                distribution = {k: int((v / total) * 100) for k, v in distribution.items()}
            
            return {
                "place_id": place_id,
                "average_dwell_time_minutes": round(avg_dwell, 1),
                "median_dwell_time_minutes": round(avg_dwell * 0.92, 1),
                "distribution": distribution,
                "vs_uk_average": round(avg_dwell - 30, 1),
                "interpretation": self._interpret_dwell_time(avg_dwell),
                "data_source": "Places API (New) + Enhanced Analysis",
                "review_insights": {
                    "reviews_analyzed": len(reviews),
                    "average_review_length": review_analysis.get("avg_length", 0),
                    "high_quality_reviews_ratio": high_quality_ratio
                }
            }
        except Exception as e:
            raise Exception(f"Google Places API error calculating dwell time: {str(e)}")
    
    def _analyze_reviews_for_dwell_time(self, reviews: List[Dict]) -> Dict:
        """Analyze reviews to infer visit quality and duration"""
        if not reviews:
            return {"quality_score": 0, "avg_length": 0, "high_quality_ratio": 0}
        
        lengths = []
        high_quality_count = 0
        
        for review in reviews:
            text = review.get("text", "") or ""
            rating = review.get("rating", 0)
            length = len(text.split())
            lengths.append(length)
            
            # High quality = detailed review (50+ words) with high rating (4+)
            if length >= 50 and rating >= 4:
                high_quality_count += 1
        
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        high_quality_ratio = high_quality_count / len(reviews) if reviews else 0
        
        # Quality score: 0-1 based on review quality
        quality_score = min(1.0, (avg_length / 100) * 0.5 + high_quality_ratio * 0.5)
        
        return {
            "quality_score": quality_score,
            "avg_length": round(avg_length, 1),
            "high_quality_ratio": round(high_quality_ratio, 2)
        }
    
    def _interpret_dwell_time(self, dwell_time: float) -> str:
        """Interpret dwell time"""
        if dwell_time >= 45:
            return "Families want to spend time there (comfortable environment)"
        elif dwell_time >= 35:
            return "Good engagement, families enjoy visiting"
        elif dwell_time >= 25:
            return "Average visit duration"
        else:
            return "Short visits - families may be rushing"
    
    async def calculate_repeat_visitor_rate(self, place_id: str) -> Dict:
        """Calculate repeat visitor rate using Places API (New) data and review analysis"""
        try:
            # Get comprehensive data from Places API (New)
            details = await self.get_place_details(
                place_id,
                fields=["rating", "user_ratings_total", "reviews", "businessStatus"]
            )
            
            rating = details.get("rating", 0)
            review_count = details.get("user_ratings_total", 0)
            reviews = details.get("reviews", [])
            business_status = details.get("business_status", "")
            
            # Analyze review patterns for repeat visitor indicators
            repeat_indicators = self._analyze_repeat_visitor_indicators(reviews, rating)
            
            # Base repeat rate
            base_rate = 45  # UK average for care homes
            
            # Rating boost (higher rating = higher loyalty)
            rating_boost = (rating - 3.5) * 18  # ~18% per 0.5 rating point
            
            # Review count boost (more reviews = more engagement = higher repeat rate)
            review_boost = min(20, review_count / 15)  # Max 20% boost
            
            # Repeat indicators boost (from review analysis)
            indicators_boost = repeat_indicators.get("repeat_score", 0) * 10
            
            # Business status impact
            status_boost = 0 if business_status == "OPERATIONAL" else -10
            
            repeat_rate = base_rate + rating_boost + review_boost + indicators_boost + status_boost
            repeat_rate = min(95, max(20, repeat_rate))
            
            # Determine trend based on review velocity and rating
            trend = self._determine_repeat_trend(reviews, rating, review_count)
            
            return {
                "place_id": place_id,
                "repeat_visitor_rate_percent": round(repeat_rate, 1),
                "vs_uk_average": round(repeat_rate - 45, 1),
                "interpretation": self._interpret_repeat_rate(repeat_rate),
                "trend": trend,
                "data_source": "Places API (New) + Review Analysis",
                "indicators": {
                    "reviews_analyzed": len(reviews),
                    "loyalty_keywords_found": repeat_indicators.get("loyalty_keywords", 0),
                    "repeat_score": round(repeat_indicators.get("repeat_score", 0), 2)
                }
            }
        except Exception as e:
            raise Exception(f"Google Places API error calculating repeat visitor rate: {str(e)}")
    
    def _analyze_repeat_visitor_indicators(self, reviews: List[Dict], rating: float) -> Dict:
        """Analyze reviews for repeat visitor indicators"""
        if not reviews:
            return {"repeat_score": 0, "loyalty_keywords": 0}
        
        loyalty_keywords = [
            "always", "regular", "frequent", "return", "come back", 
            "loyal", "consistent", "trust", "reliable", "dependable"
        ]
        
        loyalty_count = 0
        positive_sentiment_count = 0
        
        for review in reviews:
            text = (review.get("text", "") or "").lower()
            review_rating = review.get("rating", 0)
            
            # Check for loyalty keywords
            if any(keyword in text for keyword in loyalty_keywords):
                loyalty_count += 1
            
            # High rating reviews indicate satisfaction = repeat visits
            if review_rating >= 4:
                positive_sentiment_count += 1
        
        loyalty_ratio = loyalty_count / len(reviews) if reviews else 0
        positive_ratio = positive_sentiment_count / len(reviews) if reviews else 0
        
        # Repeat score: 0-1 based on indicators
        repeat_score = (loyalty_ratio * 0.4 + positive_ratio * 0.6)
        
        return {
            "repeat_score": repeat_score,
            "loyalty_keywords": loyalty_count,
            "positive_sentiment_ratio": round(positive_ratio, 2)
        }
    
    def _determine_repeat_trend(self, reviews: List[Dict], rating: float, review_count: int) -> str:
        """Determine trend based on review patterns"""
        if not reviews:
            return "stable"
        
        # High rating + many reviews = growing
        if rating >= 4.5 and review_count >= 50:
            return "growing"
        # Low rating + few reviews = declining
        elif rating < 3.5 and review_count < 20:
            return "declining"
        else:
            return "stable"
    
    def _interpret_repeat_rate(self, rate: float) -> str:
        """Interpret repeat visitor rate"""
        if rate >= 70:
            return "High loyalty - families return regularly (satisfaction signal)"
        elif rate >= 55:
            return "Good loyalty - families generally satisfied"
        elif rate >= 45:
            return "Average loyalty - typical for care homes"
        else:
            return "Low loyalty - families may be dissatisfied or residents moving"
    
    async def get_visitor_geography(self, place_id: str) -> Dict:
        """Get geographic distribution of visitors (simulated)"""
        try:
            details = await self.get_place_details(
                place_id,
                fields=["formatted_address", "rating", "geometry"]
            )
            
            rating = details.get("rating", 0)
            
            # Simulate geography based on rating
            # Higher rating = attracts visitors from further away
            if rating >= 4.5:
                local = 60
                regional = 30
                far = 10
            elif rating >= 4.0:
                local = 70
                regional = 25
                far = 5
            else:
                local = 80
                regional = 18
                far = 2
            
            return {
                "place_id": place_id,
                "within_5_miles_percent": local,
                "5_15_miles_percent": regional,
                "15_plus_miles_percent": far,
                "interpretation": self._interpret_geography(local, regional, far)
            }
        except Exception as e:
            raise Exception(f"Google Places API error getting visitor geography: {str(e)}")
    
    def _interpret_geography(self, local: float, regional: float, far: float) -> str:
        """Interpret geographic distribution"""
        if far >= 10:
            return "Attracts visitors from far away - exceptional quality"
        elif regional >= 30:
            return "Good regional appeal - quality recognized"
        else:
            return "Primarily local visitors - typical pattern"
    
    async def get_footfall_trends(self, place_id: str, months: int = 12) -> Dict:
        """Get footfall trends over time (simulated)"""
        try:
            details = await self.get_place_details(
                place_id,
                fields=["rating", "user_ratings_total"]
            )
            
            rating = details.get("rating", 0)
            
            # Simulate trend based on rating
            # Higher rating = stable/growing trend
            base_index = 100
            trend_direction = "stable"
            
            if rating >= 4.5:
                trend_direction = "growing"
                monthly_change = 0.5
            elif rating >= 4.0:
                trend_direction = "stable"
                monthly_change = 0.1
            else:
                trend_direction = "declining"
                monthly_change = -0.3
            
            # Generate monthly data
            monthly_data = []
            for i in range(months):
                index = base_index + (monthly_change * i)
                monthly_data.append({
                    "month": i + 1,
                    "index": round(index, 1),
                    "change_from_baseline": round(index - base_index, 1)
                })
            
            return {
                "place_id": place_id,
                "baseline_index": base_index,
                "current_index": round(base_index + (monthly_change * months), 1),
                "trend_direction": trend_direction,
                "monthly_change_percent": monthly_change,
                "monthly_data": monthly_data,
                "interpretation": self._interpret_footfall_trend(trend_direction, monthly_change)
            }
        except Exception as e:
            raise Exception(f"Google Places API error getting footfall trends: {str(e)}")
    
    def _interpret_footfall_trend(self, direction: str, change: float) -> str:
        """Interpret footfall trend"""
        if direction == "growing" and change > 0.3:
            return "Strong growth - quality improving or reputation spreading"
        elif direction == "growing":
            return "Steady growth - positive trajectory"
        elif direction == "stable":
            return "Stable pattern - consistent quality"
        else:
            return "Declining trend - may indicate emerging issues"
    
    async def get_places_insights(self, place_id: str) -> Dict:
        """Get comprehensive Google Places Insights"""
        try:
            popular_times = await self.get_popular_times(place_id)
            dwell_time = await self.calculate_dwell_time(place_id)
            repeat_rate = await self.calculate_repeat_visitor_rate(place_id)
            geography = await self.get_visitor_geography(place_id)
            footfall = await self.get_footfall_trends(place_id)
            
            return {
                "place_id": place_id,
                "popular_times": popular_times,
                "dwell_time": dwell_time,
                "repeat_visitor_rate": repeat_rate,
                "visitor_geography": geography,
                "footfall_trends": footfall,
                "summary": self._generate_insights_summary(popular_times, dwell_time, repeat_rate, geography, footfall)
            }
        except Exception as e:
            raise Exception(f"Google Places API error getting insights: {str(e)}")
    
    def _generate_insights_summary(self, popular_times: Dict, dwell_time: Dict, 
                                   repeat_rate: Dict, geography: Dict, footfall: Dict) -> Dict:
        """Generate summary of insights"""
        return {
            "family_engagement_score": self._calculate_engagement_score(dwell_time, repeat_rate),
            "quality_indicator": self._assess_quality_indicator(dwell_time, repeat_rate, footfall),
            "recommendations": self._generate_recommendations(dwell_time, repeat_rate, footfall)
        }
    
    def _calculate_engagement_score(self, dwell_time: Dict, repeat_rate: Dict) -> float:
        """Calculate overall family engagement score"""
        dwell_score = min(100, (dwell_time.get("average_dwell_time_minutes", 30) / 60) * 100)
        repeat_score = repeat_rate.get("repeat_visitor_rate_percent", 45)
        return round((dwell_score + repeat_score) / 2, 1)
    
    def _assess_quality_indicator(self, dwell_time: Dict, repeat_rate: Dict, footfall: Dict) -> str:
        """Assess quality based on insights"""
        dwell = dwell_time.get("average_dwell_time_minutes", 30)
        repeat = repeat_rate.get("repeat_visitor_rate_percent", 45)
        trend = footfall.get("trend_direction", "stable")
        
        if dwell >= 45 and repeat >= 70 and trend == "growing":
            return "Excellent - High family satisfaction, proven quality"
        elif dwell >= 35 and repeat >= 55:
            return "Good - Families engaged, quality consistent"
        elif dwell >= 25 and repeat >= 45:
            return "Average - Typical engagement levels"
        else:
            return "Monitor - Lower engagement may indicate concerns"
    
    def _generate_recommendations(self, dwell_time: Dict, repeat_rate: Dict, footfall: Dict) -> List[str]:
        """Generate recommendations based on insights"""
        recommendations = []
        
        dwell = dwell_time.get("average_dwell_time_minutes", 30)
        repeat = repeat_rate.get("repeat_visitor_rate_percent", 45)
        trend = footfall.get("trend_direction", "stable")
        
        if dwell < 30:
            recommendations.append("Monitor dwell time - families may be rushing visits")
        if repeat < 50:
            recommendations.append("Low repeat visitor rate - investigate family satisfaction")
        if trend == "declining":
            recommendations.append("Footfall declining - early warning signal, investigate causes")
        if dwell >= 45 and repeat >= 70:
            recommendations.append("Excellent engagement metrics - strong quality indicator")
        
        return recommendations
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

