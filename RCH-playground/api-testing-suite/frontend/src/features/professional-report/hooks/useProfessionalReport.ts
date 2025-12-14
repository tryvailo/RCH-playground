import { useMutation, useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { useEffect, useRef } from 'react';
import type { ProfessionalQuestionnaireResponse, ProfessionalReportData } from '../types';

// Use relative path through Vite proxy, fallback to direct connection
const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || '';

interface JobStatusResponse {
  job_id: string;
  report_id: string;
  status: 'pending' | 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  started_at: string;
  completed_at?: string;
  result?: {
    questionnaire: any;
    report: ProfessionalReportData;
    generated_at: string;
    report_id: string;
    status: 'completed';
  };
  error?: string;
}

// Response can be either async (job_id) or legacy sync (report)
type ProfessionalReportResponse = 
  | { job_id: string; report_id: string; status: string; message: string }
  | { questionnaire: any; report: ProfessionalReportData; generated_at: string; report_id: string; status: 'completed' };

export const useGenerateProfessionalReport = () => {
  return useMutation<ProfessionalReportResponse, Error, ProfessionalQuestionnaireResponse>({
    // Prevent React Query from canceling the mutation
    retry: false, // Don't retry on error - let user retry manually
    mutationFn: async (questionnaire: ProfessionalQuestionnaireResponse) => {
      let timeoutId: ReturnType<typeof setTimeout> | undefined;
      let controller: AbortController | undefined;
      try {
        console.log('🚀 useGenerateProfessionalReport - Starting report generation');
        console.log('Sending request to:', `${API_BASE_URL}/api/professional-report`);
        console.log('API_BASE_URL:', API_BASE_URL);
        console.log('Questionnaire keys:', Object.keys(questionnaire || {}));
        
        // Check if server is reachable first (quick health check)
        try {
          const healthUrl = API_BASE_URL ? `${API_BASE_URL}/health` : '/health';
          await axios.get(healthUrl, { timeout: 2000 }).then(() => {
            console.log('✅ Server health check passed');
          }).catch(() => {
            // Health check failed silently - server might be up but health endpoint slow/unavailable
            // This is non-critical, so we continue with the request
          });
        } catch (healthError) {
          // Health check failed silently - continue anyway
        }
        
        // Check if server is reachable first
        controller = new AbortController();
        // Professional report generation can take 5-10 minutes due to multiple API calls and data enrichment
        const REPORT_TIMEOUT = 600000; // 10 minutes (600 seconds) - increased for complex reports
        timeoutId = setTimeout(() => {
          console.error(`⏰ Request timeout after ${REPORT_TIMEOUT / 1000} seconds - aborting`);
          controller.abort();
        }, REPORT_TIMEOUT);
        
        const url = API_BASE_URL ? `${API_BASE_URL}/api/professional-report` : '/api/professional-report';
        console.log('Using API URL:', url);
        console.log('Request payload size:', JSON.stringify(questionnaire).length, 'bytes');
        
        console.log('📤 Sending POST request to:', url);
        console.log('Request config:', {
          timeout: 60000,
          hasSignal: !!controller.signal,
          headers: { 'Content-Type': 'application/json' }
        });
        
        const requestStartTime = Date.now();
        console.log('⏳ Calling axios.post at:', new Date().toISOString());
        
        let response;
        try {
          response = await axios.post<ProfessionalReportResponse>(
            url,
            questionnaire,
            {
              headers: {
                'Content-Type': 'application/json',
              },
              signal: controller.signal,
              timeout: 600000, // 10 minutes timeout for report generation (can take time due to multiple API calls and data enrichment)
            }
          );
          
          const requestDuration = Date.now() - requestStartTime;
          console.log(`✅ Request completed in ${requestDuration}ms`);
          console.log('📥 Response received! Status:', response.status, response.statusText);
        } catch (axiosError) {
          const requestDuration = Date.now() - requestStartTime;
          console.error(`❌ Request failed after ${requestDuration}ms`);
          console.error('Axios error caught in inner try-catch:', axiosError);
          throw axiosError; // Re-throw to be handled by outer catch
        }

        if (timeoutId) {
          clearTimeout(timeoutId);
        }

        // Check if we got a valid response
        if (!response || !response.data) {
          throw new Error('Server returned an empty response. Please check if the server is running.');
        }

        console.log('✅ Response received - status:', response.status);
        console.log('Response data:', response.data);
        console.log('Response data type:', typeof response.data);
        console.log('Response data keys:', Object.keys(response.data || {}));
        
        // Log specific fields to help debug
        if (response.data && typeof response.data === 'object') {
          console.log('Has job_id?', 'job_id' in response.data, response.data.job_id);
          console.log('Has report?', 'report' in response.data, !!(response.data as any).report);
          console.log('Has status?', 'status' in response.data, (response.data as any).status);
        }

        // Return response (can be job_id or legacy report)
        return response.data;
      } catch (error) {
        console.error('❌ Error in useGenerateProfessionalReport:', error);
        
        if (timeoutId) {
          clearTimeout(timeoutId);
        }
        
        if (axios.isAxiosError(error)) {
          console.error('Axios error details:', {
            code: error.code,
            message: error.message,
            name: error.name,
            response: error.response ? {
              status: error.response.status,
              statusText: error.response.statusText,
              data: error.response.data
            } : 'No response',
            request: error.request ? 'Request made but no response' : 'No request made',
            config: {
              timeout: error.config?.timeout,
              signal: error.config?.signal ? 'Has signal' : 'No signal'
            }
          });
          
          // Check if request was canceled
          if (error.code === 'ERR_CANCELED' || error.message === 'canceled' || error.name === 'CanceledError') {
            console.error('❌ Request was canceled');
            if (controller) {
              console.error('Controller aborted:', controller.signal.aborted);
              console.error('Controller reason:', controller.signal.reason);
              
              // Check if it was canceled due to timeout
              if (controller.signal.aborted) {
                const errMsg = 'Server request timed out after 10 minutes. The report generation is taking longer than expected. This may be due to slow API responses or a large number of care homes to analyze. Please try again or contact support.';
                console.error('❌ Request canceled due to timeout:', errMsg);
                throw new Error(errMsg);
              }
            } else {
              // Request was canceled for another reason (component unmount, React Query cancellation, etc.)
              // This is often normal behavior - don't show it as an error to the user
              const errMsg = 'Request was canceled. If this happens repeatedly, the server may not be responding. Please check if the backend server is running on http://localhost:8000';
              console.warn('⚠️ Request canceled (not timeout - likely React Query or component unmount):', errMsg);
              // Still throw to let React Query handle it, but with a more helpful message
              throw new Error(errMsg);
            }
          }
          
          // Network error - server not reachable
          if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT' || error.message.includes('timeout')) {
            const errMsg = 'Server request timed out. The server may be unavailable. Please check if the backend server is running.';
            console.error('❌ Timeout error:', errMsg);
            throw new Error(errMsg);
          }
          
          // Network error - no connection
          if (error.code === 'ERR_NETWORK' || error.message.includes('Network Error') || (!error.response && error.code !== 'ERR_CANCELED')) {
            const errMsg = 'Cannot connect to server. Please check if the backend server is running and accessible.';
            console.error('❌ Network error:', errMsg);
            console.error('Error code:', error.code);
            console.error('Error message:', error.message);
            throw new Error(errMsg);
          }
          
          // Server responded with error
          if (error.response) {
            const message = error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to start professional report generation';
            console.error('❌ Server error response:', {
              status: error.response.status,
              statusText: error.response.statusText,
              data: error.response.data,
              message
            });
            throw new Error(message);
          }
          
          const errMsg = error.message || 'Failed to start professional report generation';
          console.error('❌ Unknown axios error:', errMsg);
          throw new Error(errMsg);
        }
        
        // Handle abort errors
        if (error instanceof Error && error.name === 'AbortError') {
          const errMsg = 'Server request timed out. The server may be unavailable. Please check if the backend server is running.';
          console.error('❌ Abort error:', errMsg);
          throw new Error(errMsg);
        }
        
        console.error('❌ Unknown error type:', typeof error, error);
        throw error;
      }
    },
  });
};

