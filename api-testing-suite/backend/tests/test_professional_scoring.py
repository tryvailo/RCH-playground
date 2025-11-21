"""
Unit tests for Professional Matching Service Scoring Methods

Tests all 8 scoring category methods:
1. Medical Capabilities (0-30 points)
2. Safety & Quality (0-25 points)
3. Location & Access (0-15 points)
4. Cultural & Social (0-15 points)
5. Financial Stability (0-20 points)
6. Staff Quality (0-20 points)
7. CQC Compliance (0-20 points)
8. Additional Services (0-11 points)
"""

import pytest
import sys
from pathlib import Path

# Add services to path
services_path = Path(__file__).parent.parent / "services"
if str(services_path) not in sys.path:
    sys.path.insert(0, str(services_path))

from services.professional_matching_service import ProfessionalMatchingService


class TestMedicalCapabilitiesScoring:
    """Tests for medical capabilities scoring (0-30 points)"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.service = ProfessionalMatchingService()
    
    def test_medical_capabilities_dementia_match(self):
        """Test specialist care match for dementia"""
        home = {
            'care_types': ['dementia', 'residential'],
            'care_dementia': True,
            'wheelchair_accessible': True,
            'medical_equipment': True,
            'on_site_pharmacy': True
        }
        user_profile = {
            'section_3_medical_needs': {
                'q9_medical_conditions': ['dementia_alzheimers'],
                'q8_care_types': ['specialised_dementia'],
                'q10_mobility_level': 'walking_aids',
                'q11_medication_management': 'simple_1_2'
            }
        }
        enriched_data = {
            'staff_data': {'registered_nurses': 2},
            'medical_capabilities': {
                'emergency_response_time': 5,
                'medication_management': True,
                'emergency_protocols': True
            }
        }
        
        score = self.service._calculate_medical_capabilities(home, user_profile, enriched_data)
        
        # Should score well for dementia care
        assert 0.0 <= score <= 1.0
        assert score >= 0.6  # Good match
    
    def test_medical_capabilities_nursing_required(self):
        """Test nursing level scoring"""
        home = {
            'care_types': ['nursing'],
            'care_nursing': True,
            'medical_equipment': True
        }
        user_profile = {
            'section_3_medical_needs': {
                'q8_care_types': ['medical_nursing'],
                'q9_medical_conditions': ['diabetes'],
                'q10_mobility_level': 'wheelchair_sometimes',
                'q11_medication_management': 'many_complex_routine'
            }
        }
        enriched_data = {
            'staff_data': {'registered_nurses': 3},
            'medical_capabilities': {
                'emergency_response_time': 5,
                'medication_management': True
            }
        }
        
        score = self.service._calculate_medical_capabilities(home, user_profile, enriched_data)
        
        # Should score well for nursing care
        assert 0.0 <= score <= 1.0
        assert score >= 0.7  # Good nursing match
    
    def test_medical_capabilities_mobility_support(self):
        """Test mobility support scoring"""
        home = {
            'care_types': ['residential'],
            'wheelchair_accessible': True,
            'medical_equipment': False
        }
        user_profile = {
            'section_3_medical_needs': {
                'q9_medical_conditions': ['mobility_problems'],
                'q10_mobility_level': 'wheelchair_permanent',
                'q8_care_types': ['general_residential']
            }
        }
        enriched_data = {
            'staff_data': {'registered_nurses': 0},
            'medical_capabilities': {}
        }
        
        score = self.service._calculate_medical_capabilities(home, user_profile, enriched_data)
        
        # Should score for wheelchair accessibility
        assert 0.0 <= score <= 1.0
        assert score >= 0.3
    
    def test_medical_capabilities_no_match(self):
        """Test scoring when home doesn't match needs"""
        home = {
            'care_types': ['residential'],
            'care_nursing': False,
            'care_dementia': False,
            'wheelchair_accessible': False,
            'medical_equipment': False
        }
        user_profile = {
            'section_3_medical_needs': {
                'q8_care_types': ['medical_nursing'],
                'q9_medical_conditions': ['dementia_alzheimers'],
                'q10_mobility_level': 'wheelchair_permanent'
            }
        }
        enriched_data = {
            'staff_data': {'registered_nurses': 0},
            'medical_capabilities': {}
        }
        
        score = self.service._calculate_medical_capabilities(home, user_profile, enriched_data)
        
        # Should score low
        assert 0.0 <= score <= 1.0
        assert score < 0.4


