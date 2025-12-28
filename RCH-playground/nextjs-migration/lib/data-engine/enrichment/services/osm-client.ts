/**
 * OpenStreetMap (OSM) Client
 * Client for OpenStreetMap Overpass API and Nominatim
 * 
 * API Documentation: 
 * - Overpass API: https://wiki.openstreetmap.org/wiki/Overpass_API
 * - Nominatim: https://nominatim.org/release-docs/develop/api/Overview/
 */

import { createLogger } from '@/lib/shared/utils/logger';
import { retryWithTimeout } from '@/lib/shared/utils/retry';

const logger = createLogger({ module: 'OSMClient' });

export interface OSMAmenity {
  name: string;
  type: string;
  category: string;
  coordinates: {
    latitude: number;
    longitude: number;
  };
  distance_m: number;
}

export interface OSMWalkability {
  score: number; // 0-100
  rating: string;
  amenities_count: number;
  public_transport_count: number;
}

export interface OSMPublicTransport {
  bus_stops: Array<{
    name: string;
    coordinates: { lat: number; lng: number };
    distance_m: number;
  }>;
  rail_stations: Array<{
    name: string;
    coordinates: { lat: number; lng: number };
    distance_m: number;
  }>;
}

/**
 * OSM Client
 */
export class OSMClient {
  private overpassUrl = 'https://overpass-api.de/api/interpreter';
  private nominatimUrl = 'https://nominatim.openstreetmap.org';
  private defaultTimeout = 30000; // 30 seconds (Overpass can be slow)

  constructor() {
    // OSM APIs are free/public, but require respectful rate limiting
  }

