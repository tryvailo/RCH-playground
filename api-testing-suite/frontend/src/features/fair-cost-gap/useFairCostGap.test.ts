/**
 * Tests for useFairCostGap hook
 * Проверка расчёта на 3 реальных примерах
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useFairCostGap } from './hooks/useFairCostGap';
import * as msifLoader from './msifLoader';

// Mock msifLoader
vi.mock('./msifLoader', () => ({
  getFairCostLower: vi.fn(),
}));

describe('useFairCostGap', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('calculates Fair Cost Gap correctly for Camden nursing', async () => {
    // Camden nursing: msif_lower £1,048 → market £1,912 → gap £864/week
    const mockGetFairCostLower = vi.mocked(msifLoader.getFairCostLower);
    mockGetFairCostLower.mockResolvedValue(1048);

    const { result } = renderHook(() =>
      useFairCostGap({
        marketPrice: 1912,
        localAuthority: 'Camden',
        careType: 'nursing',
      })
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.msifLower).toBe(1048);
    expect(result.current.gapWeekly).toBeCloseTo(864, 0);
    expect(result.current.gapAnnual).toBeCloseTo(864 * 52, 0);
    expect(result.current.gapFiveYear).toBeCloseTo(864 * 52 * 5, 0);
    expect(result.current.gapPercent).toBeCloseTo((864 / 1048) * 100, 1);
    expect(result.current.error).toBeNull();
  });

  it('calculates Fair Cost Gap correctly for Birmingham residential', async () => {
    // Birmingham residential: msif_lower £650 → market £950 → gap £300/week
    const mockGetFairCostLower = vi.mocked(msifLoader.getFairCostLower);
    mockGetFairCostLower.mockResolvedValue(650);

    const { result } = renderHook(() =>
      useFairCostGap({
        marketPrice: 950,
        localAuthority: 'Birmingham',
        careType: 'residential',
      })
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.msifLower).toBe(650);
    expect(result.current.gapWeekly).toBeCloseTo(300, 0);
    expect(result.current.gapAnnual).toBeCloseTo(300 * 52, 0);
    expect(result.current.gapFiveYear).toBeCloseTo(300 * 52 * 5, 0);
    expect(result.current.gapPercent).toBeCloseTo((300 / 650) * 100, 1);
  });

  it('calculates Fair Cost Gap correctly for London dementia', async () => {
    // London dementia: msif_lower £820 → market £1200 → gap £380/week
    const mockGetFairCostLower = vi.mocked(msifLoader.getFairCostLower);
    mockGetFairCostLower.mockResolvedValue(820);

    const { result } = renderHook(() =>
      useFairCostGap({
        marketPrice: 1200,
        localAuthority: 'London',
        careType: 'residential_dementia',
      })
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.msifLower).toBe(820);
    expect(result.current.gapWeekly).toBeCloseTo(380, 0);
    expect(result.current.gapAnnual).toBeCloseTo(380 * 52, 0);
    expect(result.current.gapFiveYear).toBeCloseTo(380 * 52 * 5, 0);
    expect(result.current.gapPercent).toBeCloseTo((380 / 820) * 100, 1);
  });

  it('handles error when MSIF data not found', async () => {
    const mockGetFairCostLower = vi.mocked(msifLoader.getFairCostLower);
    mockGetFairCostLower.mockResolvedValue(null);

    const { result } = renderHook(() =>
      useFairCostGap({
        marketPrice: 1000,
        localAuthority: 'Unknown',
        careType: 'residential',
      })
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toContain('MSIF data not found');
    expect(result.current.gapWeekly).toBe(0);
  });

  it('handles market price lower than MSIF lower bound', async () => {
    const mockGetFairCostLower = vi.mocked(msifLoader.getFairCostLower);
    mockGetFairCostLower.mockResolvedValue(1000);

    const { result } = renderHook(() =>
      useFairCostGap({
        marketPrice: 800,
        localAuthority: 'Test',
        careType: 'residential',
      })
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Gap should be 0 (no overpayment)
    expect(result.current.gapWeekly).toBe(0);
    expect(result.current.gapAnnual).toBe(0);
    expect(result.current.gapFiveYear).toBe(0);
    expect(result.current.gapPercent).toBe(0);
  });

  it('does not calculate when disabled', async () => {
    const mockGetFairCostLower = vi.mocked(msifLoader.getFairCostLower);

    const { result } = renderHook(() =>
      useFairCostGap({
        marketPrice: 1000,
        localAuthority: 'Test',
        careType: 'residential',
        enabled: false,
      })
    );

    // Should not call getFairCostLower when disabled
    expect(mockGetFairCostLower).not.toHaveBeenCalled();
    expect(result.current.isLoading).toBe(false);
  });
});

