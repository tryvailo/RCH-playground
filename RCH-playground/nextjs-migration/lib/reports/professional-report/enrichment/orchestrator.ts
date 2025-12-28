/**
 * Enrichment Orchestrator
 * Coordinates all enrichment services for Professional Report
 * Ported from Python services/enrichment_orchestrator.py
 */

import { CareHome } from '@/lib/shared/types/care-home';
import { FinancialEnrichment } from './financial';
import { StaffEnrichment } from './staff';
import { FSAEnrichment } from './fsa';
import { GooglePlacesEnrichment } from './google-places';
import { getFlags } from '@/lib/shared/config/feature-flags';
import { createLogger } from '@/lib/shared/utils/logger';
import { retryWithTimeout } from '@/lib/shared/utils/retry';

export interface EnrichmentConfig {
  enableFinancial?: boolean;
  enableStaff?: boolean;
  enableFSA?: boolean;
  enableGooglePlaces?: boolean;
  parallel?: boolean;
  parallelLimit?: number;
  timeoutPerSource?: number;
  cacheResults?: boolean;
}

export interface EnrichmentResult {
  home: CareHome;
  enrichments: {
    financial?: any;
    staff?: any;
    fsa?: any;
    googlePlaces?: any;
  };
  metadata: {
    enrichedAt: string;
    sources: string[];
    errors?: string[];
    enrichmentTime?: number;
  };
}

export class EnrichmentOrchestrator {
  private financial: FinancialEnrichment;
  private staff: StaffEnrichment;
  private fsa: FSAEnrichment;
  private googlePlaces: GooglePlacesEnrichment;
  private cache: Map<string, EnrichmentResult> = new Map();
  private logger = createLogger({ module: 'EnrichmentOrchestrator' });
  private flags = getFlags();

  constructor() {
    this.financial = new FinancialEnrichment();
    this.staff = new StaffEnrichment();
    this.fsa = new FSAEnrichment();
    this.googlePlaces = new GooglePlacesEnrichment();
  }

  /**
   * Enrich single home
   * 
   * @param home Care home to enrich
   * @param config Enrichment configuration
   * @param context Additional context (questionnaire, etc.)
   * @returns Enrichment result
   */
  async enrichHome(
    home: CareHome,
    config: EnrichmentConfig,
    context?: any
  ): Promise<EnrichmentResult> {
    const homeId = (home as any).cqc_location_id || home.id || home.name;

    // Check cache
    if (config.cacheResults && this.cache.has(homeId)) {
      return this.cache.get(homeId)!;
    }

    const enrichments: any = {};
    const sources: string[] = [];
    const errors: string[] = [];
    const startTime = Date.now();

    // Parallel enrichment from different sources (with feature flags)
    const tasks: Promise<void>[] = [];
    const timeout = config.timeoutPerSource || this.flags.enrichmentTimeout;

    if (config.enableFinancial && this.flags.enableFinancialEnrichment) {
      tasks.push(
        retryWithTimeout(
          () => this.financial.enrich(home, context),
          timeout,
          { maxAttempts: 2 }
        )
          .then((data) => {
            enrichments.financial = data;
            sources.push('financial');
          })
          .catch((err) => {
            const errorMsg = err instanceof Error ? err.message : String(err);
            errors.push(`financial: ${errorMsg}`);
            this.logger.warn({ homeId, error: errorMsg }, 'Financial enrichment failed');
          })
      );
    } else if (config.enableFinancial) {
      this.logger.debug('Financial enrichment disabled by feature flag');
    }

    if (config.enableStaff && this.flags.enableStaffEnrichment) {
      tasks.push(
        retryWithTimeout(
          () => this.staff.enrich(home, context),
          timeout,
          { maxAttempts: 2 }
        )
          .then((data) => {
            enrichments.staff = data;
            sources.push('staff');
          })
          .catch((err) => {
            const errorMsg = err instanceof Error ? err.message : String(err);
            errors.push(`staff: ${errorMsg}`);
            this.logger.warn({ homeId, error: errorMsg }, 'Staff enrichment failed');
          })
      );
    } else if (config.enableStaff) {
      this.logger.debug('Staff enrichment disabled by feature flag');
    }

    if (config.enableFSA && this.flags.enableFSAEnrichment) {
      tasks.push(
        retryWithTimeout(
          () => this.fsa.enrich(home, context),
          timeout,
          { maxAttempts: 2 }
        )
          .then((data) => {
            enrichments.fsa = data;
            sources.push('fsa');
          })
          .catch((err) => {
            const errorMsg = err instanceof Error ? err.message : String(err);
            errors.push(`fsa: ${errorMsg}`);
            this.logger.warn({ homeId, error: errorMsg }, 'FSA enrichment failed');
          })
      );
    } else if (config.enableFSA) {
      this.logger.debug('FSA enrichment disabled by feature flag');
    }

    if (config.enableGooglePlaces && this.flags.enableGooglePlacesEnrichment) {
      tasks.push(
        retryWithTimeout(
          () => this.googlePlaces.enrich(home, context),
          timeout,
          { maxAttempts: 2 }
        )
          .then((data) => {
            enrichments.googlePlaces = data;
            sources.push('googlePlaces');
          })
          .catch((err) => {
            const errorMsg = err instanceof Error ? err.message : String(err);
            errors.push(`googlePlaces: ${errorMsg}`);
            this.logger.warn({ homeId, error: errorMsg }, 'Google Places enrichment failed');
          })
      );
    } else if (config.enableGooglePlaces) {
      this.logger.debug('Google Places enrichment disabled by feature flag');
    }

    await Promise.allSettled(tasks);

    const enrichmentTime = Date.now() - startTime;

    const result: EnrichmentResult = {
      home,
      enrichments,
      metadata: {
        enrichedAt: new Date().toISOString(),
        sources,
        errors: errors.length > 0 ? errors : undefined,
        enrichmentTime,
      },
    };

    // Cache result
    if (config.cacheResults) {
      this.cache.set(homeId, result);
    }

    return result;
  }

  /**
   * Batch enrich homes
   * 
   * @param homes Array of care homes
   * @param config Enrichment configuration
   * @param context Additional context
   * @param onProgress Optional progress callback
   * @returns Array of enrichment results
   */
  async enrichHomes(
    homes: CareHome[],
    config: EnrichmentConfig,
    context?: any,
    onProgress?: (progress: number, message: string) => void
  ): Promise<EnrichmentResult[]> {
    const results: EnrichmentResult[] = [];
    const total = homes.length;
    const parallelLimit = config.parallelLimit || 5;

    // Process in batches to limit concurrency
    for (let i = 0; i < homes.length; i += parallelLimit) {
      const batch = homes.slice(i, i + parallelLimit);
      const batchResults = await Promise.all(
        batch.map((home) => this.enrichHome(home, config, context))
      );
      results.push(...batchResults);

      if (onProgress) {
        const progress = Math.round(((i + batch.length) / total) * 100);
        onProgress(progress, `Enriched ${i + batch.length}/${total} homes`);
      }
    }

    return results;
  }

}