class TestSafetyQualityScoring:
    """Tests for safety & quality scoring (0-25 points)"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.service = ProfessionalMatchingService()
    
    def test_safety_quality_outstanding_cqc(self):
        """Test scoring with Outstanding CQC rating"""
        home = {
            'rating': 'Outstanding',
            'overall_rating': 'Outstanding'
        }
        user_profile = {
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls_occurred'
            }
        }
        enriched_data = {
            'cqc_detailed': {
                'overall_rating': 'Outstanding',
                'safe_rating': 'Outstanding',
                'trend': 'improving',
                'safeguarding_incidents': 0
            },
            'fsa_detailed': {'rating': 5},
            'financial_data': {'filing_compliance': True}
        }
        
        score = self.service._calculate_safety_quality(home, user_profile, enriched_data)
        
        # Should score very high
        assert 0.0 <= score <= 1.0
        assert score >= 0.8
    
    def test_safety_quality_high_fall_risk(self):
        """Test scoring with high fall risk user"""
        home = {
            'rating': 'Good',
            'overall_rating': 'Good'
        }
        user_profile = {
            'section_4_safety_special_needs': {
                'q13_fall_history': 'high_risk_of_falling'
            }
        }
        enriched_data = {
            'cqc_detailed': {
                'overall_rating': 'Good',
                'safe_rating': 'Outstanding',  # Important for fall risk
                'trend': 'stable',
                'safeguarding_incidents': 0
            },
            'fsa_detailed': {'rating': 5},
            'financial_data': {'filing_compliance': True}
        }
        
        score = self.service._calculate_safety_quality(home, user_profile, enriched_data)
        
        # Should score well due to Outstanding Safe rating
        assert 0.0 <= score <= 1.0
        assert score >= 0.7
    
    def test_safety_quality_fsa_rating(self):
        """Test FSA food safety rating scoring"""
        home = {'rating': 'Good'}
        user_profile = {'section_4_safety_special_needs': {'q13_fall_history': 'no_falls_occurred'}}
        
        # Test FSA rating 5
        enriched_data = {
            'cqc_detailed': {'overall_rating': 'Good', 'trend': 'stable', 'safeguarding_incidents': 0},
            'fsa_detailed': {'rating': 5},
            'financial_data': {'filing_compliance': True}
        }
        score_5 = self.service._calculate_safety_quality(home, user_profile, enriched_data)
        
        # Test FSA rating 3
        enriched_data['fsa_detailed'] = {'rating': 3}
        score_3 = self.service._calculate_safety_quality(home, user_profile, enriched_data)
        
        # Rating 5 should score higher
        assert score_5 > score_3
    
    def test_safety_quality_incidents_penalty(self):
        """Test safeguarding incidents penalty"""
        home = {'rating': 'Good'}
        user_profile = {'section_4_safety_special_needs': {'q13_fall_history': 'no_falls_occurred'}}
        
        # No incidents
        enriched_data = {
            'cqc_detailed': {
                'overall_rating': 'Good',
                'trend': 'stable',
                'safeguarding_incidents': 0
            },
            'fsa_detailed': {'rating': 5},
            'financial_data': {'filing_compliance': True}
        }
        score_no_incidents = self.service._calculate_safety_quality(home, user_profile, enriched_data)
        
        # With incidents
        enriched_data['cqc_detailed']['safeguarding_incidents'] = 3
        score_with_incidents = self.service._calculate_safety_quality(home, user_profile, enriched_data)
        
        # Should penalize incidents
        assert score_no_incidents > score_with_incidents


class TestLocationAccessScoring:
    """Tests for location & access scoring (0-15 points)"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.service = ProfessionalMatchingService()
    
    def test_location_access_within_5km(self):
        """Test distance scoring within 5km"""
        home = {
            'latitude': 51.5074,
            'longitude': -0.1278
        }
        user_profile = {
            'section_2_location_budget': {
                'q6_max_distance': 'within_5km',
                'user_latitude': 51.5074,
                'user_longitude': -0.1278
            }
        }
        
        score = self.service._calculate_location_access(home, user_profile)
        
        # Should score maximum for same location
        assert 0.0 <= score <= 1.0
        assert score >= 0.9
    
    def test_location_access_public_transport(self):
        """Test public transport scoring"""
        home = {
            'latitude': 51.5074,
            'longitude': -0.1278,
            'public_transport_nearby': True,
            'visitor_parking': True
        }
        user_profile = {
            'section_2_location_budget': {
                'q6_max_distance': 'distance_not_important',
                'user_latitude': 51.5074,
                'user_longitude': -0.1278
            }
        }
        
        score = self.service._calculate_location_access(home, user_profile)
        
        # Should score well for transport and parking
        assert 0.0 <= score <= 1.0
        assert score >= 0.7
    
    def test_location_access_distance_not_important(self):
        """Test scoring when distance is not important"""
        home = {
            'latitude': 51.6000,  # Far away
            'longitude': -0.2000,
            'public_transport_nearby': True,
            'visitor_parking': True
        }
        user_profile = {
            'section_2_location_budget': {
                'q6_max_distance': 'distance_not_important',
                'user_latitude': 51.5074,
                'user_longitude': -0.1278
            }
        }
        
        score = self.service._calculate_location_access(home, user_profile)
        
        # Should still score for transport/parking even if far
        assert 0.0 <= score <= 1.0
        assert score >= 0.3
    
    def test_location_access_missing_coordinates(self):
        """Test scoring with missing coordinates"""
        home = {}
        user_profile = {
            'section_2_location_budget': {
                'q6_max_distance': 'within_5km'
            }
        }
        
        score = self.service._calculate_location_access(home, user_profile)
        
        # Should return default score
        assert 0.0 <= score <= 1.0


