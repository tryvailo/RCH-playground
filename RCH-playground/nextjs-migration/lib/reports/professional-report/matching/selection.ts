/**
 * Selection Service
 * Selects top 5 homes with diversity guarantees
 * Ported from Python services/matching/selection_service.py
 */

import { ScoredHome } from '../types';

export interface SelectionResult {
  top_5: Array<{
    home: any;
    score: number;
    category: string;
    categoryScores: any;
  }>;
  category_winners: {
    [category: string]: {
      home_name: string;
      score: number;
      category: string;
    };
  };
  diversity_metrics: {
    unique_providers: number;
    unique_locations: number;
    homes_replaced: number;
  };
}

export class SelectionService {
  /**
   * Select top 5 homes with diversity
   * 
   * @param scoredHomes Array of scored homes
   * @param questionnaire User questionnaire
   * @param enrichedHomesMap Map of home_id -> enriched_data
   * @returns Selection result
   */
  async selectTop5(
    scoredHomes: ScoredHome[],
    questionnaire: any,
    enrichedHomesMap: Record<string, any>
  ): Promise<SelectionResult> {
    if (scoredHomes.length === 0) {
      return {
        top_5: [],
        category_winners: {},
        diversity_metrics: {
          unique_providers: 0,
          unique_locations: 0,
          homes_replaced: 0,
        },
      };
    }

    // 1. Select best overall
    const bestOverall = this.selectBestOverall(scoredHomes);

    // 2. Select category winners
    const categoryWinners = this.selectCategoryWinners(
      scoredHomes,
      questionnaire
    );

    // 3. Build top 5 with diversity
    const top5 = this.buildTop5WithDiversity(
      scoredHomes,
      bestOverall,
      categoryWinners
    );

    // 4. Calculate diversity metrics
    const diversityMetrics = this.calculateDiversityMetrics(top5);

    return {
      top_5: top5,
      category_winners: categoryWinners,
      diversity_metrics: diversityMetrics,
    };
  }

  /**
   * Select best overall home
   */
  private selectBestOverall(scoredHomes: ScoredHome[]): ScoredHome | null {
    return scoredHomes.length > 0 ? scoredHomes[0] : null;
  }

  /**
   * Select category winners
   */
  private selectCategoryWinners(
    scoredHomes: ScoredHome[],
    questionnaire: any
  ): Record<string, any> {
    const winners: Record<string, any> = {};

    // Best medical & safety
    const medicalSafety = scoredHomes
      .map((h) => ({
        scoredHome: h,
        score: h.categoryScores.medical + h.categoryScores.safety,
      }))
      .sort((a, b) => b.score - a.score)[0];

    if (medicalSafety) {
      winners['best_medical_safety'] = {
        home_name: (medicalSafety.scoredHome.home as any)?.name || '',
        score: medicalSafety.score,
        category: 'medical_safety',
      };
    }

    // Best value (financial)
    const bestValue = scoredHomes
      .map((h) => ({
        scoredHome: h,
        score: h.categoryScores.financial,
      }))
      .sort((a, b) => b.score - a.score)[0];

    if (bestValue) {
      winners['best_value'] = {
        home_name: (bestValue.scoredHome.home as any)?.name || '',
        score: bestValue.score,
        category: 'financial',
      };
    }

    return winners;
  }

  /**
   * Build top 5 with diversity
   */
  private buildTop5WithDiversity(
    scoredHomes: ScoredHome[],
    bestOverall: ScoredHome | null,
    categoryWinners: Record<string, any>
  ): Array<{
    home: any;
    score: number;
    category: string;
    categoryScores: any;
  }> {
    const top5: Array<{
      home: any;
      score: number;
      category: string;
      categoryScores: any;
    }> = [];
    const usedHomeIds = new Set<string>();
    const usedProviders = new Set<string>();

    // Add best overall
    if (bestOverall) {
      const homeId = this.getHomeId(bestOverall.home);
      const provider = this.getProvider(bestOverall.home);

      top5.push({
        home: bestOverall.home,
        score: bestOverall.score,
        category: 'best_overall',
        categoryScores: bestOverall.categoryScores,
      });

      usedHomeIds.add(homeId);
      if (provider) usedProviders.add(provider);
    }

    // Add remaining homes ensuring diversity
    for (const scored of scoredHomes) {
      if (top5.length >= 5) break;

      const homeId = this.getHomeId(scored.home);
      const provider = this.getProvider(scored.home);

      // Skip if already used
      if (usedHomeIds.has(homeId)) continue;

      // Prefer different providers
      if (usedProviders.has(provider) && top5.length >= 2) {
        continue; // Skip if we already have homes from this provider
      }

      top5.push({
        home: scored.home,
        score: scored.score,
        category: this.determineCategory(scored, categoryWinners),
        categoryScores: scored.categoryScores,
      });

      usedHomeIds.add(homeId);
      if (provider) usedProviders.add(provider);
    }

    return top5;
  }

  /**
   * Calculate diversity metrics
   */
  private calculateDiversityMetrics(
    top5: Array<{ home: any }>
  ): {
    unique_providers: number;
    unique_locations: number;
    homes_replaced: number;
  } {
    const providers = new Set<string>();
    const locations = new Set<string>();

    for (const item of top5) {
      const provider = this.getProvider(item.home);
      const location = this.getLocation(item.home);

      if (provider) providers.add(provider);
      if (location) locations.add(location);
    }

    return {
      unique_providers: providers.size,
      unique_locations: locations.size,
      homes_replaced: 0, // TODO: Track replacements
    };
  }

  /**
   * Get home ID
   */
  private getHomeId(home: any): string {
    return (
      home.cqc_location_id ||
      home.id ||
      home.name ||
      String(Math.random())
    );
  }

  /**
   * Get provider name
   */
  private getProvider(home: any): string {
    return (
      home.provider_name ||
      home.provider ||
      (home as any).organisation_name ||
      ''
    );
  }

  /**
   * Get location
   */
  private getLocation(home: any): string {
    return home.city || home.local_authority || home.location || '';
  }

  /**
   * Determine category for home
   */
  private determineCategory(
    scored: ScoredHome,
    categoryWinners: Record<string, any>
  ): string {
    // Check if this home is a category winner
    const homeName = scored.home.name || '';
    for (const [category, winner] of Object.entries(categoryWinners)) {
      if (winner.home_name === homeName) {
        return category;
      }
    }

    return 'best_overall';
  }
}

