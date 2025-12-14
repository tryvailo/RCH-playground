"""
Unit tests for Google Places API with caching
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_clients.google_places_client import GooglePlacesAPIClient


class TestGooglePlacesCaching:
    """Test Google Places API caching functionality"""
    
    @pytest.mark.asyncio
    async def test_find_place_with_cache_hit(self):
        """Test find_place returns cached result when available"""
        mock_cache = AsyncMock()
        mock_cache.get = AsyncMock(return_value={"place_id": "test123", "name": "Test Place"})
        mock_cache.set = AsyncMock(return_value=True)
        
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"places": []})
        mock_response.raise_for_status = MagicMock()
        
        with patch('api_clients.google_places_client.get_cache_manager') as mock_get_cache:
            mock_get_cache.return_value = mock_cache
            
            client = GooglePlacesAPIClient(api_key="test_key", use_cache=True)
            client.cache = mock_cache
            client.client = mock_client
            
            # Should return cached result without API call
            result = await client.find_place("Test Place")
            assert result == {"place_id": "test123", "name": "Test Place"}
            mock_client.post.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_find_place_with_cache_miss(self):
        """Test find_place fetches and caches result on cache miss"""
        mock_cache = AsyncMock()
        mock_cache.get = AsyncMock(return_value=None)  # Cache miss
        mock_cache.set = AsyncMock(return_value=True)
        mock_cache._generate_cache_key = MagicMock(return_value="test_key")
        
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={
            "places": [{
                "id": "places/test123",
                "displayName": {"text": "Test Place"},
                "formattedAddress": "123 Test St",
                "rating": 4.5,
                "userRatingCount": 100
            }]
        })
        mock_response.raise_for_status = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        
        with patch('api_clients.google_places_client.get_cache_manager') as mock_get_cache:
            mock_get_cache.return_value = mock_cache
            
            client = GooglePlacesAPIClient(api_key="test_key", use_cache=True)
            client.cache = mock_cache
            client.client = mock_client
            
            result = await client.find_place("Test Place")
            
            # Should have called API
            mock_client.post.assert_called_once()
            # Should have cached the result
            mock_cache.set.assert_called_once()
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_get_place_details_with_cache(self):
        """Test get_place_details uses cache"""
        mock_cache = AsyncMock()
        mock_cache.get = AsyncMock(return_value={"place_id": "test123", "name": "Test Place"})
        mock_cache.set = AsyncMock(return_value=True)
        
        mock_client = AsyncMock()
        
        with patch('api_clients.google_places_client.get_cache_manager') as mock_get_cache:
            mock_get_cache.return_value = mock_cache
            
            client = GooglePlacesAPIClient(api_key="test_key", use_cache=True)
            client.cache = mock_cache
            client.client = mock_client
            
            result = await client.get_place_details("test123")
            assert result == {"place_id": "test123", "name": "Test Place"}
            mock_client.get.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_cache_disabled(self):
        """Test that API calls work when cache is disabled"""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={
            "places": [{
                "id": "places/test123",
                "displayName": {"text": "Test Place"}
            }]
        })
        mock_response.raise_for_status = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        
        client = GooglePlacesAPIClient(api_key="test_key", use_cache=False)
        client.client = mock_client
        
        result = await client.find_place("Test Place")
        assert result is not None
        mock_client.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self):
        """Test cache key generation"""
        client = GooglePlacesAPIClient(api_key="test_key", use_cache=False)
        
        # Test key generation
        key1 = client._get_cache_key("find_place", "Test Place", "TEXT_QUERY")
        key2 = client._get_cache_key("find_place", "Test Place", "TEXT_QUERY")
        key3 = client._get_cache_key("find_place", "Other Place", "TEXT_QUERY")
        
        # Same inputs should generate same key
        assert key1 == key2
        # Different inputs should generate different key
        assert key1 != key3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

