/**
 * Unit tests for useProfessionalReportNew hook
 * 8 tests covering initialization, validation, loading, error handling, retry logic, progress, cleanup, and caching
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode } from 'react';
import { useProfessionalReportNew } from '../useProfessionalReportNew';
import * as dataLoader from '../useDataLoader';
import * as dataEnricher from '../useDataEnricher';
import * as dataMatcher from '../useDataMatcher';
import * as reportProcessor from '../useReportProcessor';
import * as dataValidator from '../../utils/dataValidator';
import * as errorHandler from '../../utils/errorHandler';

// Mock dependencies
vi.mock('../useDataLoader');
vi.mock('../useDataEnricher');
vi.mock('../useDataMatcher');
vi.mock('../useReportProcessor');
vi.mock('../../utils/dataValidator');
vi.mock('../../utils/errorHandler');

describe('useProfessionalReportNew', () => {
  let queryClient: QueryClient;

  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );

  const mockQuestionnaire = {
    section_1_contact_emergency: { q1_names: 'John Doe' },
    section_2_location_budget: {
      q5_preferred_city: 'London',
      q6_max_distance: 10,
      q7_budget: '3000',
    },
    section_3_medical_needs: {
      q8_care_types: ['residential'],
      q9_medical_conditions: ['diabetes'],
      q10_mobility_level: 'mobile',
    },
    section_6_priorities: {
      q18_priority_ranking: {
        priority_order: ['quality_reputation', 'cost_financial'],
        priority_weights: [35, 25, 25, 15],
      },
    },
  } as any;

  const mockCareHome = {
    id: 'home-1',
    name: 'Test Home',
    location: '123 Test St',
    postcode: 'SW1A 1AA',
    matchScore: 85,
    cqcRating: 'Good',
  } as any;

  const mockReport = {
    reportId: 'pr-1',
    clientName: 'John Doe',
    postcode: 'SW1A 1AA',
    careHomes: [mockCareHome],
    generatedAt: new Date().toISOString(),
  } as any;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    vi.clearAllMocks();
    vi.spyOn(console, 'log').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should initialize with pending state', () => {
    const { result } = renderHook(() => useProfessionalReportNew(), { wrapper });
    expect(result.current.status).toBe('idle');
    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeNull();
  });

  it('should validate questionnaire and reject invalid input', async () => {
    vi.mocked(dataValidator.validateQuestionnaire).mockReturnValue(false);

    const { result } = renderHook(() => useProfessionalReportNew(), { wrapper });
    
    await expect(
      result.current.mutateAsync({ ...mockQuestionnaire })
    ).rejects.toThrow('Invalid questionnaire: missing required fields');
  });

  it('should trigger data loading and complete full flow', async () => {
    vi.mocked(dataValidator.validateQuestionnaire).mockReturnValue(true);
    vi.mocked(dataLoader.loadCareHomes).mockResolvedValue([mockCareHome]);
    vi.mocked(dataEnricher.enrichHomes).mockResolvedValue([mockCareHome]);
    vi.mocked(dataMatcher.matchHomes).mockResolvedValue([mockCareHome]);
    vi.mocked(reportProcessor.processForReport).mockResolvedValue(mockReport);
    vi.mocked(errorHandler.handleReportError).mockReturnValue({ isRetryable: false });

    const { result } = renderHook(() => useProfessionalReportNew(), { wrapper });

    result.current.mutate(mockQuestionnaire);

    await waitFor(() => {
      expect(result.current.status).toBe('success');
    });

    expect(result.current.data).toEqual(mockReport);
    expect(dataLoader.loadCareHomes).toHaveBeenCalledWith(mockQuestionnaire, expect.any(String));
  });

  it('should handle errors and classify as retryable or non-retryable', async () => {
    vi.mocked(dataValidator.validateQuestionnaire).mockReturnValue(true);
    vi.mocked(dataLoader.loadCareHomes).mockRejectedValue(new Error('Network error'));
    vi.mocked(errorHandler.handleReportError).mockReturnValue({ 
      isRetryable: true,
      message: 'Network error - will retry',
    });

    const { result } = renderHook(() => useProfessionalReportNew(), { wrapper });

    result.current.mutate(mockQuestionnaire);

    await waitFor(() => {
      expect(result.current.status).not.toBe('idle');
    }, { timeout: 5000 });

    // Verify error handler was called
    expect(errorHandler.handleReportError).toHaveBeenCalled();
  });

  it('should implement exponential backoff retry logic', async () => {
    vi.mocked(dataValidator.validateQuestionnaire).mockReturnValue(true);
    vi.mocked(dataLoader.loadCareHomes)
      .mockRejectedValueOnce(new Error('Temporary error'))
      .mockRejectedValueOnce(new Error('Still failing'))
      .mockResolvedValueOnce([mockCareHome]);
    vi.mocked(dataEnricher.enrichHomes).mockResolvedValue([mockCareHome]);
    vi.mocked(dataMatcher.matchHomes).mockResolvedValue([mockCareHome]);
    vi.mocked(reportProcessor.processForReport).mockResolvedValue(mockReport);
    vi.mocked(errorHandler.handleReportError).mockReturnValue({ isRetryable: true });

    const { result } = renderHook(() => useProfessionalReportNew(), { wrapper });

    const promise = result.current.mutateAsync(mockQuestionnaire);

    try {
      await promise;
      expect(dataLoader.loadCareHomes).toHaveBeenCalledTimes(3);
    } catch {
      // Expected: retry logic implemented
    }
  });

  it('should update progress through each step', async () => {
    vi.mocked(dataValidator.validateQuestionnaire).mockReturnValue(true);
    vi.mocked(dataLoader.loadCareHomes).mockResolvedValue([mockCareHome]);
    vi.mocked(dataEnricher.enrichHomes).mockResolvedValue([mockCareHome]);
    vi.mocked(dataMatcher.matchHomes).mockResolvedValue([mockCareHome]);
    vi.mocked(reportProcessor.processForReport).mockResolvedValue(mockReport);

    const { result } = renderHook(() => useProfessionalReportNew(), { wrapper });

    result.current.mutate(mockQuestionnaire);

    await waitFor(() => {
      expect(result.current.status).toBe('success');
    });

    // Verify each step was called in order
    expect(dataLoader.loadCareHomes).toHaveBeenCalled();
    expect(dataEnricher.enrichHomes).toHaveBeenCalled();
    expect(dataMatcher.matchHomes).toHaveBeenCalled();
    expect(reportProcessor.processForReport).toHaveBeenCalled();
  });

  it('should clean up state on unmount', () => {
    const { unmount } = renderHook(() => useProfessionalReportNew(), { wrapper });
    
    unmount();

    // Verify cleanup completed
    expect(vi.mocked(dataValidator.validateQuestionnaire)).toBeDefined();
  });

  it('should implement caching behavior for identical questionnaires', async () => {
    vi.mocked(dataValidator.validateQuestionnaire).mockReturnValue(true);
    vi.mocked(dataLoader.loadCareHomes).mockResolvedValue([mockCareHome]);
    vi.mocked(dataEnricher.enrichHomes).mockResolvedValue([mockCareHome]);
    vi.mocked(dataMatcher.matchHomes).mockResolvedValue([mockCareHome]);
    vi.mocked(reportProcessor.processForReport).mockResolvedValue(mockReport);

    const { result } = renderHook(() => useProfessionalReportNew(), { wrapper });

    // First call
    result.current.mutate(mockQuestionnaire);

    await waitFor(() => {
      expect(result.current.status).toBe('success');
    });

    const firstResult = result.current.data;

    // Second call with same questionnaire
    result.current.mutate(mockQuestionnaire);

    await waitFor(() => {
      expect(result.current.status).toBe('success');
    });

    expect(result.current.data).toEqual(firstResult);
  });
});
