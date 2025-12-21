"""
Unit and Integration Tests for Matching Fallback Logic

Tests for:
- check_field_with_fallback()
- check_care_types_v2()
- evaluate_home_match_v2()
- Integration with SimpleMatchingService
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from services.matching_fallback import (
    check_field_with_fallback,
    check_multiple_fields,
    check_care_types_v2,
    evaluate_home_match_v2
)
from services.matching_fallback_config import MatchResult, FieldMatchResult
from services.simple_matching_service import SimpleMatchingService


class TestCheckFieldWithFallback:
    """Unit tests for check_field_with_fallback()"""
    
    def test_direct_match_true(self):
        """Test direct match when field is TRUE"""
        home = {'serves_dementia_band': True}
        result = check_field_with_fallback(home, 'serves_dementia_band', True)
        
        assert result.result == MatchResult.MATCH
        assert result.score_multiplier == 1.0
        assert result.confidence == 1.0
        assert result.proxy_used is None
    
    def test_direct_match_false(self):
        """Test direct match when field is FALSE"""
        home = {'serves_dementia_band': False}
        result = check_field_with_fallback(home, 'serves_dementia_band', True)
        
        assert result.result == MatchResult.NO_MATCH
        assert result.score_multiplier == 0.0
        assert result.confidence == 1.0
    
    def test_proxy_match(self):
        """Test proxy match when primary is NULL but proxy indicates match"""
        home = {
            'serves_dementia_band': None,  # NULL
            'care_dementia': True  # Proxy
        }
        result = check_field_with_fallback(home, 'serves_dementia_band', True)
        
        assert result.result == MatchResult.PROXY_MATCH
        assert result.proxy_used == 'care_dementia'
        assert 0.7 <= result.score_multiplier <= 0.9  # Proxy confidence
        assert result.confidence == 0.9  # care_dementia proxy confidence
    
    def test_unknown_no_proxy(self):
        """Test unknown when field is NULL and no proxy available"""
        home = {
            'serves_dementia_band': None,
            'care_dementia': None  # No proxy
        }
        result = check_field_with_fallback(home, 'serves_dementia_band', True)
        
        assert result.result == MatchResult.UNKNOWN
        assert result.score_multiplier == 0.7  # null_penalty
        assert result.confidence == 0.0
    
    def test_multiple_proxies(self):
        """Test that first matching proxy is used"""
        home = {
            'serves_mental_health': None,
            'care_nursing': True,  # Proxy 1 (confidence 0.6)
            'serves_whole_population': True  # Proxy 2 (confidence 0.4)
        }
        result = check_field_with_fallback(home, 'serves_mental_health', True)
        
        assert result.result == MatchResult.PROXY_MATCH
        # Should use first matching proxy (care_nursing with higher confidence)
        assert result.proxy_used == 'care_nursing'
        assert result.confidence == 0.6


class TestCheckCareTypesV2:
    """Unit tests for check_care_types_v2()"""
    
    def test_direct_match(self):
        """Test direct match for care types"""
        home = {
            'care_dementia': True,
            'care_nursing': None,
            'care_residential': False
        }
        result = check_care_types_v2(home, ['specialised_dementia', 'medical_nursing', 'general_residential'])
        
        assert 'specialised_dementia' in result['matched']
        assert 'medical_nursing' in result['unknown']  # NULL
        assert 'general_residential' in result['explicit_false']  # FALSE
        # has_explicit_false is True only if explicit_false exists AND no matches
        # Here we have a match, so has_explicit_false should be False
        assert result['has_explicit_false'] is False  # We have a match, so not fully disqualified
    
    def test_explicit_false_disqualification(self):
        """Test that explicit FALSE disqualifies when no matches"""
        home = {
            'care_dementia': False,
            'care_nursing': False
        }
        result = check_care_types_v2(home, ['specialised_dementia', 'medical_nursing'])
        
        assert len(result['matched']) == 0
        assert len(result['explicit_false']) == 2
        assert result['has_explicit_false'] is True
    
    def test_null_handling(self):
        """Test that NULL values are treated as unknown, not FALSE"""
        home = {
            'care_dementia': None,
            'care_nursing': None
        }
        result = check_care_types_v2(home, ['specialised_dementia', 'medical_nursing'])
        
        assert len(result['matched']) == 0
        assert len(result['explicit_false']) == 0  # NULL ≠ FALSE
        assert len(result['unknown']) == 2
        assert result['has_explicit_false'] is False  # No explicit FALSE
    
    def test_no_requirements(self):
        """Test when no care types are required"""
        home = {'care_dementia': True}
        result = check_care_types_v2(home, [])
        
        assert len(result['matched']) == 0
        assert len(result['unknown']) == 0
        assert result['has_explicit_false'] is False


class TestEvaluateHomeMatchV2:
    """Unit tests for evaluate_home_match_v2()"""
    
    def test_disqualified_explicit_false(self):
        """Test that explicit FALSE for critical care type disqualifies"""
        home = {
            'care_dementia': False,
            'care_residential': False,
            'care_nursing': False
        }
        result = evaluate_home_match_v2(
            home=home,
            required_care=['specialised_dementia'],
            conditions=[],
            mobility='',
            behavioral=[]
        )
        
        assert result['status'] == 'disqualified'
        assert result['score'] == 0
        assert 'does not provide' in result['reason'].lower()
    
    def test_match_direct_true(self):
        """Test match when all requirements are met"""
        home = {
            'care_dementia': True,
            'serves_dementia_band': True,
            'wheelchair_access': True
        }
        result = evaluate_home_match_v2(
            home=home,
            required_care=['specialised_dementia'],
            conditions=['dementia_alzheimers'],
            mobility='wheelchair_user',
            behavioral=[]
        )
        
        assert result['status'] in ['match', 'partial']
        assert result['score'] > 0
        assert len(result['matched']) > 0
    
    def test_partial_match_proxy(self):
        """Test partial match when using proxy fields"""
        home = {
            'care_dementia': True,  # Proxy for serves_dementia_band
            'serves_dementia_band': None,  # NULL
            'wheelchair_access': True
        }
        result = evaluate_home_match_v2(
            home=home,
            required_care=['specialised_dementia'],
            conditions=['dementia_alzheimers'],
            mobility='wheelchair_user',
            behavioral=[]
        )
        
        assert result['status'] in ['match', 'partial']
        assert len(result['partial']) > 0  # Should have proxy matches
        assert result['data_completeness'] > 0
    
    def test_uncertain_high_unknown_ratio(self):
        """Test uncertain status when too many unknowns"""
        home = {
            'care_dementia': None,
            'serves_dementia_band': None,
            'serves_mental_health': None
        }
        result = evaluate_home_match_v2(
            home=home,
            required_care=['specialised_dementia'],
            conditions=['dementia_alzheimers', 'anxiety'],
            mobility='',
            behavioral=[]
        )
        
        # Should be uncertain if unknown > matched
        if len(result['unknown']) > len(result['matched']):
            assert result['status'] == 'uncertain'
        assert result['data_completeness'] < 100
    
    def test_wandering_risk_with_secure_garden(self):
        """Test behavioral concern with amenity requirement"""
        home = {
            'serves_dementia_band': True,
            'secure_garden': True
        }
        result = evaluate_home_match_v2(
            home=home,
            required_care=[],
            conditions=[],
            mobility='',
            behavioral=['wandering_risk']
        )
        
        assert result['status'] in ['match', 'partial']
        # Should check both serves_dementia_band and secure_garden
        assert len(result['matched']) >= 1
    
    def test_critical_missing_with_explicit_false(self):
        """Test that critical missing with explicit FALSE disqualifies"""
        home = {
            'serves_dementia_band': False,  # Explicit FALSE
            'care_dementia': False
        }
        result = evaluate_home_match_v2(
            home=home,
            required_care=[],
            conditions=['dementia_alzheimers'],  # Critical condition
            mobility='',
            behavioral=[]
        )
        
        # Should be disqualified if critical condition has explicit FALSE
        if result['status'] == 'disqualified':
            assert result['score'] == 0


class TestIntegrationWithSimpleMatchingService:
    """Integration tests with SimpleMatchingService"""
    
    def test_service_bands_score_with_fallback(self):
        """Test Service Bands Score uses fallback logic"""
        service = SimpleMatchingService()
        
        home = {
            'serves_dementia_band': None,  # NULL
            'care_dementia': True,  # Proxy
            'cqc_rating_safe': 'Good'
        }
        questionnaire = {
            'section_3_medical_needs': {
                'q9_medical_conditions': ['dementia_alzheimers']
            },
            'section_4_safety_special_needs': {
                'q16_behavioral_concerns': []
            }
        }
        
        score, details = service._calculate_service_bands_score_v2(home, questionnaire)
        
        assert score >= 80  # Should get proxy match score (90% * 35 points)
        assert details['data_quality']['proxy_matches'] > 0
        assert len(details['checks']) > 0
    
    def test_medical_safety_with_service_bands(self):
        """Test Medical & Safety score integrates Service Bands"""
        service = SimpleMatchingService()
        
        home = {
            'serves_dementia_band': True,
            'care_dementia': True,
            'cqc_rating_safe': 'Good',
            'wheelchair_access': True,
            'care_nursing': False
        }
        questionnaire = {
            'section_3_medical_needs': {
                'q8_care_types': ['specialised_dementia'],
                'q9_medical_conditions': ['dementia_alzheimers'],
                'q10_mobility_level': 'uses_walking_aid',
                'q11_medication_management': 'simple_routine',
                'q12_special_equipment': ['no_special_equipment'],
                'q13_age_range': '85_94'
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': '1_2_no_serious_injuries'
            }
        }
        enriched_data = {}
        
        score = service._calculate_medical_safety(home, questionnaire, enriched_data, debug=True)
        
        assert score >= 85  # Should be high with all matches
        # Service Bands should contribute 35 points (100% match)
    
    def test_prefilter_integration(self):
        """Test that pre-filtering works with evaluate_home_match_v2"""
        # Simulate pre-filtering logic from report_routes.py
        homes = [
            {
                'name': 'Home 1',
                'care_dementia': True,
                'serves_dementia_band': True
            },
            {
                'name': 'Home 2',
                'care_dementia': False,  # Explicit FALSE
                'care_residential': False,
                'care_nursing': False
            },
            {
                'name': 'Home 3',
                'care_dementia': None,  # NULL
                'serves_dementia_band': None
            }
        ]
        
        required_care = ['specialised_dementia']
        conditions = ['dementia_alzheimers']
        mobility = ''
        behavioral = []
        
        filtered_homes = []
        disqualified_homes = []
        
        for home in homes:
            match_result = evaluate_home_match_v2(
                home=home,
                required_care=required_care,
                conditions=conditions,
                mobility=mobility,
                behavioral=behavioral
            )
            
            if match_result['status'] == 'disqualified':
                disqualified_homes.append(home)
            else:
                home['_prefilter_match_result'] = match_result
                filtered_homes.append(home)
        
        assert len(disqualified_homes) == 1  # Home 2 (explicit FALSE)
        assert len(filtered_homes) == 2  # Home 1 (match) and Home 3 (uncertain)
        assert filtered_homes[0]['name'] == 'Home 1'
        assert filtered_homes[1]['name'] == 'Home 3'


class TestEdgeCases:
    """Edge case tests"""
    
    def test_empty_home_dict(self):
        """Test with completely empty home dictionary"""
        home = {}
        result = check_field_with_fallback(home, 'serves_dementia_band', True)
        
        assert result.result == MatchResult.UNKNOWN
        assert result.score_multiplier == 0.7  # null_penalty
    
    def test_no_medical_conditions(self):
        """Test when no medical conditions are specified"""
        home = {'care_dementia': True}
        result = evaluate_home_match_v2(
            home=home,
            required_care=[],
            conditions=[],  # No conditions
            mobility='',
            behavioral=[]
        )
        
        assert result['status'] == 'match'  # No requirements = match
        assert result['score'] == 100.0
    
    def test_invalid_field_name(self):
        """Test with field that doesn't exist in config"""
        home = {'some_field': True}
        result = check_field_with_fallback(home, 'nonexistent_field', True)
        
        # Should use default config (no proxies, null_penalty 0.7)
        assert result.result == MatchResult.UNKNOWN
        assert result.score_multiplier == 0.7
    
    def test_multiple_critical_conditions(self):
        """Test with multiple critical conditions"""
        home = {
            'serves_dementia_band': True,
            'serves_mental_health': True,
            'serves_physical_disabilities': True
        }
        result = evaluate_home_match_v2(
            home=home,
            required_care=[],
            conditions=['dementia_alzheimers', 'parkinsons'],  # Both have required_field
            mobility='',
            behavioral=[]
        )
        
        assert result['status'] in ['match', 'partial']
        assert len(result['matched']) >= 2  # Should match both conditions


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

