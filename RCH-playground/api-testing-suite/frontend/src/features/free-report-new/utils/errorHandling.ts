/**
 * Error handling utilities for Free Report
 * Provides detailed error logging and user-friendly error messages
 */

import axios from 'axios';

/**
 * Detailed error information interface
 */
export interface ErrorDetails {
  message: string;
  code?: string;
  status?: number;
  statusText?: string;
  data?: any;
  url?: string;
  isNetworkError: boolean;
  isBackendError: boolean;
  isTimeout: boolean;
}

/**
 * Analyze and extract detailed error information
 * 
 * @param error - Error object (can be AxiosError or generic Error)
 * @returns ErrorDetails with all available information
 */
export const analyzeError = (error: unknown): ErrorDetails => {
  const defaultDetails: ErrorDetails = {
    message: error instanceof Error ? error.message : 'Unknown error occurred',
    isNetworkError: false,
    isBackendError: false,
    isTimeout: false,
  };

  if (axios.isAxiosError(error)) {
    const isTimeoutError = error.code === 'ETIMEDOUT' || error.code === 'ECONNABORTED';
    
    return {
      message: error.message,
      code: error.code,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      url: error.config?.url,
      isNetworkError: 
        error.code === 'ECONNREFUSED' ||
        error.code === 'ERR_NETWORK' ||
        isTimeoutError,
      isBackendError: 
        error.response?.status !== undefined &&
        error.response.status >= 400,
      isTimeout: isTimeoutError,
    };
  }

  return defaultDetails;
};

/**
 * Log detailed error information to console
 * 
 * @param error - Error object
 * @param context - Additional context string (e.g., "Free Report generation")
 */
export const logError = (error: unknown, context: string = 'Free Report'): void => {
  const details = analyzeError(error);
  
  console.error(`❌ ${context} error:`, {
    message: details.message,
    code: details.code,
    status: details.status,
    statusText: details.statusText,
    data: details.data,
    url: details.url,
    isNetworkError: details.isNetworkError,
    isBackendError: details.isBackendError,
    isTimeout: details.isTimeout,
  });
};

/**
 * Create user-friendly error message
 * 
 * @param error - Error object
 * @returns User-friendly error message string
 */
export const getUserFriendlyErrorMessage = (error: unknown): string => {
  const details = analyzeError(error);
  
  if (details.isNetworkError) {
    return 'Cannot connect to server. Please check your internet connection and try again.';
  }
  
  if (details.isTimeout) {
    return 'Request timed out. The server is taking too long to respond. Please try again.';
  }
  
  if (details.isBackendError) {
    if (details.status === 404) {
      return 'The requested resource was not found. Please check your input and try again.';
    }
    if (details.status === 500) {
      return 'Server error occurred. Please try again later or contact support.';
    }
    return `Server error (${details.status}): ${details.statusText || details.message}`;
  }
  
  return `An error occurred: ${details.message}`;
};

/**
 * Check if error indicates backend is not available
 * Should throw error instead of using fallback data
 */
export const isBackendUnavailable = (error: unknown): boolean => {
  const details = analyzeError(error);
  
  return (
    details.isNetworkError ||
    details.status === 404 ||
    details.status === 500
  );
};

