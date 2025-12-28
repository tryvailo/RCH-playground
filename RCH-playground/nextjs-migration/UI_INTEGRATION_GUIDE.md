# 🎨 UI INTEGRATION GUIDE

**Phase:** Day 5+ (UI Integration)  
**Status:** 📋 READY FOR INTEGRATION  
**Audience:** Frontend Developers, UI Team

---

## 🎯 INTEGRATION OVERVIEW

### What You're Getting
✅ Fully functional enrichment orchestrator  
✅ 6 enrichment services (FSA, Financial, Google, Staff, CQC, Neighbourhood)  
✅ Type-safe TypeScript interfaces  
✅ Comprehensive logging & monitoring  
✅ Error handling & graceful degradation  
✅ Performance optimized (parallel batch processing)  

### Integration Points
```
Your UI Component
    ↓
Professional Report Generator
    ↓
EnrichmentOrchestrator ⭐ (NEW)
    ↓
6 Enrichment Services
    ↓
External APIs (FSA, Companies House, Google, etc.)
```

---

## 📦 AVAILABLE EXPORTS

### Main Orchestrator
```typescript
// Location: lib/data-engine/enrichment/orchestrator.ts

export class EnrichmentOrchestrator {
  // Initialize services (already done in constructor)
  constructor()
  
  // Enrich single home
  async enrichHome(
    home: CareHome,
    config: EnrichmentConfig,
    context?: EnrichmentContext
  ): Promise<EnrichedHome>
  
  // Enrich multiple homes (batch)
  async enrichHomesBatch(
    homes: CareHome[],
    config: EnrichmentConfig,
    context?: EnrichmentContext,
    progressCallback?: (progress: number, message: string) => void
  ): Promise<EnrichedHome[]>
  
  // Get a specific service
  getService(sourceName: string): IEnrichmentService | undefined
  
  // List all registered services
  listServices(): string[]
  
  // Clear cache
  clearCache(): void
  
  // Get statistics
  getStats(): {
    orchestrator: {
      batchesProcessed: number
      totalHomesEnriched: number
      successful: number
      failed: number
      totalTime: number
      avgTimePerBatch: number
    }
    services: Record<string, any>
    cacheSize: number
  }
  
  // Reset statistics
  resetStats(): void
}
```

### Type Definitions
```typescript
// Location: lib/data-engine/enrichment/types.ts

export interface EnrichmentConfig {
  enabledSources: string[] // ['fsa', 'financial', 'google', 'staff', 'cqc', 'neighbourhood']
  parallelLimit: number // 3-5 recommended
  timeoutPerSource: number // 30 seconds recommended
  retryFailed: boolean // false recommended
  cacheResults: boolean // true recommended
}

export interface EnrichedHome {
  homeId: string
  home: CareHome
  enrichments: {
    fsa?: any // FSA rating data
    financial?: any // Financial stability data
    google?: any // Google Places data
    staff?: any // Staff quality data
    cqc?: any // CQC inspection data
    neighbourhood?: any // Neighbourhood analysis data
  }
  metadata: {
    enrichmentTime: number // milliseconds
    sourcesUsed: string[] // successful sources
    sourcesFailed: string[] // failed sources
    errors: string[] // error messages
  }
}

export interface EnrichmentResult {
  source: string
  status: 'success' | 'partial' | 'failed' | 'cached'
  data: Record<string, any>
  error?: string
  processingTime?: number
  metadata?: Record<string, any>
}
```

---

## 🔌 INTEGRATION EXAMPLES

### Example 1: Single Home Enrichment

```typescript
import { EnrichmentOrchestrator } from '@/lib/data-engine/enrichment/orchestrator';
import { CareHome } from '@/lib/shared/types/care-home';

async function enrichSingleHome(home: CareHome) {
  const orchestrator = new EnrichmentOrchestrator();
  
  const config = {
    enabledSources: ['fsa', 'financial', 'google', 'staff', 'cqc', 'neighbourhood'],
    parallelLimit: 3,
    timeoutPerSource: 30,
    retryFailed: false,
    cacheResults: true,
  };
  
  try {
    const enrichedHome = await orchestrator.enrichHome(home, config);
    
    // Use enriched data
    console.log('Enrichment complete:', enrichedHome.metadata);
    return enrichedHome;
  } catch (error) {
    console.error('Enrichment failed:', error);
    // Handle error gracefully
    return null;
  }
}
```