export const useCheckProfessionalReportStatus = (jobId: string | null, enabled: boolean = true) => {
  const isEnabled = enabled && !!jobId;
  
  return useQuery<JobStatusResponse, Error>({
    queryKey: ['professional-report-status', jobId],
    queryFn: async () => {
      if (!jobId) {
        throw new Error('Job ID is required');
      }

      let timeoutId: ReturnType<typeof setTimeout> | undefined;
      try {
        console.log('Polling job status for jobId:', jobId);
        
        // Check if server is reachable with timeout
        const controller = new AbortController();
        timeoutId = setTimeout(() => controller.abort(), 8000); // 8 second timeout for polling
        
        const url = API_BASE_URL ? `${API_BASE_URL}/api/professional-report/status/${jobId}` : `/api/professional-report/status/${jobId}`;
        const response = await axios.get<JobStatusResponse>(
          url,
          {
            signal: controller.signal,
            timeout: 8000, // 8 second timeout
          }
        );

        if (timeoutId) {
          clearTimeout(timeoutId);
        }

        // Check if we got a valid response
        if (!response || !response.data) {
          throw new Error('Server returned an empty response. Please check if the server is running.');
        }

        console.log('Status response:', response.data);
        return response.data;
      } catch (error) {
        if (timeoutId) {
          clearTimeout(timeoutId);
        }
        console.error('Error polling job status:', error);
        
        if (axios.isAxiosError(error)) {
          // Network error - server not reachable
          if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT' || error.message.includes('timeout')) {
            throw new Error('Server request timed out. The server may be unavailable. Please check if the backend server is running.');
          }
          
          // Network error - no connection
          if (error.code === 'ERR_NETWORK' || error.message.includes('Network Error') || !error.response) {
            throw new Error('Cannot connect to server. Please check if the backend server is running and accessible.');
          }
          
          // Server responded with error
          if (error.response) {
            const message = error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to check report status';
            throw new Error(message);
          }
          
          throw new Error(error.message || 'Failed to check report status');
        }
        
        // Handle abort errors
        if (error instanceof Error && error.name === 'AbortError') {
          throw new Error('Server request timed out. The server may be unavailable. Please check if the backend server is running.');
        }
        
        throw error;
      }
    },
    enabled: isEnabled,
    retry: 2, // Reduce retries to fail faster
    retryDelay: 1000,
    refetchInterval: (query) => {
      if (!isEnabled) {
        return false;
      }
      
      // Stop polling if there's an error
      if (query.state.error) {
        console.log('Polling stopped due to error:', query.state.error);
        return false;
      }
      
      const data = query.state.data;
      // Poll every 2 seconds if processing, stop if completed or failed
      if (data?.status === 'processing' || data?.status === 'queued' || data?.status === 'pending') {
        console.log('Polling active, status:', data?.status);
        return 2000;
      }
      console.log('Polling stopped, status:', data?.status);
      return false;
    },
  });
};

