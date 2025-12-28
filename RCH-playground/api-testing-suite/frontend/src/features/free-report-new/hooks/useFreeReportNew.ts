import { useMutation } from '@tanstack/react-query';
import axios from 'axios';
import type { QuestionnaireResponse, FreeReportData } from '../types';
import { normalizePostcode, normalizeCareType } from '../utils/normalization';
import { calculateFundingEligibility } from '../utils/fundingEligibility';
import { transformBackendResponse } from '../utils/transform';
import { logError, getUserFriendlyErrorMessage, isBackendUnavailable } from '../utils/errorHandling';
import { fetchMSIFForMutation } from './useMSIF';

// Use relative path through Vite proxy, fallback to direct connection only if env var is set
const API_BASE_URL = (import.meta.env as any).VITE_API_URL || '';

/**
 * Hook для генерации Free Report с улучшенной обработкой данных
 * Использует модульную структуру для нормализации, трансформации и обработки ошибок
 */
export const useFreeReportNew = () => {
  return useMutation({
    mutationFn: async (questionnaire: QuestionnaireResponse): Promise<FreeReportData> => {
      console.log('🚀 Generating Free Report (New) for:', questionnaire.postcode);

      // ЭТАП 1: Валидация
      if (!questionnaire.postcode && !questionnaire.location_postcode) {
        throw new Error('Postcode or location postcode is required');
      }

      // ЭТАП 2: Нормализация входных данных
      const normalizedPostcode = normalizePostcode(
        questionnaire.postcode || questionnaire.location_postcode
      );
      const normalizedCareType = normalizeCareType(questionnaire.care_type) || 'residential';

      // ЭТАП 3: Fetch MSIF Lower Bound (for correct Fair Cost Gap calculation)
      console.log('📥 Fetching MSIF lower bound...');
      let msifLowerBound = 700; // fallback
      try {
        if (normalizedPostcode) {
          msifLowerBound = await fetchMSIFForMutation(normalizedPostcode, normalizedCareType);
          console.log(`✅ MSIF lower bound: £${msifLowerBound}/week`);
        }
      } catch (error) {
        console.warn('⚠️ MSIF fetch failed, using fallback:', error);
      }

      // ЭТАП 4: Prepare normalized request data
      const requestData: any = {
        postcode: normalizedPostcode || '',
        budget: questionnaire.budget || 0,
        care_type: normalizedCareType,
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

      // ЭТАП 5: Load care homes from backend
      console.log('📥 Loading care homes from database...');
      
      try {
        const url = API_BASE_URL ? `${API_BASE_URL}/api/free-report` : '/api/free-report';
        
        console.log('📤 Sending free report request:', {
          url,
          postcode: requestData.postcode,
          budget: requestData.budget,
          care_type: requestData.care_type,
          chc_probability: requestData.chc_probability,
        });
        
        const response = await axios.post<any>(url, requestData, {
          timeout: 120000,  // 120 seconds (includes parallel LLM calls)
        });

        console.log('✅ Report generated successfully', {
          care_homes_count: response.data.care_homes?.length || 0,
          report_id: response.data.report_id,
        });
        
        // Debug: Check what we receive from backend
        if (response.data.care_homes && response.data.care_homes.length > 0) {
          const firstHome = response.data.care_homes[0];
          console.log('🔍 [useFreeReportNew] First home from backend:', {
            name: firstHome.name,
            weekly_cost: firstHome.weekly_cost,
            weekly_cost_type: typeof firstHome.weekly_cost,
            has_weekly_cost: 'weekly_cost' in firstHome,
            keys: Object.keys(firstHome).slice(0, 15)
          });
        }

        // ЭТАП 6: Transform backend response to frontend format
        const transformedData = transformBackendResponse(
          response.data,
          msifLowerBound,
          normalizedPostcode || questionnaire.postcode
        );
        
        // Debug: Check what we get after transformation
        if (transformedData.homes && transformedData.homes.length > 0) {
          const firstTransformed = transformedData.homes[0];
          console.log('🔍 [useFreeReportNew] First home after transformation:', {
            name: firstTransformed.name,
            price_range: firstTransformed.price_range,
            avg_price: firstTransformed.price_range ? (firstTransformed.price_range.min + firstTransformed.price_range.max) / 2 : 0
          });
        }

        // ЭТАП 7: Generate funding eligibility if not provided by backend
        const fundingEligibility = transformedData.fundingEligibility || 
          calculateFundingEligibility(questionnaire);

        // ЭТАП 8: Assemble final report
        const report: FreeReportData = {
          homes: transformedData.homes,
          fairCostGap: transformedData.fairCostGap,
          chcTeaserPercent: questionnaire.chc_probability || 50,
          fundingEligibility,
          areaProfile: transformedData.areaProfile,
          areaMap: transformedData.areaMap,
          llmInsights: transformedData.llmInsights,
        };

        return report;
      } catch (error) {
        // Детальная обработка ошибок
        logError(error, 'Free Report generation');
        
        // Check if backend is unavailable - throw user-friendly error
        if (isBackendUnavailable(error)) {
          const errorMessage = getUserFriendlyErrorMessage(error);
          console.error('❌ Backend not available - cannot generate report without real data');
          throw new Error(errorMessage);
        }
        
        // For other errors, throw with user-friendly message
        throw new Error(getUserFriendlyErrorMessage(error));
      }
    },
    mutationKey: ['free-report-new'],
  });
};
