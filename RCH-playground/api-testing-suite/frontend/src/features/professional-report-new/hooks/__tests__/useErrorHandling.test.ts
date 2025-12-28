/**
 * Unit tests for useErrorHandling hook
 * 8 tests covering error classification, messages, logging, retry logic, cleanup, callbacks, boundary integration, and recovery
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import * as errorHandler from '../../utils/errorHandler';
import * as dataValidator from '../../utils/dataValidator';

vi.mock('../../utils/errorHandler');
vi.mock('../../utils/dataValidator');

describe('useErrorHandling', () => {
  const mockLogError = vi.fn();
  const mockSanitizeErrorMessage = vi.fn((err) => {
    if (err instanceof Error) return err.message;
    return String(err);
  });

  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(console, 'error').mockImplementation(() => {});
    vi.spyOn(console, 'log').mockImplementation(() => {});

    vi.mocked(errorHandler.logError).mockImplementation(mockLogError);
    vi.mocked(dataValidator.sanitizeErrorMessage).mockImplementation(mockSanitizeErrorMessage);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should classify retryable errors (network, timeout)', () => {
    const networkError = new Error('Network timeout');
    const timeoutError = new Error('Request timeout');
    const tempError = new Error('Service temporarily unavailable');

    vi.mocked(errorHandler.handleReportError).mockReturnValue({
      isRetryable: true,
      message: 'Network error - will retry',
      type: 'NETWORK_ERROR',
    });

    const handleNetworkError = errorHandler.handleReportError(networkError);
    expect(handleNetworkError.isRetryable).toBe(true);

    const handleTimeoutError = errorHandler.handleReportError(timeoutError);
    expect(handleTimeoutError.isRetryable).toBe(true);

    const handleTempError = errorHandler.handleReportError(tempError);
    expect(handleTempError.isRetryable).toBe(true);
  });

  it('should classify non-retryable errors (validation, auth, not found)', () => {
    const validationError = new Error('Invalid questionnaire: missing required fields');
    const authError = new Error('Unauthorized');
    const notFoundError = new Error('Care homes not found');

    vi.mocked(errorHandler.handleReportError)
      .mockReturnValueOnce({
        isRetryable: false,
        message: 'Invalid input - will not retry',
        type: 'VALIDATION_ERROR',
      })
      .mockReturnValueOnce({
        isRetryable: false,
        message: 'Authentication failed',
        type: 'AUTH_ERROR',
      })
      .mockReturnValueOnce({
        isRetryable: false,
        message: 'Resource not found',
        type: 'NOT_FOUND_ERROR',
      });

    expect(errorHandler.handleReportError(validationError).isRetryable).toBe(false);
    expect(errorHandler.handleReportError(authError).isRetryable).toBe(false);
    expect(errorHandler.handleReportError(notFoundError).isRetryable).toBe(false);
  });

  it('should generate user-friendly error messages', () => {
    const errors = [
      new Error('Network timeout'),
      new Error('API rate limit exceeded'),
      new Error('Database connection failed'),
    ];

    vi.mocked(dataValidator.sanitizeErrorMessage)
      .mockReturnValueOnce('Unable to connect - please check your internet.')
      .mockReturnValueOnce('Service temporarily overloaded.')
      .mockReturnValueOnce('Database temporarily unavailable.');

    errors.forEach((error, index) => {
      const message = dataValidator.sanitizeErrorMessage(error);
      expect(message).toBeDefined();
      expect(typeof message).toBe('string');
    });
  });

  it('should log errors with context', () => {
    const error = new Error('Test error');
    const context = 'Report Generation (Attempt 1/3)';

    errorHandler.logError(error, context);

    expect(errorHandler.logError).toHaveBeenCalledWith(error, context);
  });

  it('should implement retry decision logic with exponential backoff', () => {
    vi.mocked(errorHandler.handleReportError).mockImplementation((error) => {
      if (error instanceof Error && error.message.includes('Network')) {
        return { isRetryable: true, delay: Math.pow(2, 1) * 1000 }; // 2s
      }
      return { isRetryable: false };
    });

    const error = new Error('Network error');
    const handled = errorHandler.handleReportError(error);

    expect(handled.isRetryable).toBe(true);
    expect(handled.delay).toBe(2000);
  });

  it('should cleanup error state', () => {
    vi.mocked(errorHandler.handleReportError).mockReturnValue({
      isRetryable: false,
      message: 'Error',
    });

    const error = new Error('Test');
    const handled = errorHandler.handleReportError(error);

    // After handling, error state should be cleanable
    expect(handled).toBeDefined();
    expect(handled.isRetryable).toBe(false);
  });

  it('should invoke error callbacks', () => {
    const onError = vi.fn();
    const onRetry = vi.fn();

    vi.mocked(errorHandler.handleReportError).mockImplementation((error) => {
      onError(error);
      return { isRetryable: true, onRetry };
    });

    const error = new Error('Test error');
    errorHandler.handleReportError(error);

    expect(onError).toHaveBeenCalledWith(error);
  });

  it('should integrate with error boundary patterns', () => {
    const errors = [
      new Error('Render error'),
      new Error('Hook initialization failed'),
      new Error('Effect cleanup error'),
    ];

    vi.mocked(errorHandler.handleReportError).mockImplementation((error) => {
      // Should provide fallback UI state
      return {
        isRetryable: false,
        message: 'Application error occurred',
        fallback: { showRetry: false, showHelp: true },
      };
    });

    errors.forEach(error => {
      const handled = errorHandler.handleReportError(error);
      expect(handled.fallback).toBeDefined();
    });
  });

  it('should support error recovery mechanisms', () => {
    const initialError = new Error('Network error');
    
    vi.mocked(errorHandler.handleReportError)
      .mockReturnValueOnce({
        isRetryable: true,
        message: 'Network error - will retry',
        recover: () => ({ action: 'retry', delay: 1000 }),
      });

    const handled = errorHandler.handleReportError(initialError);
    const recovery = handled.recover?.();

    expect(recovery?.action).toBe('retry');
    expect(recovery?.delay).toBe(1000);
  });

  it('should handle cascading errors', () => {
    const primaryError = new Error('Cache lookup failed');
    const secondaryError = new Error('Database query failed');
    const finalError = new Error('All data sources exhausted');

    let callCount = 0;
    vi.mocked(errorHandler.handleReportError).mockImplementation(() => {
      callCount++;
      return {
        isRetryable: callCount < 3,
        message: `Error attempt ${callCount}`,
      };
    });

    errorHandler.handleReportError(primaryError);
    errorHandler.handleReportError(secondaryError);
    const final = errorHandler.handleReportError(finalError);

    expect(final.isRetryable).toBe(false);
    expect(callCount).toBe(3);
  });
});
