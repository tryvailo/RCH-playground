"""
Unit tests for safe float conversion functions

This test suite covers the bug where string values like "Waived fees or 2"
could not be converted to float, causing report generation to fail.

Bug History:
- This error occurred before and was fixed
- The error reoccurred, indicating the fix was not comprehensive enough
- This test ensures the fix is properly tested and prevents regression
"""
import pytest
from services.negotiation_strategy_service import _safe_float_convert as negotiation_safe_float
from services.comparative_analysis_service import _safe_float_convert as comparative_safe_float
import re


def safe_float_convert_main(value):
    """Replicate the function from main.py for testing"""
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except (ValueError, TypeError):
            match = re.search(r'(\d+\.?\d*)', value)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, TypeError):
                    pass
    return 0


class TestSafeFloatConversion:
    """Test suite for safe float conversion functions"""
    
    def test_none_value(self):
        """Test handling of None values"""
        assert negotiation_safe_float(None) is None
        assert comparative_safe_float(None) == 0.0
        assert safe_float_convert_main(None) == 0
    
    def test_integer_values(self):
        """Test handling of integer values"""
        assert negotiation_safe_float(42) == 42.0
        assert comparative_safe_float(42) == 42.0
        assert safe_float_convert_main(42) == 42.0
    
    def test_float_values(self):
        """Test handling of float values"""
        assert negotiation_safe_float(42.5) == 42.5
        assert comparative_safe_float(42.5) == 42.5
        assert safe_float_convert_main(42.5) == 42.5
    
    def test_simple_string_numbers(self):
        """Test conversion of simple numeric strings"""
        assert negotiation_safe_float("42") == 42.0
        assert comparative_safe_float("42") == 42.0
        assert safe_float_convert_main("42") == 42.0
        
        assert negotiation_safe_float("42.5") == 42.5
        assert comparative_safe_float("42.5") == 42.5
        assert safe_float_convert_main("42.5") == 42.5
    
    def test_string_with_whitespace(self):
        """Test conversion of strings with whitespace"""
        assert negotiation_safe_float("  42  ") == 42.0
        assert comparative_safe_float("  42  ") == 42.0
        assert safe_float_convert_main("  42  ") == 42.0
    
    def test_currency_format(self):
        """Test conversion of currency-formatted strings"""
        assert negotiation_safe_float("£42") == 42.0
        assert comparative_safe_float("£42") == 42.0
        assert safe_float_convert_main("£42") == 42.0
        
        assert negotiation_safe_float("£42.50") == 42.5
        assert comparative_safe_float("£42.50") == 42.5
        assert safe_float_convert_main("£42.50") == 42.5
    
    def test_percentage_format(self):
        """Test conversion of percentage-formatted strings"""
        assert negotiation_safe_float("42%") == 42.0
        assert comparative_safe_float("42%") == 42.0
        assert safe_float_convert_main("42%") == 42.0
        
        assert negotiation_safe_float("42.5%") == 42.5
        assert comparative_safe_float("42.5%") == 42.5
        assert safe_float_convert_main("42.5%") == 42.5
    
    def test_text_with_numbers(self):
        """Test extraction of numbers from descriptive text (THE BUG)"""
        # This is the specific case that caused the error
        assert negotiation_safe_float("Waived fees or 2") == 2.0
        assert comparative_safe_float("Waived fees or 2") == 2.0
        assert safe_float_convert_main("Waived fees or 2") == 2.0
        
        # More test cases
        assert negotiation_safe_float("Price is 42.5 per week") == 42.5
        assert comparative_safe_float("Price is 42.5 per week") == 42.5
        assert safe_float_convert_main("Price is 42.5 per week") == 42.5
        
        assert negotiation_safe_float("Starting from £850") == 850.0
        assert comparative_safe_float("Starting from £850") == 850.0
        assert safe_float_convert_main("Starting from £850") == 850.0
    
    def test_range_format(self):
        """Test extraction of first number from range format"""
        assert negotiation_safe_float("2-3") == 2.0
        assert comparative_safe_float("2-3") == 2.0
        assert safe_float_convert_main("2-3") == 2.0
        
        assert negotiation_safe_float("42.5-50") == 42.5
        assert comparative_safe_float("42.5-50") == 42.5
        assert safe_float_convert_main("42.5-50") == 42.5
    
    def test_invalid_strings(self):
        """Test handling of strings without numbers"""
        assert negotiation_safe_float("no numbers here") is None
        assert comparative_safe_float("no numbers here") == 0.0
        assert safe_float_convert_main("no numbers here") == 0
        
        assert negotiation_safe_float("") is None
        assert comparative_safe_float("") == 0.0
        assert safe_float_convert_main("") == 0
    
    def test_empty_string(self):
        """Test handling of empty strings"""
        assert negotiation_safe_float("   ") is None
        assert comparative_safe_float("   ") == 0.0
        assert safe_float_convert_main("   ") == 0
    
    def test_real_world_cases(self):
        """Test real-world cases that might occur in care home data"""
        test_cases = [
            ("Waived fees or 2", 2.0),
            ("2-3% discount", 2.0),
            ("£850 per week", 850.0),
            ("Starting from 750", 750.0),
            ("Price: 950", 950.0),
            ("42.5", 42.5),
            ("Call for pricing", None),  # negotiation returns None, others return 0
            ("TBD", None),
            ("N/A", None),
        ]
        
        for input_value, expected in test_cases:
            if expected is None:
                assert negotiation_safe_float(input_value) is None
                assert comparative_safe_float(input_value) == 0.0
                assert safe_float_convert_main(input_value) == 0
            else:
                assert negotiation_safe_float(input_value) == expected
                assert comparative_safe_float(input_value) == expected
                assert safe_float_convert_main(input_value) == expected


