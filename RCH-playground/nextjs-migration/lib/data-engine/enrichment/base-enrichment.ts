/**
 * Base Enrichment Service
 * Базовый класс для всех enrichment services в Data Engine
 */

import { CareHome } from '@/lib/shared/types/care-home';
import { createLogger, LogContext } from '@/lib/shared/utils/logger';
import { retry, RetryOptions } from '@/lib/shared/utils/retry';
import { DataCache } from '@/lib/data-engine/core/data-cache';
import { getFlags } from '@/lib/shared/config/feature-flags';
import {
  IEnrichmentService,
  EnrichmentResult,
  EnrichmentContext,
  EnrichmentOptions,
} from './types';

/**
 * Базовый класс для всех enrichment services
 */
export abstract class BaseEnrichmentService implements IEnrichmentService {
  /** Название service (должно быть переопределено) */
  abstract serviceName: string;

  /** Кэш для enrichment данных */
  protected cache?: DataCache;

  /** Логгер */
  protected logger: ReturnType<typeof createLogger>;

  /** Опции */
  protected options: Required<EnrichmentOptions>;

  /** Feature flags */
  protected flags = getFlags();

  constructor(options: EnrichmentOptions = {}) {
    this.options = {
      useCache: options.useCache ?? true,
      cacheTTL: options.cacheTTL ?? 3600000, // 1 hour default
      timeout: options.timeout ?? 30000, // 30 seconds default
      maxRetries: options.maxRetries ?? 2,
      retryDelay: options.retryDelay ?? 1000,
      logger: options.logger,
    };

    // Инициализация кэша
    if (this.options.useCache) {
      this.cache = new DataCache(this.options.cacheTTL);
    }

    // Инициализация логгера (будет обновлен после установки serviceName)
    this.logger = this.options.logger || createLogger({
      module: 'Enrichment:Base',
    });
  }

  /**
   * Инициализировать логгер с правильным serviceName
   * Должен быть вызван в конструкторе подкласса после установки serviceName
   */
  protected initLogger(): void {
    if (!this.options.logger) {
      this.logger = createLogger({
        module: `Enrichment:${this.serviceName}`,
      });
    }
  }

  /**
   * Обогатить care home
   * Должен быть реализован в подклассах
   */
  abstract enrich(
    home: CareHome,
    context?: EnrichmentContext
  ): Promise<EnrichmentResult>;

  /**
   * Проверить доступность service
   * По умолчанию проверяет feature flags
   */
  isAvailable(): boolean {
    const flagMap: Record<string, keyof typeof this.flags> = {
      financial: 'enableFinancialEnrichment',
      staff: 'enableStaffEnrichment',
      fsa: 'enableFSAEnrichment',
      googlePlaces: 'enableGooglePlacesEnrichment',
    };

    const flagName = flagMap[this.serviceName];
    if (flagName) {
      return this.flags[flagName] === true;
    }

    // Если нет feature flag, считаем доступным
    return true;
  }

  /**
   * Выполнить операцию с retry
   */
  protected async withRetry<T>(
    fn: () => Promise<T>,
    options?: RetryOptions
  ): Promise<T> {
    const retryOptions: RetryOptions = {
      maxAttempts: options?.maxAttempts ?? this.options.maxRetries,
      initialDelay: options?.initialDelay ?? this.options.retryDelay,
      ...options,
    };

    return retry(fn, retryOptions);
  }

  /**
   * Выполнить операцию с timeout
   */
  protected async withTimeout<T>(
    fn: () => Promise<T>,
    timeout?: number
  ): Promise<T> {
    const timeoutMs = timeout ?? this.options.timeout;

    return Promise.race([
      fn(),
      new Promise<T>((_, reject) =>
        setTimeout(
          () => reject(new Error(`${this.serviceName} enrichment timeout`)),
          timeoutMs
        )
      ),
    ]);
  }

