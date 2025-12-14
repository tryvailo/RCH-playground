"""
Unit tests for MatchingService 50-point scoring algorithm
"""
import pytest
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent.parent.parent
src_path = project_root / "src" / "free_report_viewer"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from services.matching_service import MatchingService

# Try to import MatchingInputs
models_path = Path(__file__).parent.parent / "models"
if str(models_path) not in sys.path:
    sys.path.insert(0, str(models_path))

try:
    from matching_models import MatchingInputs, MatchingScore
except ImportError:
    # Fallback class
    class MatchingInputs:
        def __init__(self, postcode, budget=None, care_type=None, user_lat=None, user_lon=None, max_distance_miles=None):
            self.postcode = postcode
            self.budget = budget
            self.care_type = care_type
            self.user_lat = user_lat
            self.user_lon = user_lon
            self.max_distance_miles = max_distance_miles


class TestLocationScoring:
    """Tests for location scoring (20 points)"""
    
    def test_score_location_within_5_miles(self):
        """Test location score for ≤5 miles"""
        service = MatchingService()
        # Same location (0 miles)
        score = service.score_location(52.4862, -1.8904, 52.4862, -1.8904)
        assert score == 20
    
    def test_score_location_within_10_miles(self):
        """Test location score for ≤10 miles"""
        service = MatchingService()
        # ~8 miles distance
        score = service.score_location(52.4862, -1.8904, 52.5000, -1.9000)
        assert score == 15
    
    def test_score_location_within_15_miles(self):
        """Test location score for ≤15 miles"""
        service = MatchingService()
        # ~12 miles distance
        score = service.score_location(52.4862, -1.8904, 52.5500, -1.9500)
        assert score == 10
    
    def test_score_location_over_15_miles(self):
        """Test location score for >15 miles"""
        service = MatchingService()
        # ~20 miles distance
        score = service.score_location(52.4862, -1.8904, 52.6000, -2.0000)
        assert score == 5
    
    def test_score_location_missing_coordinates(self):
        """Test location score with missing coordinates"""
        service = MatchingService()
        score = service.score_location(None, None, 52.4862, -1.8904)
        assert score == 5  # Default score


class TestCQCRatingScoring:
    """Tests for CQC rating scoring (25 points)"""
    
    def test_score_cqc_outstanding(self):
        """Test CQC score for Outstanding"""
        service = MatchingService()
        assert service.score_cqc_rating("Outstanding") == 25
    
    def test_score_cqc_good(self):
        """Test CQC score for Good"""
        service = MatchingService()
        assert service.score_cqc_rating("Good") == 20
    
    def test_score_cqc_requires_improvement(self):
        """Test CQC score for Requires Improvement"""
        service = MatchingService()
        assert service.score_cqc_rating("Requires Improvement") == 10
        assert service.score_cqc_rating("Requires improvement") == 10  # Case variation
    
    def test_score_cqc_inadequate(self):
        """Test CQC score for Inadequate"""
        service = MatchingService()
        assert service.score_cqc_rating("Inadequate") == 0
    
    def test_score_cqc_none(self):
        """Test CQC score for None/missing"""
        service = MatchingService()
        assert service.score_cqc_rating(None) == 0
        assert service.score_cqc_rating("Unknown") == 0


class TestBudgetMatchScoring:
    """Tests for budget match scoring (20 points)"""
    
    def test_score_budget_within_budget(self):
        """Test budget score when price is within budget"""
        service = MatchingService()
        assert service.score_budget_match(950, 1000, "residential") == 20
    
    def test_score_budget_exact_match(self):
        """Test budget score when price equals budget"""
        service = MatchingService()
        assert service.score_budget_match(1000, 1000, "residential") == 20
    
    def test_score_budget_50_over(self):
        """Test budget score when price is +£50 over budget"""
        service = MatchingService()
        assert service.score_budget_match(1050, 1000, "residential") == 20
    
    def test_score_budget_75_over(self):
        """Test budget score when price is +£75 over budget"""
        service = MatchingService()
        assert service.score_budget_match(1075, 1000, "residential") == 15
    
    def test_score_budget_150_over(self):
        """Test budget score when price is +£150 over budget"""
        service = MatchingService()
        assert service.score_budget_match(1150, 1000, "residential") == 10
    
    def test_score_budget_250_over(self):
        """Test budget score when price is +£250 over budget"""
        service = MatchingService()
        assert service.score_budget_match(1250, 1000, "residential") == 0
    
    def test_score_budget_no_budget(self):
        """Test budget score when no budget specified"""
        service = MatchingService()
        assert service.score_budget_match(1000, None, "residential") == 10  # Neutral


