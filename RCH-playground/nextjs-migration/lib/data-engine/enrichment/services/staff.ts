/**
 * Staff Enrichment Service
 * Enriches care homes with staff quality data
 * 
 * Uses multiple sources:
 * - Glassdoor (employee reviews and ratings)
 * - LinkedIn (employee profiles and company data)
 * - Job Boards (job postings and requirements)
 * - Perplexity AI (comprehensive research)
 */

import { CareHome } from '@/lib/shared/types/care-home';
import { BaseEnrichmentService } from '../base-enrichment';
import {
  EnrichmentResult,
  EnrichmentContext,
  EnrichmentOptions,
} from '../types';
import {
  StaffDataClient,
  GlassdoorData,
  LinkedInData,
  JobBoardData,
  PerplexityResearchResult,
} from './staff-client';

export interface StaffEnrichmentData {
  employee_satisfaction: {
    glassdoor_rating: number | null;
    glassdoor_reviews_count: number;
    work_life_balance: number | null;
    management_rating: number | null;
    overall_satisfaction: number | null; // 0-5
  };
  staff_retention: {
    turnover_rate: number | null; // % per year
    average_tenure: number | null; // years
    retention_trend: 'improving' | 'stable' | 'declining' | null;
  };
  qualifications: {
    rn_count: number | null; // Registered Nurses
    certified_staff_percentage: number | null; // 0-100
    training_programs: string[];
  };
  combined_analysis: {
    employee_satisfaction_rating: number | null; // 0-5
    turnover_rate_percent: number | null;
    average_tenure_years: number | null;
    staff_quality_score: number | null; // 0-100
    staff_quality_category: 'excellent' | 'good' | 'adequate' | 'concerning' | 'poor' | null;
  };
  summary: {
    status: 'available' | 'not_available' | 'partial';
    data_quality: 'high' | 'medium' | 'low';
    sources: string[];
  };
}

export class StaffEnrichmentService extends BaseEnrichmentService {
  serviceName = 'staff';
  private staffDataClient: StaffDataClient;
  private cacheTTL: number = 7 * 24 * 60 * 60 * 1000; // 7 days

  constructor(options: EnrichmentOptions = {}) {
    super(options);

    // Staff enrichment timeout (30 seconds - может быть долгим из-за Perplexity)
    const timeout = options.timeout || 30000;
    const perplexityApiKey = process.env.PERPLEXITY_API_KEY;
    const usePerplexity = process.env.USE_PERPLEXITY_FOR_STAFF !== 'false';

    this.staffDataClient = new StaffDataClient(perplexityApiKey, usePerplexity);

    // Staff data cache TTL = 7 days (данные обновляются реже)
    if (options.cacheTTL) {
      this.cacheTTL = options.cacheTTL;
    }

    // Initialize logger after serviceName is set
    this.initLogger();
  }

