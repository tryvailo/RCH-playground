"""
Tests for ONS and OSM integrations
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import json

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_integrations.ons_loader import ONSLoader
from data_integrations.osm_loader import OSMLoader


class TestONSLoader:
    """Tests for ONSLoader"""
    
    @pytest.fixture
    def mock_loader(self):
        """Create loader with mocked HTTP client"""
        loader = ONSLoader()
        loader.cache = MagicMock()
        loader.cache.get.return_value = None
        loader.cache.set.return_value = True
        return loader
    
    @pytest.mark.asyncio
    async def test_postcode_to_lsoa_success(self, mock_loader):
        """Test successful LSOA lookup"""
        mock_response = {
            "status": 200,
            "result": {
                "postcode": "SW1A 1AA",
                "lsoa": "Westminster 001A",
                "msoa": "Westminster 001",
                "admin_district": "Westminster",
                "region": "London",
                "country": "England",
                "latitude": 51.5014,
                "longitude": -0.1419,
                "codes": {
                    "lsoa": "E01004736",
                    "msoa": "E02000977",
                    "admin_district": "E09000033"
                }
            }
        }
        
        mock_loader.client.get = AsyncMock(return_value=MagicMock(
            status_code=200,
            json=lambda: mock_response
        ))
        
        result = await mock_loader.postcode_to_lsoa("SW1A 1AA")
        
        assert result['lsoa_code'] == "E01004736"
        assert result['local_authority'] == "Westminster"
        assert result['region'] == "London"
        
        await mock_loader.close()
    
    @pytest.mark.asyncio
    async def test_postcode_not_found(self, mock_loader):
        """Test postcode not found handling"""
        mock_loader.client.get = AsyncMock(return_value=MagicMock(
            status_code=404
        ))
        
        result = await mock_loader.postcode_to_lsoa("INVALID")
        
        assert 'error' in result
        assert 'not found' in result['error']
        
        await mock_loader.close()
    
    @pytest.mark.asyncio
    async def test_wellbeing_data(self, mock_loader):
        """Test wellbeing data retrieval"""
        result = await mock_loader.get_wellbeing_data(
            lsoa_code="E01004736",
            local_authority="Westminster"
        )
        
        assert 'indicators' in result
        assert 'happiness' in result['indicators']
        assert 'social_wellbeing_index' in result
        assert result['social_wellbeing_index']['score'] > 0
        
        await mock_loader.close()
    
    def test_wellbeing_index_calculation(self, mock_loader):
        """Test Social Wellbeing Index calculation"""
        indicators = {
            'happiness': 8.0,
            'life_satisfaction': 8.0,
            'anxiety': 2.0,  # Lower is better
            'worthwhile': 8.0
        }
        
        result = mock_loader._calculate_wellbeing_index(indicators)
        
        assert result['score'] > 70  # Should be high with these values
        assert result['rating'] in ['Excellent', 'Good']
    
    @pytest.mark.asyncio
    async def test_full_area_profile(self, mock_loader):
        """Test full area profile generation"""
        # Mock postcode lookup
        mock_loader.client.get = AsyncMock(return_value=MagicMock(
            status_code=200,
            json=lambda: {
                "status": 200,
                "result": {
                    "postcode": "B1 1BB",
                    "lsoa": "Birmingham 001",
                    "admin_district": "Birmingham",
                    "region": "West Midlands",
                    "codes": {"lsoa": "E01008391"}
                }
            }
        ))
        
        result = await mock_loader.get_full_area_profile("B1 1BB")
        
        assert 'geography' in result
        assert 'wellbeing' in result
        assert 'economic' in result
        assert 'demographics' in result
        assert 'summary' in result
        
        await mock_loader.close()


class TestOSMLoader:
    """Tests for OSMLoader"""
    
    @pytest.fixture
    def mock_loader(self):
        """Create loader with mocked components"""
        loader = OSMLoader()
        loader.cache = MagicMock()
        loader.cache.get.return_value = None
        loader.cache.set.return_value = True
        return loader
    
    def test_haversine_distance(self, mock_loader):
        """Test distance calculation"""
        # London to Birmingham roughly 163km
        distance = mock_loader._haversine(51.5074, -0.1278, 52.4862, -1.8904)
        
        assert 160000 < distance < 170000  # meters
    
    def test_haversine_same_point(self, mock_loader):
        """Test distance to same point is 0"""
        distance = mock_loader._haversine(51.5074, -0.1278, 51.5074, -0.1278)
        
        assert distance < 1  # Should be essentially 0
    
    @pytest.mark.asyncio
    async def test_calculate_walk_score(self, mock_loader):
        """Test Walk Score calculation with mocked data"""
        # Mock amenity response
        mock_amenities = {
            'by_category': {
                'grocery': [
                    {'name': 'Tesco', 'distance_m': 200, 'type': 'supermarket'}
                ],
                'healthcare': [
                    {'name': 'Boots', 'distance_m': 150, 'type': 'pharmacy'}
                ],
                'parks': [
                    {'name': 'Victoria Park', 'distance_m': 300, 'type': 'park'}
                ],
                'restaurants': [
                    {'name': 'Cafe', 'distance_m': 100, 'type': 'cafe'}
                ]
            },
            'total_amenities': 4
        }
        
        mock_loader.get_nearby_amenities = AsyncMock(return_value=mock_amenities)
        
        result = await mock_loader.calculate_walk_score(52.4862, -1.8904)
        
        assert 'walk_score' in result
        assert 0 <= result['walk_score'] <= 100
        assert 'rating' in result
        assert 'care_home_relevance' in result
        
        await mock_loader.close()
    
    @pytest.mark.asyncio
    async def test_nearby_amenities_with_categories(self, mock_loader):
        """Test filtered amenity search"""
        mock_response = {
            'elements': [
                {
                    'type': 'node',
                    'lat': 52.4863,
                    'lon': -1.8905,
                    'tags': {'amenity': 'pharmacy', 'name': 'Boots'}
                },
                {
                    'type': 'node',
                    'lat': 52.4865,
                    'lon': -1.8910,
                    'tags': {'amenity': 'hospital', 'name': 'City Hospital'}
                }
            ]
        }
        
        mock_loader._query_overpass = AsyncMock(return_value=mock_response)
        
        result = await mock_loader.get_nearby_amenities(
            52.4862, -1.8904,
            categories=['healthcare']
        )
        
        assert 'by_category' in result
        assert 'healthcare' in result['by_category']
        
        await mock_loader.close()
    
    def test_categorize_amenities(self, mock_loader):
        """Test amenity categorization"""
        elements = [
            {
                'type': 'node',
                'lat': 52.4863,
                'lon': -1.8905,
                'tags': {'amenity': 'pharmacy', 'name': 'Boots'}
            },
            {
                'type': 'node',
                'lat': 52.4870,
                'lon': -1.8920,
                'tags': {'amenity': 'restaurant', 'name': 'Pizza Place'}
            }
        ]
        
        result = mock_loader._categorize_amenities(elements, 52.4862, -1.8904)
        
        assert len(result['healthcare']) == 1
        assert len(result['restaurants']) == 1
        assert result['healthcare'][0]['name'] == 'Boots'
    
    def test_care_home_relevance_scoring(self, mock_loader):
        """Test care home relevance assessment"""
        category_scores = {
            'healthcare': {'score': 80, 'count': 3},
            'parks': {'score': 70, 'count': 2},
            'restaurants': {'score': 60, 'count': 5}
        }
        
        result = mock_loader._assess_care_home_relevance(category_scores)
        
        assert 'score' in result
        assert 'rating' in result
        assert 'healthcare_access' in result
        assert result['healthcare_access'] == 'Good'
    
    @pytest.mark.asyncio
    async def test_infrastructure_report(self, mock_loader):
        """Test infrastructure report generation"""
        mock_response = {
            'elements': [
                {'tags': {'highway': 'bus_stop'}},
                {'tags': {'highway': 'bus_stop'}},
                {'tags': {'highway': 'crossing'}},
                {'tags': {'lit': 'yes'}},
                {'tags': {'amenity': 'bench'}}
            ]
        }
        
        mock_loader._query_overpass = AsyncMock(return_value=mock_response)
        
        result = await mock_loader.get_infrastructure_report(52.4862, -1.8904)
        
        assert 'public_transport' in result
        assert 'pedestrian_safety' in result
        assert 'safety_score' in result
        
        await mock_loader.close()


class TestIntegration:
    """Integration tests (require network access)"""
    
    @pytest.mark.skip(reason="Requires network access")
    @pytest.mark.asyncio
    async def test_real_lsoa_lookup(self):
        """Test real LSOA lookup"""
        async with ONSLoader() as loader:
            result = await loader.postcode_to_lsoa("SW1A 1AA")
            
            assert result['local_authority'] == "Westminster"
            assert result['lsoa_code'].startswith("E01")
    
    @pytest.mark.skip(reason="Requires network access")
    @pytest.mark.asyncio
    async def test_real_walk_score(self):
        """Test real Walk Score calculation"""
        async with OSMLoader() as loader:
            # Westminster coordinates
            result = await loader.calculate_walk_score(51.5014, -0.1419)
            
            assert result['walk_score'] > 50  # Central London should be walkable
            assert 'care_home_relevance' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
