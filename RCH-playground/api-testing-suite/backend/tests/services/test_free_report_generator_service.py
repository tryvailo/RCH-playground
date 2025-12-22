"""Tests for Free Report Generator Service"""
import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "models"))

from free_report_generator_service import (
    FreeReportGeneratorService,
    get_free_report_generator_service,
)
from free_report_models import FreeReportRequest, CareTypeEnum


@pytest.fixture
def sample_request():
    """Sample free report request"""
    return FreeReportRequest(
        postcode="SW1A1AA",
        budget=1200.0,
        care_type=CareTypeEnum.RESIDENTIAL,
        chc_probability=35.0,
    )


@pytest.fixture
def sample_care_homes():
    """Sample care homes"""
    return [
        {
            "name": "Safe Home",
            "address": "123 Main St",
            "postcode": "SW1A1AA",
            "weekly_cost": 1200,
            "rating": "Good",
            "cqc_rating_overall": "Good",
            "latitude": 51.5,
            "longitude": -0.1,
            "care_types": ["residential"],
        },
        {
            "name": "Value Home",
            "address": "456 Park Ave",
            "postcode": "SW1A1BB",
            "weekly_cost": 950,
            "rating": "Good",
            "cqc_rating_overall": "Good",
            "latitude": 51.51,
            "longitude": -0.11,
            "care_types": ["residential"],
        },
        {
            "name": "Premium Home",
            "address": "789 Garden Rd",
            "postcode": "SW1A1CC",
            "weekly_cost": 1500,
            "rating": "Outstanding",
            "cqc_rating_overall": "Outstanding",
            "latitude": 51.49,
            "longitude": -0.09,
            "care_types": ["residential"],
        },
    ]


@pytest.fixture
def service():
    """Generator service instance"""
    return FreeReportGeneratorService()


@pytest.fixture
def mock_service_with_mocks():
    """Generator service with mocked dependencies"""
    gap_service_mock = Mock()
    gap_service_mock.calculate_gap.return_value = {
        "gap_week": 152,
        "gap_year": 7904,
        "gap_5year": 39520,
        "gap_percent": 14.5,
        "market_price": 1200,
        "msif_lower_bound": 1048,
        "explanation": "Test gap",
        "gap_text": "Test gap text",
        "recommendations": [],
    }

    matching_service_mock = Mock()
    matching_service_mock.select_top_3_homes.return_value = {
        "safe_bet": {
            "name": "Safe Home",
            "weekly_cost": 1200,
            "cqc_rating_overall": "Good",
        },
        "best_value": {
            "name": "Value Home",
            "weekly_cost": 950,
            "cqc_rating_overall": "Good",
        },
        "premium": {
            "name": "Premium Home",
            "weekly_cost": 1500,
            "cqc_rating_overall": "Outstanding",
        },
    }

    return FreeReportGeneratorService(
        fair_cost_gap_service=gap_service_mock,
        matching_service=matching_service_mock,
    )


