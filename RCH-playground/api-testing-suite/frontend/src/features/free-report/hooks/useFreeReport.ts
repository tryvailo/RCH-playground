import { useMutation, useQuery } from '@tanstack/react-query';
import axios from 'axios';
import type { QuestionnaireResponse, FreeReportResponse, FreeReportData, CareHomeData, FairCostGapData, FundingEligibility, AreaProfile, AreaMapData } from '../types';
import { getFairCostLower } from '../../fair-cost-gap/msifLoader';
import type { CareType } from '../../fair-cost-gap/types';

// Use relative path through Vite proxy, fallback to direct connection only if env var is set
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

// Helper: Get local authority from postcode (fallback logic)
const getLocalAuthorityFromPostcode = (postcode: string): string => {
  const postcodeUpper = postcode.toUpperCase().trim();
  
  // London postcodes
  if (postcodeUpper.match(/^(SW|SE|NW|NE|E|W|N|WC|EC)/)) {
    return 'Westminster';
  }
  
  // Manchester
  if (postcodeUpper.startsWith('M')) {
    return 'Manchester';
  }
  
  // Birmingham
  if (postcodeUpper.startsWith('B')) {
    return 'Birmingham';
  }
  
  // Liverpool
  if (postcodeUpper.startsWith('L')) {
    return 'Liverpool';
  }
  
  // Leeds
  if (postcodeUpper.startsWith('LS')) {
    return 'Leeds';
  }
  
  // Camden (default for SW1A)
  if (postcodeUpper.startsWith('SW1')) {
    return 'Camden';
  }
  
  return 'Westminster'; // Default fallback
};

// Helper: Convert care type string to MSIF CareType enum
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

// Fetch MSIF lower bound using shared msifLoader
// This ensures consistent MSIF data across Free Report and other tabs
const fetchMSIFLowerBound = async (localAuthority: string, careType: string): Promise<number> => {
  const msifCareType = toMSIFCareType(careType);
  
  try {
    // Use shared getFairCostLower from msifLoader (with caching and fallback)
    const fairCost = await getFairCostLower(localAuthority, msifCareType);
    return fairCost || 700; // Default fallback if null
  } catch (error) {
    console.warn('MSIF loader failed, using fallback:', error);
    // Fallback values based on care type
    const fallbackValues: Record<CareType, number> = {
      residential: 700,
      nursing: 1048,
      residential_dementia: 800,
      nursing_dementia: 1048,
    };
    return fallbackValues[msifCareType] || 700;
  }
};

// Calculate Fair Cost Gap
const calculateFairCostGap = (
  marketPrice: number,
  msifLowerBound: number
): FairCostGapData => {
  const weekly = marketPrice - msifLowerBound;
  const annual = weekly * 52;
  const fiveYear = annual * 5;
  const percent = msifLowerBound > 0 ? ((weekly / msifLowerBound) * 100) : 0;

  return {
    weekly: Math.max(0, weekly),
    annual: Math.max(0, annual),
    fiveYear: Math.max(0, fiveYear),
    percent: Math.max(0, percent),
  };
};

// Calculate Funding Eligibility based on questionnaire
const calculateFundingEligibility = (questionnaire: QuestionnaireResponse): FundingEligibility => {
  const chcProb = questionnaire.chc_probability || 35;
  
  // CHC probability range based on questionnaire
  let chcRange: string;
  let chcSavings: string;
  if (chcProb >= 75) {
    chcRange = '75-90%';
    chcSavings = '£78,000-£130,000/year';
  } else if (chcProb >= 50) {
    chcRange = '50-75%';
    chcSavings = '£52,000-£78,000/year';
  } else if (chcProb >= 25) {
    chcRange = '25-50%';
    chcSavings = '£26,000-£52,000/year';
  } else {
    chcRange = '10-25%';
    chcSavings = '£10,000-£26,000/year';
  }

  // LA funding probability (typically 60-80% for most applicants)
  const laProb = Math.min(95, 50 + (chcProb * 0.4));
  
  // DPA probability (usually high if property owner)
  const dpaProb = 85;

  return {
    chc: {
      probability_range: chcRange,
      savings_range: chcSavings,
    },
    la: {
      probability: `${Math.round(laProb)}%`,
      savings_range: '£20,000-£50,000/year',
    },
    dpa: {
      probability: `${dpaProb}%`,
      cash_flow_relief: '£2,000+/week deferred',
    },
  };
};

