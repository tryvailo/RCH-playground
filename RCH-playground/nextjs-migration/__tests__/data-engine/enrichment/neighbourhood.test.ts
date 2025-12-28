/**
 * Neighbourhood Analysis Enrichment Service Tests
 */

import { NeighbourhoodAnalysisEnrichmentService } from '@/lib/data-engine/enrichment/services/neighbourhood';
import { OSPlacesClient } from '@/lib/data-engine/enrichment/services/os-places-client';
import { ONSClient } from '@/lib/data-engine/enrichment/services/ons-client';
import { OSMClient } from '@/lib/data-engine/enrichment/services/osm-client';
import { NHSBSAClient } from '@/lib/data-engine/enrichment/services/nhsbsa-client';
import { CareHome } from '@/lib/shared/types/care-home';

// Mock clients
jest.mock('@/lib/data-engine/enrichment/services/os-places-client');
jest.mock('@/lib/data-engine/enrichment/services/ons-client');
jest.mock('@/lib/data-engine/enrichment/services/osm-client');
jest.mock('@/lib/data-engine/enrichment/services/nhsbsa-client');

describe('NeighbourhoodAnalysisEnrichmentService', () => {
  let service: NeighbourhoodAnalysisEnrichmentService;
  let mockOSPlacesClient: jest.Mocked<OSPlacesClient>;
  let mockOSMClient: jest.Mocked<OSMClient>;
  let mockNHSBSAClient: jest.Mocked<NHSBSAClient>;

  const mockHome: CareHome = {
    id: 'test-1',
    name: 'Test Care Home',
    postcode: 'SW1A 1AA',
    latitude: 51.5074,
    longitude: -0.1278,
  };

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();

    // Create mock clients with default implementations
    mockOSPlacesClient = {
      getAddressByPostcode: jest.fn().mockResolvedValue({
        address: '123 Test St',
        postcode: 'SW1A 1AA',
      }),
      createAddressFromCoordinates: jest.fn().mockResolvedValue({
        address: '123 Test St',
        postcode: 'SW1A 1AA',
      }),
      getCoordinatesFromPostcode: jest.fn().mockResolvedValue({
        latitude: 51.5074,
        longitude: -0.1278,
      }),
    } as any;

    mockOSMClient = {
      getNearbyAmenities: jest.fn().mockResolvedValue([]),
      calculateWalkability: jest.fn().mockResolvedValue({
        score: 75,
        rating: 'Good',
        amenities_count: 10,
        public_transport_count: 5,
      }),
      getPublicTransport: jest.fn().mockResolvedValue({
        bus_stops: [],
        rail_stations: [],
      }),
    } as any;

    mockNHSBSAClient = {
      getNearestGPPractices: jest.fn().mockResolvedValue([]),
      getHealthProfile: jest.fn().mockResolvedValue(null),
    } as any;

    // Mock constructors
    (OSPlacesClient as jest.MockedClass<typeof OSPlacesClient>).mockImplementation(
      () => mockOSPlacesClient
    );
    (OSMClient as jest.MockedClass<typeof OSMClient>).mockImplementation(
      () => mockOSMClient
    );
    (NHSBSAClient as jest.MockedClass<typeof NHSBSAClient>).mockImplementation(
      () => mockNHSBSAClient
    );

    service = new NeighbourhoodAnalysisEnrichmentService({
      useCache: false, // Disable cache for tests
      timeout: 60000,
    });
  });

  describe('enrich', () => {
    it('should successfully enrich home with neighbourhood data', async () => {
      const mockWalkability = {
        score: 75,
        rating: 'Good',
        amenities_count: 10,
        public_transport_count: 5,
      };

      const mockAmenities = [
        {
          name: 'Park',
          type: 'park',
          category: 'parks',
          coordinates: { latitude: 51.508, longitude: -0.128 },
          distance_m: 200,
        },
        {
          name: 'Shop',
          type: 'shop',
          category: 'shopping',
          coordinates: { latitude: 51.507, longitude: -0.127 },
          distance_m: 150,
        },
      ];

      const mockTransport = {
        bus_stops: [
          {
            name: 'Bus Stop',
            coordinates: { lat: 51.5075, lng: -0.1275 },
            distance_m: 100,
          },
        ],
        rail_stations: [],
      };

      mockOSPlacesClient.getAddressByPostcode.mockResolvedValue({
        formatted_address: 'Test Address',
        postcode: 'SW1A 1AA',
      } as any);

      mockOSMClient.calculateWalkability.mockResolvedValue(mockWalkability);
      mockOSMClient.getNearbyAmenities.mockResolvedValue(mockAmenities);
      mockOSMClient.getPublicTransport.mockResolvedValue(mockTransport);
      mockNHSBSAClient.getNearestGPPractices.mockResolvedValue([]);

      const result = await service.enrich(mockHome);

      expect(result.status).toBe('success');
      expect(result.source).toBe('neighbourhood');
      expect(result.data.walkability?.score).toBe(75);
      expect(result.data.osm?.amenities.by_category.parks.length).toBe(1);
      expect(mockOSMClient.calculateWalkability).toHaveBeenCalled();
    });

    it('should handle missing postcode by using coordinates', async () => {
      const homeWithoutPostcode = {
        ...mockHome,
        postcode: undefined,
      };

      const mockWalkability = {
        score: 70,
        rating: 'Good',
        amenities_count: 8,
        public_transport_count: 3,
      };

      mockOSMClient.calculateWalkability.mockResolvedValue(mockWalkability);
      mockOSMClient.getNearbyAmenities.mockResolvedValue([]);
      mockOSMClient.getPublicTransport.mockResolvedValue({ bus_stops: [], rail_stations: [] });
      mockNHSBSAClient.getNearestGPPractices.mockResolvedValue([]);

      const result = await service.enrich(homeWithoutPostcode);

      expect(result.status).toBe('success');
      expect(result.data.coordinates).toEqual({
        latitude: 51.5074,
        longitude: -0.1278,
      });
    });

    it('should handle API errors gracefully', async () => {
      mockOSPlacesClient.getAddressByPostcode.mockRejectedValue(
        new Error('Network timeout')
      );
      mockOSMClient.calculateWalkability.mockRejectedValue(
        new Error('Network timeout')
      );
      mockOSMClient.getNearbyAmenities.mockRejectedValue(
        new Error('Network timeout')
      );
      mockOSMClient.getPublicTransport.mockRejectedValue(
        new Error('Network timeout')
      );
      mockNHSBSAClient.getNearestGPPractices.mockRejectedValue(
        new Error('Network timeout')
      );

      const result = await service.enrich(mockHome);

      // When API calls fail, should still return result with coordinates
      expect(result.status).toMatch(/success|partial/);
    });

    it('should calculate overall score correctly', async () => {
      const mockWalkability = {
        score: 80,
        rating: 'Excellent',
        amenities_count: 15,
        public_transport_count: 8,
      };

      mockOSMClient.calculateWalkability.mockResolvedValue(mockWalkability);
      mockOSMClient.getNearbyAmenities.mockResolvedValue(
        Array(15).fill(null).map((_, i) => ({
          name: `Amenity ${i}`,
          category: 'shopping',
          coordinates: { latitude: 51.507, longitude: -0.127 },
          distance_m: 100 + i * 10,
        }))
      );
      mockOSMClient.getPublicTransport.mockResolvedValue({
        bus_stops: Array(5).fill(null).map(() => ({
          name: 'Bus Stop',
          coordinates: { lat: 51.507, lng: -0.127 },
          distance_m: 200,
        })),
        rail_stations: [],
      });
      mockNHSBSAClient.getNearestGPPractices.mockResolvedValue([]);

      const result = await service.enrich(mockHome);

      expect(result.status).toBe('success');
      expect(result.data.overall?.score).toBeGreaterThan(0);
      expect(result.data.overall?.rating).toBeDefined();
    });
  });

  describe('isAvailable', () => {
    it('should check feature flags', () => {
      const available = service.isAvailable();
      expect(typeof available).toBe('boolean');
    });
  });
});



