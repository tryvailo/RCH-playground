/**
 * Normalization utilities for Free Report data
 * Handles normalization of postcode and care_type before sending to backend
 */

/**
 * Normalize postcode: remove spaces, ensure uppercase
 * Example: "B11 1AA" -> "B111AA"
 */
export const normalizePostcode = (postcode?: string): string | undefined => {
  if (!postcode) return undefined;
  const normalized = postcode.replace(/\s+/g, '').toUpperCase().trim();
  
  // Базовая проверка формата UK postcode (5-8 символов)
  if (normalized.length < 5 || normalized.length > 8) {
    console.warn(`Invalid postcode format: ${postcode} (normalized: ${normalized})`);
  }
  
  return normalized;
};

/**
 * Normalize care_type to match backend enum values
 * Handles common variations: "Residential Care", "nursing", "DEMENTIA", etc.
 * 
 * @param careType - Input care type string
 * @returns Normalized care type: 'residential' | 'nursing' | 'dementia' | 'respite' | undefined
 */
export const normalizeCareType = (careType?: string): string | undefined => {
  if (!careType) return undefined;
  
  const normalized = careType.toLowerCase().trim();
  
  // Map common variations to backend enum values
  if (normalized.includes('residential') && !normalized.includes('dementia')) {
    return 'residential';
  }
  
  if (normalized.includes('nursing')) {
    return 'nursing';
  }
  
  if (normalized.includes('dementia')) {
    return 'dementia';
  }
  
  if (normalized.includes('respite')) {
    return 'respite';
  }
  
  // Если не распознан, предупредить и вернуть как есть
  const validTypes = ['residential', 'nursing', 'dementia', 'respite'];
  if (!validTypes.includes(normalized)) {
    console.warn(`Unknown care type: ${careType} (normalized: ${normalized}), using as-is`);
  }
  
  return normalized;
};

/**
 * Get local authority from postcode
 * Used for MSIF lookup
 */
export const getLocalAuthorityFromPostcode = (postcode: string): string => {
  const postcodeUpper = postcode.toUpperCase().trim();
  
  // London postcodes
  if (postcodeUpper.match(/^(SW|SE|NW|NE|E|W|N|WC|EC)/)) {
    return 'Westminster';
  }
  
  // Manchester
  if (postcodeUpper.startsWith('M')) {
    return 'Manchester';
  }
  
  // Birmingham
  if (postcodeUpper.startsWith('B')) {
    return 'Birmingham';
  }
  
  // Liverpool
  if (postcodeUpper.startsWith('L')) {
    return 'Liverpool';
  }
  
  // Leeds
  if (postcodeUpper.startsWith('LS')) {
    return 'Leeds';
  }
  
  // Camden (default for SW1)
  if (postcodeUpper.startsWith('SW1')) {
    return 'Camden';
  }
  
  return 'Westminster'; // Default fallback
};

