/**
 * OS Places API Client
 * Client for Ordnance Survey Places API (AddressBase Premium)
 * 
 * API Documentation: https://osdatahub.os.uk/docs/places/overview
 */

import { createLogger } from '@/lib/shared/utils/logger';
import { retryWithTimeout } from '@/lib/shared/utils/retry';

const logger = createLogger({ module: 'OSPlacesClient' });

export interface OSPlacesAddress {
  uprn?: string;
  formatted_address: string;
  address_line_1?: string;
  address_line_2?: string;
  address_line_3?: string;
  post_town?: string;
  postcode: string;
  country?: string;
  centroid?: {
    latitude: number;
    longitude: number;
  };
}

export interface OSPlacesCoordinates {
  latitude: number;
  longitude: number;
  uprn?: string;
}

/**
 * OS Places API Client
 */
export class OSPlacesClient {
  private baseUrl = 'https://api.os.uk/search/places/v1';
  private apiKey: string;
  private defaultTimeout = 10000; // 10 seconds

  constructor(apiKey?: string) {
    this.apiKey = apiKey || process.env.OS_PLACES_API_KEY || '';
    
    if (!this.apiKey || this.apiKey.length < 10) {
      logger.warn('OS Places API key not provided. Some features may not work.');
    }
  }

  /**
   * Make authenticated request to OS Places API
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
    url.searchParams.append('key', this.apiKey);

    return retryWithTimeout(
      async () => {
        const response = await fetch(url.toString());

        if (!response.ok) {
          const errorBody = await response.text();
          logger.error(
            { url: url.toString(), status: response.status, body: errorBody },
            `OS Places API error: ${response.status}`
          );
          
          if (response.status === 401) {
            throw new Error('OS Places API authentication failed (401 Unauthorized). Check API key.');
          }
          if (response.status === 429) {
            throw new Error('OS Places API rate limit exceeded.');
          }
          throw new Error(
            `OS Places API request failed with status ${response.status}: ${errorBody}`
          );
        }
        return response.json() as T;
      },
      timeout,
      { maxAttempts: 3, initialDelay: 1000 }
    );
  }

  /**
   * Get address by postcode
   */
  async getAddressByPostcode(postcode: string): Promise<OSPlacesAddress | null> {
    try {
      const data = await this.makeRequest<{ results: any[] }>(
        '/postcode',
        { postcode: postcode.replace(/\s+/g, '') },
        this.defaultTimeout
      );
      
      if (data.results && data.results.length > 0) {
        const result = data.results[0];
        return {
          uprn: result.uprn,
          formatted_address: result.DPA?.ADDRESS || result.formatted_address,
          address_line_1: result.DPA?.ADDRESS_LINE_1,
          post_town: result.DPA?.POST_TOWN,
          postcode: result.DPA?.POSTCODE || postcode,
          country: result.DPA?.COUNTRY_CODE || 'GB',
          centroid: result.DPA?.LAT && result.DPA?.LON
            ? {
                latitude: parseFloat(result.DPA.LAT),
                longitude: parseFloat(result.DPA.LON),
              }
            : undefined,
        };
      }
      return null;
    } catch (error) {
      logger.error(
        { error: String(error), postcode },
        'OS Places getAddressByPostcode failed'
      );
      return null;
    }
  }

  /**
   * Create address from coordinates
   */
  async createAddressFromCoordinates(
    latitude: number,
    longitude: number
  ): Promise<OSPlacesAddress | null> {
    try {
      const data = await this.makeRequest<{ results: any[] }>(
        '/nearest',
        { lat: latitude, lon: longitude, radius: 100 },
        this.defaultTimeout
      );
      
      if (data.results && data.results.length > 0) {
        const result = data.results[0];
        return {
          uprn: result.uprn,
          formatted_address: result.DPA?.ADDRESS || result.formatted_address,
          address_line_1: result.DPA?.ADDRESS_LINE_1,
          post_town: result.DPA?.POST_TOWN,
          postcode: result.DPA?.POSTCODE,
          country: result.DPA?.COUNTRY_CODE || 'GB',
          centroid: {
            latitude,
            longitude,
          },
        };
      }
      return null;
    } catch (error) {
      logger.error(
        { error: String(error), latitude, longitude },
        'OS Places createAddressFromCoordinates failed'
      );
      return null;
    }
  }

  /**
   * Get coordinates from postcode
   */
  async getCoordinatesFromPostcode(
    postcode: string
  ): Promise<OSPlacesCoordinates | null> {
    const address = await this.getAddressByPostcode(postcode);
    if (address?.centroid) {
      return {
        latitude: address.centroid.latitude,
        longitude: address.centroid.longitude,
        uprn: address.uprn,
      };
    }
    return null;
  }
}



