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
from api_clients.openai_client import OpenAIClient
from utils.auth import get_api_credentials, get_cqc_credentials, credentials_store


def get_cqc_client() -> CQCAPIClient:
    """Get configured CQC API client"""
    try:
        creds, cqc_creds = get_cqc_credentials()
        
        if not creds or not cqc_creds:
            raise ValueError(
                "CQC API credentials are not configured. "
                "Please set CQC subscription keys in config.json or environment variables. "
                "Get your API keys at: https://api-portal.service.cqc.org.uk/"
            )
        
        # Check if subscription keys are placeholders
        placeholder_values = [
            "your-primary-subscription-key",
            "your-secondary-subscription-key",
            "your-cqc-primary-key",
            "your-cqc-secondary-key",
            "placeholder",
            "example",
            "test"
        ]
        
        primary_key = cqc_creds.primary_subscription_key
        if not primary_key:
            raise ValueError(
                "CQC API primary subscription key is not configured. "
                "Please set CQC_PRIMARY_SUBSCRIPTION_KEY in config.json or environment variable. "
                "Get your API keys at: https://api-portal.service.cqc.org.uk/"
            )
        
        # Check if primary key is a placeholder
        if primary_key.lower() in [p.lower() for p in placeholder_values] or primary_key.startswith("your-"):
            raise ValueError(
                "CQC API primary subscription key appears to be a placeholder. "
                "Please set a valid subscription key in config.json or environment variable CQC_PRIMARY_SUBSCRIPTION_KEY. "
                "Get your API keys at: https://api-portal.service.cqc.org.uk/"
            )
        
        # Check secondary key if provided
        secondary_key = cqc_creds.secondary_subscription_key
        if secondary_key and (secondary_key.lower() in [p.lower() for p in placeholder_values] or secondary_key.startswith("your-")):
            # Secondary key is optional, so just log a warning but don't fail
            print("⚠️ CQC secondary subscription key appears to be a placeholder, will use primary key only")
            secondary_key = None
        
        # Check partner code if provided
        partner_code = cqc_creds.partner_code
        if partner_code and (partner_code.lower() in ["yourpartnercode", "your-partner-code", "placeholder", "example", "test"] or partner_code.startswith("Your")):
            # Partner code is optional (legacy), so just log a warning
            print("⚠️ CQC partner code appears to be a placeholder, will use subscription key authentication only")
            partner_code = None
        
        return CQCAPIClient(
            partner_code=partner_code,
            primary_subscription_key=primary_key,
            secondary_subscription_key=secondary_key
        )
    except (ValueError, RuntimeError) as e:
        # Re-raise ValueError and RuntimeError as-is (they contain useful messages)
        raise
    except Exception as e:
        error_msg = str(e)
        if "credentials not configured" in error_msg or "subscription key" in error_msg.lower():
            raise ValueError(
                "CQC API credentials are not configured. "
                "Please set CQC subscription keys in config.json or environment variables. "
                "Get your API keys at: https://api-portal.service.cqc.org.uk/"
            )
        raise RuntimeError(f"Failed to initialize CQC client: {e}")


def get_fsa_client() -> FSAAPIClient:
    """Get configured FSA API client"""
    try:
        creds, service_creds = get_api_credentials("fsa")
        api_key = service_creds.api_key
        
        # FSA API might not require an API key (public API), but check if provided
        if api_key:
            # Check if API key is a placeholder
            placeholder_values = [
                "your-fsa-api-key",
                "your-fsa-key",
                "placeholder",
                "example",
                "test"
            ]
            if api_key.lower() in [p.lower() for p in placeholder_values] or api_key.startswith("your-"):
                print("⚠️ FSA API key appears to be a placeholder, will try to use FSA API without key")
                api_key = None
        
        return FSAAPIClient(api_key=api_key)
    except HTTPException as e:
        # FSA API is public, so missing credentials might be OK
        print("⚠️ FSA API credentials not configured, will try to use public API")
        return FSAAPIClient(api_key=None)


def get_companies_house_client() -> CompaniesHouseAPIClient:
    """Get configured Companies House client"""
    try:
        creds, service_creds = get_api_credentials("companies_house")
        api_key = service_creds.api_key
        
        # Check if API key is a placeholder
        placeholder_values = [
            "your-companies-house-api-key",
            "your-companies-house-key",
            "placeholder",
            "example",
            "test"
        ]
        if api_key.lower() in [p.lower() for p in placeholder_values] or api_key.startswith("your-"):
            raise ValueError(
                "Companies House API key is not configured. "
                "Please set a valid API key in config.json or environment variable COMPANIES_HOUSE_API_KEY. "
                "Get your API key at: https://developer.company-information.service.gov.uk/"
            )
        
        return CompaniesHouseAPIClient(api_key=api_key)
    except HTTPException as e:
        # Convert HTTPException to ValueError for better error handling outside route handlers
        raise ValueError(f"Companies House API configuration error: {e.detail}")


