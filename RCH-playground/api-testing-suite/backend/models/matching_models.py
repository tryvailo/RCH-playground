"""
Matching Models
Data types for 50-point matching algorithm
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class MatchingInputs:
    """Inputs для matching algorithm с поддержкой приоритетов"""
    postcode: str
    budget: Optional[float] = None
    care_type: Optional[str] = None
    user_lat: Optional[float] = None
    user_lon: Optional[float] = None
    max_distance_miles: Optional[float] = None
    
    # Новые поля из опросников (опционально)
    location_postcode: Optional[str] = None
    timeline: Optional[str] = None  # "urgent" | "1_month" | "2_3_months" | "6_plus_months"
    medical_conditions: Optional[List[str]] = None
    max_distance_km: Optional[float] = None
    priority_order: Optional[List[str]] = None  # ["quality", "cost", "proximity"]
    priority_weights: Optional[List[int]] = None  # [50, 30, 20] (сумма = 100)
    
    def __post_init__(self):
        """Валидация после инициализации"""
        # Использовать location_postcode если postcode не указан
        if not self.postcode and self.location_postcode:
            self.postcode = self.location_postcode
        
        # Валидация priority_weights
        if self.priority_weights:
            total = sum(self.priority_weights)
            if total != 100 and total > 0:
                # Нормализовать веса
                self.priority_weights = [int(w * 100 / total) for w in self.priority_weights]
        
        # Дефолтные приоритеты если не указаны
        if not self.priority_order:
            self.priority_order = ["quality", "cost", "proximity"]
        if not self.priority_weights:
            self.priority_weights = [40, 35, 25]  # Сбалансированные
    
    def get_max_distance_km(self) -> float:
        """Получить максимальное расстояние в км"""
        if self.max_distance_km:
            return self.max_distance_km
        if self.max_distance_miles:
            return self.max_distance_miles * 1.60934
        return 30.0  # Дефолт для FREE Report
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for compatibility"""
        return {
            'postcode': self.postcode,
            'budget': self.budget,
            'care_type': self.care_type,
            'user_lat': self.user_lat,
            'user_lon': self.user_lon,
            'max_distance_miles': self.max_distance_miles,
            'location_postcode': self.location_postcode,
            'timeline': self.timeline,
            'medical_conditions': self.medical_conditions,
            'max_distance_km': self.max_distance_km,
            'priority_order': self.priority_order,
            'priority_weights': self.priority_weights
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

