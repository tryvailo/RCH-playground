/**
 * Staff Enrichment Service Tests
 */

import { StaffEnrichmentService } from '@/lib/data-engine/enrichment/services/staff';
import { StaffDataClient } from '@/lib/data-engine/enrichment/services/staff-client';
import { CareHome } from '@/lib/shared/types/care-home';

// Mock StaffDataClient
jest.mock('@/lib/data-engine/enrichment/services/staff-client');

describe('StaffEnrichmentService', () => {
  let service: StaffEnrichmentService;
  let mockStaffDataClient: jest.Mocked<StaffDataClient>;

  const mockHome: CareHome = {
    id: 'test-1',
    name: 'Test Care Home',
    postcode: 'SW1A 1AA',
    cqc_location_id: '1-1234567890',
    provider_name: 'Test Care Provider Ltd',
  } as any;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();

    // Create mock client with default implementations
    mockStaffDataClient = {
      getGlassdoorData: jest.fn().mockResolvedValue({
        company_name: 'Test Care Provider Ltd',
        rating: 4.2,
        reviews_count: 15,
        work_life_balance: 3.8,
        management_rating: 4.0,
      }),
      getLinkedInData: jest.fn().mockResolvedValue(null),
      getJobBoardData: jest.fn().mockResolvedValue(null),
      getComprehensiveResearch: jest.fn().mockResolvedValue({
        company_name: 'Test Care Provider Ltd',
        employee_satisfaction: {
          rating: 4.2,
        },
        staff_retention: {
          turnover_rate: 12,
          average_tenure: 3.5,
          trend: 'improving' as const,
        },
        qualifications: {
          training_programs: ['dementia', 'palliative'],
        },
      }),
    } as any;

    // Mock StaffDataClient constructor
    (StaffDataClient as jest.MockedClass<typeof StaffDataClient>).mockImplementation(
      () => mockStaffDataClient
    );

    service = new StaffEnrichmentService({
      useCache: false, // Disable cache for tests
      timeout: 30000,
    });
  });

  describe('enrich', () => {
    it('should successfully enrich home with staff data', async () => {
      const mockGlassdoor = {
        company_name: 'Test Care Provider Ltd',
        rating: 4.2,
        reviews_count: 15,
        work_life_balance: 3.8,
        management_rating: 4.0,
      };

      const mockResearch = {
        company_name: 'Test Care Provider Ltd',
        employee_satisfaction: {
          rating: 4.2,
        },
        staff_retention: {
          turnover_rate: 12,
          average_tenure: 3.5,
          trend: 'improving' as const,
        },
        qualifications: {
          training_programs: ['dementia', 'palliative'],
        },
      };

      mockStaffDataClient.getGlassdoorData.mockResolvedValue(mockGlassdoor);
      mockStaffDataClient.getLinkedInData.mockResolvedValue(null);
      mockStaffDataClient.getJobBoardData.mockResolvedValue(null);
      mockStaffDataClient.getComprehensiveResearch.mockResolvedValue(mockResearch);

      const result = await service.enrich(mockHome);

      expect(result.status).toBe('success');
      expect(result.source).toBe('staff');
      expect(result.data.employee_satisfaction.glassdoor_rating).toBe(4.2);
      expect(result.data.staff_retention.turnover_rate).toBe(12);
      expect(result.data.staff_retention.average_tenure).toBe(3.5);
      expect(result.data.combined_analysis.staff_quality_score).toBeDefined();
    });

    it('should handle missing data gracefully', async () => {
      mockStaffDataClient.getGlassdoorData.mockResolvedValue(null);
      mockStaffDataClient.getLinkedInData.mockResolvedValue(null);
      mockStaffDataClient.getJobBoardData.mockResolvedValue(null);
      mockStaffDataClient.getComprehensiveResearch.mockResolvedValue(null);

      const result = await service.enrich(mockHome);

      // When no data available, should handle gracefully
      expect(result.status).toMatch(/success|partial/);
      expect(result.data.summary.status).toMatch(/not_available|available/);
    });

    it('should combine data from multiple sources', async () => {
      const mockGlassdoor = {
        company_name: 'Test Care Provider Ltd',
        rating: 4.0,
      };

      const mockResearch = {
        company_name: 'Test Care Provider Ltd',
        staff_retention: {
          turnover_rate: 15,
        },
      };

      mockStaffDataClient.getGlassdoorData.mockResolvedValue(mockGlassdoor);
      mockStaffDataClient.getLinkedInData.mockResolvedValue({ company_name: 'Test' });
      mockStaffDataClient.getJobBoardData.mockResolvedValue({ company_name: 'Test' });
      mockStaffDataClient.getComprehensiveResearch.mockResolvedValue(mockResearch);

      const result = await service.enrich(mockHome);

      expect(result.status).toBe('success');
      expect(result.data.summary.sources.length).toBeGreaterThan(0);
      expect(result.data.employee_satisfaction.glassdoor_rating).toBe(4.0);
      expect(result.data.staff_retention.turnover_rate).toBe(15);
    });

    it('should calculate staff quality score correctly', async () => {
      const mockGlassdoor = {
        company_name: 'Test Care Provider Ltd',
        rating: 4.5,
      };

      const mockResearch = {
        company_name: 'Test Care Provider Ltd',
        staff_retention: {
          turnover_rate: 8, // Low turnover
          average_tenure: 4.0, // High tenure
        },
      };

      mockStaffDataClient.getGlassdoorData.mockResolvedValue(mockGlassdoor);
      mockStaffDataClient.getLinkedInData.mockResolvedValue(null);
      mockStaffDataClient.getJobBoardData.mockResolvedValue(null);
      mockStaffDataClient.getComprehensiveResearch.mockResolvedValue(mockResearch);

      const result = await service.enrich(mockHome);

      expect(result.status).toBe('success');
      expect(result.data.combined_analysis.staff_quality_score).toBeGreaterThan(50);
      expect(result.data.combined_analysis.staff_quality_category).toBeDefined();
    });

    it('should handle API errors gracefully', async () => {
      mockStaffDataClient.getGlassdoorData.mockRejectedValue(
        new Error('network timeout')
      );
      mockStaffDataClient.getLinkedInData.mockRejectedValue(
        new Error('network timeout')
      );
      mockStaffDataClient.getJobBoardData.mockRejectedValue(
        new Error('network timeout')
      );
      mockStaffDataClient.getComprehensiveResearch.mockRejectedValue(
        new Error('network timeout')
      );

      const result = await service.enrich(mockHome);

      // When all data sources fail, should still return result
      expect(result.status).toMatch(/success|partial/);
    });
  });

  describe('isAvailable', () => {
    it('should check feature flags', () => {
      const available = service.isAvailable();
      expect(typeof available).toBe('boolean');
    });
  });
});