  /**
   * Выполнить операцию с кэшированием
   */
  protected async withCache<T>(
    key: string,
    fn: () => Promise<T>,
    ttl?: number
  ): Promise<T> {
    if (!this.cache) {
      return fn();
    }

    const cacheKey = `enrichment:${this.serviceName}:${key}`;
    const cached = this.cache.get<T>(cacheKey);

    if (cached) {
      this.logger.debug({ cacheKey }, 'Cache hit');
      return cached;
    }

    const result = await fn();
    const cacheTTL = ttl ?? this.options.cacheTTL;
    this.cache.set(cacheKey, result, cacheTTL);

    return result;
  }

  /**
   * Генерировать cache key для home
   */
  protected getCacheKey(home: CareHome, suffix?: string): string {
    const homeId = home.cqc_location_id || home.id || 'unknown';
    return suffix ? `${homeId}:${suffix}` : homeId;
  }

  /**
   * Создать успешный результат
   */
  protected createSuccessResult(
    data: Record<string, any>,
    metadata?: EnrichmentResult['metadata'],
    processingTime?: number
  ): EnrichmentResult {
    return {
      source: this.serviceName,
      status: 'success',
      data,
      metadata: {
        enrichedAt: new Date().toISOString(),
        ...metadata,
      },
      processingTime,
    };
  }

  /**
   * Создать частичный результат
   */
  protected createPartialResult(
    data: Record<string, any>,
    error: string,
    metadata?: EnrichmentResult['metadata'],
    processingTime?: number
  ): EnrichmentResult {
    return {
      source: this.serviceName,
      status: 'partial',
      data,
      error,
      metadata: {
        enrichedAt: new Date().toISOString(),
        errors: [error],
        ...metadata,
      },
      processingTime,
    };
  }

  /**
   * Создать результат с ошибкой
   */
  protected createErrorResult(
    error: string | Error,
    processingTime?: number
  ): EnrichmentResult {
    const errorMessage = error instanceof Error ? error.message : error;

    return {
      source: this.serviceName,
      status: 'failed',
      data: {},
      error: errorMessage,
      metadata: {
        enrichedAt: new Date().toISOString(),
        errors: [errorMessage],
      },
      processingTime,
    };
  }

  /**
   * Создать результат из кэша
   */
  protected createCachedResult(
    data: Record<string, any>,
    processingTime?: number
  ): EnrichmentResult {
    return {
      source: this.serviceName,
      status: 'cached',
      data,
      metadata: {
        enrichedAt: new Date().toISOString(),
        sources: ['cache'],
      },
      processingTime,
    };
  }

  /**
   * Валидация входных данных
   */
  protected validateHome(home: CareHome): void {
    if (!home) {
      throw new Error('Home is required');
    }

    if (!home.name && !home.cqc_location_id && !home.id) {
      throw new Error('Home must have at least name, cqc_location_id, or id');
    }
  }

  /**
   * Логирование начала enrichment
   */
  protected logStart(home: CareHome, context?: EnrichmentContext): void {
    const homeId = home.cqc_location_id || home.id || 'unknown';
    this.logger.info(
      { homeId, homeName: home.name, requestId: context?.requestId },
      `Starting ${this.serviceName} enrichment`
    );
  }

  /**
   * Логирование завершения enrichment
   */
  protected logComplete(
    result: EnrichmentResult,
    home: CareHome
  ): void {
    const homeId = home.cqc_location_id || home.id || 'unknown';
    this.logger.info(
      {
        homeId,
        status: result.status,
        processingTime: result.processingTime,
      },
      `Completed ${this.serviceName} enrichment`
    );
  }

  /**
   * Логирование ошибки
   */
  protected logError(error: Error | string, home: CareHome): void {
    const homeId = home.cqc_location_id || home.id || 'unknown';
    const errorMessage = error instanceof Error ? error.message : String(error);
    this.logger.error(
      { homeId, error: errorMessage },
      `${this.serviceName} enrichment failed`
    );
  }
}

