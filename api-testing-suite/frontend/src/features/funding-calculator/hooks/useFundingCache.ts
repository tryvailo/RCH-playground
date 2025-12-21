/**
 * useFundingCache - Client-side caching of results
 * 
 * Features:
 * - Cache by form data hash
 * - 24-hour TTL
 * - localStorage persistence
 */

import { useCallback } from 'react';
import { FormData, FundingEligibilityResult } from '../types/funding.types';

const CACHE_KEY = 'funding_calculator_cache';
const CACHE_TTL = 24 * 60 * 60 * 1000; // 24 hours

interface CacheEntry {
  key: string;
  result: FundingEligibilityResult;
  timestamp: number;
}

export function useFundingCache() {
  const getCache = useCallback((): CacheEntry[] => {
    try {
      const cached = localStorage.getItem(CACHE_KEY);
      return cached ? JSON.parse(cached) : [];
    } catch {
      return [];
    }
  }, []);

  const makeKey = useCallback((formData: FormData): string => {
    // Create a simple hash of form data
    const key = JSON.stringify({
      age: formData.age,
      domains: formData.domainAssessments,
      capital: formData.capitalAssets,
      income: formData.weeklyIncome,
      property: formData.propertyDetails?.value,
    });
    return key;
  }, []);

  const getCached = useCallback(
    (key: string): FundingEligibilityResult | null => {
      const cache = getCache();
      const entry = cache.find((e) => e.key === key);

      if (!entry) return null;

      // Check if expired
      if (Date.now() - entry.timestamp > CACHE_TTL) {
        // Remove expired entry
        const updated = cache.filter((e) => e.key !== key);
        localStorage.setItem(CACHE_KEY, JSON.stringify(updated));
        return null;
      }

      return entry.result;
    },
    [getCache]
  );

  const setCached = useCallback((key: string, result: FundingEligibilityResult) => {
    const cache = getCache();
    
    // Remove if already exists
    const filtered = cache.filter((e) => e.key !== key);
    
    // Add new entry
    filtered.push({
      key,
      result,
      timestamp: Date.now(),
    });

    // Keep only last 10 entries
    const trimmed = filtered.slice(-10);
    
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify(trimmed));
    } catch {
      console.warn('Failed to cache result');
    }
  }, [getCache]);

  const isCached = useCallback(
    (formData: FormData): boolean => {
      const key = makeKey(formData);
      return getCached(key) !== null;
    },
    [makeKey, getCached]
  );

  const clearCache = useCallback(() => {
    try {
      localStorage.removeItem(CACHE_KEY);
    } catch {
      console.warn('Failed to clear cache');
    }
  }, []);

  return {
    getCached,
    setCached,
    isCached,
    clearCache,
    makeKey,
  };
}

export type UseFundingCacheReturn = ReturnType<typeof useFundingCache>;
