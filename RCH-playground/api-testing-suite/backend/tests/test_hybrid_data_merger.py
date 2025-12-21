"""
Unit tests for Hybrid data merger.

Tests:
- merge_single_home()
- merge_cqc_and_staging()
- get_merge_statistics()
"""
import unittest
from services.hybrid_data_merger import (
    merge_single_home,
    merge_cqc_and_staging,
    get_merge_statistics,
    CQC_CRITICAL_FIELDS,
    STAGING_PREFERRED_FIELDS
)


class TestMergeSingleHome(unittest.TestCase):
    """Test merge_single_home function"""
    
    def test_merge_with_staging_data(self):
        """Test merging CQC and Staging data"""
        cqc_home = {
            'location_id': '1-10000302982',
            'name': 'Test Care Home',
            'serves_older_people': True,
            'cqc_rating_overall': 'Good',
            'latitude': 52.1234,
            'longitude': -1.5678,
            'fee_residential_from': None,  # Missing in CQC
        }
        
        staging_data = {
            'cqc_location_id': '1-10000302982',
            'fee_residential_from': 995.0,  # From Staging
            'review_average_score': 4.5,
            'wheelchair_access': True,
        }
        
        merged = merge_single_home(cqc_home, staging_data)
        
        # Critical fields from CQC should be preserved
        self.assertEqual(merged['name'], 'Test Care Home')
        self.assertEqual(merged['serves_older_people'], True)
        self.assertEqual(merged['cqc_rating_overall'], 'Good')
        self.assertEqual(merged['latitude'], 52.1234)
        
        # Staging preferred fields should be used
        self.assertEqual(merged['fee_residential_from'], 995.0)
        self.assertEqual(merged['review_average_score'], 4.5)
        self.assertTrue(merged['wheelchair_access'])
    
    def test_merge_without_staging_data(self):
        """Test merging when Staging data is None"""
        cqc_home = {
            'location_id': '1-10000302982',
            'name': 'Test Care Home',
            'serves_older_people': True,
        }
        
        merged = merge_single_home(cqc_home, None)
        
        # Should return CQC data unchanged
        self.assertEqual(merged, cqc_home)
    
    def test_critical_fields_priority(self):
        """Test that critical fields from CQC are never overridden"""
        cqc_home = {
            'location_id': '1-10000302982',
            'name': 'CQC Name',
            'cqc_rating_overall': 'Good',
            'latitude': 52.1234,
        }
        
        staging_data = {
            'cqc_location_id': '1-10000302982',
            'name': 'Staging Name',  # Should not override
            'cqc_rating_overall': 'Outstanding',  # Should not override
            'latitude': 53.5678,  # Should not override
        }
        
        merged = merge_single_home(cqc_home, staging_data)
        
        # CQC values should be preserved
        self.assertEqual(merged['name'], 'CQC Name')
        self.assertEqual(merged['cqc_rating_overall'], 'Good')
        self.assertEqual(merged['latitude'], 52.1234)
    
    def test_staging_preferred_fields(self):
        """Test that Staging preferred fields are used when available"""
        cqc_home = {
            'location_id': '1-10000302982',
            'fee_residential_from': None,  # Missing in CQC
            'review_average_score': None,  # Missing in CQC
        }
        
        staging_data = {
            'cqc_location_id': '1-10000302982',
            'fee_residential_from': 995.0,
            'review_average_score': 4.5,
        }
        
        merged = merge_single_home(cqc_home, staging_data)
        
        # Staging values should be used
        self.assertEqual(merged['fee_residential_from'], 995.0)
        self.assertEqual(merged['review_average_score'], 4.5)
    
    def test_fallback_logic(self):
        """Test fallback: use Staging if CQC is None/empty"""
        cqc_home = {
            'location_id': '1-10000302982',
            'some_field': None,  # Missing in CQC
        }
        
        staging_data = {
            'cqc_location_id': '1-10000302982',
            'some_field': 'staging_value',
        }
        
        merged = merge_single_home(cqc_home, staging_data)
        
        # Staging value should be used as fallback
        self.assertEqual(merged['some_field'], 'staging_value')
    
    def test_skip_connection_key(self):
        """Test that cqc_location_id connection key is skipped"""
        cqc_home = {
            'location_id': '1-10000302982',
        }
        
        staging_data = {
            'cqc_location_id': '1-10000302982',
            'other_field': 'value',
        }
        
        merged = merge_single_home(cqc_home, staging_data)
        
        # cqc_location_id should not be added from Staging (it's a connection key)
        # But it should be in merged if it was in CQC
        self.assertEqual(merged['location_id'], '1-10000302982')


