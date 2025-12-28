/**
 * MSIF (Market Sustainability and Improvement Fund) hook
 * Provides MSIF lower bound with React Query caching
 */

import { useQuery } from '@tanstack/react-query';
import { getFairCostLower } from '../../fair-cost-gap/msifLoader';
import type { CareType } from '../../fair-cost-gap/types';
import { getLocalAuthorityFromPostcode } from '../utils/normalization';
import { DEFAULT_MSIF_FALLBACK } from '../utils/constants';

/**
 * Convert care type string to MSIF CareType enum
 */
const toMSIFCareType = (careType?: string): CareType => {
  if (!careType) return 'nursing';
  
  const mapping: Record<string, CareType> = {
    residential: 'residential',
    nursing: 'nursing',
    dementia: 'residential_dementia',
    respite: 'residential',
  };
  
  return mapping[careType] || 'nursing';
};

/**
 * Fetch MSIF lower bound using shared msifLoader
 * This ensures consistent MSIF data across Free Report and other tabs
 * 
 * @param localAuthority - Local authority name
 * @param careType - Care type string
 * @returns MSIF lower bound value
 */
const fetchMSIFLowerBound = async (
  localAuthority: string,
  careType: string
): Promise<number> => {
  const msifCareType = toMSIFCareType(careType);
  
  try {
    // Use shared getFairCostLower from msifLoader (with caching and fallback)
    const fairCost = await getFairCostLower(localAuthority, msifCareType);
    if (fairCost) return fairCost;
    
    // Fallback values based on care type
    const fallbackKey = msifCareType as string;
    return DEFAULT_MSIF_FALLBACK[fallbackKey] || DEFAULT_MSIF_FALLBACK.default;
  } catch (error) {
    console.warn('MSIF loader failed, using fallback:', error);
    // Fallback values based on care type
    const fallbackKey = msifCareType as string;
    return DEFAULT_MSIF_FALLBACK[fallbackKey] || DEFAULT_MSIF_FALLBACK.default;
  }
};

/**
 * Hook to fetch MSIF lower bound with React Query caching
 * 
 * @param postcode - User postcode (for local authority lookup)
 * @param careType - Care type string
 * @returns React Query result with MSIF lower bound
 */
export const useMSIF = (postcode: string | null, careType: string | null) => {
  return useQuery({
    queryKey: ['msif-fair-cost', postcode, careType],
    queryFn: async () => {
      if (!postcode || !careType) return null;
      
      const localAuthority = getLocalAuthorityFromPostcode(postcode);
      return await fetchMSIFLowerBound(localAuthority, careType);
    },
    enabled: !!postcode && !!careType,
    staleTime: 1000 * 60 * 60, // Consider fresh for 1 hour
    gcTime: 1000 * 60 * 60 * 24, // Keep in cache for 24 hours
  });
};

/**
 * Fetch MSIF lower bound (for use in mutations)
 * This is a regular function, not a hook, so it can be called inside mutations
 * 
 * @param postcode - User postcode
 * @param careType - Care type string
 * @returns MSIF lower bound value
 */
export const fetchMSIFForMutation = async (
  postcode: string,
  careType: string
): Promise<number> => {
  const localAuthority = getLocalAuthorityFromPostcode(postcode);
  return await fetchMSIFLowerBound(localAuthority, careType);
};

