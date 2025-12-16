"""
Error handling utilities for API clients
"""
import traceback
from fastapi import HTTPException


def handle_cqc_error(e: Exception) -> HTTPException:
    """Handle CQC API errors and return appropriate HTTPException"""
    error_message = str(e)
    error_detail = f"{error_message}\n{traceback.format_exc()}"
    print(f"CQC API error: {error_detail}")
    
    # Provide more helpful error messages
    if "403" in error_message or "Forbidden" in error_message:
        return HTTPException(
            status_code=403,
            detail="CQC API access denied. Please configure CQC subscription keys in API Configuration. Register at https://api-portal.service.cqc.org.uk/"
        )
    elif "401" in error_message or "Unauthorized" in error_message:
        return HTTPException(
            status_code=401,
            detail="CQC API authentication failed. Please check your subscription keys in API Configuration."
        )
    elif "429" in error_message or "rate limit" in error_message.lower():
        return HTTPException(
            status_code=429,
            detail="CQC API rate limit exceeded. Please wait before retrying."
        )
    else:
        return HTTPException(status_code=500, detail=f"CQC API error: {error_message}")


def handle_fsa_error(e: Exception) -> HTTPException:
    """Handle FSA API errors and return appropriate HTTPException"""
    error_message = str(e)
    print(f"FSA API error: {error_message}")
    
    if "404" in error_message or "not found" in error_message.lower():
        return HTTPException(
            status_code=404,
            detail="FSA establishment not found"
        )
    elif "429" in error_message or "rate limit" in error_message.lower():
        return HTTPException(
            status_code=429,
            detail="FSA API rate limit exceeded. Please wait before retrying."
        )
    else:
        return HTTPException(status_code=500, detail=f"FSA API error: {error_message}")


def handle_companies_house_error(e: Exception) -> HTTPException:
    """Handle Companies House API errors and return appropriate HTTPException"""
    error_message = str(e)
    print(f"Companies House API error: {error_message}")
    
    if "401" in error_message or "Unauthorized" in error_message:
        return HTTPException(
            status_code=401,
            detail="Companies House API authentication failed. Please check your API key."
        )
    elif "404" in error_message or "not found" in error_message.lower():
        return HTTPException(
            status_code=404,
            detail="Company not found"
        )
    elif "429" in error_message or "rate limit" in error_message.lower():
        return HTTPException(
            status_code=429,
            detail="Companies House API rate limit exceeded."
        )
    else:
        return HTTPException(status_code=500, detail=f"Companies House API error: {error_message}")


def handle_google_places_error(e: Exception) -> HTTPException:
    """Handle Google Places API errors and return appropriate HTTPException"""
    error_message = str(e)
    print(f"Google Places API error: {error_message}")
    
    if "REQUEST_DENIED" in error_message or "invalid" in error_message.lower():
        return HTTPException(
            status_code=401,
            detail="Google Places API request denied. Please check your API key."
        )
    elif "ZERO_RESULTS" in error_message:
        return HTTPException(
            status_code=404,
            detail="No results found for the search query"
        )
    elif "OVER_QUERY_LIMIT" in error_message:
        return HTTPException(
            status_code=429,
            detail="Google Places API quota exceeded."
        )
    else:
        return HTTPException(status_code=500, detail=f"Google Places API error: {error_message}")


def handle_firecrawl_error(e: Exception) -> HTTPException:
    """Handle Firecrawl API errors and return appropriate HTTPException"""
    error_message = str(e)
    print(f"Firecrawl API error: {error_message}")
    
    if "401" in error_message or "Unauthorized" in error_message:
        return HTTPException(
            status_code=401,
            detail="Firecrawl API authentication failed. Please check your API key."
        )
    elif "429" in error_message or "rate limit" in error_message.lower():
        return HTTPException(
            status_code=429,
            detail="Firecrawl API rate limit exceeded."
        )
    else:
        return HTTPException(status_code=500, detail=f"Firecrawl API error: {error_message}")