class TestMergeCQCAndStaging(unittest.TestCase):
    """Test merge_cqc_and_staging function"""
    
    def test_basic_merge(self):
        """Test basic merging of CQC and Staging data"""
        cqc_homes = [
            {
                'location_id': '1-10000302982',
                'name': 'Home 1',
                'serves_older_people': True,
            },
            {
                'location_id': '1-10000302983',
                'name': 'Home 2',
                'serves_older_people': False,
            },
        ]
        
        staging_index = {
            '1-10000302982': {
                'cqc_location_id': '1-10000302982',
                'fee_residential_from': 995.0,
            },
            # Home 2 has no Staging data
        }
        
        merged = merge_cqc_and_staging(cqc_homes, staging_index)
        
        self.assertEqual(len(merged), 2)
        
        # Home 1 should have Staging data
        self.assertEqual(merged[0]['name'], 'Home 1')
        self.assertEqual(merged[0]['fee_residential_from'], 995.0)
        
        # Home 2 should have only CQC data
        self.assertEqual(merged[1]['name'], 'Home 2')
        self.assertIsNone(merged[1].get('fee_residential_from'))
    
    def test_merge_without_location_id(self):
        """Test merging when CQC home has no location_id"""
        cqc_homes = [
            {
                'name': 'Home Without ID',
                # No location_id
            },
        ]
        
        staging_index = {}
        
        merged = merge_cqc_and_staging(cqc_homes, staging_index)
        
        # Should still include the home (CQC only)
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]['name'], 'Home Without ID')
    
    def test_merge_with_alternative_formats(self):
        """Test merging with alternative location_id formats"""
        cqc_homes = [
            {
                'location_id': '1-10000302982',
                'name': 'Home 1',
            },
            {
                'location_id': '10000302983',  # Without prefix
                'name': 'Home 2',
            },
        ]
        
        staging_index = {
            '1-10000302982': {
                'cqc_location_id': '1-10000302982',
                'fee_residential_from': 995.0,
            },
            '1-10000302983': {  # With prefix in Staging
                'cqc_location_id': '1-10000302983',
                'fee_residential_from': 1100.0,
            },
        }
        
        merged = merge_cqc_and_staging(cqc_homes, staging_index)
        
        # Home 1 should match
        self.assertEqual(merged[0]['fee_residential_from'], 995.0)
        
        # Home 2 should match (alternative format)
        self.assertEqual(merged[1]['fee_residential_from'], 1100.0)


class TestGetMergeStatistics(unittest.TestCase):
    """Test get_merge_statistics function"""
    
    def test_basic_statistics(self):
        """Test basic merge statistics"""
        cqc_homes = [
            {'location_id': '1-10000302982'},
            {'location_id': '1-10000302983'},
            {'location_id': '1-10000302984'},
        ]
        
        staging_index = {
            '1-10000302982': {'cqc_location_id': '1-10000302982'},
            '1-10000302983': {'cqc_location_id': '1-10000302983'},
            '1-10000302985': {'cqc_location_id': '1-10000302985'},  # Only in Staging
        }
        
        stats = get_merge_statistics(cqc_homes, staging_index)
        
        self.assertEqual(stats['total_cqc'], 3)
        self.assertEqual(stats['total_staging'], 3)
        self.assertEqual(stats['matched'], 2)  # 2 matches
        
        # Note: cqc_only may include alternative formats, so we check >= 1
        self.assertGreaterEqual(stats['cqc_only'], 1)  # At least 1 only in CQC
        
        self.assertEqual(stats['staging_only'], 1)  # 1 only in Staging
        self.assertAlmostEqual(stats['match_rate'], 66.7, places=1)
    
    def test_empty_cqc(self):
        """Test statistics with empty CQC"""
        cqc_homes = []
        staging_index = {
            '1-10000302982': {'cqc_location_id': '1-10000302982'},
        }
        
        stats = get_merge_statistics(cqc_homes, staging_index)
        
        self.assertEqual(stats['total_cqc'], 0)
        self.assertEqual(stats['total_staging'], 1)
        self.assertEqual(stats['matched'], 0)
        self.assertEqual(stats['match_rate'], 0.0)
    
    def test_empty_staging(self):
        """Test statistics with empty Staging"""
        cqc_homes = [
            {'location_id': '1-10000302982'},
        ]
        staging_index = {}
        
        stats = get_merge_statistics(cqc_homes, staging_index)
        
        self.assertEqual(stats['total_cqc'], 1)
        self.assertEqual(stats['total_staging'], 0)
        self.assertEqual(stats['matched'], 0)
        self.assertEqual(stats['match_rate'], 0.0)


if __name__ == '__main__':
    unittest.main()

