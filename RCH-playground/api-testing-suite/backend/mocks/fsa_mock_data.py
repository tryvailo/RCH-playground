"""
FSA Mock Data
Sample data for FSA FHRS API endpoints (used when live API unavailable)
"""
from typing import Dict, List, Any
from copy import deepcopy

FSA_SAMPLE_FHRS_ID = 192203

FSA_SAMPLE_DATA = {
    "establishments": [
        {
            "FHRSID": 192203,
            "fhrsId": 192203,
            "BusinessName": "The Meadows Care Centre",
            "businessName": "The Meadows Care Centre",
            "BusinessType": "Hospitals/Childcare/Caring Premises",
            "BusinessTypeID": 7835,
            "RatingValue": 5,
            "ratingValue": 5,
            "RatingKey": "fhrs_5_en-gb",
            "ratingKey": "fhrs_5_en-gb",
            "RatingDate": "2024-10-30",
            "ratingDate": "2024-10-30",
            "AddressLine1": "100 Meadow Lane",
            "addressLine1": "100 Meadow Lane",
            "AddressLine2": "Kingston Upon Hull",
            "addressLine2": "Kingston Upon Hull",
            "PostCode": "HU5 1AB",
            "postcode": "HU5 1AB",
            "LocalAuthorityCode": "E06000010",
            "LocalAuthorityName": "Kingston upon Hull City Council",
            "geocode": {"longitude": "-0.368", "latitude": "53.744"},
            "Scores": {
                "Hygiene": 0,
                "Structural": 5,
                "ConfidenceInManagement": 5
            },
            "NewRatingPending": False,
            "SchemeType": "FHRS",
            "links": {
                "EstablishmentDetail": "https://ratings.food.gov.uk/business/en-GB/192203"
            }
        },
        {
            "FHRSID": 997221,
            "fhrsId": 997221,
            "BusinessName": "Riverside View Nursing Home",
            "businessName": "Riverside View Nursing Home",
            "BusinessType": "Hospitals/Childcare/Caring Premises",
            "BusinessTypeID": 7835,
            "RatingValue": 4,
            "ratingValue": 4,
            "RatingKey": "fhrs_4_en-gb",
            "ratingKey": "fhrs_4_en-gb",
            "RatingDate": "2023-11-18",
            "ratingDate": "2023-11-18",
            "AddressLine1": "48 Riverside Road",
            "addressLine1": "48 Riverside Road",
            "AddressLine2": "Leeds",
            "addressLine2": "Leeds",
            "PostCode": "LS5 3HG",
            "postcode": "LS5 3HG",
            "LocalAuthorityCode": "E08000035",
            "LocalAuthorityName": "Leeds City Council",
            "geocode": {"longitude": "-1.599", "latitude": "53.822"},
            "Scores": {
                "Hygiene": 5,
                "Structural": 10,
                "ConfidenceInManagement": 5
            },
            "NewRatingPending": False,
            "SchemeType": "FHRS",
            "links": {
                "EstablishmentDetail": "https://ratings.food.gov.uk/business/en-GB/997221"
            }
        }
    ],
    "details": {
        "FHRSID": 192203,
        "fhrsId": 192203,
        "BusinessName": "The Meadows Care Centre",
        "BusinessType": "Hospitals/Childcare/Caring Premises",
        "BusinessTypeID": 7835,
        "RatingValue": 5,
        "RatingKey": "fhrs_5_en-gb",
        "RatingDate": "2024-10-30",
        "AddressLine1": "100 Meadow Lane",
        "AddressLine2": "Kingston Upon Hull",
        "PostCode": "HU5 1AB",
        "LocalAuthorityCode": "E06000010",
        "LocalAuthorityName": "Kingston upon Hull City Council",
        "LocalAuthorityWebSite": "http://www.hullcc.gov.uk",
        "geocode": {"longitude": "-0.368", "latitude": "53.744"},
        "scores": {
            "hygiene": 0,
            "structural": 5,
            "confidence_in_management": 5
        },
        "breakdown_scores": {
            "hygiene": 0,
            "structural": 5,
            "confidence_in_management": 5,
            "hygiene_label": "Very good",
            "structural_label": "Good",
            "confidence_label": "Good"
        },
        "LastInspectionDate": "2024-10-30",
        "links": {
            "EstablishmentDetail": "https://ratings.food.gov.uk/business/en-GB/192203"
        }
    },
    "history": [
        {
            "date": "2024-10-30",
            "rating": 5,
            "rating_key": "fhrs_5_en-gb",
            "inspection_type": "Full",
            "local_authority": "Kingston upon Hull City Council"
        },
        {
            "date": "2023-09-12",
            "rating": 4,
            "rating_key": "fhrs_4_en-gb",
            "inspection_type": "Full",
            "local_authority": "Kingston upon Hull City Council"
        },
        {
            "date": "2022-08-05",
            "rating": 5,
            "rating_key": "fhrs_5_en-gb",
            "inspection_type": "Full",
            "local_authority": "Kingston upon Hull City Council"
        },
        {
            "date": "2021-06-15",
            "rating": 5,
            "rating_key": "fhrs_5_en-gb",
            "inspection_type": "Full",
            "local_authority": "Kingston upon Hull City Council"
        }
    ],
    "trends": {
        "current_rating": 5,
        "rating_date": "2024-10-30",
        "trend": "improving",
        "history_count": 4,
        "consistency": "consistently high",
        "prediction": {
            "predicted_rating": 5,
            "predicted_label": "fhrs_5_en-gb",
            "confidence": "High"
        },
        "breakdown_scores": {
            "hygiene": 0,
            "structural": 5,
            "confidence_in_management": 5
        }
    },
    "diabetes_score": {
        "score": 86,
        "label": "Suitable for diabetic residents",
        "recommendation": "Strong controls in place for diabetic diets and monitoring.",
        "breakdown": [
            "Kitchen staff trained on diabetic meal plans",
            "Dedicated nutrition monitoring log",
            "Regular GP coordination for residents with diabetes"
        ],
        "max_score": 100
    },
    "premium": {
        "enhanced_history": [
            {
                "date": "2024-10-30",
                "rating": 5,
                "rating_key": "fhrs_5_en-gb",
                "breakdown_scores": {"hygiene": 0, "structural": 5, "confidence_in_management": 5},
                "local_authority": "Kingston upon Hull City Council",
                "inspection_type": "Full"
            },
            {
                "date": "2023-09-12",
                "rating": 4,
                "rating_key": "fhrs_4_en-gb",
                "breakdown_scores": {"hygiene": 5, "structural": 10, "confidence_in_management": 5},
                "local_authority": "Kingston upon Hull City Council",
                "inspection_type": "Full"
            },
            {
                "date": "2022-08-05",
                "rating": 5,
                "rating_key": "fhrs_5_en-gb",
                "breakdown_scores": {"hygiene": 0, "structural": 5, "confidence_in_management": 5},
                "local_authority": "Kingston upon Hull City Council",
                "inspection_type": "Full"
            }
        ],
        "monitoring_alerts": [
            {
                "type": "info",
                "message": "Inspection scheduled within the next 6 months",
                "severity": "low",
                "date": "2025-02-01"
            }
        ],
        "trends": {
            "trend": "stable",
            "consistency": "consistently high",
            "history_count": 4
        },
        "diabetes_score": {
            "score": 86,
            "label": "Suitable for diabetic residents",
            "recommendation": "Strong controls in place for diabetic diets and monitoring."
        },
        "monitoring_status": "active",
        "last_check": "2025-01-05T09:00:00Z",
        "next_check": "2025-01-12T09:00:00Z"
    },
    "health_score": {
        "score": 92,
        "confidence": "High",
        "supporting_factors": [
            "Zero hygiene issues in latest inspection",
            "Strong structural upkeep noted by inspectors",
            "Management systems rated as very good"
        ]
    }
}


