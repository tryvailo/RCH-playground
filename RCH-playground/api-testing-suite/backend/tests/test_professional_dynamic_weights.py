"""
Tests for Professional Matching Service Dynamic Weights

Tests all 6 weight adjustment rules and their combinations.
Based on TECHNICAL_PROFESSIONAL_Dynamic_Weights_v2.md
"""

import pytest
from services.professional_matching_service import (
    ProfessionalMatchingService,
    ScoringWeights
)


class TestDynamicWeights:
    """Test dynamic weight calculation"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.service = ProfessionalMatchingService()
    
    def test_base_weights(self):
        """Test base weights (no conditions)"""
        questionnaire = {
            'section_3_medical_needs': {
                'q9_medical_conditions': ['no_serious_medical']
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls_occurred'
            },
            'section_2_location_budget': {
                'q7_budget': '5000_7000_self'
            },
            'section_5_timeline': {
                'q17_placement_timeline': 'planning_2_3_months'
            }
        }
        
        weights, conditions = self.service.calculate_dynamic_weights(questionnaire)
        
        # Should use base weights (normalized)
        assert abs(weights.medical - 19.0) < 1.0
        assert abs(weights.safety - 16.0) < 1.0
        assert abs(weights.location - 10.0) < 1.0
        assert abs(weights.social - 10.0) < 1.0
        assert abs(weights.financial - 13.0) < 1.0
        assert abs(weights.staff - 13.0) < 1.0
        assert abs(weights.cqc - 13.0) < 1.0
        assert abs(weights.services - 7.0) < 1.0
        
        # Weights should sum to 100%
        total = sum([
            weights.medical, weights.safety, weights.location, weights.social,
            weights.financial, weights.staff, weights.cqc, weights.services
        ])
        assert abs(total - 100.0) < 0.1
        
        assert len(conditions) == 0
    
    def test_rule_1_high_fall_risk(self):
        """Test Rule 1: High Fall Risk"""
        questionnaire = {
            'section_3_medical_needs': {
                'q9_medical_conditions': ['no_serious_medical']
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'high_risk_of_falling'
            },
            'section_2_location_budget': {
                'q7_budget': '5000_7000_self'
            },
            'section_5_timeline': {
                'q17_placement_timeline': 'planning_2_3_months'
            }
        }
        
        weights, conditions = self.service.calculate_dynamic_weights(questionnaire)
        
        # Safety should be increased to ~25%
        assert weights.safety >= 24.0
        assert weights.safety <= 26.0
        
        # Other categories should be reduced
        assert weights.medical < 19.0
        assert weights.location < 10.0
        assert weights.social < 10.0
        assert weights.services < 7.0
        
        # Weights should sum to 100%
        total = sum([
            weights.medical, weights.safety, weights.location, weights.social,
            weights.financial, weights.staff, weights.cqc, weights.services
        ])
        assert abs(total - 100.0) < 0.1
        
        assert 'high_fall_risk' in conditions
    
    def test_rule_1_3plus_falls(self):
        """Test Rule 1: 3+ falls with serious injuries"""
        questionnaire = {
            'section_4_safety_special_needs': {
                'q13_fall_history': '3_plus_or_serious_injuries'
            }
        }
        
        weights, conditions = self.service.calculate_dynamic_weights(questionnaire)
        
        assert weights.safety >= 24.0
        assert 'high_fall_risk' in conditions
    
    def test_rule_2_dementia(self):
        """Test Rule 2: Dementia/Alzheimer's"""
        questionnaire = {
            'section_3_medical_needs': {
                'q9_medical_conditions': ['dementia_alzheimers']
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls_occurred'  # No fall risk
            }
        }
        
        weights, conditions = self.service.calculate_dynamic_weights(questionnaire)
        
        # Medical should be increased to ~26%
        assert weights.medical >= 25.0
        assert weights.medical <= 27.0
        
        # Safety should be slightly increased
        assert weights.safety >= 17.0
        
        # Services should be decreased
        assert weights.services <= 3.0
        
        # Weights should sum to 100%
        total = sum([
            weights.medical, weights.safety, weights.location, weights.social,
            weights.financial, weights.staff, weights.cqc, weights.services
        ])
        assert abs(total - 100.0) < 0.1
        
        assert 'dementia' in conditions
    
    def test_rule_3_multiple_conditions(self):
        """Test Rule 3: Multiple Complex Medical Conditions (3+)"""
        questionnaire = {
            'section_3_medical_needs': {
                'q9_medical_conditions': ['diabetes', 'heart_conditions', 'mobility_problems']
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls_occurred'  # No fall risk
            }
        }
        
        weights, conditions = self.service.calculate_dynamic_weights(questionnaire)
        
        # Medical should be increased to ~29%
        assert weights.medical >= 28.0
        assert weights.medical <= 30.0
        
        # Location and Social should be decreased
        assert weights.location <= 8.0
        assert weights.social <= 8.0
        
        # Weights should sum to 100%
        total = sum([
            weights.medical, weights.safety, weights.location, weights.social,
            weights.financial, weights.staff, weights.cqc, weights.services
        ])
        assert abs(total - 100.0) < 0.1
        
        assert 'multiple_conditions' in conditions
    
    def test_rule_4_nursing_required(self):
        """Test Rule 4: Nursing Level Required"""
        questionnaire = {
            'section_3_medical_needs': {
                'q8_care_types': ['medical_nursing'],
                'q9_medical_conditions': ['no_serious_medical']
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls_occurred'
            }
        }
        
        weights, conditions = self.service.calculate_dynamic_weights(questionnaire)
        
        # Medical and Staff should be increased
        assert weights.medical >= 21.0
        assert weights.staff >= 15.0
        
        # Weights should sum to 100%
        total = sum([
            weights.medical, weights.safety, weights.location, weights.social,
            weights.financial, weights.staff, weights.cqc, weights.services
        ])
        assert abs(total - 100.0) < 0.1
        
        assert 'nursing_required' in conditions
    
    def test_rule_5_low_budget(self):
        """Test Rule 5: Low Budget Constraint"""
        questionnaire = {
            'section_2_location_budget': {
                'q7_budget': 'under_3000_self'
            },
            'section_3_medical_needs': {
                'q9_medical_conditions': ['no_serious_medical']
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls_occurred'
            }
        }
        
        weights, conditions = self.service.calculate_dynamic_weights(questionnaire)
        
        # Financial should be increased to ~19%
        assert weights.financial >= 18.0
        assert weights.financial <= 20.0
        
        # Services should be decreased
        assert weights.services <= 4.0
        
        # Weights should sum to 100%
        total = sum([
            weights.medical, weights.safety, weights.location, weights.social,
            weights.financial, weights.staff, weights.cqc, weights.services
        ])
        assert abs(total - 100.0) < 0.1
        
        assert 'low_budget' in conditions
    
    def test_rule_6_urgent_placement(self):
        """Test Rule 6: Urgent Placement"""
        questionnaire = {
            'section_5_timeline': {
                'q17_placement_timeline': 'urgent_2_weeks'
            },
            'section_3_medical_needs': {
                'q9_medical_conditions': ['no_serious_medical']
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls_occurred'
            }
        }
        
        weights, conditions = self.service.calculate_dynamic_weights(questionnaire)
        
        # Location should be increased to ~17%
        assert weights.location >= 16.0
        assert weights.location <= 18.0
        
        # Services should be decreased
        assert weights.services <= 3.0
        
        # Weights should sum to 100%
        total = sum([
            weights.medical, weights.safety, weights.location, weights.social,
            weights.financial, weights.staff, weights.cqc, weights.services
        ])
        assert abs(total - 100.0) < 0.1
        
        assert 'urgent_placement' in conditions
    
    def test_priority_fall_risk_overrides_dementia(self):
        """Test Priority: Fall Risk overrides Dementia"""
        questionnaire = {
            'section_3_medical_needs': {
                'q9_medical_conditions': ['dementia_alzheimers']
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'high_risk_of_falling'
            }
        }
        
        weights, conditions = self.service.calculate_dynamic_weights(questionnaire)
        
        # Should apply fall risk weights (safety high), NOT dementia weights
        assert weights.safety >= 24.0
        assert 'high_fall_risk' in conditions
        assert 'dementia' not in conditions  # Should NOT apply dementia adjustment
    
    def test_priority_dementia_overrides_multiple_conditions(self):
        """Test Priority: Dementia overrides Multiple Conditions"""
        questionnaire = {
            'section_3_medical_needs': {
                'q9_medical_conditions': ['dementia_alzheimers', 'diabetes', 'heart_conditions']
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls_occurred'
            }
        }
        
        weights, conditions = self.service.calculate_dynamic_weights(questionnaire)
        
        # Should apply dementia weights, NOT multiple conditions
        assert weights.medical >= 25.0
        assert weights.medical <= 27.0  # Dementia range, not 29% from multiple
        assert 'dementia' in conditions
        assert 'multiple_conditions' not in conditions
    
    def test_combination_nursing_and_low_budget(self):
        """Test Combination: Nursing + Low Budget"""
        questionnaire = {
            'section_2_location_budget': {
                'q7_budget': 'under_3000_local'
            },
            'section_3_medical_needs': {
                'q8_care_types': ['medical_nursing'],
                'q9_medical_conditions': ['no_serious_medical']
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls_occurred'
            }
        }
        
        weights, conditions = self.service.calculate_dynamic_weights(questionnaire)
        
        # Both adjustments should apply (allow for normalization variance)
        assert weights.medical >= 20.0  # From nursing (normalized)
        assert weights.staff >= 15.0  # From nursing
        assert weights.financial >= 18.0  # From low budget
        
        assert 'nursing_required' in conditions
        assert 'low_budget' in conditions
        
        # Weights should sum to 100%
        total = sum([
            weights.medical, weights.safety, weights.location, weights.social,
            weights.financial, weights.staff, weights.cqc, weights.services
        ])
        assert abs(total - 100.0) < 0.1
    
    def test_combination_urgent_and_low_budget(self):
        """Test Combination: Urgent + Low Budget"""
        questionnaire = {
            'section_2_location_budget': {
                'q7_budget': 'under_3000_self'
            },
            'section_5_timeline': {
                'q17_placement_timeline': 'urgent_2_weeks'
            },
            'section_3_medical_needs': {
                'q9_medical_conditions': ['no_serious_medical']
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls_occurred'
            }
        }
        
        weights, conditions = self.service.calculate_dynamic_weights(questionnaire)
        
        # Both adjustments should apply
        assert weights.location >= 16.0  # From urgent
        assert weights.financial >= 18.0  # From low budget
        
        assert 'urgent_placement' in conditions
        assert 'low_budget' in conditions
        
        # Weights should sum to 100%
        total = sum([
            weights.medical, weights.safety, weights.location, weights.social,
            weights.financial, weights.staff, weights.cqc, weights.services
        ])
        assert abs(total - 100.0) < 0.1
    
    def test_complex_combination_all_rules(self):
        """Test Complex Combination: All applicable rules (except conflicting)"""
        questionnaire = {
            'section_2_location_budget': {
                'q7_budget': 'under_3000_local'
            },
            'section_3_medical_needs': {
                'q8_care_types': ['medical_nursing'],
                'q9_medical_conditions': ['diabetes', 'mobility_problems']  # 2 conditions, not 3+
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls_occurred'  # No fall risk
            },
            'section_5_timeline': {
                'q17_placement_timeline': 'urgent_2_weeks'
            }
        }
        
        weights, conditions = self.service.calculate_dynamic_weights(questionnaire)
        
        # Should apply: Nursing, Low Budget, Urgent
        assert 'nursing_required' in conditions
        assert 'low_budget' in conditions
        assert 'urgent_placement' in conditions
        
        # Should NOT apply: Fall Risk, Dementia, Multiple Conditions
        assert 'high_fall_risk' not in conditions
        assert 'dementia' not in conditions
        assert 'multiple_conditions' not in conditions
        
        # Weights should sum to 100%
        total = sum([
            weights.medical, weights.safety, weights.location, weights.social,
            weights.financial, weights.staff, weights.cqc, weights.services
        ])
        assert abs(total - 100.0) < 0.1
    
    def test_edge_case_no_serious_medical_excluded(self):
        """Test Edge Case: 'no_serious_medical' excluded from condition count"""
        questionnaire = {
            'section_3_medical_needs': {
                'q9_medical_conditions': ['no_serious_medical', 'diabetes', 'heart_conditions']
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls_occurred'
            }
        }
        
        weights, conditions = self.service.calculate_dynamic_weights(questionnaire)
        
        # Should count only 2 actual conditions (diabetes, heart), not 3
        # So should NOT trigger multiple_conditions rule
        assert 'multiple_conditions' not in conditions
    
    def test_edge_case_1_2_falls_minor_adjustment(self):
        """Test Edge Case: 1-2 falls (not high risk)"""
        questionnaire = {
            'section_4_safety_special_needs': {
                'q13_fall_history': '1_2_no_serious_injuries'
            }
        }
        
        weights, conditions = self.service.calculate_dynamic_weights(questionnaire)
        
        # Should NOT trigger high fall risk rule
        assert 'high_fall_risk' not in conditions
        # Should use base weights or minor adjustments only


class TestScoringWeights:
    """Test ScoringWeights dataclass"""
    
    def test_normalize(self):
        """Test weight normalization"""
        weights = ScoringWeights(
            medical=38,
            safety=32,
            location=20,
            social=20,
            financial=26,
            staff=26,
            cqc=26,
            services=14
        )
        
        normalized = weights.normalize()
        
        # Should sum to 100%
        total = sum([
            normalized.medical, normalized.safety, normalized.location, normalized.social,
            normalized.financial, normalized.staff, normalized.cqc, normalized.services
        ])
        assert abs(total - 100.0) < 0.1
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        weights = ScoringWeights()
        weights_dict = weights.to_dict()
        
        assert isinstance(weights_dict, dict)
        assert 'medical' in weights_dict
        assert 'safety' in weights_dict
        assert len(weights_dict) == 8

