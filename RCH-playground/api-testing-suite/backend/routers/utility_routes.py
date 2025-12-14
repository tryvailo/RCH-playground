"""
Utility Routes
Handles utility endpoints like proxy-fetch, cache management, etc.
"""
from fastapi import APIRouter, HTTPException, Body, Query
from fastapi.responses import Response
from typing import Optional
import httpx

router = APIRouter(prefix="/api", tags=["Utilities"])


@router.post("/proxy-fetch")
async def proxy_fetch(url: str = Body(..., embed=True)):
    """Proxy fetch endpoint to avoid CORS issues when loading external files"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return Response(
                content=response.content,
                media_type=response.headers.get("content-type", "application/octet-stream"),
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy fetch failed: {str(e)}")


@router.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    try:
        from utils.cache import get_cache_manager
        cache = get_cache_manager()
        
        if not cache.enabled:
            return {
                "status": "disabled",
                "enabled": False,
                "message": "Cache is not enabled or Redis is not available"
            }
        
        stats = await cache.get_stats()
        return {
            "status": "success",
            "enabled": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cache stats: {str(e)}")


@router.delete("/cache/clear")
async def clear_cache(prefix: Optional[str] = Query(None)):
    """Clear cache entries"""
    try:
        from utils.cache import get_cache_manager
        cache = get_cache_manager()
        
        if not cache.enabled:
            return {
                "status": "disabled",
                "message": "Cache is not enabled"
            }
        
        cleared = await cache.clear(prefix=prefix)
        return {
            "status": "success",
            "cleared": cleared,
            "prefix": prefix
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


@router.get("/cache/test")
async def test_cache():
    """Test cache functionality"""
    try:
        from utils.cache import get_cache_manager
        cache = get_cache_manager()
        
        if not cache.enabled:
            return {
                "status": "disabled",
                "enabled": False,
                "message": "Cache is not enabled or Redis is not available"
            }
        
        # Test set/get
        test_key = "test_key"
        test_value = "test_value"
        
        await cache.set(test_key, test_value, ttl=60)
        retrieved = await cache.get(test_key)
        
        return {
            "status": "success",
            "enabled": True,
            "test": {
                "set": test_key,
                "get": retrieved,
                "match": retrieved == test_value
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache test failed: {str(e)}")

