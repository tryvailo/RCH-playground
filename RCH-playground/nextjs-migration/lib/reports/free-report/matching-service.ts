/**
 * Free Report Matching Service
 * Selects top 3 strategic care homes (Safe Bet, Best Value, Premium)
 * Ported from Python services/free_report_matching_service.py
 */

import { CareHome } from '@/lib/shared/types/care-home';
import { extractWeeklyPrice } from '@/lib/data-engine/utils/price-extractor';
import { calculateDistanceKm, validateCoordinates } from '@/lib/data-engine/utils/geo';
import { MatchedHomes } from './types';

export class FreeReportMatchingService {
  /**
   * Select 3 homes with different strategies:
   * - Safe Bet: Best balance of quality, price, location
   * - Best Value: Best price/quality ratio
   * - Premium: Highest quality available
   */
  selectTop3Homes(
    homes: CareHome[],
    budget: number,
    careType: string,
    userLat?: number,
    userLon?: number,
    maxDistanceKm: number = 30.0
  ): MatchedHomes {
    // Filter homes first
    let filteredHomes = this.filterByQuality(homes);
    filteredHomes = this.filterByPrice(filteredHomes, budget, careType);
    filteredHomes = this.filterByLocation(
      filteredHomes,
      userLat,
      userLon,
      maxDistanceKm
    );

    if (filteredHomes.length === 0) {
      // Fallback: return first 3 homes from input
      return {
        safe_bet: homes[0] || null,
        best_value: homes[1] || null,
        premium: homes[2] || null,
      };
    }

    // Score all homes
    const scoredHomes = this.scoreHomes(filteredHomes, budget, careType);

    // Find Safe Bet
    const safeBet = this.findSafeBet(scoredHomes, budget, careType);

    // Find Best Value (excluding Safe Bet)
    const remainingHomes = scoredHomes.filter(
      (h) => !safeBet || h.home.name !== safeBet.name
    );
    const bestValue = this.findBestValue(remainingHomes, budget, careType);

    // Find Premium (excluding Safe Bet and Best Value)
    const finalRemaining = remainingHomes.filter(
      (h) => !bestValue || h.home.name !== bestValue.name
    );
    const premium = this.findPremium(finalRemaining, budget, careType);

    return {
      safe_bet: safeBet,
      best_value: bestValue,
      premium: premium,
    };
  }

  /**
   * Filter homes with Good or Outstanding CQC rating
   */
  private filterByQuality(homes: CareHome[]): CareHome[] {
    return homes.filter((h) => {
      const rating = this.getCQCRating(h);
      const ratingLower = rating.toLowerCase();
      return (
        ratingLower === 'good' || ratingLower === 'outstanding'
      );
    });
  }

  /**
   * Filter homes within budget + £200
   */
  private filterByPrice(
    homes: CareHome[],
    budget: number,
    careType: string
  ): CareHome[] {
    if (budget <= 0) {
      return homes;
    }

    return homes.filter(
      (h) => extractWeeklyPrice(h, careType as any) <= budget + 200
    );
  }

  /**
   * Filter homes within max distance
   */
  private filterByLocation(
    homes: CareHome[],
    userLat?: number,
    userLon?: number,
    maxKm: number = 30.0
  ): CareHome[] {
    if (!userLat || !userLon) {
      return homes;
    }

    const filtered: CareHome[] = [];

    for (const home of homes) {
      const homeLat = home.latitude;
      const homeLon = home.longitude;

      if (homeLat && homeLon) {
        try {
          if (
            validateCoordinates(userLat, userLon) &&
            validateCoordinates(homeLat, homeLon)
          ) {
            const distance = calculateDistanceKm(
              userLat,
              userLon,
              homeLat,
              homeLon
            );
            if (distance <= maxKm) {
              filtered.push({ ...home, distance_km: distance, distanceKm: distance });
            }
          }
        } catch {
          // Skip invalid coordinates
        }
      }
    }

    return filtered.length > 0 ? filtered : homes;
  }

  /**
   * Score all homes for ranking
   */
  private scoreHomes(
    homes: CareHome[],
    budget: number,
    careType: string
  ): Array<{ home: CareHome; score: number }> {
    const scored: Array<{ home: CareHome; score: number }> = [];

    for (const home of homes) {
      const price = extractWeeklyPrice(home, careType as any);
      if (price <= 0) {
        continue; // Skip homes without valid price
      }

      const score = this.calculateHomeScore(home, budget, careType, price);
      scored.push({ home, score });
    }

    // Sort by score (descending)
    scored.sort((a, b) => b.score - a.score);

    return scored;
  }

