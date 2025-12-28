/**
 * Data Cache
 * In-memory caching for Data Engine
 */

import { CacheEntry } from '@/lib/shared/types/common';

export class DataCache {
  private cache: Map<string, CacheEntry<any>>;
  private defaultTTL: number = 3600000; // 1 hour in milliseconds

  constructor(defaultTTL?: number) {
    this.cache = new Map();
    if (defaultTTL) {
      this.defaultTTL = defaultTTL;
    }
  }

  /**
   * Get value from cache
   * 
   * @param key Cache key
   * @returns Cached value or null if not found/expired
   */
  get<T>(key: string): T | null {
    const cached = this.cache.get(key);
    if (!cached) {
      return null;
    }

    if (Date.now() > cached.expiresAt) {
      this.cache.delete(key);
      return null;
    }

    return cached.data as T;
  }

  /**
   * Set value in cache
   * 
   * @param key Cache key
   * @param data Data to cache
   * @param ttl Time to live in milliseconds (optional, uses default if not provided)
   */
  set(key: string, data: any, ttl?: number): void {
    const expiresAt = Date.now() + (ttl || this.defaultTTL);
    this.cache.set(key, { data, expiresAt });
  }

  /**
   * Generate cache key from prefix and parameters
   * 
   * @param prefix Key prefix
   * @param params Parameters object
   * @returns Generated cache key
   */
  generateKey(prefix: string, params: Record<string, any>): string {
    const sorted = Object.keys(params)
      .sort()
      .map((k) => `${k}:${params[k]}`)
      .join('|');
    return `${prefix}:${sorted}`;
  }

  /**
   * Clear all cache
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Remove specific key from cache
   * 
   * @param key Cache key to remove
   */
  delete(key: string): void {
    this.cache.delete(key);
  }

  /**
   * Check if key exists and is not expired
   * 
   * @param key Cache key
   * @returns True if key exists and is valid
   */
  has(key: string): boolean {
    const cached = this.cache.get(key);
    if (!cached) {
      return false;
    }

    if (Date.now() > cached.expiresAt) {
      this.cache.delete(key);
      return false;
    }

    return true;
  }
}



