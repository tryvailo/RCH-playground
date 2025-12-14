"""
Enhanced Error Handler for API Endpoints
Provides detailed error information and consistent error responses
"""
import traceback
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import httpx

logger = logging.getLogger(__name__)


class DetailedHTTPException(HTTPException):
    """Extended HTTPException with detailed error information"""
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_type: Optional[str] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[list] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_type = error_type
        self.error_code = error_code
        self.context = context or {}
        self.suggestions = suggestions or []


def handle_api_error(
    error: Exception,
    api_name: str,
    operation: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Handle API errors with detailed information
    
    Args:
        error: The exception that occurred
        api_name: Name of the API (e.g., "CQC", "Google Places")
        operation: Operation being performed (e.g., "search", "get_details")
        context: Additional context information
    
    Returns:
        Dictionary with detailed error information
    """
    context = context or {}
    error_detail = {
        "api_name": api_name,
        "operation": operation,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context
    }
    
    # Handle specific error types
    if isinstance(error, httpx.HTTPStatusError):
        status_code = error.response.status_code
        error_detail["http_status"] = status_code
        error_detail["error_type"] = "HTTPError"
        
        # Try to extract error details from response
        try:
            error_body = error.response.json()
            error_detail["api_error"] = error_body.get("error", {})
            error_detail["api_message"] = error_body.get("message", "")
        except:
            error_detail["api_response"] = error.response.text[:500]
        
        # Add specific suggestions based on status code
        if status_code == 401:
            error_detail["suggestions"] = [
                "Check if API key is correct",
                "Verify API key has not expired",
                "Ensure API key has required permissions"
            ]
        elif status_code == 403:
            error_detail["suggestions"] = [
                "Check if API key has required permissions",
                "Verify account is active and not suspended",
                "Check if Partner Code is required (for CQC API)"
            ]
        elif status_code == 429:
            error_detail["suggestions"] = [
                "Rate limit exceeded - wait before retrying",
                "Consider implementing exponential backoff",
                "Check rate limit settings in API documentation"
            ]
        elif status_code == 500:
            error_detail["suggestions"] = [
                "API server error - try again later",
                "Check API status page for outages",
                "Contact API support if issue persists"
            ]
    
    elif isinstance(error, httpx.TimeoutException):
        error_detail["error_type"] = "TimeoutError"
        error_detail["suggestions"] = [
            "Request timed out - check network connection",
            "API may be slow - try again later",
            "Consider increasing timeout settings"
        ]
    
    elif isinstance(error, httpx.ConnectError):
        error_detail["error_type"] = "ConnectionError"
        error_detail["suggestions"] = [
            "Cannot connect to API - check network connection",
            "Verify API endpoint URL is correct",
            "Check if API service is available"
        ]
    
    elif isinstance(error, ValueError):
        error_detail["error_type"] = "ValidationError"
        error_detail["suggestions"] = [
            "Check input parameters are valid",
            "Verify required fields are provided",
            "Check data format matches API requirements"
        ]
    
    elif isinstance(error, KeyError):
        error_detail["error_type"] = "MissingDataError"
        error_detail["suggestions"] = [
            "Required data field is missing",
            "Check API response structure",
            "Verify API version compatibility"
        ]
    
    # Log error with traceback
    logger.error(
        f"{api_name} API error in {operation}: {str(error)}",
        extra={
            "error_type": error_detail["error_type"],
            "context": context,
            "traceback": traceback.format_exc()
        }
    )
    
    return error_detail


def create_error_response(
    error: Exception,
    api_name: str,
    operation: str,
    status_code: int = 500,
    context: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Create a detailed error response
    
    Args:
        error: The exception that occurred
        api_name: Name of the API
        operation: Operation being performed
        status_code: HTTP status code
        context: Additional context
    
    Returns:
        JSONResponse with detailed error information
    """
    error_detail = handle_api_error(error, api_name, operation, context)
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "error": error_detail,
            "timestamp": str(datetime.now())
        }
    )


def safe_api_call(
    func,
    api_name: str,
    operation: str,
    default_return: Any = None,
    context: Optional[Dict[str, Any]] = None
):
    """
    Decorator for safe API calls with error handling
    
    Usage:
        @safe_api_call(api_name="CQC", operation="search")
        async def search_homes(...):
            ...
    """
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_detail = handle_api_error(e, api_name, operation, context)
            raise DetailedHTTPException(
                status_code=500,
                detail=error_detail["error_message"],
                error_type=error_detail["error_type"],
                context=error_detail.get("context", {}),
                suggestions=error_detail.get("suggestions", [])
            )
    return wrapper

