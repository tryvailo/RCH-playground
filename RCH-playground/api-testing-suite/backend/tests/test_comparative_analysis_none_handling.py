"""
Unit tests for None value handling in ComparativeAnalysisService

Tests cover the fixes for:
- None weeklyPrice values
- None altman_z values
- None match_score values
- None top_score, score_range, price_range values
"""
import pytest
from services.comparative_analysis_service import ComparativeAnalysisService


class TestComparativeAnalysisNoneHandling:
    """Test None value handling in ComparativeAnalysisService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = ComparativeAnalysisService()
    
    def test_generate_comparative_analysis_with_none_weekly_price(self):
        """Test generate_comparative_analysis handles None weeklyPrice"""
        care_homes = [
            {
                'id': '1',
                'name': 'Test Home 1',
                'matchScore': 85.5,
                'weeklyPrice': None,  # None value
                'cqcRating': 'Good'
            },
            {
                'id': '2',
                'name': 'Test Home 2',
                'matchScore': 80.0,
                'weeklyPrice': 850,
                'cqcRating': 'Good'
            }
        ]
        questionnaire = {}
        
        # Should not raise TypeError
        result = self.service.generate_comparative_analysis(care_homes, questionnaire)
        assert 'comparison_table' in result
        assert 'price_comparison' in result
    
    def test_generate_comparative_analysis_with_none_match_score(self):
        """Test generate_comparative_analysis handles None matchScore"""
        care_homes = [
            {
                'id': '1',
                'name': 'Test Home 1',
                'matchScore': None,  # None value
                'weeklyPrice': 800,
                'cqcRating': 'Good'
            }
        ]
        questionnaire = {}
        
        # Should not raise TypeError
        result = self.service.generate_comparative_analysis(care_homes, questionnaire)
        assert 'rankings' in result
    
    def test_identify_key_differentiators_with_none_altman_z(self):
        """Test _identify_key_differentiators handles None altman_z_score"""
        care_homes = [
            {
                'id': '1',
                'name': 'Test Home 1',
                'matchScore': 85.0,
                'weeklyPrice': 800,
                'financialStability': {
                    'altman_z_score': None,  # None value
                    'bankruptcy_risk_score': 30
                }
            },
            {
                'id': '2',
                'name': 'Test Home 2',
                'matchScore': 80.0,
                'weeklyPrice': 850,
                'financialStability': {
                    'altman_z_score': 2.5,
                    'bankruptcy_risk_score': 25
                }
            }
        ]
        questionnaire = {}
        
        # Should not raise TypeError
        result = self.service._identify_key_differentiators(care_homes, questionnaire)
        assert isinstance(result, list)
    
    def test_analyze_score_tiers_with_none_match_scores(self):
        """Test _analyze_score_tiers handles None match_score values"""
        rankings = [
            {
                'home_name': 'Test Home 1',
                'match_score': None,  # None value
                'rank': 1
            },
            {
                'home_name': 'Test Home 2',
                'match_score': 85.0,
                'rank': 2
            },
            {
                'home_name': 'Test Home 3',
                'match_score': 80.0,
                'rank': 3
            }
        ]
        
        # Should not raise TypeError
        result = self.service._analyze_score_tiers(rankings)
        assert 'tier_1_excellent' in result
        assert 'tier_2_very_good' in result
    
    def test_generate_recommendation_with_none_values(self):
        """Test _generate_recommendation handles None top_score, score_range, price_range"""
        homes = [
            {
                'id': '1',
                'name': 'Test Home 1',
                'matchScore': None,  # None value
                'weeklyPrice': None  # None value
            }
        ]
        rankings = {
            'statistics': {
                'score_range': None  # None value
            }
        }
        price_comparison = {
            'statistics': {
                'price_range': None  # None value
            }
        }
        
        # Should not raise TypeError
        result = self.service._generate_recommendation(homes, rankings, price_comparison)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_calculate_value_score_with_none_price(self):
        """Test _calculate_value_score handles None price parameter"""
        home = {
            'id': '1',
            'name': 'Test Home',
            'matchScore': 85.0
        }
        price = None  # None value
        avg_price = 850.0
        
        # Should not raise TypeError
        result = self.service._calculate_value_score(home, price, avg_price)
        assert isinstance(result, (int, float))
        assert result >= 0
    
    def test_calculate_value_score_with_none_match_score(self):
        """Test _calculate_value_score handles None matchScore in home"""
        home = {
            'id': '1',
            'name': 'Test Home',
            'matchScore': None  # None value
        }
        price = 800.0
        avg_price = 850.0
        
        # Should not raise TypeError
        result = self.service._calculate_value_score(home, price, avg_price)
        assert isinstance(result, (int, float))
        assert result >= 0
    
    def test_generate_price_comparison_with_none_prices(self):
        """Test _generate_price_comparison handles None weeklyPrice values"""
        care_homes = [
            {
                'id': '1',
                'name': 'Test Home 1',
                'weeklyPrice': None,  # None value
                'matchScore': 85.0
            },
            {
                'id': '2',
                'name': 'Test Home 2',
                'weeklyPrice': 850,
                'matchScore': 80.0
            },
            {
                'id': '3',
                'name': 'Test Home 3',
                'weeklyPrice': None,  # None value
                'matchScore': 75.0
            }
        ]
        
        # Should not raise TypeError
        result = self.service._generate_price_comparison(care_homes)
        assert 'statistics' in result
        assert 'homes' in result
    
    def test_generate_match_score_rankings_with_none_scores(self):
        """Test _generate_match_score_rankings handles None matchScore values"""
        care_homes = [
            {
                'id': '1',
                'name': 'Test Home 1',
                'matchScore': None,  # None value
                'weeklyPrice': 800
            },
            {
                'id': '2',
                'name': 'Test Home 2',
                'matchScore': 85.0,
                'weeklyPrice': 850
            }
        ]
        
        # Should not raise TypeError
        result = self.service._generate_match_score_rankings(care_homes)
        assert 'rankings' in result
        assert 'statistics' in result