class TestCulturalSocialScoring:
    """Tests for cultural & social scoring (0-15 points)"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.service = ProfessionalMatchingService()
    
    def test_cultural_social_high_engagement(self):
        """Test scoring with high visitor engagement"""
        home = {
            'google_review_count': 50,
            'activities': ['arts', 'music', 'gardening', 'outings', 'exercise'],
            'local_partnerships': True,
            'community_events': True
        }
        user_profile = {
            'section_4_safety_special_needs': {
                'q16_social_personality': 'very_sociable'
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
        
        score = self.service._calculate_cultural_social(home, user_profile, enriched_data)
        
        # Should score very high
        assert 0.0 <= score <= 1.0
        assert score >= 0.8
    
    def test_cultural_social_quiet_personality(self):
        """Test scoring for quiet personality"""
        home = {
            'google_review_count': 20,
            'activities': ['arts', 'music'],
            'local_partnerships': False
        }
        user_profile = {
            'section_4_safety_special_needs': {
                'q16_social_personality': 'prefers_quiet'
            }
        }
        enriched_data = {
            'google_places': {
                'review_count': 20,
                'average_dwell_time_minutes': 20,
                'repeat_visitor_rate': 0.2
            }
        }
        
        score = self.service._calculate_cultural_social(home, user_profile, enriched_data)
        
        # Should score moderately (not too many activities)
        assert 0.0 <= score <= 1.0
        assert score >= 0.4
    
    def test_cultural_social_low_engagement(self):
        """Test scoring with low engagement"""
        home = {
            'google_review_count': 5,
            'activities': [],
            'local_partnerships': False
        }
        user_profile = {
            'section_4_safety_special_needs': {
                'q16_social_personality': 'very_sociable'
            }
        }
        enriched_data = {
            'google_places': {
                'review_count': 5,
                'average_dwell_time_minutes': 10,
                'repeat_visitor_rate': 0.1
            }
        }
        
        score = self.service._calculate_cultural_social(home, user_profile, enriched_data)
        
        # Should score low
        assert 0.0 <= score <= 1.0
        assert score < 0.4


class TestFinancialStabilityScoring:
    """Tests for financial stability scoring (0-20 points)"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.service = ProfessionalMatchingService()
    
    def test_financial_stability_excellent(self):
        """Test scoring with excellent financials"""
        home = {}
        enriched_data = {
            'financial_data': {
                'net_margin_3year_avg': 0.20,  # 20% margin
                'current_ratio': 2.5,  # Excellent liquidity
                'altman_z_score': 3.5,  # Very safe
                'filing_compliance': True
            }
        }
        
        score = self.service._calculate_financial_stability(home, enriched_data)
        
        # Should score very high
        assert 0.0 <= score <= 1.0
        assert score >= 0.9
    
    def test_financial_stability_bankruptcy_risk(self):
        """Test scoring with bankruptcy risk"""
        home = {}
        enriched_data = {
            'financial_data': {
                'net_margin_3year_avg': 0.05,
                'current_ratio': 0.8,  # Poor liquidity
                'altman_z_score': 1.5,  # High risk
                'filing_compliance': True
            }
        }
        
        score = self.service._calculate_financial_stability(home, enriched_data)
        
        # Should score low
        assert 0.0 <= score <= 1.0
        assert score < 0.4
    
    def test_financial_stability_altman_z_score(self):
        """Test Altman Z-score impact"""
        home = {}
        
        # Safe Z-score
        enriched_data_safe = {
            'financial_data': {
                'net_margin_3year_avg': 0.10,
                'current_ratio': 1.5,
                'altman_z_score': 3.0,
                'filing_compliance': True
            }
        }
        score_safe = self.service._calculate_financial_stability(home, enriched_data_safe)
        
        # Risky Z-score
        enriched_data_risky = {
            'financial_data': {
                'net_margin_3year_avg': 0.10,
                'current_ratio': 1.5,
                'altman_z_score': 1.5,  # High risk
                'filing_compliance': True
            }
        }
        score_risky = self.service._calculate_financial_stability(home, enriched_data_risky)
        
        # Safe should score higher
        assert score_safe > score_risky