class TestCareTypeMatchScoring:
    """Tests for care type match scoring (15 points)"""
    
    def test_score_care_type_perfect_match(self):
        """Test care type score for perfect match"""
        service = MatchingService()
        assert service.score_care_type_match("residential", ["residential"]) == 15
        assert service.score_care_type_match("nursing", ["nursing"]) == 15
        assert service.score_care_type_match("dementia", ["dementia"]) == 15
    
    def test_score_care_type_close_match(self):
        """Test care type score for close match"""
        service = MatchingService()
        # Residential -> Residential Dementia
        assert service.score_care_type_match("residential", ["residential_dementia"]) == 10
        # Nursing -> Nursing Dementia
        assert service.score_care_type_match("nursing", ["nursing_dementia"]) == 10
        # Dementia -> Residential Dementia
        assert service.score_care_type_match("dementia", ["residential_dementia"]) == 10
    
    def test_score_care_type_general_match(self):
        """Test care type score for general match"""
        service = MatchingService()
        assert service.score_care_type_match("residential", ["nursing"]) == 5
        assert service.score_care_type_match("nursing", ["residential"]) == 5
    
    def test_score_care_type_no_match(self):
        """Test care type score when no care types available"""
        service = MatchingService()
        assert service.score_care_type_match("residential", []) == 5  # General match
    
    def test_score_care_type_no_user_type(self):
        """Test care type score when user type not specified"""
        service = MatchingService()
        assert service.score_care_type_match(None, ["residential"]) == 5  # General match


class TestAvailabilityScoring:
    """Tests for availability scoring (10 points)"""
    
    def test_score_availability_beds_available(self):
        """Test availability score when beds are available"""
        service = MatchingService()
        assert service.score_availability(5, None, None) == 10
        assert service.score_availability(1, None, None) == 10
    
    def test_score_availability_status_available(self):
        """Test availability score with status 'Available'"""
        service = MatchingService()
        assert service.score_availability(None, "Available", None) == 10
        assert service.score_availability(None, "available", None) == 10  # Case insensitive
    
    def test_score_availability_status_limited(self):
        """Test availability score with status 'Limited availability'"""
        service = MatchingService()
        assert service.score_availability(None, "Limited availability", None) == 5
        assert service.score_availability(None, "Limited", None) == 5
    
    def test_score_availability_status_waiting(self):
        """Test availability score with status 'Waiting list'"""
        service = MatchingService()
        assert service.score_availability(None, "Waiting list", None) == 5
    
    def test_score_availability_status_full(self):
        """Test availability score with status 'Full'"""
        service = MatchingService()
        assert service.score_availability(None, "Full", None) == 0
        assert service.score_availability(None, "full", None) == 0
    
    def test_score_availability_has_availability_true(self):
        """Test availability score with has_availability=True"""
        service = MatchingService()
        assert service.score_availability(None, None, True) == 10
    
    def test_score_availability_has_availability_false(self):
        """Test availability score with has_availability=False"""
        service = MatchingService()
        assert service.score_availability(None, None, False) == 0
    
    def test_score_availability_no_data(self):
        """Test availability score with no data"""
        service = MatchingService()
        assert service.score_availability(None, None, None) == 0


