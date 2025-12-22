"""Tests for Fair Cost Gap Service"""
import pytest
import sys
from pathlib import Path

# Add services to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))

from fair_cost_gap_service import FairCostGapService, get_fair_cost_gap_service


@pytest.fixture
def service():
    return FairCostGapService()


class TestFairCostGapCalculation:
    """Test fair cost gap calculations"""

    def test_calculate_gap_basic(self, service):
        """Test basic gap calculation"""
        gap = service.calculate_gap(market_price=1912, msif_lower_bound=1048)

        assert gap["gap_week"] == 864
        assert gap["gap_year"] == 44928
        assert gap["gap_5year"] == 224640
        assert abs(gap["gap_percent"] - 82.4) < 0.1

    def test_calculate_gap_zero_difference(self, service):
        """Test when price equals MSIF"""
        gap = service.calculate_gap(market_price=1048, msif_lower_bound=1048)

        assert gap["gap_week"] == 0
        assert gap["gap_year"] == 0
        assert gap["gap_5year"] == 0
        assert gap["gap_percent"] == 0

    def test_calculate_gap_below_msif(self, service):
        """Test when price is below MSIF (negative gap)"""
        gap = service.calculate_gap(market_price=900, msif_lower_bound=1048)

        assert gap["gap_week"] == -148
        assert gap["gap_year"] == -7696
        assert gap["gap_5year"] == -38480

    def test_calculate_gap_explanation(self, service):
        """Test explanation text generation"""
        gap = service.calculate_gap(market_price=1912, msif_lower_bound=1048)

        assert "Market price" in gap["explanation"]
        assert "MSIF fair cost" in gap["explanation"]
        assert "82.4%" in gap["explanation"]

    def test_calculate_gap_text_positive(self, service):
        """Test gap text for positive gap"""
        gap = service.calculate_gap(market_price=1912, msif_lower_bound=1048)

        assert "Переплата" in gap["gap_text"]
        assert "44,928" in gap["gap_text"] or "44928" in gap["gap_text"]
        assert "224,640" in gap["gap_text"] or "224640" in gap["gap_text"]

    def test_calculate_gap_text_negative(self, service):
        """Test gap text for negative gap"""
        gap = service.calculate_gap(market_price=900, msif_lower_bound=1048)

        assert "Экономия" in gap["gap_text"]

    def test_recommendations_high_gap(self, service):
        """Test recommendations for high gap"""
        gap = service.calculate_gap(market_price=1912, msif_lower_bound=1048)

        recommendations = gap["recommendations"]
        assert "Use MSIF data to negotiate lower fees" in recommendations
        assert "Consider homes in adjacent local authorities" in recommendations

    def test_recommendations_low_gap(self, service):
        """Test recommendations for low gap"""
        gap = service.calculate_gap(market_price=1100, msif_lower_bound=1048)

        recommendations = gap["recommendations"]
        assert "Compare prices across multiple homes" in recommendations

    def test_recommendations_no_gap(self, service):
        """Test recommendations when no gap"""
        gap = service.calculate_gap(market_price=1048, msif_lower_bound=1048)

        recommendations = gap["recommendations"]
        assert "excellent market price" in recommendations[0]

    def test_market_price_stored(self, service):
        """Test that market price is stored in response"""
        gap = service.calculate_gap(market_price=1912, msif_lower_bound=1048)
        assert gap["market_price"] == 1912

    def test_msif_lower_bound_stored(self, service):
        """Test that MSIF lower bound is stored in response"""
        gap = service.calculate_gap(market_price=1912, msif_lower_bound=1048)
        assert gap["msif_lower_bound"] == 1048

    def test_care_type_parameter(self, service):
        """Test care_type parameter (doesn't affect calculation but is logged)"""
        gap = service.calculate_gap(
            market_price=1912, msif_lower_bound=1048, care_type="nursing_dementia"
        )
        assert gap["gap_week"] == 864

    def test_singleton_instance(self):
        """Test that singleton returns same instance"""
        service1 = get_fair_cost_gap_service()
        service2 = get_fair_cost_gap_service()
        assert service1 is service2

    def test_rounding_precision(self, service):
        """Test that results are rounded to 2 decimal places"""
        gap = service.calculate_gap(market_price=1234.567, msif_lower_bound=1000.123)

        # Check all numeric values are rounded to 2 decimal places
        assert gap["gap_week"] == round(gap["gap_week"], 2)
        assert gap["gap_year"] == round(gap["gap_year"], 2)
        assert gap["gap_5year"] == round(gap["gap_5year"], 2)
        assert gap["market_price"] == round(gap["market_price"], 2)
        assert gap["msif_lower_bound"] == round(gap["msif_lower_bound"], 2)
