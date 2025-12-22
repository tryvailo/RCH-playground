"""
Configuration Routes
Handles API credentials management and configuration
"""
from fastapi import APIRouter, HTTPException, Request, Body
from typing import Dict, Any
import json
import os
from pathlib import Path

from models.schemas import ApiCredentials
from config_manager import get_credentials, save_config
from core.dependencies import credentials_store

router = APIRouter(prefix="/api/config", tags=["Configuration"])

# Placeholder patterns to detect example/tutorial values
PLACEHOLDER_PATTERNS = [
    'your-', 'example-', 'test-', 'placeholder',
    'xxx', '***', 'fake-', 'sample-',
    'replace-', 'insert-', 'add-',
    'enter your',
]

def is_placeholder(value) -> bool:
    """Check if a value is a placeholder/example value"""
    if value is None or not isinstance(value, str):
        return False
    return any(p in value.lower() for p in PLACEHOLDER_PATTERNS)

def strip_placeholders(data: dict) -> dict:
    """Remove placeholder values from credentials dict"""
    result = {}
    for key, val in data.items():
        if isinstance(val, dict):
            # Recursively clean nested dicts
            cleaned = {k: v for k, v in val.items() if not is_placeholder(v)}
            if cleaned:  # Only include if has real (non-placeholder) values
                result[key] = cleaned
        elif not is_placeholder(val) and val is not None:
            result[key] = val
    return result


