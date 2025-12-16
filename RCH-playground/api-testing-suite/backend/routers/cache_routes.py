"""
Cache Management API Routes
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/cache", tags=["Cache Management"])


@router.get("/stats")
async def get_cache_stats():
    """Get cache statistics"""
    try:
        from utils.cache import get_cache_manager
        cache = get_cache_manager()
        
        if not cache.enabled:
            return {
                "status": "disabled",
                "message": "Redis cache is not enabled or not available"
            }
        
        # Get cache statistics
        try:
            # Count keys with google_places prefix
            keys = await cache.redis_client.keys("google_places:*")
            key_count = len(keys) if keys else 0
            
            # Get memory info if available
            info = await cache.redis_client.info("memory")
            memory_used = info.get("used_memory_human", "N/A")
            
            return {
                "status": "enabled",
                "cache_enabled": True,
                "google_places_keys": key_count,
                "memory_used": memory_used,
                "cache_ttl_default": cache.cache_ttl if hasattr(cache, 'cache_ttl') else 86400
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get cache stats: {str(e)}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@router.delete("/clear")
async def clear_cache(prefix: Optional[str] = None):
    """Clear cache entries"""
    try:
        from utils.cache import get_cache_manager
        cache = get_cache_manager()
        
        if not cache.enabled:
            raise HTTPException(status_code=400, detail="Cache is not enabled")
        
        if prefix:
            # Clear specific prefix
            pattern = f"{prefix}:*"
            keys = await cache.redis_client.keys(pattern)
            if keys:
                await cache.redis_client.delete(*keys)
            return {
                "status": "success",
                "message": f"Cleared {len(keys)} keys with prefix '{prefix}'"
            }
        else:
            # Clear all google_places keys
            keys = await cache.redis_client.keys("google_places:*")
            if keys:
                await cache.redis_client.delete(*keys)
            return {
                "status": "success",
                "message": f"Cleared {len(keys)} Google Places cache keys"
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


@router.get("/test")
async def test_cache():
    """Test cache connectivity"""
    try:
        from utils.cache import get_cache_manager
        cache = get_cache_manager()
        
        if not cache.enabled:
            return {
                "status": "disabled",
                "message": "Redis cache is not enabled"
            }
        
        # Test write and read
        test_key = "cache_test:connection"
        test_value = {"test": True, "timestamp": datetime.now().isoformat()}
        
        await cache.set(test_key, test_value, ttl=60)
        retrieved = await cache.get(test_key)
        
        if retrieved and retrieved.get("test"):
            await cache.delete(test_key)
            return {
                "status": "success",
                "message": "Cache is working correctly"
            }
        else:
            return {
                "status": "error",
                "message": "Cache read/write test failed"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Cache test failed: {str(e)}"
        }