class TestStaffQualityScoring:
    """Tests for staff quality scoring (0-20 points)"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.service = ProfessionalMatchingService()
    
    def test_staff_quality_excellent(self):
        """Test scoring with excellent staff quality"""
        home = {}
        enriched_data = {
            'staff_data': {
                'glassdoor_rating': 4.5,
                'average_tenure_years': 5.0,
                'annual_turnover_rate': 0.08  # Low turnover
            }
        }
        
        score = self.service._calculate_staff_quality(home, enriched_data)
        
        # Should score very high
        assert 0.0 <= score <= 1.0
        assert score >= 0.9
    
    def test_staff_quality_high_turnover(self):
        """Test scoring with high turnover"""
        home = {}
        enriched_data = {
            'staff_data': {
                'glassdoor_rating': 3.5,
                'average_tenure_years': 1.0,
                'annual_turnover_rate': 0.6  # Very high turnover
            }
        }
        
        score = self.service._calculate_staff_quality(home, enriched_data)
        
        # Should score low
        assert 0.0 <= score <= 1.0
        assert score < 0.4
    
    def test_staff_quality_tenure_impact(self):
        """Test tenure impact on scoring"""
        home = {}
        
        # Long tenure
        enriched_data_long = {
            'staff_data': {
                'glassdoor_rating': 4.0,
                'average_tenure_years': 5.0,
                'annual_turnover_rate': 0.15
            }
        }
        score_long = self.service._calculate_staff_quality(home, enriched_data_long)
        
        # Short tenure
        enriched_data_short = {
            'staff_data': {
                'glassdoor_rating': 4.0,
                'average_tenure_years': 0.5,
                'annual_turnover_rate': 0.15
            }
        }
        score_short = self.service._calculate_staff_quality(home, enriched_data_short)
        
        # Long tenure should score higher
        assert score_long > score_short


class TestCQCComplianceScoring:
    """Tests for CQC compliance scoring (0-20 points)"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.service = ProfessionalMatchingService()
    
    def test_cqc_compliance_all_outstanding(self):
        """Test scoring with all Outstanding ratings"""
        home = {
            'rating': 'Outstanding',
            'overall_rating': 'Outstanding'
        }
        enriched_data = {
            'cqc_detailed': {
                'safe_rating': 'Outstanding',
                'effective_rating': 'Outstanding',
                'caring_rating': 'Outstanding',
                'responsive_rating': 'Outstanding',
                'well_led_rating': 'Outstanding'
            }
        }
        
        score = self.service._calculate_cqc_compliance(home, enriched_data)
        
        # Should score maximum (all 4 points each = 20/20)
        assert 0.0 <= score <= 1.0
        assert score >= 0.95
    
    def test_cqc_compliance_mixed_ratings(self):
        """Test scoring with mixed ratings"""
        home = {'rating': 'Good'}
        enriched_data = {
            'cqc_detailed': {
                'safe_rating': 'Good',
                'effective_rating': 'Outstanding',
                'caring_rating': 'Good',
                'responsive_rating': 'Requires improvement',
                'well_led_rating': 'Good'
            }
        }
        
        score = self.service._calculate_cqc_compliance(home, enriched_data)
        
        # Should score moderately
        assert 0.0 <= score <= 1.0
        assert 0.5 <= score <= 0.8
    
    def test_cqc_compliance_missing_ratings(self):
        """Test scoring with missing ratings"""
        home = {'rating': 'Good'}
        enriched_data = {
            'cqc_detailed': {}
        }
        
        score = self.service._calculate_cqc_compliance(home, enriched_data)
        
        # Should use defaults
        assert 0.0 <= score <= 1.0


