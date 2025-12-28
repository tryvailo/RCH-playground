/**
 * Free Report Generator
 * Orchestrates the report generation process
 * Ported from Python services/free_report_generator_service.py
 */

import { DataLoader } from '@/lib/data-engine/core/data-loader';
import { DataValidator } from '@/lib/data-engine/core/data-validator';
import { DataCache } from '@/lib/data-engine/core/data-cache';
import { extractWeeklyPrice } from '@/lib/data-engine/utils/price-extractor';
import { FreeReportMatchingService, getFreeReportMatchingService } from './matching-service';
import { FairCostGapService, getFairCostGapService } from './fair-cost-gap';
import { createLogger } from '@/lib/shared/utils/logger';
import { retry } from '@/lib/shared/utils/retry';
import {
  FreeReportRequest,
  FreeReportResponse,
  FreeReportCareHome,
  MatchedHomes,
} from './types';

export class FreeReportGenerator {
  private dataLoader: DataLoader;
  private dataValidator: DataValidator;
  private dataCache: DataCache;
  private matchingService: FreeReportMatchingService;
  private fairCostGapService: FairCostGapService;
  private logger = createLogger({ module: 'FreeReportGenerator' });

  constructor() {
    this.dataLoader = new DataLoader();
    this.dataValidator = new DataValidator();
    this.dataCache = new DataCache(3600000); // 1 hour TTL
    this.matchingService = getFreeReportMatchingService();
    this.fairCostGapService = getFairCostGapService();
  }

