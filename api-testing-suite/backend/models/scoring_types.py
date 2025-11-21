"""
Scoring Types
Type definitions for scoring settings to ensure consistency between frontend and backend
"""
from typing import Dict, TypedDict, Optional


class ScoringWeightsDict(TypedDict, total=False):
    """Scoring weights structure (matches frontend ScoringWeights)"""
    location: int
    cqc: int
    budget: int
    careType: int  # camelCase to match frontend
    availability: int
    googleReviews: int  # camelCase to match frontend


class LocationThresholdsDict(TypedDict, total=False):
    """Location scoring thresholds"""
    within5Miles: int
    within10Miles: int
    within15Miles: int
    over15Miles: int


class BudgetThresholdsDict(TypedDict, total=False):
    """Budget scoring thresholds"""
    withinBudget: int
    plus50: int
    plus100: int
    plus200: int


class GoogleReviewsThresholdsDict(TypedDict, total=False):
    """Google Reviews scoring thresholds"""
    highRating: int
    goodRatingManyReviews: int
    goodRatingFewReviews: int
    mediumRatingMany: int
    mediumRatingFew: int


class ScoringThresholdsDict(TypedDict, total=False):
    """Scoring thresholds structure (matches frontend ScoringThresholds)"""
    location: LocationThresholdsDict
    budget: BudgetThresholdsDict
    googleReviews: GoogleReviewsThresholdsDict  # camelCase to match frontend


def normalize_scoring_weights(weights: Dict) -> ScoringWeightsDict:
    """
    Normalize scoring weights to ensure camelCase keys
    
    Args:
        weights: Dict with potentially mixed naming (camelCase or snake_case)
    
    Returns:
        Normalized weights dict with camelCase keys
    """
    normalized = {}
    key_mapping = {
        'care_type': 'careType',
        'google_reviews': 'googleReviews',
    }
    
    for key, value in weights.items():
        normalized_key = key_mapping.get(key, key)
        normalized[normalized_key] = int(value)
    
    return normalized


def normalize_scoring_thresholds(thresholds: Dict) -> ScoringThresholdsDict:
    """
    Normalize scoring thresholds to ensure camelCase keys
    
    Args:
        thresholds: Dict with potentially mixed naming
    
    Returns:
        Normalized thresholds dict with camelCase keys
    """
    normalized = {}
    
    if 'location' in thresholds:
        normalized['location'] = thresholds['location']
    
    if 'budget' in thresholds:
        normalized['budget'] = thresholds['budget']
    
    if 'google_reviews' in thresholds:
        normalized['googleReviews'] = thresholds['google_reviews']
    elif 'googleReviews' in thresholds:
        normalized['googleReviews'] = thresholds['googleReviews']
    
    return normalized