def get_google_places_client() -> GooglePlacesAPIClient:
    """Get configured Google Places client"""
    try:
        creds, service_creds = get_api_credentials("google_places")
        api_key = service_creds.api_key
        
        # Check if API key is a placeholder
        placeholder_values = [
            "your-google-places-api-key",
            "your-google-places-key",
            "placeholder",
            "example",
            "test"
        ]
        if api_key.lower() in [p.lower() for p in placeholder_values] or api_key.startswith("your-"):
            raise ValueError(
                "Google Places API key is not configured. "
                "Please set a valid API key in config.json or environment variable GOOGLE_PLACES_API_KEY. "
                "Get your API key at: https://console.cloud.google.com/apis/credentials"
            )
        
        return GooglePlacesAPIClient(api_key=api_key)
    except HTTPException as e:
        raise ValueError(f"Google Places API configuration error: {e.detail}")


def get_perplexity_client() -> PerplexityAPIClient:
    """Get configured Perplexity client"""
    try:
        creds, service_creds = get_api_credentials("perplexity")
        api_key = service_creds.api_key
        
        # Check if API key is a placeholder
        placeholder_values = [
            "your-perplexity-api-key",
            "your-perplexity-key",
            "placeholder",
            "example",
            "test"
        ]
        if api_key.lower() in [p.lower() for p in placeholder_values] or api_key.startswith("your-"):
            raise ValueError(
                "Perplexity API key is not configured. "
                "Please set a valid API key in config.json or environment variable PERPLEXITY_API_KEY. "
                "Get your API key at: https://www.perplexity.ai/settings/api"
            )
        
        return PerplexityAPIClient(api_key=api_key)
    except HTTPException as e:
        raise ValueError(f"Perplexity API configuration error: {e.detail}")


def get_besttime_client() -> BestTimeClient:
    """Get configured BestTime client"""
    try:
        creds, service_creds = get_api_credentials("besttime")
        private_key = getattr(service_creds, 'private_key', None)
        public_key = getattr(service_creds, 'public_key', None)
        if not private_key or not public_key:
            raise ValueError("BestTime credentials not configured (private_key and public_key required)")
        
        # Check if keys are placeholders
        placeholder_values = [
            "your-besttime-private-key",
            "your-besttime-public-key",
            "your-besttime-key",
            "placeholder",
            "example",
            "test"
        ]
        if (private_key.lower() in [p.lower() for p in placeholder_values] or private_key.startswith("your-") or
            public_key.lower() in [p.lower() for p in placeholder_values] or public_key.startswith("your-")):
            raise ValueError(
                "BestTime API keys are not configured. "
                "Please set valid keys in config.json or environment variables BESTTIME_PRIVATE_KEY and BESTTIME_PUBLIC_KEY. "
                "Get your API keys at: https://besttime.app/dashboard"
            )
        
        return BestTimeClient(private_key=private_key, public_key=public_key)
    except HTTPException as e:
        raise ValueError(f"BestTime API configuration error: {e.detail}")


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
    try:
        creds, service_creds = get_api_credentials("firecrawl")
        api_key = getattr(service_creds, 'api_key', None)
        if not api_key:
            raise ValueError("Firecrawl API key not found")
        
        # Check if API key is a placeholder
        placeholder_values = [
            "your-firecrawl-api-key",
            "your-firecrawl-key",
            "placeholder",
            "example",
            "test"
        ]
        if api_key.lower() in [p.lower() for p in placeholder_values] or api_key.startswith("your-"):
            raise ValueError(
                "Firecrawl API key is not configured. "
                "Please set a valid API key in config.json or environment variable FIRECRAWL_API_KEY. "
                "Get your API key at: https://firecrawl.dev/dashboard"
            )
        
        # Get Anthropic API key if available (optional)
        anthropic_api_key = None
        if creds and hasattr(creds, 'anthropic') and creds.anthropic:
            anthropic_api_key = getattr(creds.anthropic, 'api_key', None)
            # Check if Anthropic key is a placeholder (optional, so just warn)
            if anthropic_api_key:
                if anthropic_api_key.lower() in [p.lower() for p in placeholder_values] or anthropic_api_key.startswith("your-"):
                    print("⚠️ Anthropic API key appears to be a placeholder, Firecrawl will work without it")
                    anthropic_api_key = None
        
        return FirecrawlAPIClient(api_key=api_key, anthropic_api_key=anthropic_api_key)
    except HTTPException as e:
        raise ValueError(f"Firecrawl API configuration error: {e.detail}")


def get_openai_client() -> OpenAIClient:
    """Get configured OpenAI client"""
    try:
        creds, service_creds = get_api_credentials("openai")
        api_key = getattr(service_creds, 'api_key', None)
        if not api_key:
            raise ValueError("OpenAI API key not found")
        
        # Check if API key is a placeholder
        placeholder_values = [
            "your-openai-api-key",
            "your-openai-key",
            "sk-placeholder",
            "placeholder",
            "example",
            "test"
        ]
        if api_key.lower() in [p.lower() for p in placeholder_values] or api_key.startswith("your-") or api_key.startswith("sk-placeholder"):
            raise ValueError(
                "OpenAI API key is not configured. "
                "Please set a valid API key in config.json or environment variable OPENAI_API_KEY. "
                "Get your API key at: https://platform.openai.com/api-keys"
            )
        
        return OpenAIClient(api_key=api_key)
    except HTTPException as e:
        raise ValueError(f"OpenAI API configuration error: {e.detail}")
    except (ValueError, AttributeError, KeyError) as e:
        raise ValueError(f"OpenAI API configuration error: {str(e)}")