  /**
   * Make request to Overpass API
   */
  private async makeOverpassRequest(
    query: string,
    timeout: number = this.defaultTimeout
  ): Promise<any> {
    return retryWithTimeout(
      async () => {
        const response = await fetch(this.overpassUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: `data=${encodeURIComponent(query)}`,
        });

        if (!response.ok) {
          const errorBody = await response.text();
          logger.error(
            { url: this.overpassUrl, status: response.status, body: errorBody },
            `Overpass API error: ${response.status}`
          );
          throw new Error(
            `Overpass API request failed with status ${response.status}: ${errorBody}`
          );
        }
        return response.json();
      },
      timeout,
      { maxAttempts: 2, initialDelay: 2000 }
    );
  }

  /**
   * Get nearby amenities
   */
  async getNearbyAmenities(
    latitude: number,
    longitude: number,
    radiusM: number = 1600,
    categories?: string[]
  ): Promise<OSMAmenity[]> {
    try {
      // Overpass query for amenities
      const query = `
        [out:json][timeout:25];
        (
          node["amenity"~"^(park|pharmacy|shop|hospital|clinic)$"](around:${radiusM},${latitude},${longitude});
          way["amenity"~"^(park|pharmacy|shop|hospital|clinic)$"](around:${radiusM},${latitude},${longitude});
        );
        out center;
      `;

      const data = await this.makeOverpassRequest(query);

      const amenities: OSMAmenity[] = [];
      if (data.elements) {
        for (const element of data.elements) {
          const lat = element.lat || element.center?.lat;
          const lon = element.lon || element.center?.lon;
          
          if (lat && lon) {
            const distance = this.calculateDistance(
              latitude,
              longitude,
              lat,
              lon
            );

            amenities.push({
              name: element.tags?.name || 'Unnamed',
              type: element.tags?.amenity || 'unknown',
              category: this.categorizeAmenity(element.tags?.amenity),
              coordinates: { latitude: lat, longitude: lon },
              distance_m: Math.round(distance),
            });
          }
        }
      }

      return amenities.sort((a, b) => a.distance_m - b.distance_m);
    } catch (error) {
      logger.error(
        { error: String(error), latitude, longitude, radiusM },
        'OSM getNearbyAmenities failed'
      );
      return [];
    }
  }

  /**
   * Calculate walkability score
   */
  async calculateWalkability(
    latitude: number,
    longitude: number,
    radiusM: number = 800
  ): Promise<OSMWalkability> {
    try {
      const amenities = await this.getNearbyAmenities(
        latitude,
        longitude,
        radiusM
      );

      const publicTransport = await this.getPublicTransport(
        latitude,
        longitude
      );

      const amenitiesCount = amenities.length;
      const transportCount =
        publicTransport.bus_stops.length + publicTransport.rail_stations.length;

      // Simple scoring algorithm
      let score = 0;
      if (amenitiesCount >= 10) score += 40;
      else if (amenitiesCount >= 5) score += 30;
      else if (amenitiesCount >= 2) score += 20;
      else score += 10;

      if (transportCount >= 5) score += 40;
      else if (transportCount >= 2) score += 30;
      else if (transportCount >= 1) score += 20;
      else score += 10;

      // Density bonus
      if (amenitiesCount + transportCount >= 15) score += 20;
      else if (amenitiesCount + transportCount >= 10) score += 10;

      score = Math.min(100, score);

      let rating = 'Poor';
      if (score >= 80) rating = 'Excellent';
      else if (score >= 60) rating = 'Good';
      else if (score >= 40) rating = 'Average';

      return {
        score,
        rating,
        amenities_count: amenitiesCount,
        public_transport_count: transportCount,
      };
    } catch (error) {
      logger.error(
        { error: String(error), latitude, longitude },
        'OSM calculateWalkability failed'
      );
      return {
        score: 0,
        rating: 'Unknown',
        amenities_count: 0,
        public_transport_count: 0,
      };
    }
  }

  /**
   * Get public transport stops
   */
  async getPublicTransport(
    latitude: number,
    longitude: number
  ): Promise<OSMPublicTransport> {
    try {
      // Bus stops within 800m
      const busQuery = `
        [out:json][timeout:25];
        (
          node["highway"="bus_stop"](around:800,${latitude},${longitude});
        );
        out;
      `;

      // Rail stations within 1600m
      const railQuery = `
        [out:json][timeout:25];
        (
          node["railway"="station"](around:1600,${latitude},${longitude});
          way["railway"="station"](around:1600,${latitude},${longitude});
        );
        out center;
      `;

      const [busData, railData] = await Promise.allSettled([
        this.makeOverpassRequest(busQuery),
        this.makeOverpassRequest(railQuery),
      ]);

      const busStops =
        busData.status === 'fulfilled' && busData.value.elements
          ? busData.value.elements.map((element: any) => ({
              name: element.tags?.name || 'Bus Stop',
              coordinates: {
                lat: element.lat,
                lng: element.lon,
              },
              distance_m: Math.round(
                this.calculateDistance(
                  latitude,
                  longitude,
                  element.lat,
                  element.lon
                )
              ),
            }))
          : [];

      const railStations =
        railData.status === 'fulfilled' && railData.value.elements
          ? railData.value.elements.map((element: any) => {
              const lat = element.lat || element.center?.lat;
              const lng = element.lon || element.center?.lon;
              return {
                name: element.tags?.name || 'Rail Station',
                coordinates: { lat, lng },
                distance_m: Math.round(
                  this.calculateDistance(latitude, longitude, lat, lng)
                ),
              };
            })
          : [];

      return {
        bus_stops: busStops.sort((a: any, b: any) => a.distance_m - b.distance_m),
        rail_stations: railStations.sort((a: any, b: any) => a.distance_m - b.distance_m),
      };
    } catch (error) {
      logger.error(
        { error: String(error), latitude, longitude },
        'OSM getPublicTransport failed'
      );
      return { bus_stops: [], rail_stations: [] };
    }
  }

  /**
   * Categorize amenity type
   */
  private categorizeAmenity(amenity: string): string {
    const categories: Record<string, string> = {
      park: 'parks',
      pharmacy: 'healthcare',
      shop: 'shopping',
      hospital: 'healthcare',
      clinic: 'healthcare',
    };
    return categories[amenity] || 'other';
  }

  /**
   * Calculate distance between two coordinates (Haversine formula)
   */
  private calculateDistance(
    lat1: number,
    lon1: number,
    lat2: number,
    lon2: number
  ): number {
    const R = 6371000; // Earth radius in meters
    const dLat = ((lat2 - lat1) * Math.PI) / 180;
    const dLon = ((lon2 - lon1) * Math.PI) / 180;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos((lat1 * Math.PI) / 180) *
        Math.cos((lat2 * Math.PI) / 180) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }
}

