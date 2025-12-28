/**
 * Services Calculator
 * Scores services & amenities (0-10 points)
 * Ported from Python services/matching/calculators/services_calculator.py
 */

import { CategoryCalculator } from '../calculator-base';

export class ServicesCalculator extends CategoryCalculator {
  readonly categoryName = 'services';
  readonly maxPoints = 10.0;

  async calculate(
    home: any,
    userProfile: any,
    enrichedData: any
  ): Promise<number> {
    let score = 0.0;

    try {
      // 1. Amenities (5 points)
      const amenitiesScore = this.scoreAmenities(home, enrichedData);
      score += amenitiesScore;

      // 2. Specialized services (3 points)
      const servicesScore = this.scoreSpecializedServices(home, enrichedData);
      score += servicesScore;

      // 3. Additional services (2 points)
      const additionalScore = this.scoreAdditionalServices(home, enrichedData);
      score += additionalScore;

      // Normalize to 0-1.0
      const normalized = Math.min(score / this.maxPoints, 1.0);
      return normalized;
    } catch (error) {
      console.warn(`Error calculating services score: ${error}`);
      return 0.0;
    }
  }

  private scoreAmenities(home: any, enrichedData: any): number {
    const amenities = this.extractField(
      enrichedData,
      'services',
      'amenities'
    );
    const amenitiesList = this.safeList(amenities);

    if (amenitiesList.length >= 8) return 5.0;
    if (amenitiesList.length >= 5) return 3.0;
    if (amenitiesList.length >= 3) return 2.0;
    if (amenitiesList.length >= 1) return 1.0;

    return 0.0;
  }

  private scoreSpecializedServices(home: any, enrichedData: any): number {
    const services = this.extractField(
      enrichedData,
      'services',
      'specialized_services'
    );
    const servicesList = this.safeList(services);

    if (servicesList.length >= 3) return 3.0;
    if (servicesList.length >= 2) return 2.0;
    if (servicesList.length >= 1) return 1.0;

    return 0.0;
  }

  private scoreAdditionalServices(home: any, enrichedData: any): number {
    const additional = this.extractField(
      enrichedData,
      'services',
      'additional_services'
    );
    const additionalList = this.safeList(additional);

    if (additionalList.length >= 2) return 2.0;
    if (additionalList.length >= 1) return 1.0;

    return 0.0;
  }
}



