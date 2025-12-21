"""
Unit tests for Staging data loader.

Tests:
- load_staging_data()
- map_staging_to_db_format()
- normalize_boolean()
- safe_parse_float()
- safe_parse_int()
"""
import unittest
from unittest.mock import patch, mock_open
import io
from services.staging_data_loader import (
    load_staging_data,
    map_staging_to_db_format,
    normalize_boolean,
    safe_parse_float,
    safe_parse_int
)


class TestNormalizeBoolean(unittest.TestCase):
    """Test normalize_boolean function"""
    
    def test_true_values(self):
        """Test that TRUE values are normalized correctly"""
        self.assertTrue(normalize_boolean('TRUE'))
        self.assertTrue(normalize_boolean('true'))
        self.assertTrue(normalize_boolean('True'))
        self.assertTrue(normalize_boolean('1'))
        self.assertTrue(normalize_boolean(1))
        self.assertTrue(normalize_boolean(True))
    
    def test_false_values(self):
        """Test that FALSE values are normalized correctly"""
        self.assertFalse(normalize_boolean('FALSE'))
        self.assertFalse(normalize_boolean('false'))
        self.assertFalse(normalize_boolean('False'))
        self.assertFalse(normalize_boolean('0'))
        self.assertFalse(normalize_boolean(0))
        self.assertFalse(normalize_boolean(False))
    
    def test_none_values(self):
        """Test that None/empty values return None"""
        self.assertIsNone(normalize_boolean(None))
        self.assertIsNone(normalize_boolean(''))
        self.assertIsNone(normalize_boolean(' '))


class TestSafeParseFloat(unittest.TestCase):
    """Test safe_parse_float function"""
    
    def test_valid_floats(self):
        """Test parsing valid float values"""
        self.assertEqual(safe_parse_float('123.45'), 123.45)
        self.assertEqual(safe_parse_float('0'), 0.0)
        self.assertEqual(safe_parse_float('-123.45'), -123.45)
        self.assertEqual(safe_parse_float(123.45), 123.45)
    
    def test_invalid_values(self):
        """Test handling of invalid values"""
        self.assertIsNone(safe_parse_float(None))
        self.assertIsNone(safe_parse_float(''))
        self.assertIsNone(safe_parse_float('abc'))
        self.assertIsNone(safe_parse_float('N/A'))


class TestSafeParseInt(unittest.TestCase):
    """Test safe_parse_int function"""
    
    def test_valid_ints(self):
        """Test parsing valid int values"""
        self.assertEqual(safe_parse_int('123'), 123)
        self.assertEqual(safe_parse_int('0'), 0)
        self.assertEqual(safe_parse_int('-123'), -123)
        self.assertEqual(safe_parse_int(123), 123)
    
    def test_invalid_values(self):
        """Test handling of invalid values"""
        self.assertIsNone(safe_parse_int(None))
        self.assertIsNone(safe_parse_int(''))
        self.assertIsNone(safe_parse_int('abc'))
        self.assertIsNone(safe_parse_int('N/A'))


