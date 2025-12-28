/**
 * Data Matcher
 * Base matching algorithm for care homes
 */

import { CareHome } from '@/lib/shared/types/care-home';

export interface MatchingConfig {
  budget?: number;
  careType: string;
  userLat?: number;
  userLon?: number;
  maxDistanceKm?: number;
  priorityOrder?: string[];
  priorityWeights?: number[];
}

export interface ScoredHome {
  home: CareHome;
  score: number;
  categoryScores: {
    [category: string]: number;
  };
  matchReasons: string[];
}

export class DataMatcher {
  /**
   * Universal matching (base algorithm)
   * 
   * @param homes Array of care homes
   * @param config Matching configuration
   * @returns Array of scored homes (sorted by score)
   */
  async matchHomes(
    homes: CareHome[],
    config: MatchingConfig
  ): Promise<ScoredHome[]> {
    const scored: ScoredHome[] = [];

    for (const home of homes) {
      const score = this.calculateScore(home, config);
      scored.push({
        home,
        score: score.total,
        categoryScores: score.categories,
        matchReasons: score.reasons,
      });
    }

    // Sort by score (descending)
    scored.sort((a, b) => b.score - a.score);

    return scored;
  }

  /**
   * Calculate score for a home
   * 
   * @param home Care home
   * @param config Matching configuration
   * @returns Score breakdown
   */
  private calculateScore(
    home: CareHome,
    config: MatchingConfig
  ): {
    total: number;
    categories: { [key: string]: number };
    reasons: string[];
  } {
    const categories: { [key: string]: number } = {};
    const reasons: string[] = [];

    // Base score
    let total = 50;

    // CQC Rating score (0-25 points)
    const cqcScore = this.getCQCScore(home.cqcRating);
    categories.cqc = cqcScore;
    total += cqcScore;
    if (cqcScore > 0) {
      reasons.push(`CQC rating: ${home.cqcRating || 'Unknown'}`);
    }

    // Price fit score (0-20 points)
    if (config.budget && config.budget > 0) {
      const priceScore = this.getPriceScore(home, config.budget, config.careType);
      categories.price = priceScore;
      total += priceScore;
      if (priceScore > 0) {
        reasons.push('Price within budget');
      }
    }

    // Distance score (0-10 points)
    if (home.distanceKm !== undefined && home.distanceKm < 999) {
      const distanceScore = this.getDistanceScore(home.distanceKm);
      categories.distance = distanceScore;
      total += distanceScore;
      if (distanceScore > 0) {
        reasons.push(`Distance: ${home.distanceKm}km`);
      }
    }

    return {
      total,
      categories,
      reasons,
    };
  }

  /**
   * Get CQC rating score
   */
  private getCQCScore(rating?: string): number {
    if (!rating) return 0;

    const ratingLower = rating.toLowerCase();
    if (ratingLower === 'outstanding') return 25;
    if (ratingLower === 'good') return 20;
    if (ratingLower.includes('requires improvement')) return 10;
    if (ratingLower === 'inadequate') return 0;

    return 0;
  }

  /**
   * Get price fit score
   */
  private getPriceScore(
    home: CareHome,
    budget: number,
    careType: string
  ): number {
    // This is a simplified version
    // Full implementation would use extractWeeklyPrice
    const price = home.weeklyPrice || home.weeklyCost || 0;
    if (price <= 0) return 0;

    const diff = Math.abs(price - budget);
    if (diff < 50) return 20;
    if (diff < 100) return 15;
    if (diff < 200) return 10;
    if (diff < 300) return 5;

    return 0;
  }

  /**
   * Get distance score
   */
  private getDistanceScore(distanceKm: number): number {
    if (distanceKm < 5) return 10;
    if (distanceKm < 15) return 5;
    if (distanceKm < 30) return 2;

    return 0;
  }
}



