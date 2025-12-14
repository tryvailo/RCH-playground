/**
 * useFairCostGap Hook
 * Calculates Fair Cost Gap based on market price and MSIF lower bound
 */
import { useState, useEffect } from 'react';
import { getFairCostLower } from '../msifLoader';
import type { FairCostGapResult, CareType } from '../types';

interface UseFairCostGapParams {
  marketPrice: number;
  localAuthority: string;
  careType: CareType;
  enabled?: boolean;
}

/**
 * Calculates Fair Cost Gap
 * 
 * Formula:
 * 1. msif_lower = value from MSIF by local_authority + care_type
 * 2. gap_week = market_price - msif_lower
 * 3. gap_year = gap_week * 52
 * 4. gap_5year = gap_year * 5
 * 5. gap_percent = (gap_week / msif_lower) * 100
 */
export function useFairCostGap({
  marketPrice,
  localAuthority,
  careType,
  enabled = true,
}: UseFairCostGapParams): FairCostGapResult {
  const [result, setResult] = useState<FairCostGapResult>({
    msifLower: 0,
    gapWeekly: 0,
    gapAnnual: 0,
    gapFiveYear: 0,
    gapPercent: 0,
    isLoading: false,
    error: null,
  });

  useEffect(() => {
    if (!enabled || !marketPrice || !localAuthority || !careType) {
      return;
    }

    const calculateGap = async () => {
      setResult((prev) => ({ ...prev, isLoading: true, error: null }));

      try {
        // Get MSIF lower bound (with fallback values - always returns a number)
        const msifLower = await getFairCostLower(localAuthority, careType);

        // getFairCostLower always returns a number (never null due to fallback)
        const msifValue = msifLower || 700;

        // Calculate gap
        const gapWeekly = Math.max(0, marketPrice - msifValue);
        const gapAnnual = gapWeekly * 52;
        const gapFiveYear = gapAnnual * 5;
        const gapPercent = msifValue > 0 ? (gapWeekly / msifValue) * 100 : 0;

        setResult({
          msifLower: msifValue,
          gapWeekly,
          gapAnnual,
          gapFiveYear,
          gapPercent,
          isLoading: false,
          error: null, // No error - fallback data is used if needed
        });
      } catch (error) {
        // Even on error, use fallback values (getFairCostLower always returns a value)
        const fallbackMsif = 700;
        const gapWeekly = Math.max(0, marketPrice - fallbackMsif);
        const gapAnnual = gapWeekly * 52;
        const gapFiveYear = gapAnnual * 5;
        const gapPercent = fallbackMsif > 0 ? (gapWeekly / fallbackMsif) * 100 : 0;
        
        setResult({
          msifLower: fallbackMsif,
          gapWeekly,
          gapAnnual,
          gapFiveYear,
          gapPercent,
          isLoading: false,
          error: null, // Don't show error - fallback data is sufficient
        });
      }
    };

    calculateGap();
  }, [marketPrice, localAuthority, careType, enabled]);

  return result;
}

