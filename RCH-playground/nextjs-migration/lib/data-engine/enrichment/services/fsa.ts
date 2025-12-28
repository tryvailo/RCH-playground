/**
 * FSA Enrichment Service
 * Enriches care homes with Food Standards Agency (FSA) Food Hygiene Rating data
 * 
 * Uses FSA API to get food hygiene ratings, sub-scores, and inspection details
 */

import { CareHome } from '@/lib/shared/types/care-home';
import { BaseEnrichmentService } from '../base-enrichment';
import {
  EnrichmentResult,
  EnrichmentContext,
  EnrichmentOptions,
} from '../types';
import { FSAClient, FSADetailedData } from './fsa-client';

export class FSAEnrichmentService extends BaseEnrichmentService {
  serviceName = 'fsa';
  private fsaClient: FSAClient;
  private cacheTTL: number = 7 * 24 * 60 * 60 * 1000; // 7 days

  constructor(options: EnrichmentOptions = {}) {
    super(options);
    
    // FSA API timeout (10 seconds)
    const timeout = options.timeout || 10000;
    this.fsaClient = new FSAClient(timeout);
    
    // Initialize logger after serviceName is set
    this.initLogger();

    // FSA cache TTL = 7 days (FSA ratings обновляются редко)
    if (options.cacheTTL) {
      this.cacheTTL = options.cacheTTL;
    }
  }

  /**
   * Обогатить care home данными FSA
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
        this.logger.debug('FSA enrichment disabled by feature flag');
        return this.createErrorResult('FSA enrichment disabled by feature flag');
      }

      // Получить cache key
      const cacheKey = this.getCacheKey(home, 'fsa');

      // Проверить кэш
      if (this.cache) {
        const cacheKeyFull = `enrichment:${this.serviceName}:${cacheKey}`;
        const cached = this.cache.get<FSADetailedData>(cacheKeyFull);

        if (cached) {
          const processingTime = Date.now() - startTime;
          const result = this.createCachedResult(cached, processingTime);
          this.logComplete(result, home);
          return result;
        }
      }

      // Извлечь данные для поиска
      const homeName = home.name;
      const postcode = home.postcode;
      const latitude = home.latitude;
      const longitude = home.longitude;

      if (!homeName || !postcode) {
        throw new Error('Home name and postcode are required for FSA enrichment');
      }

      // Поиск бизнеса в FSA API (с retry)
      const business = await this.withRetry(
        () =>
          this.fsaClient.searchBusiness(
            homeName,
            postcode,
            latitude,
            longitude
          ),
        {
          maxAttempts: 3,
          initialDelay: 1000,
        }
      );

      if (!business) {
        // Бизнес не найден в FSA - это не ошибка, просто нет данных
        const processingTime = Date.now() - startTime;
        const result = this.createPartialResult(
          {},
          'Business not found in FSA database',
          {
            sources: [],
            dataQuality: 'low',
          },
          processingTime
        );
        this.logComplete(result, home);
        return result;
      }

      // Получить детальные данные
      const detailedData = await this.fsaClient.getDetailedData(business);

      // Сохранить в кэш
      if (this.cache) {
        const cacheKeyFull = `enrichment:${this.serviceName}:${cacheKey}`;
        this.cache.set(cacheKeyFull, detailedData, this.cacheTTL);
      }

      const processingTime = Date.now() - startTime;
      const result = this.createSuccessResult(
        detailedData,
        {
          sources: ['fsa_api'],
          dataQuality: detailedData.fsa_rating !== null ? 'high' : 'medium',
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
}