class TestGoogleReviewsScoring:
    """Tests for Google reviews scoring (10 points)"""
    
    def test_score_google_reviews_high_rating(self):
        """Test Google reviews score for ≥4.5 rating"""
        service = MatchingService()
        assert service.score_google_reviews(4.5, 10) == 10
        assert service.score_google_reviews(4.8, 5) == 10
    
    def test_score_google_reviews_good_rating_many_reviews(self):
        """Test Google reviews score for ≥4.0 rating with ≥20 reviews"""
        service = MatchingService()
        assert service.score_google_reviews(4.0, 25) == 7
        assert service.score_google_reviews(4.2, 50) == 7
    
    def test_score_google_reviews_good_rating_few_reviews(self):
        """Test Google reviews score for ≥4.0 rating with <20 reviews"""
        service = MatchingService()
        assert service.score_google_reviews(4.0, 10) == 5
        assert service.score_google_reviews(4.1, 15) == 5
    
    def test_score_google_reviews_medium_rating_many_reviews(self):
        """Test Google reviews score for ≥3.5 rating with ≥10 reviews"""
        service = MatchingService()
        assert service.score_google_reviews(3.5, 15) == 4
        assert service.score_google_reviews(3.8, 20) == 4
    
    def test_score_google_reviews_medium_rating_few_reviews(self):
        """Test Google reviews score for ≥3.5 rating with <10 reviews"""
        service = MatchingService()
        assert service.score_google_reviews(3.5, 5) == 2
        assert service.score_google_reviews(3.7, 8) == 2
    
    def test_score_google_reviews_low_rating(self):
        """Test Google reviews score for <3.5 rating"""
        service = MatchingService()
        assert service.score_google_reviews(3.0, 50) == 0
        assert service.score_google_reviews(2.5, 100) == 0
    
    def test_score_google_reviews_no_rating(self):
        """Test Google reviews score when no rating"""
        service = MatchingService()
        assert service.score_google_reviews(None, 10) == 0
        assert service.score_google_reviews(None, None) == 0


class TestCalculate50PointScore:
    """Tests for full 50-point score calculation"""
    
    def test_calculate_full_score_perfect_match(self):
        """Test full score calculation for perfect match"""
        service = MatchingService()
        user_inputs = MatchingInputs(
            postcode="B44 8DD",
            budget=1000,
            care_type="residential",
            user_lat=52.533398,
            user_lon=-1.8904
        )
        
        home = {
            'name': 'Perfect Match Home',
            'latitude': 52.533398,
            'longitude': -1.8904,
            'rating': 'Outstanding',
            'weekly_cost': 950,
            'care_types': ['residential'],
            'beds_available': 5,
            'google_rating': 4.8,
            'review_count': 50
        }
        
        score = service.calculate_50_point_score(home, user_inputs)
        
        assert score.location_score == 20  # Same location
        assert score.cqc_score == 25  # Outstanding
        assert score.budget_score == 20  # Within budget
        assert score.care_type_score == 15  # Perfect match
        assert score.availability_score == 10  # Beds available
        assert score.google_reviews_score == 10  # ≥4.5 rating
        assert score.total_score == 100  # Perfect score
    
    def test_calculate_full_score_average_match(self):
        """Test full score calculation for average match"""
        service = MatchingService()
        user_inputs = MatchingInputs(
            postcode="B44 8DD",
            budget=1000,
            care_type="residential",
            user_lat=52.533398,
            user_lon=-1.8904
        )
        
        home = {
            'name': 'Average Match Home',
            'latitude': 52.5500,  # ~12 miles away
            'longitude': -1.9500,
            'rating': 'Good',
            'weekly_cost': 1100,  # +£100 over budget
            'care_types': ['residential'],
            'beds_available': 0,
            'availability_status': 'Limited availability',
            'google_rating': 4.0,
            'review_count': 15
        }
        
        score = service.calculate_50_point_score(home, user_inputs)
        
        assert score.location_score == 10  # ~12 miles
        assert score.cqc_score == 20  # Good
        assert score.budget_score == 15  # +£100 over
        assert score.care_type_score == 15  # Perfect match
        assert score.availability_score == 5  # Limited availability
        assert score.google_reviews_score == 5  # 4.0 with <20 reviews
        assert score.total_score == 70  # Total score


