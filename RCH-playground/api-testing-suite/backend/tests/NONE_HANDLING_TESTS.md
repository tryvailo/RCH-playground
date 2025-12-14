# None Value Handling Tests

This document describes the unit tests created to prevent regression of None value handling errors.

## Overview

These tests cover all the fixes for `TypeError: '>' not supported between instances of 'NoneType' and 'int'` and `TypeError: Cannot read properties of null (reading 'replace')` errors that were fixed across multiple services and components.

## Backend Tests

### test_negotiation_strategy_none_handling.py

**Purpose**: Tests None value handling in `NegotiationStrategyService._identify_priority_questions()`

**Coverage**:
- `turnover_rate_percent` None handling
- `bankruptcy_risk_score` None handling
- String to float conversion for these values
- Missing `staffQuality` and `financialStability` objects
- Empty care homes list

**Key Test Cases**:
- `test_identify_priority_questions_with_none_turnover_rate`: Tests None `turnover_rate_percent`
- `test_identify_priority_questions_with_none_bankruptcy_risk`: Tests None `bankruptcy_risk_score`
- `test_identify_priority_questions_with_string_turnover_rate`: Tests string `turnover_rate_percent`
- `test_identify_priority_questions_with_string_bankruptcy_risk`: Tests string `bankruptcy_risk_score`
- `test_identify_priority_questions_with_high_turnover_rate`: Tests high turnover rate detection
- `test_identify_priority_questions_with_high_bankruptcy_risk`: Tests high bankruptcy risk detection
- `test_identify_priority_questions_with_missing_staff_quality`: Tests missing `staffQuality`
- `test_identify_priority_questions_with_missing_financial_stability`: Tests missing `financialStability`
- `test_identify_priority_questions_with_empty_care_homes`: Tests empty list handling

### test_comparative_analysis_none_handling.py

**Purpose**: Tests None value handling in `ComparativeAnalysisService`

**Coverage**:
- None `weeklyPrice` values
- None `matchScore` values
- None `altman_z_score` values
- None `top_score`, `score_range`, `price_range` values
- None price parameters in `_calculate_value_score()`

**Key Test Cases**:
- `test_generate_comparative_analysis_with_none_weekly_price`: Tests None `weeklyPrice`
- `test_generate_comparative_analysis_with_none_match_score`: Tests None `matchScore`
- `test_identify_key_differentiators_with_none_altman_z`: Tests None `altman_z_score`
- `test_analyze_score_tiers_with_none_match_scores`: Tests None `match_score` in rankings
- `test_generate_recommendation_with_none_values`: Tests None `top_score`, `score_range`, `price_range`
- `test_calculate_value_score_with_none_price`: Tests None price parameter
- `test_calculate_value_score_with_none_match_score`: Tests None `matchScore` in home
- `test_generate_price_comparison_with_none_prices`: Tests None `weeklyPrice` values
- `test_generate_match_score_rankings_with_none_scores`: Tests None `matchScore` values

### test_safe_float_conversion.py

**Purpose**: Tests safe float conversion functions across services

**Coverage**:
- None value handling
- String to float conversion (including strings with text like "Waived fees or 2")
- Integer and float value handling
- Edge cases

**Note**: This test file already existed and covers the regression bug for string-to-float conversion.

## Frontend Tests

### NegotiationStrategyViewer.test.tsx

**Purpose**: Tests None/null value handling in `NegotiationStrategyViewer` React component

**Coverage**:
- Null `region` value handling (prevents `.replace()` error)
- Null `care_type` value handling (prevents `.replace()` error)
- Null `negotiation_potential.potential` value handling (prevents `.toUpperCase()` error)
- Null `discount.priority` value handling (prevents `.toUpperCase()` error)
- Null `category` value handling (prevents `.replace()` error)
- Undefined values handling
- Missing objects handling
- Empty arrays handling

**Key Test Cases**:
- `handles null region value gracefully`: Tests null `region`
- `handles null care_type value gracefully`: Tests null `care_type`
- `handles undefined region value gracefully`: Tests undefined `region`
- `handles undefined care_type value gracefully`: Tests undefined `care_type`
- `handles null negotiation_potential.potential value gracefully`: Tests null `potential`
- `handles null discount priority value gracefully`: Tests null `priority`
- `handles null category in questions_to_ask_at_visit gracefully`: Tests null `category`
- `handles missing negotiation_potential object gracefully`: Tests missing object
- `handles empty price_comparison array`: Tests empty array
- `handles region with underscore correctly`: Tests underscore replacement
- `handles care_type with underscore correctly`: Tests underscore replacement

## Running the Tests

### Backend Tests

```bash
# Run all None handling tests
cd api-testing-suite/backend
pytest tests/test_negotiation_strategy_none_handling.py -v
pytest tests/test_comparative_analysis_none_handling.py -v
pytest tests/test_safe_float_conversion.py -v

# Run all tests
pytest tests/ -v
```

### Frontend Tests

```bash
# Run NegotiationStrategyViewer tests
cd api-testing-suite/frontend
npm test -- NegotiationStrategyViewer.test.tsx

# Run all tests
npm test
```

## Test Coverage

These tests ensure that:

1. **None values are handled gracefully** - No `TypeError` when comparing None with numbers
2. **Null values are handled gracefully** - No `TypeError` when calling methods on null objects
3. **String values are converted safely** - String numbers are converted to float before comparison
4. **Missing objects/fields are handled** - Missing optional fields don't cause errors
5. **Edge cases are covered** - Empty arrays, undefined values, etc.

## Regression Prevention

These tests prevent the following errors from recurring:

1. `TypeError: '>' not supported between instances of 'NoneType' and 'int'`
2. `TypeError: Cannot read properties of null (reading 'replace')`
3. `TypeError: Cannot read properties of null (reading 'toUpperCase')`
4. `ValueError: could not convert string to float: 'Waived fees or 2'`

## Related Documentation

- `BUG_NONETYPE_COMPARISON_FIX.md` - Details of all fixes applied
- `README_SAFE_FLOAT_TESTS.md` - Documentation for safe float conversion tests
- `PROFESSIONAL_REPORT_TESTS.md` - Overall test coverage for Professional Report

