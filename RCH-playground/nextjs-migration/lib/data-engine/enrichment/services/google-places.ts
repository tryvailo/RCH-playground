/**
 * Google Places Enrichment Service
 * Enriches care homes with Google Places data (reviews, photos, popular times, insights)
 * 
 * Uses Google Places API to get reviews, photos, and optional Places Insights API
 * for advanced metrics like dwell time and repeat visitors
 */

import { CareHome } from '@/lib/shared/types/care-home';
import { BaseEnrichmentService } from '../base-enrichment';
import {
  EnrichmentResult,
  EnrichmentContext,
  EnrichmentOptions,
} from '../types';
import {
  GooglePlacesClient,
  GooglePlaceDetails,
  GooglePlacesEnrichmentData,
  PopularTimes,
  PlaceInsights,
} from './google-places-client';

export class GooglePlacesEnrichmentService extends BaseEnrichmentService {
  serviceName = 'googlePlaces';
  private googlePlacesClient: GooglePlacesClient;
  private cacheTTL: number = 24 * 60 * 60 * 1000; // 24 hours

  constructor(options: EnrichmentOptions = {}) {
    super(options);

    // Google Places API timeout (10 seconds)
    const timeout = options.timeout || 10000;
    const apiKey = process.env.GOOGLE_PLACES_API_KEY;
    const useInsights = process.env.GOOGLE_PLACES_INSIGHTS_ENABLED === 'true';
    this.googlePlacesClient = new GooglePlacesClient(apiKey, timeout, useInsights);

    // Google Places cache TTL = 24 hours (данные обновляются чаще)
    if (options.cacheTTL) {
      this.cacheTTL = options.cacheTTL;
    }

    // Initialize logger after serviceName is set
    this.initLogger();
  }

  /**
   * Обогатить care home данными Google Places
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
        this.logger.debug('Google Places enrichment disabled by feature flag');
        return this.createErrorResult('Google Places enrichment disabled by feature flag');
      }

      // Получить cache key
      const cacheKey = this.getCacheKey(home, 'google-places');

      // Проверить кэш
      if (this.cache) {
        const cacheKeyFull = `enrichment:${this.serviceName}:${cacheKey}`;
        const cached = this.cache.get<GooglePlacesEnrichmentData>(cacheKeyFull);

        if (cached) {
          const processingTime = Date.now() - startTime;
          const result = this.createCachedResult(cached, processingTime);
          this.logComplete(result, home);
          return result;
        }
      }

      // Извлечь данные для поиска
      const homeName = home.name;
      const address = home.address || `${homeName}, ${home.postcode}`;
      const latitude = home.latitude;
      const longitude = home.longitude;

      if (!homeName) {
        throw new Error('Home name is required for Google Places enrichment');
      }

      // Поиск места в Google Places (с retry)
      const place = await this.withRetry(
        () =>
          this.googlePlacesClient.findPlace(
            `${homeName} ${home.postcode}`,
            latitude && longitude ? { lat: latitude, lng: longitude } : undefined
          ),
        {
          maxAttempts: 3,
          initialDelay: 1000,
        }
      );

      if (!place || !place.place_id) {
        // Место не найдено - это не ошибка, просто нет данных
        const processingTime = Date.now() - startTime;
        const result = this.createPartialResult(
          {
            place_id: null,
            rating: null,
            reviews_count: 0,
            photos: [],
            popular_times: null,
            insights: null,
            reviews: [],
            summary: {
              status: 'not_available',
              data_quality: 'low',
            },
          },
          'Place not found in Google Places',
          {
            sources: [],
            dataQuality: 'low',
          },
          processingTime
        );
        this.logComplete(result, home);
        return result;
      }

      // Получить детали места (параллельно с insights если включено)
      const [placeDetails, insights] = await Promise.allSettled([
        this.withRetry(
          () => this.googlePlacesClient.getPlaceDetails(place.place_id),
          { maxAttempts: 2 }
        ),
        this.googlePlacesClient.getPlaceInsights(place.place_id).catch(() => null),
      ]);

      const details =
        placeDetails.status === 'fulfilled' ? placeDetails.value : null;
      const placeInsights =
        insights.status === 'fulfilled' ? insights.value : null;

      // Получить popular times (если доступно)
      const popularTimes = await this.googlePlacesClient
        .getPopularTimes(place.place_id)
        .catch(() => null);

      // Формирование enrichment данных
      const enrichmentData = this.formatEnrichmentData(
        place,
        details,
        popularTimes,
        placeInsights
      );

      // Сохранить в кэш
      if (this.cache) {
        const cacheKeyFull = `enrichment:${this.serviceName}:${cacheKey}`;
        this.cache.set(cacheKeyFull, enrichmentData, this.cacheTTL);
      }

      const processingTime = Date.now() - startTime;
      const result = this.createSuccessResult(
        enrichmentData,
        {
          sources: ['google_places_api', ...(placeInsights ? ['google_places_insights'] : [])],
          dataQuality: this.determineDataQuality(enrichmentData),
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
        lowerErrorMessage.includes('econn') ||
        lowerErrorMessage.includes('api key')
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
   * Форматировать enrichment данные
   */
  private formatEnrichmentData(
    place: any,
    details: GooglePlaceDetails | null,
    popularTimes: PopularTimes | null,
    insights: PlaceInsights | null
  ): GooglePlacesEnrichmentData {
    // Использовать details если доступно, иначе place
    const source = details || place;

    // Формировать фото URLs
    const photos =
      source.photos?.slice(0, 10).map((photo: any) => ({
        url: this.googlePlacesClient.getPhotoUrl(photo.photo_reference),
        width: photo.width || 1920,
        height: photo.height || 1080,
      })) || [];

    // Формировать reviews
    const reviews =
      source.reviews?.map((review: any) => ({
        author: review.author_name,
        rating: review.rating,
        text: review.text,
        date: new Date(review.time * 1000).toISOString(),
      })) || [];

    // Определить статус
    let status: GooglePlacesEnrichmentData['summary']['status'] = 'available';
    if (!source.rating && !source.reviews && photos.length === 0) {
      status = 'not_available';
    } else if (!source.rating || !source.reviews) {
      status = 'partial';
    }

    return {
      place_id: source.place_id || null,
      rating: source.rating || null,
      reviews_count: source.user_rating_total || reviews.length || 0,
      photos,
      popular_times: popularTimes,
      insights: insights || null,
      reviews,
      summary: {
        status,
        data_quality: this.determineDataQuality({
          rating: source.rating,
          reviews_count: source.user_rating_total || reviews.length,
          photos: photos.length,
          insights: insights ? 1 : 0,
        } as any),
      },
    };
  }

  /**
   * Определить качество данных
   */
  private determineDataQuality(data: GooglePlacesEnrichmentData | any): 'high' | 'medium' | 'low' {
    if (!data) {
      return 'low';
    }

    const hasRating = data.rating !== null && data.rating !== undefined;
    const hasReviews = (data.reviews_count || 0) > 0;
    const hasPhotos = (data.photos?.length || 0) > 0;
    const hasInsights = data.insights !== null;

    if (hasRating && hasReviews && hasPhotos && hasInsights) {
      return 'high';
    } else if (hasRating && (hasReviews || hasPhotos)) {
      return 'medium';
    } else {
      return 'low';
    }
  }
}



