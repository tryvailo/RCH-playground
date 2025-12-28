/**
 * Safety Calculator
 * Scores safety & quality (0-25 points)
 * Ported from Python services/matching/calculators/safety_calculator.py
 */

import { CategoryCalculator } from '../calculator-base';

export class SafetyCalculator extends CategoryCalculator {
  readonly categoryName = 'safety';
  readonly maxPoints = 25.0;

  async calculate(
    home: any,
    userProfile: any,
    enrichedData: any
  ): Promise<number> {
    let score = 0.0;

    try {
      // 1. CQC overall rating (10 points)
      const cqcScore = this.scoreCQCRating(home, enrichedData);
      score += cqcScore;

      // 2. FSA food safety (5 points)
      const fsaScore = this.scoreFSA(home, enrichedData);
      score += fsaScore;

      // 3. Safeguarding incidents (5 points)
      const safeguardingScore = this.scoreSafeguarding(home, enrichedData);
      score += safeguardingScore;

      // 4. Filing compliance (5 points)
      const complianceScore = this.scoreCompliance(home, enrichedData);
      score += complianceScore;

      // Normalize to 0-1.0
      const normalized = Math.min(score / this.maxPoints, 1.0);
      return normalized;
    } catch (error) {
      console.warn(`Error calculating safety score: ${error}`);
      return 0.0;
    }
  }

  private scoreCQCRating(home: any, enrichedData: any): number {
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

  private scoreFSA(home: any, enrichedData: any): number {
    const fsaData = enrichedData?.fsa || {};
    const fsaRating = fsaData.fsa_rating || home.fsa_rating;

    if (fsaRating == null) return 0.0;

    // FSA rating is typically 0-5
    const rating = this.safeFloat(fsaRating, 0);
    if (rating >= 5) return 5.0;
    if (rating >= 4) return 4.0;
    if (rating >= 3) return 2.0;
    if (rating >= 2) return 1.0;

    return 0.0;
  }

  private scoreSafeguarding(home: any, enrichedData: any): number {
    const incidents = this.safeInt(
      this.extractField(enrichedData, 'cqc', 'safeguarding_incidents'),
      0
    );

    // Fewer incidents = higher score
    if (incidents === 0) return 5.0;
    if (incidents <= 2) return 3.0;
    if (incidents <= 5) return 1.0;

    return 0.0;
  }

  private scoreCompliance(home: any, enrichedData: any): number {
    const isCompliant = this.extractField(
      enrichedData,
      'cqc',
      'filing_compliance'
    );

    if (isCompliant === true) return 5.0;
    if (isCompliant === false) return 0.0;

    // Default: assume compliant if no data
    return 3.0;
  }
}



