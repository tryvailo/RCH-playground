"""
Environmental Analysis Module
Calculates noise and pollution levels based on OS Features API data (roads, infrastructure)

Uses proximity to roads, road types, and traffic density as indicators
"""
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path
import math
import asyncio

from .cache_manager import get_cache_manager


class EnvironmentalAnalyzer:
    """
    Analyzes environmental factors (noise and pollution) based on OS Features API data
    
    Uses:
    - Road proximity and types
    - Road density
    - Infrastructure proximity
    """
    
    FEATURES_URL = "https://api.os.uk/features/v1/wfs"
    
    # Road type classifications for noise/pollution estimation
    ROAD_TYPES = {
        'motorway': {'noise_factor': 1.0, 'pollution_factor': 1.0, 'traffic_density': 'very_high'},
        'trunk': {'noise_factor': 0.85, 'pollution_factor': 0.85, 'traffic_density': 'high'},
        'primary': {'noise_factor': 0.70, 'pollution_factor': 0.70, 'traffic_density': 'high'},
        'secondary': {'noise_factor': 0.55, 'pollution_factor': 0.55, 'traffic_density': 'medium'},
        'tertiary': {'noise_factor': 0.40, 'pollution_factor': 0.40, 'traffic_density': 'medium'},
        'residential': {'noise_factor': 0.25, 'pollution_factor': 0.25, 'traffic_density': 'low'},
        'service': {'noise_factor': 0.15, 'pollution_factor': 0.15, 'traffic_density': 'very_low'},
    }
    
    # Distance thresholds (in meters)
    DISTANCE_THRESHOLDS = {
        'very_close': 50,      # High impact
        'close': 100,          # Medium-high impact
        'moderate': 200,       # Medium impact
        'far': 500,           # Low impact
        'very_far': 1000      # Very low impact
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Environmental Analyzer
        
        Args:
            api_key: OS Data Hub API key (optional, loads from config if not provided)
        """
        self.api_key = api_key
        if not self.api_key:
            self._load_from_config()
        
        self.cache = get_cache_manager()
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _load_from_config(self):
        """Load API credentials from config.json"""
        try:
            config_path = Path(__file__).parent.parent / "config.json"
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                    os_config = config.get('os_places', {})
                    self.api_key = os_config.get('api_key')
        except Exception as e:
            print(f"Failed to load OS config: {e}")
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in meters (Haversine formula)"""
        R = 6371000  # Earth radius in meters
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi / 2) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _get_distance_category(self, distance_m: float) -> str:
        """Categorize distance"""
        if distance_m <= self.DISTANCE_THRESHOLDS['very_close']:
            return 'very_close'
        elif distance_m <= self.DISTANCE_THRESHOLDS['close']:
            return 'close'
        elif distance_m <= self.DISTANCE_THRESHOLDS['moderate']:
            return 'moderate'
        elif distance_m <= self.DISTANCE_THRESHOLDS['far']:
            return 'far'
        else:
            return 'very_far'
    
    def _calculate_distance_decay(self, distance_m: float) -> float:
        """
        Calculate distance decay factor for noise/pollution
        Uses inverse square law approximation
        """
        if distance_m <= 0:
            return 1.0
        
        # Base distance for full impact (10 meters)
        base_distance = 10.0
        
        # Decay factor (inverse square with minimum threshold)
        decay = (base_distance / max(distance_m, base_distance)) ** 1.5
        
        # Apply minimum threshold (noise/pollution doesn't completely disappear)
        return max(decay, 0.05)  # Minimum 5% impact even at far distances
    
    async def _fetch_roads_nearby(
        self, 
        lat: float, 
        lon: float, 
        radius_m: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Fetch roads near location using OpenStreetMap Overpass API
        (OS Features API can be used as alternative, but OSM is more accessible)
        Returns empty list if API is unavailable (fallback to estimation)
        """
        # Check cache
        cache_key = f"roads_{lat}_{lon}_{radius_m}"
        cached = self.cache.get('environmental', cache_key)
        if cached:
            return cached
        
        try:
            # Use Overpass API to get roads with shorter timeout
            overpass_url = "https://overpass-api.de/api/interpreter"
            
            # Build query for roads within radius (reduced timeout for faster response)
            query = f"""
            [out:json][timeout:10];
            (
              way["highway"~"^(motorway|trunk|primary|secondary|tertiary|residential|service|unclassified)"]
              (around:{radius_m},{lat},{lon});
            );
            out geom;
            """
            
            # Use shorter timeout to fail fast
            response = await asyncio.wait_for(
                self.client.post(
                    overpass_url,
                    data={"data": query},
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10.0  # 10 second timeout (reduced from 20)
                ),
                timeout=12.0  # Overall timeout including connection
            )
            
            if response.status_code == 200:
                data = response.json()
                roads = []
                
                for element in data.get('elements', []):
                    if element.get('type') == 'way' and 'geometry' in element:
                        tags = element.get('tags', {})
                        highway_type = tags.get('highway', 'unknown')
                        
                        # Calculate distance to nearest point on road
                        min_distance = float('inf')
                        for point in element.get('geometry', []):
                            if 'lat' in point and 'lon' in point:
                                dist = self._calculate_distance(lat, lon, point['lat'], point['lon'])
                                min_distance = min(min_distance, dist)
                        
                        if min_distance < float('inf'):
                            roads.append({
                                'type': highway_type,
                                'name': tags.get('name', 'Unnamed Road'),
                                'distance_m': round(min_distance, 1),
                                'ref': tags.get('ref', ''),
                                'lanes': tags.get('lanes', ''),
                                'maxspeed': tags.get('maxspeed', '')
                            })
                
                # Sort by distance
                roads.sort(key=lambda x: x['distance_m'])
                
                self.cache.set('environmental', cache_key, roads)
                return roads
            else:
                return []
                
        except (httpx.TimeoutException, asyncio.TimeoutError):
            print(f"Timeout fetching roads from Overpass API (location: {lat}, {lon})")
            return []  # Return empty - will use fallback estimation
        except Exception as e:
            print(f"Error fetching roads: {e}")
            return []  # Return empty - will use fallback estimation
    
    async def analyze_noise_level(
        self,
        latitude: float,
        longitude: float,
        radius_m: int = 500
    ) -> Dict[str, Any]:
        """
        Calculate noise level based on nearby roads and infrastructure
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            radius_m: Search radius in meters
            
        Returns:
            Noise analysis with score (0-100) and rating
        """
        # Check cache
        cache_key = f"noise_{latitude}_{longitude}_{radius_m}"
        cached = self.cache.get('environmental', cache_key)
        if cached:
            return cached
        
        try:
            # Fetch nearby roads (simplified - would use OS Features API)
            roads = await self._fetch_roads_nearby(latitude, longitude, radius_m)
            
            # For now, use a simplified calculation based on typical urban patterns
            # In production, this would use actual OS Features API road data
            
            # Calculate noise score based on:
            # 1. Proximity to major roads (estimated)
            # 2. Road density in area
            # 3. Urban vs rural context
            
            # Calculate noise based on actual road data
            noise_score = await self._estimate_noise_from_roads(latitude, longitude, radius_m)
            
            # Categorize noise level
            if noise_score >= 70:
                rating = "Very High"
                description = "High traffic noise expected. Close to major roads or highways."
            elif noise_score >= 55:
                rating = "High"
                description = "Significant traffic noise. Near busy roads or urban center."
            elif noise_score >= 40:
                rating = "Moderate"
                description = "Moderate traffic noise. Typical urban/suburban levels."
            elif noise_score >= 25:
                rating = "Low"
                description = "Low traffic noise. Residential area with limited traffic."
            else:
                rating = "Very Low"
                description = "Very low traffic noise. Quiet residential or rural area."
            
            result = {
                'location': {'latitude': latitude, 'longitude': longitude},
                'noise_score': round(noise_score, 1),
                'rating': rating,
                'description': description,
                'radius_analyzed_m': radius_m,
                'factors': {
                    'major_roads_nearby': noise_score > 50,
                    'urban_area': noise_score > 40,
                    'estimated_traffic_density': 'high' if noise_score > 50 else 'medium' if noise_score > 30 else 'low'
                },
                'recommendations': self._get_noise_recommendations(noise_score),
                'fetched_at': datetime.now().isoformat()
            }
            
            self.cache.set('environmental', cache_key, result)
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'location': {'latitude': latitude, 'longitude': longitude},
                'noise_score': None,
                'rating': 'Unknown',
                'fetched_at': datetime.now().isoformat()
            }
    
    async def _estimate_noise_from_roads(self, lat: float, lon: float, radius_m: int) -> float:
        """
        Estimate noise level based on actual road data
        Falls back to simplified estimation if road data unavailable
        """
        try:
            roads = await self._fetch_roads_nearby(lat, lon, radius_m)
        except Exception as e:
            print(f"Failed to fetch roads, using fallback estimation: {e}")
            roads = []
        
        if not roads:
            # No roads found or API unavailable - use simplified estimation
            # Base on typical UK patterns: urban areas ~40-50, suburban ~25-35, rural ~15-25
            # This is a simplified fallback
            return 35.0  # Default moderate level
        
        noise_contributions = []
        
        for road in roads[:20]:  # Limit to closest 20 roads
            road_type = road.get('type', 'unknown')
            distance = road.get('distance_m', 1000)
            
            # Get road type factors
            road_factors = self.ROAD_TYPES.get(road_type, {
                'noise_factor': 0.30,
                'pollution_factor': 0.30,
                'traffic_density': 'low'
            })
            
            # Calculate contribution based on distance and road type
            distance_decay = self._calculate_distance_decay(distance)
            contribution = road_factors['noise_factor'] * 100 * distance_decay
            
            noise_contributions.append(contribution)
        
        # Sum contributions with diminishing returns
        if noise_contributions:
            # Use square root to prevent over-scoring with many roads
            total_noise = sum(noise_contributions)
            noise_score = min(math.sqrt(total_noise * 2), 100)
        else:
            noise_score = 20.0  # Base level if no major roads
        
        return round(noise_score, 1)
    
    def _estimate_noise_from_location(self, lat: float, lon: float, radius_m: int) -> float:
        """
        Estimate noise level (synchronous version for fallback)
        """
        # This is a fallback - async version should be used
        return 35.0
    
    def _get_noise_recommendations(self, noise_score: float) -> List[str]:
        """Get recommendations based on noise level"""
        recommendations = []
        
        if noise_score >= 60:
            recommendations.append("Consider soundproofing measures for care home")
            recommendations.append("Position bedrooms away from road-facing side")
            recommendations.append("Install double-glazed windows")
        elif noise_score >= 40:
            recommendations.append("Monitor noise levels, especially during peak traffic hours")
            recommendations.append("Consider landscaping to provide noise buffer")
        else:
            recommendations.append("Noise levels are generally acceptable for care home")
        
        return recommendations
    
    async def analyze_pollution_level(
        self,
        latitude: float,
        longitude: float,
        radius_m: int = 500
    ) -> Dict[str, Any]:
        """
        Calculate air pollution level based on nearby roads and traffic
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            radius_m: Search radius in meters
            
        Returns:
            Pollution analysis with score (0-100) and rating
        """
        # Check cache
        cache_key = f"pollution_{latitude}_{longitude}_{radius_m}"
        cached = self.cache.get('environmental', cache_key)
        if cached:
            return cached
        
        try:
            # Pollution is closely related to noise (both from traffic)
            # Use similar methodology but with different weighting
            
            # Fetch nearby roads (would use OS Features API)
            roads = await self._fetch_roads_nearby(latitude, longitude, radius_m)
            
            # Calculate pollution based on actual road data
            pollution_score = await self._estimate_pollution_from_roads(latitude, longitude, radius_m)
            
            # Categorize pollution level
            if pollution_score >= 70:
                rating = "Very High"
                description = "High air pollution expected. Close to major traffic routes."
            elif pollution_score >= 55:
                rating = "High"
                description = "Elevated air pollution. Near busy roads or industrial areas."
            elif pollution_score >= 40:
                rating = "Moderate"
                description = "Moderate air pollution. Typical urban levels."
            elif pollution_score >= 25:
                rating = "Low"
                description = "Low air pollution. Good air quality expected."
            else:
                rating = "Very Low"
                description = "Very low air pollution. Excellent air quality."
            
            result = {
                'location': {'latitude': latitude, 'longitude': longitude},
                'pollution_score': round(pollution_score, 1),
                'rating': rating,
                'description': description,
                'radius_analyzed_m': radius_m,
                'factors': {
                    'major_roads_nearby': pollution_score > 50,
                    'traffic_density': 'high' if pollution_score > 50 else 'medium' if pollution_score > 30 else 'low',
                    'urban_area': pollution_score > 40
                },
                'recommendations': self._get_pollution_recommendations(pollution_score),
                'fetched_at': datetime.now().isoformat()
            }
            
            self.cache.set('environmental', cache_key, result)
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'location': {'latitude': latitude, 'longitude': longitude},
                'pollution_score': None,
                'rating': 'Unknown',
                'fetched_at': datetime.now().isoformat()
            }
    
    async def _estimate_pollution_from_roads(self, lat: float, lon: float, radius_m: int) -> float:
        """
        Estimate pollution level based on actual road data
        Pollution is typically 0.85x of noise level (similar sources but disperses more)
        """
        try:
            # Get noise score first (based on roads)
            noise_score = await self._estimate_noise_from_roads(lat, lon, radius_m)
            
            # Pollution is slightly lower than noise (air disperses more than sound)
            pollution_score = noise_score * 0.85
            
            return round(pollution_score, 1)
        except Exception as e:
            print(f"Error estimating pollution, using fallback: {e}")
            # Fallback to moderate level
            return 30.0
    
    def _get_pollution_recommendations(self, pollution_score: float) -> List[str]:
        """Get recommendations based on pollution level"""
        recommendations = []
        
        if pollution_score >= 60:
            recommendations.append("Consider air filtration systems for care home")
            recommendations.append("Monitor air quality regularly")
            recommendations.append("Position outdoor areas away from road-facing side")
        elif pollution_score >= 40:
            recommendations.append("Air quality is acceptable but monitor during high traffic periods")
            recommendations.append("Consider air quality monitoring")
        else:
            recommendations.append("Air quality is good for care home residents")
        
        return recommendations
    
    async def analyze_environmental(
        self,
        latitude: float,
        longitude: float,
        radius_m: int = 500
    ) -> Dict[str, Any]:
        """
        Comprehensive environmental analysis (noise + pollution)
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            radius_m: Search radius in meters
            
        Returns:
            Combined environmental analysis
        """
        noise = await self.analyze_noise_level(latitude, longitude, radius_m)
        pollution = await self.analyze_pollution_level(latitude, longitude, radius_m)
        
        # Calculate overall environmental score
        if noise.get('noise_score') is not None and pollution.get('pollution_score') is not None:
            overall_score = (noise['noise_score'] + pollution['pollution_score']) / 2
        else:
            overall_score = None
        
        return {
            'location': {'latitude': latitude, 'longitude': longitude},
            'noise': noise,
            'pollution': pollution,
            'overall_environmental_score': round(overall_score, 1) if overall_score else None,
            'overall_rating': self._get_overall_rating(overall_score) if overall_score else 'Unknown',
            'fetched_at': datetime.now().isoformat()
        }
    
    def _get_overall_rating(self, score: float) -> str:
        """Get overall environmental rating"""
        if score >= 70:
            return "Poor"
        elif score >= 55:
            return "Below Average"
        elif score >= 40:
            return "Average"
        elif score >= 25:
            return "Good"
        else:
            return "Excellent"
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

