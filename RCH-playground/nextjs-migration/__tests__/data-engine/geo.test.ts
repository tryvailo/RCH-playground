/**
 * Geographic Utilities Tests
 * Compare with Python implementation
 */

import {
  calculateDistanceKm,
  validateCoordinates,
} from '@/lib/data-engine/utils/geo';

describe('Geographic Utilities', () => {
  describe('calculateDistanceKm', () => {
    it('should calculate distance between London coordinates', () => {
      // London to nearby point (~1km)
      const distance = calculateDistanceKm(
        51.5074, // London lat
        -0.1278, // London lon
        51.5155, // Nearby lat
        -0.0922 // Nearby lon
      );

      expect(distance).toBeGreaterThan(0);
      expect(distance).toBeLessThan(10); // Should be less than 10km
    });

    it('should calculate distance correctly for known coordinates', () => {
      // Distance between two close points
      const distance = calculateDistanceKm(
        51.5074,
        -0.1278,
        51.5075,
        -0.1279
      );

      expect(distance).toBeGreaterThan(0);
      expect(distance).toBeLessThan(1); // Should be very close
    });

    it('should throw error for invalid coordinates', () => {
      expect(() => {
        calculateDistanceKm(91, 0, 51.5074, -0.1278); // Invalid lat
      }).toThrow();

      expect(() => {
        calculateDistanceKm(51.5074, -181, 51.5074, -0.1278); // Invalid lon
      }).toThrow();
    });
  });

  describe('validateCoordinates', () => {
    it('should validate correct coordinates', () => {
      expect(validateCoordinates(51.5074, -0.1278)).toBe(true);
      expect(validateCoordinates(0, 0)).toBe(true);
      expect(validateCoordinates(-90, -180)).toBe(true);
      expect(validateCoordinates(90, 180)).toBe(true);
    });

    it('should reject invalid coordinates', () => {
      expect(validateCoordinates(91, 0)).toBe(false); // Lat too high
      expect(validateCoordinates(-91, 0)).toBe(false); // Lat too low
      expect(validateCoordinates(0, 181)).toBe(false); // Lon too high
      expect(validateCoordinates(0, -181)).toBe(false); // Lon too low
    });

    it('should handle null/undefined', () => {
      expect(validateCoordinates(null, null)).toBe(false);
      expect(validateCoordinates(undefined, undefined)).toBe(false);
      expect(validateCoordinates(51.5074, null)).toBe(false);
      expect(validateCoordinates(null, -0.1278)).toBe(false);
    });
  });
});



