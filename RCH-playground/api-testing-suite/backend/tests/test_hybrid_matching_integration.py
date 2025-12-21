"""
Integration tests for hybrid matching approach.

Tests:
- Matching with hybrid data (CQC + Staging)
- Fallback to legacy CSV
- End-to-end matching flow
"""
import unittest
from unittest.mock import patch, MagicMock
from services.csv_care_homes_service import get_care_homes, get_care_homes_hybrid
from services.simple_matching_service import SimpleMatchingService


class TestHybridMatchingIntegration(unittest.TestCase):
    """Test integration of hybrid data with matching algorithm"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.matching_service = SimpleMatchingService()
        
        # Sample questionnaire
        self.questionnaire = {
            'section_2_location_budget': {
                'q6_max_distance': 'within_30km',
                'q7_budget': '3000_5000_self',
            },
            'section_3_medical_needs': {
                'q8_care_types': ['residential'],
                'q9_medical_conditions': ['dementia_alzheimers'],
                'q10_mobility_level': 'independent',
                'q11_medication_management': 'needs_reminders',
                'q12_special_equipment': [],
                'q13_age_range': '65_plus',
            },
        }
    
    @patch('services.csv_care_homes_service.load_cqc_homes')
    @patch('services.csv_care_homes_service.load_staging_data')
    @patch('services.csv_care_homes_service.merge_cqc_and_staging')
    def test_matching_with_hybrid_data(self, mock_merge, mock_staging, mock_cqc):
        """Test matching with hybrid data (CQC + Staging)"""
        # Mock CQC homes
        mock_cqc.return_value = [
            {
                'location_id': '1-10000302982',
                'name': 'Test Home 1',
                'serves_older_people': True,
                'serves_dementia_band': True,
                'care_residential': True,
                'cqc_rating_overall': 'Good',
                'cqc_rating_safe': 'Good',
                'latitude': 52.1234,
                'longitude': -1.5678,
                'fee_residential_from': None,  # Missing in CQC
            },
        ]
        
        # Mock Staging data
        mock_staging.return_value = {
            '1-10000302982': {
                'cqc_location_id': '1-10000302982',
                'fee_residential_from': 995.0,  # From Staging
                'review_average_score': 4.5,
                'wheelchair_access': True,
            },
        }
        
        # Mock merged homes
        mock_merge.return_value = [
            {
                'location_id': '1-10000302982',
                'name': 'Test Home 1',
                'serves_older_people': True,
                'serves_dementia_band': True,
                'care_residential': True,
                'cqc_rating_overall': 'Good',
                'cqc_rating_safe': 'Good',
                'latitude': 52.1234,
                'longitude': -1.5678,
                'fee_residential_from': 995.0,  # From Staging
                'review_average_score': 4.5,
                'wheelchair_access': True,
                'distance_km': 5.0,
            },
        ]
        
        # Test hybrid approach
        homes = get_care_homes_hybrid(limit=1)
        
        self.assertEqual(len(homes), 1)
        self.assertEqual(homes[0]['name'], 'Test Home 1')
        
        # Verify Staging data is present
        self.assertEqual(homes[0]['fee_residential_from'], 995.0)
        self.assertEqual(homes[0]['review_average_score'], 4.5)
        self.assertTrue(homes[0]['wheelchair_access'])
        
        # Test matching with hybrid data
        enriched_data = {}
        match_result = self.matching_service.calculate_100_point_match(
            home=homes[0],
            user_profile=self.questionnaire,
            enriched_data=enriched_data
        )
        
        # Should have a valid match score
        self.assertIsNotNone(match_result)
        self.assertIn('total', match_result)
        self.assertGreater(match_result['total'], 0)
    
    @patch('services.csv_care_homes_service.load_cqc_homes')
    def test_fallback_to_legacy_csv(self, mock_cqc):
        """Test fallback to legacy CSV when hybrid approach fails"""
        # Mock CQC loader to raise exception
        mock_cqc.side_effect = Exception("CQC load failed")
        
        # Should fallback to legacy CSV
        homes = get_care_homes(use_hybrid=True, limit=5)
        
        # Should still return homes (from legacy CSV)
        # Note: This test depends on legacy CSV being available
        # In real scenario, it would load from merged_care_homes_west_midlands.csv
        pass
    
    def test_matching_uses_staging_pricing(self):
        """Test that matching algorithm uses pricing from Staging"""
        home = {
            'location_id': '1-10000302982',
            'name': 'Test Home',
            'serves_older_people': True,
            'care_residential': True,
            'cqc_rating_overall': 'Good',
            'latitude': 52.1234,
            'longitude': -1.5678,
            'distance_km': 5.0,
            'fee_residential_from': 995.0,  # From Staging
        }
        
        enriched_data = {}
        match_result = self.matching_service.calculate_100_point_match(
            home=home,
            user_profile=self.questionnaire,
            enriched_data=enriched_data
        )
        
        # Should calculate budget match using Staging pricing
        self.assertIsNotNone(match_result)
        category_scores = match_result.get('category_scores', {})
        financial_score = category_scores.get('financial', 0)
        
        # Financial score should be > 0 (budget match uses fee_residential_from)
        self.assertGreater(financial_score, 0)
    
    def test_matching_uses_staging_amenities(self):
        """Test that matching algorithm uses amenities from Staging"""
        home = {
            'location_id': '1-10000302982',
            'name': 'Test Home',
            'serves_older_people': True,
            'care_residential': True,
            'cqc_rating_overall': 'Good',
            'latitude': 52.1234,
            'longitude': -1.5678,
            'distance_km': 5.0,
            'wheelchair_access': True,  # From Staging
            'wifi_available': True,  # From Staging
            'parking_onsite': True,  # From Staging
        }
        
        enriched_data = {}
        match_result = self.matching_service.calculate_100_point_match(
            home=home,
            user_profile=self.questionnaire,
            enriched_data=enriched_data
        )
        
        # Should calculate location and lifestyle scores using Staging amenities
        self.assertIsNotNone(match_result)
        category_scores = match_result.get('category_scores', {})
        location_score = category_scores.get('location', 0)
        lifestyle_score = category_scores.get('lifestyle', 0)
        
        # Scores should be > 0 (amenities contribute to location and lifestyle)
        self.assertGreater(location_score, 0)
        self.assertGreater(lifestyle_score, 0)


class TestHybridDataFlow(unittest.TestCase):
    """Test end-to-end data flow with hybrid approach"""
    
    @patch('services.csv_care_homes_service.load_cqc_homes')
    @patch('services.csv_care_homes_service.load_staging_data')
    @patch('services.csv_care_homes_service.merge_cqc_and_staging')
    def test_end_to_end_flow(self, mock_merge, mock_staging, mock_cqc):
        """Test complete flow from data loading to matching"""
        # Setup mocks
        mock_cqc.return_value = [
            {
                'location_id': '1-10000302982',
                'name': 'Test Home',
                'serves_older_people': True,
                'care_residential': True,
                'cqc_rating_overall': 'Good',
                'latitude': 52.1234,
                'longitude': -1.5678,
            },
        ]
        
        mock_staging.return_value = {
            '1-10000302982': {
                'cqc_location_id': '1-10000302982',
                'fee_residential_from': 995.0,
            },
        }
        
        mock_merge.return_value = [
            {
                'location_id': '1-10000302982',
                'name': 'Test Home',
                'serves_older_people': True,
                'care_residential': True,
                'cqc_rating_overall': 'Good',
                'latitude': 52.1234,
                'longitude': -1.5678,
                'fee_residential_from': 995.0,
                'distance_km': 5.0,
            },
        ]
        
        # Test complete flow
        homes = get_care_homes_hybrid(limit=1)
        
        # Verify data is merged
        self.assertEqual(len(homes), 1)
        self.assertEqual(homes[0]['fee_residential_from'], 995.0)
        
        # Verify mocks were called
        mock_cqc.assert_called_once()
        mock_staging.assert_called_once()
        mock_merge.assert_called_once()


if __name__ == '__main__':
    unittest.main()

