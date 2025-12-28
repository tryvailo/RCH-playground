/**
 * FSA API Client
 * Client for Food Standards Agency (FSA) Food Hygiene Rating Scheme API
 * 
 * API Documentation: https://api.ratings.food.gov.uk/
 */

export interface FSABusiness {
  BusinessName: string;
  BusinessType: string;
  BusinessTypeID: string;
  AddressLine1: string;
  AddressLine2?: string;
  AddressLine3?: string;
  AddressLine4?: string;
  PostCode: string;
  RatingValue: string; // "5", "4", "3", "2", "1", "0", "Exempt", "AwaitingInspection"
  RatingKey: string;
  RatingDate: string;
  LocalAuthorityCode: string;
  LocalAuthorityName: string;
  LocalAuthorityWebSite?: string;
  LocalAuthorityEmailAddress?: string;
  HygieneScore?: string;
  StructuralScore?: string;
  ConfidenceInManagementScore?: string;
  SchemeType: string;
  geocode?: {
    longitude: string;
    latitude: string;
  };
  RightToReply?: string;
  Distance?: string;
  NewRatingPending?: string;
}

export interface FSASearchResponse {
  establishments: FSABusiness[];
  meta: {
    dataSource: string;
    extractDate: string;
    itemCount: number;
    pageNumber: number;
    pageSize: number;
    returncode: string;
    totalCount: number;
    totalPages: number;
  };
  links: Array<{
    rel: string;
    href: string;
  }>;
}

export interface FSADetailedData {
  fsa_rating: number | null; // 0-5, null if exempt/awaiting
  fsa_rating_key: string;
  fsa_rating_date: string | null;
  fsa_health_score: number; // 0 = no issues, higher = more issues
  hygiene_score: number | null;
  structural_score: number | null;
  management_score: number | null;
  local_authority: string;
  inspection_details: {
    last_inspection: string | null;
    next_inspection: string | null;
  };
  sub_scores: {
    hygiene: number | null;
    structural: number | null;
    management: number | null;
  };
  summary: {
    status: 'available' | 'not_available' | 'exempt' | 'awaiting';
    rating: string;
    rating_label: string;
  };
}

/**
 * FSA API Client
 */
export class FSAClient {
  private baseUrl = 'https://api.ratings.food.gov.uk';
  private apiVersion = '2';
  private timeout: number;

  constructor(timeout: number = 10000) {
    this.timeout = timeout;
  }

