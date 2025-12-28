/**
 * CQC Deep Dive Enrichment Service
 * Enriches care homes with comprehensive CQC data
 * 
 * Provides:
 * - Inspection history (5+ years)
 * - Enforcement actions (red flags)
 * - Provider-level pattern detection
 * - Rating trend calculation
 * - Regulated activities parsing
 */

import { CareHome } from '@/lib/shared/types/care-home';
import { BaseEnrichmentService } from '../base-enrichment';
import {
  EnrichmentResult,
  EnrichmentContext,
  EnrichmentOptions,
} from '../types';
import {
  CQCClient,
  CQCInspection,
  CQCEnforcementAction,
  CQCProviderLocation,
} from './cqc-client';

export interface RegulatedActivity {
  id: string; // e.g., "accommodation_nursing"
  name: string; // e.g., "Accommodation for persons who require nursing..."
  active: boolean;
  cqc_field: string; // Original CQC field name
}

export interface CQCDeepDiveData {
  // Current Ratings (6 domains)
  overall: string; // "Outstanding" / "Good" / "Requires improvement" / "Inadequate"
  safe: string;
  effective: string;
  caring: string;
  responsive: string;
  well_led: string;
  
  // Dates
  last_inspection_date: string | null;
  publication_date: string | null;
  report_url: string | null;
  
  // Regulated Activities
  regulated_activities: RegulatedActivity[];
  
  // Quick flags
  has_nursing_care_license: boolean;
  has_personal_care_license: boolean;
  has_surgical_procedures_license: boolean;
  has_treatment_license: boolean;
  has_diagnostic_license: boolean;
  
  // Derived
  days_since_inspection: number | null;
  rating_trend: 'Improving' | 'Stable' | 'Declining' | 'Insufficient data';
  
  // Enrichment from CQC API
  inspection_history: CQCInspection[]; // Full history 5+ years
  enforcement_actions: CQCEnforcementAction[]; // Warning notices, conditions
  provider_locations: CQCProviderLocation[] | null; // All provider locations for pattern detection
  
  summary: {
    status: 'available' | 'not_available' | 'partial';
    data_quality: 'high' | 'medium' | 'low';
    sources: string[];
  };
}

export class CQCDeepDiveEnrichmentService extends BaseEnrichmentService {
  serviceName = 'cqcDeepDive';
  private cqcClient: CQCClient;
  private cacheTTL: number = 7 * 24 * 60 * 60 * 1000; // 7 days

  constructor(options: EnrichmentOptions = {}) {
    super(options);

    // CQC API timeout (30 seconds)
    const timeout = options.timeout || 30000;
    const apiKey = process.env.CQC_API_KEY;
    this.cqcClient = new CQCClient(apiKey);

    // CQC data cache TTL = 7 days (данные обновляются реже)
    if (options.cacheTTL) {
      this.cacheTTL = options.cacheTTL;
    }

    // Initialize logger after serviceName is set
    this.initLogger();
  }