### Example 2: Batch Enrichment with Progress

```typescript
import { EnrichmentOrchestrator } from '@/lib/data-engine/enrichment/orchestrator';

async function enrichMultipleHomes(homes: CareHome[], onProgress: (p: number, msg: string) => void) {
  const orchestrator = new EnrichmentOrchestrator();
  
  const config = {
    enabledSources: ['fsa', 'financial', 'google', 'staff', 'cqc', 'neighbourhood'],
    parallelLimit: 3,
    timeoutPerSource: 30,
    retryFailed: false,
    cacheResults: true,
  };
  
  try {
    const enrichedHomes = await orchestrator.enrichHomesBatch(
      homes,
      config,
      undefined,
      (progress, message) => {
        // Update UI with progress
        console.log(`Progress: ${progress}% - ${message}`);
        onProgress(progress, message);
      }
    );
    
    return enrichedHomes;
  } catch (error) {
    console.error('Batch enrichment failed:', error);
    return [];
  }
}
```

### Example 3: Professional Report Integration

```typescript
// Already integrated in lib/reports/professional-report/generator.ts
// But if you need to use it directly:

import { EnrichmentOrchestrator } from '@/lib/data-engine/enrichment/orchestrator';

class MyReportGenerator {
  private enrichmentOrchestrator = new EnrichmentOrchestrator();
  
  async generateReport(homes: CareHome[], questionnaire: any) {
    // Step 1: Enrich homes
    const config = {
      enabledSources: ['fsa', 'financial', 'google', 'staff', 'cqc', 'neighbourhood'],
      parallelLimit: 3,
      timeoutPerSource: 30,
      retryFailed: false,
      cacheResults: true,
    };
    
    const enrichedHomes = await this.enrichmentOrchestrator.enrichHomesBatch(homes, config);
    
    // Step 2: Use enriched data in your report
    enrichedHomes.forEach(enrichedHome => {
      const { fsa, financial, google, staff, cqc, neighbourhood } = enrichedHome.enrichments;
      
      // Use enriched data for your calculations
      console.log('Enriched with:', enrichedHome.metadata.sourcesUsed);
    });
  }
}
```

### Example 4: Monitoring & Statistics

```typescript
import { EnrichmentOrchestrator } from '@/lib/data-engine/enrichment/orchestrator';

const orchestrator = new EnrichmentOrchestrator();

// After enriching homes...
const stats = orchestrator.getStats();

console.log('Statistics:', {
  batchesProcessed: stats.orchestrator.batchesProcessed,
  totalHomesEnriched: stats.orchestrator.totalHomesEnriched,
  successful: stats.orchestrator.successful,
  failed: stats.orchestrator.failed,
  totalTime: stats.orchestrator.totalTime,
  avgTimePerBatch: stats.orchestrator.avgTimePerBatch,
  cacheSize: stats.cacheSize,
});
```

---

## 🛠️ CONFIGURATION GUIDE

### Feature Flags
```env
# Enable/disable enrichment services
NEXT_PUBLIC_ENRICHMENT_FSA=true
NEXT_PUBLIC_ENRICHMENT_FINANCIAL=true
NEXT_PUBLIC_ENRICHMENT_GOOGLE_PLACES=true
NEXT_PUBLIC_ENRICHMENT_STAFF=true
NEXT_PUBLIC_ENRICHMENT_CQC=true
NEXT_PUBLIC_ENRICHMENT_NEIGHBOURHOOD=true
```

### API Keys
```env
# Required for enrichment services
COMPANIES_HOUSE_API_KEY=your_key
GOOGLE_PLACES_API_KEY=your_key
CQC_API_KEY=your_key
PERPLEXITY_API_KEY=your_key
OS_PLACES_API_KEY=your_key (optional)
```