export const usePollProfessionalReport = (jobId: string | null, onComplete: (data: ProfessionalReportData) => void, onError: (error: Error) => void) => {
  const enabled = !!jobId;
  console.log('usePollProfessionalReport called with jobId:', jobId, 'enabled:', enabled);
  
  const { data: status, error, isLoading, isError } = useCheckProfessionalReportStatus(jobId, enabled);
  const completedRef = useRef(false);
  
  useEffect(() => {
    console.log('usePollProfessionalReport - jobId changed:', jobId, 'enabled:', enabled, 'isLoading:', isLoading, 'isError:', isError);
  }, [jobId, enabled, isLoading, isError]);

  // Handle completed status
  useEffect(() => {
    if (!enabled || completedRef.current || !status) {
      return;
    }
    
    if (status.status === 'completed' && status.result) {
      completedRef.current = true;
      console.log('Report completed, calling onComplete');
      onComplete(status.result.report);
    } else if (status.status === 'failed') {
      completedRef.current = true;
      console.log('Report failed, calling onError');
      onError(new Error(status.error || 'Report generation failed'));
    }
  }, [status, enabled, onComplete, onError]);

  // Handle polling errors - check for server connectivity issues
  useEffect(() => {
    if (!enabled || completedRef.current || !error) {
      return;
    }
    
    // Check if it's a server connectivity error
    const errorMessage = error instanceof Error ? error.message : String(error);
    const isServerError = errorMessage.includes('Cannot connect to server') || 
                         errorMessage.includes('Server request timed out') ||
                         errorMessage.includes('server is running');
    
    if (isServerError) {
      completedRef.current = true;
      console.log('Server connectivity error detected, calling onError');
      onError(error instanceof Error ? error : new Error(errorMessage));
    } else if (isError) {
      // Only mark as completed for non-connectivity errors after a delay
      // to allow for retries
      const timeoutId = setTimeout(() => {
        if (!completedRef.current) {
          completedRef.current = true;
          console.log('Polling error after retries, calling onError');
          onError(error instanceof Error ? error : new Error(errorMessage));
        }
      }, 5000); // Wait 5 seconds before giving up
      
      return () => clearTimeout(timeoutId);
    }
  }, [error, enabled, onError, isError]);
  
  // Reset completedRef when jobId changes (new job started)
  useEffect(() => {
    completedRef.current = false;
  }, [jobId]);

  return {
    status: status?.status,
    progress: status?.progress ?? 0,
    message: status?.message ?? '',
    isLoading: (status?.status === 'processing' || status?.status === 'queued' || status?.status === 'pending') && !isError,
    isError: isError || status?.status === 'failed',
    error: error,
  };
};
