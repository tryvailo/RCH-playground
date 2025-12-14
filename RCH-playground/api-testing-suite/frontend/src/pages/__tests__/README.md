# Funding Calculator Tests

## Overview

Comprehensive test suite for the Funding Calculator component covering:
- Component rendering
- Form validation
- Domain assessments
- Form submission
- Error handling
- Results display
- Edge cases
- Loading states

## Running Tests

### Install Dependencies

```bash
cd frontend
npm install
```

### Run All Tests

```bash
npm test
```

### Run Tests in Watch Mode

```bash
npm test -- --watch
```

### Run Tests with UI

```bash
npm run test:ui
```

### Run Tests with Coverage

```bash
npm run test:coverage
```

### Run Specific Test File

```bash
npm test FundingCalculator.test.tsx
```

### Run Specific Test

```bash
npm test -- -t "should render the calculator form"
```

## Test Coverage

### Component Rendering (6 tests)
- ✅ Renders calculator form
- ✅ Renders all 12 DST domain fields
- ✅ Renders complex therapies section
- ✅ Renders income disregards section
- ✅ Renders asset disregards section

### Form Validation (4 tests)
- ✅ Requires age field
- ✅ Accepts valid age values
- ✅ Rejects negative capital assets
- ✅ Rejects negative weekly income

### Domain Assessments (2 tests)
- ✅ Allows selecting domain levels
- ✅ Has all domain level options

### Form Submission (4 tests)
- ✅ Submits form with valid data
- ✅ Builds correct domain assessments
- ✅ Calculates adjusted capital assets after disregards
- ✅ Calculates adjusted weekly income after disregards

### Error Handling (5 tests)
- ✅ Displays network error message
- ✅ Displays validation error message
- ✅ Displays server error message
- ✅ Shows retry button for retryable errors
- ✅ Shows support contact link

### Results Display (2 tests)
- ✅ Displays CHC eligibility results
- ✅ Displays means test breakdown

### Edge Cases (4 tests)
- ✅ Handles zero capital assets
- ✅ Handles very high capital assets
- ✅ Handles all domains set to no needs
- ✅ Handles property details when property checkbox is checked

### Loading States (1 test)
- ✅ Shows loading state during calculation

## Test Structure

Tests use:
- **Vitest** - Test runner
- **@testing-library/react** - React component testing
- **@testing-library/user-event** - User interaction simulation
- **jsdom** - DOM environment for tests

## Mocking

- `axios` is mocked to avoid actual API calls
- All API responses are controlled in tests
- Error scenarios are simulated

## Best Practices

1. **Isolation**: Each test is independent
2. **Cleanup**: Tests clean up after themselves
3. **Mocking**: External dependencies are mocked
4. **Coverage**: Aim for >80% code coverage
5. **Readability**: Tests are self-documenting