  /**
   * Generate a free report
   * 
   * @param request Validated questionnaire request
   * @returns FreeReportResponse with complete report data
   */
  async generate(request: FreeReportRequest): Promise<FreeReportResponse> {
    const reportId = crypto.randomUUID();
    const logger = this.logger.child({ reportId, postcode: request.postcode });

    try {
      logger.info('Starting free report generation');

      // 1. Check cache
      const cacheKey = this.dataCache.generateKey('free-report', request);
      const cached = this.dataCache.get<FreeReportResponse>(cacheKey);
      if (cached) {
        logger.info({ cacheKey }, 'Returning cached report');
        return cached;
      }

      // 2. Validate questionnaire
      try {
        this.dataValidator.validateQuestionnaire(request);
      } catch (error) {
        logger.error({ error }, 'Questionnaire validation failed');
        throw new Error(`Invalid questionnaire: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }

      // 3. Resolve postcode (with retry)
      let postcodeInfo;
      try {
        postcodeInfo = await retry(
          () => this.dataLoader.resolvePostcode(request.postcode),
          { maxAttempts: 3, initialDelay: 1000 }
        );
        logger.info({ localAuthority: postcodeInfo.localAuthority }, 'Postcode resolved');
      } catch (error) {
        logger.error({ error, postcode: request.postcode }, 'Failed to resolve postcode');
        throw new Error(`Failed to resolve postcode: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }

      const localAuthority = postcodeInfo.localAuthority;
      const userLat = postcodeInfo.latitude;
      const userLon = postcodeInfo.longitude;

      // 4. Load care homes (with retry)
      let homes;
      try {
        homes = await retry(
          () => this.dataLoader.loadCareHomes({
            localAuthority,
            careType: request.care_type || 'residential',
            userLat,
            userLon,
            maxDistanceKm: request.max_distance_km || 30.0,
            limit: 50,
          }),
          { maxAttempts: 2, initialDelay: 500 }
        );
        logger.info({ count: homes.length }, 'Care homes loaded');
      } catch (error) {
        logger.error({ error }, 'Failed to load care homes');
        throw new Error(`Failed to load care homes: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }

      // 5. Validate homes
      const validation = this.dataValidator.validateHomes(homes);
      const validHomes = validation.data || [];
      if (validHomes.length === 0) {
        logger.warn('No valid homes found after validation');
      }

      // 6. Filter by quality
      const filteredHomes = this.filterByQuality(
        validHomes,
        request.care_type || 'residential'
      );
      logger.debug({ 
        before: validHomes.length, 
        after: filteredHomes.length 
      }, 'Homes filtered by quality');

      // 7. Matching (select top 3)
      const matched = this.matchingService.selectTop3Homes(
        filteredHomes,
        request.budget || 0,
        request.care_type || 'residential',
        userLat,
        userLon,
        request.max_distance_km || 30.0
      );
      logger.info({
        safeBet: !!matched.safe_bet,
        bestValue: !!matched.best_value,
        premium: !!matched.premium,
      }, 'Homes matched');

      // 8. Calculate Fair Cost Gap
      const fairCostGap = this.calculateFairCostGap(
        matched,
        request.care_type || 'residential',
        request.budget || 0
      );

      // 9. Format response
      const response: FreeReportResponse = {
        questionnaire: request,
        care_homes: this.formatMatchedHomes(
          matched,
          request.care_type || 'residential'
        ),
        fair_cost_gap: fairCostGap,
        area_profile: null, // Can be extended
        area_map: null, // Can be extended
        llm_insights: null, // Can be extended
        generated_at: new Date().toISOString(),
        report_id: reportId,
      };

      // 10. Cache response
      try {
        this.dataCache.set(cacheKey, response, 3600000); // 1 hour
      } catch (error) {
        logger.warn({ error }, 'Failed to cache response');
        // Don't fail if caching fails
      }

      logger.info({ 
        reportId,
        careHomesCount: response.care_homes.length 
      }, 'Free report generated successfully');

      return response;
    } catch (error) {
      logger.error({
        error: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
      }, 'Free report generation failed');
      throw error;
    }
  }

  /**
   * Filter homes by CQC quality rating
   */
  private filterByQuality(
    homes: any[],
    careType: string
  ): any[] {
    const filtered = homes.filter((h) => {
      const rating =
        h.cqc_rating_overall ||
        h.rating ||
        h.overall_cqc_rating ||
        h.cqcRating ||
        '';
      const ratingLower = rating.toLowerCase();
      return (
        ratingLower === 'good' || ratingLower === 'outstanding'
      );
    });

    return filtered.length > 0 ? filtered : homes;
  }

  /**
   * Calculate fair cost gap
   */
  private calculateFairCostGap(
    matched: MatchedHomes,
    careType: string,
    budget: number
  ): any {
    // Use average price from matched homes
    const prices: number[] = [];
    const homes = [matched.safe_bet, matched.best_value, matched.premium];

    for (const home of homes) {
      if (home) {
        const price = extractWeeklyPrice(home, careType as any);
        if (price > 0) {
          prices.push(price);
        }
      }
    }

    const marketPrice =
      prices.length > 0
        ? prices.reduce((sum, p) => sum + p, 0) / prices.length
        : budget || 1200.0;

    // Default MSIF values
    const msifDefaults: Record<string, number> = {
      residential: 700,
      nursing: 1048,
      dementia: 800,
      respite: 700,
    };
    const msifLowerBound = msifDefaults[careType] || 700;

    return this.fairCostGapService.calculateGap(
      marketPrice,
      msifLowerBound,
      careType
    );
  }

  /**
   * Format matched homes for response
   */
  private formatMatchedHomes(
    matched: MatchedHomes,
    careType: string
  ): FreeReportCareHome[] {
    const homes: FreeReportCareHome[] = [];

    const matchTypes: Array<['Safe Bet' | 'Best Value' | 'Premium', any]> = [
      ['Safe Bet', matched.safe_bet],
      ['Best Value', matched.best_value],
      ['Premium', matched.premium],
    ];

    for (const [matchType, home] of matchTypes) {
      if (home) {
        const formatted: FreeReportCareHome = {
          name: home.name || '',
          address: home.address,
          postcode: home.postcode || '',
          weekly_cost: extractWeeklyPrice(home, careType as any),
          rating:
            home.cqc_rating_overall ||
            home.rating ||
            home.cqcRating ||
            undefined,
          care_types: home.care_types || home.careTypes || [],
          distance_km: home.distance_km || home.distanceKm,
          match_type: matchType,
          photo_url: home.photo_url || home.photoUrl,
          fsa_rating: home.fsa_rating || home.fsaRating,
        };
        homes.push(formatted);
      }
    }

    return homes;
  }
}

