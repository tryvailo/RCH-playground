/**
 * Data Loader
 * Universal data loader with fallback mechanisms
 */

import { CareHome, PostcodeInfo } from '@/lib/shared/types/care-home';
import { DatabaseSource } from '../sources/database';
import { CSVLoader } from '../sources/csv-loader';
import { PostcodeResolver } from '../sources/postcode-resolver';
import { calculateDistanceKm, validateCoordinates } from '../utils/geo';

export interface DataLoaderConfig {
  localAuthority?: string;
  careType: string;
  userLat?: number;
  userLon?: number;
  maxDistanceKm?: number;
  limit?: number;
}

export class DataLoader {
  private dbSource: DatabaseSource;
  private csvLoader: CSVLoader;
  private postcodeResolver: PostcodeResolver;

  constructor() {
    this.dbSource = new DatabaseSource();
    this.csvLoader = new CSVLoader();
    this.postcodeResolver = new PostcodeResolver();
  }

  /**
   * Universal method to load care homes
   * Tries different sources with fallback
   * 
   * @param config Loader configuration
   * @returns Array of care homes
   */
  async loadCareHomes(config: DataLoaderConfig): Promise<CareHome[]> {
    // 1. Try to load from PostgreSQL database
    try {
      const homes = await this.dbSource.loadHomes(config);
      if (homes.length > 0) {
        console.log(`✅ Loaded ${homes.length} homes from database`);
        return this.calculateDistances(homes, config.userLat, config.userLon);
      }
    } catch (error) {
      console.warn('Database load failed, trying CSV:', error);
    }

    // 2. Fallback: CSV files
    try {
      const homes = await this.csvLoader.loadHomes(config);
      if (homes.length > 0) {
        console.log(`✅ Loaded ${homes.length} homes from CSV`);
        return this.calculateDistances(homes, config.userLat, config.userLon);
      }
    } catch (error) {
      console.warn('CSV load failed:', error);
    }

    // 3. Fallback: Mock data (for development)
    console.warn('All data sources failed, returning empty array');
    return [];
  }

  /**
   * Resolve postcode to coordinates and local authority
   * 
   * @param postcode UK postcode
   * @returns Postcode info
   */
  async resolvePostcode(postcode: string): Promise<PostcodeInfo> {
    return this.postcodeResolver.resolve(postcode);
  }

  /**
   * Calculate distances for all homes
   * 
   * @param homes Array of care homes
   * @param userLat User latitude
   * @param userLon User longitude
   * @returns Homes with calculated distances
   */
  private calculateDistances(
    homes: CareHome[],
    userLat?: number,
    userLon?: number
  ): CareHome[] {
    if (!userLat || !userLon) {
      return homes;
    }

    if (!validateCoordinates(userLat, userLon)) {
      console.warn('Invalid user coordinates, skipping distance calculation');
      return homes;
    }

    return homes.map((home) => {
      if (home.distanceKm !== undefined && home.distanceKm < 999) {
        return home; // Distance already calculated
      }

      if (home.latitude && home.longitude) {
        try {
          if (validateCoordinates(home.latitude, home.longitude)) {
            const distance = calculateDistanceKm(
              userLat,
              userLon,
              home.latitude,
              home.longitude
            );
            return { ...home, distanceKm: Math.round(distance * 100) / 100 };
          }
        } catch (error) {
          console.warn(`Failed to calculate distance for ${home.name}:`, error);
        }
      }

      return { ...home, distanceKm: 9999.0 };
    });
  }
}



