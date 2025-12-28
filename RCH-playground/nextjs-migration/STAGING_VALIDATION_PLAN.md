# 🧪 STAGING VALIDATION & TESTING PLAN

**Phase:** Days 3-4  
**Environment:** Staging  
**Objective:** Validate enrichment migration before production deployment  
**Status:** 📋 COMPREHENSIVE VALIDATION PLAN

---

## 📋 VALIDATION OVERVIEW

### What We're Testing
- ✅ Enrichment functionality (all 6 services)
- ✅ Data accuracy vs Python version
- ✅ Performance metrics
- ✅ Memory stability
- ✅ Concurrent load handling
- ✅ Error recovery

### Success Criteria
1. **Functional:** All enrichment services work correctly
2. **Accurate:** Results match Python version
3. **Performant:** Batch < 60s, no memory leaks
4. **Reliable:** Graceful error handling, no crashes
5. **Observable:** Full logging, metrics collection
6. **Safe:** Ready for production deployment

---

## 🔍 TEST SUITE 1: FUNCTIONAL VALIDATION

### Test 1.1: Single Home Enrichment
**Goal:** Verify single home enrichment works end-to-end

```bash
# Test data
HOME_ID=1-test-001
HOME_NAME="Test Care Home"
POSTCODE="SW1A 1AA"

# Expected outputs
- FSA data with rating
- Financial data with stability score
- Google Places data with ratings
- Staff data with quality score
- CQC data with ratings
- Neighbourhood data with walkability

# Verification
✓ All 6 services return data
✓ No errors in enrichment
✓ Data structure matches expected schema
✓ Enrichment time < 30 seconds
```

### Test 1.2: Batch Enrichment (Parallel)
**Goal:** Verify parallel batch processing works

```bash
# Test batch
HOMES_COUNT=5

# Expected behavior
- All 5 homes enrich simultaneously (not sequential)
- Total time ~30s (not 100s)
- parallelOptimized flag = true

# Verification
✓ Batch time < 60 seconds
✓ Parallel flag active in logs
✓ All homes enriched successfully
✓ No memory spikes during batch
```

### Test 1.3: Missing API Keys Handling
**Goal:** Verify graceful degradation with missing keys

```bash
# Test scenario
UNSET: COMPANIES_HOUSE_API_KEY

# Expected behavior
- Financial service disabled
- Other services work normally
- Clear error logging
- Report generation continues

# Verification
✓ System starts without error
✓ Financial enrichment skipped
✓ Other data available
✓ No crash/crash
```

### Test 1.4: Service Error Handling
**Goal:** Verify error recovery for API failures

```bash
# Test scenario
- CQC API returns 500 error
- Google Places API timeout

# Expected behavior
- Graceful degradation
- Other services continue
- Error logged with context
- Report generated with available data

# Verification
✓ No crash on API error
✓ Partial enrichment returns
✓ Errors documented in metadata
✓ Other services unaffected
```

---

## 🔄 TEST SUITE 2: ACCURACY VALIDATION

### Test 2.1: Compare with Python Version

```bash
# Test setup
HOMES_COUNT=20

# Process with both versions (parallel)
PYTHON_OUTPUT=$(run_python_enrichment)
TS_OUTPUT=$(run_typescript_enrichment)

# Comparison
- FSA ratings match
- Financial scores match (within 0.01%)
- CQC ratings match
- Staff quality levels match
- Google ratings match
- Neighbourhood scores match

# Verification Results
✓ Functional equivalence
✓ Numerical accuracy
✓ Data structure match
✓ Timestamp handling correct
```

### Test 2.2: Edge Case Data

```bash
# Edge cases
1. Home without postcode
   - Should use coordinates instead
   - Neighbourhood data still generated

2. Home without company number
   - Should skip financial enrichment
   - Other services work

3. Invalid postcode
   - Graceful error
   - Fallback handling
   - Report continues

# Verification
✓ All edge cases handled
✓ No unexpected errors
✓ Graceful degradation
✓ User-friendly error messages
```

---

## ⚡ TEST SUITE 3: PERFORMANCE VALIDATION

### Test 3.1: Single Home Performance