### Optimal Configuration
```typescript
const optimalConfig = {
  enabledSources: [
    'fsa',
    'financial',
    'google',
    'staff',
    'cqc',
    'neighbourhood'
  ],
  parallelLimit: 3, // Limit concurrent requests
  timeoutPerSource: 30, // 30 seconds per service
  retryFailed: false, // Already has retry in services
  cacheResults: true, // Speed up repeated enrichments
};
```

---

## 📊 DATA STRUCTURE

### FSA Enrichment
```json
{
  "source": "fsa",
  "status": "success",
  "data": {
    "fsa_rating": 5,
    "rating_label": "Very Good",
    "rating_color": "#00AA00",
    "last_inspection": "2024-01-15",
    "hygiene_score": 4.5,
    "structural_score": 4.0,
    "confidence_in_management_score": 5.0
  }
}
```

### Financial Enrichment
```json
{
  "source": "financial",
  "status": "success",
  "data": {
    "altman_z_score": 8.5,
    "bankruptcy_risk": 0.02,
    "financial_health": "stable",
    "last_accounts_date": "2024-03-31",
    "revenue": 5000000,
    "profit": 250000
  }
}
```

### Google Places Enrichment
```json
{
  "source": "google",
  "status": "success",
  "data": {
    "google_rating": 4.8,
    "review_count": 125,
    "top_reviews": [...],
    "photos": [...],
    "popular_times": {...}
  }
}
```

### Staff Enrichment
```json
{
  "source": "staff",
  "status": "success",
  "data": {
    "staff_quality": "high",
    "glassdoor_rating": 4.2,
    "staff_turnover": 0.15,
    "average_tenure_years": 4.5,
    "reviews_count": 42
  }
}
```

### CQC Enrichment
```json
{
  "source": "cqc",
  "status": "success",
  "data": {
    "cqc_rating": "Good",
    "rating_date": "2024-06-01",
    "inspection_history": [...],
    "enforcement_actions": [],
    "regulated_activities": ["Accommodation for persons with mental health needs"]
  }
}
```

### Neighbourhood Enrichment
```json
{
  "source": "neighbourhood",
  "status": "success",
  "data": {
    "walkability_score": 7.5,
    "amenities": {
      "schools": [...],
      "hospitals": [...],
      "transport": [...]
    },
    "crime_index": 2.3,
    "green_space_score": 8.1
  }
}
```

---

## ⚠️ ERROR HANDLING

### Graceful Degradation
```typescript
// If an enrichment service fails, others continue
const enrichedHome = await orchestrator.enrichHome(home, config);

// Check which services succeeded
console.log('Used sources:', enrichedHome.metadata.sourcesUsed);
console.log('Failed sources:', enrichedHome.metadata.sourcesFailed);
console.log('Errors:', enrichedHome.metadata.errors);

// Use available data, skip failed sources
if (enrichedHome.enrichments.fsa) {
  // Use FSA data
}

if (!enrichedHome.enrichments.financial) {
  // Financial enrichment failed, use fallback
}
```

### Error Categories
```
1. API Errors (401, 429, 500)
   → Logged, retry attempted
   → Service marked as failed
   → Other services continue
   
2. Timeout Errors (>timeout limit)
   → Logged as timeout
   → Partial data returned if available
   → Service marked as failed
   
3. Missing API Keys
   → Service skipped at initialization
   → Feature flag disabled
   → Clear log message
   
4. Network Errors
   → Retry mechanism activates
   → Logged with context
   → Service marked as failed after retries
```

---

## 📈 MONITORING & LOGGING

### Log Levels

```
✅ SUCCESS (debug level)
  "enrichment completed (4500ms)"

🐌 SLOW (info level)
  "slow enrichment (8200ms, 82% of timeout)"

⏱️ WARNING (warn level)
  "approaching timeout (28500ms, 95%)"

❌ ERROR (error level)
  "failed/timeout (30000ms)"
```