class TestMapStagingToDBFormat(unittest.TestCase):
    """Test map_staging_to_db_format function"""
    
    def test_basic_mapping(self):
        """Test basic field mapping"""
        staging_row = {
            'cqc_location_id': '1-10000302982',
            'parsed_fee_residential_from': '995.0',
            'parsed_fee_nursing_from': '1250.0',
            'parsed_fee_dementia_from': '1100.0',
            'parsed_review_average_score': '4.5',
            'parsed_review_count': '25',
            'parsed_wheelchair_access': 'TRUE',
            'parsed_wifi_available': 'FALSE',
            'parsed_parking_onsite': 'TRUE',
            'parsed_beds_total': '30',
            'parsed_accepts_self_funding': 'TRUE',
        }
        
        db_data = map_staging_to_db_format(staging_row)
        
        # Check connection key
        self.assertEqual(db_data['cqc_location_id'], '1-10000302982')
        
        # Check pricing
        self.assertEqual(db_data['fee_residential_from'], 995.0)
        self.assertEqual(db_data['fee_nursing_from'], 1250.0)
        self.assertEqual(db_data['fee_dementia_from'], 1100.0)
        
        # Check reviews
        self.assertEqual(db_data['review_average_score'], 4.5)
        self.assertEqual(db_data['review_count'], 25)
        
        # Check amenities
        self.assertTrue(db_data['wheelchair_access'])
        self.assertFalse(db_data['wifi_available'])
        self.assertTrue(db_data['parking_onsite'])
        
        # Check availability
        self.assertEqual(db_data['beds_total'], 30)
        
        # Check funding
        self.assertTrue(db_data['accepts_self_funding'])
    
    def test_missing_cqc_location_id(self):
        """Test that missing cqc_location_id returns empty dict"""
        staging_row = {
            'parsed_fee_residential_from': '995.0',
        }
        
        db_data = map_staging_to_db_format(staging_row)
        
        self.assertEqual(db_data, {})
    
    def test_dormant_home(self):
        """Test that dormant homes are skipped during loading"""
        # This is tested in load_staging_data, not in map_staging_to_db_format
        # But we can verify that is_dormant is not mapped
        staging_row = {
            'cqc_location_id': '1-10000302982',
            'is_dormant': 'TRUE',
            'parsed_fee_residential_from': '995.0',
        }
        
        db_data = map_staging_to_db_format(staging_row)
        
        # Should still map data (dormant check is in load_staging_data)
        self.assertEqual(db_data['cqc_location_id'], '1-10000302982')
        self.assertEqual(db_data['fee_residential_from'], 995.0)


class TestLoadStagingData(unittest.TestCase):
    """Test load_staging_data function"""
    
    @patch('services.staging_data_loader.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_staging_data_success(self, mock_file, mock_exists):
        """Test successful loading of Staging data"""
        mock_exists.return_value = True
        
        # Create mock CSV data
        csv_data = """cqc_location_id,is_dormant,parsed_fee_residential_from,parsed_review_average_score,parsed_wheelchair_access
1-10000302982,FALSE,995.0,4.5,TRUE
1-10000302983,TRUE,1250.0,4.0,FALSE
1-10000302984,FALSE,1100.0,4.8,TRUE"""
        
        mock_file.return_value = io.StringIO(csv_data)
        
        # Clear cache
        from services.staging_data_loader import _staging_index_cache
        _staging_index_cache = None
        
        staging_index = load_staging_data()
        
        # Should have 2 records (one is dormant)
        self.assertEqual(len(staging_index), 2)
        
        # Check first record
        self.assertIn('1-10000302982', staging_index)
        self.assertEqual(staging_index['1-10000302982']['fee_residential_from'], 995.0)
        self.assertEqual(staging_index['1-10000302982']['review_average_score'], 4.5)
        self.assertTrue(staging_index['1-10000302982']['wheelchair_access'])
        
        # Check second record (not dormant)
        self.assertIn('1-10000302984', staging_index)
        self.assertEqual(staging_index['1-10000302984']['fee_residential_from'], 1100.0)
        
        # Dormant record should not be in index
        self.assertNotIn('1-10000302983', staging_index)
    
    @patch('services.staging_data_loader.Path.exists')
    def test_load_staging_data_file_not_found(self, mock_exists):
        """Test handling of missing CSV file"""
        mock_exists.return_value = False
        
        # Clear cache
        from services.staging_data_loader import _staging_index_cache
        _staging_index_cache = None
        
        staging_index = load_staging_data()
        
        self.assertEqual(len(staging_index), 0)
    
    @patch('services.staging_data_loader.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_staging_data_empty_location_id(self, mock_file, mock_exists):
        """Test that records with empty location_id are skipped"""
        mock_exists.return_value = True
        
        # Create mock CSV data with empty location_id
        csv_data = """cqc_location_id,is_dormant,parsed_fee_residential_from
1-10000302982,FALSE,995.0
,FALSE,1250.0
1-10000302984,FALSE,1100.0"""
        
        mock_file.return_value = io.StringIO(csv_data)
        
        # Clear cache
        from services.staging_data_loader import _staging_index_cache
        _staging_index_cache = None
        
        staging_index = load_staging_data()
        
        # Should have 2 records (one has empty location_id)
        self.assertEqual(len(staging_index), 2)
        self.assertIn('1-10000302982', staging_index)
        self.assertIn('1-10000302984', staging_index)


if __name__ == '__main__':
    unittest.main()

