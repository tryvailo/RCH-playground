import axios from 'axios';
import type { ProfessionalQuestionnaireResponse, ProfessionalCareHome } from '../types';

/**
 * Load care homes from SQLite database via API
 * This function exclusively uses SQLite - no CSV fallback
 */
/**
 * Convert distance string to number in km
 * Handles formats: "within_5km", "within_15km", "within_30km", "distance_not_important", "5km", "15km", etc.
 */
function convertDistanceToKm(distance: string | undefined): number | undefined {
  if (!distance || distance === 'distance_not_important') {
    return undefined; // No distance limit
  }
  
  // Handle "within_Xkm" format
  if (distance.startsWith('within_')) {
    const kmMatch = distance.match(/within_(\d+)km/);
    if (kmMatch) {
      return parseFloat(kmMatch[1]);
    }
  }
  
  // Handle "Xkm" format (legacy)
  const kmMatch = distance.match(/(\d+)km/);
  if (kmMatch) {
    return parseFloat(kmMatch[1]);
  }
  
  // Try to parse as number directly
  const num = parseFloat(distance);
  if (!isNaN(num)) {
    return num;
  }
  
  // Default fallback
  return 30; // Default to 30km if can't parse
}

export async function loadCareHomes(
  questionnaire: ProfessionalQuestionnaireResponse,
  apiBaseUrl: string
): Promise<ProfessionalCareHome[]> {
  if (!questionnaire.section_2_location_budget.q5_preferred_city) {
    throw new Error('City/postcode is required');
  }

  try {
    // Endpoint uses SQLite database exclusively
    // ✅ FIX: Use relative path through Vite proxy by default (like other features)
    // Only use absolute URL if apiBaseUrl is explicitly set
    const url = apiBaseUrl ? `${apiBaseUrl}/api/care-homes` : '/api/care-homes';

    // ✅ FIX: Convert distance string to number (backend expects float, not string)
    const distanceKm = convertDistanceToKm(questionnaire.section_2_location_budget.q6_max_distance);

    // ✅ REFACTOR: Load homes matching non-strict filters (postcode, distance)
    // Use reasonable limit (500) to avoid timeout - matching algorithm can work with this
    // Quality filtering happens during matching, not during load
    const response = await axios.get<any>(url, {
      params: {
        postcode: questionnaire.section_2_location_budget.q5_preferred_city,
        distance: distanceKm, // ✅ FIX: Send as number, not string
        limit: 500, // ✅ Reasonable limit to prevent timeout while still getting good candidates
        cache: true,
      },
      timeout: 60000, // ✅ Increased timeout to 60s for postcode resolution and data loading
    });

    // ✅ FIX: Validate response structure immediately
    if (!response || !response.data) {
      throw new Error('Invalid API response: missing data');
    }

    // ✅ FIX: Check for empty homes array immediately
    const rawHomes = response.data.homes || [];
    if (!Array.isArray(rawHomes)) {
      throw new Error('Invalid API response: homes is not an array');
    }
    
    if (rawHomes.length === 0) {
      const postcode = questionnaire.section_2_location_budget.q5_preferred_city;
      throw new Error(
        `No care homes found for postcode "${postcode}". ` +
        `Please try a different location or increase the search distance.`
      );
    }

    // Transform to ProfessionalCareHome format
    // ✅ REFACTOR: Don't slice here - we need all homes for matching
    const homes: ProfessionalCareHome[] = rawHomes
      .map((home: any, index: number) => {
        // ✅ FIX: Validate required fields
        if (!home.name || !home.postcode) {
          console.warn(`⚠️ Home at index ${index} missing required fields:`, home);
        }
        
        return {
          id: home.id || `home-${index}`,
          name: home.name || '',
          location: home.address || '',
          postcode: home.postcode || '',
          strategy: 'default',
          strategyLabel: 'Standard Match',
          cqcRating: home.cqc_rating || 'Not Rated',
          distance: `${home.distance_km || 0}km`,
          weeklyPrice: home.weekly_cost || 0,
          matchScore: 0,
          lastAudited: new Date().toISOString(),
          dataSource: ['rch-db'],
          whyChosen: 'Selected from database',
          whyAligns: ['Selected from database'], // Required field - must be array
          keyStrengths: [],
          mustVerify: [],
          contact: {
            phone: home.phone || '',
            email: home.email || '',
          },
          factorScores: [],
        };
      })
      .filter((home) => {
        // ✅ FIX: Filter out homes with missing critical data
        return home.name && home.postcode;
      });

    // ✅ FIX: Final check after filtering
    if (homes.length === 0) {
      throw new Error(
        'No valid care homes found after filtering. ' +
        'All homes are missing required data (name or postcode).'
      );
    }

    console.log(`✅ Loaded ${homes.length} care homes`);
    return homes;
  } catch (error) {
    console.error('❌ Failed to load care homes:', error);
    
    // ✅ FIX: Better error messages with network error handling
    if (axios.isAxiosError(error)) {
      // Network error - server not reachable
      if (error.code === 'ERR_NETWORK' || error.code === 'ERR_CONNECTION_REFUSED' || 
          (error.message && error.message.includes('Network Error'))) {
        throw new Error(
          'Cannot connect to backend server. ' +
          'Please make sure the backend server is running. ' +
          'If using Vite proxy, ensure backend is on port 3001. ' +
          'If backend is on a different port, set VITE_API_URL environment variable.'
        );
      }
      if (error.response?.status === 422) {
        const detail = error.response.data?.detail || error.response.data?.message || 'Validation error';
        throw new Error(`Invalid request parameters: ${detail}. Please check your location and distance settings.`);
      }
      if (error.response?.status === 400) {
        const detail = error.response.data?.detail || error.response.data?.message || 'Bad request';
        throw new Error(`Invalid request: ${detail}`);
      }
      if (error.response?.status === 500) {
        throw new Error('Server error while loading care homes. Please try again later.');
      }
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        throw new Error('Request timed out. Please try again or reduce the search distance.');
      }
    }
    
    throw new Error(`Failed to load care homes: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}
