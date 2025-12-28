/**
 * Data transformation utilities for Free Report
 * Transforms backend response to frontend format with all necessary fields
 */

import type { CareHome, CareHomeData, AreaProfile, AreaMapData, FreeReportResponse } from '../types';
import {
  DEFAULT_PHOTO_URL,
  WHY_THIS_HOME_TEXTS,
  DEFAULT_WHY_THIS_HOME,
  PRICE_RANGE_PERCENT,
  DEFAULT_BAND,
} from './constants';

/**
 * Transform a single care home from backend format to frontend format
 * 
 * @param home - Backend care home data
 * @param index - Index in the list (for band calculation)
 * @param questionnairePostcode - Fallback postcode from questionnaire
 * @returns Transformed CareHomeData
 */
export const transformCareHome = (
  home: any,
  index: number,
  questionnairePostcode?: string
): CareHomeData => {
  const matchType = (home.match_type || 
    (index === 0 ? 'Safe Bet' : index === 1 ? 'Best Value' : 'Premium')) as 'Safe Bet' | 'Best Value' | 'Premium';
  
  // Extract weekly cost - SIMPLIFIED like old version
  // Old version directly uses home.weekly_cost, so we do the same
  let weeklyCost = 0;
  
  // SIMPLIFIED: Use direct weekly_cost field like old version does
  // Old version: price_range: { min: home.weekly_cost * 0.9, max: home.weekly_cost * 1.1 }
  // Debug: Log what we receive
  const hasWeeklyCost = 'weekly_cost' in home;
  console.log(`🔍 [transformCareHome] ${home.name}:`, {
    has_weekly_cost: hasWeeklyCost,
    weekly_cost_value: home.weekly_cost,
    weekly_cost_type: typeof home.weekly_cost,
    weekly_cost_is_null: home.weekly_cost === null,
    weekly_cost_is_undefined: home.weekly_cost === undefined,
    weekly_cost_is_zero: home.weekly_cost === 0,
    first_10_keys: Object.keys(home).slice(0, 10)
  });
  
  // Extract weekly_cost directly (like old version)
  if (home.weekly_cost != null && home.weekly_cost !== undefined) {
    // Handle both string and number types
    const costValue = typeof home.weekly_cost === 'string' 
      ? parseFloat(home.weekly_cost) 
      : Number(home.weekly_cost);
    
    console.log(`🔍 [transformCareHome] ${home.name} - Parsing weekly_cost:`, {
      original: home.weekly_cost,
      parsed: costValue,
      isNaN: isNaN(costValue),
      isPositive: costValue > 0
    });
    
    if (!isNaN(costValue) && costValue > 0) {
      weeklyCost = costValue;
      console.log(`✅ [transformCareHome] ${home.name} - Extracted: £${weeklyCost}/week`);
    } else {
      console.warn(`⚠️ [transformCareHome] ${home.name} - Invalid weekly_cost:`, {
        original: home.weekly_cost,
        parsed: costValue,
        isNaN: isNaN(costValue)
      });
    }
  } else {
    console.warn(`⚠️ [transformCareHome] ${home.name} - weekly_cost is null/undefined`);
  }
  
  // FALLBACK: Only if weekly_cost is 0, try _original_home
  if (weeklyCost === 0 && home._original_home) {
    const original = home._original_home;
    console.log(`⚠️ [transformCareHome] ${home.name} - Trying _original_home fallback`);
    
    if (original.weekly_cost != null && original.weekly_cost !== undefined) {
      const costValue = typeof original.weekly_cost === 'string' 
        ? parseFloat(original.weekly_cost) 
        : Number(original.weekly_cost);
      if (!isNaN(costValue) && costValue > 0) {
        weeklyCost = costValue;
        console.log(`✅ [transformCareHome] ${home.name} - Extracted from _original_home: £${weeklyCost}/week`);
      }
    }
  }
  
  // Final check
  if (weeklyCost === 0) {
    console.error(`❌ [transformCareHome] ${home.name} - FAILED to extract price!`, {
      home_weekly_cost: home.weekly_cost,
      has_original: !!home._original_home,
      original_weekly_cost: home._original_home?.weekly_cost
    });
  }
  
  // Create price_range exactly like old version: min = weekly_cost * 0.9, max = weekly_cost * 1.1
  // Old version: price_range: { min: home.weekly_cost * 0.9, max: home.weekly_cost * 1.1 }
  const price_range = weeklyCost > 0 ? {
    min: weeklyCost * 0.9,
    max: weeklyCost * 1.1,
  } : {
    min: 0,
    max: 0,
  };
  
  console.log(`🔍 [transformCareHome] ${home.name} - Final price_range:`, {
    weeklyCost,
    price_range,
    will_be_zero: weeklyCost === 0
  });
  
  return {
    name: home.name || '',
    photo: home.photo_url || home.photo || DEFAULT_PHOTO_URL,
    band: home.band ?? (index + 1) ?? DEFAULT_BAND,
    price_range: price_range,
    distance: home.distance_km ?? 0, // Use nullish coalescing to allow 0.0 as valid value
    fsa_color: home.fsa_color as 'green' | 'yellow' | 'red' | undefined,
    fsa_rating: home.fsa_rating,
    fsa_rating_key: home.fsa_rating_key,
    fsa_rating_date: home.fsa_rating_date,
    fsa_health_score: home.fsa_health_score,
    match_type: matchType,
    why_this_home: WHY_THIS_HOME_TEXTS[matchType] || DEFAULT_WHY_THIS_HOME,
    rating: home.rating,
    features: home.features || [],
    care_types: home.care_types || [],
    address: home.address || '',
    city: home.city || '',
    postcode: home.postcode || questionnairePostcode || '',
    contact_phone: home.contact_phone,
    website: home.website,
  };
};

