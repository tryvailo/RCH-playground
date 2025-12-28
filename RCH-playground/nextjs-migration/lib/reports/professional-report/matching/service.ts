/**
 * Professional Matching Service
 * 156-point matching algorithm using 8 category calculators
 * Ported from Python services/professional_matching_service.py
 */

import {
  MedicalCalculator,
  SafetyCalculator,
  LocationCalculator,
  FinancialCalculator,
  StaffCalculator,
  CQCCalculator,
  SocialCalculator,
  ServicesCalculator,
  CALCULATORS,
} from './calculators';
import { CategoryScores, ScoredHome } from '../types';

export interface ScoringWeights {
  medical: number;
  safety: number;
  location: number;
  financial: number;
  staff: number;
  cqc: number;
  social: number;
  services: number;
}

export class ProfessionalMatchingService {
  private calculators = {
    medical: new MedicalCalculator(),
    safety: new SafetyCalculator(),
    location: new LocationCalculator(),
    financial: new FinancialCalculator(),
    staff: new StaffCalculator(),
    cqc: new CQCCalculator(),
    social: new SocialCalculator(),
    services: new ServicesCalculator(),
  };

  /**
   * Calculate dynamic weights based on questionnaire
   */
  calculateDynamicWeights(questionnaire: any): ScoringWeights {
    // Default weights (156-point system)
    const defaultWeights: ScoringWeights = {
      medical: 30,
      safety: 25,
      location: 15,
      financial: 20,
      staff: 18,
      cqc: 16,
      social: 12,
      services: 10,
    };

    // TODO: Implement dynamic weight calculation based on user priorities
    // For now, return default weights
    return defaultWeights;
  }

  /**
   * Match homes using 156-point algorithm
   * 
   * @param enrichedHomes Array of enriched care homes
   * @param questionnaire User questionnaire
   * @returns Array of scored homes
   */
  async matchHomes(
    enrichedHomes: any[],
    questionnaire: any
  ): Promise<ScoredHome[]> {
    const weights = this.calculateDynamicWeights(questionnaire);
    const scored: ScoredHome[] = [];

    for (const enriched of enrichedHomes) {
      const home = enriched.home || enriched;
      const enrichments = enriched.enrichments || {};

      // Calculate scores for each category
      const categoryScores: CategoryScores = {
        medical: 0,
        safety: 0,
        location: 0,
        financial: 0,
        staff: 0,
        cqc: 0,
        social: 0,
        services: 0,
      };

      // Calculate each category score (0-1.0 normalized)
      categoryScores.medical = await this.calculators.medical.calculate(
        home,
        questionnaire,
        enrichments
      );
      categoryScores.safety = await this.calculators.safety.calculate(
        home,
        questionnaire,
        enrichments
      );
      categoryScores.location = await this.calculators.location.calculate(
        home,
        questionnaire,
        enrichments
      );
      categoryScores.financial = await this.calculators.financial.calculate(
        home,
        questionnaire,
        enrichments
      );
      categoryScores.staff = await this.calculators.staff.calculate(
        home,
        questionnaire,
        enrichments
      );
      categoryScores.cqc = await this.calculators.cqc.calculate(
        home,
        questionnaire,
        enrichments
      );
      categoryScores.social = await this.calculators.social.calculate(
        home,
        questionnaire,
        enrichments
      );
      categoryScores.services = await this.calculators.services.calculate(
        home,
        questionnaire,
        enrichments
      );

      // Calculate total score (weighted sum, max 156 points)
      const totalScore =
        categoryScores.medical * weights.medical +
        categoryScores.safety * weights.safety +
        categoryScores.location * weights.location +
        categoryScores.financial * weights.financial +
        categoryScores.staff * weights.staff +
        categoryScores.cqc * weights.cqc +
        categoryScores.social * weights.social +
        categoryScores.services * weights.services;

      scored.push({
        home,
        score: Math.round(totalScore * 100) / 100, // Round to 2 decimals
        categoryScores,
      });
    }

    // Sort by score (descending)
    scored.sort((a, b) => b.score - a.score);

    return scored;
  }
}



