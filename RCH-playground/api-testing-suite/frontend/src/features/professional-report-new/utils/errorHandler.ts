/**
 * Custom error class for report generation
 */
export class ReportGenerationError extends Error {
  constructor(
    public code: string,
    message: string,
    public details?: any
  ) {
    super(message);
    this.name = 'ReportGenerationError';
  }
}

/**
 * Error codes for different failure scenarios
 */
export const ERROR_CODES = {
  INVALID_QUESTIONNAIRE: 'INVALID_QUESTIONNAIRE',
  LOAD_HOMES_FAILED: 'LOAD_HOMES_FAILED',
  ENRICH_FAILED: 'ENRICH_FAILED',
  MATCH_FAILED: 'MATCH_FAILED',
  PROCESS_FAILED: 'PROCESS_FAILED',
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
};

/**
 * Handle error and return user-friendly message
 * Comprehensive error handling matching old version
 */
export function handleReportError(error: any): {
  code: string;
  message: string;
  userMessage: string;
  isRetryable: boolean;
  details?: any;
} {
  let code = ERROR_CODES.UNKNOWN_ERROR;
  let message = 'An unknown error occurred';
  let userMessage = 'An error occurred. Please try again.';
  let isRetryable = false;
  let details: any = undefined;

  // Check if it's an Axios error (most common)
  if (error && typeof error === 'object' && 'isAxiosError' in error && error.isAxiosError) {
    const axiosError = error as any;
    
    // Check if request was canceled
    if (axiosError.code === 'ERR_CANCELED' || axiosError.message === 'canceled' || axiosError.name === 'CanceledError') {
      code = ERROR_CODES.TIMEOUT_ERROR;
      message = 'Request was canceled';
      userMessage = 'The request was canceled. If this happens repeatedly, the server may not be responding. Please check if the backend server is running.';
      isRetryable = true;
      details = {
        code: axiosError.code,
        aborted: axiosError.request?.signal?.aborted,
        reason: axiosError.request?.signal?.reason,
      };
    }
    // Network error - server not reachable (timeout)
    else if (axiosError.code === 'ECONNABORTED' || axiosError.code === 'ETIMEDOUT' || (axiosError.message && String(axiosError.message).includes('timeout'))) {
      code = ERROR_CODES.TIMEOUT_ERROR;
      message = 'Server request timed out';
      userMessage = 'Server request timed out. The server may be unavailable. Please check if the backend server is running.';
      isRetryable = true;
      details = {
        code: axiosError.code,
        timeout: axiosError.config?.timeout,
        url: axiosError.config?.url,
      };
    }
    // Network error - no connection (including connection refused)
    else if (axiosError.code === 'ERR_NETWORK' || axiosError.code === 'ERR_CONNECTION_REFUSED' || 
             (axiosError.message && String(axiosError.message).includes('Network Error')) || 
             (!axiosError.response && axiosError.code !== 'ERR_CANCELED')) {
      code = ERROR_CODES.NETWORK_ERROR;
      message = 'Cannot connect to server';
      userMessage = 'Cannot connect to backend server. Please make sure the backend server is running. ' +
                    'If using Vite proxy, ensure backend is on port 3001. ' +
                    'If backend is on a different port, set VITE_API_URL environment variable.';
      isRetryable = true; // ✅ Network errors are retryable
      details = {
        code: axiosError.code,
        message: axiosError.message,
        url: axiosError.config?.url,
      };
    }
    // Server responded with error
    else if (axiosError.response) {
      const status = axiosError.response.status;
      const statusText = axiosError.response.statusText;
      const responseData = axiosError.response.data;
      
      if (status === 404) {
        code = ERROR_CODES.LOAD_HOMES_FAILED;
        message = 'Data not found';
        userMessage = 'Some data could not be found. Please try again.';
        isRetryable = true;
      } else if (status >= 500) {
        code = ERROR_CODES.UNKNOWN_ERROR;
        message = 'Server error';
        userMessage = responseData?.detail || responseData?.message || `Server error occurred (${status}). Please try again later.`;
        isRetryable = true;
      } else if (status >= 400) {
        code = ERROR_CODES.INVALID_QUESTIONNAIRE;
        message = 'Request error';
        userMessage = responseData?.detail || responseData?.message || `Invalid request (${status}). Please check your data.`;
        isRetryable = false;
      }
      
      details = {
        status,
        statusText,
        data: responseData,
        url: axiosError.config?.url,
      };
    }
    // Unknown axios error
    else {
      code = ERROR_CODES.UNKNOWN_ERROR;
      message = axiosError.message || 'Unknown axios error';
      userMessage = 'An unexpected error occurred. Please try again.';
      isRetryable = false;
      details = {
        code: axiosError.code,
        message: axiosError.message,
        name: axiosError.name,
        config: axiosError.config,
      };
    }
  }
  // Handle abort errors
  else if (error instanceof Error && error.name === 'AbortError') {
    code = ERROR_CODES.TIMEOUT_ERROR;
    message = 'Request aborted';
    userMessage = 'Server request timed out. The server may be unavailable. Please check if the backend server is running.';
    isRetryable = true;
  }
  // Network errors (TypeError with fetch)
  else if (error instanceof TypeError && String(error.message).indexOf('fetch') >= 0) {
    code = ERROR_CODES.NETWORK_ERROR;
    message = 'Network connection failed';
    userMessage = 'Unable to connect to server. Please check your internet connection.';
    isRetryable = true;
  }
  // Timeout errors (generic)
  else if (error.code === 'ECONNABORTED' || (error.message && String(error.message).indexOf('timeout') >= 0)) {
    code = ERROR_CODES.TIMEOUT_ERROR;
    message = 'Request timeout';
    userMessage = 'The request took too long. Please try again.';
    isRetryable = true;
  }
  // Validation errors
  else if (error.message && String(error.message).indexOf('required') >= 0) {
    code = ERROR_CODES.INVALID_QUESTIONNAIRE;
    message = 'Invalid questionnaire data';
    userMessage = 'Please fill in all required fields in the questionnaire.';
    isRetryable = false;
  }
  // API errors (non-axios)
  else if (error.response?.status) {
    if (error.response.status === 404) {
      code = ERROR_CODES.LOAD_HOMES_FAILED;
      message = 'Data not found';
      userMessage = 'Some data could not be found. Please try again.';
      isRetryable = true;
    } else if (error.response.status >= 500) {
      code = ERROR_CODES.UNKNOWN_ERROR;
      message = 'Server error';
      userMessage = 'Server error occurred. Please try again later.';
      isRetryable = true;
    } else if (error.response.status >= 400) {
      code = ERROR_CODES.INVALID_QUESTIONNAIRE;
      message = 'Request error';
      userMessage = 'Invalid request. Please check your data.';
      isRetryable = false;
    }
    details = {
      status: error.response.status,
      statusText: error.response.statusText,
      data: error.response.data,
    };
  }
  // Parse error message if available
  else if (error instanceof Error) {
    message = error.message;
    userMessage = error.message;
    isRetryable = false;
  }
  
  return {
    code,
    message,
    userMessage: userMessage || message,
    isRetryable,
    details,
  };
}