// Mock data generator
const generateMockReportData = (
  questionnaire: QuestionnaireResponse
): FreeReportData => {
  const marketPrice = questionnaire.budget || 1200;
  const msifLowerBound = 1048; // Mock MSIF value
  
  const fairCostGap = calculateFairCostGap(marketPrice, msifLowerBound);
  const fundingEligibility = calculateFundingEligibility(questionnaire);
  
  const mockHomes: CareHomeData[] = [
    {
      name: 'Sunshine Care Home',
      photo: 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=400',
      band: 3,
      price_range: { min: 1000, max: 1150 },
      distance: 2.5,
      fsa_color: 'green',
      match_type: 'Safe Bet',
      why_this_home: 'Excellent balance of price and quality. High CQC rating and close location make this home a safe choice.',
      rating: 'Good',
      features: ['Garden', 'Activities', '24/7 Care'],
      address: '123 High Street',
      city: 'London',
      postcode: 'SW1A 1AA',
    },
    {
      name: 'Greenfield Manor',
      photo: 'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400',
      band: 2,
      price_range: { min: 900, max: 1000 },
      distance: 3.2,
      fsa_color: 'green',
      match_type: 'Best Value',
      why_this_home: 'Best price-to-quality ratio. Affordable price while maintaining high care standards.',
      rating: 'Good',
      features: ['Dementia Specialist', 'Transport Access'],
      address: '456 Park Avenue',
      city: 'London',
      postcode: 'SW1A 2BB',
    },
    {
      name: 'Elmwood House',
      photo: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=400',
      band: 4,
      price_range: { min: 1300, max: 1450 },
      distance: 4.1,
      fsa_color: 'green',
      match_type: 'Premium',
      why_this_home: 'Premium option with outstanding CQC rating. Perfect choice for those seeking the highest quality of care.',
      rating: 'Outstanding',
      features: ['Luxury Facilities', 'Specialist Care', 'Family Involvement'],
      address: '789 Garden Road',
      city: 'London',
      postcode: 'SW1A 3CC',
    },
  ];

  return {
    homes: mockHomes,
    fairCostGap,
    chcTeaserPercent: questionnaire.chc_probability || 35.5,
    fundingEligibility,
  };
};

