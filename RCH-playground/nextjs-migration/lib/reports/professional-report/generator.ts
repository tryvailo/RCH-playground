/**
 * Professional Report Generator
 * Orchestrates the professional report generation process
 * Ported from Python services/report_generation/assembler.py
 */

import { DataLoader } from '@/lib/data-engine/core/data-loader';
import { DataValidator } from '@/lib/data-engine/core/data-validator';
import { DataCache } from '@/lib/data-engine/core/data-cache';
import { EnrichmentOrchestrator, EnrichmentConfig } from '@/lib/data-engine/enrichment/orchestrator';
import { ProfessionalMatchingService } from './matching/service';
import { SelectionService } from './matching/selection';
import { ReasoningGenerator } from './matching/reasoning';
import { createLogger } from '@/lib/shared/utils/logger';
import { retry } from '@/lib/shared/utils/retry';
import {
  ProfessionalReportQuestionnaire,
  ProfessionalReportResponse,
} from './types';

export class ProfessionalReportGenerator {
  private dataLoader: DataLoader;
  private dataValidator: DataValidator;
  private dataCache: DataCache;
  private enrichmentOrchestrator: EnrichmentOrchestrator;
  private matchingService: ProfessionalMatchingService;
  private selectionService: SelectionService;
  private reasoningGenerator: ReasoningGenerator;
  private logger = createLogger({ module: 'ProfessionalReportGenerator' });

  constructor() {
    this.dataLoader = new DataLoader();
    this.dataValidator = new DataValidator();
    this.dataCache = new DataCache(3600000); // 1 hour TTL
    this.enrichmentOrchestrator = new EnrichmentOrchestrator();
    this.matchingService = new ProfessionalMatchingService();
    this.selectionService = new SelectionService();
    this.reasoningGenerator = new ReasoningGenerator();
  }

