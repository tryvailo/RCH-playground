/**
 * Data Engine Core
 * Main exports for Data Engine core modules
 */

export { DataLoader } from './data-loader';
export { DataEnricher } from './data-enricher';
export { DataMatcher } from './data-matcher';
export { DataValidator } from './data-validator';
export { DataCache } from './data-cache';

export type { DataLoaderConfig } from './data-loader';
export type { EnrichmentConfig, EnrichmentResult } from './data-enricher';
export type { MatchingConfig, ScoredHome } from './data-matcher';

// Enrichment module
export * from '../enrichment';

