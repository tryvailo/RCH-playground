import { useMutation, useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { useEffect, useRef } from 'react';
import type { ProfessionalQuestionnaireResponse, ProfessionalReportResponse, ProfessionalReportData } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface JobStatusResponse {
  job_id: string;
  report_id: string;
  status: 'pending' | 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  started_at: string;
  completed_at?: string;
  result?: ProfessionalReportResponse;
  error?: string;
}

// Response can be either async (job_id) or legacy sync (report)
type ProfessionalReportResponse = 
  | { job_id: string; report_id: string; status: string; message: string }
  | { questionnaire: any; report: ProfessionalReportData; generated_at: string; report_id: string; status: 'completed' };

export const useGenerateProfessionalReport = () => {
  return useMutation<ProfessionalReportResponse, Error, ProfessionalQuestionnaireResponse>({
    mutationFn: async (questionnaire: ProfessionalQuestionnaireResponse) => {
      try {
        console.log('Sending request to:', `${API_BASE_URL}/api/professional-report`);
        const response = await axios.post<ProfessionalReportResponse>(
          `${API_BASE_URL}/api/professional-report`,
          questionnaire,
          {
            headers: {
              'Content-Type': 'application/json',
            },
          }
        );

        console.log('Response status:', response.status);
        console.log('Response data:', response.data);
        console.log('Response data type:', typeof response.data);
        console.log('Response data keys:', Object.keys(response.data || {}));

        // Return response (can be job_id or legacy report)
        return response.data;
      } catch (error) {
        if (axios.isAxiosError(error)) {
          const message = error.response?.data?.detail || error.message || 'Failed to start professional report generation';
          throw new Error(message);
        }
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

      try {
        console.log('Polling job status for jobId:', jobId);
        const response = await axios.get<JobStatusResponse>(
          `${API_BASE_URL}/api/professional-report/status/${jobId}`
        );

        console.log('Status response:', response.data);
        return response.data;
      } catch (error) {
        console.error('Error polling job status:', error);
        throw error;
      }
    },
    enabled: isEnabled,
    retry: 3,
    retryDelay: 1000,
    refetchInterval: (query) => {
      if (!isEnabled) {
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
  
  const { data: status, error, isLoading } = useCheckProfessionalReportStatus(jobId, enabled);
  const completedRef = useRef(false);
  
  useEffect(() => {
    console.log('usePollProfessionalReport - jobId changed:', jobId, 'enabled:', enabled, 'isLoading:', isLoading);
  }, [jobId, enabled, isLoading]);

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

  // Handle polling errors
  useEffect(() => {
    if (!enabled || completedRef.current || !error) {
      return;
    }
    
    completedRef.current = true;
    console.log('Polling error, calling onError');
    onError(error);
  }, [error, enabled, onError]);
  
  // Reset completedRef when jobId changes (new job started)
  useEffect(() => {
    completedRef.current = false;
  }, [jobId]);

  return {
    status: status?.status,
    progress: status?.progress ?? 0,
    message: status?.message ?? '',
    isLoading: status?.status === 'processing' || status?.status === 'queued',
    isError: !!error || status?.status === 'failed',
  };
};
