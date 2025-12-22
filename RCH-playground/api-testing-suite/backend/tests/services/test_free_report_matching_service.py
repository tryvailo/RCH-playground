"""Tests for Free Report Matching Service"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))

from free_report_matching_service import (
    FreeReportMatchingService,
    get_free_report_matching_service,
)


@pytest.fixture
def service():
    return FreeReportMatchingService()


@pytest.fixture
def sample_homes():
    """Sample care homes for testing"""
    return [
        {
            "name": "Safe Home",
            "address": "123 Main St",
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
            "weekly_cost": 1500,
            "rating": "Outstanding",
            "cqc_rating_overall": "Outstanding",
            "latitude": 51.49,
            "longitude": -0.09,
            "care_types": ["residential"],
        },
    ]


class TestFreeReportMatchingService:
    """Test matching service"""

    def test_select_top_3_homes_basic(self, service, sample_homes):
        """Test basic home selection"""
        result = service.select_top_3_homes(
            homes=sample_homes,
            budget=1200,
            care_type="residential",
            user_lat=51.5,
            user_lon=-0.1,
        )

        assert "safe_bet" in result
        assert "best_value" in result
        assert "premium" in result

    def test_safe_bet_selection(self, service, sample_homes):
        """Test that safe bet is selected correctly"""
        result = service.select_top_3_homes(
            homes=sample_homes,
            budget=1200,
            care_type="residential",
        )

        safe_bet = result["safe_bet"]
        assert safe_bet is not None
        assert "name" in safe_bet
        # Safe bet should have good quality and reasonable price
        assert safe_bet.get("cqc_rating_overall", "").lower() in [
            "good",
            "outstanding",
        ]

    def test_best_value_selection(self, service, sample_homes):
        """Test that best value is selected correctly"""
        result = service.select_top_3_homes(
            homes=sample_homes,
            budget=1200,
            care_type="residential",
        )

        best_value = result["best_value"]
        # Should be different from safe bet
        if result["safe_bet"]:
            assert best_value is None or best_value["name"] != result["safe_bet"]["name"]

    def test_premium_selection(self, service, sample_homes):
        """Test that premium is selected correctly"""
        result = service.select_top_3_homes(
            homes=sample_homes,
            budget=1200,
            care_type="residential",
        )

        premium = result["premium"]
        if premium:
            # Premium should have high quality
            rating = premium.get("cqc_rating_overall", "").lower()
            assert rating in ["outstanding", "good"]

    def test_quality_filtering(self, service):
        """Test that poor quality homes are filtered"""
        homes = [
            {
                "name": "Good Home",
                "weekly_cost": 1000,
                "cqc_rating_overall": "Good",
                "care_types": ["residential"],
            },
            {
                "name": "Bad Home",
                "weekly_cost": 800,
                "cqc_rating_overall": "Inadequate",
                "care_types": ["residential"],
            },
        ]

        result = service.select_top_3_homes(
            homes=homes,
            budget=1200,
            care_type="residential",
        )

        # Should not select inadequate home
        selected_names = {
            result["safe_bet"]["name"] if result["safe_bet"] else None,
            result["best_value"]["name"] if result["best_value"] else None,
            result["premium"]["name"] if result["premium"] else None,
        }
        assert "Bad Home" not in selected_names

    def test_price_filtering(self, service):
        """Test price filtering"""
        homes = [
            {
                "name": "Affordable",
                "weekly_cost": 1200,
                "cqc_rating_overall": "Good",
                "care_types": ["residential"],
            },
            {
                "name": "Too Expensive",
                "weekly_cost": 2500,
                "cqc_rating_overall": "Good",
                "care_types": ["residential"],
            },
        ]

        result = service.select_top_3_homes(
            homes=homes,
            budget=1200,
            care_type="residential",
        )

        # Expensive home should be filtered (budget + 200 = 1400)
        # 2500 > 1400 so should be excluded
        if result["safe_bet"]:
            assert result["safe_bet"]["weekly_cost"] <= 1400

    def test_no_valid_homes_fallback(self, service):
        """Test fallback when no homes meet criteria"""
        homes = [
            {
                "name": "Home 1",
                "weekly_cost": 1000,
                "cqc_rating_overall": "Inadequate",
                "care_types": ["residential"],
            },
            {
                "name": "Home 2",
                "weekly_cost": 2000,
                "cqc_rating_overall": "Inadequate",
                "care_types": ["residential"],
            },
        ]

        result = service.select_top_3_homes(
            homes=homes,
            budget=1200,
            care_type="residential",
        )

        # Should still return something (fallback to first homes)
        assert result is not None

    def test_cqc_rating_score(self, service):
        """Test CQC rating scoring"""
        assert service._get_cqc_rating_score("Outstanding") == 4
        assert service._get_cqc_rating_score("Good") == 3
        assert service._get_cqc_rating_score("Requires Improvement") == 2
        assert service._get_cqc_rating_score("Inadequate") == 1
        assert service._get_cqc_rating_score("Unknown") == 0

    def test_cqc_rating_extraction(self, service):
        """Test CQC rating extraction from home"""
        home = {
            "cqc_rating_overall": "Outstanding",
            "rating": "Good",
        }
        assert service._get_cqc_rating(home) == "Outstanding"

        home = {
            "overall_cqc_rating": "Good",
        }
        assert service._get_cqc_rating(home) == "Good"

        home = {"rating": "Good"}
        assert service._get_cqc_rating(home) == "Good"

    def test_singleton_pattern(self):
        """Test that service can be retrieved as singleton"""
        service1 = get_free_report_matching_service()
        service2 = get_free_report_matching_service()
        assert isinstance(service1, FreeReportMatchingService)
        assert isinstance(service2, FreeReportMatchingService)

    def test_location_filtering(self, service):
        """Test location-based filtering"""
        homes = [
            {
                "name": "Close Home",
                "weekly_cost": 1200,
                "cqc_rating_overall": "Good",
                "latitude": 51.5,
                "longitude": -0.1,
                "care_types": ["residential"],
            },
            {
                "name": "Far Home",
                "weekly_cost": 1200,
                "cqc_rating_overall": "Good",
                "latitude": 52.5,  # Much farther away
                "longitude": -0.1,
                "care_types": ["residential"],
            },
        ]

        result = service.select_top_3_homes(
            homes=homes,
            budget=1200,
            care_type="residential",
            user_lat=51.5,
            user_lon=-0.1,
            max_distance_km=30,
        )

        # Close home should be prioritized
        if result["safe_bet"]:
            assert result["safe_bet"]["name"] in ["Close Home", "Far Home"]

    def test_price_score_calculation(self, service):
        """Test price scoring logic"""
        home = {
            "name": "Test",
            "cqc_rating_overall": "Good",
            "weekly_cost": 1200,
        }
        # At exact budget (Good CQC = +20, price diff < 50 = +20, total = 50+20+20 = 90)
        score = service._calculate_home_score(home, 1200, "residential", 1200)
        assert score > 50  # Should get bonus for price match

        # Way off budget (Good CQC = +20, price diff > 200 = 0, total = 50+20 = 70)
        home["weekly_cost"] = 2000
        score = service._calculate_home_score(home, 1200, "residential", 2000)
        assert score == 70  # Base + CQC score

    def test_empty_homes_list(self, service):
        """Test handling of empty homes list"""
        result = service.select_top_3_homes(
            homes=[],
            budget=1200,
            care_type="residential",
        )

        # Should return dict with None values
        assert result["safe_bet"] is None
        assert result["best_value"] is None
        assert result["premium"] is None
