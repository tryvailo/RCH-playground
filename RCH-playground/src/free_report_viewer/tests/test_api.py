"""
Tests for Free Report Viewer API Client
"""
import pytest
from unittest.mock import Mock, patch
from free_report_viewer.api import FreeReportAPIClient
from free_report_viewer.models import QuestionnaireResponse, CareType


def test_api_client_init():
    """Test API client initialization"""
    client = FreeReportAPIClient(base_url="http://test:8000")
    assert client.base_url == "http://test:8000"
    assert client.endpoint == "http://test:8000/api/free-report"


def test_api_client_default_url():
    """Test API client with default URL"""
    client = FreeReportAPIClient()
    assert client.base_url == "http://localhost:8000"


@patch('httpx.Client')
def test_generate_report_success(mock_client_class):
    """Test successful report generation"""
    # Mock response
    mock_response = Mock()
    mock_response.json.return_value = {
        "questionnaire": {
            "postcode": "SW1A 1AA",
            "budget": 1200.0
        },
        "care_homes": [
            {
                "name": "Test Home",
                "address": "123 St",
                "postcode": "SW1A 1AA",
                "weekly_cost": 1100.0
            }
        ],
        "fair_cost_gap": {
            "gap_week": 150.0,
            "gap_year": 7800.0,
            "gap_5year": 39000.0,
            "market_price": 1050.0,
            "msif_lower_bound": 900.0,
            "local_authority": "Westminster",
            "care_type": "residential",
            "explanation": "Test",
            "recommendations": []
        },
        "generated_at": "2024-01-01T00:00:00",
        "report_id": "test-id"
    }
    mock_response.raise_for_status = Mock()
    
    # Mock client context manager
    mock_client = Mock()
    mock_client.post.return_value = mock_response
    mock_client_class.return_value.__enter__.return_value = mock_client
    
    # Test
    client = FreeReportAPIClient()
    questionnaire = QuestionnaireResponse(
        postcode="SW1A 1AA",
        budget=1200.0,
        care_type=CareType.RESIDENTIAL
    )
    
    report = client.generate_report(questionnaire)
    
    assert report.questionnaire.postcode == "SW1A 1AA"
    assert len(report.care_homes) == 1
    mock_client.post.assert_called_once()


@patch('httpx.Client')
def test_generate_report_http_error(mock_client_class):
    """Test report generation with HTTP error"""
    import httpx
    
    # Mock client context manager
    mock_client = Mock()
    mock_client.post.side_effect = httpx.HTTPError("Connection error")
    mock_client_class.return_value.__enter__.return_value = mock_client
    
    client = FreeReportAPIClient()
    questionnaire = QuestionnaireResponse(postcode="SW1A 1AA")
    
    with pytest.raises(httpx.HTTPError):
        client.generate_report(questionnaire)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