```bash
# Metrics to track
- Total enrichment time
- Time per service:
  - FSA: target < 5s
  - Financial: target < 10s
  - Google Places: target < 10s
  - Staff: target < 30s
  - CQC: target < 30s
  - Neighbourhood: target < 20s

# Results Criteria
✓ Total < 30 seconds
✓ Each service within budget
✓ No timeouts
✓ All data returned
```

### Test 3.2: Batch Performance

```bash
# Load test
BATCH_SIZES = [1, 5, 10, 20, 50]

# Expected scaling (parallel)
- 1 home: ~20s
- 5 homes: ~25-30s (parallel)
- 10 homes: ~30-35s (parallel)
- 20 homes: ~35-40s (parallel)
- 50 homes: ~40-45s (parallel)

# NOT expected (sequential would be):
- 5 homes: ~100s ❌
- 10 homes: ~200s ❌

# Verification
✓ Parallel efficiency > 50%
✓ No degradation with load
✓ Linear scaling (not exponential)
```

### Test 3.3: Memory Usage

```bash
# Memory tracking
START_MEMORY = measure()
PROCESS_HOMES = 1000

# Monitor during processing
- Peak memory should be < 500MB
- Memory should not grow unbounded
- LRU cache working (1000 entry limit)

# Verification
✓ Memory stable at 400-500MB
✓ No memory leaks
✓ Cache eviction working
✓ GC pauses normal
```

---

## 🔐 TEST SUITE 4: RELIABILITY VALIDATION

### Test 4.1: Timeout Monitoring

```bash
# Verify timeout logs
- Normal operation: ✅ logs (debug level)
- Slow operation (>50%): 🐌 logs (info level)
- Approaching timeout (>80%): ⏱️ logs (warn level)
- Timeout exceeded: ❌ logs (error level)

# Verification
✓ All timeout categories logged
✓ Log levels correct
✓ Timing percentages accurate
✓ Easy to identify slow services
```

### Test 4.2: Error Recovery

```bash
# Test failures
1. Network timeout
   - Handled gracefully
   - Retry mechanism works
   - Partial data returned

2. Invalid API response
   - Logged and handled
   - Service marked failed
   - Other services continue

3. Database error
   - Graceful degradation
   - Error message clear
   - System stable

# Verification
✓ All error types handled
✓ No unhandled exceptions
✓ Recovery time < 5s
✓ Data integrity maintained
```

### Test 4.3: Concurrent Requests

```bash
# Concurrent user simulation
CONCURRENT_USERS = 10
HOMES_PER_USER = 5

# Expected behavior
- All users enriched successfully
- No race conditions
- No data corruption
- System stable

# Verification
✓ 50 concurrent enrichments
✓ No deadlocks
✓ All complete successfully
✓ Memory/CPU normal
```

---

## 📊 TEST SUITE 5: DATA VALIDATION

### Test 5.1: Schema Validation

```bash
# Verify enrichment result schema
EnrichedHome {
  homeId: string ✓
  home: CareHome ✓
  enrichments: {
    fsa?: FSAData ✓
    financial?: FinancialData ✓
    google?: GoogleData ✓
    staff?: StaffData ✓
    cqc?: CQCData ✓
    neighbourhood?: NeighbourhoodData ✓
  }
  metadata: {
    enrichmentTime: number ✓
    sourcesUsed: string[] ✓
    sourcesFailed: string[] ✓
    errors: string[] ✓
  }
}

# Verification
✓ All fields present
✓ Types correct
✓ Optional fields handled
✓ Nested structures valid
```

### Test 5.2: Data Consistency

```bash
# Process same home multiple times
ITERATIONS = 5

# Verify
- Same input → same output (cached or fresh)
- Timestamp progression correct
- No data drift
- Cache hits when expected

# Verification
✓ Deterministic results
✓ Cache working
✓ Data consistency maintained
```

---

## 📈 MONITORING & METRICS

### Metrics to Collect

