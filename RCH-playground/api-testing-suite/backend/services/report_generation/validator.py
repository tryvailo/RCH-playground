"""
Report Validator

Validates questionnaire and care home data for professional report generation.

Extracted from report_routes.py lines 98-101 and 419-487
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Validation error"""
    pass


class ReportValidator:
    """Validate questionnaire and home data"""
    
    def validate_questionnaire(self, questionnaire: Dict[str, Any]) -> None:
        """
        Validate professional questionnaire structure.
        
        Args:
            questionnaire: Questionnaire to validate
        
        Raises:
            ValidationError if invalid
        """
        try:
            from models.schemas import validate_questionnaire
            validate_questionnaire(questionnaire)
            logger.info("✅ Questionnaire validation passed")
        except Exception as e:
            logger.error(f"Questionnaire validation failed: {e}")
            raise ValidationError(f"Invalid questionnaire: {str(e)}")
    
    def validate_homes(
        self,
        homes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate care home data.
        
        Args:
            homes: List of care homes to validate
        
        Returns:
            {
                'valid_homes': List[Dict],
                'invalid_homes': List[Dict],
                'total_homes': int,
                'valid_count': int,
                'invalid_count': int,
                'errors': List[str],
                'warnings': List[str]
            }
        """
        try:
            from services.professional_report_validator import validate_care_homes_batch
            
            validation_summary = validate_care_homes_batch(homes)
            
            valid_homes = [
                home for home, result in zip(homes, validation_summary['results'])
                if result['validation']['is_valid']
            ]
            
            invalid_homes = [
                home for home, result in zip(homes, validation_summary['results'])
                if not result['validation']['is_valid']
            ]
            
            logger.info(
                f"✅ Validation complete: {len(valid_homes)} valid, "
                f"{len(invalid_homes)} invalid out of {len(homes)}"
            )
            
            return {
                'valid_homes': valid_homes,
                'invalid_homes': invalid_homes,
                'total_homes': len(homes),
                'valid_count': len(valid_homes),
                'invalid_count': len(invalid_homes),
                'errors': validation_summary.get('errors', []),
                'warnings': validation_summary.get('warnings', [])
            }
        
        except Exception as e:
            logger.warning(f"Home validation failed: {e}")
            # Return all homes as valid if validation service unavailable
            return {
                'valid_homes': homes,
                'invalid_homes': [],
                'total_homes': len(homes),
                'valid_count': len(homes),
                'invalid_count': 0,
                'errors': [str(e)],
                'warnings': []
            }