/**
 * Log error with context
 * Comprehensive logging matching old version
 */
export function logError(error: any, context: string): void {
  const handled = handleReportError(error);
  
  console.error(`❌ Error [${context}]:`);
  console.error(`Code: ${handled.code}`);
  console.error(`Message: ${handled.message}`);
  console.error(`User Message: ${handled.userMessage}`);
  console.error(`Retryable: ${handled.isRetryable}`);
  
  // Detailed error information
  if (handled.details) {
    console.error('Details:', handled.details);
  }
  
  // Stack trace
  if (error?.stack) {
    console.error('Stack:', error.stack);
  }
  
  // Axios-specific details
  if (error && typeof error === 'object' && 'isAxiosError' in error && error.isAxiosError) {
    const axiosError = error as any;
    console.error('Axios error details:', {
      code: axiosError.code,
      message: axiosError.message,
      name: axiosError.name,
      response: axiosError.response ? {
        status: axiosError.response.status,
        statusText: axiosError.response.statusText,
        data: axiosError.response.data
      } : 'No response',
      request: axiosError.request ? 'Request made but no response' : 'No request made',
      config: {
        timeout: axiosError.config?.timeout,
        url: axiosError.config?.url,
        method: axiosError.config?.method,
        signal: axiosError.config?.signal ? 'Has signal' : 'No signal'
      }
    });
  }
  
  // Response data
  if (error?.response?.data) {
    console.error('Response data:', error.response.data);
  }
}

/**
 * Create error boundary component
 */
export function createErrorFallback(error: Error, resetError: () => void) {
  const handled = handleReportError(error);
  
  return {
    title: 'Report Generation Failed',
    message: handled.userMessage,
    action: handled.isRetryable ? 'Try Again' : 'Go Back',
    onAction: resetError,
    canRetry: handled.isRetryable,
  };
}

/**
 * Gracefully handle partial failures
 */
export function handlePartialFailure(failedSteps: string[]): {
  severity: 'warning' | 'error';
  message: string;
  canContinue: boolean;
} {
  if (failedSteps.includes('matching') || failedSteps.includes('process')) {
    return {
      severity: 'error',
      message: 'Critical step failed. Cannot generate report.',
      canContinue: false,
    };
  }

  if (failedSteps.includes('enrich')) {
    return {
      severity: 'warning',
      message: 'Some enrichment data could not be loaded. Report may be incomplete.',
      canContinue: true,
    };
  }

  return {
    severity: 'warning',
    message: 'Some data could not be loaded.',
    canContinue: true,
  };
}