```javascript
{
  // Performance
  "enrichment_time_ms": 22450,
  "batch_size": 5,
  "time_per_home_ms": 4490,
  "parallel_factor": 4.5,
  
  // Success rates
  "total_homes": 100,
  "successful": 98,
  "partial": 2,
  "failed": 0,
  "success_rate": "98%",
  
  // Service-level
  "services": {
    "fsa": { success: 98, avg_time: 4200 },
    "financial": { success: 96, avg_time: 8900 },
    "google": { success: 99, avg_time: 7800 },
    "staff": { success: 95, avg_time: 25000 },
    "cqc": { success: 98, avg_time: 12000 },
    "neighbourhood": { success: 97, avg_time: 18000 }
  },
  
  // Memory
  "memory_start_mb": 150,
  "memory_peak_mb": 480,
  "memory_end_mb": 420,
  "cache_size": 875,
  
  // Timing percentiles
  "p50": 20000,
  "p75": 25000,
  "p95": 31000,
  "p99": 35000
}
```

---

## ✅ VALIDATION CHECKLIST

### Pre-Staging Checks
- [ ] All code changes committed
- [ ] Build succeeds: `npm run build`
- [ ] Tests pass: `npm test`
- [ ] No TypeScript errors
- [ ] Environment variables configured
- [ ] API keys set for all services

### Staging Deployment
- [ ] Deploy to staging environment
- [ ] Services initialized correctly
- [ ] All enrichment services registered
- [ ] Feature flags configured
- [ ] Logging configured
- [ ] Monitoring tools ready

### Functional Testing
- [ ] Test 1.1: Single home enrichment
- [ ] Test 1.2: Batch enrichment (parallel)
- [ ] Test 1.3: Missing API keys handling
- [ ] Test 1.4: Service error handling
- [ ] All tests pass

### Accuracy Validation
- [ ] Test 2.1: Compare with Python version
- [ ] Test 2.2: Edge case data
- [ ] Results match within tolerance
- [ ] No data discrepancies

### Performance Testing
- [ ] Test 3.1: Single home timing
- [ ] Test 3.2: Batch scaling
- [ ] Test 3.3: Memory stability
- [ ] Performance meets targets

### Reliability Testing
- [ ] Test 4.1: Timeout monitoring
- [ ] Test 4.2: Error recovery
- [ ] Test 4.3: Concurrent requests
- [ ] All recovery mechanisms work

### Data Validation
- [ ] Test 5.1: Schema validation
- [ ] Test 5.2: Data consistency
- [ ] Data integrity verified

### Sign-Off
- [ ] QA approval
- [ ] Performance metrics approved
- [ ] No blocking issues found
- [ ] Ready for production

---

## 🚀 STAGING TEST EXECUTION SCRIPT

```bash
#!/bin/bash
# staging-validation.sh

set -e

echo "🧪 STAGING VALIDATION SUITE"
echo "============================"

# 1. Deploy to staging
echo "📦 Deploying to staging..."
npm run build
npm run deploy:staging
sleep 5

# 2. Run functional tests
echo "✅ Testing functionality..."
npm test -- --testPathPatterns="enrichment" --coverage

# 3. Run E2E validation
echo "🔄 Running E2E tests..."
npm run test:e2e:staging

# 4. Performance test
echo "⚡ Performance validation..."
npm run test:performance:staging

# 5. Compare with Python
echo "🔀 Comparing with Python version..."
npm run test:comparison:python

# 6. Memory profiling
echo "💾 Memory profiling..."
npm run test:memory:staging

# 7. Load testing
echo "📊 Load testing..."
npm run test:load:staging -- --users 10 --duration 300

# 8. Collect metrics
echo "📈 Collecting metrics..."
npm run metrics:collect:staging > metrics.json

# 9. Generate report
echo "📋 Generating report..."
npm run report:staging metrics.json > STAGING_VALIDATION_REPORT.md

echo ""
echo "✅ STAGING VALIDATION COMPLETE"
echo "📄 See STAGING_VALIDATION_REPORT.md for details"
```

---

## 📝 EXPECTED OUTCOMES

### Success Indicators
✅ All enrichment services functional  
✅ Performance within targets (batch < 60s)  
✅ Memory stable (< 500MB)  
✅ Results match Python (within tolerance)  
✅ Error handling graceful  
✅ Logging comprehensive  
✅ Zero blocking issues  

### Sign-Off Ready
✅ QA approval obtained  
✅ Performance approved  
✅ Data accuracy verified  
✅ Reliability confirmed  
✅ Ready for production  

---

**Timeline:** Days 3-4  
**Effort:** ~16 hours  
**Next Step:** Production deployment (Day 5)

See: STAGING_VALIDATION_RESULTS.md (after completion)
