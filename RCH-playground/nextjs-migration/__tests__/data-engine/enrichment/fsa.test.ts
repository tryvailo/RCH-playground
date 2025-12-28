/**
 * FSA Enrichment Service Tests
 */

import { FSAEnrichmentService } from '@/lib/data-engine/enrichment/services/fsa';
import { FSAClient } from '@/lib/data-engine/enrichment/services/fsa-client';
import { CareHome } from '@/lib/shared/types/care-home';

// Mock FSAClient
jest.mock('@/lib/data-engine/enrichment/services/fsa-client');

describe('FSAEnrichmentService', () => {
  let service: FSAEnrichmentService;
  let mockFSAClient: jest.Mocked<FSAClient>;

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
    mockFSAClient = {
      searchBusiness: jest.fn().mockResolvedValue({
        BusinessName: 'Test Care Home',
        PostCode: 'SW1A 1AA',
        RatingValue: '5',
        RatingKey: 'fhrs_5_en-gb',
        RatingDate: '2024-11-15',
        LocalAuthorityName: 'Westminster',
        HygieneScore: '0',
        StructuralScore: '0',
        ConfidenceInManagementScore: '0',
        SchemeType: 'FHRS',
      }),
      getDetailedData: jest.fn().mockReturnValue({
        fsa_rating: 5,
        fsa_rating_key: 'fhrs_5_en-gb',
        fsa_rating_date: '2024-11-15',
        fsa_health_score: 0,
        hygiene_score: 0,
        structural_score: 0,
        management_score: 0,
        local_authority: 'Westminster',
        inspection_details: {
          last_inspection: '2024-11-15',
          next_inspection: null,
        },
        sub_scores: {
          hygiene: 0,
          structural: 0,
          management: 0,
        },
        summary: {
          status: 'available' as const,
          rating: '5',
          rating_label: 'Excellent',
        },
      }),
    } as any;

    // Mock FSAClient constructor
    (FSAClient as jest.MockedClass<typeof FSAClient>).mockImplementation(
      () => mockFSAClient
    );

    service = new FSAEnrichmentService({
      useCache: false, // Disable cache for tests
      timeout: 10000,
    });
  });

  describe('enrich', () => {
    it('should successfully enrich home with FSA data', async () => {
      const mockBusiness = {
        BusinessName: 'Test Care Home',
        PostCode: 'SW1A 1AA',
        RatingValue: '5',
        RatingKey: 'fhrs_5_en-gb',
        RatingDate: '2024-11-15',
        LocalAuthorityName: 'Westminster',
        HygieneScore: '0',
        StructuralScore: '0',
        ConfidenceInManagementScore: '0',
        SchemeType: 'FHRS',
      };

      const mockDetailedData = {
        fsa_rating: 5,
        fsa_rating_key: 'fhrs_5_en-gb',
        fsa_rating_date: '2024-11-15',
        fsa_health_score: 0,
        hygiene_score: 0,
        structural_score: 0,
        management_score: 0,
        local_authority: 'Westminster',
        inspection_details: {
          last_inspection: '2024-11-15',
          next_inspection: null,
        },
        sub_scores: {
          hygiene: 0,
          structural: 0,
          management: 0,
        },
        summary: {
          status: 'available' as const,
          rating: '5',
          rating_label: 'Excellent',
        },
      };

      mockFSAClient.searchBusiness.mockResolvedValue(mockBusiness as any);
      mockFSAClient.getDetailedData.mockReturnValue(mockDetailedData);

      const result = await service.enrich(mockHome);

      expect(result.status).toBe('success');
      expect(result.source).toBe('fsa');
      expect(result.data.fsa_rating).toBe(5);
      expect(result.data.summary.rating_label).toBe('Excellent');
      expect(mockFSAClient.searchBusiness).toHaveBeenCalledWith(
        'Test Care Home',
        'SW1A 1AA',
        51.5074,
        -0.1278
      );
    });

    it('should return partial result when business not found', async () => {
      mockFSAClient.searchBusiness.mockResolvedValue(null);

      const result = await service.enrich(mockHome);

      expect(result.status).toBe('partial');
      expect(result.error).toContain('Business not found');
      expect(result.data).toEqual({});
    });

    it('should handle API errors gracefully', async () => {
      mockFSAClient.searchBusiness.mockRejectedValue(
        new Error('Network error')
      );

      const result = await service.enrich(mockHome);

      expect(result.status).toBe('partial');
      expect(result.error).toContain('Network error');
    });

    it('should handle timeout errors', async () => {
      mockFSAClient.searchBusiness.mockRejectedValue(
        new Error('FSA API request timeout after 10000ms')
      );

      const result = await service.enrich(mockHome);

      expect(result.status).toBe('partial');
      expect(result.error).toContain('timeout');
    });

    it('should validate home data', async () => {
      const invalidHome = {} as CareHome;

      const result = await service.enrich(invalidHome);
      expect(result.status).toBe('failed');
      expect(result.error).toMatch(/Home|required/);
    });

    it('should require name and postcode', async () => {
      const homeWithoutName = {
        ...mockHome,
        name: '',
      };

      const result = await service.enrich(homeWithoutName);
      expect(result.status).toBe('failed');
      expect(result.error).toContain('required');
    });

    it('should handle different rating values', async () => {
      const testCases = [
        { rating: '5', expectedNumeric: 5, expectedLabel: 'Excellent' },
        { rating: '4', expectedNumeric: 4, expectedLabel: 'Very Good' },
        { rating: '3', expectedNumeric: 3, expectedLabel: 'Good' },
        { rating: '2', expectedNumeric: 2, expectedLabel: 'Fair' },
        { rating: '1', expectedNumeric: 1, expectedLabel: 'Poor' },
        { rating: '0', expectedNumeric: 0, expectedLabel: 'Urgent Improvement Required' },
      ];

      for (const testCase of testCases) {
        const mockBusiness = {
          BusinessName: 'Test Care Home',
          PostCode: 'SW1A 1AA',
          RatingValue: testCase.rating,
          RatingKey: `fhrs_${testCase.rating}_en-gb`,
          RatingDate: '2024-11-15',
          LocalAuthorityName: 'Westminster',
          SchemeType: 'FHRS',
        };

        const mockDetailedData = {
          fsa_rating: testCase.expectedNumeric,
          fsa_rating_key: `fhrs_${testCase.rating}_en-gb`,
          fsa_rating_date: '2024-11-15',
          fsa_health_score: 0,
          hygiene_score: null,
          structural_score: null,
          management_score: null,
          local_authority: 'Westminster',
          inspection_details: {
            last_inspection: '2024-11-15',
            next_inspection: null,
          },
          sub_scores: {
            hygiene: null,
            structural: null,
            management: null,
          },
          summary: {
            status: 'available' as const,
            rating: testCase.rating,
            rating_label: testCase.expectedLabel,
          },
        };

        mockFSAClient.searchBusiness.mockResolvedValue(mockBusiness as any);
        mockFSAClient.getDetailedData.mockReturnValue(mockDetailedData);

        const result = await service.enrich(mockHome);

        expect(result.status).toBe('success');
        expect(result.data.summary.rating).toBe(testCase.rating);
        expect(result.data.fsa_rating).toBe(testCase.expectedNumeric);
      }
    });
  });

  describe('isAvailable', () => {
    it('should check feature flags', () => {
      // This will depend on feature flags configuration
      const available = service.isAvailable();
      expect(typeof available).toBe('boolean');
    });
  });
});

