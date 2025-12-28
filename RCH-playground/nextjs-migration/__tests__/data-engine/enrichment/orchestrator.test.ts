/**
 * Enrichment Orchestrator Tests
 */

import { CareHome } from '@/lib/shared/types/care-home';
import { IEnrichmentService, EnrichmentResult } from '@/lib/data-engine/enrichment/types';

// Mock all enrichment services with inline factory functions
jest.mock('@/lib/data-engine/enrichment/services/fsa', () => ({
  FSAEnrichmentService: class MockFSA implements IEnrichmentService {
    serviceName = 'fsa';
    async enrich(): Promise<EnrichmentResult> {
      return {
        source: 'fsa',
        status: 'success',
        data: { fsa_rating: 5 },
        metadata: { enrichedAt: new Date().toISOString() },
      };
    }
    isAvailable(): boolean {
      return true;
    }
  },
}));

jest.mock('@/lib/data-engine/enrichment/services/financial', () => ({
  FinancialEnrichmentService: class MockFinancial implements IEnrichmentService {
    serviceName = 'financial';
    async enrich(): Promise<EnrichmentResult> {
      return {
        source: 'financial',
        status: 'success',
        data: { financial_score: 8.5 },
        metadata: { enrichedAt: new Date().toISOString() },
      };
    }
    isAvailable(): boolean {
      return true;
    }
  },
}));

jest.mock('@/lib/data-engine/enrichment/services/google-places', () => ({
  GooglePlacesEnrichmentService: class MockGoogle implements IEnrichmentService {
    serviceName = 'google';
    async enrich(): Promise<EnrichmentResult> {
      return {
        source: 'google',
        status: 'success',
        data: { google_rating: 4.8 },
        metadata: { enrichedAt: new Date().toISOString() },
      };
    }
    isAvailable(): boolean {
      return true;
    }
  },
}));

jest.mock('@/lib/data-engine/enrichment/services/staff', () => ({
  StaffEnrichmentService: class MockStaff implements IEnrichmentService {
    serviceName = 'staff';
    async enrich(): Promise<EnrichmentResult> {
      return {
        source: 'staff',
        status: 'success',
        data: { staff_quality: 'high' },
        metadata: { enrichedAt: new Date().toISOString() },
      };
    }
    isAvailable(): boolean {
      return true;
    }
  },
}));

jest.mock('@/lib/data-engine/enrichment/services/cqc', () => ({
  CQCDeepDiveEnrichmentService: class MockCQC implements IEnrichmentService {
    serviceName = 'cqc';
    async enrich(): Promise<EnrichmentResult> {
      return {
        source: 'cqc',
        status: 'success',
        data: { cqc_rating: 'Good' },
        metadata: { enrichedAt: new Date().toISOString() },
      };
    }
    isAvailable(): boolean {
      return true;
    }
  },
}));

jest.mock('@/lib/data-engine/enrichment/services/neighbourhood', () => ({
  NeighbourhoodAnalysisEnrichmentService: class MockNeighbourhood implements IEnrichmentService {
    serviceName = 'neighbourhood';
    async enrich(): Promise<EnrichmentResult> {
      return {
        source: 'neighbourhood',
        status: 'success',
        data: { walkability_score: 7.5 },
        metadata: { enrichedAt: new Date().toISOString() },
      };
    }
    isAvailable(): boolean {
      return true;
    }
  },
}));

// Import orchestrator after mocks are defined
import { EnrichmentOrchestrator, EnrichmentConfig } from '@/lib/data-engine/enrichment/orchestrator';

describe('EnrichmentOrchestrator', () => {
  let orchestrator: EnrichmentOrchestrator;

  const mockHome: CareHome = {
    id: 'test-1',
    name: 'Test Care Home',
    postcode: 'SW1A 1AA',
    latitude: 51.5074,
    longitude: -0.1278,
    cqc_location_id: '1-1234567890',
  } as any;

  beforeEach(() => {
    orchestrator = new EnrichmentOrchestrator();
  });

  describe('enrichHome', () => {
    it('should enrich a single home with all enabled sources', async () => {
      const config: EnrichmentConfig = {
        enabledSources: ['fsa', 'financial'],
        parallelLimit: 5,
        timeoutPerSource: 30,
        retryFailed: false,
        cacheResults: false,
      };

      const result = await orchestrator.enrichHome(mockHome, config);

      expect(result.homeId).toBeDefined();
      expect(result.home).toEqual(mockHome);
      expect(result.enrichments).toBeDefined();
      expect(result.metadata).toBeDefined();
    });

    it('should handle missing services gracefully', async () => {
      const config: EnrichmentConfig = {
        enabledSources: ['nonexistent'],
        parallelLimit: 5,
        timeoutPerSource: 30,
        retryFailed: false,
        cacheResults: false,
      };

      const result = await orchestrator.enrichHome(mockHome, config);

      expect(result.metadata.errors.length).toBeGreaterThan(0);
      expect(result.metadata.errors[0]).toContain('Service not available');
    });

    it('should cache results when enabled', async () => {
      const config: EnrichmentConfig = {
        enabledSources: ['fsa'],
        parallelLimit: 5,
        timeoutPerSource: 30,
        retryFailed: false,
        cacheResults: true,
      };

      const result1 = await orchestrator.enrichHome(mockHome, config);
      const result2 = await orchestrator.enrichHome(mockHome, config);

      // Second call should be faster (cached)
      expect(result2.metadata.enrichmentTime).toBeLessThanOrEqual(result1.metadata.enrichmentTime);
    });
  });

  describe('enrichHomesBatch', () => {
    it('should enrich multiple homes', async () => {
      const homes: CareHome[] = [
        mockHome,
        { ...mockHome, id: 'test-2', name: 'Test Care Home 2' },
      ];

      const config: EnrichmentConfig = {
        enabledSources: ['fsa'],
        parallelLimit: 5,
        timeoutPerSource: 30,
        retryFailed: false,
        cacheResults: false,
      };

      const results = await orchestrator.enrichHomesBatch(
        homes,
        config,
        undefined,
        (progress, message) => {
          expect(progress).toBeGreaterThanOrEqual(0);
          expect(progress).toBeLessThanOrEqual(100);
          expect(typeof message).toBe('string');
        }
      );

      expect(results.length).toBe(2);
      expect(results[0].homeId).toBeDefined();
      expect(results[1].homeId).toBeDefined();
    });
  });

  describe('listServices', () => {
    it('should return list of registered services', () => {
      const services = orchestrator.listServices();
      expect(Array.isArray(services)).toBe(true);
    });
  });

  describe('getStats', () => {
    it('should return orchestrator statistics', () => {
      const stats = orchestrator.getStats();
      expect(stats.orchestrator).toBeDefined();
      expect(stats.services).toBeDefined();
      expect(stats.cacheSize).toBeDefined();
    });
  });
});



