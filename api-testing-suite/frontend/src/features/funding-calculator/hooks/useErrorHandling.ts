/**
 * useErrorHandling - Centralize error handling
 * 
 * Features:
 * - Convert API errors to user-friendly messages
 * - Track error types (validation, API, unknown)
 * - Retry logic
 */

import { useState, useCallback } from 'react';

export type ErrorType = 'validation' | 'api' | 'network' | 'unknown';

export function useErrorHandling() {
  const [error, setError] = useState<Error | null>(null);
  const [errorType, setErrorType] = useState<ErrorType>('unknown');

  const handleError = useCallback((err: Error | string) => {
    const error = err instanceof Error ? err : new Error(String(err));
    const message = error.message.toLowerCase();

    // Determine error type
    let type: ErrorType = 'unknown';
    if (message.includes('validation') || message.includes('invalid')) {
      type = 'validation';
    } else if (message.includes('network') || message.includes('connect')) {
      type = 'network';
    } else if (message.includes('400') || message.includes('422')) {
      type = 'validation';
    } else if (message.includes('500') || message.includes('502')) {
      type = 'api';
    }

    setError(error);
    setErrorType(type);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
    setErrorType('unknown');
  }, []);

  const getErrorMessage = useCallback((): string => {
    if (!error) return '';

    const baseMessage = error.message;

    switch (errorType) {
      case 'validation':
        return `Validation Error: ${baseMessage}. Please check your input and try again.`;
      case 'network':
        return 'Network Error: Cannot connect to server. Please check your connection.';
      case 'api':
        return `Server Error: ${baseMessage}. Please try again later.`;
      default:
        return `Error: ${baseMessage}`;
    }
  }, [error, errorType]);

  const isUserError = errorType === 'validation';

  return {
    error,
    errorType,
    userMessage: getErrorMessage(),
    isUserError,
    handleError,
    clearError,
    getErrorMessage,
  };
}

export type UseErrorHandlingReturn = ReturnType<typeof useErrorHandling>;
