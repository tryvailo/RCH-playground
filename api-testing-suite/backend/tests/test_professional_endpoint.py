"""
Unit tests for Professional Report API endpoint

Tests POST /api/professional-report endpoint
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from main import app

client = TestClient(app)


class TestProfessionalReportEndpoint:
    """Tests for /api/professional-report endpoint"""
    
    def test_professional_report_basic_request(self):
        """Test basic professional report request"""
        questionnaire = {
            'section_1_contact_emergency': {
                'q1_names': 'Contact: John Doe; Patient: Jane Doe',
                'q2_email': 'john@example.com',
                'q3_phone': '+44 20 1234 5678',
                'q4_emergency_contact': 'Emergency: +44 20 1234 5679'
            },
            'section_2_location_budget': {
                'q5_preferred_city': 'London',
                'q6_max_distance': 'within_15km',
                'q7_budget': '5000_7000_self'
            },
            'section_3_medical_needs': {
                'q8_care_types': ['general_residential'],
                'q9_medical_conditions': ['no_serious_medical'],
                'q10_mobility_level': 'fully_mobile',
                'q11_medication_management': 'none',
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
        
        response = client.post("/api/professional-report", json=questionnaire)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert 'questionnaire' in data
        assert 'report' in data
        assert 'generated_at' in data
        assert 'report_id' in data
        assert 'status' in data
        
        # Check report structure
        report = data['report']
        assert 'reportId' in report
        assert 'clientName' in report
        assert 'appliedWeights' in report
        assert 'appliedConditions' in report
        assert 'careHomes' in report
        
        # Check weights structure
        weights = report['appliedWeights']
        assert 'medical' in weights
        assert 'safety' in weights
        assert 'location' in weights
        assert 'social' in weights
        assert 'financial' in weights
        assert 'staff' in weights
        assert 'cqc' in weights
        assert 'services' in weights
        
        # Check weights sum to ~100%
        total_weight = sum(weights.values())
        assert abs(total_weight - 100.0) < 1.0
        
        # Check care homes
        assert len(report['careHomes']) == 5
        
        # Check each care home structure
        for home in report['careHomes']:
            assert 'id' in home
            assert 'name' in home
            assert 'matchScore' in home
            assert 'weeklyPrice' in home
            assert 'factorScores' in home
            assert len(home['factorScores']) == 8
    
    def test_professional_report_dementia_profile(self):
        """Test professional report with dementia profile"""
        questionnaire = {
            'section_1_contact_emergency': {
                'q1_names': 'Contact: Test',
                'q2_email': 'test@example.com',
                'q3_phone': '+44 20 1234 5678',
                'q4_emergency_contact': 'Emergency: +44 20 1234 5679'
            },
            'section_2_location_budget': {
                'q5_preferred_city': 'London',
                'q6_max_distance': 'distance_not_important',
                'q7_budget': '5000_7000_local'
            },
            'section_3_medical_needs': {
                'q8_care_types': ['specialised_dementia'],
                'q9_medical_conditions': ['dementia_alzheimers'],
                'q10_mobility_level': 'walking_aids',
                'q11_medication_management': 'simple_1_2',
                'q12_age_range': '85_94'
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls_occurred',
                'q14_allergies': ['no_allergies'],
                'q15_dietary_requirements': ['no_special_requirements'],
                'q16_social_personality': 'prefers_quiet'
            },
            'section_5_timeline': {
                'q17_placement_timeline': 'planning_2_3_months'
            }
        }
        
        response = client.post("/api/professional-report", json=questionnaire)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check dementia condition applied
        assert 'dementia' in data['report']['appliedConditions']
        
        # Check medical weight increased
        assert data['report']['appliedWeights']['medical'] >= 25.0
    
    def test_professional_report_high_fall_risk(self):
        """Test professional report with high fall risk"""
        questionnaire = {
            'section_1_contact_emergency': {
                'q1_names': 'Contact: Test',
                'q2_email': 'test@example.com',
                'q3_phone': '+44 20 1234 5678',
                'q4_emergency_contact': 'Emergency: +44 20 1234 5679'
            },
            'section_2_location_budget': {
                'q5_preferred_city': 'London',
                'q6_max_distance': 'within_5km',
                'q7_budget': 'over_7000_self'
            },
            'section_3_medical_needs': {
                'q8_care_types': ['medical_nursing'],
                'q9_medical_conditions': ['diabetes'],
                'q10_mobility_level': 'wheelchair_sometimes',
                'q11_medication_management': 'many_complex_routine',
                'q12_age_range': '85_94'
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'high_risk_of_falling',  # High fall risk
                'q14_allergies': ['no_allergies'],
                'q15_dietary_requirements': ['no_special_requirements'],
                'q16_social_personality': 'moderately_sociable'
            },
            'section_5_timeline': {
                'q17_placement_timeline': 'urgent_2_weeks'
            }
        }
        
        response = client.post("/api/professional-report", json=questionnaire)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check fall risk condition applied
        assert 'high_fall_risk' in data['report']['appliedConditions']
        
        # Check safety weight increased
        assert data['report']['appliedWeights']['safety'] >= 24.0
        
        # Check other high-priority conditions NOT applied (fall risk overrides)
        assert 'dementia' not in data['report']['appliedConditions']
    
    def test_professional_report_low_budget(self):
        """Test professional report with low budget"""
        questionnaire = {
            'section_1_contact_emergency': {
                'q1_names': 'Contact: Test',
                'q2_email': 'test@example.com',
                'q3_phone': '+44 20 1234 5678',
                'q4_emergency_contact': 'Emergency: +44 20 1234 5679'
            },
            'section_2_location_budget': {
                'q5_preferred_city': 'London',
                'q6_max_distance': 'within_30km',
                'q7_budget': 'under_3000_self'  # Low budget
            },
            'section_3_medical_needs': {
                'q8_care_types': ['general_residential'],
                'q9_medical_conditions': ['no_serious_medical'],
                'q10_mobility_level': 'fully_mobile',
                'q11_medication_management': 'none',
                'q12_age_range': '65_74'
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls_occurred',
                'q14_allergies': ['no_allergies'],
                'q15_dietary_requirements': ['no_special_requirements'],
                'q16_social_personality': 'moderately_sociable'
            },
            'section_5_timeline': {
                'q17_placement_timeline': 'exploring_6_plus_months'
            }
        }
        
        response = client.post("/api/professional-report", json=questionnaire)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check low budget condition applied
        assert 'low_budget' in data['report']['appliedConditions']
        
        # Check financial weight increased
        assert data['report']['appliedWeights']['financial'] >= 18.0
    
    def test_professional_report_multiple_conditions(self):
        """Test professional report with multiple conditions"""
        questionnaire = {
            'section_1_contact_emergency': {
                'q1_names': 'Contact: Test',
                'q2_email': 'test@example.com',
                'q3_phone': '+44 20 1234 5678',
                'q4_emergency_contact': 'Emergency: +44 20 1234 5679'
            },
            'section_2_location_budget': {
                'q5_preferred_city': 'London',
                'q6_max_distance': 'within_15km',
                'q7_budget': '5000_7000_self'
            },
            'section_3_medical_needs': {
                'q8_care_types': ['medical_nursing'],
                'q9_medical_conditions': ['diabetes', 'heart_conditions', 'mobility_problems'],  # 3+ conditions
                'q10_mobility_level': 'wheelchair_sometimes',
                'q11_medication_management': 'many_complex_routine',
                'q12_age_range': '85_94'
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls_occurred',  # No fall risk
                'q14_allergies': ['no_allergies'],
                'q15_dietary_requirements': ['diabetic_diet'],
                'q16_social_personality': 'moderately_sociable'
            },
            'section_5_timeline': {
                'q17_placement_timeline': 'planning_2_3_months'
            }
        }
        
        response = client.post("/api/professional-report", json=questionnaire)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check multiple conditions applied
        assert 'multiple_conditions' in data['report']['appliedConditions']
        
        # Check medical weight increased significantly
        assert data['report']['appliedWeights']['medical'] >= 28.0
    
    def test_professional_report_urgent_placement(self):
        """Test professional report with urgent placement"""
        questionnaire = {
            'section_1_contact_emergency': {
                'q1_names': 'Contact: Test',
                'q2_email': 'test@example.com',
                'q3_phone': '+44 20 1234 5678',
                'q4_emergency_contact': 'Emergency: +44 20 1234 5679'
            },
            'section_2_location_budget': {
                'q5_preferred_city': 'London',
                'q6_max_distance': 'within_5km',
                'q7_budget': '5000_7000_self'
            },
            'section_3_medical_needs': {
                'q8_care_types': ['general_residential'],
                'q9_medical_conditions': ['no_serious_medical'],
                'q10_mobility_level': 'fully_mobile',
                'q11_medication_management': 'none',
                'q12_age_range': '75_84'
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls_occurred',
                'q14_allergies': ['no_allergies'],
                'q15_dietary_requirements': ['no_special_requirements'],
                'q16_social_personality': 'very_sociable'
            },
            'section_5_timeline': {
                'q17_placement_timeline': 'urgent_2_weeks'  # Urgent
            }
        }
        
        response = client.post("/api/professional-report", json=questionnaire)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check urgent condition applied
        assert 'urgent_placement' in data['report']['appliedConditions']
        
        # Check location weight increased
        assert data['report']['appliedWeights']['location'] >= 16.0
    
    def test_professional_report_care_homes_sorted(self):
        """Test that care homes are sorted by match score"""
        questionnaire = {
            'section_1_contact_emergency': {
                'q1_names': 'Contact: Test',
                'q2_email': 'test@example.com',
                'q3_phone': '+44 20 1234 5678',
                'q4_emergency_contact': 'Emergency: +44 20 1234 5679'
            },
            'section_2_location_budget': {
                'q5_preferred_city': 'London',
                'q6_max_distance': 'distance_not_important',
                'q7_budget': '5000_7000_self'
            },
            'section_3_medical_needs': {
                'q8_care_types': ['general_residential'],
                'q9_medical_conditions': ['no_serious_medical'],
                'q10_mobility_level': 'fully_mobile',
                'q11_medication_management': 'none',
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
        
        response = client.post("/api/professional-report", json=questionnaire)
        
        assert response.status_code == 200
        data = response.json()
        
        care_homes = data['report']['careHomes']
        
        # Check homes are sorted by match score (descending)
        for i in range(len(care_homes) - 1):
            assert care_homes[i]['matchScore'] >= care_homes[i + 1]['matchScore']
    
    def test_professional_report_factor_scores_structure(self):
        """Test that factor scores have correct structure"""
        questionnaire = {
            'section_1_contact_emergency': {
                'q1_names': 'Contact: Test',
                'q2_email': 'test@example.com',
                'q3_phone': '+44 20 1234 5678',
                'q4_emergency_contact': 'Emergency: +44 20 1234 5679'
            },
            'section_2_location_budget': {
                'q5_preferred_city': 'London',
                'q6_max_distance': 'distance_not_important',
                'q7_budget': '5000_7000_self'
            },
            'section_3_medical_needs': {
                'q8_care_types': ['general_residential'],
                'q9_medical_conditions': ['no_serious_medical'],
                'q10_mobility_level': 'fully_mobile',
                'q11_medication_management': 'none',
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
        
        response = client.post("/api/professional-report", json=questionnaire)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check first home's factor scores
        first_home = data['report']['careHomes'][0]
        factor_scores = first_home['factorScores']
        
        # Should have 8 categories
        assert len(factor_scores) == 8
        
        # Check each factor score structure
        for factor in factor_scores:
            assert 'category' in factor
            assert 'score' in factor
            assert 'maxScore' in factor
            assert 'weight' in factor
            assert 'verified' in factor
            assert 'dataQuality' in factor
            
            # Check score is within valid range
            assert 0 <= factor['score'] <= factor['maxScore']
            
            # Check weight is positive
            assert factor['weight'] > 0

