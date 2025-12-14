"""
FastAPI Main Application - Refactored Version
RightCareHome API Testing Suite

This is a refactored version that uses modular routers.
The original main.py endpoints are gradually being moved to domain-specific routers.
"""
import sys
from pathlib import Path

# Add RCH-data src to Python path if not already there
project_root = Path(__file__).parent.parent.parent.parent.parent
rch_data_src_path = project_root / "RCH-data" / "src"
if str(rch_data_src_path) not in sys.path:
    sys.path.insert(0, str(rch_data_src_path))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from utils.auth import initialize_credentials_store
from routers.config_routes import credentials_store as config_credentials_store
from utils.cache import close_cache_manager, get_cache_manager

# Import routers
from routers import (
    config_routes,
    test_data_routes,
    cqc_routes,
    fsa_routes,
    test_routes,
    companies_house_routes,
    google_places_routes,
    perplexity_routes,
    firecrawl_routes,
    report_routes,
    analytics_routes,
    utility_routes
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    print("🚀 Starting RightCareHome API Testing Suite...")
    
    # Initialize credentials store
    initialize_credentials_store()
    # Sync with config router's credentials store
    from utils.auth import credentials_store
    config_credentials_store["default"] = credentials_store.get("default")
    print("✅ Configuration loaded")
    
    # Initialize cache manager
    cache = get_cache_manager()
    if cache.enabled:
        print("✅ Redis cache initialized")
    else:
        print("⚠️ Redis cache disabled (not configured or unavailable)")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")
    await close_cache_manager()
    print("✅ Cache connections closed")


app = FastAPI(
    title="RightCareHome API Testing Suite",
    description="Comprehensive API testing platform for UK care homes data sources",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Root Endpoints ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RightCareHome API Testing Suite",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "config": "/api/config",
            "test": "/api/test",
            "analyze": "/api/analyze",
            "test_data": "/api/test-data",
            "report": "/api/report"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint to verify API status"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "message": "RightCareHome API Testing Suite is running"
    }


# ==================== Register Routers ====================

# Configuration routes
app.include_router(config_routes.router)

# Test data routes
app.include_router(test_data_routes.router)

# CQC API routes
app.include_router(cqc_routes.router)

# FSA API routes
app.include_router(fsa_routes.router)

# Test routes
app.include_router(test_routes.router)

# Companies House routes
app.include_router(companies_house_routes.router)

# Google Places routes
app.include_router(google_places_routes.router)

# Perplexity routes
app.include_router(perplexity_routes.router)

# Firecrawl routes
app.include_router(firecrawl_routes.router)

# Report routes
app.include_router(report_routes.router)

# Analytics routes
app.include_router(analytics_routes.router)

# Utility routes
app.include_router(utility_routes.router)

# RCH-data routes (already modularized)
try:
    from api_clients.rch_data_routes import router as rch_data_router
    app.include_router(rch_data_router)
except ImportError:
    print("⚠️ RCH-data routes not available (modules not installed)")


# ==================== Migration Status ====================
# 
# ✅ All major endpoints have been migrated to routers:
# 
# ✅ Configuration endpoints -> routers/config_routes.py
# ✅ Test data endpoints -> routers/test_data_routes.py
# ✅ CQC endpoints -> routers/cqc_routes.py
# ✅ FSA endpoints -> routers/fsa_routes.py
# ✅ Companies House endpoints -> routers/companies_house_routes.py
# ✅ Google Places endpoints -> routers/google_places_routes.py
# ✅ Perplexity endpoints -> routers/perplexity_routes.py
# ✅ Firecrawl endpoints -> routers/firecrawl_routes.py
# ✅ Test endpoints -> routers/test_routes.py
# ✅ Report endpoints -> routers/report_routes.py
# ✅ Analytics endpoints -> routers/analytics_routes.py
# ✅ Utility endpoints -> routers/utility_routes.py
#
# Next step: Replace main.py with this refactored version after testing.
# See CODE_ANALYSIS_DUPLICATION_MODULARITY.md for details.


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

