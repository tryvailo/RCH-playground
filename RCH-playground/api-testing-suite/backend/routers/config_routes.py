"""
Configuration Routes
Handles API credentials management and configuration
"""
from fastapi import APIRouter, HTTPException
from typing import Dict
import json
import os
from pathlib import Path

from models.schemas import ApiCredentials
from config_manager import get_credentials, save_config
from core.dependencies import credentials_store

router = APIRouter(prefix="/api/config", tags=["Configuration"])


@router.post("/credentials")
async def save_credentials(credentials: ApiCredentials):
    """Save API credentials to config file"""
    try:
        # Save to config file
        save_config(credentials)
        
        # Update in-memory store
        credentials_store["default"] = credentials
        
        return {
            "status": "success",
            "message": "Credentials saved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload")
async def reload_config():
    """Reload configuration from config file"""
    try:
        credentials_store["default"] = get_credentials()
        return {
            "status": "success",
            "message": "Configuration reloaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload configuration: {str(e)}")


@router.get("/credentials")
async def get_credentials_endpoint():
    """Get saved credentials with full keys for editing"""
    try:
        # Reload from config file to get latest
        creds = get_credentials()
        
        # Always return all credential sections, even if empty
        # This allows frontend to show empty fields when keys are missing
        result: Dict = {
            "status": "configured" if any([creds.cqc, creds.companies_house, creds.google_places, creds.perplexity, creds.besttime, creds.autumna, creds.openai, creds.firecrawl]) else "not_configured",
            "credentials": {}
        }
        
        # CQC - always include section
        result["credentials"]["cqc"] = {
            "partnerCode": creds.cqc.partner_code if creds.cqc and creds.cqc.partner_code else "",
            "useWithoutCode": creds.cqc.use_without_code if creds.cqc else True,
            "primarySubscriptionKey": creds.cqc.primary_subscription_key if creds.cqc and creds.cqc.primary_subscription_key else "",
            "secondarySubscriptionKey": creds.cqc.secondary_subscription_key if creds.cqc and creds.cqc.secondary_subscription_key else "",
            "hasPartnerCode": bool(creds.cqc and creds.cqc.partner_code),
            "hasSubscriptionKeys": bool(creds.cqc and creds.cqc.primary_subscription_key)
        }
        
        # Companies House - always include section
        result["credentials"]["companiesHouse"] = {
            "apiKey": creds.companies_house.api_key if creds.companies_house and creds.companies_house.api_key else "",
            "hasApiKey": bool(creds.companies_house and creds.companies_house.api_key)
        }
        
        # Google Places - always include section
        result["credentials"]["googlePlaces"] = {
            "apiKey": creds.google_places.api_key if creds.google_places and creds.google_places.api_key else "",
            "hasApiKey": bool(creds.google_places and creds.google_places.api_key)
        }
        
        # Perplexity - always include section
        result["credentials"]["perplexity"] = {
            "apiKey": creds.perplexity.api_key if creds.perplexity and creds.perplexity.api_key else "",
            "hasApiKey": bool(creds.perplexity and creds.perplexity.api_key)
        }
        
        # BestTime - always include section
        result["credentials"]["besttime"] = {
            "privateKey": creds.besttime.private_key if creds.besttime and creds.besttime.private_key else "",
            "publicKey": creds.besttime.public_key if creds.besttime and creds.besttime.public_key else "",
            "hasKeys": bool(creds.besttime and creds.besttime.private_key and creds.besttime.public_key)
        }
        
        # Autumna - always include section
        result["credentials"]["autumna"] = {
            "proxyUrl": creds.autumna.proxy_url if creds.autumna and creds.autumna.proxy_url else "",
            "useProxy": creds.autumna.use_proxy if creds.autumna else False,
            "hasProxy": bool(creds.autumna and creds.autumna.proxy_url)
        }
        
        # Firecrawl - always include section
        result["credentials"]["firecrawl"] = {
            "apiKey": creds.firecrawl.api_key if creds.firecrawl and creds.firecrawl.api_key else "",
            "hasApiKey": bool(creds.firecrawl and creds.firecrawl.api_key)
        }
        
        # OpenAI - always include section
        result["credentials"]["openai"] = {
            "apiKey": creds.openai.api_key if creds.openai and creds.openai.api_key else "",
            "hasApiKey": bool(creds.openai and creds.openai.api_key)
        }
        
        # Anthropic Claude - always include section
        result["credentials"]["anthropic"] = {
            "apiKey": creds.anthropic.api_key if creds.anthropic and creds.anthropic.api_key else "",
            "hasApiKey": bool(creds.anthropic and creds.anthropic.api_key)
        }
        
        return result
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error in get_credentials_endpoint: {str(e)}")
        print(f"❌ Traceback: {error_trace}")
        # Return empty credentials structure on error
        return {
            "status": "error",
            "error": str(e),
            "credentials": {
                "cqc": {"partnerCode": "", "useWithoutCode": True, "primarySubscriptionKey": "", "secondarySubscriptionKey": "", "hasPartnerCode": False, "hasSubscriptionKeys": False},
                "companiesHouse": {"apiKey": "", "hasApiKey": False},
                "googlePlaces": {"apiKey": "", "hasApiKey": False},
                "perplexity": {"apiKey": "", "hasApiKey": False},
                "besttime": {"privateKey": "", "publicKey": "", "hasKeys": False},
                "autumna": {"proxyUrl": "", "useProxy": False, "hasProxy": False},
                "firecrawl": {"apiKey": "", "hasApiKey": False},
                "openai": {"apiKey": "", "hasApiKey": False},
                "anthropic": {"apiKey": "", "hasApiKey": False}
            }
        }


@router.post("/validate")
async def validate_credentials():
    """Validate all configured credentials"""
    if "default" not in credentials_store:
        raise HTTPException(status_code=400, detail="No credentials configured")
    
    creds = credentials_store["default"]
    validation_results = {}
    
    # Validate each API
    if creds.cqc and (creds.cqc.primary_subscription_key or creds.cqc.partner_code):
        validation_results["cqc"] = {"configured": True, "valid": False}  # Would need actual API call to validate
    else:
        validation_results["cqc"] = {"configured": False, "valid": False}
    
    if creds.companies_house and creds.companies_house.api_key:
        validation_results["companies_house"] = {"configured": True, "valid": False}
    else:
        validation_results["companies_house"] = {"configured": False, "valid": False}
    
    if creds.google_places and creds.google_places.api_key:
        validation_results["google_places"] = {"configured": True, "valid": False}
    else:
        validation_results["google_places"] = {"configured": False, "valid": False}
    
    if creds.perplexity and creds.perplexity.api_key:
        validation_results["perplexity"] = {"configured": True, "valid": False}
    else:
        validation_results["perplexity"] = {"configured": False, "valid": False}
    
    return {
        "status": "success",
        "validation_results": validation_results
    }

