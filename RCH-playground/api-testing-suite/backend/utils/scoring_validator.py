"""
Scoring Settings Validator
Validates and normalizes scoring weights and thresholds
"""
from typing import Dict, Any, Optional, Tuple

# Try to import scoring types for better type safety
try:
    from models.scoring_types import (
        ScoringWeightsDict,
        ScoringThresholdsDict,
        normalize_scoring_weights,
        normalize_scoring_thresholds
    )
    SCORING_TYPES_AVAILABLE = True
except ImportError:
    SCORING_TYPES_AVAILABLE = False


def validate_scoring_weights(weights: Optional[Dict[str, int]]) -> Dict[str, int]:
    """
    Validate and normalize scoring weights
    
    Args:
        weights: Dict with weights for each category
    
    Returns:
        Validated and normalized weights dict
    
    Raises:
        ValueError: If weights are invalid
    """
    if weights is None:
        return {}
    
    # Normalize keys: convert snake_case to camelCase
    if SCORING_TYPES_AVAILABLE:
        normalized_weights = normalize_scoring_weights(weights)
    else:
        normalized_weights = {}
        key_mapping = {
            'care_type': 'careType',
            'google_reviews': 'googleReviews',
        }
        for key, value in weights.items():
            normalized_key = key_mapping.get(key, key)
            normalized_weights[normalized_key] = value
    
    # Required keys (in camelCase)
    required_keys = ['location', 'cqc', 'budget', 'careType', 'availability', 'googleReviews']
    
    # Check all required keys are present
    for key in required_keys:
        if key not in normalized_weights:
            raise ValueError(f"Missing required weight key: {key}")
    
    # Validate values
    for key, value in normalized_weights.items():
        if not isinstance(value, (int, float)):
            raise ValueError(f"Invalid weight value for {key}: must be a number, got {type(value)}")
        if value < 0:
            raise ValueError(f"Invalid weight value for {key}: must be >= 0, got {value}")
        if value > 100:
            raise ValueError(f"Invalid weight value for {key}: must be <= 100, got {value}")
    
    # Normalize weights to sum to 100
    total = sum(normalized_weights.values())
    if total == 0:
        raise ValueError("Total weight cannot be 0")
    
    if total != 100:
        # Scale proportionally
        normalized = {}
        for key, value in normalized_weights.items():
            normalized[key] = int((value / total) * 100)
        return normalized
    
    return {k: int(v) for k, v in normalized_weights.items()}


def validate_scoring_thresholds(thresholds: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate scoring thresholds
    
    Args:
        thresholds: Dict with thresholds for location, budget, googleReviews
    
    Returns:
        Validated thresholds dict
    
    Raises:
        ValueError: If thresholds are invalid
    """
    if thresholds is None:
        return {}
    
    validated = {}
    
    # Validate location thresholds
    if 'location' in thresholds:
        loc_thresholds = thresholds['location']
        if not isinstance(loc_thresholds, dict):
            raise ValueError("location thresholds must be a dict")
        
        required_loc_keys = ['within5Miles', 'within10Miles', 'within15Miles', 'over15Miles']
        validated_loc = {}
        for key in required_loc_keys:
            if key not in loc_thresholds:
                raise ValueError(f"Missing location threshold: {key}")
            value = loc_thresholds[key]
            if not isinstance(value, (int, float)) or value < 0 or value > 100:
                raise ValueError(f"Invalid location threshold {key}: must be 0-100, got {value}")
            validated_loc[key] = int(value)
        validated['location'] = validated_loc
    
    # Validate budget thresholds
    if 'budget' in normalized_thresholds:
        budget_thresholds = normalized_thresholds['budget']
        if not isinstance(budget_thresholds, dict):
            raise ValueError("budget thresholds must be a dict")
        
        required_budget_keys = ['withinBudget', 'plus50', 'plus100', 'plus200']
        validated_budget = {}
        for key in required_budget_keys:
            if key not in budget_thresholds:
                raise ValueError(f"Missing budget threshold: {key}")
            value = budget_thresholds[key]
            if not isinstance(value, (int, float)) or value < 0 or value > 100:
                raise ValueError(f"Invalid budget threshold {key}: must be 0-100, got {value}")
            validated_budget[key] = int(value)
        validated['budget'] = validated_budget
    
    # Validate googleReviews thresholds
    if 'googleReviews' in normalized_thresholds:
        review_thresholds = normalized_thresholds['googleReviews']
        if not isinstance(review_thresholds, dict):
            raise ValueError("googleReviews thresholds must be a dict")
        
        required_review_keys = [
            'highRating', 'goodRatingManyReviews', 'goodRatingFewReviews',
            'mediumRatingMany', 'mediumRatingFew'
        ]
        validated_review = {}
        for key in required_review_keys:
            if key not in review_thresholds:
                raise ValueError(f"Missing googleReviews threshold: {key}")
            value = review_thresholds[key]
            if not isinstance(value, (int, float)) or value < 0 or value > 100:
                raise ValueError(f"Invalid googleReviews threshold {key}: must be 0-100, got {value}")
            validated_review[key] = int(value)
        validated['googleReviews'] = validated_review
    
    return validated


def validate_scoring_settings(
    weights: Optional[Dict[str, int]] = None,
    thresholds: Optional[Dict[str, Any]] = None
) -> Tuple[Dict[str, int], Dict[str, Any]]:
    """
    Validate both scoring weights and thresholds
    
    Args:
        weights: Scoring weights dict
        thresholds: Scoring thresholds dict
    
    Returns:
        Tuple of (validated_weights, validated_thresholds)
    
    Raises:
        ValueError: If validation fails
    """
    validated_weights = validate_scoring_weights(weights) if weights else {}
    validated_thresholds = validate_scoring_thresholds(thresholds) if thresholds else {}
    
    return validated_weights, validated_thresholds

