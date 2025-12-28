/**
 * Enrichment Cache
 * Специализированный кэш для enrichment данных
 * Использует DataCache из core, но добавляет enrichment-specific логику
 */

import { DataCache } from '@/lib/data-engine/core/data-cache';
import { EnrichmentResult } from './types';

/**
 * Кэш для enrichment данных
 * Обертка над DataCache с enrichment-specific методами
 */
export class EnrichmentCache {
  private cache: DataCache;

  constructor(ttl: number = 3600000) {
    // 1 hour default TTL
    this.cache = new DataCache(ttl);
  }

  /**
   * Получить enrichment результат из кэша
   */
  get(serviceName: string, homeId: string): EnrichmentResult | null {
    const key = this.generateKey(serviceName, homeId);
    return this.cache.get<EnrichmentResult>(key);
  }

  /**
   * Сохранить enrichment результат в кэш
   */
  set(
    serviceName: string,
    homeId: string,
    result: EnrichmentResult,
    ttl?: number
  ): void {
    const key = this.generateKey(serviceName, homeId);
    this.cache.set(key, result, ttl);
  }

  /**
   * Проверить наличие в кэше
   */
  has(serviceName: string, homeId: string): boolean {
    const key = this.generateKey(serviceName, homeId);
    return this.cache.has(key);
  }

  /**
   * Удалить из кэша
   */
  delete(serviceName: string, homeId: string): void {
    const key = this.generateKey(serviceName, homeId);
    this.cache.delete(key);
  }

  /**
   * Очистить весь кэш
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Генерировать cache key
   */
  private generateKey(serviceName: string, homeId: string): string {
    return `enrichment:${serviceName}:${homeId}`;
  }

  /**
   * Получить статистику кэша
   */
  getStats(): {
    size: number;
    hitRate?: number;
    missRate?: number;
  } {
    // DataCache может не иметь статистики, возвращаем базовую
    return {
      size: 0, // TODO: добавить статистику в DataCache если нужно
    };
  }
}