def get_fsa_sample_establishments() -> List[Dict[str, Any]]:
    """Get sample FSA establishments"""
    return deepcopy(FSA_SAMPLE_DATA["establishments"])


def get_fsa_sample_details(fhrs_id: int) -> Dict[str, Any]:
    """Get sample FSA establishment details"""
    sample = deepcopy(FSA_SAMPLE_DATA["details"])
    sample["FHRSID"] = fhrs_id
    sample["fhrsId"] = fhrs_id
    return sample


def get_fsa_sample_history(fhrs_id: int) -> List[Dict[str, Any]]:
    """Get sample FSA inspection history"""
    history = deepcopy(FSA_SAMPLE_DATA["history"])
    for entry in history:
        entry.setdefault("fhrs_id", fhrs_id)
    return history


def get_fsa_sample_trends(fhrs_id: int) -> Dict[str, Any]:
    """Get sample FSA trends"""
    sample = deepcopy(FSA_SAMPLE_DATA["trends"])
    sample["fhrs_id"] = fhrs_id
    return sample


def get_fsa_sample_diabetes_score(fhrs_id: int) -> Dict[str, Any]:
    """Get sample FSA diabetes score"""
    sample = deepcopy(FSA_SAMPLE_DATA["diabetes_score"])
    sample["fhrs_id"] = fhrs_id
    return sample


def get_fsa_sample_premium(fhrs_id: int) -> Dict[str, Any]:
    """Get sample FSA premium data"""
    sample = deepcopy(FSA_SAMPLE_DATA["premium"])
    sample["fhrs_id"] = fhrs_id
    return sample


def get_fsa_sample_health_score(fhrs_id: int) -> Dict[str, Any]:
    """Get sample FSA health score"""
    sample = deepcopy(FSA_SAMPLE_DATA["health_score"])
    sample["fhrs_id"] = fhrs_id
    return sample

