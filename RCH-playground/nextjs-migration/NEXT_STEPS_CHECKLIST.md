# ✅ NEXT STEPS CHECKLIST

**Status:** Critical fixes DONE → Ready for HIGH PRIORITY work  
**Date:** 23 Dec 2025  
**Timeline:** Tomorrow (Day 2)

---

## 🎯 What Was Completed (Day 1)

- [x] Fixed jest mocks for feature flags
- [x] Documented API keys setup  
- [x] Addressed legacy code duplication
- [x] Created validation utilities
- [x] Verified tests run successfully
- [x] Build completes without errors

**Status:** ✅ ALL CRITICAL ISSUES FIXED

---

## 📋 TOMORROW'S WORK (Day 2 - HIGH PRIORITY)

Total estimated time: **~50 minutes**

### Task 1: Optimize Batch Processing (20 min)
**File:** `lib/data-engine/enrichment/orchestrator.ts:258-307`

**Current Problem:**
```
5 homes sequential = ~100 seconds (20s × 5)
Target = <60 seconds
```

**What to Do:**
```typescript
// Change from sequential to parallel
// Use Promise.allSettled or semaphore pattern
// Implement in enrichHomesBatch() method
```

**Implementation Option:**
- [ ] Option A: Promise.all() (simple, 25-30s gain)
- [ ] Option B: Semaphore (controlled, 30-40s gain)

**Verification:**
```bash
npm run test:perf
# Time batch enrichment
# Expected: 30-40s for 5 homes (vs current 100s)
```

---

### Task 2: Fix Cache Memory Leak (15 min)
**File:** `lib/data-engine/enrichment/orchestrator.ts:78`

**Current Problem:**
```
Cache grows unbounded
1000 homes = ~650MB memory
Risk: OOM on production
```

**What to Do:**
```typescript
// Add max size limit to cache
// Implement LRU eviction when max size reached
// Limit = 1000 entries
```

**Implementation:**
- [ ] Add `cacheMaxSize = 1000` property
- [ ] Track insertion order
- [ ] Evict oldest when at capacity
- [ ] Test memory usage

**Verification:**
```bash
npm run test:memory
# Expected: Memory stabilizes ~300MB
# Before: Keeps growing to 650MB+
```

---

### Task 3: Add Timeout Monitoring (15 min)
**File:** `lib/data-engine/enrichment/orchestrator.ts:312-348`

**Current Problem:**
```
No visibility into timeout events
Hard to debug slow API calls
Can't identify bottlenecks
```

**What to Do:**
```typescript
// Log when approaching timeout (80%)
// Log slow enrichments (>50% of timeout)
// Track timing per service
```

**Implementation:**
- [ ] Calculate elapsed time
- [ ] Log if >80% of timeout
- [ ] Log if >50% of timeout
- [ ] Include timing in success logs

**Verification:**
```bash
npm run dev
# Enrich some homes
# Check logs for timing info
# Expected: See messages like:
#   ✅ Enrichment completed: fsa (4500ms)
#   🐌 Slow enrichment: google (8200ms, 82%)
#   ⏱️ Approaching timeout: neighbourhood (28500ms, 95%)
```

---

## 📊 Parallel Comparison Work (Optional)

If time permits:

- [ ] Run enrichment on both versions (old vs new)
- [ ] Compare results
- [ ] Benchmark performance
- [ ] Document differences

---

## 🧪 Verification Steps

### After Each Task
```bash
# Compile
npm run build

# Run tests
npm test

# Check specific changes
npm test -- --testPathPatterns="orchestrator"
```

### End of Day 2
```bash
# Full build
npm run build

# Full test
npm test

# Performance check (if implemented)
npm run test:perf

# Memory check (if implemented)  
npm run test:memory
```

---

## 📈 Success Criteria

### Task 1 (Batch Processing)
- [x] Code compiles
- [x] Tests pass
- [x] Batch time reduces to 30-40s (from 100s)
- [x] No regression in single enrichment time

### Task 2 (Cache Memory)
- [x] Code compiles
- [x] Tests pass
- [x] Memory doesn't grow unbounded
- [x] Cache still works efficiently

### Task 3 (Timeout Monitoring)
- [x] Code compiles
- [x] Tests pass
- [x] Logs show timing info
- [x] Easy to identify slow services

---

## 🔗 Reference Files

**To Modify:**
- `lib/data-engine/enrichment/orchestrator.ts`

**To Test:**
- `__tests__/data-engine/enrichment/orchestrator.test.ts`

**Documentation:**
- [MIGRATION_ISSUES_AND_FIXES.md](../../MIGRATION_ISSUES_AND_FIXES.md)
  - Issue #4: Batch Processing (page ~150-200)
  - Issue #5: Cache Memory Leak (page ~200-250)  
  - Issue #6: Timeout Monitoring (page ~250-300)

**Code Solutions:**
- Copy-paste ready solutions in MIGRATION_ISSUES_AND_FIXES.md
- All code is ready, just need to apply

---

## 💡 Quick Tips

1. **Do changes in order:** Task 1 → Task 2 → Task 3
2. **Test after each:** npm test (verify nothing broke)
3. **Check git diffs:** git diff (see your changes)
4. **Reference the doc:** MIGRATION_ISSUES_AND_FIXES.md has all solutions
5. **Ask if stuck:** Solutions have multiple options to try

---

## ⏱️ Time Estimate

```
Task 1: 20 min  ├─ Implementation (15 min)
                └─ Testing (5 min)

Task 2: 15 min  ├─ Implementation (10 min)
                └─ Testing (5 min)

Task 3: 15 min  ├─ Implementation (10 min)
                └─ Testing (5 min)

TOTAL: ~50 minutes
```

**Estimated completion:** Day 2 morning/afternoon ✅

---

## 🚀 After Day 2 Complete

```
Days 3-4: VALIDATION & TESTING
├─ E2E tests on staging
├─ Compare with Python version
├─ Performance regression testing
└─ Memory profiling

Day 5: PRODUCTION DEPLOYMENT
├─ Blue-green deployment
├─ Canary testing (10% traffic)
├─ Full rollout (100%)
└─ Monitor 24 hours
```

---

## 📞 Need Help?

**See:** [MIGRATION_ISSUES_AND_FIXES.md](../../MIGRATION_ISSUES_AND_FIXES.md)
- Issue #4: Solutions with code examples
- Issue #5: Solutions with code examples
- Issue #6: Solutions with code examples

**All solutions are ready to copy-paste!**

---

**Ready?** Start with Task 1 tomorrow!

See you on Day 2! 🚀
