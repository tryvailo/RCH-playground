/**
 * Google Places Enrichment Service Tests
 */

import { GooglePlacesEnrichmentService } from '@/lib/data-engine/enrichment/services/google-places';
import { GooglePlacesClient } from '@/lib/data-engine/enrichment/services/google-places-client';
import { CareHome } from '@/lib/shared/types/care-home';

// Mock GooglePlacesClient
jest.mock('@/lib/data-engine/enrichment/services/google-places-client');

describe('GooglePlacesEnrichmentService', () => {
  let service: GooglePlacesEnrichmentService;
  let mockGooglePlacesClient: jest.Mocked<GooglePlacesClient>;

  const mockHome: CareHome = {
    id: 'test-1',
    name: 'Test Care Home',
    postcode: 'SW1A 1AA',
    latitude: 51.5074,
    longitude: -0.1278,
    cqc_location_id: '1-1234567890',
  };

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();

    // Create mock client with default implementations
    mockGooglePlacesClient = {
      findPlace: jest.fn().mockResolvedValue({
        place_id: 'ChIJ...',
        name: 'Test Care Home',
        formatted_address: '123 Test St, London',
        rating: 4.5,
        user_rating_total: 127,
        photos: [],
      }),
      getPlaceDetails: jest.fn().mockResolvedValue({
        place_id: 'ChIJ...',
        name: 'Test Care Home',
        rating: 4.5,
        user_rating_total: 127,
        reviews: [],
      }),
      getPhotoUrl: jest.fn().mockReturnValue('https://maps.googleapis.com/...'),
      getPopularTimes: jest.fn().mockResolvedValue(null),
      getPlaceInsights: jest.fn().mockResolvedValue(null),
    } as any;

    // Mock GooglePlacesClient constructor
    (GooglePlacesClient as jest.MockedClass<typeof GooglePlacesClient>).mockImplementation(
      () => mockGooglePlacesClient
    );

    service = new GooglePlacesEnrichmentService({
      useCache: false, // Disable cache for tests
      timeout: 10000,
    });
  });

  describe('enrich', () => {
    it('should successfully enrich home with Google Places data', async () => {
      const mockPlace = {
        place_id: 'ChIJ...',
        name: 'Test Care Home',
        formatted_address: '123 Test St, London',
        geometry: {
          location: {
            lat: 51.5074,
            lng: -0.1278,
          },
        },
        rating: 4.5,
        user_rating_total: 127,
        photos: [
          {
            photo_reference: 'photo_ref_1',
            width: 1920,
            height: 1080,
          },
        ],
      };

      const mockDetails = {
        ...mockPlace,
        reviews: [
          {
            author_name: 'John D.',
            rating: 5,
            text: 'Excellent care...',
            time: 1704067200, // Unix timestamp
          },
        ],
      };

      mockGooglePlacesClient.findPlace.mockResolvedValue(mockPlace as any);
      mockGooglePlacesClient.getPlaceDetails.mockResolvedValue(mockDetails as any);
      mockGooglePlacesClient.getPhotoUrl.mockReturnValue('https://maps.googleapis.com/...');
      mockGooglePlacesClient.getPopularTimes.mockResolvedValue(null);
      mockGooglePlacesClient.getPlaceInsights.mockResolvedValue(null);

      const result = await service.enrich(mockHome);

      expect(result.status).toBe('success');
      expect(result.source).toBe('googlePlaces');
      expect(result.data.place_id).toBe('ChIJ...');
      expect(result.data.rating).toBe(4.5);
      expect(result.data.reviews_count).toBe(127);
      expect(result.data.photos.length).toBeGreaterThan(0);
      expect(mockGooglePlacesClient.findPlace).toHaveBeenCalled();
    });

    it('should return partial result when place not found', async () => {
      mockGooglePlacesClient.findPlace.mockResolvedValue(null);

      const result = await service.enrich(mockHome);

      expect(result.status).toBe('partial');
      expect(result.error).toContain('Place not found');
      expect(result.data.place_id).toBeNull();
    });

    it('should handle API errors gracefully', async () => {
      mockGooglePlacesClient.findPlace.mockRejectedValue(
        new Error('API key invalid')
      );

      const result = await service.enrich(mockHome);

      expect(result.status).toBe('partial');
      expect(result.error).toContain('API key');
    });

    it('should handle timeout errors', async () => {
      mockGooglePlacesClient.findPlace.mockRejectedValue(
        new Error('Google Places API request timeout after 10000ms')
      );

      const result = await service.enrich(mockHome);

      expect(result.status).toBe('partial');
      expect(result.error).toContain('timeout');
    });

    it('should include insights if available', async () => {
      const mockPlace = {
        place_id: 'ChIJ...',
        name: 'Test Care Home',
        formatted_address: '123 Test St, London',
        rating: 4.5,
        user_rating_total: 127,
        photos: [],
      };

      const mockInsights = {
        place_id: 'ChIJ...',
        dwell_time: 45,
        repeat_visitors: 0.65,
        footfall_trends: 'increasing' as const,
      };

      mockGooglePlacesClient.findPlace.mockResolvedValue(mockPlace as any);
      mockGooglePlacesClient.getPlaceDetails.mockResolvedValue(mockPlace as any);
      mockGooglePlacesClient.getPhotoUrl.mockReturnValue('https://...');
      mockGooglePlacesClient.getPopularTimes.mockResolvedValue(null);
      mockGooglePlacesClient.getPlaceInsights.mockResolvedValue(mockInsights);

      const result = await service.enrich(mockHome);

      expect(result.status).toBe('success');
      expect(result.data.insights).toBeDefined();
      expect(result.data.insights?.dwell_time).toBe(45);
      expect(result.data.insights?.repeat_visitors).toBe(0.65);
    });

    it('should format reviews correctly', async () => {
      const mockPlace = {
        place_id: 'ChIJ...',
        name: 'Test Care Home',
        rating: 4.5,
        user_rating_total: 2,
      };

      const mockDetails = {
        ...mockPlace,
        reviews: [
          {
            author_name: 'John D.',
            rating: 5,
            text: 'Excellent care',
            time: 1704067200,
          },
          {
            author_name: 'Jane S.',
            rating: 4,
            text: 'Very good',
            time: 1703980800,
          },
        ],
      };

      mockGooglePlacesClient.findPlace.mockResolvedValue(mockPlace as any);
      mockGooglePlacesClient.getPlaceDetails.mockResolvedValue(mockDetails as any);
      mockGooglePlacesClient.getPhotoUrl.mockReturnValue('https://...');
      mockGooglePlacesClient.getPopularTimes.mockResolvedValue(null);
      mockGooglePlacesClient.getPlaceInsights.mockResolvedValue(null);

      const result = await service.enrich(mockHome);

      expect(result.status).toBe('success');
      expect(result.data.reviews.length).toBe(2);
      expect(result.data.reviews[0].author).toBe('John D.');
      expect(result.data.reviews[0].rating).toBe(5);
    });
  });

  describe('isAvailable', () => {
    it('should check feature flags', () => {
      const available = service.isAvailable();
      expect(typeof available).toBe('boolean');
    });
  });
});



