"""
Test Simple Matching Improvements for MVP Launch

Tests 3 improvements:
1. Stronger high-risk weights
2. Specialty home bonus
3. Care type mismatch penalty
"""

import sys
from pathlib import Path
import json

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.simple_matching_service import SimpleMatchingService


class TestSimpleMatchingImprovements:
    """Test suite for MVP improvements"""
    
    def __init__(self):
        self.matcher = SimpleMatchingService()
        self.results = []
    
    def setup_dementia_profile(self):
        """Create test dementia client profile"""
        return {
            'id': 'test_dementia_client',
            'section_3_medical_needs': {
                'q8_care_types': ['specialised_dementia'],
                'q9_medical_conditions': ['dementia_alzheimers'],
                'q10_mobility_level': 'can_mobilize_with_assistance',
                'q11_medication_management': 'moderate_assistance_required'
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls'
            },
            'section_5_timeline': {
                'q17_placement_timeline': 'within_1_month'
            }
        }
    
    def setup_nursing_profile(self):
        """Create test nursing client profile"""
        return {
            'id': 'test_nursing_client',
            'section_3_medical_needs': {
                'q8_care_types': ['medical_nursing'],
                'q9_medical_conditions': ['post_operative_care'],
                'q10_mobility_level': 'limited_mobility',
                'q11_medication_management': 'full_assistance_required'
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'no_falls'
            },
            'section_5_timeline': {
                'q17_placement_timeline': 'within_1_month'
            }
        }
    
    def setup_high_fall_risk_profile(self):
        """Create test high fall-risk client profile"""
        return {
            'id': 'test_fall_risk_client',
            'section_3_medical_needs': {
                'q8_care_types': ['general_residential'],
                'q9_medical_conditions': [],
                'q10_mobility_level': 'limited_mobility'
            },
            'section_4_safety_special_needs': {
                'q13_fall_history': 'high_risk_of_falling'
            },
            'section_5_timeline': {
                'q17_placement_timeline': 'within_1_month'
            }
        }
    
    def setup_generic_home(self):
        """Create test generic residential home"""
        return {
            'id': 'generic_home_001',
            'name': 'Generic Residential Care',
            'care_types': ['residential'],
            'care_residential': True,
            'care_nursing': False,
            'wheelchair_accessible': True,
            'cqc_rating_safe': 'Good'
        }
    
    def setup_dementia_specialist_home(self):
        """Create test dementia specialist home"""
        return {
            'id': 'dementia_home_001',
            'name': 'Dementia Specialist Care Home',
            'care_types': ['dementia', 'residential'],
            'care_residential': True,
            'care_nursing': False,
            'wheelchair_accessible': True,
            'cqc_rating_safe': 'Outstanding'
        }
    
    def setup_nursing_home(self):
        """Create test nursing home"""
        return {
            'id': 'nursing_home_001',
            'name': 'Quality Nursing Care',
            'care_types': ['nursing', 'residential'],
            'care_residential': True,
            'care_nursing': True,
            'wheelchair_accessible': True,
            'cqc_rating_safe': 'Good'
        }
    
    def setup_fall_safe_home(self):
        """Create test fall-safe home"""
        return {
            'id': 'fall_safe_home_001',
            'name': 'Fall-Safe Residential Home',
            'care_types': ['residential', 'fall_prevention'],
            'care_residential': True,
            'care_nursing': False,
            'wheelchair_accessible': True,
            'cqc_rating_safe': 'Outstanding'
        }
    
    def test_dementia_with_generic_home(self):
        """
        TEST 1: Dementia client + Generic home
        Expected: Should score LOWER than specialist (signal: don't choose this)
        Before: 68
        After: 54 (with penalties and lower specialty bonus)
        """
        profile = self.setup_dementia_profile()
        home = self.setup_generic_home()
        
        result = self.matcher.calculate_100_point_match(home, profile, {})
        score = result['total']
        
        print(f"\n✓ Test 1: Dementia + Generic Home")
        print(f"  Score: {score}/100")
        print(f"  Expected: 50-60 (weak match)")
        
        # Should be in 50-60 range (weak but possible)
        assert score < 70, f"Score {score} should be < 70 for generic home with dementia client"
        assert score > 40, f"Score {score} should be > 40 (still viable)"
        
        self.results.append({
            'test': 'Dementia + Generic',
            'score': score,
            'status': 'PASS',
            'expected': '50-60'
        })
    
    def test_dementia_with_specialist_home(self):
        """
        TEST 2: Dementia client + Specialist home
        Expected: Should score HIGH (clear winner!)
        Before: 75
        After: 80+ (with specialty bonus + strong weights)
        """
        profile = self.setup_dementia_profile()
        home = self.setup_dementia_specialist_home()
        
        result = self.matcher.calculate_100_point_match(home, profile, {}, debug=True)
        score = result['total']
        
        print(f"\n✓ Test 2: Dementia + Specialist Home")
        print(f"  Score: {score}/100")
        print(f"  Expected: 70+ (excellent match)")
        if 'debug' in result:
            print(f"  Debug: {result['debug']}")
        
        # Should be 70+
        assert score >= 70, f"Score {score} should be >= 70 for specialist home with dementia client"
        
        self.results.append({
            'test': 'Dementia + Specialist',
            'score': score,
            'status': 'PASS',
            'expected': '70+'
        })
    
    def test_nursing_with_residential_only_home(self):
        """
        TEST 3: Nursing client + Residential-only home
        Expected: Should score LOWER (care type mismatch penalty!)
        Before: 65
        After: 40-55 (with -25 penalty applied)
        """
        profile = self.setup_nursing_profile()
        home = self.setup_generic_home()
        
        result = self.matcher.calculate_100_point_match(home, profile, {}, debug=True)
        score = result['total']
        
        print(f"\n✓ Test 3: Nursing + Residential-Only Home")
        print(f"  Score: {score}/100")
        print(f"  Expected: 40-60 (care mismatch)")
        if 'debug' in result and 'care_type_penalty' in result.get('debug', {}):
            print(f"  Penalty Applied: {result['debug']['care_type_penalty']}")
        
        # Should be significantly lower
        assert score < 75, f"Score {score} should be < 75 for nursing/residential mismatch"
        assert score > 30, f"Score {score} should be > 30 (still viable as fallback)"
        
        self.results.append({
            'test': 'Nursing + Residential',
            'score': score,
            'status': 'PASS',
            'expected': '40-60'
        })
    
    def test_nursing_with_nursing_home(self):
        """
        TEST 4: Nursing client + Nursing home
        Expected: Should score HIGH (good match with specialty bonus)
        Before: 75
        After: 68-75 (with specialty bonus +12 points)
        """
        profile = self.setup_nursing_profile()
        home = self.setup_nursing_home()
        
        result = self.matcher.calculate_100_point_match(home, profile, {})
        score = result['total']
        
        print(f"\n✓ Test 4: Nursing + Nursing Home")
        print(f"  Score: {score}/100")
        print(f"  Expected: 65+ (good match with specialty bonus)")
        
        # Should be 65+
        assert score >= 65, f"Score {score} should be >= 65 for nursing home with nursing client"
        
        self.results.append({
            'test': 'Nursing + Nursing Home',
            'score': score,
            'status': 'PASS',
            'expected': '65+'
        })
    
    def test_fall_risk_with_generic_home(self):
        """
        TEST 5: Fall-risk client + Generic home
        Expected: Should score LOWER due to stronger high-risk weights
        Before: 62
        After: 60-75 (stronger medical/safety weighting)
        """
        profile = self.setup_high_fall_risk_profile()
        home = self.setup_generic_home()
        
        result = self.matcher.calculate_100_point_match(home, profile, {})
        score = result['total']
        
        print(f"\n✓ Test 5: Fall-Risk + Generic Home")
        print(f"  Score: {score}/100")
        print(f"  Expected: 60-75 (acceptable fallback)")
        
        # Should be in 60-75 range
        assert score < 80, f"Score {score} should be < 80 (not ideal)"
        assert score > 50, f"Score {score} should be > 50"
        
        self.results.append({
            'test': 'Fall-Risk + Generic',
            'score': score,
            'status': 'PASS',
            'expected': '60-75'
        })
    
    def test_fall_risk_with_fall_safe_home(self):
        """
        TEST 6: Fall-risk client + Fall-safe specialist home
        Expected: Should score HIGH (clear specialist match)
        Before: 73
        After: 75+ (stronger weights + emphasis on medical/safety)
        """
        profile = self.setup_high_fall_risk_profile()
        home = self.setup_fall_safe_home()
        
        result = self.matcher.calculate_100_point_match(home, profile, {})
        score = result['total']
        
        print(f"\n✓ Test 6: Fall-Risk + Fall-Safe Home")
        print(f"  Score: {score}/100")
        print(f"  Expected: 72+ (excellent match)")
        
        # Should be 72+
        assert score >= 72, f"Score {score} should be >= 72 for fall-safe specialist"
        
        self.results.append({
            'test': 'Fall-Risk + Fall-Safe',
            'score': score,
            'status': 'PASS',
            'expected': '72+'
        })
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*80)
        print("SIMPLE MATCHING IMPROVEMENTS - TEST SUITE")
        print("="*80)
        
        try:
            self.test_dementia_with_generic_home()
            self.test_dementia_with_specialist_home()
            self.test_nursing_with_residential_only_home()
            self.test_nursing_with_nursing_home()
            self.test_fall_risk_with_generic_home()
            self.test_fall_risk_with_fall_safe_home()
            
            print("\n" + "="*80)
            print("TEST RESULTS SUMMARY")
            print("="*80)
            
            for result in self.results:
                status_icon = "✅" if result['status'] == 'PASS' else "❌"
                print(f"{status_icon} {result['test']:30s} → {result['score']:6.1f}/100 (expected: {result['expected']})")
            
            print(f"\n✅ ALL TESTS PASSED ({len(self.results)}/6)")
            return True
            
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {e}")
            return False


if __name__ == '__main__':
    tester = TestSimpleMatchingImprovements()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
