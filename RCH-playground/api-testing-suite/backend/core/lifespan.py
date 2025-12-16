"""
Application lifespan management (startup/shutdown)
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI

from config_manager import get_credentials
from utils.cache import close_cache_manager, get_cache_manager
from .dependencies import credentials_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    print("🚀 Starting RightCareHome API Testing Suite...")
    
    # Load credentials from config file
    credentials_store["default"] = get_credentials()
    print("✅ Configuration loaded")
    
    # Initialize cache manager
    cache = get_cache_manager()
    if cache.enabled:
        print("✅ Redis cache initialized")
    else:
        print("⚠️ Redis cache disabled (not configured or unavailable)")
    
    # Start local retry scheduler if running locally (not on Vercel)
    is_vercel = os.getenv('VERCEL') == '1' or os.getenv('VERCEL_ENV') is not None
    if not is_vercel:
        try:
            from services.local_retry_scheduler import get_scheduler
            scheduler = get_scheduler()
            await scheduler.start()
            print("✅ Local retry scheduler started (for development)")
        except Exception as e:
            print(f"⚠️ Failed to start local retry scheduler: {e}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")
    
    # Stop local retry scheduler
    if not is_vercel:
        try:
            from services.local_retry_scheduler import get_scheduler
            scheduler = get_scheduler()
            await scheduler.stop()
            print("✅ Local retry scheduler stopped")
        except Exception as e:
            print(f"⚠️ Failed to stop local retry scheduler: {e}")
    
    await close_cache_manager()
    print("✅ Cache connections closed")
