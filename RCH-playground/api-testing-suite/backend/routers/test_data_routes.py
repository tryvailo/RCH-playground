"""
Test Data Routes
Provides test data for API testing
"""
from fastapi import APIRouter
import json
import os
from pathlib import Path

router = APIRouter(prefix="/api", tags=["Test Data"])


@router.get("/test-data")
async def get_test_data():
    """Get test data for API testing (real UK care homes from CQC registry)"""
    test_data_path = os.path.join(os.path.dirname(__file__), "..", "test_data.json")
    try:
        with open(test_data_path, 'r') as f:
            test_data = json.load(f)
        return {"status": "success", "data": test_data}
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "Test data file not found",
            "data": {
                "fsa_test_care_homes": [
                    {
                        "name": "Kinross Residential Care Home",
                        "address": "201 Havant Road, Drayton, Portsmouth, Hampshire, PO6 1EE",
                        "city": "Portsmouth",
                        "postcode": "PO6 1EE",
                        "county": "Hampshire",
                        "source": "CQC Official Registry"
                    },
                    {
                        "name": "Meadows House Residential and Nursing Home",
                        "address": "Cullum Welch Court, London, SE3 0PW",
                        "city": "London",
                        "postcode": "SE3 0PW",
                        "county": "Greater London",
                        "source": "CQC Official Registry"
                    },
                    {
                        "name": "Roborough House",
                        "address": "Tamerton Road, Woolwell, Plymouth, Devon, PL6 7BQ",
                        "city": "Plymouth",
                        "postcode": "PL6 7BQ",
                        "county": "Devon",
                        "source": "CQC Official Registry"
                    }
                ],
                "companies_house_test_companies": [
                    {
                        "name": "Kinross Residential Care Home",
                        "address": "201 Havant Road, Drayton, Portsmouth, Hampshire, PO6 1EE",
                        "note": "Search by name to find company number"
                    },
                    {
                        "name": "Meadows House Residential and Nursing Home",
                        "address": "Cullum Welch Court, London, SE3 0PW",
                        "note": "Search by name to find company number"
                    },
                    {
                        "name": "Roborough House",
                        "address": "Tamerton Road, Woolwell, Plymouth, Devon, PL6 7BQ",
                        "note": "Search by name to find company number"
                    }
                ],
                "description": "Real UK care homes from CQC official registry for API testing",
                "last_updated": "2025-01-27"
            }
        }