  /**
   * Generate professional report
   * 
   * @param questionnaire User questionnaire
   * @returns Professional report response
   */
  async generate(
    questionnaire: ProfessionalReportQuestionnaire
  ): Promise<ProfessionalReportResponse> {
    const reportId = crypto.randomUUID();
    const logger = this.logger.child({ reportId });

    try {
      logger.info('Starting professional report generation');

      // LOW FIX #11: Full questionnaire validation
      if (!questionnaire) {
        throw new Error('Questionnaire is required');
      }

      // LOW FIX #11: Validate required sections and fields
      const locationBudget = questionnaire.section_2_location_budget || {};
      const medicalNeeds = questionnaire.section_3_medical_needs || {};
      const postcode = locationBudget.q4_postcode || '';
      const preferredCity = locationBudget.q5_preferred_city || '';

      // LOW FIX #11: Validate postcode is provided and not empty
      if (!postcode || postcode.trim().length === 0) {
        throw new Error('Postcode (q4_postcode) is required for professional report generation');
      }

      // LOW FIX #11: Validate medical needs data exists
      const careTypes = medicalNeeds.q8_care_types || [];
      if (!Array.isArray(careTypes)) {
        throw new Error('Invalid care types format in section_3_medical_needs.q8_care_types');
      }

      // 3. Resolve location (with retry)
      let postcodeInfo;
      try {
        postcodeInfo = await retry(
          () => this.dataLoader.resolvePostcode(postcode),
          { maxAttempts: 3, initialDelay: 1000 }
        );
        
        // LOW FIX #11: Validate postcode resolution returned valid coordinates
        if (!postcodeInfo.latitude || !postcodeInfo.longitude) {
          throw new Error('Postcode resolution did not return valid coordinates');
        }
        
        logger.info({ localAuthority: postcodeInfo.localAuthority }, 'Postcode resolved');
      } catch (error) {
        logger.error({ error, postcode }, 'Failed to resolve postcode');
        throw new Error(`Failed to resolve postcode: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }

      const userLat = postcodeInfo.latitude;
      const userLon = postcodeInfo.longitude;

      // 4. Determine care type (careTypes already defined above)
      const careType = this.determineCareType(careTypes);

      // 5. Load care homes (with retry)
      let homes;
      try {
        homes = await retry(
          () => this.dataLoader.loadCareHomes({
            localAuthority: postcodeInfo.localAuthority,
            careType,
            userLat,
            userLon,
            maxDistanceKm: 50, // Professional report uses larger radius
            limit: 50,
          }),
          { maxAttempts: 2, initialDelay: 500 }
        );
        logger.info({ count: homes.length }, 'Care homes loaded');
      } catch (error) {
        logger.error({ error }, 'Failed to load care homes');
        throw new Error(`Failed to load care homes: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }

      // 6. Validate homes
      const validation = this.dataValidator.validateHomes(homes);
      const validHomes = validation.data || [];
      if (validHomes.length === 0) {
        logger.warn('No valid homes found after validation');
      }

      // 7. Enrich homes (parallel) - using Data Engine EnrichmentOrchestrator
      let enrichedResults;
      try {
        const enrichmentConfig: EnrichmentConfig = {
          enabledSources: ['fsa', 'financial', 'google', 'staff', 'cqc', 'neighbourhood'],
          parallelLimit: 5,
          timeoutPerSource: 30, // seconds
          retryFailed: false,
          cacheResults: true,
        };

        const enrichedHomes = await this.enrichmentOrchestrator.enrichHomesBatch(
          validHomes,
          enrichmentConfig,
          {
            questionnaire,
            params: {
              userLat,
              userLon,
              postcode,
            },
          },
          (progress, message) => {
            logger.debug({ progress, message }, 'Enrichment progress');
          }
        );

        // HIGH FIX #5: Convert to old format for compatibility while preserving ALL metadata
        enrichedResults = enrichedHomes.map((enriched) => ({
          home: enriched.home,
          enrichments: enriched.enrichments,
          metadata: {
            enrichedAt: new Date().toISOString(),
            sources: enriched.metadata.sourcesUsed,
            sourcesFailed: enriched.metadata.sourcesFailed,  // Preserve failed sources
            errors: enriched.metadata.errors.length > 0 ? enriched.metadata.errors : undefined,
            enrichmentTime: enriched.metadata.enrichmentTime,
            // HIGH FIX #5: Preserve original metadata structure for traceability
            originalMetadata: enriched.metadata,
          },
        }));

        logger.info({ count: enrichedResults.length }, 'Homes enriched');
      } catch (error) {
        logger.error({ error }, 'Enrichment failed');
        // Continue with empty enrichments rather than failing completely
        enrichedResults = validHomes.map((home) => ({
          home,
          enrichments: {},
          metadata: {
            enrichedAt: new Date().toISOString(),
            sources: [],
            errors: [error instanceof Error ? error.message : String(error)],
          },
        }));
      }

      // 8. Match homes (156-point algorithm)
    const scoredHomes = await this.matchingService.matchHomes(
      enrichedResults.map((r) => ({ ...r.home, enrichments: r.enrichments })),
      questionnaire
    );

      // 9. Select top 5 with diversity
    // HIGH FIX #5: Preserve enrichment metadata alongside enrichments
    const enrichedMap: Record<string, any> = {};
    const metadataMap: Record<string, any> = {};
    for (const enriched of enrichedResults) {
      const homeId =
        enriched.home.cqc_location_id ||
        enriched.home.id ||
        enriched.home.name;
      enrichedMap[homeId] = enriched.enrichments;
      metadataMap[homeId] = enriched.metadata;  // Preserve metadata for traceability
    }

    const selectionResult = await this.selectionService.selectTop5(
      scoredHomes,
      questionnaire,
      enrichedMap
    );

      // 10. Generate reasoning for each
    // HIGH FIX #5: Include enrichment metadata in response for traceability
    const top5WithReasoning = selectionResult.top_5.map((item, index) => {
      const homeId =
        item.home.cqc_location_id || item.home.id || item.home.name;
      const enriched = enrichedMap[homeId] || {};
      const enrichmentMetadata = metadataMap[homeId];

      const reasoning = this.reasoningGenerator.generateReasoning(
        item.home,
        item.category,
        questionnaire,
        enriched,
        item
      );

      return {
        rank: index + 1,
        home: {
          id: item.home.cqc_location_id || item.home.id,
          name: item.home.name,
          location: item.home.city || item.home.local_authority,
          distance_km: item.home.distance_km || item.home.distanceKm,
          rating: item.home.rating || item.home.cqc_rating_overall,
          price_weekly: item.home.weekly_price || item.home.weeklyCost,
          care_types: item.home.care_types || item.home.careTypes || [],
        },
        match: {
          score: item.score,
          normalized: Math.round((item.score / 156) * 100),
          category_scores: item.categoryScores,
          point_allocations: item.categoryScores, // Simplified
        },
        reasoning,
        category: item.category,
        // HIGH FIX #5: Include enrichment metadata for debugging/audit trail
        enrichmentMetadata: enrichmentMetadata ? {
          sources: enrichmentMetadata.sources,
          sourcesFailed: enrichmentMetadata.sourcesFailed,
          enrichmentTime: enrichmentMetadata.enrichmentTime,
          errors: enrichmentMetadata.errors,
        } : undefined,
      };
    });

      // 11. Build response
      const response: ProfessionalReportResponse = {
        summary: {
          generated_at: new Date().toISOString(),
          user_location: this.getUserLocation(questionnaire),
          care_type: this.getCareType(questionnaire),
          total_homes_evaluated: scoredHomes.length,
          diversity: selectionResult.diversity_metrics,
        },
        matching: {
          top_5: top5WithReasoning,
          category_winners: selectionResult.category_winners,
        },
        questionnaire,
        report_id: reportId,
      };

      logger.info({
        reportId,
        homesEvaluated: scoredHomes.length,
        top5Count: top5WithReasoning.length,
      }, 'Professional report generated successfully');

      return response;
    } catch (error) {
      logger.error({
        error: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
      }, 'Professional report generation failed');
      throw error;
    }
  }

  /**
   * Determine care type from questionnaire
   */
  private determineCareType(careTypes: string[]): string {
    if (careTypes.includes('specialised_dementia')) return 'dementia';
    if (careTypes.includes('nursing') || careTypes.includes('general_nursing'))
      return 'nursing';
    if (careTypes.includes('general_residential')) return 'residential';
    return 'residential'; // Default
  }

  /**
   * Get user location string
   */
  private getUserLocation(questionnaire: ProfessionalReportQuestionnaire): string {
    const locationBudget = questionnaire.section_2_location_budget || {};
    const postcode = locationBudget.q4_postcode || '';
    const city = locationBudget.q5_preferred_city || '';

    if (postcode && city) {
      return `${postcode} (${city})`;
    }
    if (postcode) return postcode;
    if (city) return city;
    return 'Not specified';
  }

  /**
   * Get care type string
   */
  private getCareType(questionnaire: ProfessionalReportQuestionnaire): string {
    const medicalNeeds = questionnaire.section_3_medical_needs || {};
    const careTypes = medicalNeeds.q8_care_types || [];

    const careTypeLabels: Record<string, string> = {
      specialised_dementia: 'Dementia Care',
      nursing: 'Nursing Care',
      general_nursing: 'Nursing Care',
      general_residential: 'Residential Care',
    };

    for (const careType of careTypes) {
      if (careType in careTypeLabels) {
        return careTypeLabels[careType];
      }
    }

    return 'Residential Care';
  }
}