/**
 * Transform array of care homes
 */
export const transformCareHomes = (
  homes: any[],
  questionnairePostcode?: string
): CareHomeData[] => {
  if (!homes || homes.length === 0) {
    console.warn('No care homes provided for transformation');
    return [];
  }
  
  return homes.slice(0, 3).map((home, index) => 
    transformCareHome(home, index, questionnairePostcode)
  );
};

/**
 * Transform area_profile from backend format to frontend format
 */
export const transformAreaProfile = (
  areaProfile: any
): AreaProfile | undefined => {
  if (!areaProfile || typeof areaProfile !== 'object') return undefined;
  
  // Проверка обязательных полей
  if (!areaProfile.area_name || typeof areaProfile.total_homes !== 'number') {
    console.warn('Invalid area_profile structure: missing required fields');
    return undefined;
  }
  
  return {
    area_name: areaProfile.area_name,
    total_homes: areaProfile.total_homes,
    average_weekly_cost: areaProfile.average_weekly_cost,
    cost_vs_national: areaProfile.cost_vs_national,
    cqc_distribution: areaProfile.cqc_distribution,
    wellbeing_index: areaProfile.wellbeing_index,
    demographics: areaProfile.demographics,
  };
};

/**
 * Transform area_map from backend format to frontend format
 */
export const transformAreaMap = (
  areaMap: any
): AreaMapData | undefined => {
  if (!areaMap || typeof areaMap !== 'object') return undefined;
  
  // Проверка обязательных полей
  if (!areaMap.user_location || !Array.isArray(areaMap.homes)) {
    console.warn('Invalid area_map structure: missing required fields');
    return undefined;
  }
  
  return {
    user_location: areaMap.user_location,
    homes: areaMap.homes,
    amenities: areaMap.amenities,
  };
};

/**
 * Transform backend response to frontend format
 * Handles both AxiosResponse and direct response objects
 */
export const transformBackendResponse = (
  response: { data: FreeReportResponse } | FreeReportResponse,
  msifLowerBound: number,
  questionnairePostcode?: string
) => {
  // Handle both AxiosResponse and direct response
  const responseData = 'data' in response ? response.data : response;
  
  // Transform care homes
  const homes = transformCareHomes(
    responseData.care_homes || [],
    questionnairePostcode
  );
  
  // Transform fair cost gap
  // Use backend's fair_cost_gap data if available, otherwise calculate
  const backendFcg = responseData.fair_cost_gap;
  const backendMsifLower = backendFcg?.msif_lower_bound || msifLowerBound;
  
  let fairCostGap;
  if (backendFcg && backendFcg.gap_week !== undefined && (backendFcg.market_price || backendFcg.gap_week > 0)) {
    // Use backend calculated values (prefer gap_percent if available)
    fairCostGap = {
      weekly: backendFcg.gap_week || 0,
      annual: backendFcg.gap_year || 0,
      fiveYear: backendFcg.gap_5year || 0,
      percent: backendFcg.gap_percent !== undefined 
        ? backendFcg.gap_percent 
        : (backendMsifLower && backendFcg.gap_week 
          ? ((backendFcg.gap_week / backendMsifLower) * 100)
          : 0),
      msifLower: backendMsifLower,
    };
  } else {
    // Fallback: calculate from backend data or use defaults
    const marketPrice = backendFcg?.market_price || 1200;
    const weekly = Math.max(0, marketPrice - backendMsifLower);
    fairCostGap = {
      weekly,
      annual: weekly * 52,
      fiveYear: weekly * 52 * 5,
      percent: backendMsifLower > 0 ? ((weekly / backendMsifLower) * 100) : 0,
      msifLower: backendMsifLower,
    };
  }
  
  // Transform area_profile
  const areaProfile = transformAreaProfile(responseData.area_profile);
  
  // Transform area_map
  const areaMap = transformAreaMap(responseData.area_map);
  
  return {
    homes,
    fairCostGap,
    chcTeaserPercent: responseData.questionnaire?.chc_probability || 0,
    fundingEligibility: responseData.funding_eligibility,
    areaProfile,
    areaMap,
    llmInsights: responseData.llm_insights,
  };
};

