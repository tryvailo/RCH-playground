"""
Configuration Manager
Handles reading and writing API credentials from/to config file
"""
import json
import os
from pathlib import Path
from typing import Dict, Optional
from models.schemas import ApiCredentials, CQCCredentials, CompaniesHouseCredentials, GooglePlacesCredentials, PerplexityCredentials, BestTimeCredentials, AutumnaCredentials, OpenAICredentials, FirecrawlCredentials, AnthropicCredentials


CONFIG_FILE = Path(__file__).parent / "config.json"


def load_config() -> ApiCredentials:
    """Load credentials from config file"""
    if not CONFIG_FILE.exists():
        print(f"Config file not found at {CONFIG_FILE}")
        return ApiCredentials()
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"Loaded config data: {list(data.keys())}")
            creds = ApiCredentials(**data)
            print(f"Successfully loaded credentials")
            return creds
    except Exception as e:
        print(f"Error loading config: {e}")
        import traceback
        traceback.print_exc()
        return ApiCredentials()


def save_config(credentials: ApiCredentials) -> None:
    """Save credentials to config file"""
    try:
        # Create directory if it doesn't exist
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict and save
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(credentials.dict(exclude_none=True), f, indent=2, ensure_ascii=False)
        
        print(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"Error saving config: {e}")
        raise


def load_from_env() -> ApiCredentials:
    """Load credentials from environment variables (fallback)"""
    creds = ApiCredentials()
    
    # CQC
    if os.getenv("CQC_PARTNER_CODE") or os.getenv("CQC_PRIMARY_SUBSCRIPTION_KEY"):
        creds.cqc = CQCCredentials(
            partner_code=os.getenv("CQC_PARTNER_CODE"),
            primary_subscription_key=os.getenv("CQC_PRIMARY_SUBSCRIPTION_KEY"),
            secondary_subscription_key=os.getenv("CQC_SECONDARY_SUBSCRIPTION_KEY")
        )
    
    # Companies House
    if os.getenv("COMPANIES_HOUSE_API_KEY"):
        creds.companies_house = CompaniesHouseCredentials(api_key=os.getenv("COMPANIES_HOUSE_API_KEY"))
    
    # Google Places
    if os.getenv("GOOGLE_PLACES_API_KEY"):
        creds.google_places = GooglePlacesCredentials(api_key=os.getenv("GOOGLE_PLACES_API_KEY"))
    
    # Perplexity
    if os.getenv("PERPLEXITY_API_KEY"):
        creds.perplexity = PerplexityCredentials(api_key=os.getenv("PERPLEXITY_API_KEY"))
    
    # BestTime
    if os.getenv("BESTTIME_PRIVATE_KEY") and os.getenv("BESTTIME_PUBLIC_KEY"):
        creds.besttime = BestTimeCredentials(
            private_key=os.getenv("BESTTIME_PRIVATE_KEY"),
            public_key=os.getenv("BESTTIME_PUBLIC_KEY")
        )
    
    # Autumna
    if os.getenv("AUTUMNA_PROXY_URL"):
        creds.autumna = AutumnaCredentials(
            proxy_url=os.getenv("AUTUMNA_PROXY_URL"),
            use_proxy=bool(os.getenv("AUTUMNA_USE_PROXY", "false").lower() == "true")
        )
    
    # OpenAI
    if os.getenv("OPENAI_API_KEY"):
        creds.openai = OpenAICredentials(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Firecrawl
    if os.getenv("FIRECRAWL_API_KEY"):
        creds.firecrawl = FirecrawlCredentials(api_key=os.getenv("FIRECRAWL_API_KEY"))
    
    # Anthropic Claude
    if os.getenv("ANTHROPIC_API_KEY"):
        creds.anthropic = AnthropicCredentials(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    return creds


def get_credentials() -> ApiCredentials:
    """Get credentials from config file or environment variables"""
    # Try config file first
    config_creds = load_config()
    
    # Merge with environment variables (env takes precedence)
    env_creds = load_from_env()
    
    # Merge: env overrides config
    merged = ApiCredentials()
    
    # CQC
    merged.cqc = env_creds.cqc or config_creds.cqc
    
    # Companies House
    merged.companies_house = env_creds.companies_house or config_creds.companies_house
    
    # Google Places
    merged.google_places = env_creds.google_places or config_creds.google_places
    
    # Perplexity
    merged.perplexity = env_creds.perplexity or config_creds.perplexity
    
    # BestTime
    merged.besttime = env_creds.besttime or config_creds.besttime
    
    # Autumna
    merged.autumna = env_creds.autumna or config_creds.autumna
    
    # OpenAI
    merged.openai = env_creds.openai or config_creds.openai
    
    # Firecrawl
    merged.firecrawl = env_creds.firecrawl or config_creds.firecrawl
    
    # Anthropic Claude
    merged.anthropic = env_creds.anthropic or config_creds.anthropic
    
    return merged


def mask_api_key(key: Optional[str]) -> Optional[str]:
    """Mask API key for display (show first 4 and last 4 characters)"""
    if not key or len(key) < 8:
        return None
    return f"{key[:4]}...{key[-4:]}"