class TestAdditionalServicesScoring:
    """Tests for additional services scoring (0-11 points)"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.service = ProfessionalMatchingService()
    
    def test_additional_services_comprehensive(self):
        """Test scoring with comprehensive services"""
        home = {
            'physiotherapy_available': True,
            'mental_health_services': True,
            'specialist_programs': ['dementia', 'diabetes'],
            'enrichment_activities': ['arts', 'music', 'gardening', 'outings', 'exercise']
        }
        user_profile = {
            'section_3_medical_needs': {
                'q9_medical_conditions': ['dementia_alzheimers']
            }
        }
        
        score = self.service._calculate_additional_services(home, user_profile)
        
        # Should score very high
        assert 0.0 <= score <= 1.0
        assert score >= 0.8
    
    def test_additional_services_minimal(self):
        """Test scoring with minimal services"""
        home = {
            'physiotherapy_available': False,
            'mental_health_services': False,
            'specialist_programs': [],
            'enrichment_activities': []
        }
        user_profile = {
            'section_3_medical_needs': {
                'q9_medical_conditions': ['no_serious_medical']
            }
        }
        
        score = self.service._calculate_additional_services(home, user_profile)
        
        # Should score low
        assert 0.0 <= score <= 1.0
        assert score < 0.3
    
    def test_additional_services_specialist_match(self):
        """Test scoring with specialist program match"""
        home = {
            'physiotherapy_available': True,
            'specialist_programs': ['dementia']
        }
        user_profile = {
            'section_3_medical_needs': {
                'q9_medical_conditions': ['dementia_alzheimers']
            }
        }
        
        score = self.service._calculate_additional_services(home, user_profile)
        
        # Should score well for matching specialist program
        assert 0.0 <= score <= 1.0
        assert score >= 0.5


class Test156PointMatch:
    """Tests for full 156-point match calculation"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.service = ProfessionalMatchingService()
    
    def test_calculate_156_point_match_with_weights(self):
        """Test full match calculation with dynamic weights"""
        home = {
            'id': 'test-home-1',
            'name': 'Test Home',
            'latitude': 51.5074,
            'longitude': -0.1278,
            'care_types': ['residential', 'nursing'],
            'care_nursing': True,
            'care_dementia': True,
            'rating': 'Good',
            'overall_rating': 'Good',
            'fsa_rating': 5,
            'weekly_cost': 800,
            'public_transport_nearby': True,
            'visitor_parking': True,
            'wheelchair_accessible': True,
            'medical_equipment': True,
            'physiotherapy_available': True,
            'specialist_programs': ['dementia'],
            'activities': ['arts', 'music'],
            'google_review_count': 30
        }
        
        user_profile = {
            'section_2_location_budget': {
                'q6_max_distance': 'within_15km',
                'user_latitude': 51.5074,
                'user_longitude': -0.1278
            },
            'section_3_medical_needs': {
                'q8_care_types': ['medical_nursing'],
                'q9_medical_conditions': ['dementia_alzheimers'],
                'q10_mobility_level': 'walking_aids',
                'q11_medication_management': 'simple_1_2'
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls_occurred',
                'q16_social_personality': 'moderately_sociable'
            }
        }
        
        enriched_data = {
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
            'fsa_detailed': {'rating': 5},
            'financial_data': {
                'net_margin_3year_avg': 0.12,
                'current_ratio': 1.8,
                'altman_z_score': 2.8,
                'filing_compliance': True
            },
            'staff_data': {
                'glassdoor_rating': 4.2,
                'average_tenure_years': 3.5,
                'annual_turnover_rate': 0.15,
                'registered_nurses': 2
            },
            'google_places': {
                'review_count': 30,
                'average_dwell_time_minutes': 45,
                'repeat_visitor_rate': 0.4,
                'community_integration_score': 0.6
            },
            'medical_capabilities': {
                'emergency_response_time': 5,
                'medication_management': True,
                'emergency_protocols': True
            }
        }
        
        result = self.service.calculate_156_point_match(home, user_profile, enriched_data)
        
        # Check result structure
        assert 'total' in result
        assert 'normalized' in result
        assert 'weights' in result
        assert 'category_scores' in result
        assert 'point_allocations' in result
        
        # Check scores are within valid range
        assert 0 <= result['total'] <= 156
        assert 0 <= result['normalized'] <= 100
        
        # Check all category scores present
        assert 'medical' in result['category_scores']
        assert 'safety' in result['category_scores']
        assert 'location' in result['category_scores']
        assert 'social' in result['category_scores']
        assert 'financial' in result['category_scores']
        assert 'staff' in result['category_scores']
        assert 'cqc' in result['category_scores']
        assert 'services' in result['category_scores']
        
        # Check weights sum to 100%
        weights = result['weights']
        total_weight = sum(weights.values())
        assert abs(total_weight - 100.0) < 0.1
    
    def test_calculate_156_point_match_dementia_weights(self):
        """Test match calculation with dementia weights"""
        home = {
            'care_types': ['dementia'],
            'care_dementia': True,
            'latitude': 51.5074,
            'longitude': -0.1278,
            'rating': 'Good',
            'specialist_programs': ['dementia']
        }
        
        user_profile = {
            'section_2_location_budget': {
                'q6_max_distance': 'distance_not_important',
                'user_latitude': 51.5074,
                'user_longitude': -0.1278
            },
            'section_3_medical_needs': {
                'q9_medical_conditions': ['dementia_alzheimers'],
                'q8_care_types': ['specialised_dementia']
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls_occurred'
            }
        }
        
        enriched_data = {
            'cqc_detailed': {'overall_rating': 'Good', 'safe_rating': 'Good', 'effective_rating': 'Good',
                           'caring_rating': 'Good', 'responsive_rating': 'Good', 'well_led_rating': 'Good',
                           'trend': 'stable', 'safeguarding_incidents': 0},
            'fsa_detailed': {'rating': 5},
            'financial_data': {'net_margin_3year_avg': 0.10, 'current_ratio': 1.5, 'altman_z_score': 2.5,
                              'filing_compliance': True},
            'staff_data': {'glassdoor_rating': 4.0, 'average_tenure_years': 3.0, 'annual_turnover_rate': 0.15},
            'google_places': {'review_count': 20, 'average_dwell_time_minutes': 30, 'repeat_visitor_rate': 0.3},
            'medical_capabilities': {'emergency_response_time': 5, 'medication_management': True}
        }
        
        result = self.service.calculate_156_point_match(home, user_profile, enriched_data)
        
        # With dementia, medical weight should be higher
        assert result['weights']['medical'] >= 25.0  # Dementia increases medical weight
        
        # Medical category should contribute more points
        assert result['point_allocations']['medical'] > result['point_allocations']['services']

