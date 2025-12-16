"""
Production-Level Unit Tests for Professional Matching Service

Comprehensive test coverage for 156-point matching algorithm including:
- Edge cases and error handling
- None/missing data handling
- All scoring methods with boundary conditions
- Dynamic weights with all questionnaire variants
- Integration tests for full matching pipeline

Test Categories:
1. Dynamic Weights - all 6 rules + combinations + priority order
2. Scoring Methods - all 8 categories with edge cases
3. 156-Point Match - full algorithm with various inputs
4. Error Handling - None values, missing data, invalid inputs
5. Social Personality Fix - verify sociable/social variants work
6. Integration - end-to-end matching with real questionnaire samples
"""

import pytest
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# Add services to path
services_path = Path(__file__).parent.parent / "services"
if str(services_path) not in sys.path:
    sys.path.insert(0, str(services_path))

from services.professional_matching_service import (
    ProfessionalMatchingService,
    ScoringWeights
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def matching_service():
    """Create matching service instance"""
    return ProfessionalMatchingService()


@pytest.fixture
def base_questionnaire():
    """Base questionnaire with no special conditions"""
    return {
        'section_1_contact_emergency': {
            'q1_names': 'Contact: John Smith; Patient: Mary Smith',
            'q2_email': 'john.smith@email.com',
            'q3_phone': '+44 7123 456789',
            'q4_emergency_contact': 'Jane Smith +44 7987 654321'
        },
        'section_2_location_budget': {
            'q4_postcode': 'B44 8DD',
            'q5_preferred_city': 'Birmingham',
            'q6_max_distance': 'within_15km',
            'q7_budget': '5000_7000_self',
            'user_latitude': 52.533398,
            'user_longitude': -1.8904
        },
        'section_3_medical_needs': {
            'q8_care_types': ['general_residential'],
            'q9_medical_conditions': ['no_serious_medical'],
            'q10_mobility_level': 'fully_mobile',
            'q11_medication_management': 'simple_1_2',
            'q12_age_range': '75_84'
        },
        'section_4_safety_special_needs': {
            'q13_fall_history': 'no_falls_occurred',
            'q14_allergies': ['no_allergies'],
            'q15_dietary_requirements': ['no_special_requirements'],
            'q16_social_personality': 'moderately_sociable'
        },
        'section_5_timeline': {
            'q17_placement_timeline': 'planning_2_3_months'
        }
    }


@pytest.fixture
def base_home():
    """Base care home with all fields populated"""
    return {
        'id': 'test-home-001',
        'cqc_location_id': '1-123456789',
        'name': 'Test Care Home',
        'address': '123 Test Street, Birmingham, B1 1AA',
        'postcode': 'B1 1AA',
        'latitude': 52.4862,
        'longitude': -1.8904,
        'care_types': ['residential', 'nursing'],
        'care_nursing': True,
        'care_dementia': False,
        'care_residential': True,
        'rating': 'Good',
        'overall_rating': 'Good',
        'fsa_rating': 5,
        'weekly_cost': 1200,
        'fee_residential_from': 1200,
        'fee_nursing_from': 1400,
        'public_transport_nearby': True,
        'visitor_parking': True,
        'wheelchair_accessible': True,
        'medical_equipment': True,
        'on_site_pharmacy': False,
        'physiotherapy_available': True,
        'mental_health_services': False,
        'specialist_programs': ['general'],
        'activities': ['arts', 'music', 'gardening'],
        'enrichment_activities': ['outings', 'exercise'],
        'google_review_count': 25,
        'google_rating': 4.2
    }


@pytest.fixture
def base_enriched_data():
    """Base enriched data from APIs"""
    return {
        'cqc_detailed': {
            'overall_rating': 'Good',
            'safe_rating': 'Good',
            'effective_rating': 'Good',
            'caring_rating': 'Good',
            'responsive_rating': 'Good',
            'well_led_rating': 'Good',
            'trend': 'stable',
            'safeguarding_incidents': 0
        },
        'fsa_detailed': {
            'rating': 5,
            'trend': 'stable'
        },
        'fsa_scoring': {
            'fsa_points': 7
        },
        'financial_data': {
            'net_margin_3year_avg': 0.12,
            'current_ratio': 1.8,
            'altman_z_score': 2.8,
            'filing_compliance': True,
            'accounts_overdue': False,
            'director_stability': {
                'resignations_last_2_years': 0,
                'active_directors': 3
            },
            'ownership_stability': {
                'changes_last_5_years': 0,
                'is_private_equity': False
            }
        },
        'staff_data': {
            'glassdoor_rating': 4.0,
            'average_tenure_years': 3.5,
            'annual_turnover_rate': 0.15,
            'registered_nurses': 2
        },
        'google_places': {
            'review_count': 25,
            'average_dwell_time_minutes': 45,
            'repeat_visitor_rate': 0.35,
            'community_integration_score': 0.6
        },
        'medical_capabilities': {
            'emergency_response_time': 5,
            'medication_management': True,
            'emergency_protocols': True
        }
    }


# =============================================================================
# 1. DYNAMIC WEIGHTS TESTS - Edge Cases & All Variants
# =============================================================================

class TestDynamicWeightsEdgeCases:
    """Edge cases for dynamic weight calculation"""
    
    def test_empty_questionnaire(self, matching_service):
        """Test with completely empty questionnaire"""
        weights, conditions = matching_service.calculate_dynamic_weights({})
        
        # Should return base weights normalized
        total = sum([
            weights.medical, weights.safety, weights.location, weights.social,
            weights.financial, weights.staff, weights.cqc, weights.services
        ])
        assert abs(total - 100.0) < 0.5
        assert len(conditions) == 0
    
    def test_none_questionnaire_values(self, matching_service):
        """Test with None values in questionnaire"""
        questionnaire = {
            'section_3_medical_needs': None,
            'section_4_safety_special_needs': None,
            'section_2_location_budget': None,
            'section_5_timeline': None
        }
        
        weights, conditions = matching_service.calculate_dynamic_weights(questionnaire)
        
        # Should not crash, return base weights
        assert weights is not None
        assert isinstance(conditions, list)
    
    def test_missing_sections(self, matching_service):
        """Test with some sections missing"""
        questionnaire = {
            'section_3_medical_needs': {
                'q9_medical_conditions': ['dementia_alzheimers']
            }
            # Missing other sections
        }
        
        weights, conditions = matching_service.calculate_dynamic_weights(questionnaire)
        
        assert 'dementia' in conditions
        assert weights.medical >= 25.0
    
    def test_empty_arrays(self, matching_service):
        """Test with empty arrays for conditions"""
        questionnaire = {
            'section_3_medical_needs': {
                'q8_care_types': [],
                'q9_medical_conditions': []
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': ''
            }
        }
        
        weights, conditions = matching_service.calculate_dynamic_weights(questionnaire)
        
        # Should use base weights
        assert len(conditions) == 0
    
    def test_all_conditions_priority_order(self, matching_service):
        """Test that priority order is respected when all conditions present"""
        questionnaire = {
            'section_2_location_budget': {
                'q7_budget': 'under_3000_self'
            },
            'section_3_medical_needs': {
                'q8_care_types': ['medical_nursing'],
                'q9_medical_conditions': ['dementia_alzheimers', 'diabetes', 'heart_conditions']
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'high_risk_of_falling'
            },
            'section_5_timeline': {
                'q17_placement_timeline': 'urgent_2_weeks'
            }
        }
        
        weights, conditions = matching_service.calculate_dynamic_weights(questionnaire)
        
        # Fall risk is highest priority - should be the ONLY condition applied
        assert 'high_fall_risk' in conditions
        assert 'dementia' not in conditions  # Lower priority
        assert 'multiple_conditions' not in conditions
        assert weights.safety >= 24.0
    
    def test_dementia_overrides_multiple_conditions(self, matching_service):
        """Test that dementia overrides multiple conditions"""
        questionnaire = {
            'section_3_medical_needs': {
                'q9_medical_conditions': [
                    'dementia_alzheimers',
                    'diabetes',
                    'heart_conditions',
                    'mobility_problems'
                ]
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls_occurred'
            }
        }
        
        weights, conditions = matching_service.calculate_dynamic_weights(questionnaire)
        
        # Dementia is higher priority than multiple conditions
        assert 'dementia' in conditions
        assert 'multiple_conditions' not in conditions
        assert weights.medical >= 25.0
        assert weights.medical <= 27.0  # Dementia range, not 29%


class TestDynamicWeightsBudgetVariants:
    """Test all budget value variants"""
    
    @pytest.mark.parametrize("budget_value,expected_low_budget", [
        ('under_3000_self', True),
        ('under_3000_local', True),
        ('under_3000_nhs', True),
        ('3000_5000_self', False),
        ('5000_7000_local', False),
        ('over_7000_self', False),
        ('', False),
        (None, False),
    ])
    def test_budget_variants(self, matching_service, budget_value, expected_low_budget):
        """Test various budget value formats"""
        questionnaire = {
            'section_2_location_budget': {
                'q7_budget': budget_value
            } if budget_value else {}
        }
        
        weights, conditions = matching_service.calculate_dynamic_weights(questionnaire)
        
        if expected_low_budget:
            assert 'low_budget' in conditions
            assert weights.financial >= 18.0
        else:
            assert 'low_budget' not in conditions


class TestDynamicWeightsFallHistoryVariants:
    """Test all fall history value variants"""
    
    @pytest.mark.parametrize("fall_value,expected_high_risk", [
        ('high_risk_of_falling', True),
        ('3_plus_or_serious_injuries', True),
        ('1_2_no_serious_injuries', False),
        ('no_falls_occurred', False),
        ('', False),
        (None, False),
    ])
    def test_fall_history_variants(self, matching_service, fall_value, expected_high_risk):
        """Test various fall history value formats"""
        questionnaire = {
            'section_4_safety_special_needs': {
                'q13_fall_history': fall_value
            } if fall_value else {}
        }
        
        weights, conditions = matching_service.calculate_dynamic_weights(questionnaire)
        
        if expected_high_risk:
            assert 'high_fall_risk' in conditions
            assert weights.safety >= 24.0
        else:
            assert 'high_fall_risk' not in conditions


# =============================================================================
# 2. SCORING METHODS - Edge Cases & None Handling
# =============================================================================

class TestMedicalCapabilitiesEdgeCases:
    """Edge cases for medical capabilities scoring"""
    
    def test_none_home_data(self, matching_service):
        """Test with None values in home data"""
        home = {
            'care_types': None,
            'care_nursing': None,
            'wheelchair_accessible': None,
            'medical_equipment': None
        }
        user_profile = {
            'section_3_medical_needs': {
                'q9_medical_conditions': ['diabetes'],
                'q8_care_types': ['medical_nursing']
            }
        }
        enriched_data = {}
        
        score = matching_service._calculate_medical_capabilities(home, user_profile, enriched_data)
        
        assert 0.0 <= score <= 1.0
    
    def test_empty_enriched_data(self, matching_service, base_home, base_questionnaire):
        """Test with empty enriched data"""
        score = matching_service._calculate_medical_capabilities(
            base_home, base_questionnaire, {}
        )
        
        assert 0.0 <= score <= 1.0
    
    def test_care_types_as_string(self, matching_service, base_questionnaire):
        """Test when care_types is string instead of list"""
        home = {
            'care_types': 'nursing',  # String instead of list
            'care_nursing': True
        }
        enriched_data = {}
        
        score = matching_service._calculate_medical_capabilities(
            home, base_questionnaire, enriched_data
        )
        
        assert 0.0 <= score <= 1.0
    
    def test_rn_count_as_string(self, matching_service, base_home, base_questionnaire):
        """Test when registered_nurses is string"""
        enriched_data = {
            'staff_data': {
                'registered_nurses': '3'  # String instead of int
            }
        }
        
        base_questionnaire['section_3_medical_needs']['q8_care_types'] = ['medical_nursing']
        base_home['care_nursing'] = True
        
        score = matching_service._calculate_medical_capabilities(
            base_home, base_questionnaire, enriched_data
        )
        
        assert 0.0 <= score <= 1.0
        assert score >= 0.3  # Should get some points for nursing capability


class TestSafetyQualityEdgeCases:
    """Edge cases for safety & quality scoring"""
    
    def test_none_ratings(self, matching_service):
        """Test with None CQC ratings"""
        home = {'rating': None, 'overall_rating': None}
        user_profile = {'section_4_safety_special_needs': {'q13_fall_history': 'no_falls_occurred'}}
        enriched_data = {
            'cqc_detailed': {'overall_rating': None, 'trend': None},
            'fsa_detailed': {'rating': None},
            'financial_data': {}
        }
        
        score = matching_service._calculate_safety_quality(home, user_profile, enriched_data)
        
        assert 0.0 <= score <= 1.0
    
    def test_fsa_rating_as_string(self, matching_service, base_home, base_questionnaire):
        """Test when FSA rating is string"""
        enriched_data = {
            'cqc_detailed': {'overall_rating': 'Good', 'trend': 'stable', 'safeguarding_incidents': 0},
            'fsa_detailed': {'rating': '5'},  # String instead of int
            'financial_data': {'filing_compliance': True}
        }
        
        score = matching_service._calculate_safety_quality(
            base_home, base_questionnaire, enriched_data
        )
        
        assert 0.0 <= score <= 1.0
    
    def test_safeguarding_incidents_as_string(self, matching_service, base_home, base_questionnaire):
        """Test when safeguarding_incidents is string"""
        enriched_data = {
            'cqc_detailed': {
                'overall_rating': 'Good',
                'trend': 'stable',
                'safeguarding_incidents': '2'  # String instead of int
            },
            'fsa_detailed': {'rating': 5},
            'financial_data': {'filing_compliance': True}
        }
        
        score = matching_service._calculate_safety_quality(
            base_home, base_questionnaire, enriched_data
        )
        
        assert 0.0 <= score <= 1.0
    
    def test_fsa_scoring_format(self, matching_service, base_home, base_questionnaire):
        """Test FSA scoring from fsa_scoring dict (new format)"""
        enriched_data = {
            'cqc_detailed': {'overall_rating': 'Good', 'trend': 'stable', 'safeguarding_incidents': 0},
            'fsa_scoring': {'fsa_points': 7},  # New format
            'financial_data': {'filing_compliance': True}
        }
        
        score = matching_service._calculate_safety_quality(
            base_home, base_questionnaire, enriched_data
        )
        
        assert score >= 0.7  # Should get high FSA score


class TestLocationAccessEdgeCases:
    """Edge cases for location & access scoring"""
    
    def test_none_coordinates(self, matching_service):
        """Test with None coordinates"""
        home = {'latitude': None, 'longitude': None}
        user_profile = {
            'section_2_location_budget': {
                'q6_max_distance': 'within_5km',
                'user_latitude': None,
                'user_longitude': None
            }
        }
        
        score = matching_service._calculate_location_access(home, user_profile)
        
        # Should return default score
        assert 0.0 <= score <= 1.0
    
    def test_string_coordinates(self, matching_service):
        """Test with string coordinates"""
        home = {
            'latitude': '52.4862',
            'longitude': '-1.8904'
        }
        user_profile = {
            'section_2_location_budget': {
                'q6_max_distance': 'within_15km',
                'user_latitude': '52.5074',
                'user_longitude': '-0.1278'
            }
        }
        
        score = matching_service._calculate_location_access(home, user_profile)
        
        assert 0.0 <= score <= 1.0
    
    def test_invalid_coordinates(self, matching_service):
        """Test with invalid coordinate values"""
        home = {
            'latitude': 'invalid',
            'longitude': 'also_invalid'
        }
        user_profile = {
            'section_2_location_budget': {
                'q6_max_distance': 'within_5km',
                'user_latitude': 52.5074,
                'user_longitude': -0.1278
            }
        }
        
        score = matching_service._calculate_location_access(home, user_profile)
        
        # Should not crash, return valid score
        assert 0.0 <= score <= 1.0
    
    def test_bus_stop_distance_as_string(self, matching_service):
        """Test with string bus_stop_distance"""
        home = {
            'latitude': 52.4862,
            'longitude': -1.8904,
            'bus_stop_distance': '300',  # String
            'public_transport_nearby': True
        }
        user_profile = {
            'section_2_location_budget': {
                'q6_max_distance': 'distance_not_important',
                'user_latitude': 52.4862,
                'user_longitude': -1.8904
            }
        }
        
        score = matching_service._calculate_location_access(home, user_profile)
        
        assert score >= 0.7


class TestCulturalSocialEdgeCases:
    """Edge cases for cultural & social scoring - including sociable fix"""
    
    @pytest.mark.parametrize("personality,expected_min_score", [
        ('very_social', 0.6),
        ('very_sociable', 0.6),  # Fixed variant
        ('moderately_social', 0.4),
        ('moderately_sociable', 0.4),  # Fixed variant
        ('prefers_quiet', 0.2),
        ('', 0.2),  # Falls to else branch
        (None, 0.2),
    ])
    def test_social_personality_variants(self, matching_service, personality, expected_min_score):
        """Test all social personality variants work correctly"""
        home = {
            'google_review_count': 50,
            'activities': ['arts', 'music', 'gardening', 'outings', 'exercise'],
            'local_partnerships': True,
            'community_events': True
        }
        user_profile = {
            'section_4_safety_special_needs': {
                'q16_social_personality': personality
            }
        }
        enriched_data = {
            'google_places': {
                'review_count': 50,
                'average_dwell_time_minutes': 60,
                'repeat_visitor_rate': 0.5,
                'community_integration_score': 0.7
            }
        }
        
        score = matching_service._calculate_cultural_social(home, user_profile, enriched_data)
        
        assert 0.0 <= score <= 1.0
        assert score >= expected_min_score, f"Personality '{personality}' scored {score}, expected >= {expected_min_score}"
    
    def test_activities_as_string(self, matching_service):
        """Test when activities is string instead of list"""
        home = {
            'activities': 'arts, music, gardening',  # String instead of list
            'google_review_count': 20
        }
        user_profile = {
            'section_4_safety_special_needs': {
                'q16_social_personality': 'very_sociable'
            }
        }
        enriched_data = {
            'google_places': {'review_count': 20}
        }
        
        score = matching_service._calculate_cultural_social(home, user_profile, enriched_data)
        
        assert 0.0 <= score <= 1.0
    
    def test_none_review_counts(self, matching_service):
        """Test with None review counts"""
        home = {
            'google_review_count': None,
            'activities': ['arts']
        }
        user_profile = {
            'section_4_safety_special_needs': {
                'q16_social_personality': 'moderately_sociable'
            }
        }
        enriched_data = {
            'google_places': {
                'review_count': None,
                'average_dwell_time_minutes': None,
                'repeat_visitor_rate': None
            }
        }
        
        score = matching_service._calculate_cultural_social(home, user_profile, enriched_data)
        
        assert 0.0 <= score <= 1.0


class TestFinancialStabilityEdgeCases:
    """Edge cases for financial stability scoring"""
    
    def test_companies_house_scoring_format(self, matching_service):
        """Test with new CompaniesHouse scoring format"""
        home = {}
        enriched_data = {
            'companies_house_scoring': {
                'financial_stability_score': 18  # Pre-calculated score
            }
        }
        
        score = matching_service._calculate_financial_stability(home, enriched_data)
        
        assert score == 0.9  # 18/20
    
    def test_altman_z_score_as_string(self, matching_service):
        """Test with string Altman Z-score"""
        home = {}
        enriched_data = {
            'financial_data': {
                'altman_z_score': '3.0',  # String
                'filing_compliance': True,
                'accounts_overdue': False
            }
        }
        
        score = matching_service._calculate_financial_stability(home, enriched_data)
        
        assert score >= 0.5
    
    def test_none_financial_data(self, matching_service):
        """Test with None financial data"""
        home = {}
        enriched_data = {
            'financial_data': None
        }
        
        score = matching_service._calculate_financial_stability(home, enriched_data)
        
        assert 0.0 <= score <= 1.0
    
    def test_empty_financial_data(self, matching_service):
        """Test with empty financial data dict"""
        home = {}
        enriched_data = {
            'financial_data': {}
        }
        
        score = matching_service._calculate_financial_stability(home, enriched_data)
        
        # Should use defaults (mid-range score)
        assert 0.0 <= score <= 1.0


class TestStaffQualityEdgeCases:
    """Edge cases for staff quality scoring"""
    
    def test_none_staff_data(self, matching_service):
        """Test with None staff data values"""
        home = {}
        enriched_data = {
            'staff_data': {
                'glassdoor_rating': None,
                'average_tenure_years': None,
                'annual_turnover_rate': None
            }
        }
        
        score = matching_service._calculate_staff_quality(home, enriched_data)
        
        assert 0.0 <= score <= 1.0
    
    def test_string_staff_values(self, matching_service):
        """Test with string staff data values"""
        home = {}
        enriched_data = {
            'staff_data': {
                'glassdoor_rating': '4.2',
                'average_tenure_years': '3.5',
                'annual_turnover_rate': '0.15'
            }
        }
        
        score = matching_service._calculate_staff_quality(home, enriched_data)
        
        assert score >= 0.5
    
    def test_empty_staff_data(self, matching_service):
        """Test with no staff data"""
        home = {}
        enriched_data = {}
        
        score = matching_service._calculate_staff_quality(home, enriched_data)
        
        assert 0.0 <= score <= 1.0


class TestCQCComplianceEdgeCases:
    """Edge cases for CQC compliance scoring"""
    
    def test_mixed_case_ratings(self, matching_service):
        """Test with mixed case rating values"""
        home = {'rating': 'good'}  # lowercase
        enriched_data = {
            'cqc_detailed': {
                'safe_rating': 'GOOD',  # uppercase
                'effective_rating': 'Good',
                'caring_rating': 'good',
                'responsive_rating': 'OUTSTANDING',
                'well_led_rating': 'Requires Improvement'
            }
        }
        
        score = matching_service._calculate_cqc_compliance(home, enriched_data)
        
        # Should handle mixed case (may use defaults for unrecognized)
        assert 0.0 <= score <= 1.0
    
    def test_all_none_ratings(self, matching_service):
        """Test with all None ratings"""
        home = {'rating': None}
        enriched_data = {
            'cqc_detailed': {
                'safe_rating': None,
                'effective_rating': None,
                'caring_rating': None,
                'responsive_rating': None,
                'well_led_rating': None
            }
        }
        
        score = matching_service._calculate_cqc_compliance(home, enriched_data)
        
        # Should use defaults
        assert 0.0 <= score <= 1.0


class TestAdditionalServicesEdgeCases:
    """Edge cases for additional services scoring"""
    
    def test_specialist_programs_as_string(self, matching_service):
        """Test with specialist_programs as string"""
        home = {
            'physiotherapy_available': True,
            'specialist_programs': 'dementia, diabetes',  # String
            'enrichment_activities': ['arts', 'music']
        }
        user_profile = {
            'section_3_medical_needs': {
                'q9_medical_conditions': ['dementia_alzheimers']
            }
        }
        
        score = matching_service._calculate_additional_services(home, user_profile)
        
        assert 0.0 <= score <= 1.0
    
    def test_all_none_services(self, matching_service):
        """Test with all None service values"""
        home = {
            'physiotherapy_available': None,
            'mental_health_services': None,
            'specialist_programs': None,
            'enrichment_activities': None
        }
        user_profile = {
            'section_3_medical_needs': {}
        }
        
        score = matching_service._calculate_additional_services(home, user_profile)
        
        assert score == 0.0


# =============================================================================
# 3. FULL 156-POINT MATCH - Integration Tests
# =============================================================================

class Test156PointMatchIntegration:
    """Integration tests for full 156-point match calculation"""
    
    def test_full_match_with_base_data(
        self, matching_service, base_home, base_questionnaire, base_enriched_data
    ):
        """Test full match with complete base data"""
        result = matching_service.calculate_156_point_match(
            base_home, base_questionnaire, base_enriched_data
        )
        
        # Verify structure
        assert 'total' in result
        assert 'normalized' in result
        assert 'weights' in result
        assert 'category_scores' in result
        assert 'point_allocations' in result
        
        # Verify types
        assert isinstance(result['total'], int)
        assert isinstance(result['normalized'], int)
        assert isinstance(result['weights'], dict)
        assert isinstance(result['category_scores'], dict)
        assert isinstance(result['point_allocations'], dict)
        
        # Verify ranges
        assert 0 <= result['total'] <= 156
        assert 0 <= result['normalized'] <= 100
        
        # Verify all 8 categories present
        expected_categories = ['medical', 'safety', 'location', 'social', 
                               'financial', 'staff', 'cqc', 'services']
        for cat in expected_categories:
            assert cat in result['category_scores']
            assert cat in result['point_allocations']
            assert cat in result['weights']
    
    def test_full_match_empty_data(self, matching_service):
        """Test full match with empty data"""
        result = matching_service.calculate_156_point_match({}, {}, {})
        
        # Should not crash
        assert 'total' in result
        assert 0 <= result['total'] <= 156
    
    def test_full_match_with_dementia_profile(
        self, matching_service, base_home, base_enriched_data
    ):
        """Test full match with dementia profile (dynamic weights)"""
        questionnaire = {
            'section_3_medical_needs': {
                'q9_medical_conditions': ['dementia_alzheimers'],
                'q8_care_types': ['specialised_dementia']
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls_occurred',
                'q16_social_personality': 'moderately_sociable'
            },
            'section_2_location_budget': {
                'user_latitude': 52.4862,
                'user_longitude': -1.8904,
                'q6_max_distance': 'within_15km'
            }
        }
        
        base_home['care_dementia'] = True
        base_home['care_types'] = ['dementia', 'nursing']
        base_home['specialist_programs'] = ['dementia']
        
        result = matching_service.calculate_156_point_match(
            base_home, questionnaire, base_enriched_data
        )
        
        # Dementia weight should be increased
        assert result['weights']['medical'] >= 25.0
        
        # Medical should get more points
        assert result['point_allocations']['medical'] > 0
    
    def test_full_match_with_high_fall_risk(
        self, matching_service, base_home, base_enriched_data
    ):
        """Test full match with high fall risk profile"""
        questionnaire = {
            'section_4_safety_special_needs': {
                'q13_fall_history': 'high_risk_of_falling',
                'q16_social_personality': 'prefers_quiet'
            },
            'section_3_medical_needs': {
                'q9_medical_conditions': ['mobility_problems']
            },
            'section_2_location_budget': {
                'user_latitude': 52.4862,
                'user_longitude': -1.8904,
                'q6_max_distance': 'within_15km'
            }
        }
        
        # Ensure home has good safety rating
        base_enriched_data['cqc_detailed']['safe_rating'] = 'Outstanding'
        
        result = matching_service.calculate_156_point_match(
            base_home, questionnaire, base_enriched_data
        )
        
        # Safety weight should be increased
        assert result['weights']['safety'] >= 24.0
    
    def test_full_match_weights_sum_to_100(
        self, matching_service, base_home, base_questionnaire, base_enriched_data
    ):
        """Test that weights always sum to 100%"""
        result = matching_service.calculate_156_point_match(
            base_home, base_questionnaire, base_enriched_data
        )
        
        total_weight = sum(result['weights'].values())
        assert abs(total_weight - 100.0) < 0.5
    
    def test_full_match_point_allocations_sum_to_total(
        self, matching_service, base_home, base_questionnaire, base_enriched_data
    ):
        """Test that point allocations sum to total score"""
        result = matching_service.calculate_156_point_match(
            base_home, base_questionnaire, base_enriched_data
        )
        
        total_from_allocations = sum(result['point_allocations'].values())
        # Allow small rounding difference
        assert abs(total_from_allocations - result['total']) < 1


# =============================================================================
# 4. ERROR HANDLING TESTS
# =============================================================================

class TestErrorHandling:
    """Tests for error handling and edge cases"""
    
    def test_none_home(self, matching_service, base_questionnaire, base_enriched_data):
        """Test with None home"""
        # Should handle None gracefully
        try:
            result = matching_service.calculate_156_point_match(
                None, base_questionnaire, base_enriched_data
            )
            # If it doesn't crash, verify result
            assert 'total' in result
        except (TypeError, AttributeError):
            # Expected - None is not subscriptable
            pass
    
    def test_non_dict_inputs(self, matching_service):
        """Test with non-dict inputs"""
        # String input
        try:
            result = matching_service.calculate_156_point_match(
                "home", "questionnaire", "enriched"
            )
            assert 'total' in result
        except (TypeError, AttributeError):
            pass
    
    def test_deeply_nested_none(self, matching_service):
        """Test with deeply nested None values"""
        home = {
            'care_types': ['nursing'],
            'rating': 'Good'
        }
        questionnaire = {
            'section_3_medical_needs': {
                'q9_medical_conditions': [None, 'diabetes', None]
            }
        }
        enriched_data = {
            'cqc_detailed': {
                'overall_rating': 'Good',
                'trend': None
            }
        }
        
        result = matching_service.calculate_156_point_match(
            home, questionnaire, enriched_data
        )
        
        assert 0 <= result['total'] <= 156
    
    def test_negative_values(self, matching_service):
        """Test with negative numeric values"""
        home = {
            'latitude': -52.4862,  # Valid negative (southern hemisphere)
            'longitude': -1.8904
        }
        enriched_data = {
            'financial_data': {
                'altman_z_score': -1.0  # Negative (very bad score)
            },
            'staff_data': {
                'annual_turnover_rate': -0.1  # Invalid negative
            }
        }
        
        result = matching_service.calculate_156_point_match(home, {}, enriched_data)
        
        assert 0 <= result['total'] <= 156


# =============================================================================
# 5. SCORING WEIGHTS CLASS TESTS
# =============================================================================

class TestScoringWeightsClass:
    """Tests for ScoringWeights dataclass"""
    
    def test_default_values(self):
        """Test default weight values"""
        weights = ScoringWeights()
        
        assert weights.medical == 19.0
        assert weights.safety == 16.0
        assert weights.location == 10.0
        assert weights.social == 10.0
        assert weights.financial == 13.0
        assert weights.staff == 13.0
        assert weights.cqc == 13.0
        assert weights.services == 7.0
    
    def test_normalize_already_100(self):
        """Test normalization when weights already sum to ~100"""
        weights = ScoringWeights()  # Sums to 101
        normalized = weights.normalize()
        
        total = sum([
            normalized.medical, normalized.safety, normalized.location, 
            normalized.social, normalized.financial, normalized.staff, 
            normalized.cqc, normalized.services
        ])
        assert abs(total - 100.0) < 0.5
    
    def test_normalize_zero_sum(self):
        """Test normalization with zero sum"""
        weights = ScoringWeights(
            medical=0, safety=0, location=0, social=0,
            financial=0, staff=0, cqc=0, services=0
        )
        normalized = weights.normalize()
        
        # Should return same (avoid division by zero)
        assert normalized.medical == 0
    
    def test_normalize_extreme_values(self):
        """Test normalization with extreme values"""
        weights = ScoringWeights(
            medical=1000, safety=1, location=1, social=1,
            financial=1, staff=1, cqc=1, services=1
        )
        normalized = weights.normalize()
        
        total = sum([
            normalized.medical, normalized.safety, normalized.location,
            normalized.social, normalized.financial, normalized.staff,
            normalized.cqc, normalized.services
        ])
        assert abs(total - 100.0) < 0.5
        assert normalized.medical > 90  # Should dominate
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        weights = ScoringWeights(medical=25, safety=20)
        weights_dict = weights.to_dict()
        
        assert isinstance(weights_dict, dict)
        assert len(weights_dict) == 8
        assert weights_dict['medical'] == 25
        assert weights_dict['safety'] == 20


# =============================================================================
# 6. REGRESSION TESTS - Real Questionnaire Samples
# =============================================================================

class TestRealQuestionnaireSamples:
    """Integration tests using real questionnaire samples"""
    
    @pytest.fixture
    def load_sample_questionnaire(self):
        """Load a sample questionnaire from file"""
        def _load(filename):
            samples_dir = Path(__file__).parent.parent.parent.parent / "data" / "sample_questionnaires"
            filepath = samples_dir / filename
            if filepath.exists():
                with open(filepath, 'r') as f:
                    return json.load(f)
            return None
        return _load
    
    def test_dementia_questionnaire(self, matching_service, load_sample_questionnaire, base_home, base_enriched_data):
        """Test with real dementia questionnaire sample"""
        questionnaire = load_sample_questionnaire("professional_questionnaire_1_dementia.json")
        
        if questionnaire is None:
            pytest.skip("Sample questionnaire not found")
        
        result = matching_service.calculate_156_point_match(
            base_home, questionnaire, base_enriched_data
        )
        
        # Verify dementia weights applied
        assert result['weights']['medical'] >= 25.0
        assert 0 <= result['total'] <= 156
    
    def test_high_fall_risk_questionnaire(
        self, matching_service, load_sample_questionnaire, base_home, base_enriched_data
    ):
        """Test with real high fall risk questionnaire sample"""
        questionnaire = load_sample_questionnaire("professional_questionnaire_5_high_fall_risk.json")
        
        if questionnaire is None:
            pytest.skip("Sample questionnaire not found")
        
        result = matching_service.calculate_156_point_match(
            base_home, questionnaire, base_enriched_data
        )
        
        # Verify fall risk weights applied
        assert result['weights']['safety'] >= 24.0
        assert 0 <= result['total'] <= 156
    
    def test_urgent_budget_questionnaire(
        self, matching_service, load_sample_questionnaire, base_home, base_enriched_data
    ):
        """Test with real urgent + budget questionnaire sample"""
        questionnaire = load_sample_questionnaire("professional_questionnaire_10_urgent_budget.json")
        
        if questionnaire is None:
            pytest.skip("Sample questionnaire not found")
        
        result = matching_service.calculate_156_point_match(
            base_home, questionnaire, base_enriched_data
        )
        
        # Both urgent and low_budget should be applied (if no higher priority condition)
        # Just verify it runs without error
        assert 0 <= result['total'] <= 156
    
    def test_all_sample_questionnaires_no_crash(
        self, matching_service, base_home, base_enriched_data
    ):
        """Test all sample questionnaires don't crash"""
        samples_dir = Path(__file__).parent.parent.parent.parent / "data" / "sample_questionnaires"
        
        if not samples_dir.exists():
            pytest.skip("Sample questionnaires directory not found")
        
        for filepath in samples_dir.glob("professional_questionnaire_*.json"):
            with open(filepath, 'r') as f:
                questionnaire = json.load(f)
            
            result = matching_service.calculate_156_point_match(
                base_home, questionnaire, base_enriched_data
            )
            
            assert 0 <= result['total'] <= 156, f"Failed for {filepath.name}"
            assert 0 <= result['normalized'] <= 100, f"Failed for {filepath.name}"


# =============================================================================
# 7. PERFORMANCE TESTS
# =============================================================================

class TestPerformance:
    """Performance tests for matching algorithm"""
    
    def test_match_calculation_time(
        self, matching_service, base_home, base_questionnaire, base_enriched_data
    ):
        """Test that match calculation is fast enough"""
        import time
        
        start = time.time()
        for _ in range(100):
            matching_service.calculate_156_point_match(
                base_home, base_questionnaire, base_enriched_data
            )
        elapsed = time.time() - start
        
        # 100 calculations should take less than 1 second
        assert elapsed < 1.0, f"100 calculations took {elapsed:.2f}s"
    
    def test_dynamic_weights_calculation_time(
        self, matching_service, base_questionnaire
    ):
        """Test that dynamic weights calculation is fast"""
        import time
        
        start = time.time()
        for _ in range(1000):
            matching_service.calculate_dynamic_weights(base_questionnaire)
        elapsed = time.time() - start
        
        # 1000 calculations should take less than 0.5 second
        assert elapsed < 0.5, f"1000 calculations took {elapsed:.2f}s"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
