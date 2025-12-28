/**
 * Financial Calculator
 * Scores financial stability & price match (0-20 points)
 * Ported from Python services/matching/calculators/financial_calculator.py
 */

import { CategoryCalculator } from '../calculator-base';
import { extractWeeklyPrice } from '@/lib/data-engine/utils/price-extractor';

export class FinancialCalculator extends CategoryCalculator {
  readonly categoryName = 'financial';
  readonly maxPoints = 20.0;

  async calculate(
    home: any,
    userProfile: any,
    enrichedData: any
  ): Promise<number> {
    let score = 0.0;

    try {
      const locationBudget = userProfile?.section_2_location_budget || {};
      const budgetRange = locationBudget.q7_budget_range || '';
      const budget = this.extractBudget(budgetRange);

      // 1. Price vs budget match (10 points)
      const priceScore = this.scorePriceMatch(home, budget);
      score += priceScore;

      // 2. Financial stability (7 points)
      const stabilityScore = this.scoreFinancialStability(home, enrichedData);
      score += stabilityScore;

      // 3. Quality-to-price ratio (3 points)
      const valueScore = this.scoreValue(home, enrichedData);
      score += valueScore;

      // Normalize to 0-1.0
      const normalized = Math.min(score / this.maxPoints, 1.0);
      return normalized;
    } catch (error) {
      console.warn(`Error calculating financial score: ${error}`);
      return 0.0;
    }
  }

  private extractBudget(budgetRange: string): number {
    // Extract budget from range string like "£1000-£1500"
    const match = budgetRange.match(/£?(\d+)/);
    if (match) {
      return parseFloat(match[1]);
    }
    return 0;
  }

  private scorePriceMatch(home: any, budget: number): number {
    if (budget <= 0) return 5.0; // Default score if no budget

    const price = extractWeeklyPrice(home, 'residential');
    if (price <= 0) return 0.0;

    const diff = Math.abs(price - budget);
    const percentDiff = (diff / budget) * 100;

    if (percentDiff < 5) return 10.0; // Within 5%
    if (percentDiff < 10) return 8.0; // Within 10%
    if (percentDiff < 20) return 5.0; // Within 20%
    if (percentDiff < 30) return 2.0; // Within 30%

    return 0.0;
  }

  private scoreFinancialStability(home: any, enrichedData: any): number {
    const financial = enrichedData?.financial || {};
    const altmanZ = this.safeFloat(financial.altman_z_score, 0);
    const bankruptcyRisk = this.safeFloat(financial.bankruptcy_risk, 0);

    let score = 0.0;

    // Altman Z-score (higher is better, >2.99 is safe)
    if (altmanZ > 2.99) {
      score += 5.0;
    } else if (altmanZ > 1.8) {
      score += 3.0;
    } else if (altmanZ > 0) {
      score += 1.0;
    }

    // Bankruptcy risk (lower is better)
    if (bankruptcyRisk < 0.1) {
      score += 2.0;
    } else if (bankruptcyRisk < 0.3) {
      score += 1.0;
    }

    return Math.min(score, 7.0);
  }

  private scoreValue(home: any, enrichedData: any): number {
    const price = extractWeeklyPrice(home, 'residential');
    if (price <= 0) return 0.0;

    // Get quality score (CQC rating)
    const rating =
      home.cqc_rating_overall ||
      home.rating ||
      this.extractField(enrichedData, 'cqc', 'overall_rating');
    const qualityScore = this.scoreRating(rating);

    // Value = quality / price ratio
    const valueRatio = qualityScore / (price / 100);

    if (valueRatio > 0.04) return 3.0;
    if (valueRatio > 0.03) return 2.0;
    if (valueRatio > 0.02) return 1.0;

    return 0.0;
  }
}



