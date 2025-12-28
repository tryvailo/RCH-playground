/**
 * CQC Calculator
 * Scores CQC quality (0-16 points)
 * Ported from Python services/matching/calculators/cqc_calculator.py
 */

import { CategoryCalculator } from '../calculator-base';

export class CQCCalculator extends CategoryCalculator {
  readonly categoryName = 'cqc';
  readonly maxPoints = 16.0;

  async calculate(
    home: any,
    userProfile: any,
    enrichedData: any
  ): Promise<number> {
    let score = 0.0;

    try {
      // 1. Overall CQC rating (10 points)
      const overallScore = this.scoreOverallRating(home, enrichedData);
      score += overallScore;

      // 2. Domain ratings (6 points)
      const domainScore = this.scoreDomainRatings(home, enrichedData);
      score += domainScore;

      // Normalize to 0-1.0
      const normalized = Math.min(score / this.maxPoints, 1.0);
      return normalized;
    } catch (error) {
      console.warn(`Error calculating CQC score: ${error}`);
      return 0.0;
    }
  }

  private scoreOverallRating(home: any, enrichedData: any): number {
    const rating =
      home.cqc_rating_overall ||
      home.rating ||
      home.overall_cqc_rating ||
      this.extractField(enrichedData, 'cqc', 'overall_rating');

    const ratingScore = this.scoreRating(rating);

    // Map to 0-10 points
    if (ratingScore === 4) return 10.0; // Outstanding
    if (ratingScore === 3) return 7.0; // Good
    if (ratingScore === 2) return 4.0; // Requires improvement
    if (ratingScore === 1) return 1.0; // Inadequate

    return 0.0;
  }

  private scoreDomainRatings(home: any, enrichedData: any): number {
    const cqcData = enrichedData?.cqc || {};
    const domains = ['effective', 'caring', 'responsive', 'well_led'];
    let score = 0.0;

    for (const domain of domains) {
      const domainRating = this.extractField(cqcData, 'domain_ratings', domain);
      const ratingScore = this.scoreRating(domainRating);

      if (ratingScore === 4) score += 1.5; // Outstanding
      else if (ratingScore === 3) score += 1.0; // Good
      else if (ratingScore === 2) score += 0.5; // Requires improvement
    }

    return Math.min(score, 6.0);
  }
}



