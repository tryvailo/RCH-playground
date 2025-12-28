/**
 * Hook for Free Report generation with Server-Sent Events (SSE)
 * Provides real-time progress updates during report generation
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import type { QuestionnaireResponse, FreeReportData } from '../types';
import { normalizePostcode, normalizeCareType } from '../utils/normalization';
import { transformBackendResponse } from '../utils/transform';
import { calculateFundingEligibility } from '../utils/fundingEligibility';
import { fetchMSIFForMutation } from './useMSIF';

const API_BASE_URL = (import.meta.env as any).VITE_API_URL || '';

export interface ProgressUpdate {
  step: string;
  progress: number;
  message: string;
  data?: any;
  timestamp?: string;
}

export interface StreamReportState {
  isLoading: boolean;
  progress: ProgressUpdate | null;
  report: FreeReportData | null;
  error: Error | null;
}

/**
 * Hook for generating Free Report with real-time progress via SSE
 */
export const useFreeReportStream = () => {
  const [state, setState] = useState<StreamReportState>({
    isLoading: false,
    progress: null,
    report: null,
    error: null,
  });

  const eventSourceRef = useRef<EventSource | null>(null);
  const msifLowerBoundRef = useRef<number>(700);

  const generateReport = useCallback(async (questionnaire: QuestionnaireResponse) => {
    // Reset state and set initial progress
    setState({
      isLoading: true,
      progress: {
        step: 'initialization',
        progress: 0,
        message: 'Starting report generation...',
      },
      report: null,
      error: null,
    });

    // Normalize data
    const normalizedPostcode = normalizePostcode(
      questionnaire.postcode || questionnaire.location_postcode
    );
    const normalizedCareType = normalizeCareType(questionnaire.care_type) || 'residential';

    // Fetch MSIF in background
    if (normalizedPostcode) {
      try {
        msifLowerBoundRef.current = await fetchMSIFForMutation(normalizedPostcode, normalizedCareType);
      } catch (error) {
        console.warn('MSIF fetch failed, using fallback:', error);
      }
    }

    return new Promise<FreeReportData>(async (resolve, reject) => {
      // Prepare request data
      const requestData = {
        postcode: normalizedPostcode || '',
        budget: questionnaire.budget || 0,
        care_type: normalizedCareType,
        chc_probability: questionnaire.chc_probability || 35,
        location_postcode: normalizePostcode(questionnaire.location_postcode) || undefined,
        timeline: questionnaire.timeline || undefined,
        medical_conditions: questionnaire.medical_conditions || [],
        max_distance_km: questionnaire.max_distance_km || 30,
        priority_order: questionnaire.priority_order || ['quality', 'cost', 'proximity'],
        priority_weights: questionnaire.priority_weights || [40, 35, 25],
      };

      // Create EventSource for SSE
      const url = API_BASE_URL 
        ? `${API_BASE_URL}/api/free-report-stream` 
        : '/api/free-report-stream';

      // For POST with SSE, we need to use fetch with ReadableStream
      // Since EventSource only supports GET, we'll use fetch API
      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestData),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error('No response body');
        }

        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                // Update progress
                setState((prev) => ({
                  ...prev,
                  progress: {
                    step: data.step,
                    progress: data.progress,
                    message: data.message,
                    data: data.data,
                    timestamp: data.timestamp,
                  },
                }));

                // Handle completion
                if (data.step === 'complete' && data.report) {
                  // Transform backend response
                  const transformedData = transformBackendResponse(
                    data.report,
                    msifLowerBoundRef.current,
                    normalizedPostcode || questionnaire.postcode
                  );

                  // Generate funding eligibility if not provided
                  const fundingEligibility = transformedData.fundingEligibility || 
                    calculateFundingEligibility(questionnaire);

                  const finalReport: FreeReportData = {
                    homes: transformedData.homes,
                    fairCostGap: transformedData.fairCostGap,
                    chcTeaserPercent: questionnaire.chc_probability || 50,
                    fundingEligibility,
                    areaProfile: transformedData.areaProfile,
                    areaMap: transformedData.areaMap,
                    llmInsights: transformedData.llmInsights,
                  };

                  setState({
                    isLoading: false,
                    progress: {
                      step: 'complete',
                      progress: 100,
                      message: 'Report generated successfully',
                    },
                    report: finalReport,
                    error: null,
                  });

                  resolve(finalReport);
                  return;
                }

                // Handle errors
                if (data.step === 'error') {
                  const error = new Error(data.message || 'Report generation failed');
                  setState({
                    isLoading: false,
                    progress: null,
                    report: null,
                    error,
                  });
                  reject(error);
                  return;
                }
              } catch (parseError) {
                console.warn('Failed to parse SSE data:', parseError);
              }
            }
          }
        }
      } catch (error) {
        setState({
          isLoading: false,
          progress: null,
          report: null,
          error: error instanceof Error ? error : new Error(String(error)),
        });
        reject(error);
      }
    });
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  return {
    ...state,
    generateReport,
  };
};
