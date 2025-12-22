"""Pytest configuration and fixtures"""
import pytest
import json
from pathlib import Path


@pytest.fixture
def sample_questionnaire():
    """Load sample questionnaire for testing"""
    return {
        "postcode": "SW1A 1AA",
        "budget": 1200.0,
        "care_type": "residential",
        "chc_probability": 35.5,
    }


@pytest.fixture
def mock_care_home():
    """Mock care home data"""
    return {
        "name": "Test Care Home",
        "address": "123 High Street",
        "postcode": "SW1A 1AA",
        "weekly_cost": 1200,
        "rating": "Good",
        "cqc_rating_overall": "Good",
        "care_types": ["residential"],
        "beds_available": 5,
        "latitude": 51.5074,
        "longitude": -0.1278,
        "distance_km": 2.5,
    }


@pytest.fixture
def sample_questionnaires_dir():
    """Get path to sample questionnaires"""
    return (
        Path(__file__).parent.parent.parent / "frontend" / "public" / "sample_questionnaires"
    )


@pytest.fixture
def load_sample_questionnaire(sample_questionnaires_dir):
    """Load a sample questionnaire file"""

    def _load(filename: str):
        filepath = sample_questionnaires_dir / filename
        if filepath.exists():
            with open(filepath) as f:
                return json.load(f)
        return None

    return _load


@pytest.fixture
def sample_care_homes():
    """Return list of sample care homes for testing"""
    return [
        {
            "name": "Sunshine Care Home",
            "address": "123 High Street",
            "postcode": "SW1A 1AA",
            "weekly_cost": 1200,
            "rating": "Good",
            "cqc_rating_overall": "Good",
            "care_types": ["residential"],
            "beds_available": 5,
            "latitude": 51.5074,
            "longitude": -0.1278,
            "distance_km": 2.5,
        },
        {
            "name": "Greenfield Manor",
            "address": "456 Park Avenue",
            "postcode": "SW1A 2BB",
            "weekly_cost": 950,
            "rating": "Good",
            "cqc_rating_overall": "Good",
            "care_types": ["residential", "dementia"],
            "beds_available": 3,
            "latitude": 51.5100,
            "longitude": -0.1300,
            "distance_km": 3.2,
        },
        {
            "name": "Elmwood House",
            "address": "789 Garden Road",
            "postcode": "SW1A 3CC",
            "weekly_cost": 1400,
            "rating": "Outstanding",
            "cqc_rating_overall": "Outstanding",
            "care_types": ["residential", "nursing"],
            "beds_available": 2,
            "latitude": 51.5050,
            "longitude": -0.1250,
            "distance_km": 1.8,
        },
    ]
