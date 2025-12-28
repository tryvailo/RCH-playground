/**
 * Price Extractor Tests
 * Compare with Python implementation
 */

import { extractWeeklyPrice, extractPriceRange } from '@/lib/data-engine/utils/price-extractor';
import { CareHome } from '@/lib/shared/types/care-home';

describe('Price Extractor', () => {
  describe('extractWeeklyPrice', () => {
    it('should extract from weekly_cost field', () => {
      const home: CareHome = {
        id: '1',
        name: 'Test Home',
        postcode: 'SW1A 1AA',
        weeklyCost: 1000,
      };
      expect(extractWeeklyPrice(home, 'residential')).toBe(1000);
    });

    it('should extract from weekly_price field', () => {
      const home: any = {
        id: '1',
        name: 'Test Home',
        postcode: 'SW1A 1AA',
        weekly_price: 1200,
      };
      expect(extractWeeklyPrice(home, 'residential')).toBe(1200);
    });

    it('should extract from care type specific fields', () => {
      const home: any = {
        id: '1',
        name: 'Test Home',
        postcode: 'SW1A 1AA',
        fee_residential_from: 1000,
        fee_nursing_from: 1500,
      };
      expect(extractWeeklyPrice(home, 'residential')).toBe(1000);
      expect(extractWeeklyPrice(home, 'nursing')).toBe(1500);
    });

    it('should return 0 for invalid data', () => {
      expect(extractWeeklyPrice(null as any, 'residential')).toBe(0);
      expect(extractWeeklyPrice({} as any, 'residential')).toBe(0);
    });

    it('should handle various field name formats', () => {
      const home1: any = { weeklyCost: 1000 };
      const home2: any = { weekly_price: 1000 };
      const home3: any = { weekly_cost: 1000 };
      const home4: any = { price_weekly: 1000 };

      expect(extractWeeklyPrice(home1, 'residential')).toBe(1000);
      expect(extractWeeklyPrice(home2, 'residential')).toBe(1000);
      expect(extractWeeklyPrice(home3, 'residential')).toBe(1000);
      expect(extractWeeklyPrice(home4, 'residential')).toBe(1000);
    });
  });

  describe('extractPriceRange', () => {
    it('should extract price range from min/max fields', () => {
      const home: any = {
        price_min: 900,
        price_max: 1100,
      };
      const range = extractPriceRange(home, 'residential');
      expect(range.min).toBe(900);
      expect(range.max).toBe(1100);
    });

    it('should calculate range from base price if min/max not available', () => {
      const home: any = {
        weekly_cost: 1000,
      };
      const range = extractPriceRange(home, 'residential');
      expect(range.min).toBeCloseTo(900, 0); // 1000 * 0.9
      expect(range.max).toBeCloseTo(1100, 0); // 1000 * 1.1
    });

    it('should return 0,0 for homes without price', () => {
      const range = extractPriceRange({} as any, 'residential');
      expect(range.min).toBe(0);
      expect(range.max).toBe(0);
    });
  });
});



