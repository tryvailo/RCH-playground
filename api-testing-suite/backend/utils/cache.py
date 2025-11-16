"""
Redis Cache Manager for API Response Caching
Optimizes Google Places API costs by caching responses
"""
import json
import hashlib
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import os

try:
    import redis.asyncio as redis
except ImportError:
    try:
        import redis
        # For older redis versions, use sync client
        redis = None
        print("⚠️ redis.asyncio not available, using sync redis")
    except ImportError:
        redis = None
        print("⚠️ Redis not installed, caching disabled")


class CacheManager:
    """Redis-based cache manager for API responses"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        enabled: bool = True
    ):
        self.enabled = enabled and redis is not None
        self.redis_client: Optional[Any] = None
        
        if self.enabled and redis is not None:
            try:
                self.redis_client = redis.Redis(
                    host=host,
                    port=port,
                    db=db,
                    password=password,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                # Test connection
                # Note: We'll test async connection in async context
            except Exception as e:
                print(f"⚠️ Redis connection failed: {e}. Caching disabled.")
                self.enabled = False
                self.redis_client = None
        elif enabled and redis is None:
            print("⚠️ Redis library not available. Install with: pip install redis")
            self.enabled = False
    
    async def _ensure_connection(self) -> bool:
        """Ensure Redis connection is available"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            await self.redis_client.ping()
            return True
        except Exception as e:
            print(f"⚠️ Redis ping failed: {e}. Caching disabled.")
            self.enabled = False
            return False
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        # Create a hash of all arguments
        key_parts = [prefix]
        
        # Add positional args
        for arg in args:
            if isinstance(arg, (str, int, float)):
                key_parts.append(str(arg))
            elif isinstance(arg, (list, dict)):
                key_parts.append(json.dumps(arg, sort_keys=True))
        
        # Add keyword args
        if kwargs:
            sorted_kwargs = json.dumps(kwargs, sort_keys=True)
            key_parts.append(sorted_kwargs)
        
        # Create hash
        key_string = ":".join(key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"{prefix}:{key_hash}"
    
    async def get(
        self,
        key: str,
        default: Optional[Any] = None
    ) -> Optional[Any]:
        """Get value from cache"""
        if not await self._ensure_connection():
            return default
        
        try:
            cached_value = await self.redis_client.get(key)
            if cached_value:
                return json.loads(cached_value)
            return default
        except Exception as e:
            print(f"⚠️ Cache get error: {e}")
            return default
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 86400  # Default 24 hours
    ) -> bool:
        """Set value in cache with TTL"""
        if not await self._ensure_connection():
            return False
        
        try:
            serialized_value = json.dumps(value, default=str)
            await self.redis_client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            print(f"⚠️ Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not await self._ensure_connection():
            return False
        
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"⚠️ Cache delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not await self._ensure_connection():
            return False
        
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            print(f"⚠️ Cache exists error: {e}")
            return False
    
    async def get_or_set(
        self,
        key: str,
        fetch_func,
        ttl: int = 86400,
        *args,
        **kwargs
    ) -> Any:
        """
        Get from cache or fetch and cache the result
        
        Args:
            key: Cache key
            fetch_func: Async function to fetch data if not cached
            ttl: Time to live in seconds
            *args, **kwargs: Arguments to pass to fetch_func
        """
        # Try to get from cache
        cached_value = await self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Fetch fresh data
        fresh_value = await fetch_func(*args, **kwargs)
        
        # Cache the result
        if fresh_value is not None:
            await self.set(key, fresh_value, ttl)
        
        return fresh_value
    
    async def get_all_keys(self, pattern: str = "*") -> List[str]:
        """Get all keys matching pattern"""
        if not await self._ensure_connection():
            return []
        
        try:
            keys = await self.redis_client.keys(pattern)
            return keys if keys else []
        except Exception as e:
            print(f"⚠️ Cache get_all_keys error: {e}")
            return []
    
    async def get_memory_info(self) -> Dict[str, Any]:
        """Get Redis memory information"""
        if not await self._ensure_connection():
            return {}
        
        try:
            info = await self.redis_client.info("memory")
            return info
        except Exception as e:
            print(f"⚠️ Cache memory info error: {e}")
            return {}
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            try:
                await self.redis_client.close()
            except Exception:
                pass


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get or create global cache manager instance"""
    global _cache_manager
    
    if _cache_manager is None:
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        redis_db = int(os.getenv("REDIS_DB", "0"))
        redis_password = os.getenv("REDIS_PASSWORD")
        redis_enabled = os.getenv("REDIS_ENABLED", "true").lower() == "true"
        
        _cache_manager = CacheManager(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password,
            enabled=redis_enabled
        )
    
    return _cache_manager


async def close_cache_manager():
    """Close global cache manager"""
    global _cache_manager
    if _cache_manager:
        await _cache_manager.close()
        _cache_manager = None

