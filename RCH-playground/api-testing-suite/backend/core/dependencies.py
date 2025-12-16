"""
Dependency injection and client factory functions
"""
from typing import Dict, Optional, Any
from fastapi import HTTPException, WebSocket

from api_clients.cqc_client import CQCAPIClient
from api_clients.google_places_client import GooglePlacesAPIClient
from api_clients.firecrawl_client import FirecrawlAPIClient
from models.schemas import ApiCredentials
from config_manager import get_credentials


# Global state
active_connections: Dict[str, WebSocket] = {}
test_results_store: Dict[str, Dict] = {}

# In-memory storage (backed by config file)
credentials_store: Dict[str, ApiCredentials] = {"default": get_credentials()}


def get_cqc_client(creds: Optional[ApiCredentials] = None) -> CQCAPIClient:
    """Helper function to create CQCAPIClient with credentials"""
    if creds is None:
        creds = credentials_store.get("default")
    
    if creds and creds.cqc:
        return CQCAPIClient(
            partner_code=creds.cqc.partner_code,
            primary_subscription_key=creds.cqc.primary_subscription_key,
            secondary_subscription_key=creds.cqc.secondary_subscription_key
        )
    else:
        return CQCAPIClient(partner_code=None)


def get_google_places_client() -> Optional[GooglePlacesAPIClient]:
    """Return a Google Places client if credentials are available, otherwise None."""
    try:
        creds = credentials_store.get("default")
        api_key = getattr(creds.google_places, "api_key", None) if creds and getattr(creds, "google_places", None) else None
        if not api_key:
            return None
        return GooglePlacesAPIClient(api_key=api_key)
    except Exception as exc:
        print(f"⚠️ Unable to initialize Google Places client: {exc}")
        return None


def get_firecrawl_client(creds: Optional[ApiCredentials] = None) -> FirecrawlAPIClient:
    """Helper function to create FirecrawlAPIClient with optional Anthropic support"""
    if creds is None:
        creds = get_credentials()
    
    if not creds or not hasattr(creds, 'firecrawl') or not creds.firecrawl:
        raise HTTPException(status_code=400, detail="Firecrawl credentials not configured")
    
    api_key = getattr(creds.firecrawl, 'api_key', None)
    if not api_key:
        raise HTTPException(status_code=400, detail="Firecrawl API key not found")
    
    # Получаем Anthropic API key если доступен (опционально)
    anthropic_api_key = None
    if hasattr(creds, 'anthropic') and creds.anthropic:
        anthropic_api_key = getattr(creds.anthropic, 'api_key', None)
    
    return FirecrawlAPIClient(api_key=api_key, anthropic_api_key=anthropic_api_key)


def reload_credentials() -> None:
    """Reload credentials from config file into memory store"""
    credentials_store["default"] = get_credentials()
