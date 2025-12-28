/**
 * Staff Calculator
 * Scores staff quality (0-18 points)
 * Ported from Python services/matching/calculators/staff_calculator.py
 */

import { CategoryCalculator } from '../calculator-base';

export class StaffCalculator extends CategoryCalculator {
  readonly categoryName = 'staff';
  readonly maxPoints = 18.0;

  async calculate(
    home: any,
    userProfile: any,
    enrichedData: any
  ): Promise<number> {
    let score = 0.0;

    try {
      // 1. Employee satisfaction (8 points)
      const satisfactionScore = this.scoreSatisfaction(home, enrichedData);
      score += satisfactionScore;

      // 2. Staff retention (6 points)
      const retentionScore = this.scoreRetention(home, enrichedData);
      score += retentionScore;

      // 3. Qualifications (4 points)
      const qualificationsScore = this.scoreQualifications(home, enrichedData);
      score += qualificationsScore;

      // Normalize to 0-1.0
      const normalized = Math.min(score / this.maxPoints, 1.0);
      return normalized;
    } catch (error) {
      console.warn(`Error calculating staff score: ${error}`);
      return 0.0;
    }
  }

  private scoreSatisfaction(home: any, enrichedData: any): number {
    const staff = enrichedData?.staff || {};
    const glassdoorRating = this.safeFloat(
      staff.employee_satisfaction?.glassdoor_rating,
      0
    );

    if (glassdoorRating >= 4.0) return 8.0;
    if (glassdoorRating >= 3.5) return 6.0;
    if (glassdoorRating >= 3.0) return 4.0;
    if (glassdoorRating >= 2.5) return 2.0;

    return 0.0;
  }

  private scoreRetention(home: any, enrichedData: any): number {
    const staff = enrichedData?.staff || {};
    const turnoverRate = this.safeFloat(
      staff.staff_retention?.turnover_rate,
      100
    );

    // Lower turnover = higher score
    if (turnoverRate < 10) return 6.0;
    if (turnoverRate < 20) return 4.0;
    if (turnoverRate < 30) return 2.0;

    return 0.0;
  }

  private scoreQualifications(home: any, enrichedData: any): number {
    const staff = enrichedData?.staff || {};
    const rnCount = this.safeInt(staff.qualifications?.rn_count, 0);
    const certifiedPercentage = this.safeFloat(
      staff.qualifications?.certified_staff_percentage,
      0
    );

    let score = 0.0;

    // RN count
    if (rnCount >= 3) score += 2.0;
    else if (rnCount >= 1) score += 1.0;

    // Certified staff percentage
    if (certifiedPercentage >= 80) score += 2.0;
    else if (certifiedPercentage >= 60) score += 1.0;

    return Math.min(score, 4.0);
  }
}



