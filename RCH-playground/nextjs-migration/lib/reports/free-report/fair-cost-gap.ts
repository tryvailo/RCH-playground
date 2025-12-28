/**
 * Fair Cost Gap Service
 * Calculates the gap between market price and MSIF fair cost
 * Ported from Python services/fair_cost_gap_service.py
 */

import { FairCostGap } from './types';

export class FairCostGapService {
  /**
   * Calculate Fair Cost Gap
   * 
   * @param marketPrice Average care home price in the area (£/week)
   * @param msifLowerBound MSIF fair cost lower bound (£/week)
   * @param careType Type of care (residential, nursing, etc.)
   * @returns Fair cost gap calculations
   */
  calculateGap(
    marketPrice: number,
    msifLowerBound: number,
    careType: string = 'residential'
  ): FairCostGap {
    // Calculate gaps
    const weeklyGap = marketPrice - msifLowerBound;
    const annualGap = weeklyGap * 52;
    const fiveYearGap = annualGap * 5;

    // Calculate percentage
    const gapPercent =
      msifLowerBound > 0 ? (weeklyGap / msifLowerBound) * 100 : 0;

    // Generate explanation
    const explanation = `Market price of £${marketPrice.toLocaleString('en-GB', {
      maximumFractionDigits: 0,
    })}/week exceeds MSIF fair cost of £${msifLowerBound.toLocaleString('en-GB', {
      maximumFractionDigits: 0,
    })}/week by ${gapPercent.toFixed(1)}%`;

    // Generate text summary
    let gapText: string;
    if (weeklyGap > 0) {
      gapText = `Переплата £${annualGap.toLocaleString('en-GB', {
        maximumFractionDigits: 0,
      })} в год = £${fiveYearGap.toLocaleString('en-GB', {
        maximumFractionDigits: 0,
      })} за 5 лет`;
    } else {
      gapText = `Экономия £${Math.abs(annualGap).toLocaleString('en-GB', {
        maximumFractionDigits: 0,
      })} в год = £${Math.abs(fiveYearGap).toLocaleString('en-GB', {
        maximumFractionDigits: 0,
      })} за 5 лет`;
    }

    return {
      gap_week: Math.round(weeklyGap * 100) / 100,
      gap_year: Math.round(annualGap * 100) / 100,
      gap_5year: Math.round(fiveYearGap * 100) / 100,
      gap_percent: Math.round(gapPercent * 10) / 10,
      market_price: Math.round(marketPrice * 100) / 100,
      msif_lower_bound: Math.round(msifLowerBound * 100) / 100,
      explanation,
      gap_text: gapText,
      recommendations: this.getRecommendations(weeklyGap),
    };
  }

  /**
   * Get recommendations based on gap size
   * 
   * @param weeklyGap Weekly gap amount
   * @returns Array of recommendations
   */
  private getRecommendations(weeklyGap: number): string[] {
    const recommendations: string[] = [];

    if (weeklyGap > 500) {
      recommendations.push('Use MSIF data to negotiate lower fees');
      recommendations.push('Consider homes in adjacent local authorities');
    }

    if (weeklyGap > 200) {
      recommendations.push('Request detailed cost breakdown');
      recommendations.push('Explore long-term commitment discounts');
    }

    if (weeklyGap > 0) {
      recommendations.push('Compare prices across multiple homes');
    } else {
      recommendations.push('This is an excellent market price');
    }

    return recommendations;
  }
}

// Singleton instance
let gapServiceInstance: FairCostGapService | null = null;

export function getFairCostGapService(): FairCostGapService {
  if (!gapServiceInstance) {
    gapServiceInstance = new FairCostGapService();
  }
  return gapServiceInstance;
}



