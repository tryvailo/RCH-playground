/**
 * CQC Deep Dive Enrichment Service Tests
 */

import { CQCDeepDiveEnrichmentService } from '@/lib/data-engine/enrichment/services/cqc';
import { CQCClient } from '@/lib/data-engine/enrichment/services/cqc-client';
import { CareHome } from '@/lib/shared/types/care-home';

// Mock CQCClient
jest.mock('@/lib/data-engine/enrichment/services/cqc-client');

describe('CQCDeepDiveEnrichmentService', () => {
  let service: CQCDeepDiveEnrichmentService;
  let mockCQCClient: jest.Mocked<CQCClient>;

  const mockHome: CareHome = {
    id: 'test-1',
    name: 'Test Care Home',
    postcode: 'SW1A 1AA',
    cqc_location_id: '1-1234567890',
    rating: 'Good',
    cqc_rating_safe: 'Good',
    cqc_rating_effective: 'Good',
    cqc_rating_caring: 'Outstanding',
    cqc_rating_responsive: 'Good',
    cqc_rating_well_led: 'Good',
    last_inspection_date: '2024-01-15',
  } as any;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();

    // Create mock client with default implementations
    mockCQCClient = {
      getLocation: jest.fn().mockResolvedValue(null),
      getLocationInspectionHistory: jest.fn().mockResolvedValue([]),
      getLocationEnforcementActions: jest.fn().mockResolvedValue([]),
      getProviderLocations: jest.fn().mockResolvedValue([]),
      getLocationHistoricalRatings: jest.fn().mockResolvedValue([]),
    } as any;

    // Mock CQCClient constructor
    (CQCClient as jest.MockedClass<typeof CQCClient>).mockImplementation(
      () => mockCQCClient
    );

    service = new CQCDeepDiveEnrichmentService({
      useCache: false, // Disable cache for tests
      timeout: 30000,
    });
  });

  describe('enrich', () => {
    it('should successfully enrich home with CQC Deep Dive data', async () => {
      const mockInspections = [
        {
          inspectionDate: '2024-01-15',
          overallRating: 'Good',
          safeRating: 'Good',
        },
        {
          inspectionDate: '2023-01-10',
          overallRating: 'Requires improvement',
          safeRating: 'Requires improvement',
        },
      ];

      const mockEnforcementActions = [];

      mockCQCClient.getLocationInspectionHistory.mockResolvedValue(mockInspections);
      mockCQCClient.getLocationEnforcementActions.mockResolvedValue(mockEnforcementActions);
      mockCQCClient.getProviderLocations.mockResolvedValue([]);

      const result = await service.enrich(mockHome);

      expect(result.status).toBe('success');
      expect(result.source).toBe('cqcDeepDive');
      expect(result.data.overall).toBe('Good');
      expect(result.data.rating_trend).toBe('Improving');
      expect(result.data.inspection_history.length).toBe(2);
      expect(mockCQCClient.getLocationInspectionHistory).toHaveBeenCalled();
    });

    it('should handle missing location ID gracefully', async () => {
      const homeWithoutLocationId = {
        ...mockHome,
        id: undefined,
        cqc_location_id: undefined,
      };

      const result = await service.enrich(homeWithoutLocationId);

      expect(result.status).toBe('failed');
      expect(result.error).toContain('location ID');
    });

    it('should calculate rating trend correctly', async () => {
      const mockInspections = [
        {
          inspectionDate: '2024-01-15',
          overallRating: 'Good',
        },
        {
          inspectionDate: '2023-01-10',
          overallRating: 'Good',
        },
        {
          inspectionDate: '2022-01-05',
          overallRating: 'Good',
        },
      ];

      mockCQCClient.getLocationInspectionHistory.mockResolvedValue(mockInspections);
      mockCQCClient.getLocationEnforcementActions.mockResolvedValue([]);
      mockCQCClient.getProviderLocations.mockResolvedValue([]);

      const result = await service.enrich(mockHome);

      expect(result.status).toBe('success');
      expect(result.data.rating_trend).toBe('Stable');
    });

    it('should parse regulated activities correctly', async () => {
      const homeWithActivities = {
        ...mockHome,
        regulated_activities: [
          {
            id: 'accommodation_nursing',
            name: 'Accommodation for persons who require nursing',
            active: true,
          },
          {
            id: 'personal_care',
            name: 'Personal care',
            active: true,
          },
        ],
      };

      mockCQCClient.getLocationInspectionHistory.mockResolvedValue([]);
      mockCQCClient.getLocationEnforcementActions.mockResolvedValue([]);
      mockCQCClient.getProviderLocations.mockResolvedValue([]);

      const result = await service.enrich(homeWithActivities);

      expect(result.status).toBe('success');
      expect(result.data.regulated_activities.length).toBe(2);
      expect(result.data.has_nursing_care_license).toBe(true);
      expect(result.data.has_personal_care_license).toBe(true);
    });

    it('should handle API errors gracefully', async () => {
      mockCQCClient.getLocationInspectionHistory.mockRejectedValue(
        new Error('timeout')
      );
      mockCQCClient.getLocationEnforcementActions.mockRejectedValue(
        new Error('timeout')
      );
      mockCQCClient.getProviderLocations.mockRejectedValue(
        new Error('timeout')
      );

      const result = await service.enrich(mockHome);

      // When API calls fail, should still return result with what data it has
      expect(result.status).toMatch(/success|partial/);
    });

    it('should include enforcement actions when available', async () => {
      const mockActions = [
        {
          actionType: 'Warning Notice',
          actionDate: '2023-06-01',
          description: 'Safety concerns',
        },
      ];

      mockCQCClient.getLocationInspectionHistory.mockResolvedValue([]);
      mockCQCClient.getLocationEnforcementActions.mockResolvedValue(mockActions);
      mockCQCClient.getProviderLocations.mockResolvedValue([]);

      const result = await service.enrich(mockHome);

      expect(result.status).toBe('success');
      expect(result.data.enforcement_actions.length).toBe(1);
      expect(result.data.enforcement_actions[0].actionType).toBe('Warning Notice');
    });
  });

  describe('isAvailable', () => {
    it('should check feature flags', () => {
      const available = service.isAvailable();
      expect(typeof available).toBe('boolean');
    });
  });
});



