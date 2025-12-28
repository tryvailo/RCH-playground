/**
 * Constants for Free Report
 * Includes default texts, fallback values, and configuration
 */

/**
 * Default photo URL fallback (Unsplash placeholder)
 */
export const DEFAULT_PHOTO_URL = 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800&h=600&fit=crop&q=80';

/**
 * "Why this home" explanation texts for each match type
 */
export const WHY_THIS_HOME_TEXTS: Record<'Safe Bet' | 'Best Value' | 'Premium', string> = {
  'Safe Bet': 'Excellent balance of price and quality. High CQC rating and close location make this home a safe choice.',
  'Best Value': 'Best price-to-quality ratio. Affordable price while maintaining high care standards.',
  'Premium': 'Premium option with outstanding CQC rating. Perfect choice for those seeking the highest quality of care.',
};

/**
 * Default fallback text if match_type is unknown
 */
export const DEFAULT_WHY_THIS_HOME = 'Recommended based on quality, price, and location.';

/**
 * Price range calculation: ±10% from weekly cost
 */
export const PRICE_RANGE_PERCENT = 0.1; // 10%

/**
 * Default band number if not provided
 */
export const DEFAULT_BAND = 3;

/**
 * Default MSIF lower bound fallback values by care type
 */
export const DEFAULT_MSIF_FALLBACK: Record<string, number> = {
  residential: 700,
  nursing: 1048,
  residential_dementia: 800,
  nursing_dementia: 1048,
  default: 700,
};


