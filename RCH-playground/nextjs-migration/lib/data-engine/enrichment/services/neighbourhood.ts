/**
 * Neighbourhood Analysis Enrichment Service
 * Enriches care homes with comprehensive neighbourhood/area analysis
 * 
 * Uses multiple sources:
 * - OS Places (Ordnance Survey) - coordinates, UPRN, addresses
 * - ONS (Office for National Statistics) - wellbeing, demographics, economics
 * - OpenStreetMap (OSM) - walkability, amenities, transport
 * - NHSBSA - health profiles, GP practices
 * - Environmental (опционально) - noise, pollution
 */

import { CareHome } from '@/lib/shared/types/care-home';
import { BaseEnrichmentService } from '../base-enrichment';
import {
  EnrichmentResult,
  EnrichmentContext,
  EnrichmentOptions,
} from '../types';
import { OSPlacesClient } from './os-places-client';
import { ONSClient } from './ons-client';
import { OSMClient } from './osm-client';
import { NHSBSAClient } from './nhsbsa-client';

export interface NeighbourhoodAnalysisData {
  postcode: string;
  coordinates: {
    latitude: number;
    longitude: number;
  } | null;

  // OS Places
  os_places?: {
    uprn?: string;
    formatted_address?: string;
  };

  // ONS Data
  social?: {
    geography: {
      lsoa_code?: string;
      local_authority?: string;
      region?: string;
    };
    wellbeing: {
      score: number | null; // 0-100
      rating: 'Excellent' | 'Good' | 'Average' | 'Poor' | null;
    };
    economic: {
      score: number | null;
      rating: string | null;
    };
    demographics: {
      over_65_percent: number | null;
      population_density: number | null;
    };
  };

  // OSM Data
  walkability?: {
    score: number; // 0-100
    rating: string;
    care_home_relevance: {
      score: number;
      rating: string;
    };
    amenities_count: number;
    public_transport_count: number;
  };

  osm?: {
    amenities: {
      by_category: {
        parks: Array<{
          name: string;
          coordinates: { lat: number; lng: number };
          distance_m: number;
        }>;
        shopping: Array<{
          name: string;
          coordinates: { lat: number; lng: number };
          distance_m: number;
        }>;
        healthcare: Array<{
          name: string;
          type: string;
          coordinates: { lat: number; lng: number };
          distance_m: number;
        }>;
      };
    };
    infrastructure: {
      public_transport: {
        bus_stops_800m: Array<{
          name: string;
          coordinates: { lat: number; lng: number };
          distance_m: number;
        }>;
        rail_stations_1600m: Array<{
          name: string;
          coordinates: { lat: number; lng: number };
          distance_m: number;
        }>;
      };
    };
  };

  // NHSBSA Data
  health?: {
    index: {
      score: number | null;
      rating: string | null;
    };
    practices_nearby: number;
    nearest_practices: Array<{
      name: string;
      coordinates: { lat: number; lng: number };
      distance_km: number;
    }>;
  };

  // Overall
  overall?: {
    score: number; // 0-100
    rating: string;
    breakdown: Array<{
      name: string;
      score: number;
      weight: string;
    }>;
  };

  summary: {
    status: 'available' | 'not_available' | 'partial';
    data_quality: 'high' | 'medium' | 'low';
    sources: string[];
  };
}

export class NeighbourhoodAnalysisEnrichmentService extends BaseEnrichmentService {
  serviceName = 'neighbourhood';
  private osPlacesClient: OSPlacesClient;
  private onsClient: ONSClient;
  private osmClient: OSMClient;
  private nhsbsaClient: NHSBSAClient;
  private cacheTTL: number = 30 * 24 * 60 * 60 * 1000; // 30 days

  constructor(options: EnrichmentOptions = {}) {
    super(options);

    // Neighbourhood analysis timeout (60 seconds - может быть долгим)
    const timeout = options.timeout || 60000;

    const osPlacesApiKey = process.env.OS_PLACES_API_KEY;
    this.osPlacesClient = new OSPlacesClient(osPlacesApiKey);
    this.onsClient = new ONSClient();
    this.osmClient = new OSMClient();
    this.nhsbsaClient = new NHSBSAClient();

    // Neighbourhood data cache TTL = 30 days (данные обновляются реже)
    if (options.cacheTTL) {
      this.cacheTTL = options.cacheTTL;
    }

    // Initialize logger after serviceName is set
    this.initLogger();
  }