  /**
   * Обогатить care home данными о персонале
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
        this.logger.debug('Staff enrichment disabled by feature flag');
        return this.createErrorResult('Staff enrichment disabled by feature flag');
      }

      // Получить cache key
      const cacheKey = this.getCacheKey(home, 'staff');

      // Проверить кэш
      if (this.cache) {
        const cacheKeyFull = `enrichment:${this.serviceName}:${cacheKey}`;
        const cached = this.cache.get<StaffEnrichmentData>(cacheKeyFull);

        if (cached) {
          const processingTime = Date.now() - startTime;
          const result = this.createCachedResult(cached, processingTime);
          this.logComplete(result, home);
          return result;
        }
      }

      // Извлечь данные для поиска
      const homeName = home.name;
      const providerName = (home as any).provider_name || homeName;
      const locationId = (home as any).cqc_location_id;
      const companiesHouseData = context?.params?.companies_house_data;

      if (!homeName) {
        throw new Error('Home name is required for Staff enrichment');
      }

      // Получить данные из разных источников (параллельно)
      const [glassdoorData, linkedinData, jobBoardData, researchData] =
        await Promise.allSettled([
          this.withRetry(
            () => this.staffDataClient.getGlassdoorData(providerName),
            { maxAttempts: 2 }
          ),
          this.withRetry(
            () => this.staffDataClient.getLinkedInData(providerName),
            { maxAttempts: 2 }
          ),
          this.withRetry(
            () => this.staffDataClient.getJobBoardData(providerName),
            { maxAttempts: 2 }
          ),
          this.withRetry(
            () =>
              this.staffDataClient.getComprehensiveResearch(
                providerName,
                locationId,
                companiesHouseData
              ),
            { maxAttempts: 2 }
          ),
        ]);

      const glassdoor =
        glassdoorData.status === 'fulfilled' ? glassdoorData.value : null;
      const linkedin =
        linkedinData.status === 'fulfilled' ? linkedinData.value : null;
      const jobBoards =
        jobBoardData.status === 'fulfilled' ? jobBoardData.value : null;
      const research =
        researchData.status === 'fulfilled' ? researchData.value : null;

      // Объединить данные из всех источников
      const enrichmentData = this.combineStaffData(
        glassdoor,
        linkedin,
        jobBoards,
        research
      );

      // Сохранить в кэш
      if (this.cache) {
        const cacheKeyFull = `enrichment:${this.serviceName}:${cacheKey}`;
        this.cache.set(cacheKeyFull, enrichmentData, this.cacheTTL);
      }

      const processingTime = Date.now() - startTime;
      const sources = [];
      if (glassdoor) sources.push('glassdoor');
      if (linkedin) sources.push('linkedin');
      if (jobBoards) sources.push('job_boards');
      if (research) sources.push('perplexity');

      const result = this.createSuccessResult(
        enrichmentData,
        {
          sources,
          dataQuality: this.determineDataQuality(enrichmentData),
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
   * Объединить данные из всех источников
   */
  private combineStaffData(
    glassdoor: GlassdoorData | null,
    linkedin: LinkedInData | null,
    jobBoards: JobBoardData | null,
    research: PerplexityResearchResult | null
  ): StaffEnrichmentData {
    // Employee Satisfaction
    const glassdoorRating = glassdoor?.rating || research?.employee_satisfaction?.rating || null;
    const workLifeBalance = glassdoor?.work_life_balance || null;
    const managementRating = glassdoor?.management_rating || null;

    // Staff Retention
    const turnoverRate =
      research?.staff_retention?.turnover_rate || null;
    const averageTenure =
      research?.staff_retention?.average_tenure || null;
    const retentionTrend = research?.staff_retention?.trend || null;

    // Qualifications
    const trainingPrograms = research?.qualifications?.training_programs || [];
    const certifications = research?.qualifications?.certifications || [];

    // Combined Analysis
    const employeeSatisfactionRating = glassdoorRating;
    const staffQualityScore = this.calculateStaffQualityScore(
      glassdoorRating,
      turnoverRate,
      averageTenure
    );
    const staffQualityCategory = this.determineStaffQualityCategory(
      staffQualityScore
    );

    // Определить статус
    let status: StaffEnrichmentData['summary']['status'] = 'available';
    if (!glassdoorRating && !turnoverRate && !averageTenure) {
      status = 'not_available';
    } else if (!glassdoorRating || !turnoverRate) {
      status = 'partial';
    }

    return {
      employee_satisfaction: {
        glassdoor_rating: glassdoorRating,
        glassdoor_reviews_count: glassdoor?.reviews_count || 0,
        work_life_balance: workLifeBalance,
        management_rating: managementRating,
        overall_satisfaction: glassdoorRating,
      },
      staff_retention: {
        turnover_rate: turnoverRate,
        average_tenure: averageTenure,
        retention_trend: retentionTrend,
      },
      qualifications: {
        rn_count: null, // Требует дополнительного анализа
        certified_staff_percentage: null, // Требует дополнительного анализа
        training_programs: trainingPrograms,
      },
      combined_analysis: {
        employee_satisfaction_rating: employeeSatisfactionRating,
        turnover_rate_percent: turnoverRate,
        average_tenure_years: averageTenure,
        staff_quality_score: staffQualityScore,
        staff_quality_category: staffQualityCategory,
      },
      summary: {
        status,
        data_quality: this.determineDataQuality({
          glassdoor_rating: glassdoorRating,
          turnover_rate: turnoverRate,
          average_tenure: averageTenure,
        } as any),
        sources: [
          ...(glassdoor ? ['glassdoor'] : []),
          ...(linkedin ? ['linkedin'] : []),
          ...(jobBoards ? ['job_boards'] : []),
          ...(research ? ['perplexity'] : []),
        ],
      },
    };
  }

  /**
   * Рассчитать общий score качества персонала (0-100)
   */
  private calculateStaffQualityScore(
    glassdoorRating: number | null,
    turnoverRate: number | null,
    averageTenure: number | null
  ): number | null {
    if (!glassdoorRating && !turnoverRate && !averageTenure) {
      return null;
    }

    let score = 0;
    let factors = 0;

    // Glassdoor rating (0-5) -> 0-50 points
    if (glassdoorRating !== null) {
      score += (glassdoorRating / 5) * 50;
      factors++;
    }

    // Turnover rate (lower is better) -> 0-30 points
    if (turnoverRate !== null) {
      // <10% = 30, 10-20% = 20, 20-30% = 10, >30% = 0
      if (turnoverRate < 10) {
        score += 30;
      } else if (turnoverRate < 20) {
        score += 20;
      } else if (turnoverRate < 30) {
        score += 10;
      }
      factors++;
    }

    // Average tenure (higher is better) -> 0-20 points
    if (averageTenure !== null) {
      // >3 years = 20, 2-3 years = 15, 1-2 years = 10, <1 year = 5
      if (averageTenure >= 3) {
        score += 20;
      } else if (averageTenure >= 2) {
        score += 15;
      } else if (averageTenure >= 1) {
        score += 10;
      } else {
        score += 5;
      }
      factors++;
    }

    // Нормализовать по количеству факторов
    if (factors === 0) {
      return null;
    }

    return Math.round((score / factors) * 2); // Scale to 0-100
  }

  /**
   * Определить категорию качества персонала
   */
  private determineStaffQualityCategory(
    score: number | null
  ): StaffEnrichmentData['combined_analysis']['staff_quality_category'] {
    if (score === null) {
      return null;
    }

    if (score >= 80) {
      return 'excellent';
    } else if (score >= 65) {
      return 'good';
    } else if (score >= 50) {
      return 'adequate';
    } else if (score >= 35) {
      return 'concerning';
    } else {
      return 'poor';
    }
  }

  /**
   * Определить качество данных
   */
  private determineDataQuality(data: any): 'high' | 'medium' | 'low' {
    const hasRating = data.glassdoor_rating !== null;
    const hasTurnover = data.turnover_rate !== null;
    const hasTenure = data.average_tenure !== null;

    if (hasRating && hasTurnover && hasTenure) {
      return 'high';
    } else if (hasRating || hasTurnover) {
      return 'medium';
    } else {
      return 'low';
    }
  }
}



