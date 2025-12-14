"""
Tests for OS Places API integration
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import json
import tempfile
import os

# Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_integrations.os_places_loader import OSPlacesLoader
from data_integrations.cache_manager import CacheManager, get_cache_manager


class TestCacheManager:
    """Tests for CacheManager"""
    
    def setup_method(self):
        """Setup test cache with temp database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_cache.db")
        # Reset singleton
        CacheManager._instance = None
        self.cache = CacheManager(self.db_path)
    
    def teardown_method(self):
        """Cleanup temp files"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
        CacheManager._instance = None
    
    def test_set_and_get(self):
        """Test basic set and get operations"""
        data = {"test": "value", "number": 123}
        
        # Set cache
        result = self.cache.set("test_source", "test_key", data)
        assert result is True
        
        # Get cache
        cached = self.cache.get("test_source", "test_key")
        assert cached == data
    
    def test_cache_miss(self):
        """Test cache miss returns None"""
        result = self.cache.get("nonexistent", "key")
        assert result is None
    
    def test_cache_expiration(self):
        """Test that expired entries are not returned"""
        data = {"test": "expired"}
        
        # Set with 0 second TTL (immediately expires)
        self.cache.set("test_source", "expire_key", data, ttl_seconds=0)
        
        # Should not be found (expired)
        import time
        time.sleep(0.1)  # Small delay to ensure expiration
        result = self.cache.get("test_source", "expire_key")
        assert result is None
    
    def test_cache_with_kwargs(self):
        """Test cache key generation with additional kwargs"""
        data = {"test": "with_params"}
        
        self.cache.set("source", "key", data, param1="value1", param2="value2")
        
        # Same params should hit cache
        cached = self.cache.get("source", "key", param1="value1", param2="value2")
        assert cached == data
        
        # Different params should miss
        missed = self.cache.get("source", "key", param1="different")
        assert missed is None
    
    def test_clear_source(self):
        """Test clearing cache by source"""
        self.cache.set("source1", "key1", {"data": 1})
        self.cache.set("source1", "key2", {"data": 2})
        self.cache.set("source2", "key1", {"data": 3})
        
        cleared = self.cache.clear_source("source1")
        assert cleared == 2
        
        # source1 entries should be gone
        assert self.cache.get("source1", "key1") is None
        assert self.cache.get("source1", "key2") is None
        
        # source2 should still exist
        assert self.cache.get("source2", "key1") == {"data": 3}
    
    def test_get_stats(self):
        """Test cache statistics"""
        self.cache.set("os_places", "postcode1", {"test": 1})
        self.cache.set("os_places", "postcode2", {"test": 2})
        self.cache.set("ons", "lsoa1", {"test": 3})
        
        # Access one entry to increment hit count
        self.cache.get("os_places", "postcode1")
        
        stats = self.cache.get_stats()
        
        assert stats['total_entries'] == 3
        assert 'os_places' in stats['by_source']
        assert stats['by_source']['os_places']['count'] == 2
        assert stats['by_source']['os_places']['total_hits'] >= 1


class TestOSPlacesLoader:
    """Tests for OSPlacesLoader"""
    
    @pytest.fixture
    def mock_loader(self):
        """Create loader with mocked HTTP client"""
        with patch.object(OSPlacesLoader, '_load_from_config'):
            loader = OSPlacesLoader(api_key="test_key")
            return loader
    
    @pytest.mark.asyncio
    async def test_get_coordinates_success(self, mock_loader):
        """Test successful coordinate lookup"""
        mock_response = {
            "results": [
                {
                    "DPA": {
                        "UPRN": "100071417680",
                        "ADDRESS": "Test Address",
                        "POSTCODE": "SW1A 1AA",
                        "LAT": 51.5014,
                        "LNG": -0.1419
                    }
                }
            ]
        }
        
        # Mock HTTP response
        mock_loader.client.get = AsyncMock(return_value=MagicMock(
            status_code=200,
            json=lambda: mock_response
        ))
        
        # Mock cache
        mock_loader.cache = MagicMock()
        mock_loader.cache.get.return_value = None
        mock_loader.cache.set.return_value = True
        
        coords = await mock_loader.get_coordinates("SW1A 1AA")
        
        assert coords is not None
        assert coords['latitude'] == 51.5014
        assert coords['longitude'] == -0.1419
        
        await mock_loader.close()
    
    @pytest.mark.asyncio
    async def test_get_coordinates_not_found(self, mock_loader):
        """Test coordinate lookup for non-existent postcode"""
        mock_loader.client.get = AsyncMock(return_value=MagicMock(
            status_code=404,
            text="Not found"
        ))
        
        mock_loader.cache = MagicMock()
        mock_loader.cache.get.return_value = None
        
        coords = await mock_loader.get_coordinates("INVALID")
        
        assert coords is None
        
        await mock_loader.close()
    
    @pytest.mark.asyncio
    async def test_cache_hit(self, mock_loader):
        """Test that cached data is returned without API call"""
        cached_data = {
            "postcode": "SW1A 1AA",
            "centroid": {"latitude": 51.5, "longitude": -0.14}
        }
        
        mock_loader.cache = MagicMock()
        mock_loader.cache.get.return_value = cached_data
        
        # Mock the HTTP client to verify it's not called
        mock_loader.client.get = AsyncMock()
        
        result = await mock_loader.get_address_by_postcode("SW1A 1AA")
        
        assert result == cached_data
        mock_loader.client.get.assert_not_called()
        
        await mock_loader.close()
    
    @pytest.mark.asyncio
    async def test_no_api_key(self):
        """Test behavior when API key is not configured"""
        with patch.object(OSPlacesLoader, '_load_from_config'):
            loader = OSPlacesLoader(api_key=None)
            loader.cache = MagicMock()
            loader.cache.get.return_value = None
            
            result = await loader.get_address_by_postcode("SW1A 1AA")
            
            assert 'error' in result
            assert 'not configured' in result['error']
            
            await loader.close()
    
    @pytest.mark.asyncio
    async def test_batch_get_coordinates(self, mock_loader):
        """Test batch coordinate lookup"""
        postcodes = ["SW1A 1AA", "B1 1BB"]
        
        # Mock get_coordinates to return test data
        async def mock_get_coords(postcode):
            if postcode == "SW1A1AA":  # Normalized
                return {"latitude": 51.5, "longitude": -0.14}
            elif postcode == "B11BB":
                return {"latitude": 52.5, "longitude": -1.9}
            return None
        
        mock_loader.get_coordinates = mock_get_coords
        
        results = await mock_loader.batch_get_coordinates(postcodes)
        
        assert len(results) == 2
        
        await mock_loader.close()


class TestOSPlacesIntegration:
    """Integration tests (require API key)"""
    
    @pytest.mark.skip(reason="Requires real API key")
    @pytest.mark.asyncio
    async def test_real_api_call(self):
        """Test real API call (manual run only)"""
        async with OSPlacesLoader() as loader:
            result = await loader.get_address_by_postcode("SW1A 1AA")
            
            assert 'addresses' in result
            assert len(result['addresses']) > 0
            
            first = result['addresses'][0]
            assert first.get('postcode') == "SW1A 1AA"
            assert first.get('latitude') is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