  /**
   * Обогатить care home данными CQC Deep Dive
   */
  async enrich(
    home: CareHome,
    context?: EnrichmentContext
  ): Promise<EnrichmentResult> {
    const startTime = Date.now();

    try {
      this.validateHome(home);
      this.logStart(home, context);

      // Проверить доступность
      if (!this.isAvailable()) {
        this.logger.debug('CQC Deep Dive enrichment disabled by feature flag');
        return this.createErrorResult('CQC Deep Dive enrichment disabled by feature flag');
      }

      // Получить cache key
      const cacheKey = this.getCacheKey(home, 'cqc-deep-dive');

      // Проверить кэш
      if (this.cache) {
        const cacheKeyFull = `enrichment:${this.serviceName}:${cacheKey}`;
        const cached = this.cache.get<CQCDeepDiveData>(cacheKeyFull);

        if (cached) {
          const processingTime = Date.now() - startTime;
          const result = this.createCachedResult(cached, processingTime);
          this.logComplete(result, home);
          return result;
        }
      }

      // Извлечь данные для поиска
      const locationId = (home as any).cqc_location_id || home.id;
      const providerId = (home as any).provider_id || (home as any).cqc_provider_id;

      if (!locationId) {
        throw new Error('CQC location ID is required for CQC Deep Dive enrichment');
      }

      // Получить базовые данные из home
      const overall = this.extractRating(home, 'overall') || this.extractRating(home, 'rating');
      const safe = this.extractRating(home, 'safe') || this.extractRating(home, 'cqc_rating_safe');
      const effective = this.extractRating(home, 'effective') || this.extractRating(home, 'cqc_rating_effective');
      const caring = this.extractRating(home, 'caring') || this.extractRating(home, 'cqc_rating_caring');
      const responsive = this.extractRating(home, 'responsive') || this.extractRating(home, 'cqc_rating_responsive');
      const wellLed = this.extractRating(home, 'well_led') || this.extractRating(home, 'cqc_rating_well_led');

      const lastInspectionDate = this.extractDate(home, 'last_inspection_date') || this.extractDate(home, 'inspection_date');
      const publicationDate = this.extractDate(home, 'publication_date');
      const reportUrl = (home as any).cqc_report_url || (home as any).report_url;

      // Парсить regulated activities
      const regulatedActivities = this.parseRegulatedActivities(
        (home as any).regulated_activities || (home as any).regulatedActivities
      );

      // Получить данные из CQC API (параллельно)
      const [inspectionHistory, enforcementActions, providerLocations] =
        await Promise.allSettled([
          this.withRetry(
            () => this.cqcClient.getLocationInspectionHistory(locationId),
            { maxAttempts: 2 }
          ),
          this.withRetry(
            () => this.cqcClient.getLocationEnforcementActions(locationId),
            { maxAttempts: 2 }
          ),
          providerId
            ? this.withRetry(
                () => this.cqcClient.getProviderLocations(providerId),
                { maxAttempts: 2 }
              )
            : Promise.resolve(null),
        ]);

      const inspections =
        inspectionHistory.status === 'fulfilled' ? inspectionHistory.value : [];
      const actions =
        enforcementActions.status === 'fulfilled' ? enforcementActions.value : [];
      const providerLocs =
        providerLocations.status === 'fulfilled' ? providerLocations.value : null;

      // Рассчитать rating trend
      const ratingTrend = this.calculateRatingTrend(overall || '', inspections);

      // Рассчитать days since inspection
      const daysSinceInspection = lastInspectionDate
        ? Math.floor(
            (Date.now() - new Date(lastInspectionDate).getTime()) /
              (1000 * 60 * 60 * 24)
          )
        : null;

      // Формировать enrichment данные
      const enrichmentData: CQCDeepDiveData = {
        overall: overall || 'Not rated',
        safe: safe || 'Not rated',
        effective: effective || 'Not rated',
        caring: caring || 'Not rated',
        responsive: responsive || 'Not rated',
        well_led: wellLed || 'Not rated',
        last_inspection_date: lastInspectionDate,
        publication_date: publicationDate,
        report_url: reportUrl,
        regulated_activities: regulatedActivities,
        has_nursing_care_license: this.hasLicense(regulatedActivities, 'nursing'),
        has_personal_care_license: this.hasLicense(regulatedActivities, 'personal'),
        has_surgical_procedures_license: this.hasLicense(regulatedActivities, 'surgical'),
        has_treatment_license: this.hasLicense(regulatedActivities, 'treatment'),
        has_diagnostic_license: this.hasLicense(regulatedActivities, 'diagnostic'),
        days_since_inspection: daysSinceInspection,
        rating_trend: ratingTrend,
        inspection_history: inspections,
        enforcement_actions: actions,
        provider_locations: providerLocs,
        summary: {
          status: this.determineStatus(overall, inspections, actions),
          data_quality: this.determineDataQuality(overall, inspections, actions),
          sources: [
            'database',
            ...(inspections.length > 0 ? ['cqc_api'] : []),
            ...(actions.length > 0 ? ['cqc_api'] : []),
            ...(providerLocs ? ['cqc_api'] : []),
          ],
        },
      };

      // Сохранить в кэш
      if (this.cache) {
        const cacheKeyFull = `enrichment:${this.serviceName}:${cacheKey}`;
        this.cache.set(cacheKeyFull, enrichmentData, this.cacheTTL);
      }

      const processingTime = Date.now() - startTime;
      const result = this.createSuccessResult(
        enrichmentData,
        {
          sources: enrichmentData.summary.sources,
          dataQuality: enrichmentData.summary.data_quality,
        },
        processingTime
      );

      this.logComplete(result, home);
      return result;
    } catch (error: unknown) {
      const processingTime = Date.now() - startTime;
      const errorObj = error instanceof Error ? error : new Error(String(error));
      this.logError(errorObj, home);

      // Если это timeout или network error, возвращаем partial result
      const errorMessage = error instanceof Error ? error.message : String(error);
      const lowerErrorMessage = errorMessage.toLowerCase();
      if (
        lowerErrorMessage.includes('timeout') ||
        lowerErrorMessage.includes('network') ||
        lowerErrorMessage.includes('econn')
      ) {
        return this.createPartialResult(
          {},
          errorMessage,
          {
            sources: [],
            dataQuality: 'low',
          },
          processingTime
        );
      }

      return this.createErrorResult(errorObj, processingTime);
    }
  }

