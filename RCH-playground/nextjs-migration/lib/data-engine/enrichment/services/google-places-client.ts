/**
 * Google Places API Client
 * Client for Google Places API and Places Insights API
 * 
 * API Documentation: 
 * - Places API: https://developers.google.com/maps/documentation/places/web-service
 * - Places Insights API: https://developers.google.com/maps/documentation/places/web-service/place-insights
 */

export interface GooglePlace {
  place_id: string;
  name: string;
  formatted_address: string;
  geometry: {
    location: {
      lat: number;
      lng: number;
    };
  };
  rating?: number;
  user_rating_total?: number;
  photos?: Array<{
    photo_reference: string;
    width: number;
    height: number;
  }>;
  types?: string[];
  opening_hours?: {
    open_now?: boolean;
    weekday_text?: string[];
  };
  reviews?: Array<{
    author_name: string;
    author_url?: string;
    language: string;
    profile_photo_url?: string;
    rating: number;
    relative_time_description: string;
    text: string;
    time: number;
  }>;
}

export interface GooglePlaceDetails extends GooglePlace {
  international_phone_number?: string;
  website?: string;
  price_level?: number;
  editorial_summary?: {
    overview: string;
  };
  current_opening_hours?: {
    open_now: boolean;
    periods: Array<{
      open: {
        day: number;
        time: string;
      };
      close?: {
        day: number;
        time: string;
      };
    }>;
    weekday_text: string[];
  };
}

export interface PopularTimes {
  [day: string]: Array<{
    hour: number;
    popularity: number; // 0-100
  }>;
}

export interface PlaceInsights {
  place_id: string;
  dwell_time?: number; // minutes
  repeat_visitors?: number; // 0-1 ratio
  footfall_trends?: 'increasing' | 'stable' | 'decreasing';
  visit_duration_distribution?: {
    short: number; // <15 min
    medium: number; // 15-60 min
    long: number; // >60 min
  };
}

export interface GooglePlacesEnrichmentData {
  place_id: string | null;
  rating: number | null;
  reviews_count: number;
  photos: Array<{
    url: string;
    width: number;
    height: number;
  }>;
  popular_times: PopularTimes | null;
  insights: PlaceInsights | null;
  reviews: Array<{
    author: string;
    rating: number;
    text: string;
    date: string;
  }>;
  summary: {
    status: 'available' | 'not_available' | 'partial';
    data_quality: 'high' | 'medium' | 'low';
  };
}

/**
 * Google Places API Client
 */
export class GooglePlacesClient {
  private apiKey: string;
  private baseUrl = 'https://maps.googleapis.com/maps/api/place';
  private timeout: number;
  private useInsights: boolean;

  constructor(apiKey?: string, timeout: number = 10000, useInsights: boolean = false) {
    this.apiKey = apiKey || process.env.GOOGLE_PLACES_API_KEY || '';
    this.timeout = timeout;
    this.useInsights = useInsights;

    if (!this.apiKey) {
      console.warn('Google Places API key not provided. Some features may not work.');
    }
  }

  /**
   * Найти место по текстовому запросу
   */
  async findPlace(
    query: string,
    location?: { lat: number; lng: number }
  ): Promise<GooglePlace | null> {
    try {
      let url = `${this.baseUrl}/findplacefromtext/json?input=${encodeURIComponent(query)}&inputtype=textquery&fields=place_id,name,formatted_address,geometry,rating,user_rating_total,photos&key=${this.apiKey}`;

      if (location) {
        url += `&locationbias=point:${location.lat},${location.lng}`;
      }

      const response = await this.fetchWithTimeout(url);

      if (!response.ok) {
        throw new Error(`Google Places API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      if (data.status !== 'OK' || !data.candidates || data.candidates.length === 0) {
        return null;
      }

      return data.candidates[0] as GooglePlace;
    } catch (error) {
      throw new Error(
        `Failed to find place: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  /**
   * Получить детали места по place_id
   */
  async getPlaceDetails(placeId: string): Promise<GooglePlaceDetails | null> {
    try {
      const fields = [
        'place_id',
        'name',
        'formatted_address',
        'geometry',
        'rating',
        'user_rating_total',
        'photos',
        'reviews',
        'opening_hours',
        'international_phone_number',
        'website',
        'price_level',
        'editorial_summary',
        'current_opening_hours',
      ].join(',');

      const url = `${this.baseUrl}/details/json?place_id=${placeId}&fields=${fields}&key=${this.apiKey}`;

      const response = await this.fetchWithTimeout(url);

      if (!response.ok) {
        throw new Error(`Google Places API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      if (data.status !== 'OK' || !data.result) {
        return null;
      }

      return data.result as GooglePlaceDetails;
    } catch (error) {
      throw new Error(
        `Failed to get place details: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  /**
   * Получить фото по photo_reference
   */
  getPhotoUrl(photoReference: string, maxWidth: number = 1920): string {
    return `${this.baseUrl}/photo?maxwidth=${maxWidth}&photoreference=${photoReference}&key=${this.apiKey}`;
  }

  /**
   * Получить популярные часы (если доступно)
   * Note: Popular times не доступны через официальный API, но могут быть получены через scraping
   */
  async getPopularTimes(placeId: string): Promise<PopularTimes | null> {
    // Popular times не доступны через официальный Google Places API
    // Это требует scraping или использования сторонних сервисов
    // Для MVP возвращаем null
    return null;
  }

  /**
   * Получить insights (требует Places Insights API - платный)
   */
  async getPlaceInsights(placeId: string): Promise<PlaceInsights | null> {
    if (!this.useInsights) {
      return null;
    }

    try {
      // Places Insights API endpoint (примерный)
      // Note: Точный endpoint может отличаться, нужно проверить документацию
      const url = `https://places.googleapis.com/v1/places/${placeId}/insights?key=${this.apiKey}`;

      const response = await this.fetchWithTimeout(url);

      if (!response.ok) {
        // Insights API может быть недоступен или требует специальной подписки
        return null;
      }

      const data = await response.json();

      return {
        place_id: placeId,
        dwell_time: data.dwell_time,
        repeat_visitors: data.repeat_visitors,
        footfall_trends: data.footfall_trends,
        visit_duration_distribution: data.visit_duration_distribution,
      };
    } catch (error) {
      // Insights API может быть недоступен
      return null;
    }
  }

  /**
   * Fetch с timeout
   */
  private async fetchWithTimeout(
    url: string,
    options: RequestInit = {}
  ): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error(`Google Places API request timeout after ${this.timeout}ms`);
      }
      throw error;
    }
  }
}



