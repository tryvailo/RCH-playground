"""
Google Places Enrichment Service
Enriches care homes with Google Places reviews and sentiment analysis
"""
import asyncio
from typing import List, Dict, Optional, Any
from api_clients.google_places_client import GooglePlacesAPIClient
from utils.cache import get_cache_manager
import logging

logger = logging.getLogger(__name__)


class GooglePlacesEnrichmentService:
    """Service to enrich care homes with Google Places reviews and sentiment analysis"""
    
    def __init__(self, api_key: str, use_cache: bool = True, cache_ttl: int = 86400):
        """
        Initialize Google Places Enrichment Service
        
        Args:
            api_key: Google Places API key
            use_cache: Whether to use Redis cache
            cache_ttl: Cache TTL in seconds (default 24 hours)
        """
        self.client = GooglePlacesAPIClient(api_key=api_key, use_cache=use_cache, cache_ttl=cache_ttl)
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        self.cache = get_cache_manager() if use_cache else None
    
    def _get_cache_key(self, home_name: str, postcode: str) -> str:
        """Generate cache key for Google Places data"""
        if self.cache:
            return self.cache._generate_cache_key("google_places_enrichment", home_name, postcode)
        return f"google_places:{home_name}:{postcode}"
    
    def _analyze_sentiment_simple(self, reviews: List[Dict]) -> Dict[str, Any]:
        """
        Simple sentiment analysis based on ratings and keywords.
        In production, this could use ML models or external APIs.
        
        Args:
            reviews: List of review dicts with 'rating' and 'text' fields
        
        Returns:
            Dict with sentiment analysis results
        """
        if not reviews:
            return {
                'average_sentiment': 0.5,
                'sentiment_label': 'neutral',
                'total_reviews': 0,
                'positive_reviews': 0,
                'negative_reviews': 0,
                'neutral_reviews': 0,
                'sentiment_distribution': {}
            }
        
        # Positive keywords
        positive_keywords = [
            'excellent', 'great', 'wonderful', 'amazing', 'fantastic', 'love',
            'caring', 'compassionate', 'professional', 'clean', 'comfortable',
            'friendly', 'helpful', 'recommend', 'highly', 'outstanding'
        ]
        
        # Negative keywords
        negative_keywords = [
            'poor', 'terrible', 'awful', 'disappointed', 'worst', 'horrible',
            'dirty', 'neglect', 'complaint', 'unprofessional', 'rude',
            'unsafe', 'concerned', 'worried', 'avoid', 'bad'
        ]
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for review in reviews:
            rating = review.get('rating', 0)
            text = review.get('text', '').lower()
            
            # Ensure rating is a number
            try:
                rating = float(rating) if rating is not None else 0.0
            except (ValueError, TypeError):
                rating = 0.0
            
            # Count keyword matches
            positive_matches = sum(1 for keyword in positive_keywords if keyword in text)
            negative_matches = sum(1 for keyword in negative_keywords if keyword in text)
            
            # Determine sentiment based on rating and keywords
            if rating >= 4 and positive_matches > negative_matches:
                positive_count += 1
            elif rating <= 2 or negative_matches > positive_matches:
                negative_count += 1
            else:
                neutral_count += 1
        
        total_reviews = len(reviews)
        average_sentiment = (
            (positive_count * 1.0 + neutral_count * 0.5) / total_reviews
            if total_reviews > 0 else 0.5
        )
        
        # Ensure average_sentiment is a float
        try:
            average_sentiment = float(average_sentiment) if average_sentiment is not None else 0.5
        except (ValueError, TypeError):
            average_sentiment = 0.5
        
        # Determine label
        if average_sentiment >= 0.7:
            sentiment_label = 'positive'
        elif average_sentiment >= 0.4:
            sentiment_label = 'neutral'
        else:
            sentiment_label = 'negative'
        
        return {
            'average_sentiment': round(average_sentiment, 2),
            'sentiment_label': sentiment_label,
            'total_reviews': total_reviews,
            'positive_reviews': positive_count,
            'negative_reviews': negative_count,
            'neutral_reviews': neutral_count,
            'sentiment_distribution': {
                'positive': round(positive_count / total_reviews * 100, 1) if total_reviews > 0 else 0,
                'negative': round(negative_count / total_reviews * 100, 1) if total_reviews > 0 else 0,
                'neutral': round(neutral_count / total_reviews * 100, 1) if total_reviews > 0 else 0
            }
        }
    
    async def _fetch_google_places_data(
        self,
        home_name: str,
        postcode: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch Google Places data for a single care home
        
        Args:
            home_name: Name of the care home
            postcode: Postcode of the care home
            latitude: Latitude coordinate
            longitude: Longitude coordinate
        
        Returns:
            Google Places data dict or None if not found
        """
        cache_key = self._get_cache_key(home_name, postcode or "")
        
        # Check cache first
        if self.use_cache and self.cache:
            cached_data = await self.cache.get(cache_key)
            if cached_data is not None:
                logger.info(f"✅ Google Places cache hit for {home_name}")
                return cached_data
        
        try:
            # Build search query
            query = f"{home_name}"
            if postcode:
                query += f" {postcode}"
            
            # Find place
            place_result = await self.client.find_place(query)
            
            if not place_result or not place_result.get('place_id'):
                # Try with location bias if coordinates available
                if latitude and longitude:
                    place_result = await self.client.find_place(
                        query,
                        location=f"{latitude},{longitude}"
                    )
                
                if not place_result or not place_result.get('place_id'):
                    logger.warning(f"Google Places: No place found for {home_name}")
                    # Cache negative result
                    if self.use_cache and self.cache:
                        await self.cache.set(cache_key, None, ttl=86400)  # 1 day
                    return None
            
            place_id = place_result.get('place_id')
            
            # Get place details with reviews and photos
            details = await self.client.get_place_details(
                place_id,
                fields=[
                    'name', 'rating', 'user_ratings_total', 'reviews',
                    'formatted_address', 'formatted_phone_number', 'website', 'photos'
                ]
            )
            
            if not details:
                return None
            
            # Extract photo URL if available
            photo_url = None
            photos = details.get('photos', [])
            if photos and len(photos) > 0:
                photo_reference = photos[0].get('photo_reference')
                if photo_reference:
                    # Generate photo URL from photo_reference
                    try:
                        from config_manager import get_credentials
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
                        else:
                            # Fallback: use backend endpoint
                            photo_url = f"/api/google-places/photo/{photo_reference}"
                    except Exception as e:
                        logger.warning(f"Error generating photo URL: {e}")
            
            # Extract reviews
            reviews = details.get('reviews', [])
            
            # Analyze sentiment
            sentiment_analysis = self._analyze_sentiment_simple(reviews)
            
            # Get Google Places Insights (NEW API features)
            insights_data = None
            try:
                insights_data = await self.client.get_places_insights(place_id)
                logger.info(f"Google Places Insights retrieved for {home_name}: dwell_time={insights_data.get('dwell_time', {}).get('average_dwell_time_minutes')}, repeat_rate={insights_data.get('repeat_visitor_rate', {}).get('repeat_visitor_rate_percent')}")
            except Exception as e:
                logger.warning(f"Failed to get Google Places Insights for {home_name}: {str(e)}")
                # Fallback: try to get individual insights
                try:
                    dwell_time_data = await self.client.calculate_dwell_time(place_id)
                    repeat_rate_data = await self.client.calculate_repeat_visitor_rate(place_id)
                    insights_data = {
                        'dwell_time': dwell_time_data,
                        'repeat_visitor_rate': repeat_rate_data,
                        'footfall_trends': await self.client.get_footfall_trends(place_id),
                        'popular_times': await self.client.get_popular_times(place_id),
                        'visitor_geography': await self.client.get_visitor_geography(place_id)
                    }
                except Exception as e2:
                    logger.warning(f"Failed to get individual Google Places Insights for {home_name}: {str(e2)}")
            
            google_places_data = {
                'place_id': place_id,
                'name': details.get('name'),
                'rating': details.get('rating'),
                'user_ratings_total': details.get('user_ratings_total', 0),
                'reviews': reviews[:10],  # Limit to 10 most recent reviews
                'reviews_count': len(reviews),
                'sentiment_analysis': sentiment_analysis,
                'formatted_address': details.get('formatted_address'),
                'formatted_phone_number': details.get('formatted_phone_number'),
                'website': details.get('website'),
                'photo_url': photo_url,  # Add photo URL
                'photo_reference': photos[0].get('photo_reference') if photos and len(photos) > 0 else None
            }
            
            # Add Google Places Insights (NEW API) if available
            if insights_data:
                google_places_data['insights'] = insights_data
                # Extract key metrics for easy access
                dwell_time = insights_data.get('dwell_time', {})
                repeat_rate = insights_data.get('repeat_visitor_rate', {})
                footfall = insights_data.get('footfall_trends', {})
                popular_times = insights_data.get('popular_times', {})
                summary = insights_data.get('summary', {})
                
                google_places_data['average_dwell_time_minutes'] = dwell_time.get('average_dwell_time_minutes')
                repeat_visitor_rate_percent = repeat_rate.get('repeat_visitor_rate_percent')
                if repeat_visitor_rate_percent is not None:
                    # Store as decimal (0-1) for consistency with matching service
                    google_places_data['repeat_visitor_rate'] = repeat_visitor_rate_percent / 100
                google_places_data['footfall_trend'] = footfall.get('trend_direction')
                google_places_data['popular_times'] = popular_times
                google_places_data['family_engagement_score'] = summary.get('family_engagement_score')
                google_places_data['quality_indicator'] = summary.get('quality_indicator')
                if google_places_data['repeat_visitor_rate']:
                    # Convert percentage to decimal for consistency
                    google_places_data['repeat_visitor_rate'] = google_places_data['repeat_visitor_rate'] / 100
                google_places_data['footfall_trend'] = footfall.get('trend_direction')
                google_places_data['popular_times'] = popular_times
                google_places_data['family_engagement_score'] = summary.get('family_engagement_score')
                google_places_data['quality_indicator'] = summary.get('quality_indicator')
            
            # Cache the result
            if self.use_cache and self.cache:
                await self.cache.set(cache_key, google_places_data, ttl=self.cache_ttl)
            
            return google_places_data
            
        except Exception as e:
            logger.error(f"Error fetching Google Places data for {home_name}: {e}")
            return None
    
    async def enrich_care_home(
        self,
        home: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enrich a single care home with Google Places reviews and sentiment
        
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
        
        google_places_data = await self._fetch_google_places_data(
            home_name=home_name,
            postcode=postcode,
            latitude=latitude,
            longitude=longitude
        )
        
        if google_places_data:
            # Add Google Places data to home
            home["google_places"] = {
                'place_id': google_places_data.get('place_id'),
                'rating': google_places_data.get('rating'),
                'user_ratings_total': google_places_data.get('user_ratings_total', 0),
                'reviews': google_places_data.get('reviews', []),
                'reviews_count': google_places_data.get('reviews_count', 0),
                'sentiment_analysis': google_places_data.get('sentiment_analysis', {}),
                'formatted_address': google_places_data.get('formatted_address'),
                'formatted_phone_number': google_places_data.get('formatted_phone_number'),
                'website': google_places_data.get('website'),
                'photo_url': google_places_data.get('photo_url'),  # Add photo URL
                'photo_reference': google_places_data.get('photo_reference')  # Add photo reference for fallback
            }
            # Also add top-level fields for backward compatibility
            home["google_rating"] = google_places_data.get('rating')
            home["google_review_count"] = google_places_data.get('user_ratings_total', 0)
            home["google_reviews"] = google_places_data.get('reviews', [])
            home["google_sentiment"] = google_places_data.get('sentiment_analysis', {})
        
        return home
    
    async def enrich_care_homes_batch(
        self,
        homes: List[Dict[str, Any]],
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Enrich multiple care homes with Google Places data (with rate limiting)
        
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
                logger.error(f"Error enriching home {i}: {enriched}")
                result.append(homes[i])  # Return original home if enrichment failed
            else:
                result.append(enriched)
        
        return result
    
    async def close(self):
        """Close Google Places client"""
        await self.client.close()

