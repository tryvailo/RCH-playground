"""
Authentication and Credential Management Utilities
Provides unified credential validation and retrieval
"""
from typing import Tuple, Any, Optional
from fastapi import HTTPException
from models.schemas import ApiCredentials
from config_manager import get_credentials

# Global credentials store (will be initialized in main.py)
credentials_store: dict = {}


def get_api_credentials(service_name: str) -> Tuple[ApiCredentials, Any]:
    """
    Get and validate API credentials for a service
    
    Args:
        service_name: Name of the service (e.g., "google_places", "companies_house")
    
    Returns:
        Tuple of (ApiCredentials, service_credentials)
    
    Raises:
        HTTPException: If credentials are not configured
    """
    creds = credentials_store.get("default")
    if not creds:
        raise HTTPException(
            status_code=400,
            detail=f"{service_name.replace('_', ' ').title()} credentials not configured"
        )
    
    # Normalize service name
    service_attr = service_name.lower().replace(' ', '_')
    service_creds = getattr(creds, service_attr, None)
    
    if not service_creds:
        raise HTTPException(
            status_code=400,
            detail=f"{service_name.replace('_', ' ').title()} credentials not configured"
        )
    
    api_key = getattr(service_creds, 'api_key', None)
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail=f"{service_name.replace('_', ' ').title()} API key not found"
        )
    
    return creds, service_creds


def get_cqc_credentials() -> Tuple[ApiCredentials, Any]:
    """Get CQC credentials (special handling for CQC API)"""
    creds = credentials_store.get("default")
    if not creds:
        # Fallback: load credentials directly if store is empty
        creds = get_credentials()
        if creds:
            credentials_store["default"] = creds
    
    if not creds:
        return None, None
    
    return creds, creds.cqc if creds.cqc else None


def initialize_credentials_store():
    """Initialize the global credentials store"""
    from config_manager import get_credentials
    credentials_store["default"] = get_credentials()

