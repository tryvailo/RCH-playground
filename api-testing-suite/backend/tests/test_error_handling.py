"""
Unit tests for error handling in API endpoints
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os
import httpx

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.error_handler import handle_api_error, create_error_response, DetailedHTTPException


class TestErrorHandler:
    """Test error handling utilities"""
    
    def test_handle_http_status_error_401(self):
        """Test handling of 401 Unauthorized error"""
        error_response = MagicMock()
        error_response.status_code = 401
        error_response.json = MagicMock(return_value={"error": {"message": "Invalid API key"}})
        
        error = httpx.HTTPStatusError(
            "Unauthorized",
            request=MagicMock(),
            response=error_response
        )
        
        error_detail = handle_api_error(error, "TestAPI", "test_operation")
        
        assert error_detail["error_type"] == "HTTPError"
        assert error_detail["http_status"] == 401
        assert "suggestions" in error_detail
        assert len(error_detail["suggestions"]) > 0
        assert "API key" in error_detail["suggestions"][0]
    
    def test_handle_http_status_error_403(self):
        """Test handling of 403 Forbidden error"""
        error_response = MagicMock()
        error_response.status_code = 403
        error_response.json = MagicMock(return_value={"error": {"message": "Forbidden"}})
        
        error = httpx.HTTPStatusError(
            "Forbidden",
            request=MagicMock(),
            response=error_response
        )
        
        error_detail = handle_api_error(error, "CQC", "search")
        
        assert error_detail["http_status"] == 403
        assert "Partner Code" in str(error_detail.get("suggestions", []))
    
    def test_handle_http_status_error_429(self):
        """Test handling of 429 Rate Limit error"""
        error_response = MagicMock()
        error_response.status_code = 429
        
        error = httpx.HTTPStatusError(
            "Rate Limit",
            request=MagicMock(),
            response=error_response
        )
        
        error_detail = handle_api_error(error, "TestAPI", "test_operation")
        
        assert error_detail["http_status"] == 429
        assert "Rate limit" in error_detail["suggestions"][0]
    
    def test_handle_timeout_error(self):
        """Test handling of timeout error"""
        error = httpx.TimeoutException("Request timed out", request=MagicMock())
        
        error_detail = handle_api_error(error, "TestAPI", "test_operation")
        
        assert error_detail["error_type"] == "TimeoutError"
        assert "timeout" in error_detail["suggestions"][0].lower()
    
    def test_handle_connection_error(self):
        """Test handling of connection error"""
        error = httpx.ConnectError("Connection failed", request=MagicMock())
        
        error_detail = handle_api_error(error, "TestAPI", "test_operation")
        
        assert error_detail["error_type"] == "ConnectionError"
        assert "connection" in error_detail["suggestions"][0].lower()
    
    def test_handle_value_error(self):
        """Test handling of ValueError"""
        error = ValueError("Invalid parameter")
        
        error_detail = handle_api_error(error, "TestAPI", "test_operation")
        
        assert error_detail["error_type"] == "ValidationError"
        assert "input parameters" in error_detail["suggestions"][0].lower()
    
    def test_handle_key_error(self):
        """Test handling of KeyError"""
        error = KeyError("missing_field")
        
        error_detail = handle_api_error(error, "TestAPI", "test_operation")
        
        assert error_detail["error_type"] == "MissingDataError"
        assert "missing" in error_detail["suggestions"][0].lower()
    
    def test_error_detail_structure(self):
        """Test that error detail has required structure"""
        error = Exception("Test error")
        
        error_detail = handle_api_error(error, "TestAPI", "test_operation", {"param": "value"})
        
        assert "api_name" in error_detail
        assert "operation" in error_detail
        assert "error_type" in error_detail
        assert "error_message" in error_detail
        assert "context" in error_detail
        assert error_detail["api_name"] == "TestAPI"
        assert error_detail["operation"] == "test_operation"
        assert error_detail["context"] == {"param": "value"}
    
    def test_detailed_http_exception(self):
        """Test DetailedHTTPException"""
        exception = DetailedHTTPException(
            status_code=400,
            detail="Test error",
            error_type="ValidationError",
            error_code="INVALID_PARAM",
            context={"param": "value"},
            suggestions=["Fix the parameter"]
        )
        
        assert exception.status_code == 400
        assert exception.detail == "Test error"
        assert exception.error_type == "ValidationError"
        assert exception.error_code == "INVALID_PARAM"
        assert exception.context == {"param": "value"}
        assert len(exception.suggestions) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

