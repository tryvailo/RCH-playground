"""
Unit tests for None value handling in NegotiationStrategyService

Tests cover the fixes for:
- turnover_rate_percent None comparison
- bankruptcy_risk_score None comparison
"""
import pytest
from services.negotiation_strategy_service import NegotiationStrategyService


class TestNegotiationStrategyNoneHandling:
    """Test None value handling in NegotiationStrategyService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = NegotiationStrategyService()
    
    def test_identify_priority_questions_with_none_turnover_rate(self):
        """Test _identify_priority_questions handles None turnover_rate_percent"""
        care_homes = [
            {
                'name': 'Test Home',
                'cqcRating': 'Good',
                'staffQuality': {
                    'turnover_rate_percent': None,  # None value
                    'average_tenure_years': 3.5
                }
            }
        ]
        questionnaire = {}
        
        # Should not raise TypeError
        result = self.service._identify_priority_questions(care_homes, questionnaire)
        assert isinstance(result, list)
    
    def test_identify_priority_questions_with_none_bankruptcy_risk(self):
        """Test _identify_priority_questions handles None bankruptcy_risk_score"""
        care_homes = [
            {
                'name': 'Test Home',
                'cqcRating': 'Good',
                'financialStability': {
                    'bankruptcy_risk_score': None,  # None value
                    'altman_z_score': 2.5
                }
            }
        ]
        questionnaire = {}
        
        # Should not raise TypeError
        result = self.service._identify_priority_questions(care_homes, questionnaire)
        assert isinstance(result, list)
    
    def test_identify_priority_questions_with_string_turnover_rate(self):
        """Test _identify_priority_questions handles string turnover_rate_percent"""
        care_homes = [
            {
                'name': 'Test Home',
                'cqcRating': 'Good',
                'staffQuality': {
                    'turnover_rate_percent': '35',  # String value
                    'average_tenure_years': 3.5
                }
            }
        ]
        questionnaire = {}
        
        # Should not raise TypeError
        result = self.service._identify_priority_questions(care_homes, questionnaire)
        assert isinstance(result, list)
    
    def test_identify_priority_questions_with_string_bankruptcy_risk(self):
        """Test _identify_priority_questions handles string bankruptcy_risk_score"""
        care_homes = [
            {
                'name': 'Test Home',
                'cqcRating': 'Good',
                'financialStability': {
                    'bankruptcy_risk_score': '55',  # String value
                    'altman_z_score': 2.5
                }
            }
        ]
        questionnaire = {}
        
        # Should not raise TypeError
        result = self.service._identify_priority_questions(care_homes, questionnaire)
        assert isinstance(result, list)
    
    def test_identify_priority_questions_with_high_turnover_rate(self):
        """Test _identify_priority_questions identifies high turnover rate"""
        care_homes = [
            {
                'name': 'Test Home',
                'cqcRating': 'Good',
                'staffQuality': {
                    'turnover_rate_percent': 35.0,  # High turnover
                    'average_tenure_years': 1.5
                }
            }
        ]
        questionnaire = {}
        
        result = self.service._identify_priority_questions(care_homes, questionnaire)
        assert len(result) > 0
        assert any('turnover' in q.lower() for q in result)
    
    def test_identify_priority_questions_with_high_bankruptcy_risk(self):
        """Test _identify_priority_questions identifies high bankruptcy risk"""
        care_homes = [
            {
                'name': 'Test Home',
                'cqcRating': 'Good',
                'financialStability': {
                    'bankruptcy_risk_score': 55.0,  # High risk
                    'altman_z_score': 1.5
                }
            }
        ]
        questionnaire = {}
        
        result = self.service._identify_priority_questions(care_homes, questionnaire)
        assert len(result) > 0
        assert any('financial' in q.lower() for q in result)
    
    def test_identify_priority_questions_with_missing_staff_quality(self):
        """Test _identify_priority_questions handles missing staffQuality"""
        care_homes = [
            {
                'name': 'Test Home',
                'cqcRating': 'Good'
                # No staffQuality field
            }
        ]
        questionnaire = {}
        
        # Should not raise AttributeError or TypeError
        result = self.service._identify_priority_questions(care_homes, questionnaire)
        assert isinstance(result, list)
    
    def test_identify_priority_questions_with_missing_financial_stability(self):
        """Test _identify_priority_questions handles missing financialStability"""
        care_homes = [
            {
                'name': 'Test Home',
                'cqcRating': 'Good'
                # No financialStability field
            }
        ]
        questionnaire = {}
        
        # Should not raise AttributeError or TypeError
        result = self.service._identify_priority_questions(care_homes, questionnaire)
        assert isinstance(result, list)
    
    def test_identify_priority_questions_with_empty_care_homes(self):
        """Test _identify_priority_questions handles empty care homes list"""
        care_homes = []
        questionnaire = {}
        
        result = self.service._identify_priority_questions(care_homes, questionnaire)
        assert isinstance(result, list)
        assert len(result) == 0

