"""
Tests for Free Report Viewer Models
"""
import pytest
from free_report_viewer.models import (
    QuestionnaireResponse,
    CareHome,
    FairCostGap,
    FreeReportResponse,
    CareType
)


def test_questionnaire_response_valid():
    """Test valid QuestionnaireResponse"""
    qr = QuestionnaireResponse(
        postcode="SW1A 1AA",
        budget=1200.0,
        care_type=CareType.RESIDENTIAL,
        chc_probability=35.5
    )
    
    assert qr.postcode == "SW1A 1AA"
    assert qr.budget == 1200.0
    assert qr.care_type == CareType.RESIDENTIAL
    assert qr.chc_probability == 35.5


def test_questionnaire_response_minimal():
    """Test QuestionnaireResponse with only required fields"""
    qr = QuestionnaireResponse(postcode="M1 1AA")
    
    assert qr.postcode == "M1 1AA"
    assert qr.budget is None
    assert qr.care_type is None


def test_questionnaire_response_invalid_postcode():
    """Test QuestionnaireResponse validation"""
    with pytest.raises(Exception):
        QuestionnaireResponse(postcode="")


def test_care_home_valid():
    """Test valid CareHome"""
    home = CareHome(
        name="Test Home",
        address="123 Test St",
        postcode="SW1A 1AA",
        weekly_cost=1200.0
    )
    
    assert home.name == "Test Home"
    assert home.weekly_cost == 1200.0


def test_care_home_invalid_cost():
    """Test CareHome with negative cost"""
    with pytest.raises(Exception):
        CareHome(
            name="Test Home",
            address="123 Test St",
            postcode="SW1A 1AA",
            weekly_cost=-100.0
        )


def test_fair_cost_gap_valid():
    """Test valid FairCostGap"""
    gap = FairCostGap(
        gap_week=150.0,
        gap_year=7800.0,
        gap_5year=39000.0,
        market_price=1050.0,
        msif_lower_bound=900.0,
        local_authority="Westminster",
        care_type="residential",
        explanation="Test explanation"
    )
    
    assert gap.gap_week == 150.0
    assert gap.gap_year == 7800.0
    assert gap.gap_5year == 39000.0
    assert gap.market_price == 1050.0
    assert gap.msif_lower_bound == 900.0


def test_free_report_response_valid():
    """Test valid FreeReportResponse"""
    questionnaire = QuestionnaireResponse(postcode="SW1A 1AA", budget=1200.0)
    care_homes = [
        CareHome(
            name="Home 1",
            address="123 St",
            postcode="SW1A 1AA",
            weekly_cost=1100.0
        )
    ]
    fair_cost_gap = FairCostGap(
        gap_week=150.0,
        gap_year=7800.0,
        gap_5year=39000.0,
        market_price=1050.0,
        msif_lower_bound=900.0,
        local_authority="Westminster",
        care_type="residential",
        explanation="Test"
    )
    
    report = FreeReportResponse(
        questionnaire=questionnaire,
        care_homes=care_homes,
        fair_cost_gap=fair_cost_gap,
        generated_at="2024-01-01T00:00:00",
        report_id="test-id"
    )
    
    assert len(report.care_homes) == 1
    assert report.fair_cost_gap.gap_week == 150.0
    assert report.fair_cost_gap.gap_5year == 39000.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

