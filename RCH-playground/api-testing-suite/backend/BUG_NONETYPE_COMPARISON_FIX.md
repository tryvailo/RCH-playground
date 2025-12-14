# Bug Fix: NoneType Comparison Error

**Date:** 2025-01-XX  
**Status:** ✅ FIXED  
**Severity:** HIGH (Blocking report generation)

## Problem

Error when generating Professional Report:
```
Error Generating Report
'>' not supported between instances of 'NoneType' and 'int'
```

## Root Cause

The error occurred when trying to compare None values with numbers in several places:

1. **negotiation_strategy_service.py** - When comparing prices without safe conversion
2. **funding_optimization_service.py** - When comparing financial values (assets, income, property_value, eligibility_probability, dpa_payment_5yr, available_deferral) that could be None
3. **red_flags_service.py** - When comparing revenues, margins, prices from pricing_history
4. **comparative_analysis_service.py** - When comparing prices, match scores, altman_z, top_score, score_range, and price_range
5. **professional_matching_service.py** - When calculating point_allocations with None category_scores or weights, and when comparing staff_quality values (glassdoor_rating, avg_tenure_years, turnover_rate) and distance_miles
6. **main.py** - When using match_result['point_allocations'] and match_result['normalized'] with None values
7. **financial_enrichment_service.py** - When comparing revenues, margins, working_capitals values
8. **staff_enrichment_service.py** - When comparing active_listings, staff_count, job_boards_count
9. **google_places_enrichment_service.py** - When comparing average_sentiment
10. **fsa_enrichment_service.py** - Removed redundant None check after int() conversion
11. **red_flags_service.py** - Added explicit float conversion for `altman_z`, `bankruptcy_risk`, `revenues`, `turnover_rate`, `avg_tenure`, `glassdoor_rating`, and `job_listings_count` values before comparisons
12. **negotiation_strategy_service.py** - Added explicit float conversion for `match_score`, `regional_average`, `autumna_avg`, `vs_market_percent`, `value_score`, `avg_price`, `price_range`, `turnover_rate_percent`, and `bankruptcy_risk_score` before comparisons

The issue was that some numeric fields could be None or strings, and were being compared directly with numbers without proper type checking and conversion.

## Solution

Added explicit type checking and conversion before all comparisons:

### 1. negotiation_strategy_service.py
- **Line 458**: Added `_safe_float_convert()` before comparing price with 0
- **Line 472, 478**: Use `price_float` instead of `price` in comparisons
- **Lines 1079-1081**: Added explicit float conversion for `bankruptcy_risk_score` before comparison in `_identify_priority_questions()`
- **Lines 1086-1094**: Added explicit float conversion for `turnover_rate_percent` before comparison in `_identify_priority_questions()`

### 2. funding_optimization_service.py

#### calculate_la_funding_availability():
- **Lines 595-608**: Added explicit float conversion for `estimated_assets` and `estimated_income`
- **Line 610-619**: Added explicit float conversion for `property_value`
- **Line 647**: Ensure `property_value` is a number before use
- **Line 655-656**: Ensure `estimated_assets` and `assessable_property_value` are numbers
- **Line 678-679**: Ensure `estimated_income` and `capital_contribution` are numbers
- **Line 693**: Ensure `income_contribution` and `capital_contribution` are numbers before calculating `total_weekly_contribution`

#### calculate_dpa_considerations():
- **Lines 904-912**: Added explicit float conversion for `property_value`
- **Lines 914-916**: Added explicit float conversion for `outstanding_mortgage`
- **Lines 917-919**: Added explicit float conversion for `estimated_weekly_care_cost`
- **Line 921**: Ensure all values are numbers before calculating equity

#### calculate_five_year_projections():
- **Lines 1148-1157**: Added explicit float conversion for `eligibility_probability` before comparisons
- **Lines 1194-1195**: Use converted `eligibility_probability` instead of raw value
- **Lines 1014-1015**: Added explicit float conversion for `dpa_payment_5yr` before comparison

#### _recommend_funding_scenario():
- **Lines 1238-1245**: Added explicit float conversion for `eligibility_probability` before comparison

#### _calculate_funding_summary():
- **Lines 1295-1303**: Added explicit float conversion for `eligibility_probability` before comparisons

#### _calculate_dpa_projections():
- **Lines 1537-1540**: Added explicit float conversion for `available_deferral`, `interest_rate`, and `admin_fee_annual` before calculations

### 3. red_flags_service.py

#### _assess_financial_stability_warnings():
- **Line 236**: Added explicit float conversion for `revenues[0]` and `revenues[-1]` before comparison
- **Line 248**: Added explicit float conversion for `margins` values before checking for negative values

#### _assess_pricing_increases_history():
- **Line 491**: Replaced list comprehension with safe extraction loop using `_safe_float_convert()` for prices from `pricing_history`

### 4. comparative_analysis_service.py

#### _analyze_price_comparison():
- **Line 339**: Replaced list comprehension with safe extraction loop using `_safe_float_convert()` for prices
- **Line 353**: Added explicit float conversion for `price` before calculations