// Transform backend response to FreeReportData
const transformBackendResponse = (
  response: { data: FreeReportResponse } | FreeReportResponse,
  msifLowerBound: number
): FreeReportData => {
  // Handle both AxiosResponse and direct response
  const responseData = 'data' in response ? response.data : response;
  
  // Use backend's fair_cost_gap data if available, otherwise calculate
  const backendFcg = responseData.fair_cost_gap;
  let fairCostGap: FairCostGapData & { msifLower?: number };
  
  if (backendFcg && backendFcg.gap_week !== undefined && backendFcg.market_price) {
    // Use backend calculated values
    fairCostGap = {
      weekly: backendFcg.gap_week || 0,
      annual: backendFcg.gap_year || 0,
      fiveYear: backendFcg.gap_5year || 0,
      percent: backendFcg.gap_percent || 0,
      msifLower: backendFcg.msif_lower_bound || msifLowerBound,
    };
  } else {
    // Fallback: calculate from backend data
    const marketPrice = backendFcg?.market_price || 1200;
    fairCostGap = {
      ...calculateFairCostGap(marketPrice, msifLowerBound),
      msifLower: backendFcg?.msif_lower_bound || msifLowerBound,
    };
  }

  const homes: CareHomeData[] = responseData.care_homes.slice(0, 3).map((home) => {
    const matchType = home.match_type || 'Safe Bet';
    const whyTexts: Record<string, string> = {
      'Safe Bet': 'Excellent balance of price and quality. High CQC rating and close location make this home a safe choice.',
      'Best Value': 'Best price-to-quality ratio. Affordable price while maintaining high care standards.',
      'Premium': 'Premium option with outstanding CQC rating. Perfect choice for those seeking the highest quality of care.',
    };

    return {
      name: home.name,
      photo: home.photo_url || home.photo || `https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800&h=600&fit=crop&q=80`,
      band: home.band || 3,
      price_range: {
        min: home.weekly_cost * 0.9,
        max: home.weekly_cost * 1.1,
      },
      distance: home.distance_km ?? 0, // Use nullish coalescing to allow 0.0 as valid value
      fsa_color: home.fsa_color,
      fsa_rating: home.fsa_rating,
      fsa_rating_key: home.fsa_rating_key,
      fsa_rating_date: home.fsa_rating_date,
      fsa_health_score: home.fsa_health_score,
      match_type: matchType,
      why_this_home: whyTexts[matchType] || 'Recommended based on quality, price, and location.',
      rating: home.rating,
      features: home.features,
      care_types: home.care_types,
      address: home.address,
      city: home.city,
      postcode: home.postcode,
      contact_phone: home.contact_phone,
      website: home.website,
    };
  });

  // Generate funding eligibility from questionnaire if not provided by backend
  const fundingEligibility = responseData.funding_eligibility || 
    calculateFundingEligibility(responseData.questionnaire);

  // Transform area_profile if provided by backend
  const areaProfile: AreaProfile | undefined = (responseData as any).area_profile ? {
    area_name: (responseData as any).area_profile.area_name,
    total_homes: (responseData as any).area_profile.total_homes,
    average_weekly_cost: (responseData as any).area_profile.average_weekly_cost,
    cost_vs_national: (responseData as any).area_profile.cost_vs_national,
    cqc_distribution: (responseData as any).area_profile.cqc_distribution,
    wellbeing_index: (responseData as any).area_profile.wellbeing_index,
    demographics: (responseData as any).area_profile.demographics,
  } : undefined;

  // Transform area_map if provided by backend
  const areaMap: AreaMapData | undefined = (responseData as any).area_map ? {
    user_location: (responseData as any).area_map.user_location,
    homes: (responseData as any).area_map.homes,
    amenities: (responseData as any).area_map.amenities,
  } : undefined;

  // Transform llm_insights if provided by backend
  const llmInsights = (responseData as any).llm_insights || undefined;

  return {
    homes,
    fairCostGap,
    chcTeaserPercent: responseData.questionnaire.chc_probability || 0,
    fundingEligibility,
    areaProfile,
    areaMap,
    llmInsights,
  };
};