  /**
   * Поиск бизнеса по названию и адресу
   */
  async searchBusiness(
    name: string,
    postcode: string,
    latitude?: number,
    longitude?: number
  ): Promise<FSABusiness | null> {
    try {
      // Сначала попробуем поиск по названию и почтовому индексу
      let url = `${this.baseUrl}/Establishments?name=${encodeURIComponent(name)}&postcode=${encodeURIComponent(postcode)}&pageSize=10&pageNumber=1`;

      // Если есть координаты, используем их для более точного поиска
      if (latitude && longitude) {
        url += `&longitude=${longitude}&latitude=${latitude}&maxDistanceLimit=5`;
      }

      const response = await this.fetchWithTimeout(url);

      if (!response.ok) {
        throw new Error(`FSA API error: ${response.status} ${response.statusText}`);
      }

      const data: FSASearchResponse = await response.json();

      if (!data.establishments || data.establishments.length === 0) {
        return null;
      }

      // Найти наиболее подходящий результат
      const bestMatch = this.findBestMatch(
        data.establishments,
        name,
        postcode,
        latitude,
        longitude
      );

      return bestMatch;
    } catch (error) {
      throw new Error(`FSA search failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Получить детальные данные FSA для бизнеса
   */
  async getDetailedData(business: FSABusiness): Promise<FSADetailedData> {
    const ratingValue = business.RatingValue;
    const ratingKey = business.RatingKey;
    const ratingDate = business.RatingDate;

    // Преобразовать rating в число
    let fsaRating: number | null = null;
    let ratingLabel = 'Unknown';

    if (ratingValue === '5') {
      fsaRating = 5;
      ratingLabel = 'Excellent';
    } else if (ratingValue === '4') {
      fsaRating = 4;
      ratingLabel = 'Very Good';
    } else if (ratingValue === '3') {
      fsaRating = 3;
      ratingLabel = 'Good';
    } else if (ratingValue === '2') {
      fsaRating = 2;
      ratingLabel = 'Fair';
    } else if (ratingValue === '1') {
      fsaRating = 1;
      ratingLabel = 'Poor';
    } else if (ratingValue === '0') {
      fsaRating = 0;
      ratingLabel = 'Urgent Improvement Required';
    } else if (ratingValue === 'Exempt') {
      ratingLabel = 'Exempt';
    } else if (ratingValue === 'AwaitingInspection') {
      ratingLabel = 'Awaiting Inspection';
    }

    // Преобразовать scores (это penalty scores, меньше = лучше)
    const hygieneScore = business.HygieneScore
      ? parseInt(business.HygieneScore, 10)
      : null;
    const structuralScore = business.StructuralScore
      ? parseInt(business.StructuralScore, 10)
      : null;
    const managementScore = business.ConfidenceInManagementScore
      ? parseInt(business.ConfidenceInManagementScore, 10)
      : null;

    // Health score = сумма всех penalty scores (0 = no issues)
    const healthScore =
      (hygieneScore ?? 0) + (structuralScore ?? 0) + (managementScore ?? 0);

    // Определить статус
    let status: FSADetailedData['summary']['status'] = 'available';
    if (ratingValue === 'Exempt') {
      status = 'exempt';
    } else if (ratingValue === 'AwaitingInspection') {
      status = 'awaiting';
    } else if (!fsaRating && !ratingValue) {
      status = 'not_available';
    }

    return {
      fsa_rating: fsaRating,
      fsa_rating_key: ratingKey,
      fsa_rating_date: ratingDate || null,
      fsa_health_score: healthScore,
      hygiene_score: hygieneScore,
      structural_score: structuralScore,
      management_score: managementScore,
      local_authority: business.LocalAuthorityName,
      inspection_details: {
        last_inspection: ratingDate || null,
        next_inspection: null, // FSA API не предоставляет эту информацию
      },
      sub_scores: {
        hygiene: hygieneScore,
        structural: structuralScore,
        management: managementScore,
      },
      summary: {
        status,
        rating: ratingValue || 'N/A',
        rating_label: ratingLabel,
      },
    };
  }

  /**
   * Найти наиболее подходящий результат из списка
   */
  private findBestMatch(
    establishments: FSABusiness[],
    name: string,
    postcode: string,
    latitude?: number,
    longitude?: number
  ): FSABusiness {
    // Простая логика: найти по точному совпадению названия
    const normalizedName = name.toLowerCase().trim();

    // Сначала попробуем точное совпадение
    let match = establishments.find(
      (e) => e.BusinessName.toLowerCase().trim() === normalizedName
    );

    if (match) {
      return match;
    }

    // Затем попробуем частичное совпадение
    match = establishments.find((e) =>
      e.BusinessName.toLowerCase().includes(normalizedName) ||
      normalizedName.includes(e.BusinessName.toLowerCase())
    );

    if (match) {
      return match;
    }

    // Если есть координаты, выберем ближайший
    if (latitude && longitude) {
      let closest: FSABusiness | null = null;
      let minDistance = Infinity;

      for (const est of establishments) {
        if (est.geocode?.latitude && est.geocode?.longitude) {
          const estLat = parseFloat(est.geocode.latitude);
          const estLon = parseFloat(est.geocode.longitude);
          const distance = this.calculateDistance(
            latitude,
            longitude,
            estLat,
            estLon
          );

          if (distance < minDistance) {
            minDistance = distance;
            closest = est;
          }
        }
      }

      if (closest) {
        return closest;
      }
    }

    // В крайнем случае вернем первый результат
    return establishments[0];
  }

  /**
   * Вычислить расстояние между двумя точками (Haversine)
   */
  private calculateDistance(
    lat1: number,
    lon1: number,
    lat2: number,
    lon2: number
  ): number {
    const R = 6371; // Радиус Земли в км
    const dLat = this.toRad(lat2 - lat1);
    const dLon = this.toRad(lon2 - lon1);

    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(this.toRad(lat1)) *
        Math.cos(this.toRad(lat2)) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  private toRad(degrees: number): number {
    return (degrees * Math.PI) / 180;
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
          'x-api-version': this.apiVersion,
          'Accept': 'application/json',
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error(`FSA API request timeout after ${this.timeout}ms`);
      }
      throw error;
    }
  }
}



