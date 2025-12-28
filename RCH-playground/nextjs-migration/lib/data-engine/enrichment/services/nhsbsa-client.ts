/**
 * NHSBSA API Client
 * Client for NHS Business Services Authority API
 * 
 * API Documentation: https://www.nhsbsa.nhs.uk/
 */

import { createLogger } from '@/lib/shared/utils/logger';
import { retryWithTimeout } from '@/lib/shared/utils/retry';

const logger = createLogger({ module: 'NHSBSAClient' });

export interface NHSBSAGPPractice {
  practice_code: string;
  practice_name: string;
  address?: string;
  postcode?: string;
  coordinates?: {
    latitude: number;
    longitude: number;
  };
  distance_km?: number;
}

export interface NHSBSAHealthProfile {
  practices_nearby: number;
  nearest_practices: NHSBSAGPPractice[];
  health_index?: number; // 0-100
}

/**
 * NHSBSA API Client
 */
export class NHSBSAClient {
  private baseUrl = 'https://www.nhsbsa.nhs.uk/api';
  private defaultTimeout = 20000; // 20 seconds

  constructor() {
    // NHSBSA API may require authentication or have specific endpoints
  }

  /**
   * Make request to NHSBSA API
   */
  private async makeRequest<T>(
    endpoint: string,
    params: Record<string, any> = {},
    timeout: number = this.defaultTimeout
  ): Promise<T> {
    const url = new URL(`${this.baseUrl}${endpoint}`);
    Object.keys(params).forEach((key) =>
      url.searchParams.append(key, String(params[key]))
    );

    return retryWithTimeout(
      async () => {
        const response = await fetch(url.toString(), {
          headers: {
            'Accept': 'application/json',
          },
        });

        if (!response.ok) {
          const errorBody = await response.text();
          logger.error(
            { url: url.toString(), status: response.status, body: errorBody },
            `NHSBSA API error: ${response.status}`
          );
          
          if (response.status === 429) {
            throw new Error('NHSBSA API rate limit exceeded.');
          }
          throw new Error(
            `NHSBSA API request failed with status ${response.status}: ${errorBody}`
          );
        }
        return response.json() as T;
      },
      timeout,
      { maxAttempts: 3, initialDelay: 2000 }
    );
  }

  /**
   * Get nearest GP practices
   */
  async getNearestGPPractices(
    latitude: number,
    longitude: number,
    maxDistanceKm: number = 5
  ): Promise<NHSBSAGPPractice[]> {
    try {
      // This is a placeholder - actual implementation would use NHSBSA API
      // For now, return empty array and let the service handle it
      // In production, you'd use the NHSBSA GP practice finder API
      return [];
    } catch (error) {
      logger.error(
        { error: String(error), latitude, longitude, maxDistanceKm },
        'NHSBSA getNearestGPPractices failed'
      );
      return [];
    }
  }

  /**
   * Get health profile for area
   */
  async getHealthProfile(
    postcode: string,
    latitude?: number,
    longitude?: number
  ): Promise<NHSBSAHealthProfile | null> {
    try {
      // This is a placeholder - actual implementation would fetch from NHSBSA datasets
      // For now, return null and let the service handle it
      return null;
    } catch (error) {
      logger.error(
        { error: String(error), postcode, latitude, longitude },
        'NHSBSA getHealthProfile failed'
      );
      return null;
    }
  }
}



