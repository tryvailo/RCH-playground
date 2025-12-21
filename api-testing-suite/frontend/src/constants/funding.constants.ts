// AUTO-GENERATED from RCH-data/src/funding_calculator/constants.py
// DO NOT EDIT MANUALLY - changes will be overwritten

export const DOMAIN_LEVELS = {
  "NO": "no",
  "LOW": "low",
  "MODERATE": "moderate",
  "HIGH": "high",
  "SEVERE": "severe",
  "PRIORITY": "priority"
} as const;

export const DOMAINS = {
  "BREATHING": "breathing",
  "NUTRITION": "nutrition",
  "CONTINENCE": "continence",
  "SKIN": "skin_integrity",
  "MOBILITY": "mobility",
  "COMMUNICATION": "communication",
  "PSYCHOLOGICAL": "psychological_emotional",
  "COGNITION": "cognition",
  "BEHAVIOUR": "behaviour",
  "DRUG_THERAPIES": "drug_therapies",
  "ALTERED_STATES": "altered_states_of_consciousness",
  "OTHER": "other_significant_needs"
} as const;

export const CHC_WEIGHTS = {
  "priority": 45,
  "severe": 20,
  "high": 9
} as const;

export const CHC_BONUSES = {
  "multiple_severe": 25,
  "unpredictability": 15,
  "multiple_high": 10,
  "complex_therapies": 8
} as const;

export const CHC_THRESHOLDS = {
  "very_high": {
    "min": 92,
    "max": 98,
    "conditions": [
      "\u22651 Priority",
      "\u22652 Severe",
      "1 Severe + \u22654 High"
    ]
  },
  "high": {
    "min": 82,
    "max": 91,
    "conditions": [
      "1 Severe + 2-3 High"
    ]
  },
  "moderate": {
    "min": 70,
    "max": 81,
    "conditions": [
      "\u22655 High"
    ]
  },
  "low": {
    "min": 0,
    "max": 69,
    "conditions": [
      "All other cases"
    ]
  }
} as const;

export const MEANS_TEST = {
  "upper_capital_limit": 23250,
  "lower_capital_limit": 14250,
  "tariff_income_rate": 250,
  "personal_expenses_allowance": 28.25,
  "minimum_income_guarantee": 189.6
} as const;

export const CARE_TYPES = {
  "residential": {
    "label": "Residential Care",
    "description": "Care home providing accommodation and personal care",
    "has_nursing": false,
    "average_weekly_cost": 800
  },
  "nursing": {
    "label": "Nursing Care",
    "description": "Nursing home providing nursing and personal care",
    "has_nursing": true,
    "average_weekly_cost": 1200
  },
  "residential_dementia": {
    "label": "Residential Dementia Care",
    "description": "Specialized residential care for dementia",
    "has_nursing": false,
    "average_weekly_cost": 900
  },
  "nursing_dementia": {
    "label": "Nursing Dementia Care",
    "description": "Specialized nursing care for dementia",
    "has_nursing": true,
    "average_weekly_cost": 1300
  },
  "respite": {
    "label": "Respite Care",
    "description": "Temporary/short-term care",
    "has_nursing": false,
    "average_weekly_cost": 700
  }
} as const;

export const VALIDATION_RULES = {
  "age": {
    "min": 18,
    "max": 110,
    "error_message": "Age must be between 18 and 110 years",
    "type": "integer"
  },
  "capital_assets": {
    "min": 0,
    "max": 1000000,
    "error_message": "Capital assets must be between \u00a30 and \u00a31,000,000",
    "type": "number"
  },
  "weekly_income": {
    "min": 0,
    "max": 5000,
    "error_message": "Weekly income must be between \u00a30 and \u00a35,000",
    "type": "number"
  },
  "property_value": {
    "min": 0,
    "max": 5000000,
    "error_message": "Property value must be between \u00a30 and \u00a35,000,000",
    "type": "number"
  },
  "care_cost_per_week": {
    "min": 100,
    "max": 10000,
    "error_message": "Weekly care cost must be between \u00a3100 and \u00a310,000",
    "type": "number"
  }
} as const;

export const FEATURES = {
  "llm_insights": true,
  "dpa_calculator": true,
  "caching": true,
  "fair_cost_gap": true,
  "five_year_projections": true
} as const;

export const VERSION = {
  "calculator_version": "2025.12.21",
  "framework_year": 2025,
  "framework_version": "2.0",
  "last_backtested": "2024-12-15",
  "backtested_cases": 1247
} as const;