"""
NHSBSA (NHS Business Services Authority) Data Loader
Provides access to English Prescribing Dataset (EPD)

API Documentation: https://opendata.nhsbsa.net/pages/api-docs
"""
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json
from pathlib import Path
import asyncio

from .cache_manager import get_cache_manager
from .proximity_matcher import ProximityMatcher, GeoPoint, create_proximity_index


class NHSBSALoader:
    """
    NHSBSA Open Data API Client
    
    Provides:
    - GP Practice prescribing data
    - Medication statistics by area
    - Health profile analysis
    - Proximity matching to care homes
    """
    
    # NHSBSA Open Data endpoints (no API key required)
    BASE_URL = "https://opendata.nhsbsa.net/api/3/action"
    
    # Postcodes.io for coordinate lookup
    POSTCODE_IO_URL = "https://api.postcodes.io/postcodes"
    
    # Key BNF (British National Formulary) categories for care homes
    CARE_HOME_RELEVANT_BNF = {
        'dementia': ['0411', '0412'],  # Drugs for dementia
        'pain': ['0407'],  # Analgesics
        'diabetes': ['0601'],  # Drugs for diabetes
        'cardiovascular': ['0201', '0202', '0203', '0204', '0205', '0206'],
        'respiratory': ['0301', '0302', '0303'],
        'mental_health': ['0401', '0402', '0403'],
        'antibiotics': ['0501'],
        'nutrition': ['0906', '0907'],  # Vitamins, nutrition
        'incontinence': ['0704'],
        'pressure_sores': ['1301']  # Skin
    }
    
    def __init__(self):
        """Initialize NHSBSA loader"""
        self.cache = get_cache_manager()
        self.client = httpx.AsyncClient(timeout=60.0)
        self._gp_practices_index: Optional[ProximityMatcher] = None
    
    async def get_gp_practices(
        self,
        postcode: Optional[str] = None,
        local_authority: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get GP practices, optionally filtered by area
        
        Uses NHS Digital ODS API for practice data
        """
        cache_key = f"gp_{postcode or local_authority or 'all'}"
        cached = self.cache.get('nhsbsa', cache_key, endpoint='practices')
        if cached:
            return cached
        
        # For now, return mock data structure
        # Real implementation would query NHS ODS API
        practices = await self._fetch_mock_practices(postcode, limit)
        
        self.cache.set('nhsbsa', cache_key, practices, endpoint='practices')
        return practices
    
    async def _fetch_mock_practices(
        self, 
        postcode: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Fetch mock GP practice data for development"""
        # Get coordinates from postcode
        coords = None
        if postcode:
            coords = await self._get_postcode_coordinates(postcode)
        
        # Generate mock practices around the coordinates
        practices = []
        base_lat = coords['latitude'] if coords else 52.4862
        base_lon = coords['longitude'] if coords else -1.8904
        
        import random
        random.seed(42)  # Reproducible
        
        for i in range(min(limit, 20)):
            lat_offset = random.uniform(-0.05, 0.05)
            lon_offset = random.uniform(-0.05, 0.05)
            
            practices.append({
                'practice_code': f'Y{10000 + i}',
                'practice_name': f'Medical Practice {i + 1}',
                'address_1': f'{random.randint(1, 200)} High Street',
                'postcode': postcode or 'B1 1BB',
                'latitude': base_lat + lat_offset,
                'longitude': base_lon + lon_offset,
                'patients_registered': random.randint(3000, 15000),
                'accepting_patients': random.choice([True, True, True, False])
            })
        
        return practices
    
    async def _get_postcode_coordinates(self, postcode: str) -> Optional[Dict[str, float]]:
        """Get coordinates for a postcode"""
        postcode = postcode.upper().strip().replace(" ", "")
        
        try:
            response = await self.client.get(f"{self.POSTCODE_IO_URL}/{postcode}")
            if response.status_code == 200:
                data = response.json()
                result = data.get('result', {})
                return {
                    'latitude': result.get('latitude'),
                    'longitude': result.get('longitude')
                }
        except Exception as e:
            print(f"Postcode lookup error: {e}")
        
        return None
    
    async def get_prescribing_data(
        self,
        practice_code: Optional[str] = None,
        bnf_code: Optional[str] = None,
        year_month: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get prescribing data from NHSBSA
        
        Args:
            practice_code: GP Practice code
            bnf_code: BNF code for medication category
            year_month: Format YYYYMM
            
        Returns:
            Prescribing statistics
        """
        # Default to recent month
        if not year_month:
            now = datetime.now()
            # Data is usually 2-3 months behind
            data_date = now - timedelta(days=90)
            year_month = data_date.strftime('%Y%m')
        
        cache_key = f"prescribing_{practice_code or 'all'}_{bnf_code or 'all'}_{year_month}"
        cached = self.cache.get('nhsbsa', cache_key, endpoint='prescribing')
        if cached:
            return cached
        
        # Query NHSBSA API
        try:
            # The actual API endpoint for prescribing data
            # This would query the real EPD dataset
            result = await self._fetch_prescribing_data(practice_code, bnf_code, year_month)
            
            self.cache.set('nhsbsa', cache_key, result, endpoint='prescribing')
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'practice_code': practice_code,
                'bnf_code': bnf_code
            }
    
    async def _fetch_prescribing_data(
        self,
        practice_code: Optional[str],
        bnf_code: Optional[str],
        year_month: str
    ) -> Dict[str, Any]:
        """Fetch prescribing data (mock for development)"""
        import random
        random.seed(hash(f"{practice_code}{bnf_code}{year_month}"))
        
        # Generate realistic mock data
        items = random.randint(100, 5000)
        cost = items * random.uniform(2, 15)
        
        return {
            'year_month': year_month,
            'practice_code': practice_code,
            'bnf_code': bnf_code,
            'items': items,
            'actual_cost': round(cost, 2),
            'quantity': items * random.randint(20, 90),
            'data_source': 'mock'  # Would be 'NHSBSA EPD' in production
        }
    
    async def get_area_health_profile(
        self,
        postcode: str,
        radius_km: float = 5.0
    ) -> Dict[str, Any]:
        """
        Get health profile for an area based on prescribing data
        
        Uses prescribing patterns from nearby GP practices to build
        a health profile of the area.
        
        Args:
            postcode: Center postcode
            radius_km: Search radius
            
        Returns:
            Area health profile with prescribing insights
        """
        cache_key = f"health_profile_{postcode}_{radius_km}"
        cached = self.cache.get('nhsbsa', cache_key, endpoint='health_profile')
        if cached:
            return cached
        
        # Get coordinates
        coords = await self._get_postcode_coordinates(postcode)
        if not coords:
            return {
                'error': 'Could not resolve postcode',
                'postcode': postcode
            }
        
        # Get nearby GP practices
        practices = await self.get_gp_practices(postcode, limit=20)
        
        # Build proximity index
        matcher = create_proximity_index(practices)
        nearby = matcher.find_within_radius(
            coords['latitude'], 
            coords['longitude'],
            radius_km
        )
        
        if not nearby:
            return {
                'error': 'No GP practices found in area',
                'postcode': postcode,
                'radius_km': radius_km
            }
        
        # Aggregate health data from nearby practices
        health_profile = await self._build_health_profile(nearby, coords)
        
        self.cache.set('nhsbsa', cache_key, health_profile, endpoint='health_profile')
        return health_profile
    
    async def _build_health_profile(
        self,
        nearby_practices: List[Dict[str, Any]],
        coords: Dict[str, float]
    ) -> Dict[str, Any]:
        """Build health profile from nearby practices"""
        import random
        
        # Calculate totals
        total_patients = sum(
            p.get('data', {}).get('patients_registered', 5000) 
            for p in nearby_practices
        )
        
        # Generate health indicators (mock for development)
        # In production, these would come from actual prescribing data
        random.seed(int(coords['latitude'] * 1000))
        
        health_indicators = {}
        for category, bnf_codes in self.CARE_HOME_RELEVANT_BNF.items():
            # Items per 1000 patients (normalized)
            items_per_1000 = random.uniform(10, 150)
            national_avg = random.uniform(30, 100)
            
            vs_national = ((items_per_1000 - national_avg) / national_avg) * 100
            
            health_indicators[category] = {
                'items_per_1000_patients': round(items_per_1000, 1),
                'national_average': round(national_avg, 1),
                'vs_national_percent': round(vs_national, 1),
                'trend': random.choice(['increasing', 'stable', 'decreasing']),
                'significance': 'Higher than average' if vs_national > 10 else 'Lower than average' if vs_national < -10 else 'Average'
            }
        
        # Top medications (mock)
        top_medications = [
            {'name': 'Paracetamol 500mg tablets', 'items': random.randint(5000, 15000)},
            {'name': 'Omeprazole 20mg capsules', 'items': random.randint(3000, 10000)},
            {'name': 'Amlodipine 5mg tablets', 'items': random.randint(2000, 8000)},
            {'name': 'Metformin 500mg tablets', 'items': random.randint(2000, 7000)},
            {'name': 'Simvastatin 40mg tablets', 'items': random.randint(1500, 6000)},
            {'name': 'Ramipril 5mg capsules', 'items': random.randint(1500, 5000)},
            {'name': 'Levothyroxine 50mcg tablets', 'items': random.randint(1000, 4000)},
            {'name': 'Bisoprolol 2.5mg tablets', 'items': random.randint(1000, 4000)},
            {'name': 'Aspirin 75mg tablets', 'items': random.randint(1000, 3500)},
            {'name': 'Salbutamol 100mcg inhaler', 'items': random.randint(800, 3000)}
        ]
        top_medications.sort(key=lambda x: x['items'], reverse=True)
        
        # Calculate health index (0-100)
        health_index = self._calculate_health_index(health_indicators)
        
        return {
            'location': {
                'latitude': coords['latitude'],
                'longitude': coords['longitude']
            },
            'practices_analyzed': len(nearby_practices),
            'total_patients': total_patients,
            'nearest_practice': nearby_practices[0] if nearby_practices else None,
            'health_indicators': health_indicators,
            'top_medications': top_medications[:10],
            'health_index': health_index,
            'care_home_considerations': self._get_care_home_considerations(health_indicators),
            'data_period': (datetime.now() - timedelta(days=90)).strftime('%Y-%m'),
            'methodology': 'Based on GP practice prescribing patterns in the area',
            'fetched_at': datetime.now().isoformat()
        }
    
    def _calculate_health_index(self, indicators: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Calculate composite health index for the area
        
        Higher score = healthier population (less chronic disease prescribing)
        """
        # Weight different categories
        weights = {
            'dementia': 0.15,
            'cardiovascular': 0.15,
            'diabetes': 0.15,
            'mental_health': 0.15,
            'respiratory': 0.10,
            'pain': 0.10,
            'antibiotics': 0.10,
            'nutrition': 0.05,
            'incontinence': 0.03,
            'pressure_sores': 0.02
        }
        
        # Lower prescribing relative to average = higher score
        weighted_sum = 0
        for category, weight in weights.items():
            if category in indicators:
                vs_national = indicators[category].get('vs_national_percent', 0)
                # Invert: lower prescribing = higher score
                category_score = max(0, min(100, 50 - vs_national))
                weighted_sum += category_score * weight
        
        score = round(weighted_sum, 1)
        
        # Determine rating
        if score >= 70:
            rating = 'Good'
            interpretation = 'Area shows lower chronic disease prescribing than average'
        elif score >= 50:
            rating = 'Average'
            interpretation = 'Area has typical prescribing patterns'
        elif score >= 30:
            rating = 'Below Average'
            interpretation = 'Area shows higher chronic disease prescribing'
        else:
            rating = 'Needs Attention'
            interpretation = 'Area has significantly higher health needs'
        
        return {
            'score': score,
            'rating': rating,
            'interpretation': interpretation,
            'percentile': self._estimate_percentile(score)
        }
    
    def _estimate_percentile(self, score: float) -> int:
        """Estimate national percentile from score"""
        if score >= 80:
            return 90
        elif score >= 70:
            return 75
        elif score >= 60:
            return 60
        elif score >= 50:
            return 45
        elif score >= 40:
            return 30
        else:
            return 15
    
    def _get_care_home_considerations(
        self, 
        indicators: Dict[str, Dict]
    ) -> List[Dict[str, str]]:
        """Get care home specific considerations from health data"""
        considerations = []
        
        # Dementia
        dementia = indicators.get('dementia', {})
        if dementia.get('vs_national_percent', 0) > 15:
            considerations.append({
                'category': 'Dementia Care',
                'finding': 'Area has higher dementia medication prescribing',
                'implication': 'Care homes may need strong dementia care capabilities',
                'priority': 'high'
            })
        
        # Diabetes
        diabetes = indicators.get('diabetes', {})
        if diabetes.get('vs_national_percent', 0) > 10:
            considerations.append({
                'category': 'Diabetes Management',
                'finding': 'Higher diabetes prevalence in the area',
                'implication': 'Care homes should have experience with diabetes care',
                'priority': 'medium'
            })
        
        # Cardiovascular
        cardio = indicators.get('cardiovascular', {})
        if cardio.get('vs_national_percent', 0) > 10:
            considerations.append({
                'category': 'Cardiovascular Care',
                'finding': 'Higher cardiovascular medication use',
                'implication': 'Nursing homes may be more appropriate for complex cases',
                'priority': 'medium'
            })
        
        # Mental Health
        mental = indicators.get('mental_health', {})
        if mental.get('vs_national_percent', 0) > 15:
            considerations.append({
                'category': 'Mental Health Support',
                'finding': 'Higher mental health medication prescribing',
                'implication': 'Look for homes with mental health trained staff',
                'priority': 'high'
            })
        
        # If no specific findings
        if not considerations:
            considerations.append({
                'category': 'General',
                'finding': 'Area has typical health profile',
                'implication': 'Standard care requirements expected',
                'priority': 'low'
            })
        
        return considerations
    
    async def find_nearest_practices_to_care_home(
        self,
        care_home_lat: float,
        care_home_lon: float,
        max_distance_km: float = 5.0,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Find nearest GP practices to a care home
        
        Useful for understanding healthcare access for residents
        """
        cache_key = f"nearest_{care_home_lat:.4f},{care_home_lon:.4f}"
        cached = self.cache.get('nhsbsa', cache_key, endpoint='nearest')
        if cached:
            return cached
        
        # Get practices in area (will be cached)
        # Use approximate postcode based on coordinates
        practices = await self.get_gp_practices(limit=50)
        
        # Build index and find nearest
        matcher = create_proximity_index(practices)
        nearest = matcher.find_nearest(
            care_home_lat, 
            care_home_lon,
            max_results=max_results,
            max_distance_km=max_distance_km
        )
        
        result = {
            'care_home_location': {
                'latitude': care_home_lat,
                'longitude': care_home_lon
            },
            'search_radius_km': max_distance_km,
            'practices_found': len(nearest),
            'nearest_practices': nearest,
            'healthcare_access_rating': self._rate_healthcare_access(nearest),
            'fetched_at': datetime.now().isoformat()
        }
        
        self.cache.set('nhsbsa', cache_key, result, endpoint='nearest')
        return result
    
    def _rate_healthcare_access(self, practices: List[Dict]) -> Dict[str, Any]:
        """Rate healthcare access based on nearby practices"""
        if not practices:
            return {
                'rating': 'Poor',
                'score': 20,
                'description': 'No GP practices found within search radius'
            }
        
        nearest_dist = practices[0]['distance_km']
        practice_count = len(practices)
        
        # Score based on nearest practice and count
        if nearest_dist <= 1.0 and practice_count >= 3:
            return {
                'rating': 'Excellent',
                'score': 95,
                'description': f'Multiple GP practices within easy reach, nearest {nearest_dist}km'
            }
        elif nearest_dist <= 2.0 and practice_count >= 2:
            return {
                'rating': 'Good',
                'score': 75,
                'description': f'Good GP access, nearest practice {nearest_dist}km'
            }
        elif nearest_dist <= 5.0:
            return {
                'rating': 'Adequate',
                'score': 55,
                'description': f'GP practice accessible at {nearest_dist}km'
            }
        else:
            return {
                'rating': 'Limited',
                'score': 35,
                'description': f'Nearest GP practice is {nearest_dist}km away'
            }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
