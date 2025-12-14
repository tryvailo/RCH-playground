"""
Tests for NHSBSA integration and proximity matching
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_integrations.nhsbsa_loader import NHSBSALoader
from data_integrations.proximity_matcher import ProximityMatcher, GeoPoint, create_proximity_index


class TestProximityMatcher:
    """Tests for ProximityMatcher"""
    
    def setup_method(self):
        """Setup test matcher"""
        self.matcher = ProximityMatcher()
    
    def test_haversine_distance(self):
        """Test Haversine distance calculation"""
        # London to Birmingham: ~163km
        dist = ProximityMatcher.haversine_distance(51.5074, -0.1278, 52.4862, -1.8904)
        assert 160 < dist < 170
    
    def test_haversine_same_point(self):
        """Test distance to same point is 0"""
        dist = ProximityMatcher.haversine_distance(51.5074, -0.1278, 51.5074, -0.1278)
        assert dist < 0.001
    
    def test_add_entity(self):
        """Test adding entities"""
        point = GeoPoint(lat=52.4862, lon=-1.8904, id="test1", name="Test Point")
        self.matcher.add_entity(point)
        
        results = self.matcher.find_nearest(52.4862, -1.8904, max_results=1)
        assert len(results) == 1
        assert results[0]['id'] == "test1"
    
    def test_find_nearest(self):
        """Test finding nearest entities"""
        # Add points at various distances
        self.matcher.add_entity(GeoPoint(lat=52.4862, lon=-1.8904, id="close", name="Close"))
        self.matcher.add_entity(GeoPoint(lat=52.5, lon=-1.9, id="medium", name="Medium"))
        self.matcher.add_entity(GeoPoint(lat=53.0, lon=-2.0, id="far", name="Far"))
        
        results = self.matcher.find_nearest(52.4862, -1.8904, max_results=3)
        
        assert len(results) == 3
        assert results[0]['id'] == "close"  # Closest first
        assert results[0]['distance_km'] < results[1]['distance_km']
    
    def test_find_within_radius(self):
        """Test finding entities within radius"""
        self.matcher.add_entity(GeoPoint(lat=52.4862, lon=-1.8904, id="close", name="Close"))
        self.matcher.add_entity(GeoPoint(lat=52.49, lon=-1.89, id="near", name="Near"))
        self.matcher.add_entity(GeoPoint(lat=53.0, lon=-2.0, id="far", name="Far"))
        
        results = self.matcher.find_within_radius(52.4862, -1.8904, radius_km=5)
        
        # Only close and near should be within 5km
        assert len(results) == 2
        assert all(r['distance_km'] <= 5 for r in results)
    
    def test_batch_find_nearest(self):
        """Test batch finding"""
        self.matcher.add_entity(GeoPoint(lat=52.4862, lon=-1.8904, id="p1", name="Point 1"))
        self.matcher.add_entity(GeoPoint(lat=51.5074, lon=-0.1278, id="p2", name="Point 2"))
        
        points = [
            (52.4862, -1.8904),  # Near Point 1
            (51.5074, -0.1278)   # Near Point 2
        ]
        
        results = self.matcher.batch_find_nearest(points, max_results=1)
        
        assert len(results) == 2
        assert results[(52.4862, -1.8904)][0]['id'] == "p1"
        assert results[(51.5074, -0.1278)][0]['id'] == "p2"


class TestCreateProximityIndex:
    """Tests for create_proximity_index helper"""
    
    def test_create_index_from_dicts(self):
        """Test creating index from list of dicts"""
        entities = [
            {'id': '1', 'name': 'Entity 1', 'latitude': 52.4862, 'longitude': -1.8904},
            {'id': '2', 'name': 'Entity 2', 'latitude': 51.5074, 'longitude': -0.1278}
        ]
        
        matcher = create_proximity_index(entities)
        
        results = matcher.find_nearest(52.4862, -1.8904, max_results=2)
        assert len(results) == 2
    
    def test_create_index_with_custom_keys(self):
        """Test with custom key names"""
        entities = [
            {'practice_code': 'Y00001', 'practice_name': 'GP 1', 'lat': 52.4862, 'lon': -1.8904}
        ]
        
        matcher = create_proximity_index(
            entities,
            lat_key='lat',
            lon_key='lon',
            id_key='practice_code',
            name_key='practice_name'
        )
        
        results = matcher.find_nearest(52.4862, -1.8904, max_results=1)
        assert results[0]['id'] == 'Y00001'
        assert results[0]['name'] == 'GP 1'
    
    def test_handles_missing_coordinates(self):
        """Test handling of entities without coordinates"""
        entities = [
            {'id': '1', 'name': 'Has coords', 'latitude': 52.4862, 'longitude': -1.8904},
            {'id': '2', 'name': 'No coords'},  # Missing lat/lon
            {'id': '3', 'name': 'Partial', 'latitude': 52.5}  # Missing lon
        ]
        
        matcher = create_proximity_index(entities)
        
        results = matcher.find_nearest(52.4862, -1.8904, max_results=10)
        assert len(results) == 1  # Only the one with full coords


class TestNHSBSALoader:
    """Tests for NHSBSALoader"""
    
    @pytest.fixture
    def mock_loader(self):
        """Create loader with mocked components"""
        loader = NHSBSALoader()
        loader.cache = MagicMock()
        loader.cache.get.return_value = None
        loader.cache.set.return_value = True
        return loader
    
    @pytest.mark.asyncio
    async def test_get_postcode_coordinates(self, mock_loader):
        """Test postcode to coordinates conversion"""
        mock_response = {
            "status": 200,
            "result": {
                "postcode": "B1 1BB",
                "latitude": 52.4862,
                "longitude": -1.8904
            }
        }
        
        mock_loader.client.get = AsyncMock(return_value=MagicMock(
            status_code=200,
            json=lambda: mock_response
        ))
        
        coords = await mock_loader._get_postcode_coordinates("B1 1BB")
        
        assert coords['latitude'] == 52.4862
        assert coords['longitude'] == -1.8904
        
        await mock_loader.close()
    
    @pytest.mark.asyncio
    async def test_get_gp_practices(self, mock_loader):
        """Test GP practices retrieval"""
        mock_loader.client.get = AsyncMock(return_value=MagicMock(
            status_code=200,
            json=lambda: {"status": 200, "result": {"latitude": 52.4862, "longitude": -1.8904}}
        ))
        
        practices = await mock_loader.get_gp_practices("B1 1BB", limit=10)
        
        assert len(practices) <= 10
        assert all('practice_code' in p for p in practices)
        assert all('latitude' in p for p in practices)
        
        await mock_loader.close()
    
    @pytest.mark.asyncio
    async def test_area_health_profile(self, mock_loader):
        """Test area health profile generation"""
        mock_loader.client.get = AsyncMock(return_value=MagicMock(
            status_code=200,
            json=lambda: {"status": 200, "result": {"latitude": 52.4862, "longitude": -1.8904}}
        ))
        
        profile = await mock_loader.get_area_health_profile("B1 1BB", radius_km=5.0)
        
        assert 'health_indicators' in profile
        assert 'health_index' in profile
        assert 'care_home_considerations' in profile
        assert 'top_medications' in profile
        
        await mock_loader.close()
    
    def test_calculate_health_index(self, mock_loader):
        """Test health index calculation"""
        indicators = {
            'dementia': {'vs_national_percent': 10},
            'cardiovascular': {'vs_national_percent': -5},
            'diabetes': {'vs_national_percent': 0},
            'mental_health': {'vs_national_percent': 5}
        }
        
        result = mock_loader._calculate_health_index(indicators)
        
        assert 'score' in result
        assert 'rating' in result
        assert 0 <= result['score'] <= 100
    
    def test_care_home_considerations_high_dementia(self, mock_loader):
        """Test care home considerations with high dementia"""
        indicators = {
            'dementia': {'vs_national_percent': 25}
        }
        
        considerations = mock_loader._get_care_home_considerations(indicators)
        
        assert len(considerations) >= 1
        dementia_consideration = next(
            (c for c in considerations if c['category'] == 'Dementia Care'),
            None
        )
        assert dementia_consideration is not None
        assert dementia_consideration['priority'] == 'high'
    
    @pytest.mark.asyncio
    async def test_find_nearest_practices(self, mock_loader):
        """Test finding nearest GP practices to a location"""
        mock_loader.get_gp_practices = AsyncMock(return_value=[
            {'practice_code': 'Y00001', 'latitude': 52.4862, 'longitude': -1.8904, 'practice_name': 'GP 1'},
            {'practice_code': 'Y00002', 'latitude': 52.49, 'longitude': -1.89, 'practice_name': 'GP 2'}
        ])
        
        result = await mock_loader.find_nearest_practices_to_care_home(
            care_home_lat=52.4862,
            care_home_lon=-1.8904,
            max_distance_km=5.0
        )
        
        assert 'nearest_practices' in result
        assert 'healthcare_access_rating' in result
        
        await mock_loader.close()
    
    def test_healthcare_access_rating(self, mock_loader):
        """Test healthcare access rating calculation"""
        # Excellent access
        practices = [{'distance_km': 0.5}, {'distance_km': 1.0}, {'distance_km': 2.0}]
        rating = mock_loader._rate_healthcare_access(practices)
        assert rating['rating'] == 'Excellent'
        
        # Limited access
        practices = [{'distance_km': 8.0}]
        rating = mock_loader._rate_healthcare_access(practices)
        assert rating['rating'] == 'Limited'
        
        # No practices
        rating = mock_loader._rate_healthcare_access([])
        assert rating['rating'] == 'Poor'


class TestIntegration:
    """Integration tests (require network)"""
    
    @pytest.mark.skip(reason="Requires network access")
    @pytest.mark.asyncio
    async def test_real_health_profile(self):
        """Test real health profile generation"""
        async with NHSBSALoader() as loader:
            profile = await loader.get_area_health_profile("B1 1BB", radius_km=5.0)
            
            assert profile['practices_analyzed'] > 0
            assert 'health_index' in profile


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
