/**
 * Social Calculator
 * Scores social & community (0-12 points)
 * Ported from Python services/matching/calculators/social_calculator.py
 */

import { CategoryCalculator } from '../calculator-base';

export class SocialCalculator extends CategoryCalculator {
  readonly categoryName = 'social';
  readonly maxPoints = 12.0;

  async calculate(
    home: any,
    userProfile: any,
    enrichedData: any
  ): Promise<number> {
    let score = 0.0;

    try {
      // 1. Social activities (6 points)
      const activitiesScore = this.scoreActivities(home, enrichedData);
      score += activitiesScore;

      // 2. Community integration (4 points)
      const communityScore = this.scoreCommunity(home, enrichedData);
      score += communityScore;

      // 3. Visitor support (2 points)
      const visitorScore = this.scoreVisitorSupport(home, enrichedData);
      score += visitorScore;

      // Normalize to 0-1.0
      const normalized = Math.min(score / this.maxPoints, 1.0);
      return normalized;
    } catch (error) {
      console.warn(`Error calculating social score: ${error}`);
      return 0.0;
    }
  }

  private scoreActivities(home: any, enrichedData: any): number {
    const activities = this.extractField(
      enrichedData,
      'social',
      'activities'
    );
    const activitiesList = this.safeList(activities);

    if (activitiesList.length >= 10) return 6.0;
    if (activitiesList.length >= 5) return 4.0;
    if (activitiesList.length >= 3) return 2.0;
    if (activitiesList.length >= 1) return 1.0;

    return 0.0;
  }

  private scoreCommunity(home: any, enrichedData: any): number {
    const community = this.extractField(
      enrichedData,
      'social',
      'community_integration'
    );

    if (community) {
      const hasOutings = this.checkContains(community, 'outings');
      const hasEvents = this.checkContains(community, 'events');

      let score = 0.0;
      if (hasOutings) score += 2.0;
      if (hasEvents) score += 2.0;

      return Math.min(score, 4.0);
    }

    return 0.0;
  }

  private scoreVisitorSupport(home: any, enrichedData: any): number {
    const visitorSupport = this.extractField(
      enrichedData,
      'social',
      'visitor_support'
    );

    if (visitorSupport) {
      const hasVisitorRooms = this.checkContains(visitorSupport, 'rooms');
      const hasFlexibleHours = this.checkContains(visitorSupport, 'flexible');

      let score = 0.0;
      if (hasVisitorRooms) score += 1.0;
      if (hasFlexibleHours) score += 1.0;

      return Math.min(score, 2.0);
    }

    return 0.0;
  }
}



