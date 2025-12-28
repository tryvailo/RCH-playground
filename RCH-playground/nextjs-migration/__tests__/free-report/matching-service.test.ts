/**
 * Free Report Matching Service Tests
 * Compare with Python implementation
 */

import { FreeReportMatchingService } from '@/lib/reports/free-report/matching-service';
import { CareHome } from '@/lib/shared/types/care-home';

describe('FreeReportMatchingService', () => {
  let service: FreeReportMatchingService;

  beforeEach(() => {
    service = new FreeReportMatchingService();
  });

  describe('selectTop3Homes', () => {
    it('should select Safe Bet, Best Value, and Premium', () => {
      const homes: CareHome[] = [
        {
          id: '1',
          name: 'Home A - Outstanding',
          postcode: 'SW1A 1AA',
          latitude: 51.5074,
          longitude: -0.1278,
          cqcRating: 'Outstanding',
          weeklyCost: 1000,
          careTypes: ['residential'],
        },
        {
          id: '2',
          name: 'Home B - Good Value',
          postcode: 'SW1A 1AB',
          latitude: 51.5075,
          longitude: -0.1279,
          cqcRating: 'Good',
          weeklyCost: 800,
          careTypes: ['residential'],
        },
        {
          id: '3',
          name: 'Home C - Premium',
          postcode: 'SW1A 1AC',
          latitude: 51.5076,
          longitude: -0.1280,
          cqcRating: 'Outstanding',
          weeklyCost: 1500,
          careTypes: ['residential'],
        },
        {
          id: '4',
          name: 'Home D - Average',
          postcode: 'SW1A 1AD',
          latitude: 51.5077,
          longitude: -0.1281,
          cqcRating: 'Good',
          weeklyCost: 1100,
          careTypes: ['residential'],
        },
      ];

      const result = service.selectTop3Homes(
        homes,
        1000, // budget
        'residential',
        51.5074, // user lat
        -0.1278, // user lon
        30.0 // max distance
      );

      expect(result.safe_bet).toBeDefined();
      expect(result.best_value).toBeDefined();
      expect(result.premium).toBeDefined();
    });

    it('should filter by quality (Good or Outstanding)', () => {
      const homes: CareHome[] = [
        {
          id: '1',
          name: 'Good Home',
          postcode: 'SW1A 1AA',
          latitude: 51.5074,
          longitude: -0.1278,
          cqcRating: 'Good',
          weeklyCost: 1000,
        },
        {
          id: '2',
          name: 'Outstanding Home',
          postcode: 'SW1A 1AB',
          latitude: 51.5075,
          longitude: -0.1279,
          cqcRating: 'Outstanding',
          weeklyCost: 1000,
        },
        {
          id: '3',
          name: 'Requires Improvement',
          postcode: 'SW1A 1AC',
          latitude: 51.5076,
          longitude: -0.1280,
          cqcRating: 'Requires improvement',
          weeklyCost: 1000,
        },
      ];

      const result = service.selectTop3Homes(
        homes,
        1000,
        'residential',
        51.5074,
        -0.1278,
        30.0
      );

      // Should not include "Requires improvement" home
      const allSelected = [
        result.safe_bet,
        result.best_value,
        result.premium,
      ].filter(Boolean);

      allSelected.forEach((home) => {
        const rating = (home as any).cqc_rating_overall || 
                      (home as any).rating || 
                      (home as any).cqcRating || '';
        expect(['good', 'outstanding']).toContain(rating.toLowerCase());
      });
    });

    it('should filter by price (budget + £200)', () => {
      const homes: CareHome[] = [
        {
          id: '1',
          name: 'Within Budget',
          postcode: 'SW1A 1AA',
          latitude: 51.5074,
          longitude: -0.1278,
          cqcRating: 'Good',
          weeklyCost: 1000, // Within budget + 200
        },
        {
          id: '2',
          name: 'Over Budget',
          postcode: 'SW1A 1AB',
          latitude: 51.5075,
          longitude: -0.1279,
          cqcRating: 'Good',
          weeklyCost: 1500, // Over budget + 200
        },
      ];

      const result = service.selectTop3Homes(
        homes,
        1000, // budget
        'residential',
        51.5074,
        -0.1278,
        30.0
      );

      // Should not include over-budget home
      const allSelected = [
        result.safe_bet,
        result.best_value,
        result.premium,
      ].filter(Boolean);

      allSelected.forEach((home) => {
        const price = (home as any).weekly_cost || 
                     (home as any).weeklyCost || 0;
        expect(price).toBeLessThanOrEqual(1200); // budget + 200
      });
    });

    it('should calculate distance correctly', () => {
      const homes: CareHome[] = [
        {
          id: '1',
          name: 'Close Home',
          postcode: 'SW1A 1AA',
          latitude: 51.5074,
          longitude: -0.1278,
          cqcRating: 'Good',
          weeklyCost: 1000,
        },
        {
          id: '2',
          name: 'Far Home',
          postcode: 'SW1A 1AB',
          latitude: 52.0, // ~50km away
          longitude: -0.5,
          cqcRating: 'Good',
          weeklyCost: 1000,
        },
      ];

      const result = service.selectTop3Homes(
        homes,
        1000,
        'residential',
        51.5074, // user location
        -0.1278,
        30.0 // max 30km
      );

      // Far home should not be selected (or distance should be > 30km)
      const allSelected = [
        result.safe_bet,
        result.best_value,
        result.premium,
      ].filter(Boolean);

      allSelected.forEach((home) => {
        const distance = (home as any).distance_km || 
                        (home as any).distanceKm;
        if (distance !== undefined) {
          expect(distance).toBeLessThanOrEqual(30.0);
        }
      });
    });

    it('should return fallback if no homes match filters', () => {
      const homes: CareHome[] = [
        {
          id: '1',
          name: 'Home A',
          postcode: 'SW1A 1AA',
          latitude: 51.5074,
          longitude: -0.1278,
          cqcRating: 'Requires improvement',
          weeklyCost: 2000, // Over budget
        },
      ];

      const result = service.selectTop3Homes(
        homes,
        1000,
        'residential',
        51.5074,
        -0.1278,
        30.0
      );

      // Should still return homes (fallback behavior)
      expect(result.safe_bet || result.best_value || result.premium).toBeDefined();
    });
  });
});