@router.post("/credentials")
async def save_credentials(credentials: ApiCredentials):
    """Save API credentials to config file"""
    try:
        import traceback
        print(f"📝 Received credentials object: {type(credentials)}")
        
        # Get keys for logging - support both Pydantic v1 and v2
        try:
            if hasattr(credentials, 'model_dump'):
                creds_dict = credentials.model_dump(exclude_none=True)
            else:
                creds_dict = credentials.dict(exclude_none=True)
            print(f"📝 Credentials keys: {list(creds_dict.keys())}")
            # Don't print full data with sensitive keys, just structure
            safe_dict = {}
            for k, v in creds_dict.items():
                if isinstance(v, dict):
                    safe_dict[k] = {sk: "***" if "key" in sk.lower() or "secret" in sk.lower() else sv for sk, sv in v.items()}
                else:
                    safe_dict[k] = "***" if "key" in k.lower() or "secret" in k.lower() else v
            print(f"📝 Credentials structure: {json.dumps(safe_dict, indent=2, default=str)}")
        except Exception as log_error:
            print(f"⚠️ Could not log credentials keys: {log_error}")
            traceback.print_exc()
        
        # Check if we have at least some credentials to save
        has_credentials = any([
            credentials.cqc,
            credentials.companies_house,
            credentials.companiesHouse,
            credentials.google_places,
            credentials.perplexity,
            credentials.openai,
            credentials.firecrawl,
            credentials.anthropic
        ])
        
        if not has_credentials:
            print(f"⚠️ No credentials provided to save")
            raise HTTPException(
                status_code=400,
                detail="No credentials provided. At least one API must be configured."
            )
        
        # Save to config file
        print(f"💾 Attempting to save credentials...")
        try:
            save_config(credentials)
        except ValueError as ve:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid credentials: {str(ve)}"
            )
        except Exception as save_error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save credentials to file: {str(save_error)}"
            )
        
        # Update in-memory store
        credentials_store["default"] = credentials
        
        print(f"✅ Credentials saved successfully")
        configured_apis = list(creds_dict.keys()) if creds_dict else []
        return {
            "status": "success",
            "message": f"Credentials saved successfully. Configured APIs: {', '.join(configured_apis)}"
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        error_msg = str(e)
        print(f"❌ Error saving credentials: {error_msg}")
        print(f"❌ Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {error_msg}")


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
        print("📝 [GET /credentials] Starting endpoint")
        
        # Reload from config file to get latest
        print("📝 [GET /credentials] Calling get_credentials()...")
        creds = get_credentials()
        print(f"📝 [GET /credentials] Loaded credentials: {type(creds)}")
        
        # Convert to dict and strip placeholder values
        print("📝 [GET /credentials] Converting to dict...")
        try:
            if hasattr(creds, 'model_dump'):
                creds_dict = creds.model_dump(exclude_none=True)
            else:
                creds_dict = creds.dict(exclude_none=True)
            print(f"📝 [GET /credentials] Dict keys: {list(creds_dict.keys())}")
        except Exception as dict_err:
            print(f"⚠️  Error converting to dict: {dict_err}")
            creds_dict = {}
        
        # Remove any placeholder values (like 'your-api-key')
        print("📝 [GET /credentials] Stripping placeholders...")
        try:
            creds_dict = strip_placeholders(creds_dict)
            print(f"📝 [GET /credentials] After stripping: {list(creds_dict.keys())}")
        except Exception as strip_err:
            print(f"⚠️  Error stripping placeholders: {strip_err}")
            # Continue anyway
        
        # Check if we have real configured credentials (not placeholders)
        has_real_config = bool(creds_dict)
        print(f"📝 [GET /credentials] Has real config: {has_real_config}")
        
        # Always return all credential sections, even if empty
        # This allows frontend to show empty fields when keys are missing
        result: Dict = {
            "status": "configured" if has_real_config else "not_configured",
            "credentials": {}
        }
        
        # Helper function for safe attribute access
        def safe_get(obj, attr, default=""):
            """Safely get attribute from object, return default if None"""
            if obj is None:
                return default
            return getattr(obj, attr, default)
        
        # CQC - always include section
        result["credentials"]["cqc"] = {
            "partnerCode": safe_get(creds.cqc, 'partner_code', ""),
            "useWithoutCode": safe_get(creds.cqc, 'use_without_code', True) if creds.cqc else True,
            "primarySubscriptionKey": safe_get(creds.cqc, 'primary_subscription_key', ""),
            "secondarySubscriptionKey": safe_get(creds.cqc, 'secondary_subscription_key', ""),
            "hasPartnerCode": bool(creds.cqc and safe_get(creds.cqc, 'partner_code')),
            "hasSubscriptionKeys": bool(creds.cqc and safe_get(creds.cqc, 'primary_subscription_key'))
        }
        
        # Companies House - always include section
        result["credentials"]["companiesHouse"] = {
            "apiKey": safe_get(creds.companies_house, 'api_key', ""),
            "hasApiKey": bool(creds.companies_house and safe_get(creds.companies_house, 'api_key'))
        }
        
        # Google Places - always include section
        result["credentials"]["googlePlaces"] = {
            "apiKey": safe_get(creds.google_places, 'api_key', ""),
            "hasApiKey": bool(creds.google_places and safe_get(creds.google_places, 'api_key'))
        }
        
        # Perplexity - always include section
        result["credentials"]["perplexity"] = {
            "apiKey": safe_get(creds.perplexity, 'api_key', ""),
            "hasApiKey": bool(creds.perplexity and safe_get(creds.perplexity, 'api_key'))
        }
        
        # Firecrawl - always include section
        result["credentials"]["firecrawl"] = {
            "apiKey": safe_get(creds.firecrawl, 'api_key', ""),
            "hasApiKey": bool(creds.firecrawl and safe_get(creds.firecrawl, 'api_key'))
        }
        
        # OpenAI - always include section
        result["credentials"]["openai"] = {
            "apiKey": safe_get(creds.openai, 'api_key', ""),
            "hasApiKey": bool(creds.openai and safe_get(creds.openai, 'api_key'))
        }
        
        # Anthropic Claude - always include section
        result["credentials"]["anthropic"] = {
            "apiKey": safe_get(creds.anthropic, 'api_key', ""),
            "hasApiKey": bool(creds.anthropic and safe_get(creds.anthropic, 'api_key'))
        }
        
        print(f"✅ [GET /credentials] Returning success response")
        return result
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error in get_credentials_endpoint: {str(e)}")
        print(f"❌ Traceback: {error_trace}")
        
        # Return success response with empty credentials on error
        # This prevents 500 errors and allows frontend to show empty form
        print("📝 Returning graceful error response (empty credentials)")
        return {
            "status": "not_configured",
            "credentials": {
                "cqc": {"partnerCode": "", "useWithoutCode": True, "primarySubscriptionKey": "", "secondarySubscriptionKey": "", "hasPartnerCode": False, "hasSubscriptionKeys": False},
                "companiesHouse": {"apiKey": "", "hasApiKey": False},
                "googlePlaces": {"apiKey": "", "hasApiKey": False},
                "perplexity": {"apiKey": "", "hasApiKey": False},
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

