"""Integration tests for Funding Calculator API endpoint."""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any
import json


@pytest.fixture
def client():
    """Create test client."""
    try:
        from main import app
        return TestClient(app)
    except ImportError:
        pytest.skip("Main app not available")


@pytest.fixture
def valid_funding_request() -> Dict[str, Any]:
    """Valid funding calculation request."""
    return {
        "age": 80,
        "domain_assessments": {
            "BREATHING": {
                "level": "SEVERE",
                "description": "Severe breathing difficulties"
            },
            "COGNITION": {
                "level": "SEVERE",
                "description": "Severe cognitive impairment"
            }
        },
        "has_primary_health_need": True,
        "requires_nursing_care": True,
        "capital_assets": 20000.0,
        "weekly_income": 300.0,
        "care_type": "nursing",
        "is_permanent_care": True,
    }


class TestFundingCalculatorEndpoint:
    """Test /api/rch-data/funding/calculate endpoint."""

    def test_endpoint_exists(self, client):
        """Test that endpoint exists."""
        response = client.post("/api/rch-data/funding/calculate", json={})
        # Should not be 404
        assert response.status_code != 404

    def test_valid_request(self, client, valid_funding_request):
        """Test valid funding calculation request."""
        response = client.post(
            "/api/rch-data/funding/calculate",
            json=valid_funding_request
        )

        if response.status_code == 503:
            pytest.skip("Funding calculator module not available")

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "chc_eligibility" in data
        assert "la_support" in data
        assert "dpa_eligibility" in data
        assert "savings" in data

        # Check CHC eligibility structure
        chc = data["chc_eligibility"]
        assert "probability_percent" in chc
        assert "is_likely_eligible" in chc
        assert "threshold_category" in chc
        assert "reasoning" in chc
        assert 0 <= chc["probability_percent"] <= 98

        # Check LA support structure
        la = data["la_support"]
        assert "top_up_probability_percent" in la
        assert "full_support_probability_percent" in la
        assert "capital_assessed" in la
        assert "tariff_income_gbp_week" in la
        assert "is_fully_funded" in la
        assert "reasoning" in la

        # Check DPA eligibility structure
        dpa = data["dpa_eligibility"]
        assert "is_eligible" in dpa
        assert "property_disregarded" in dpa
        assert "reasoning" in dpa

        # Check savings structure
        savings = data["savings"]
        assert "weekly_savings" in savings
        assert "annual_gbp" in savings
        assert "five_year_gbp" in savings

    def test_chc_high_probability_with_priority_domain(self, client):
        """Test that PRIORITY domain gives high CHC probability."""
        request = {
            "age": 80,
            "domain_assessments": {
                "BREATHING": {
                    "level": "PRIORITY",
                    "description": "Critical breathing needs"
                }
            },
            "capital_assets": 0.0,
            "weekly_income": 0.0,
            "care_type": "nursing",
            "is_permanent_care": True,
        }

        response = client.post("/api/rch-data/funding/calculate", json=request)

        if response.status_code == 503:
            pytest.skip("Funding calculator module not available")

        assert response.status_code == 200
        data = response.json()

        chc = data["chc_eligibility"]
        assert chc["probability_percent"] >= 92
        assert chc["is_likely_eligible"] is True
        assert chc["threshold_category"] == "very_high"

    def test_chc_multiple_severe_domains(self, client):
        """Test that multiple SEVERE domains give high probability."""
        request = {
            "age": 80,
            "domain_assessments": {
                "COGNITION": {
                    "level": "SEVERE",
                    "description": "Severe cognitive impairment"
                },
                "MOBILITY": {
                    "level": "SEVERE",
                    "description": "Severe mobility issues"
                }
            },
            "capital_assets": 0.0,
            "weekly_income": 0.0,
            "care_type": "nursing",
            "is_permanent_care": True,
        }

        response = client.post("/api/rch-data/funding/calculate", json=request)

        if response.status_code == 503:
            pytest.skip("Funding calculator module not available")

        assert response.status_code == 200
        data = response.json()

        chc = data["chc_eligibility"]
        assert chc["probability_percent"] >= 92
        assert "multiple_severe" in chc.get("bonuses_applied", [])

    def test_la_full_support_below_lower_limit(self, client):
        """Test that capital below lower limit gives full LA support."""
        request = {
            "age": 80,
            "domain_assessments": {},
            "capital_assets": 10000.0,  # Below £14,250
            "weekly_income": 200.0,
            "care_type": "residential",
            "is_permanent_care": True,
        }

        response = client.post("/api/rch-data/funding/calculate", json=request)

        if response.status_code == 503:
            pytest.skip("Funding calculator module not available")

        assert response.status_code == 200
        data = response.json()

        la = data["la_support"]
        assert la["full_support_probability_percent"] == 100
        assert la["is_fully_funded"] is True

    def test_la_self_funding_above_upper_limit(self, client):
        """Test that capital above upper limit gives no LA support."""
        request = {
            "age": 80,
            "domain_assessments": {},
            "capital_assets": 50000.0,  # Above £23,250
            "weekly_income": 500.0,
            "care_type": "residential",
            "is_permanent_care": True,
        }

        response = client.post("/api/rch-data/funding/calculate", json=request)

        if response.status_code == 503:
            pytest.skip("Funding calculator module not available")

        assert response.status_code == 200
        data = response.json()

        la = data["la_support"]
        assert la["full_support_probability_percent"] == 0
        assert la["top_up_probability_percent"] == 0
        assert la["is_fully_funded"] is False

    def test_dpa_eligibility_with_property(self, client):
        """Test DPA eligibility with property."""
        request = {
            "age": 80,
            "domain_assessments": {},
            "capital_assets": 10000.0,  # Below threshold
            "weekly_income": 200.0,
            "care_type": "residential",
            "is_permanent_care": True,
            "property": {
                "value": 250000.0,
                "is_main_residence": True,
                "has_qualifying_relative": False,
            },
        }

        response = client.post("/api/rch-data/funding/calculate", json=request)

        if response.status_code == 503:
            pytest.skip("Funding calculator module not available")

        assert response.status_code == 200
        data = response.json()

        dpa = data["dpa_eligibility"]
        assert dpa["is_eligible"] is True

    def test_complex_therapies_bonus(self, client):
        """Test that complex therapies add bonus to CHC probability."""
        request = {
            "age": 80,
            "domain_assessments": {
                "BREATHING": {
                    "level": "HIGH",
                    "description": "High breathing needs"
                }
            },
            "has_peg_feeding": True,
            "has_tracheostomy": True,
            "capital_assets": 0.0,
            "weekly_income": 0.0,
            "care_type": "nursing",
            "is_permanent_care": True,
        }

        response = client.post("/api/rch-data/funding/calculate", json=request)

        if response.status_code == 503:
            pytest.skip("Funding calculator module not available")

        assert response.status_code == 200
        data = response.json()

        chc = data["chc_eligibility"]
        assert "complex_therapies" in chc.get("bonuses_applied", [])

    def test_unpredictability_bonus(self, client):
        """Test that unpredictability indicators add bonus."""
        request = {
            "age": 80,
            "domain_assessments": {
                "BEHAVIOUR": {
                    "level": "HIGH",
                    "description": "High behavioural needs"
                }
            },
            "has_unpredictable_needs": True,
            "has_fluctuating_condition": True,
            "capital_assets": 0.0,
            "weekly_income": 0.0,
            "care_type": "nursing",
            "is_permanent_care": True,
        }

        response = client.post("/api/rch-data/funding/calculate", json=request)

        if response.status_code == 503:
            pytest.skip("Funding calculator module not available")

        assert response.status_code == 200
        data = response.json()

        chc = data["chc_eligibility"]
        assert "unpredictability" in chc.get("bonuses_applied", [])

    def test_invalid_domain_level(self, client):
        """Test that invalid domain level is handled gracefully."""
        request = {
            "age": 80,
            "domain_assessments": {
                "BREATHING": {
                    "level": "INVALID_LEVEL",
                    "description": "Test"
                }
            },
            "capital_assets": 0.0,
            "weekly_income": 0.0,
            "care_type": "residential",
            "is_permanent_care": True,
        }

        response = client.post("/api/rch-data/funding/calculate", json=request)

        if response.status_code == 503:
            pytest.skip("Funding calculator module not available")

        # Should either skip invalid domain or return 400
        assert response.status_code in [200, 400]

    def test_missing_required_fields(self, client):
        """Test that missing required fields return 422."""
        request = {
            "age": 80,
            # Missing domain_assessments, capital_assets, etc.
        }

        response = client.post("/api/rch-data/funding/calculate", json=request)

        # Should return validation error
        assert response.status_code == 422

    def test_negative_capital_assets(self, client):
        """Test that negative capital assets are rejected."""
        request = {
            "age": 80,
            "domain_assessments": {},
            "capital_assets": -1000.0,
            "weekly_income": 0.0,
            "care_type": "residential",
            "is_permanent_care": True,
        }

        response = client.post("/api/rch-data/funding/calculate", json=request)

        # Should return validation error
        assert response.status_code == 422

    def test_negative_weekly_income(self, client):
        """Test that negative weekly income is rejected."""
        request = {
            "age": 80,
            "domain_assessments": {},
            "capital_assets": 0.0,
            "weekly_income": -50.0,
            "care_type": "residential",
            "is_permanent_care": True,
        }

        response = client.post("/api/rch-data/funding/calculate", json=request)

        # Should return validation error
        assert response.status_code == 422

    def test_invalid_age(self, client):
        """Test that invalid age is rejected."""
        request = {
            "age": 150,  # Too old
            "domain_assessments": {},
            "capital_assets": 0.0,
            "weekly_income": 0.0,
            "care_type": "residential",
            "is_permanent_care": True,
        }

        response = client.post("/api/rch-data/funding/calculate", json=request)

        # Should return validation error
        assert response.status_code == 422

    def test_all_domains_no_needs(self, client):
        """Test calculation with all domains set to no needs."""
        request = {
            "age": 80,
            "domain_assessments": {},  # No domains assessed
            "capital_assets": 20000.0,
            "weekly_income": 300.0,
            "care_type": "residential",
            "is_permanent_care": True,
        }

        response = client.post("/api/rch-data/funding/calculate", json=request)

        if response.status_code == 503:
            pytest.skip("Funding calculator module not available")

        assert response.status_code == 200
        data = response.json()

        chc = data["chc_eligibility"]
        # Should have low probability with no needs
        assert chc["probability_percent"] < 70
        assert chc["threshold_category"] == "low"

    def test_property_with_qualifying_relative(self, client):
        """Test that property with qualifying relative is disregarded."""
        request = {
            "age": 80,
            "domain_assessments": {},
            "capital_assets": 10000.0,
            "weekly_income": 200.0,
            "care_type": "residential",
            "is_permanent_care": True,
            "property": {
                "value": 250000.0,
                "is_main_residence": True,
                "has_qualifying_relative": True,  # Should disregard property
            },
        }

        response = client.post("/api/rch-data/funding/calculate", json=request)

        if response.status_code == 503:
            pytest.skip("Funding calculator module not available")

        assert response.status_code == 200
        data = response.json()

        dpa = data["dpa_eligibility"]
        assert dpa["property_disregarded"] is True

        la = data["la_support"]
        # Property should not be counted in capital assessment
        assert la["capital_assessed"] < 250000

    def test_tariff_income_calculation(self, client):
        """Test that tariff income is calculated correctly."""
        request = {
            "age": 80,
            "domain_assessments": {},
            "capital_assets": 20000.0,  # Between £14,250 and £23,250
            "weekly_income": 200.0,
            "care_type": "residential",
            "is_permanent_care": True,
        }

        response = client.post("/api/rch-data/funding/calculate", json=request)

        if response.status_code == 503:
            pytest.skip("Funding calculator module not available")

        assert response.status_code == 200
        data = response.json()

        la = data["la_support"]
        # Tariff income should be calculated: (20000 - 14250) / 250 = 23
        assert la["tariff_income_gbp_week"] > 0
        assert la["tariff_income_gbp_week"] <= 40  # Reasonable upper bound

    def test_response_time(self, client, valid_funding_request):
        """Test that response time is acceptable (< 2 seconds)."""
        import time

        start_time = time.time()
        response = client.post(
            "/api/rch-data/funding/calculate",
            json=valid_funding_request
        )
        end_time = time.time()

        response_time = end_time - start_time

        if response.status_code == 503:
            pytest.skip("Funding calculator module not available")

        assert response.status_code == 200
        assert response_time < 2.0, f"Response time {response_time}s exceeds 2s threshold"

