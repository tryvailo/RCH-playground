"""
Category Calculator Base Class

Abstract base for all 8 category scoring calculators in matching algorithm.
Each calculator scores a specific category (0-1.0) based on home data, user profile, and enriched data.

Categories:
1. Medical - Specialist care, nursing, equipment
2. Safety - CQC, FSA, safeguarding
3. Location - Distance, accessibility
4. Financial - Price, stability, benchmarks
5. Staff - Retention, qualifications, glassdoor
6. CQC - Overall rating, specific categories
7. Social - Activities, community
8. Services - Additional amenities

Total: 156 points distributed via weights across 8 categories
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class CategoryCalculator(ABC):
    """
    Abstract base class for category score calculation.
    
    All calculators:
    - Return score as float 0-1.0
    - Extract data from multiple sources (home, user_profile, enriched_data)
    - Handle missing/None values gracefully
    - Log warnings for suspicious data
    """
    
    # Override in subclasses
    CATEGORY_NAME: str = None
    MAX_POINTS: float = None  # e.g., 30.0 for medical
    
    @abstractmethod
    async def calculate(
        self,
        home: Dict[str, Any],
        user_profile: Dict[str, Any],
        enriched_data: Dict[str, Any]
    ) -> float:
        """
        Calculate category score.
        
        Args:
            home: Care home data (from DB/CSV)
            user_profile: User questionnaire response
            enriched_data: Enriched data from APIs (financial, staff, fsa, google, cqc)
        
        Returns:
            Score as float 0-1.0 (will be multiplied by weight and 156)
        """
        pass
    
    def _extract_field(
        self,
        obj: Dict[str, Any],
        *keys: str,
        default: Any = None
    ) -> Any:
        """
        Safe nested field extraction.
        
        Usage:
            self._extract_field(home, 'rating')
            self._extract_field(enriched, 'cqc_detailed', 'overall_rating')
        
        Args:
            obj: Dictionary to extract from
            *keys: Nested keys to follow
            default: Default value if not found
        
        Returns:
            Extracted value or default
        """
        current = obj
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return default
        return current if current is not None else default
    
    def _safe_float(
        self,
        value: Any,
        default: float = 0.0,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None
    ) -> float:
        """
        Safe conversion to float with bounds checking.
        
        Args:
            value: Value to convert
            default: Default if conversion fails
            min_val: Minimum allowed value
            max_val: Maximum allowed value
        
        Returns:
            Float value bounded by min/max
        """
        if value is None:
            return default
        
        try:
            result = float(value)
            if min_val is not None:
                result = max(result, min_val)
            if max_val is not None:
                result = min(result, max_val)
            return result
        except (ValueError, TypeError):
            return default
    
    def _safe_int(
        self,
        value: Any,
        default: int = 0,
        min_val: Optional[int] = None,
        max_val: Optional[int] = None
    ) -> int:
        """Safe conversion to int with bounds checking"""
        if value is None:
            return default
        
        try:
            result = int(value)
            if min_val is not None:
                result = max(result, min_val)
            if max_val is not None:
                result = min(result, max_val)
            return result
        except (ValueError, TypeError):
            return default
    
    def _safe_list(
        self,
        value: Any,
        default: Optional[List] = None
    ) -> List:
        """Safe conversion to list"""
        if default is None:
            default = []
        
        if isinstance(value, list):
            return value
        elif isinstance(value, str):
            return [value]
        elif value is None:
            return default
        else:
            return default
    
    def _normalize_string(self, value: Any, case: str = 'lower') -> str:
        """
        Normalize string value.
        
        Args:
            value: Value to normalize
            case: 'lower' or 'upper'
        
        Returns:
            Normalized string
        """
        if value is None:
            return ''
        
        s = str(value).strip()
        if case == 'lower':
            return s.lower()
        elif case == 'upper':
            return s.upper()
        else:
            return s
    
    def _score_with_scale(
        self,
        score: float,
        scale: Dict[tuple, float]
    ) -> float:
        """
        Score value using tiered scale.
        
        Example:
            scale = {
                (0, 5): 0.0,      # 0-5 gets 0
                (5, 15): 0.5,     # 5-15 gets 0.5
                (15, 20): 1.0     # 15+ gets 1.0
            }
        
        Args:
            score: Score to evaluate
            scale: Dict of (min, max) -> value
        
        Returns:
            Scaled value
        """
        for (min_val, max_val), scaled_val in scale.items():
            if min_val <= score < max_val:
                return scaled_val
        
        # If above all ranges, return highest
        return max(v for v in scale.values())
    
    def _check_contains(
        self,
        container: Union[List, str, Dict],
        *items: str,
        case_sensitive: bool = False
    ) -> bool:
        """
        Check if container contains any of the items.
        
        Args:
            container: List, string, or dict to search
            *items: Items to find
            case_sensitive: Whether comparison is case-sensitive
        
        Returns:
            True if any item found
        """
        if container is None:
            return False
        
        if isinstance(container, dict):
            items_to_check = list(container.keys())
        elif isinstance(container, str):
            items_to_check = [container]
        else:
            items_to_check = list(container)
        
        for item in items:
            item_to_check = item if case_sensitive else str(item).lower()
            
            for check in items_to_check:
                check_str = str(check) if case_sensitive else str(check).lower()
                if item_to_check in check_str:
                    return True
        
        return False
    
    def _score_rating(
        self,
        rating: str,
        rating_map: Dict[str, float]
    ) -> float:
        """
        Score a categorical rating (e.g., CQC ratings).
        
        Args:
            rating: Rating string (e.g., 'Outstanding', 'Good')
            rating_map: Dict of rating -> points
        
        Returns:
            Points for this rating
        """
        if rating is None:
            return 0.0
        
        rating_normalized = self._normalize_string(rating, case='lower')
        
        for key, value in rating_map.items():
            key_normalized = self._normalize_string(key, case='lower')
            if rating_normalized == key_normalized:
                return value
        
        return 0.0
    
    def _log_warning(self, message: str, home_id: Optional[str] = None):
        """Log warning for data quality issues"""
        prefix = f"[{self.CATEGORY_NAME}]" if self.CATEGORY_NAME else "[Calculator]"
        if home_id:
            prefix += f" (ID: {home_id})"
        logger.warning(f"{prefix} {message}")
    
    def _log_debug(self, message: str):
        """Log debug message"""
        prefix = f"[{self.CATEGORY_NAME}]" if self.CATEGORY_NAME else "[Calculator]"
        logger.debug(f"{prefix} {message}")


class CalculatorRegistry:
    """Registry for managing calculators"""
    
    _calculators: Dict[str, CategoryCalculator] = {}
    
    @classmethod
    def register(cls, name: str, calculator: CategoryCalculator) -> None:
        """Register a calculator"""
        cls._calculators[name] = calculator
        logger.info(f"Registered calculator: {name}")
    
    @classmethod
    def get(cls, name: str) -> Optional[CategoryCalculator]:
        """Get a registered calculator"""
        return cls._calculators.get(name)
    
    @classmethod
    def get_all(cls) -> Dict[str, CategoryCalculator]:
        """Get all registered calculators"""
        return cls._calculators.copy()
    
    @classmethod
    def list_calculators(cls) -> List[str]:
        """List all registered calculator names"""
        return list(cls._calculators.keys())
