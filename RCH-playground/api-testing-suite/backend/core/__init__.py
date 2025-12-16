"""
Core module for RightCareHome API Testing Suite
Contains shared dependencies, lifespan management, and error handlers
"""

from .dependencies import (
    get_cqc_client,
    get_firecrawl_client,
    get_google_places_client,
    credentials_store,
    active_connections,
    test_results_store
)
from .lifespan import lifespan
from .error_handlers import handle_cqc_error

__all__ = [
    "get_cqc_client",
    "get_firecrawl_client", 
    "get_google_places_client",
    "credentials_store",
    "active_connections",
    "test_results_store",
    "lifespan",
    "handle_cqc_error"
]
