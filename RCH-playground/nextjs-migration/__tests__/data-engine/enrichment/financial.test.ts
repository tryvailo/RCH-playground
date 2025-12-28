/**
 * Financial Enrichment Service Tests
 */

import { FinancialEnrichmentService } from '@/lib/data-engine/enrichment/services/financial';
import { CompaniesHouseClient } from '@/lib/data-engine/enrichment/services/companies-house-client';
import { CareHome } from '@/lib/shared/types/care-home';

// Mock CompaniesHouseClient
jest.mock('@/lib/data-engine/enrichment/services/companies-house-client');

describe('FinancialEnrichmentService', () => {
  let service: FinancialEnrichmentService;
  let mockCompaniesHouseClient: jest.Mocked<CompaniesHouseClient>;

  const mockHome: CareHome = {
    id: 'test-1',
    name: 'Test Care Home',
    postcode: 'SW1A 1AA',
    cqc_location_id: '1-1234567890',
    company_number: '12345678',
  } as any;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();

    // Create mock client with default implementations
    mockCompaniesHouseClient = {
      getCompanyProfile: jest.fn().mockResolvedValue({
        company_number: '12345678',
        company_name: 'Test Care Home Ltd',
        company_status: 'active',
      }),
      getAccounts: jest.fn().mockResolvedValue({
        company_number: '12345678',
        accounts: {},
      }),
      getFilingHistory: jest.fn().mockResolvedValue({
        items: [],
        items_per_page: 50,
        kind: 'filing-history',
        start_index: 0,
        total_count: 0,
      }),
      searchCompany: jest.fn().mockResolvedValue([]),
    } as any;

    // Mock CompaniesHouseClient constructor
    (CompaniesHouseClient as jest.MockedClass<typeof CompaniesHouseClient>).mockImplementation(
      () => mockCompaniesHouseClient
    );

    service = new FinancialEnrichmentService({
      useCache: false, // Disable cache for tests
      timeout: 15000,
    });
  });

  describe('enrich', () => {
    it('should successfully enrich home with financial data', async () => {
      const mockProfile = {
        company_number: '12345678',
        company_name: 'Test Care Home Ltd',
        company_status: 'active',
      };

      const mockAccounts = {
        company_number: '12345678',
        accounts: {
          balance_sheet: {
            current_assets: {
              total_current_assets: 500000,
            },
            creditors_amounts_falling_due_within_one_year: 200000,
            total_net_assets: 1000000,
          },
          profit_and_loss: {
            turnover: 2000000,
            profit_or_loss_before_tax: 300000,
          },
          other_accounts: {
            total_assets: 1000000,
            total_liabilities: 300000,
            shareholders_funds: 700000,
          },
          last_accounts: {
            made_up_to: '2024-12-31',
          },
        },
      };

      const mockFilingHistory = {
        items: [
          {
            date: '2024-12-31',
            type: 'accounts',
            category: 'accounts',
            transaction_id: 'abc123',
          },
        ],
        items_per_page: 50,
        kind: 'filing-history',
        start_index: 0,
        total_count: 1,
      };

      mockCompaniesHouseClient.getCompanyProfile.mockResolvedValue(mockProfile as any);
      mockCompaniesHouseClient.getAccounts.mockResolvedValue(mockAccounts as any);
      mockCompaniesHouseClient.getFilingHistory.mockResolvedValue(mockFilingHistory as any);

      const result = await service.enrich(mockHome);

      expect(result.status).toBe('success');
      expect(result.source).toBe('financial');
      expect(result.data.company_number).toBe('12345678');
      expect(result.data.financial_stability.altman_z_score).toBeDefined();
      expect(result.data.financial_stability.bankruptcy_risk).toBeDefined();
      expect(mockCompaniesHouseClient.getCompanyProfile).toHaveBeenCalledWith('12345678');
    });

    it('should return partial result when company number not provided', async () => {
      const homeWithoutCompanyNumber = {
        ...mockHome,
        company_number: undefined,
      } as any;

      const result = await service.enrich(homeWithoutCompanyNumber);

      expect(result.status).toBe('partial');
      expect(result.error).toContain('No company number');
    });

    it('should search company by name if company number not provided', async () => {
      const homeWithoutCompanyNumber = {
        ...mockHome,
        company_number: undefined,
      } as any;

      const mockSearchResult = [
        {
          company_number: '12345678',
          company_name: 'Test Care Home Ltd',
        },
      ];

      mockCompaniesHouseClient.searchCompany.mockResolvedValue(mockSearchResult as any);
      mockCompaniesHouseClient.getCompanyProfile.mockResolvedValue({
        company_number: '12345678',
        company_name: 'Test Care Home Ltd',
      } as any);
      mockCompaniesHouseClient.getAccounts.mockResolvedValue({
        company_number: '12345678',
        accounts: {},
      } as any);
      mockCompaniesHouseClient.getFilingHistory.mockResolvedValue({
        items: [],
        items_per_page: 50,
        kind: 'filing-history',
        start_index: 0,
        total_count: 0,
      } as any);

      const result = await service.enrich(homeWithoutCompanyNumber);

      expect(mockCompaniesHouseClient.searchCompany).toHaveBeenCalledWith('Test Care Home');
      expect(result.status).toBe('success');
    });

    it('should handle API errors gracefully', async () => {
      mockCompaniesHouseClient.getCompanyProfile.mockRejectedValue(
        new Error('network error')
      );
      mockCompaniesHouseClient.getAccounts.mockRejectedValue(
        new Error('network error')
      );
      mockCompaniesHouseClient.getFilingHistory.mockRejectedValue(
        new Error('network error')
      );

      const result = await service.enrich(mockHome);

      // When all API calls fail, should handle gracefully
      expect(result.status).toMatch(/success|partial/);
    });

    it('should handle timeout errors', async () => {
      mockCompaniesHouseClient.getCompanyProfile.mockRejectedValue(
        new Error('Companies House API request timeout after 15000ms')
      );
      mockCompaniesHouseClient.getAccounts.mockRejectedValue(
        new Error('timeout')
      );
      mockCompaniesHouseClient.getFilingHistory.mockRejectedValue(
        new Error('timeout')
      );

      const result = await service.enrich(mockHome);

      // When all API calls timeout, should still return result
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



