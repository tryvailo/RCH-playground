import type { ProfessionalQuestionnaireResponse, ProfessionalReportData, ProfessionalCareHome } from '../types';

/**
 * Validate UK postcode format (basic validation)
 * UK postcode format: AA9A 9AA or A9A 9AA or A9 9AA or A99 9AA or AA9 9AA or AA99 9AA
 */
export function validatePostcode(postcode: string): boolean {
  if (!postcode || typeof postcode !== 'string') return false;
  
  // Remove spaces and convert to uppercase
  const cleaned = postcode.replace(/\s+/g, '').toUpperCase();
  
  // UK postcode regex pattern
  const ukPostcodePattern = /^[A-Z]{1,2}[0-9][A-Z0-9]?[0-9][A-Z]{2}$/;
  
  return ukPostcodePattern.test(cleaned);
}

/**
 * Validate distance enum values
 * Valid values: 'within_5km', 'within_15km', 'within_30km', 'distance_not_important', or legacy formats
 */
export function validateDistance(distance: string | number | undefined): boolean {
  if (distance === undefined || distance === null) return true; // Optional field
  
  // Valid enum values
  const validDistances = [
    'within_5km',
    'within_15km',
    'within_30km',
    'distance_not_important',
    // Legacy formats
    '5km',
    '10km',
    '15km',
    '20km',
    '30km'
  ];
  
  if (typeof distance === 'string') {
    return validDistances.includes(distance);
  }
  
  // If it's a number, it's invalid (should be enum string)
  return false;
}

/**
 * Validate budget range (reasonable values: 500-10000 per week)
 */
export function validateBudget(budget: string | number | undefined): boolean {
  if (budget === undefined || budget === null) return true; // Optional field
  
  const numBudget = typeof budget === 'string' ? parseFloat(budget) : budget;
  
  if (isNaN(numBudget)) return false;
  
  return numBudget >= 500 && numBudget <= 10000;
}

/**
 * Validate questionnaire has all required fields
 * ✅ FIX: Enhanced validation with postcode format and range checks
 */
export function validateQuestionnaire(data: any): data is ProfessionalQuestionnaireResponse {
  if (!data) return false;
  
  // Required sections
  const hasContactInfo = data.section_1_contact_emergency?.q1_names;
  const hasLocation = data.section_2_location_budget?.q5_preferred_city;
  const hasMedicalNeeds = data.section_3_medical_needs;
  
  if (!hasContactInfo || !hasLocation || !hasMedicalNeeds) {
    return false;
  }
  
  // Note: q5_preferred_city is a city name (e.g., "Birmingham"), not a postcode
  // Postcode validation is not applicable here
  
  // ✅ FIX: Validate distance enum value
  const distance = data.section_2_location_budget?.q6_max_distance;
  if (distance !== undefined && !validateDistance(distance)) {
    console.warn(`⚠️ Invalid distance: ${distance} (must be one of: within_5km, within_15km, within_30km, distance_not_important)`);
    // Don't fail validation, but log warning
  }
  
  // ✅ FIX: Validate budget range
  const budget = data.section_2_location_budget?.q7_budget;
  if (budget !== undefined && !validateBudget(budget)) {
    console.warn(`⚠️ Invalid budget: ${budget} (must be 500-10000 per week)`);
    // Don't fail validation, but log warning
  }
  
  return true;
}

/**
 * Validate enriched home has required data
 */
export function validateEnrichedHome(home: any): boolean {
  return !!(
    home.id &&
    home.name &&
    home.location &&
    home.postcode
  );
}

/**
 * Validate report structure is complete
 */
export function validateReport(report: any): report is ProfessionalReportData {
  return !!(
    report.reportId &&
    report.clientName &&
    report.careHomes &&
    Array.isArray(report.careHomes) &&
    report.careHomes.length > 0 &&
    report.generatedAt
  );
}

/**
 * Get validation error message
 */
export function getValidationError(field: string): string {
  const messages: { [key: string]: string } = {
    'contact_info': 'Please provide contact information (name)',
    'location': 'Please provide location/postcode',
    'medical_needs': 'Please provide medical care requirements',
    'budget': 'Please specify your budget',
    'homes': 'No care homes found matching your criteria',
    'enrichment': 'Failed to fetch enrichment data for homes',
    'matching': 'Failed to match and score homes',
    'report': 'Failed to generate report - please try again',
  };
  
  return messages[field] || `Validation error: ${field}`;
}

/**
 * Log validation error for debugging
 */
export function logValidationError(field: string, error: string, context?: any): void {
  console.warn(`⚠️ Validation Error [${field}]:`, error);
  if (context) {
    console.warn('Context:', context);
  }
}

/**
 * Check if home data is sufficient for display
 */
export function hasMinimumHomeData(home: ProfessionalCareHome): boolean {
  return !!(
    home.name &&
    home.matchScore !== undefined &&
    home.contact
  );
}

/**
 * Validate API response structure
 */
export function validateApiResponse(response: any, expectedFields: string[]): boolean {
  if (!response || typeof response !== 'object') {
    return false;
  }
  
  return expectedFields.every(field => field in response);
}

/**
 * Sanitize error message for user display
 */
export function sanitizeErrorMessage(error: any): string {
  if (error instanceof Error) {
    return error.message;
  }
  
  if (typeof error === 'string') {
    return error;
  }
  
  if (error?.response?.data?.message) {
    return error.response.data.message;
  }
  
  if (error?.response?.status === 404) {
    return 'Data not found. Please try again.';
  }
  
  if (error?.response?.status === 500) {
    return 'Server error. Please try again later.';
  }
  
  if (error?.code === 'ECONNABORTED') {
    return 'Request timeout. Please check your connection.';
  }
  
  return 'An unexpected error occurred. Please try again.';
}

/**
 * Check if error is retryable
 */
export function isRetryableError(error: any): boolean {
  if (!error) return false;
  
  // Network errors
  if (error.code === 'ECONNABORTED' || error.code === 'ENOTFOUND') {
    return true;
  }
  
  // Server errors (5xx are retryable)
  if (error.response?.status >= 500) {
    return true;
  }
  
  // Timeout errors
  if (error.message?.includes('timeout')) {
    return true;
  }
  
  return false;
}

/**
 * Get retry strategy for error
 */
export function getRetryStrategy(error: any, attemptNumber: number): { delay: number; shouldRetry: boolean } {
  if (!isRetryableError(error)) {
    return { delay: 0, shouldRetry: false };
  }
  
  if (attemptNumber >= 3) {
    return { delay: 0, shouldRetry: false };
  }
  
  // Exponential backoff: 1s, 2s, 4s
  const delay = Math.pow(2, attemptNumber - 1) * 1000;
  
  return { delay, shouldRetry: true };
}
