/**
 * Fair Cost Gap Types
 * Типы для модуля расчёта Fair Cost Gap
 */

export type CareType = 'residential' | 'nursing' | 'residential_dementia' | 'nursing_dementia';

export interface FairCostGapData {
  msifLower: number;
  marketPrice: number;
  gapWeekly: number;
  gapAnnual: number;
  gapFiveYear: number;
  gapPercent: number;
}

export interface FairCostGapResult {
  msifLower: number;
  gapWeekly: number;
  gapAnnual: number;
  gapFiveYear: number;
  gapPercent: number;
  isLoading: boolean;
  error: string | null;
}

export interface MSIFData {
  [localAuthority: string]: {
    residential?: number;
    nursing?: number;
    residential_dementia?: number;
    nursing_dementia?: number;
  };
}

export interface MSIFStoreState {
  msifData: MSIFData | null;
  isLoading: boolean;
  error: string | null;
  lastFetched: number | null;
  setMSIFData: (data: MSIFData) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearCache: () => void;
}