#### _identify_key_differentiators():
- **Line 407**: Added safe extraction and conversion for `matchScore` values, filtering out None

#### _calculate_value_score():
- **Line 685**: Added explicit float conversion for `matchScore` before calculation
- **Line 707**: Added explicit float conversion for `price` parameter before comparison

#### _identify_key_differentiators():
- **Lines 434-437**: Replaced list comprehension with safe extraction loop for prices, using `_safe_float_convert()` and `home_prices_map`
- **Lines 507-520**: Added explicit float conversion for `best_altman_z` before comparison and in description

#### _analyze_score_tiers():
- **Lines 740-772**: Added explicit float conversion for all `match_score` values before comparisons

#### _generate_recommendation():
- **Lines 808-829**: Added explicit float conversion for `top_score`, `top_price`, `score_range`, and `price_range` before comparisons

### 5. professional_matching_service.py

#### calculate_156_point_match():
- **Lines 229-238**: Added safe conversion for all `category_scores` and `weights_dict` values before calculating `point_allocations`
- **Lines 241-248**: Added safe conversion for `total_score` and `normalized` before returning

#### _calculate_staff_quality():
- **Lines 804-806**: Added explicit float conversion for `glassdoor_rating` before comparison
- **Lines 818-820**: Added explicit float conversion for `avg_tenure_years` before comparison
- **Lines 832-848**: Added explicit float conversion for `turnover_rate` before comparison

#### _calculate_location_access():
- **Lines 521-525**: Added explicit float conversion for `distance_miles` before comparisons

### 6. main.py

#### generate_professional_report():
- **Lines 5284-5342**: Added safe conversion for all `match_result['point_allocations']` values using `.get()` with default 0
- **Line 5268**: Added safe conversion for `match_result['normalized']` using `.get()` with default 0

### 7. financial_enrichment_service.py

#### _calculate_three_year_summary():
- **Lines 235-261**: Added explicit float conversion for `rev0`, `rev_last`, `margin0`, `margin_last`, `wc0`, `wc_last` before comparisons with try/except blocks

### 8. staff_enrichment_service.py

#### _calculate_overall_turnover_estimate():
- **Lines 167-170**: Added explicit float conversion for `active_listings` and `staff_count` before comparison

#### _assess_combined_data_quality():
- **Lines 191-202**: Added explicit float conversion for `job_boards_count` before comparison

### 9. google_places_enrichment_service.py

#### _analyze_sentiment_simple():
- **Lines 100-106**: Added explicit float conversion for `average_sentiment` before comparison

### 10. fsa_enrichment_service.py

#### _rating_to_color():
- **Line 85**: Removed redundant None check after int() conversion (rating_int is guaranteed to be int or exception would have been raised)

### 11. red_flags_service.py

#### _assess_financial_stability():
- **Lines 154-156**: Added explicit float conversion for `altman_z` before comparison
- **Lines 178-180**: Added explicit float conversion for `bankruptcy_risk` before comparison
- **Lines 247-249**: Added explicit float conversion for `revenue_start` and `revenue_end` with try/except blocks

### 12. negotiation_strategy_service.py

#### _generate_market_rate_analysis():
- **Lines 288-289**: Added explicit float conversion for `regional_multiplier` and `uk_average` before calculation
- **Lines 295-298**: Added explicit float conversion for `autumna_avg` before calculation
- **Lines 321-331**: Added explicit float conversion for `vs_market` and `vs_uk` before passing to functions

#### _get_price_positioning():
- **Lines 368-371**: Added explicit float conversion for `vs_market_percent` before comparison

#### _assess_negotiation_potential():
- **Lines 384-388**: Added explicit float conversion for `vs_market_percent` and `match_score` before comparisons

#### _identify_best_value():
- **Lines 495-540**: Added explicit float conversion for `match_score`, `regional_average`, `value_score` before comparisons and calculations

#### _generate_market_insights():
- **Lines 558-571**: Added explicit float conversion for `prices`, `avg_price`, `price_range`, and `regional_average` before comparisons

### 11. red_flags_service.py (Additional fixes)

#### _assess_staff_turnover():
- **Lines 407-409**: Added explicit float conversion for `turnover_rate` before comparison
- **Lines 431-433**: Added explicit float conversion for `avg_tenure` before comparison
- **Lines 455-457**: Added explicit float conversion for `glassdoor_rating` before comparison
- **Lines 469-470**: Added explicit float conversion for `job_listings_count` before comparison

## Pattern

All numeric comparisons now follow this pattern:
```python
# Before (unsafe):
if value > 0:  # Error if value is None

# After (safe):
value = float(value) if value is not None else 0.0
if value > 0:  # Safe comparison
```

## Testing

- ✅ No linter errors
- ✅ All numeric values are converted to float before comparisons
- ✅ Default values provided for None cases
- ✅ Type errors handled with try/except

## Prevention

- Always convert values to numbers before mathematical operations
- Use `_safe_float_convert()` for user input or external data
- Add explicit None checks before comparisons
- Provide default values for optional numeric fields