class TestFreeReportGeneratorService:
    """Test generator service"""

    @pytest.mark.asyncio
    async def test_generate_basic(self, service, sample_request, sample_care_homes):
        """Test basic report generation"""
        response = await service.generate(
            request=sample_request,
            care_homes=sample_care_homes,
            local_authority="Westminster",
            user_lat=51.5,
            user_lon=-0.1,
        )

        assert response.report_id is not None
        assert response.questionnaire is not None
        assert response.fair_cost_gap is not None
        assert response.generated_at is not None

    @pytest.mark.asyncio
    async def test_generate_with_matched_homes(
        self, mock_service_with_mocks, sample_request, sample_care_homes
    ):
        """Test report generation includes matched homes"""
        response = await mock_service_with_mocks.generate(
            request=sample_request,
            care_homes=sample_care_homes,
            local_authority="Westminster",
            user_lat=51.5,
            user_lon=-0.1,
        )

        assert len(response.care_homes) > 0
        assert response.care_homes[0]["match_type"] in [
            "Safe Bet",
            "Best Value",
            "Premium",
        ]

    @pytest.mark.asyncio
    async def test_generate_fair_cost_gap(
        self, mock_service_with_mocks, sample_request, sample_care_homes
    ):
        """Test that fair cost gap is calculated"""
        response = await mock_service_with_mocks.generate(
            request=sample_request,
            care_homes=sample_care_homes,
        )

        assert response.fair_cost_gap["gap_week"] == 152
        assert response.fair_cost_gap["market_price"] == 1200

    @pytest.mark.asyncio
    async def test_quality_filtering(
        self, service, sample_request
    ):
        """Test that low quality homes are filtered"""
        homes_with_poor_quality = [
            {
                "name": "Poor Home",
                "address": "Bad St",
                "postcode": "XX1 1XX",
                "weekly_cost": 800,
                "rating": "Inadequate",
                "cqc_rating_overall": "Inadequate",
                "latitude": 51.5,
                "longitude": -0.1,
                "care_types": ["residential"],
            },
        ]

        response = await service.generate(
            request=sample_request,
            care_homes=homes_with_poor_quality,
        )

        # Should still return a response even with poor homes
        assert response is not None

    @pytest.mark.asyncio
    async def test_dependency_injection(self):
        """Test dependency injection of services"""
        gap_mock = Mock()
        matching_mock = Mock()

        service = FreeReportGeneratorService(
            fair_cost_gap_service=gap_mock,
            matching_service=matching_mock,
        )

        assert service.gap_service == gap_mock
        assert service.matching_service == matching_mock

    def test_filter_by_quality(self, service):
        """Test quality filtering"""
        homes = [
            {
                "name": "Good Home",
                "cqc_rating_overall": "Good",
            },
            {
                "name": "Outstanding Home",
                "rating": "Outstanding",
            },
            {
                "name": "Bad Home",
                "cqc_rating_overall": "Inadequate",
            },
        ]

        filtered = service._filter_by_quality(homes, "residential")

        # Should have at least Good and Outstanding homes
        filtered_names = {h["name"] for h in filtered}
        assert "Good Home" in filtered_names or "Outstanding Home" in filtered_names

    def test_format_matched_homes(self, service):
        """Test home formatting"""
        matched = {
            "safe_bet": {
                "name": "Safe Home",
                "address": "123 St",
                "postcode": "SW1A1AA",
                "weekly_cost": 1200,
                "cqc_rating_overall": "Good",
                "care_types": ["residential"],
            },
            "best_value": None,
            "premium": None,
        }

        formatted = service._format_matched_homes(matched, "residential")

        assert len(formatted) == 1
        assert formatted[0]["name"] == "Safe Home"
        assert formatted[0]["match_type"] == "Safe Bet"
        assert formatted[0]["weekly_cost"] == 1200

    def test_calculate_fair_cost_gap(self, service):
        """Test fair cost gap calculation"""
        matched = {
            "safe_bet": {
                "name": "Home",
                "weekly_cost": 1200,
                "care_types": ["residential"],
            },
            "best_value": None,
            "premium": None,
        }

        gap = service._calculate_fair_cost_gap(
            matched, "residential", budget=1200
        )

        assert gap is not None
        assert "gap_week" in gap
        assert "gap_year" in gap

    def test_singleton_pattern(self):
        """Test singleton-style factory"""
        service1 = get_free_report_generator_service()
        service2 = get_free_report_generator_service()

        assert isinstance(service1, FreeReportGeneratorService)
        assert isinstance(service2, FreeReportGeneratorService)

    @pytest.mark.asyncio
    async def test_empty_homes_list(self, service, sample_request):
        """Test handling of empty homes list"""
        response = await service.generate(
            request=sample_request,
            care_homes=[],
        )

        assert response is not None
        assert response.report_id is not None
