/**
 * Calculator Base Class
 * Base class for all category calculators
 * Ported from Python services/matching/calculator_base.py
 */

export abstract class CategoryCalculator {
  abstract readonly categoryName: string;
  abstract readonly maxPoints: number;

  /**
   * Calculate score for this category
   * 
   * @param home Care home data
   * @param userProfile User questionnaire
   * @param enrichedData Enriched data
   * @returns Normalized score (0-1.0)
   */
  abstract calculate(
    home: any,
    userProfile: any,
    enrichedData: any
  ): Promise<number>;

  /**
   * Extract field from nested object safely
   */
  protected extractField(
    obj: any,
    ...path: string[]
  ): any {
    let current = obj;
    for (const key of path) {
      if (current == null || typeof current !== 'object') {
        return undefined;
      }
      current = current[key];
    }
    return current;
  }

  /**
   * Safe float conversion
   */
  protected safeFloat(value: any, defaultValue: number = 0): number {
    if (value == null) return defaultValue;
    const num = parseFloat(value);
    return isNaN(num) ? defaultValue : num;
  }

  /**
   * Safe int conversion
   */
  protected safeInt(value: any, defaultValue: number = 0): number {
    if (value == null) return defaultValue;
    const num = parseInt(value, 10);
    return isNaN(num) ? defaultValue : num;
  }

  /**
   * Safe list conversion
   */
  protected safeList(value: any): any[] {
    if (Array.isArray(value)) return value;
    if (value == null) return [];
    return [value];
  }

  /**
   * Normalize string
   */
  protected normalizeString(value: any): string {
    if (typeof value === 'string') return value.toLowerCase().trim();
    if (value == null) return '';
    return String(value).toLowerCase().trim();
  }

  /**
   * Score with scale (tiered scoring)
   */
  protected scoreWithScale(
    value: number,
    thresholds: number[],
    scores: number[]
  ): number {
    for (let i = 0; i < thresholds.length; i++) {
      if (value >= thresholds[i]) {
        return scores[i] || 0;
      }
    }
    return 0;
  }

  /**
   * Check if container contains value
   */
  protected checkContains(container: any, value: string): boolean {
    if (container == null) return false;
    const str = String(container).toLowerCase();
    return str.includes(value.toLowerCase());
  }

  /**
   * Score rating
   */
  protected scoreRating(rating: string): number {
    const ratingLower = this.normalizeString(rating);
    if (ratingLower.includes('outstanding')) return 4;
    if (ratingLower.includes('good')) return 3;
    if (ratingLower.includes('requires improvement')) return 2;
    if (ratingLower === 'inadequate') return 1;
    return 0;
  }
}



