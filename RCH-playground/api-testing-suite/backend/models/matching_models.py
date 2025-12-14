"""
Matching Models
Data types for 50-point matching algorithm
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class MatchingInputs:
    """Inputs для matching algorithm"""
    postcode: str
    budget: Optional[float] = None
    care_type: Optional[str] = None
    user_lat: Optional[float] = None
    user_lon: Optional[float] = None
    max_distance_miles: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for compatibility"""
        return {
            'postcode': self.postcode,
            'budget': self.budget,
            'care_type': self.care_type,
            'user_lat': self.user_lat,
            'user_lon': self.user_lon,
            'max_distance_miles': self.max_distance_miles
        }


@dataclass
class MatchingScore:
    """50-point score breakdown"""
    location_score: int = 0
    cqc_score: int = 0
    budget_score: int = 0
    care_type_score: int = 0
    availability_score: int = 0
    google_reviews_score: int = 0
    total_score: int = 0
    
    def calculate_total(self):
        """Calculate total score from all components"""
        self.total_score = (
            self.location_score +
            self.cqc_score +
            self.budget_score +
            self.care_type_score +
            self.availability_score +
            self.google_reviews_score
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict"""
        return {
            'location': self.location_score,
            'cqc': self.cqc_score,
            'budget': self.budget_score,
            'care_type': self.care_type_score,
            'availability': self.availability_score,
            'google_reviews': self.google_reviews_score,
            'total': self.total_score
        }

