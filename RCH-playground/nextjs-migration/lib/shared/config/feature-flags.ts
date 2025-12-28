/**
 * Feature Flags
 * Centralized feature flag management
 */

export interface FeatureFlags {
  // Enrichment services
  enableFinancialEnrichment: boolean;
  enableStaffEnrichment: boolean;
  enableFSAEnrichment: boolean;
  enableGooglePlacesEnrichment: boolean;
  enrichmentFSA: boolean;
  enrichmentFinancial: boolean;
  enrichmentGooglePlaces: boolean;
  enrichmentStaff: boolean;
  enrichmentCQC: boolean;
  enrichmentNeighbourhood: boolean;

  // Data sources
  enableDatabaseSource: boolean;
  enableCSVSource: boolean;

  // Caching
  enableCaching: boolean;
  cacheTTL: number; // in milliseconds

  // Performance
  maxConcurrentEnrichments: number;
  enrichmentTimeout: number; // in milliseconds
}

/**
 * Get feature flags from environment variables
 */
export function getFeatureFlags(): FeatureFlags {
  const isDevelopment = process.env.NODE_ENV === 'development';

  return {
    // Enrichment services - can be enabled/disabled via env vars
    enableFinancialEnrichment:
      process.env.ENABLE_FINANCIAL_ENRICHMENT === 'true',
    enableStaffEnrichment: process.env.ENABLE_STAFF_ENRICHMENT === 'true',
    enableFSAEnrichment: process.env.ENABLE_FSA_ENRICHMENT === 'true',
    enableGooglePlacesEnrichment:
      process.env.ENABLE_GOOGLE_PLACES_ENRICHMENT === 'true',
    
    // New enrichment services (Data Engine)
    enrichmentFSA: process.env.ENABLE_FSA_ENRICHMENT !== 'false',
    enrichmentFinancial: process.env.ENABLE_FINANCIAL_ENRICHMENT !== 'false',
    enrichmentGooglePlaces: process.env.ENABLE_GOOGLE_PLACES_ENRICHMENT !== 'false',
    enrichmentStaff: process.env.ENABLE_STAFF_ENRICHMENT !== 'false',
    enrichmentCQC: process.env.ENABLE_CQC_ENRICHMENT !== 'false',
    enrichmentNeighbourhood: process.env.ENABLE_NEIGHBOURHOOD_ENRICHMENT !== 'false',

    // Data sources
    enableDatabaseSource: process.env.ENABLE_DATABASE_SOURCE !== 'false',
    enableCSVSource: process.env.ENABLE_CSV_SOURCE !== 'false',

    // Caching
    enableCaching: process.env.ENABLE_CACHING !== 'false',
    cacheTTL: parseInt(process.env.CACHE_TTL_MS || '3600000', 10), // 1 hour default

    // Performance
    maxConcurrentEnrichments: parseInt(
      process.env.MAX_CONCURRENT_ENRICHMENTS || '5',
      10
    ),
    enrichmentTimeout: parseInt(
      process.env.ENRICHMENT_TIMEOUT_MS || '30000',
      10
    ), // 30 seconds default
  };
}

/**
 * Singleton feature flags instance
 */
let featureFlags: FeatureFlags | null = null;

export function getFlags(): FeatureFlags {
  if (!featureFlags) {
    featureFlags = getFeatureFlags();
  }
  return featureFlags;
}

