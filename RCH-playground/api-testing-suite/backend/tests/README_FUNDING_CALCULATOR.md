# Funding Calculator API Integration Tests

## Overview

Integration tests for the `/api/rch-data/funding/calculate` endpoint covering:
- Valid requests
- CHC eligibility calculations
- LA support calculations
- DPA eligibility
- Complex therapies and bonuses
- Validation errors
- Edge cases
- Performance

## Running Tests

### Run All Funding Calculator Tests

```bash
cd backend
pytest tests/test_funding_calculator_api.py -v
```

### Run with Coverage

```bash
pytest tests/test_funding_calculator_api.py --cov=api_clients.rch_data_routes --cov-report=html -v
```

### Run Specific Test Class

```bash
pytest tests/test_funding_calculator_api.py::TestFundingCalculatorEndpoint -v
```

### Run Specific Test

```bash
pytest tests/test_funding_calculator_api.py::TestFundingCalculatorEndpoint::test_valid_request -v
```

## Test Coverage

### Valid Requests (1 test)
- ✅ Valid funding calculation request

### CHC Eligibility (2 tests)
- ✅ High probability with PRIORITY domain
- ✅ Multiple SEVERE domains give high probability

### LA Support (3 tests)
- ✅ Full support below lower limit
- ✅ Self-funding above upper limit
- ✅ Tariff income calculation

### DPA Eligibility (2 tests)
- ✅ DPA eligibility with property
- ✅ Property with qualifying relative is disregarded

### Complex Features (2 tests)
- ✅ Complex therapies bonus
- ✅ Unpredictability bonus

### Validation (4 tests)
- ✅ Invalid domain level handled gracefully
- ✅ Missing required fields return 422
- ✅ Negative capital assets rejected
- ✅ Negative weekly income rejected
- ✅ Invalid age rejected

### Edge Cases (3 tests)
- ✅ All domains set to no needs
- ✅ Property with qualifying relative
- ✅ Response time < 2 seconds

## Test Structure

Tests use:
- **pytest** - Test framework
- **TestClient** - FastAPI test client
- **Fixtures** - Reusable test data

## Prerequisites

- RCH-data package installed: `pip install -e ../RCH-data`
- Backend server dependencies installed
- Funding calculator module available

## Skipping Tests

Tests automatically skip if:
- Funding calculator module is not available (503 status)
- RCH-data package is not installed

## Best Practices

1. **Isolation**: Each test is independent
2. **Fixtures**: Reusable test data via fixtures
3. **Assertions**: Clear, specific assertions
4. **Error Handling**: Tests handle service unavailability gracefully
5. **Performance**: Tests verify response time requirements