  /**
   * Calculate scoring for a home
   */
  private calculateHomeScore(
    home: CareHome,
    budget: number,
    careType: string,
    price: number
  ): number {
    let score = 50.0; // Base score

    // Quality (25 points)
    const cqcRating = this.getCQCRating(home);
    const ratingLower = cqcRating.toLowerCase();
    if (ratingLower === 'outstanding') {
      score += 25;
    } else if (ratingLower === 'good') {
      score += 20;
    }

    // Price fit (20 points)
    if (budget > 0) {
      const priceDiff = Math.abs(price - budget);
      if (priceDiff < 50) {
        score += 20;
      } else if (priceDiff < 100) {
        score += 15;
      } else if (priceDiff < 200) {
        score += 10;
      }
    }

    // Distance (10 points)
    const distance = home.distanceKm ?? 999;
    if (typeof distance === 'number') {
      if (distance < 5) {
        score += 10;
      } else if (distance < 15) {
        score += 5;
      }
    }

    return score;
  }

  /**
   * Find best balance of quality, price, location
   */
  private findSafeBet(
    scoredHomes: Array<{ home: CareHome; score: number }>,
    budget: number,
    careType: string
  ): CareHome | null {
    let best: CareHome | null = null;
    let bestScore = -1;

    for (const scored of scoredHomes) {
      const home = scored.home;
      const price = extractWeeklyPrice(home, careType as any);
      const cqc = this.getCQCRatingScore(this.getCQCRating(home));

      // Must have good quality
      if (cqc < 3) {
        continue;
      }

      // Calculate balance score
      let balance = cqc * 10;
      if (budget > 0) {
        const priceDiff = Math.abs(price - budget);
        if (priceDiff < 50) {
          balance += 5;
        } else if (priceDiff < 100) {
          balance += 3;
        }
      }

      const distance = home.distanceKm ?? 999;
      if (typeof distance === 'number' && distance < 15) {
        balance += 2;
      }

      if (balance > bestScore) {
        bestScore = balance;
        best = home;
      }
    }

    return best;
  }

  /**
   * Find best price/quality ratio
   */
  private findBestValue(
    scoredHomes: Array<{ home: CareHome; score: number }>,
    budget: number,
    careType: string
  ): CareHome | null {
    let best: CareHome | null = null;
    let bestScore = -1;

    for (const scored of scoredHomes) {
      const home = scored.home;
      const price = extractWeeklyPrice(home, careType as any);
      const cqc = this.getCQCRatingScore(this.getCQCRating(home));

      // Must have at least requires improvement
      if (cqc < 2) {
        continue;
      }

      // Value score: quality/price ratio
      if (price > 0) {
        const valueScore = cqc / (price / 100);
        if (valueScore > bestScore) {
          bestScore = valueScore;
          best = home;
        }
      }
    }

    return best;
  }

  /**
   * Find highest quality home
   */
  private findPremium(
    scoredHomes: Array<{ home: CareHome; score: number }>,
    budget: number,
    careType: string
  ): CareHome | null {
    let best: CareHome | null = null;
    let bestCqc = -1;

    for (const scored of scoredHomes) {
      const home = scored.home;
      const cqc = this.getCQCRatingScore(this.getCQCRating(home));

      if (cqc > bestCqc) {
        bestCqc = cqc;
        best = home;
      }
    }

    return best;
  }

  /**
   * Extract CQC rating from home data
   */
  private getCQCRating(home: CareHome): string {
    return (
      (home as any).cqc_rating_overall ||
      (home as any).overall_cqc_rating ||
      home.cqcRating ||
      (home as any).rating ||
      'Unknown'
    );
  }

  /**
   * Convert CQC rating to numeric score
   */
  private getCQCRatingScore(ratingStr: string): number {
    if (!ratingStr || typeof ratingStr !== 'string') {
      return 0;
    }

    const ratingLower = ratingStr.toLowerCase();
    if (ratingLower.includes('outstanding')) {
      return 4;
    } else if (ratingLower.includes('good')) {
      return 3;
    } else if (ratingLower.includes('requires improvement')) {
      return 2;
    } else if (ratingLower === 'inadequate') {
      return 1;
    }

    return 0;
  }
}

// Singleton instance
let matchingServiceInstance: FreeReportMatchingService | null = null;

export function getFreeReportMatchingService(): FreeReportMatchingService {
  if (!matchingServiceInstance) {
    matchingServiceInstance = new FreeReportMatchingService();
  }
  return matchingServiceInstance;
}

