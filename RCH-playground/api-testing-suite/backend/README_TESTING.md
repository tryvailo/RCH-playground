# Testing Matching for All Questionnaires

## Quick Start

1. **Make sure backend is running:**
   ```bash
   cd api-testing-suite/backend
   # Start backend server (usually: uvicorn main:app --reload)
   ```

2. **Run the test script:**
   ```bash
   python3 test_matching_all_questionnaires.py
   ```

3. **Check results:**
   - Console output: Real-time test results
   - `matching_test_results.json`: Detailed JSON results
   - `matching_test_report.txt`: Human-readable comparison report

## What the Test Does

The script tests all 6 questionnaires:
- `questionnaire_1.json`: SW1A 1AA, residential, £1200/week
- `questionnaire_2.json`: M1 1AA, nursing, £1500/week
- `questionnaire_3.json`: B1 1AA, dementia, £1000/week
- `questionnaire_4.json`: B44 8DD, residential, £950/week
- `questionnaire_5.json`: B31 2TX, dementia, £1200/week
- `questionnaire_6.json`: B72 1DU, nursing, £1400/week

For each questionnaire, it:
1. Sends POST request to `/api/free-report`
2. Extracts 3 scenarios: Safe Bet, Best Value, Premium
3. Compares results across questionnaires
4. Checks for uniqueness (no duplicate recommendations)

## Expected Output

The report shows:
- **Summary**: How many questionnaires tested successfully
- **Detailed Results**: For each questionnaire, shows all 3 scenarios with:
  - Care home name
  - Postcode
  - Distance
  - Weekly cost
  - CQC rating
- **Comparison by Scenario**: Groups all Safe Bet, Best Value, Premium recommendations
- **Uniqueness Analysis**: Detects if same care home recommended multiple times

## Troubleshooting

If you get HTTP 500 errors:
1. Check backend logs for detailed error messages
2. Ensure database is connected and accessible
3. Verify all required services are running (PostcodeResolver, PricingService, etc.)
4. Check that care_homes database table has data

If backend is not running:
- The script will fail with connection errors
- Start backend first: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`

## Interpreting Results

**Good signs:**
- ✅ All 6 questionnaires return different care homes
- ✅ Each scenario (Safe Bet, Best Value, Premium) shows unique homes
- ✅ No duplicate recommendations across questionnaires
- ✅ Distances and costs vary based on postcode/location

**Warning signs:**
- ⚠️ Same care homes recommended for different postcodes
- ⚠️ Duplicate recommendations in same scenario
- ⚠️ All questionnaires return same 3 homes
- ⚠️ Distances don't match postcode locations