// Main hook
export const useGenerateFreeReport = () => {
  return useMutation({
    mutationFn: async (questionnaire: QuestionnaireResponse): Promise<FreeReportData> => {
      const localAuthority = getLocalAuthorityFromPostcode(questionnaire.postcode);
      const careType = questionnaire.care_type || 'residential';

      try {
        // Step 1: Try to fetch MSIF lower bound (using shared msifLoader)
        let msifLowerBound: number;
        try {
          msifLowerBound = await fetchMSIFLowerBound(localAuthority, careType);
        } catch (error) {
          console.warn('MSIF fetch failed, using fallback');
          msifLowerBound = 1048; // Fallback
        }

        // Step 2: Try to generate report from backend
        try {
          // Normalize care_type to match backend enum (residential, nursing, dementia, respite)
          const normalizeCareType = (careType?: string): string | undefined => {
            if (!careType) return undefined;
            const normalized = careType.toLowerCase().trim();
            // Map common variations to backend enum values
            if (normalized.includes('residential') && !normalized.includes('dementia')) {
              return 'residential';
            }
            if (normalized.includes('nursing')) {
              return 'nursing';
            }
            if (normalized.includes('dementia')) {
              return 'dementia';
            }
            if (normalized.includes('respite')) {
              return 'respite';
            }
            // Default fallback
            return normalized;
          };

          // Normalize postcode (remove spaces, ensure uppercase)
          const normalizePostcode = (postcode?: string): string | undefined => {
            if (!postcode) return undefined;
            return postcode.replace(/\s+/g, '').toUpperCase().trim();
          };

          // Prepare request data with normalization
          const requestData: any = {
            postcode: normalizePostcode(questionnaire.postcode || questionnaire.location_postcode) || '',
            budget: questionnaire.budget || 0,
            care_type: normalizeCareType(questionnaire.care_type) || 'residential',
            chc_probability: questionnaire.chc_probability || 35,
            // Optional fields
            location_postcode: normalizePostcode(questionnaire.location_postcode) || undefined,
            timeline: questionnaire.timeline || undefined,
            medical_conditions: questionnaire.medical_conditions || [],
            max_distance_km: questionnaire.max_distance_km || 30,
            priority_order: questionnaire.priority_order || ['quality', 'cost', 'proximity'],
            priority_weights: questionnaire.priority_weights || [40, 35, 25],
          };

          // Include scoring settings if available
          if ((questionnaire as any).scoring_weights) {
            requestData.scoring_weights = (questionnaire as any).scoring_weights;
          }
          if ((questionnaire as any).scoring_thresholds) {
            requestData.scoring_thresholds = (questionnaire as any).scoring_thresholds;
          }
          
          const url = API_BASE_URL ? `${API_BASE_URL}/api/free-report` : '/api/free-report';
          
          console.log('📤 Sending free report request:', {
            url,
            postcode: requestData.postcode,
            budget: requestData.budget,
            care_type: requestData.care_type,
            chc_probability: requestData.chc_probability,
          });
          
          const response = await axios.post<FreeReportResponse>(
            url,
            requestData,
            {
              timeout: 30000, // 30 seconds timeout
            }
          );

          console.log('✅ Free report response received:', {
            care_homes_count: response.data.care_homes?.length || 0,
            report_id: response.data.report_id,
          });

          // Transform backend response to FreeReportData
          return transformBackendResponse(response.data, msifLowerBound);
        } catch (error) {
          // Log detailed error information
          if (axios.isAxiosError(error)) {
            console.error('❌ Free report API error:', {
              message: error.message,
              code: error.code,
              status: error.response?.status,
              statusText: error.response?.statusText,
              data: error.response?.data,
              url: error.config?.url,
            });
            
            // If backend is not ready, use mock data
            if (
              error.code === 'ECONNREFUSED' ||
              error.code === 'ERR_NETWORK' ||
              error.response?.status === 404 ||
              error.response?.status === 500
            ) {
              console.warn('⚠️ Backend not available, using mock data');
              
              // Recalculate Fair Cost Gap with fetched MSIF
              const marketPrice = questionnaire.budget || 1200;
              const fairCostGap = calculateFairCostGap(marketPrice, msifLowerBound);
              
              const mockData = generateMockReportData(questionnaire);
              return {
                ...mockData,
                fairCostGap, // Use calculated gap with real MSIF if available
              };
            }
          } else {
            console.error('❌ Unexpected error:', error);
          }
          throw error;
        }
      } catch (error) {
        // Final fallback: use mock data with fallback MSIF
        console.warn('⚠️ All API calls failed, using full mock data', error);
        return generateMockReportData(questionnaire);
      }
    },
    // Cache configuration
    mutationKey: ['free-report'],
    gcTime: 1000 * 60 * 60, // Cache for 1 hour
  });
};

// Hook to fetch MSIF data separately (for pre-fetching or display)
export const useMSIFFairCost = (localAuthority: string | null, careType: string | null) => {
  return useQuery({
    queryKey: ['msif-fair-cost', localAuthority, careType],
    queryFn: async () => {
      if (!localAuthority || !careType) return null;
      return await fetchMSIFLowerBound(localAuthority, careType);
    },
    enabled: !!localAuthority && !!careType,
    staleTime: 1000 * 60 * 60, // Consider fresh for 1 hour
    gcTime: 1000 * 60 * 60 * 24, // Keep in cache for 24 hours
  });
};