  /**
   * Извлечь рейтинг из home объекта
   */
  private extractRating(home: CareHome, field: string): string | null {
    const value = (home as any)[field];
    if (!value) return null;
    
    const str = String(value).trim();
    if (!str || str === 'null' || str === 'undefined') return null;
    
    return str;
  }

  /**
   * Извлечь дату из home объекта
   */
  private extractDate(home: CareHome, field: string): string | null {
    const value = (home as any)[field];
    if (!value) return null;
    
    // Если это уже строка в формате ISO
    if (typeof value === 'string') {
      return value;
    }
    
    // Если это Date объект
    if (value instanceof Date) {
      return value.toISOString();
    }
    
    return null;
  }

  /**
   * Парсить regulated activities из JSONB или объекта
   */
  private parseRegulatedActivities(
    data: any
  ): RegulatedActivity[] {
    if (!data) return [];

    // Если это массив
    if (Array.isArray(data)) {
      return data.map((item) => ({
        id: item.id || item.key || '',
        name: item.name || item.value || '',
        active: item.active !== false,
        cqc_field: item.cqc_field || item.field || '',
      }));
    }

    // Если это объект
    if (typeof data === 'object') {
      return Object.keys(data).map((key) => ({
        id: key,
        name: data[key]?.name || key,
        active: data[key]?.active !== false,
        cqc_field: key,
      }));
    }

    return [];
  }

  /**
   * Проверить наличие лицензии
   */
  private hasLicense(
    activities: RegulatedActivity[],
    type: 'nursing' | 'personal' | 'surgical' | 'treatment' | 'diagnostic'
  ): boolean {
    const patterns = {
      nursing: /nursing|accommodation.*nursing/i,
      personal: /personal.*care|accommodation.*personal/i,
      surgical: /surgical|surgery/i,
      treatment: /treatment|diagnostic.*treatment/i,
      diagnostic: /diagnostic|diagnosis/i,
    };

    const pattern = patterns[type];
    return activities.some(
      (activity) =>
        activity.active && pattern.test(activity.id + ' ' + activity.name)
    );
  }

  /**
   * Рассчитать rating trend
   */
  private calculateRatingTrend(
    currentRating: string,
    inspectionHistory: CQCInspection[]
  ): 'Improving' | 'Stable' | 'Declining' | 'Insufficient data' {
    const RATING_ORDER: Record<string, number> = {
      Inadequate: 1,
      'Requires improvement': 2,
      Good: 3,
      Outstanding: 4,
    };

    if (inspectionHistory.length < 2) {
      return 'Insufficient data';
    }

    // Сортировать по дате (новые первые)
    const sorted = [...inspectionHistory].sort((a, b) => {
      const dateA = new Date(a.inspectionDate).getTime();
      const dateB = new Date(b.inspectionDate).getTime();
      return dateB - dateA;
    });

    const current = RATING_ORDER[currentRating] || 0;
    const previous = RATING_ORDER[sorted[1]?.overallRating || ''] || 0;

    if (current === 0 || previous === 0) {
      return 'Insufficient data';
    }

    if (current > previous) {
      return 'Improving';
    } else if (current < previous) {
      return 'Declining';
    } else {
      return 'Stable';
    }
  }

  /**
   * Определить статус данных
   */
  private determineStatus(
    overall: string | null,
    inspections: CQCInspection[],
    actions: CQCEnforcementAction[]
  ): 'available' | 'not_available' | 'partial' {
    if (!overall && inspections.length === 0 && actions.length === 0) {
      return 'not_available';
    }
    if (overall && (inspections.length > 0 || actions.length > 0)) {
      return 'available';
    }
    return 'partial';
  }

  /**
   * Определить качество данных
   */
  private determineDataQuality(
    overall: string | null,
    inspections: CQCInspection[],
    actions: CQCEnforcementAction[]
  ): 'high' | 'medium' | 'low' {
    if (overall && inspections.length >= 2 && actions.length >= 0) {
      return 'high';
    }
    if (overall && (inspections.length > 0 || actions.length > 0)) {
      return 'medium';
    }
    return 'low';
  }
}