### Accessing Logs
```typescript
import { createLogger } from '@/lib/shared/utils/logger';

const logger = createLogger({ module: 'MyComponent' });

// Logs appear in:
// - Browser console (dev environment)
// - Server logs (via Pino)
// - Structured logs (JSON format)
```

---

## 🚀 PERFORMANCE TIPS

### Caching Strategy
```typescript
// Cache enabled (recommended)
config.cacheResults = true

// First call: ~25-30 seconds
const result1 = await orchestrator.enrichHome(home, config);

// Same home: ~10ms (from cache)
const result2 = await orchestrator.enrichHome(home, config);

// Different home: ~25-30 seconds (no cache)
const result3 = await orchestrator.enrichHome(otherHome, config);
```

### Batch vs Single
```typescript
// Single home: Use for one-off enrichments
await orchestrator.enrichHome(home, config);

// Batch: Use for multiple homes (parallel processing)
// 5 homes in ~30s (parallel), NOT ~100s (sequential)
await orchestrator.enrichHomesBatch(homes, config);
```

### Memory Considerations
```typescript
// Cache is bounded to 1000 entries (~500MB max)
// No memory leaks, safe for long-running processes

// If you want to clear cache between sessions
orchestrator.clearCache();

// Get current cache size
const stats = orchestrator.getStats();
console.log('Cache entries:', stats.cacheSize); // 0-1000
```

---

## 🧪 TESTING IN YOUR COMPONENT

```typescript
// Test enrichment integration
it('should enrich homes with all services', async () => {
  const orchestrator = new EnrichmentOrchestrator();
  const home = createMockHome();
  
  const config = {
    enabledSources: ['fsa', 'financial', 'google', 'staff', 'cqc', 'neighbourhood'],
    parallelLimit: 3,
    timeoutPerSource: 30,
    retryFailed: false,
    cacheResults: true,
  };
  
  const enriched = await orchestrator.enrichHome(home, config);
  
  expect(enriched.metadata.sourcesUsed).toHaveLength(6);
  expect(enriched.metadata.errors).toHaveLength(0);
  expect(enriched.enrichments.fsa).toBeDefined();
  // ... test other services
});
```

---

## ✅ INTEGRATION CHECKLIST

- [ ] Import EnrichmentOrchestrator in your component
- [ ] Configure EnrichmentConfig with your settings
- [ ] Add API keys to environment variables
- [ ] Enable feature flags as needed
- [ ] Add progress callback for UX
- [ ] Handle error cases gracefully
- [ ] Display enrichment status to user
- [ ] Test with mock data first
- [ ] Test with real API keys
- [ ] Monitor performance metrics
- [ ] Set up logging in production

---

## 📞 SUPPORT & DEBUGGING

### Common Issues

**1. Service not registered**
```
Check: Feature flag enabled?
Check: API key configured?
Check: Environment variables loaded?
```

**2. Enrichment timing out**
```
Check: API is accessible?
Check: Network connectivity?
Increase: timeoutPerSource to 45+ seconds
```

**3. Memory growing**
```
Check: Cache clearing logic?
Check: LRU eviction working?
Monitor: getStats().cacheSize
```

**4. Partial enrichment**
```
This is expected behavior!
Check: metadata.errors for details
Use: Available data, skip failed sources
```

---

## 🎯 NEXT STEPS

1. **Review this guide** - Understand integration points
2. **Copy examples** - Use provided code snippets
3. **Test locally** - With mock data first
4. **Integrate** - Into your UI component
5. **Test with APIs** - Verify real data flows
6. **Monitor** - Watch logs and performance
7. **Deploy** - To production

---

**Ready to integrate?** Let me know when you're starting Day 5 UI integration work!

See also:
- [DAYS_3_4_VALIDATION_REPORT.md](./DAYS_3_4_VALIDATION_REPORT.md) - Validation results
- [lib/data-engine/enrichment/](./lib/data-engine/enrichment/) - Source code
- [lib/reports/professional-report/](./lib/reports/professional-report/) - Integration example