class TestPriceProcessingInServices:
    """Test that services handle price conversion correctly"""
    
    def test_negotiation_strategy_price_extraction(self):
        """Test price extraction in negotiation strategy service"""
        from services.negotiation_strategy_service import _safe_float_convert
        
        # Simulate care home data with problematic price formats
        care_homes = [
            {'weeklyPrice': 'Waived fees or 2'},
            {'weeklyPrice': '£850'},
            {'weeklyPrice': 750},
            {'weeklyPrice': '950.5'},
            {'weeklyPrice': None},
        ]
        
        prices = []
        for home in care_homes:
            price = home.get('weeklyPrice')
            price_float = _safe_float_convert(price)
            if price_float and price_float > 0:
                prices.append(price_float)
        
        # Should extract: 2.0, 850.0, 750.0, 950.5 (None is skipped)
        assert len(prices) == 4
        assert 2.0 in prices
        assert 850.0 in prices
        assert 750.0 in prices
        assert 950.5 in prices
    
    def test_comparative_analysis_price_formatting(self):
        """Test price formatting in comparative analysis service"""
        from services.comparative_analysis_service import _safe_float_convert
        
        # Simulate care home data with problematic price formats
        homes = [
            {'weeklyPrice': 'Waived fees or 2'},
            {'weeklyPrice': '£850'},
            {'weeklyPrice': 750},
        ]
        
        for home in homes:
            price = home.get('weeklyPrice', 0)
            price_float = _safe_float_convert(price)
            # Should format without error
            formatted = f"£{price_float:,.0f}"
            assert formatted.startswith('£')
            assert price_float >= 0


class TestNoneTypeComparisonBug:
    """Test suite for NoneType comparison bug"""
    
    def test_price_comparison_with_none(self):
        """Test that price comparisons handle None values correctly"""
        from services.negotiation_strategy_service import _safe_float_convert
        
        # Simulate care home with None price
        home = {'weeklyPrice': None, 'matchScore': 85}
        price = home.get('weeklyPrice')
        price_float = _safe_float_convert(price)
        
        # Should not raise error when comparing
        assert price_float is None or price_float >= 0
        if price_float and price_float > 0:
            # This should not raise TypeError
            assert isinstance(price_float, (int, float))
    
    def test_funding_calculations_with_none(self):
        """Test that funding calculations handle None values correctly"""
        from services.funding_optimization_service import FundingOptimizationService
        
        service = FundingOptimizationService()
        
        # Test with None values
        questionnaire = {
            'section_2_location_budget': {'q7_budget': '3000_5000_self'},
            'section_3_medical_needs': {'q9_medical_conditions': ['diabetes']}
        }
        
        # Should not raise TypeError when None values are passed
        try:
            la_funding = service.calculate_la_funding_availability(
                questionnaire=questionnaire,
                estimated_assets=None,
                estimated_income=None
            )
            # Should have default values
            assert 'funding_available' in la_funding
            assert isinstance(la_funding.get('funding_available'), bool)
        except TypeError as e:
            pytest.fail(f"TypeError raised with None values: {e}")
    
    def test_dpa_calculations_with_none(self):
        """Test that DPA calculations handle None values correctly"""
        from services.funding_optimization_service import FundingOptimizationService
        
        service = FundingOptimizationService()
        
        questionnaire = {
            'section_2_location_budget': {'q7_budget': '3000_5000_self'}
        }
        
        # Should not raise TypeError when None values are passed
        try:
            dpa = service.calculate_dpa_considerations(
                questionnaire=questionnaire,
                property_value=None,
                outstanding_mortgage=None
            )
            # Should have default values
            assert 'dpa_eligible' in dpa
            assert isinstance(dpa.get('dpa_eligible'), bool)
        except TypeError as e:
            pytest.fail(f"TypeError raised with None values: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

