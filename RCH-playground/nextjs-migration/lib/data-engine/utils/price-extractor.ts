/**
 * Price Extractor Utilities
 * Ported from Python utils/price_extractor.py
 */

import { CARE_TYPE_FIELDS } from '@/lib/shared/constants/care-types';

export type CareType = 'residential' | 'nursing' | 'dementia' | 'respite';

/**
 * Extract weekly price from care home data, checking multiple field names and care types
 * 
 * Handles various data sources:
 * - Direct price fields (weeklyPrice, weekly_price, etc.)
 * - Care-type specific fields (fee_residential_from, fee_nursing_from, etc.)
 * - Nested weekly_costs dictionaries (from mock data)
 * 
 * @param homeData Dictionary containing care home data
 * @param preferredCareType Optional preferred care type for price lookup
 * @returns Weekly price as number, or 0.0 if not found
 */
export function extractWeeklyPrice(
  homeData: Record<string, any>,
  preferredCareType?: CareType
): number {
  if (!homeData || typeof homeData !== 'object') {
    return 0.0;
  }

  // Try direct price fields first (most common)
  const directFields = [
    'weeklyPrice',
    'weekly_price',
    'price_weekly',
    'weekly_cost',
    'weeklyCost', // camelCase variant
  ];

  for (const field of directFields) {
    const value = homeData[field];
    if (value !== null && value !== undefined) {
      try {
        const price = parseFloat(value);
        if (price > 0) {
          return price;
        }
      } catch {
        continue;
      }
    }
  }

  // Try care-type specific fields (from database schema)
  if (preferredCareType) {
    const careTypeLower = preferredCareType.toLowerCase();
    const careTypeFields = CARE_TYPE_FIELDS[careTypeLower] || [];

    for (const field of careTypeFields) {
      const value = homeData[field];
      if (value !== null && value !== undefined) {
        try {
          const price = parseFloat(value);
          if (price > 0) {
            return price;
          }
        } catch {
          continue;
        }
      }
    }
  }

  // Try all fee fields as fallback
  const allFeeFields = [
    'fee_residential_from',
    'fee_nursing_from',
    'fee_dementia_from',
    'fee_dementia_residential_from',
    'fee_dementia_nursing_from',
    'fee_respite_from',
  ];

  for (const field of allFeeFields) {
    const value = homeData[field];
    if (value !== null && value !== undefined) {
      try {
        const price = parseFloat(value);
        if (price > 0) {
          return price;
        }
      } catch {
        continue;
      }
    }
  }

  // Try weekly_costs nested dict (from mock data)
  const weeklyCosts = homeData.weekly_costs || homeData.weeklyCosts;
  if (weeklyCosts && typeof weeklyCosts === 'object') {
    // Build lookup order
    const lookupOrder: string[] = [];
    if (preferredCareType) {
      lookupOrder.push(preferredCareType.toLowerCase());
    }
    lookupOrder.push('residential', 'nursing', 'dementia', 'respite');

    for (const careKey of lookupOrder) {
      const value = weeklyCosts[careKey];
      if (value !== null && value !== undefined) {
        try {
          const price = parseFloat(value);
          if (price > 0) {
            return price;
          }
        } catch {
          continue;
        }
      }
    }
  }

  // If rawData present, attempt extraction from it (for Professional Report frontend format)
  const rawData = homeData.rawData;
  if (rawData && typeof rawData === 'object' && rawData !== homeData) {
    const price = extractWeeklyPrice(rawData, preferredCareType);
    if (price > 0) {
      return price;
    }
  }

  return 0.0;
}

/**
 * Extract price range (min/max) from care home data
 * 
 * @param homeData Dictionary containing care home data
 * @param preferredCareType Optional preferred care type
 * @returns Dictionary with 'min' and 'max' keys
 */
export function extractPriceRange(
  homeData: Record<string, any>,
  preferredCareType?: CareType
): { min: number; max: number } {
  // Check for explicit range fields first
  const priceMin = homeData.price_min || homeData.weekly_price_min || homeData.priceMin;
  const priceMax = homeData.price_max || homeData.weekly_price_max || homeData.priceMax;

  if (priceMin !== undefined && priceMin !== null && priceMax !== undefined && priceMax !== null) {
    try {
      const min = parseFloat(String(priceMin));
      const max = parseFloat(String(priceMax));
      if (!isNaN(min) && !isNaN(max) && min > 0 && max > 0) {
        return { min, max };
      }
    } catch {
      // Fall through to default
    }
  }

  // If no explicit range, use base price to estimate
  const basePrice = extractWeeklyPrice(homeData, preferredCareType);

  if (basePrice <= 0) {
    return { min: 0.0, max: 0.0 };
  }

  // Default: estimate range as ±10% of base price
  return {
    min: Math.round(basePrice * 0.9 * 100) / 100,
    max: Math.round(basePrice * 1.1 * 100) / 100,
  };
}