class TestSelect3StrategicHomes:
    """Integration tests for select_3_strategic_homes"""
    
    def test_select_3_homes_basic(self):
        """Test basic selection of 3 strategic homes"""
        service = MatchingService()
        user_inputs = MatchingInputs(
            postcode="B44 8DD",
            budget=1000,
            care_type="residential",
            user_lat=52.533398,
            user_lon=-1.8904
        )
        
        candidates = [
            {
                'name': 'Safe Bet Home',
                'location_id': '1',
                'latitude': 52.5350,
                'longitude': -1.8920,
                'rating': 'Outstanding',
                'weekly_cost': 1000,
                'care_types': ['residential'],
                'beds_available': 5,
                'google_rating': 4.0,
                'review_count': 20
            },
            {
                'name': 'Best Reputation Home',
                'location_id': '2',
                'latitude': 52.5400,
                'longitude': -1.9000,
                'rating': 'Good',
                'weekly_cost': 1100,
                'care_types': ['residential'],
                'beds_available': 3,
                'google_rating': 4.8,
                'review_count': 150
            },
            {
                'name': 'Smart Value Home',
                'location_id': '3',
                'latitude': 52.5500,
                'longitude': -1.9100,
                'rating': 'Good',
                'weekly_cost': 800,
                'care_types': ['residential'],
                'beds_available': 2,
                'google_rating': 4.2,
                'review_count': 45
            }
        ]
        
        result = service.select_3_strategic_homes(candidates, user_inputs)
        
        assert len(result) == 3
        assert 'safe_bet' in result
        assert 'best_reputation' in result
        assert 'smart_value' in result
        
        # Check that Safe Bet has highest CQC
        assert result['safe_bet']['rating'] == 'Outstanding'
        
        # Check that Best Reputation has highest Google rating
        assert result['best_reputation']['google_rating'] == 4.8
    
    def test_select_3_homes_with_duplicates(self):
        """Test selection handles duplicates correctly"""
        service = MatchingService()
        user_inputs = MatchingInputs(
            postcode="B44 8DD",
            budget=1000,
            care_type="residential",
            user_lat=52.533398,
            user_lon=-1.8904
        )
        
        # Same home appears multiple times
        same_home = {
            'name': 'Same Home',
            'location_id': '1',
            'latitude': 52.5350,
            'longitude': -1.8920,
            'rating': 'Outstanding',
            'weekly_cost': 1000,
            'care_types': ['residential'],
            'beds_available': 5,
            'google_rating': 4.8,
            'review_count': 50
        }
        
        candidates = [same_home, same_home.copy(), same_home.copy()]
        
        result = service.select_3_strategic_homes(candidates, user_inputs)
        
        # Should still return 3 homes (with fallback strategies)
        assert len(result) >= 1
    
    def test_select_3_homes_empty_candidates(self):
        """Test selection with empty candidates"""
        service = MatchingService()
        user_inputs = MatchingInputs(
            postcode="B44 8DD",
            budget=1000,
            care_type="residential"
        )
        
        result = service.select_3_strategic_homes([], user_inputs)
        assert result == {}
    
    def test_select_3_homes_missing_data(self):
        """Test selection with homes missing some data"""
        service = MatchingService()
        user_inputs = MatchingInputs(
            postcode="B44 8DD",
            budget=1000,
            care_type="residential",
            user_lat=52.533398,
            user_lon=-1.8904
        )
        
        candidates = [
            {
                'name': 'Home with Missing Data',
                'location_id': '1',
                'latitude': 52.5350,
                'longitude': -1.8920,
                'rating': 'Good',
                'weekly_cost': 1000,
                'care_types': ['residential']
                # Missing: beds_available, google_rating, etc.
            }
        ]
        
        result = service.select_3_strategic_homes(candidates, user_inputs)
        
        # Should still work with missing data
        assert len(result) >= 1
        assert 'safe_bet' in result or 'best_reputation' in result or 'smart_value' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

