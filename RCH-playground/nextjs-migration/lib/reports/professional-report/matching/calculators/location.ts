/**
 * Location Calculator
 * Scores location & access (0-15 points)
 * Ported from Python services/matching/calculators/location_calculator.py
 */

import { CategoryCalculator } from '../calculator-base';

export class LocationCalculator extends CategoryCalculator {
  readonly categoryName = 'location';
  readonly maxPoints = 15.0;

  async calculate(
    home: any,
    userProfile: any,
    enrichedData: any
  ): Promise<number> {
    let score = 0.0;

    try {
      const locationBudget = userProfile?.section_2_location_budget || {};
      const maxDistancePref = locationBudget.q6_max_distance || '';

      // 1. Distance scoring (10 points)
      const distanceScore = this.scoreDistance(home, maxDistancePref);
      score += distanceScore;

      // 2. Accessibility features (3 points)
      const accessibilityScore = this.scoreAccessibility(home, enrichedData);
      score += accessibilityScore;

      // 3. Transport access (2 points)
      const transportScore = this.scoreTransport(home, enrichedData);
      score += transportScore;

      // Normalize to 0-1.0
      const normalized = Math.min(score / this.maxPoints, 1.0);
      return normalized;
    } catch (error) {
      console.warn(`Error calculating location score: ${error}`);
      return 0.0;
    }
  }

  private scoreDistance(home: any, maxDistancePref: string): number {
    const distance = this.safeFloat(home.distance_km, 999);

    if (maxDistancePref === 'within_5km') {
      if (distance <= 5) return 10.0;
      if (distance <= 15) return 5.0;
      return 0.0;
    }

    if (maxDistancePref === 'within_15km') {
      if (distance <= 15) return 10.0;
      if (distance <= 30) return 5.0;
      return 0.0;
    }

    if (maxDistancePref === 'within_30km') {
      if (distance <= 30) return 10.0;
      if (distance <= 50) return 5.0;
      return 0.0;
    }

    // distance_not_important or default
    if (distance < 5) return 10.0;
    if (distance < 15) return 7.0;
    if (distance < 30) return 5.0;
    if (distance < 50) return 2.0;

    return 0.0;
  }

  private scoreAccessibility(home: any, enrichedData: any): number {
    let score = 0.0;

    const accessibility = this.extractField(
      enrichedData,
      'location',
      'accessibility_features'
    );
    const features = this.safeList(accessibility);

    if (features.length >= 3) {
      score += 3.0;
    } else if (features.length >= 1) {
      score += 1.5;
    }

    return Math.min(score, 3.0);
  }

  private scoreTransport(home: any, enrichedData: any): number {
    let score = 0.0;

    const transport = this.extractField(
      enrichedData,
      'location',
      'transport_access'
    );

    if (transport) {
      const hasPublicTransport = this.checkContains(transport, 'public');
      const hasParking = this.checkContains(transport, 'parking');

      if (hasPublicTransport) score += 1.0;
      if (hasParking) score += 1.0;
    }

    return Math.min(score, 2.0);
  }
}



