"""
Client Factory for API Clients
Provides unified client initialization with dependency injection
"""
from typing import Optional
from fastapi import Depends, HTTPException
from api_clients.cqc_client import CQCAPIClient
from api_clients.fsa_client import FSAAPIClient
from api_clients.companies_house_client import CompaniesHouseAPIClient
from api_clients.google_places_client import GooglePlacesAPIClient
from api_clients.perplexity_client import PerplexityAPIClient
from api_clients.besttime_client import BestTimeClient
from api_clients.autumna_scraper import AutumnaScraper
from api_clients.firecrawl_client import FirecrawlAPIClient
from utils.auth import get_api_credentials, get_cqc_credentials, credentials_store


def get_cqc_client() -> CQCAPIClient:
    """Get configured CQC API client"""
    creds, cqc_creds = get_cqc_credentials()
    
    if creds and cqc_creds:
        return CQCAPIClient(
            partner_code=cqc_creds.partner_code,
            primary_subscription_key=cqc_creds.primary_subscription_key,
            secondary_subscription_key=cqc_creds.secondary_subscription_key
        )
    else:
        return CQCAPIClient(partner_code=None)


def get_fsa_client() -> FSAAPIClient:
    """Get configured FSA API client"""
    creds, service_creds = get_api_credentials("fsa")
    return FSAAPIClient(api_key=service_creds.api_key)


def get_companies_house_client() -> CompaniesHouseAPIClient:
    """Get configured Companies House client"""
    creds, service_creds = get_api_credentials("companies_house")
    return CompaniesHouseAPIClient(api_key=service_creds.api_key)


def get_google_places_client() -> GooglePlacesAPIClient:
    """Get configured Google Places client"""
    creds, service_creds = get_api_credentials("google_places")
    return GooglePlacesAPIClient(api_key=service_creds.api_key)


def get_perplexity_client() -> PerplexityAPIClient:
    """Get configured Perplexity client"""
    creds, service_creds = get_api_credentials("perplexity")
    return PerplexityAPIClient(api_key=service_creds.api_key)


def get_besttime_client() -> BestTimeClient:
    """Get configured BestTime client"""
    creds, service_creds = get_api_credentials("besttime")
    private_key = getattr(service_creds, 'private_key', None)
    public_key = getattr(service_creds, 'public_key', None)
    if not private_key or not public_key:
        raise HTTPException(status_code=400, detail="BestTime credentials not configured (private_key and public_key required)")
    return BestTimeClient(private_key=private_key, public_key=public_key)


def get_autumna_scraper() -> AutumnaScraper:
    """Get configured Autumna scraper"""
    creds = credentials_store.get("default")
    proxy_url = None
    if creds and hasattr(creds, 'autumna') and creds.autumna:
        use_proxy = getattr(creds.autumna, 'use_proxy', False)
        if use_proxy:
            proxy_url = getattr(creds.autumna, 'proxy_url', None)
    return AutumnaScraper(proxy=proxy_url)


def get_firecrawl_client() -> FirecrawlAPIClient:
    """Get configured Firecrawl client"""
    creds, service_creds = get_api_credentials("firecrawl")
    api_key = getattr(service_creds, 'api_key', None)
    if not api_key:
        raise HTTPException(status_code=400, detail="Firecrawl API key not found")
    
    # Get Anthropic API key if available (optional)
    anthropic_api_key = None
    if creds and hasattr(creds, 'anthropic') and creds.anthropic:
        anthropic_api_key = getattr(creds.anthropic, 'api_key', None)
    
    return FirecrawlAPIClient(api_key=api_key, anthropic_api_key=anthropic_api_key)

