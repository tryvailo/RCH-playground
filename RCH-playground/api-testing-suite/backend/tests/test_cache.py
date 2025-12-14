"""
Unit tests for Redis cache functionality
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.cache import CacheManager, get_cache_manager


class TestCacheManager:
    """Test CacheManager class"""
    
    @pytest.mark.asyncio
    async def test_cache_disabled_when_redis_unavailable(self):
        """Test that cache is disabled when Redis is unavailable"""
        with patch('utils.cache.redis', None):
            cache = CacheManager(enabled=True)
            assert cache.enabled is False
    
    @pytest.mark.asyncio
    async def test_get_cache_key_generation(self):
        """Test cache key generation"""
        cache = CacheManager(enabled=False)
        
        # Test key generation without Redis
        key = cache._generate_cache_key("test", "arg1", "arg2", param1="value1")
        assert key.startswith("test:")
        assert len(key) > 0
    
    @pytest.mark.asyncio
    async def test_get_none_when_cache_disabled(self):
        """Test that get returns None when cache is disabled"""
        cache = CacheManager(enabled=False)
        result = await cache.get("test_key")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_set_false_when_cache_disabled(self):
        """Test that set returns False when cache is disabled"""
        cache = CacheManager(enabled=False)
        result = await cache.set("test_key", {"test": "value"}, ttl=60)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_or_set_with_disabled_cache(self):
        """Test get_or_set when cache is disabled"""
        cache = CacheManager(enabled=False)
        
        async def fetch_func():
            return {"data": "test"}
        
        result = await cache.get_or_set("test_key", fetch_func, ttl=60)
        assert result == {"data": "test"}
    
    @pytest.mark.asyncio
    async def test_cache_operations_with_mock_redis(self):
        """Test cache operations with mocked Redis"""
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_redis.get = AsyncMock(return_value='{"test": "value"}')
        mock_redis.setex = AsyncMock(return_value=True)
        mock_redis.delete = AsyncMock(return_value=1)
        mock_redis.exists = AsyncMock(return_value=1)
        mock_redis.keys = AsyncMock(return_value=["key1", "key2"])
        mock_redis.info = AsyncMock(return_value={"used_memory_human": "1MB"})
        mock_redis.close = AsyncMock()
        
        with patch('utils.cache.redis') as mock_redis_module:
            mock_redis_module.Redis = MagicMock(return_value=mock_redis)
            
            cache = CacheManager(enabled=True)
            cache.redis_client = mock_redis
            
            # Test get
            result = await cache.get("test_key")
            assert result == {"test": "value"}
            mock_redis.get.assert_called_once()
            
            # Test set
            result = await cache.set("test_key", {"test": "value"}, ttl=60)
            assert result is True
            mock_redis.setex.assert_called_once()
            
            # Test delete
            result = await cache.delete("test_key")
            assert result is True
            mock_redis.delete.assert_called_once()
            
            # Test exists
            result = await cache.exists("test_key")
            assert result is True
            mock_redis.exists.assert_called_once()
            
            # Test get_all_keys
            keys = await cache.get_all_keys("test:*")
            assert len(keys) == 2
            mock_redis.keys.assert_called()
            
            # Test get_memory_info
            info = await cache.get_memory_info()
            assert "used_memory_human" in info
            
            # Test close
            await cache.close()
            mock_redis.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_or_set_caches_result(self):
        """Test that get_or_set caches the result"""
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_redis.get = AsyncMock(return_value=None)  # First call: cache miss
        mock_redis.setex = AsyncMock(return_value=True)
        
        with patch('utils.cache.redis') as mock_redis_module:
            mock_redis_module.Redis = MagicMock(return_value=mock_redis)
            
            cache = CacheManager(enabled=True)
            cache.redis_client = mock_redis
            
            call_count = 0
            
            async def fetch_func():
                nonlocal call_count
                call_count += 1
                return {"data": f"test_{call_count}"}
            
            # First call - should fetch and cache
            result1 = await cache.get_or_set("test_key", fetch_func, ttl=60)
            assert result1 == {"data": "test_1"}
            assert call_count == 1
            mock_redis.setex.assert_called_once()
            
            # Second call - should return cached value
            mock_redis.get = AsyncMock(return_value='{"data": "test_1"}')
            result2 = await cache.get_or_set("test_key", fetch_func, ttl=60)
            assert result2 == {"data": "test_1"}
            assert call_count == 1  # Should not call fetch_func again
    
    @pytest.mark.asyncio
    async def test_error_handling_in_cache_operations(self):
        """Test error handling in cache operations"""
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(side_effect=Exception("Connection error"))
        
        with patch('utils.cache.redis') as mock_redis_module:
            mock_redis_module.Redis = MagicMock(return_value=mock_redis)
            
            cache = CacheManager(enabled=True)
            cache.redis_client = mock_redis
            
            # All operations should return safe defaults on error
            result = await cache.get("test_key")
            assert result is None
            
            result = await cache.set("test_key", {"test": "value"}, ttl=60)
            assert result is False
            
            result = await cache.delete("test_key")
            assert result is False
            
            result = await cache.exists("test_key")
            assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

