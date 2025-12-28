/**
 * CQC API Client
 * Client for Care Quality Commission (CQC) API
 * 
 * API Documentation: https://www.cqc.org.uk/about-us/transparency/using-cqc-data
 */

import { createLogger } from '@/lib/shared/utils/logger';
import { retryWithTimeout } from '@/lib/shared/utils/retry';

const logger = createLogger({ module: 'CQCClient' });

export interface CQCLocation {
  locationId: string;
  name: string;
  providerId?: string;
  overallRating?: string;
  safeRating?: string;
  effectiveRating?: string;
  caringRating?: string;
  responsiveRating?: string;
  wellLedRating?: string;
  lastInspectionDate?: string;
  publicationDate?: string;
  reportUrl?: string;
  regulatedActivities?: any;
  [key: string]: any;
}

export interface CQCInspection {
  inspectionId?: string;
  inspectionDate: string;
  overallRating?: string;
  safeRating?: string;
  effectiveRating?: string;
  caringRating?: string;
  responsiveRating?: string;
  wellLedRating?: string;
  reportUrl?: string;
  [key: string]: any;
}

export interface CQCEnforcementAction {
  actionId?: string;
  actionType: string; // "Warning Notice", "Condition", etc.
  actionDate: string;
  description?: string;
  status?: string;
  [key: string]: any;
}

export interface CQCProviderLocation {
  locationId: string;
  name: string;
  overallRating?: string;
  lastInspectionDate?: string;
  [key: string]: any;
}

/**
 * CQC API Client
 */
export class CQCClient {
  private baseUrl = 'https://api.cqc.org.uk/public/v1';
  private apiKey: string;
  private defaultTimeout = 30000; // 30 seconds

  constructor(apiKey?: string) {
    this.apiKey = apiKey || process.env.CQC_API_KEY || '';
    
    if (!this.apiKey || this.apiKey.length < 10) {
      logger.warn('CQC API key not provided or invalid. Some features may not work.');
    }
  }

  /**
   * Make authenticated request to CQC API
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

    const headers: HeadersInit = {
      'Accept': 'application/json',
      'Ocp-Apim-Subscription-Key': this.apiKey,
    };

    return retryWithTimeout(
      async () => {
        const response = await fetch(url.toString(), { headers });

        if (!response.ok) {
          const errorBody = await response.text();
          const errorMsg = `CQC API error: ${response.status} - ${errorBody}`;
          logger.error(
            { url: url.toString(), status: response.status, body: errorBody },
            errorMsg
          );
          
          if (response.status === 401) {
            throw new Error(
              'CQC API authentication failed (401 Unauthorized). Check API key.'
            );
          }
          if (response.status === 429) {
            throw new Error('CQC API rate limit exceeded.');
          }
          throw new Error(
            `CQC API request failed with status ${response.status}: ${errorBody}`
          );
        }
        return response.json() as T;
      },
      timeout,
      { maxAttempts: 3, initialDelay: 2000 }
    );
  }

  /**
   * Get location details by location ID
   */
  async getLocation(locationId: string): Promise<CQCLocation | null> {
    try {
      const data = await this.makeRequest<CQCLocation>(
        `/locations/${locationId}`,
        {},
        this.defaultTimeout
      );
      return data;
    } catch (error) {
      logger.error(
        { error: String(error), locationId },
        'CQC getLocation failed'
      );
      return null;
    }
  }

  /**
   * Get inspection history for a location (5+ years)
   */
  async getLocationInspectionHistory(
    locationId: string,
    limit: number = 50
  ): Promise<CQCInspection[]> {
    try {
      // CQC API endpoint for inspection history
      // Note: Actual endpoint may vary, this is a placeholder structure
      const data = await this.makeRequest<{ inspections: CQCInspection[] }>(
        `/locations/${locationId}/inspections`,
        { limit },
        this.defaultTimeout
      );
      return data.inspections || [];
    } catch (error) {
      logger.error(
        { error: String(error), locationId },
        'CQC getLocationInspectionHistory failed'
      );
      return [];
    }
  }

  /**
   * Get enforcement actions for a location
   */
  async getLocationEnforcementActions(
    locationId: string
  ): Promise<CQCEnforcementAction[]> {
    try {
      // CQC API endpoint for enforcement actions
      const data = await this.makeRequest<{ actions: CQCEnforcementAction[] }>(
        `/locations/${locationId}/enforcement-actions`,
        {},
        this.defaultTimeout
      );
      return data.actions || [];
    } catch (error) {
      logger.error(
        { error: String(error), locationId },
        'CQC getLocationEnforcementActions failed'
      );
      return [];
    }
  }

  /**
   * Get all locations for a provider
   */
  async getProviderLocations(
    providerId: string
  ): Promise<CQCProviderLocation[]> {
    try {
      const data = await this.makeRequest<{ locations: CQCProviderLocation[] }>(
        `/providers/${providerId}/locations`,
        {},
        this.defaultTimeout
      );
      return data.locations || [];
    } catch (error) {
      logger.error(
        { error: String(error), providerId },
        'CQC getProviderLocations failed'
      );
      return [];
    }
  }

  /**
   * Get historical ratings for a location
   */
  async getLocationHistoricalRatings(
    locationId: string
  ): Promise<CQCInspection[]> {
    // This is essentially the same as inspection history
    return this.getLocationInspectionHistory(locationId);
  }
}

