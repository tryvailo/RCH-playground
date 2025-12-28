/**
 * Reasoning Generator
 * Generates human-readable reasoning for home selection
 * Ported from Python services/matching/reasoning_generator.py
 */

export interface Reasoning {
  summary: string;
  key_strengths: string[];
  considerations?: string[];
}

export class ReasoningGenerator {
  /**
   * Generate reasoning for a home
   * 
   * @param home Care home
   * @param category Selection category
   * @param questionnaire User questionnaire
   * @param enrichedData Enriched data
   * @param fullHomeData Full home data with scores
   * @returns Reasoning object
   */
  generateReasoning(
    home: any,
    category: string,
    questionnaire: any,
    enrichedData: any,
    fullHomeData: any
  ): Reasoning {
    const strengths: string[] = [];
    const considerations: string[] = [];

    // Generate based on category
    if (category === 'best_overall') {
      strengths.push('Best overall match based on comprehensive scoring');
    } else if (category === 'best_medical_safety') {
      strengths.push('Excellent medical capabilities and safety standards');
    } else if (category === 'best_value') {
      strengths.push('Best value for money with strong quality-to-price ratio');
    }

    // Add strengths based on scores
    const categoryScores = fullHomeData?.categoryScores || {};
    if (categoryScores.medical > 0.7) {
      strengths.push('Strong medical care capabilities');
    }
    if (categoryScores.safety > 0.7) {
      strengths.push('High safety and quality standards');
    }
    if (categoryScores.location > 0.7) {
      strengths.push('Convenient location with good access');
    }
    if (categoryScores.financial > 0.7) {
      strengths.push('Good financial stability');
    }

    // Add considerations
    if (categoryScores.medical < 0.5) {
      considerations.push('Medical capabilities may be limited');
    }
    if (categoryScores.safety < 0.5) {
      considerations.push('Review safety records carefully');
    }

    // Generate summary
    const summary = this.generateSummary(home, category, strengths);

    return {
      summary,
      key_strengths: strengths.length > 0 ? strengths : ['Good overall match'],
      considerations: considerations.length > 0 ? considerations : undefined,
    };
  }

  /**
   * Generate summary text
   */
  private generateSummary(
    home: any,
    category: string,
    strengths: string[]
  ): string {
    const homeName = home.name || 'This care home';
    const categoryMap: Record<string, string> = {
      best_overall: 'best overall match',
      best_medical_safety: 'excellent medical and safety match',
      best_value: 'best value option',
    };

    const categoryText = categoryMap[category] || 'good match';

    if (strengths.length > 0) {
      return `${homeName} is the ${categoryText} for your needs. ${strengths[0]}.`;
    }

    return `${homeName} is a ${categoryText} based on our comprehensive analysis.`;
  }
}