  /**
   * Обогатить care home данными Neighbourhood Analysis
   */
  async enrich(
    home: CareHome,
    context?: EnrichmentContext
  ): Promise<EnrichmentResult> {
    const startTime = Date.now();

    try {
      this.validateHome(home);
      this.logStart(home, context);

      // Проверить доступность
      if (!this.isAvailable()) {
        this.logger.debug('Neighbourhood analysis disabled by feature flag');
        return this.createErrorResult('Neighbourhood analysis disabled by feature flag');
      }

      // Получить cache key
      const cacheKey = this.getCacheKey(home, 'neighbourhood');

      // Проверить кэш
      if (this.cache) {
        const cacheKeyFull = `enrichment:${this.serviceName}:${cacheKey}`;
        const cached = this.cache.get<NeighbourhoodAnalysisData>(cacheKeyFull);

        if (cached) {
          const processingTime = Date.now() - startTime;
          const result = this.createCachedResult(cached, processingTime);
          this.logComplete(result, home);
          return result;
        }
      }

      // Извлечь данные для анализа
      const postcode = home.postcode;
      const latitude = home.latitude;
      const longitude = home.longitude;

      if (!postcode && !(latitude && longitude)) {
        throw new Error('Postcode or coordinates are required for Neighbourhood Analysis');
      }

      // Получить координаты если нет
      let lat = latitude;
      let lon = longitude;

      if (!lat || !lon) {
        const coords = await this.osPlacesClient.getCoordinatesFromPostcode(
          postcode!
        );
        if (coords) {
          lat = coords.latitude;
          lon = coords.longitude;
        }
      }

      if (!lat || !lon) {
        throw new Error('Could not determine coordinates for Neighbourhood Analysis');
      }

      // Получить данные из всех источников (параллельно)
      const [osPlacesData, osmWalkability, osmAmenities, osmTransport, nhsbsaData] =
        await Promise.allSettled([
          postcode
            ? this.withRetry(
                () => this.osPlacesClient.getAddressByPostcode(postcode),
                { maxAttempts: 2 }
              )
            : Promise.resolve(null),
          this.withRetry(
            () => this.osmClient.calculateWalkability(lat!, lon!),
            { maxAttempts: 2 }
          ),
          this.withRetry(
            () => this.osmClient.getNearbyAmenities(lat!, lon!, 1600),
            { maxAttempts: 2 }
          ),
          this.withRetry(
            () => this.osmClient.getPublicTransport(lat!, lon!),
            { maxAttempts: 2 }
          ),
          this.withRetry(
            () => this.nhsbsaClient.getNearestGPPractices(lat!, lon!, 5),
            { maxAttempts: 2 }
          ),
        ]);

      const osPlaces =
        osPlacesData.status === 'fulfilled' ? osPlacesData.value : null;
      const walkability =
        osmWalkability.status === 'fulfilled' ? osmWalkability.value : null;
      const amenities =
        osmAmenities.status === 'fulfilled' ? osmAmenities.value : [];
      const transport =
        osmTransport.status === 'fulfilled' ? osmTransport.value : null;
      const nhsbsaPractices =
        nhsbsaData.status === 'fulfilled' ? nhsbsaData.value : [];

      // Формировать enrichment данные
      const enrichmentData = this.formatNeighbourhoodData(
        postcode || '',
        lat!,
        lon!,
        osPlaces,
        walkability,
        amenities,
        transport,
        nhsbsaPractices
      );

      // Сохранить в кэш
      if (this.cache) {
        const cacheKeyFull = `enrichment:${this.serviceName}:${cacheKey}`;
        this.cache.set(cacheKeyFull, enrichmentData, this.cacheTTL);
      }

      const processingTime = Date.now() - startTime;
      const sources = [
        ...(osPlaces ? ['os_places'] : []),
        ...(walkability ? ['osm'] : []),
        ...(nhsbsaPractices.length > 0 ? ['nhsbsa'] : []),
      ];

      const result = this.createSuccessResult(
        enrichmentData,
        {
          sources,
          dataQuality: enrichmentData.summary.data_quality,
        },
        processingTime
      );

      this.logComplete(result, home);
      return result;
    } catch (error: unknown) {
      const processingTime = Date.now() - startTime;
      const errorObj = error instanceof Error ? error : new Error(String(error));
      this.logError(errorObj, home);

      // Если это timeout или network error, возвращаем partial result
      const errorMessage = error instanceof Error ? error.message : String(error);
      const lowerErrorMessage = errorMessage.toLowerCase();
      if (
        lowerErrorMessage.includes('timeout') ||
        lowerErrorMessage.includes('network') ||
        lowerErrorMessage.includes('econn')
      ) {
        return this.createPartialResult(
          {},
          errorMessage,
          {
            sources: [],
            dataQuality: 'low',
          },
          processingTime
        );
      }

      return this.createErrorResult(errorObj, processingTime);
    }
  }

