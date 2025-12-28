/**
 * Enrichment Types
 * Типы и интерфейсы для enrichment services в Data Engine
 */

import { CareHome } from '@/lib/shared/types/care-home';

/**
 * Результат enrichment операции
 */
export interface EnrichmentResult {
  /** Название enrichment service */
  source: string;
  
  /** Статус операции */
  status: 'success' | 'partial' | 'failed' | 'cached';
  
  /** Обогащенные данные */
  data: Record<string, any>;
  
  /** Ошибка (если есть) */
  error?: string;
  
  /** Время обработки в миллисекундах */
  processingTime?: number;
  
  /** Метаданные */
  metadata?: {
    /** Источники данных */
    sources?: string[];
    
    /** Ошибки (если есть) */
    errors?: string[];
    
    /** Дата обогащения */
    enrichedAt?: string;
    
    /** Качество данных */
    dataQuality?: 'high' | 'medium' | 'low';
    
    /** Дополнительные метаданные */
    [key: string]: any;
  };
}

/**
 * Контекст для enrichment
 */
export interface EnrichmentContext {
  /** User questionnaire (для professional report) */
  questionnaire?: Record<string, any>;
  
  /** Дополнительные параметры */
  params?: Record<string, any>;
  
  /** Request ID для логирования */
  requestId?: string;
}

/**
 * Опции для enrichment service
 */
export interface EnrichmentOptions {
  /** Использовать кэш */
  useCache?: boolean;
  
  /** TTL кэша в миллисекундах */
  cacheTTL?: number;
  
  /** Timeout в миллисекундах */
  timeout?: number;
  
  /** Максимальное количество попыток retry */
  maxRetries?: number;
  
  /** Начальная задержка для retry */
  retryDelay?: number;
  
  /** Логгер */
  logger?: any;
}

/**
 * Конфигурация для enrichment orchestrator
 */
export interface EnrichmentConfig {
  /** Включить Financial enrichment */
  enableFinancial?: boolean;
  
  /** Включить Staff enrichment */
  enableStaff?: boolean;
  
  /** Включить FSA enrichment */
  enableFSA?: boolean;
  
  /** Включить Google Places enrichment */
  enableGooglePlaces?: boolean;
  
  /** Выполнять параллельно */
  parallel?: boolean;
  
  /** Лимит параллельных запросов */
  parallelLimit?: number;
  
  /** Timeout для каждого источника */
  timeoutPerSource?: number;
  
  /** Кэшировать результаты */
  cacheResults?: boolean;
}

/**
 * Callback для прогресса enrichment
 */
export type EnrichmentProgressCallback = (
  progress: number,
  message: string
) => void;

/**
 * Базовый интерфейс для enrichment service
 */
export interface IEnrichmentService {
  /** Название service */
  serviceName: string;
  
  /** Обогатить care home */
  enrich(
    home: CareHome,
    context?: EnrichmentContext
  ): Promise<EnrichmentResult>;
  
  /** Проверить доступность service */
  isAvailable(): boolean;
}

/**
 * Результат обогащения нескольких домов
 */
export interface EnrichmentBatchResult {
  /** Успешно обогащенные дома */
  successful: Array<{
    home: CareHome;
    result: EnrichmentResult;
  }>;
  
  /** Дома с ошибками */
  failed: Array<{
    home: CareHome;
    error: string;
  }>;
  
  /** Общая статистика */
  stats: {
    total: number;
    successful: number;
    failed: number;
    cached: number;
    averageTime: number;
  };
}



