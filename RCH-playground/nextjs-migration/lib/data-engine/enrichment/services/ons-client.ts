/**
 * ONS API Client
 * Client for Office for National Statistics API
 * 
 * API Documentation: https://www.ons.gov.uk/developer
 */

import { createLogger } from '@/lib/shared/utils/logger';
import { retryWithTimeout } from '@/lib/shared/utils/retry';

const logger = createLogger({ module: 'ONSClient' });

export interface ONSWellbeingData {
  lsoa_code?: string;
  local_authority?: string;
  wellbeing_score?: number; // 0-100
  economic_score?: number; // 0-100
  demographics?: {
    over_65_percent?: number;
    population_density?: number;
  };
}

export interface ONSGeography {
  lsoa_code: string;
  local_authority: string;
  region?: string;
}

/**
 * ONS API Client
 */
export class ONSClient {
  private baseUrl = 'https://api.beta.ons.gov.uk/v1';
  private defaultTimeout = 15000; // 15 seconds

  constructor() {
    // ONS API is generally free/public, but may require registration
  }

  /**
   * Make request to ONS API
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
            `ONS API error: ${response.status}`
          );
          
          if (response.status === 429) {
            throw new Error('ONS API rate limit exceeded.');
          }
          throw new Error(
            `ONS API request failed with status ${response.status}: ${errorBody}`
          );
        }
        return response.json() as T;
      },
      timeout,
      { maxAttempts: 3, initialDelay: 2000 }
    );
  }

  /**
   * Get LSOA code from postcode
   * Note: This is a simplified implementation. In production, you'd use a postcode-to-LSOA lookup service.
   */
  async getLSOAFromPostcode(postcode: string): Promise<string | null> {
    try {
      // This is a placeholder - actual implementation would use ONS postcode directory
      // For now, return null and let the service handle it
      return null;
    } catch (error) {
      logger.error(
        { error: String(error), postcode },
        'ONS getLSOAFromPostcode failed'
      );
      return null;
    }
  }

  /**
   * Get wellbeing data for LSOA
   */
  async getWellbeingData(lsoaCode: string): Promise<ONSWellbeingData | null> {
    try {
      // This is a placeholder - actual implementation would fetch from ONS datasets
      // For now, return null and let the service handle it
      return null;
    } catch (error) {
      logger.error(
        { error: String(error), lsoaCode },
        'ONS getWellbeingData failed'
      );
      return null;
    }
  }

  /**
   * Get geography data from postcode
   */
  async getGeographyFromPostcode(
    postcode: string
  ): Promise<ONSGeography | null> {
    try {
      // This is a placeholder - actual implementation would use ONS postcode directory
      // For now, return null and let the service handle it
      return null;
    } catch (error) {
      logger.error(
        { error: String(error), postcode },
        'ONS getGeographyFromPostcode failed'
      );
      return null;
    }
  }
}