  /**
   * Форматировать neighbourhood данные
   */
  private formatNeighbourhoodData(
    postcode: string,
    latitude: number,
    longitude: number,
    osPlaces: any,
    walkability: any,
    amenities: any[],
    transport: any,
    nhsbsaPractices: any[]
  ): NeighbourhoodAnalysisData {
    // Группировать amenities по категориям
    const amenitiesByCategory = {
      parks: amenities.filter((a) => a.category === 'parks'),
      shopping: amenities.filter((a) => a.category === 'shopping'),
      healthcare: amenities.filter((a) => a.category === 'healthcare'),
    };

    // Рассчитать overall score
    const overallScore = this.calculateOverallScore(walkability, amenities.length);

    return {
      postcode,
      coordinates: { latitude, longitude },
      os_places: osPlaces
        ? {
            uprn: osPlaces.uprn,
            formatted_address: osPlaces.formatted_address,
          }
        : undefined,
      walkability: walkability
        ? {
            ...walkability,
            care_home_relevance: {
              score: this.calculateCareHomeRelevance(walkability),
              rating: this.scoreToRating(
                this.calculateCareHomeRelevance(walkability)
              ),
            },
          }
        : undefined,
      osm: {
        amenities: {
          by_category: {
            parks: amenitiesByCategory.parks.map((a) => ({
              name: a.name,
              coordinates: { lat: a.coordinates.latitude, lng: a.coordinates.longitude },
              distance_m: a.distance_m,
            })),
            shopping: amenitiesByCategory.shopping.map((a) => ({
              name: a.name,
              coordinates: { lat: a.coordinates.latitude, lng: a.coordinates.longitude },
              distance_m: a.distance_m,
            })),
            healthcare: amenitiesByCategory.healthcare.map((a) => ({
              name: a.name,
              type: a.type,
              coordinates: { lat: a.coordinates.latitude, lng: a.coordinates.longitude },
              distance_m: a.distance_m,
            })),
          },
        },
        infrastructure: {
          public_transport: {
            bus_stops_800m: transport?.bus_stops || [],
            rail_stations_1600m: transport?.rail_stations || [],
          },
        },
      },
      health: {
        index: {
          score: null, // Would come from NHSBSA health profile
          rating: null,
        },
        practices_nearby: nhsbsaPractices.length,
        nearest_practices: nhsbsaPractices.map((p) => ({
          name: p.practice_name,
          coordinates: {
            lat: p.coordinates?.latitude || 0,
            lng: p.coordinates?.longitude || 0,
          },
          distance_km: p.distance_km || 0,
        })),
      },
      overall: {
        score: overallScore,
        rating: this.scoreToRating(overallScore),
        breakdown: [
          {
            name: 'Walkability',
            score: walkability?.score || 0,
            weight: '30%',
          },
          {
            name: 'Amenities',
            score: Math.min(100, (amenities.length / 10) * 100),
            weight: '40%',
          },
          {
            name: 'Public Transport',
            score: Math.min(100, ((transport?.bus_stops.length || 0) + (transport?.rail_stations.length || 0)) * 20),
            weight: '30%',
          },
        ],
      },
      summary: {
        status: this.determineStatus(walkability, amenities.length, nhsbsaPractices.length),
        data_quality: this.determineDataQuality(walkability, amenities.length, nhsbsaPractices.length),
        sources: [
          ...(osPlaces ? ['os_places'] : []),
          ...(walkability ? ['osm'] : []),
          ...(nhsbsaPractices.length > 0 ? ['nhsbsa'] : []),
        ],
      },
    };
  }

  /**
   * Рассчитать overall score
   */
  private calculateOverallScore(walkability: any, amenitiesCount: number): number {
    let score = 0;
    
    if (walkability) {
      score += walkability.score * 0.3;
    }
    
    score += Math.min(100, (amenitiesCount / 10) * 100) * 0.4;
    
    return Math.round(score);
  }

  /**
   * Рассчитать care home relevance score
   */
  private calculateCareHomeRelevance(walkability: any): number {
    if (!walkability) return 0;
    
    // Care homes benefit from good walkability, amenities, and transport
    let score = walkability.score;
    
    // Bonus for high amenities count
    if (walkability.amenities_count >= 10) score += 10;
    else if (walkability.amenities_count >= 5) score += 5;
    
    // Bonus for public transport
    if (walkability.public_transport_count >= 5) score += 10;
    else if (walkability.public_transport_count >= 2) score += 5;
    
    return Math.min(100, score);
  }

  /**
   * Конвертировать score в rating
   */
  private scoreToRating(score: number): string {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Average';
    return 'Poor';
  }

  /**
   * Определить статус данных
   */
  private determineStatus(
    walkability: any,
    amenitiesCount: number,
    practicesCount: number
  ): 'available' | 'not_available' | 'partial' {
    if (!walkability && amenitiesCount === 0 && practicesCount === 0) {
      return 'not_available';
    }
    if (walkability && amenitiesCount > 0) {
      return 'available';
    }
    return 'partial';
  }

  /**
   * Определить качество данных
   */
  private determineDataQuality(
    walkability: any,
    amenitiesCount: number,
    practicesCount: number
  ): 'high' | 'medium' | 'low' {
    if (walkability && amenitiesCount >= 5 && practicesCount > 0) {
      return 'high';
    }
    if (walkability || amenitiesCount > 0) {
      return 'medium';
    }
    return 'low';
  }
}



