/**
 * Fair Cost Gap Service Tests
 * Compare with Python implementation
 */

import { FairCostGapService } from '@/lib/reports/free-report/fair-cost-gap';

describe('FairCostGapService', () => {
  let service: FairCostGapService;

  beforeEach(() => {
    service = new FairCostGapService();
  });

  describe('calculateGap', () => {
    it('should calculate gap correctly for nursing care', () => {
      const result = service.calculateGap(
        1912, // market price
        1048, // MSIF lower bound
        'nursing'
      );

      expect(result.gap_week).toBeCloseTo(864, 0); // 1912 - 1048
      expect(result.gap_year).toBeCloseTo(44928, 0); // 864 * 52
      expect(result.gap_5year).toBeCloseTo(224640, 0); // 44928 * 5
      expect(result.gap_percent).toBeCloseTo(82.4, 0); // (864 / 1048) * 100
      expect(result.market_price).toBe(1912);
      expect(result.msif_lower_bound).toBe(1048);
    });

    it('should calculate gap correctly for residential care', () => {
      const result = service.calculateGap(
        1200, // market price
        700, // MSIF lower bound
        'residential'
      );

      expect(result.gap_week).toBeCloseTo(500, 0);
      expect(result.gap_year).toBeCloseTo(26000, 0);
      expect(result.gap_5year).toBeCloseTo(130000, 0);
      expect(result.gap_percent).toBeCloseTo(71.4, 0);
    });

    it('should handle negative gap (market price below MSIF)', () => {
      const result = service.calculateGap(
        600, // market price (below MSIF)
        700, // MSIF lower bound
        'residential'
      );

      expect(result.gap_week).toBeCloseTo(-100, 0);
      expect(result.gap_year).toBeCloseTo(-5200, 0);
      expect(result.gap_5year).toBeCloseTo(-26000, 0);
      expect(result.gap_percent).toBeCloseTo(-14.3, 0);
    });

    it('should generate recommendations based on gap size', () => {
      const largeGap = service.calculateGap(2000, 700, 'residential');
      expect(largeGap.recommendations.length).toBeGreaterThan(0);
      expect(largeGap.recommendations).toContain(
        'Use MSIF data to negotiate lower fees'
      );

      const smallGap = service.calculateGap(800, 700, 'residential');
      expect(smallGap.recommendations.length).toBeGreaterThan(0);
    });

    it('should format gap text correctly', () => {
      const positiveGap = service.calculateGap(1200, 700, 'residential');
      expect(positiveGap.gap_text).toContain('Переплата');

      const negativeGap = service.calculateGap(600, 700, 'residential');
      expect(negativeGap.gap_text).toContain('Экономия');
    });

    it('should handle zero MSIF lower bound', () => {
      const result = service.calculateGap(1000, 0, 'residential');
      expect(result.gap_percent).toBe(0);
      expect(result.gap_week).toBe(1000);
    });
  });

  describe('MSIF defaults', () => {
    it('should use correct MSIF defaults for each care type', () => {
      const residential = service.calculateGap(1000, 700, 'residential');
      expect(residential.msif_lower_bound).toBe(700);

      const nursing = service.calculateGap(1000, 1048, 'nursing');
      expect(nursing.msif_lower_bound).toBe(1048);

      const dementia = service.calculateGap(1000, 800, 'dementia');
      expect(dementia.msif_lower_bound).toBe(800);

      const respite = service.calculateGap(1000, 700, 'respite');
      expect(respite.msif_lower_bound).toBe(700);
    });
  });
});



