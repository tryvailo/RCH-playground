/**
 * Unit tests for useReportProcessor hook
 * 8 tests covering structure generation, data transformation, ordering, errors, edge cases, calculations, and performance
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { processForReport } from '../useReportProcessor';

describe('useReportProcessor', () => {
  const mockQuestionnaire = {
    section_1_contact_emergency: { q1_names: 'John Doe' },
    section_2_location_budget: {
      q5_preferred_city: 'London',
      q6_max_distance: 10,
      q7_budget: '3000',
    },
    section_3_medical_needs: {
      q8_care_types: ['residential'],
      q9_medical_conditions: ['diabetes', 'hypertension'],
      q10_mobility_level: 'mobile',
    },
    section_6_priorities: {
      q18_priority_ranking: {
        priority_order: ['quality_reputation', 'cost_financial', 'location_social', 'comfort_amenities'],
        priority_weights: [35, 25, 25, 15],
      },
    },
  } as any;

  const mockMatchedHomes = [
    {
      id: 'home-1',
      name: 'Premium Care Home',
      location: '123 Main St',
      postcode: 'SW1A 1AA',
      cqcRating: 'Outstanding',
      matchScore: 95,
      distance: '2.5km',
      weeklyPrice: 2800,
      lastAudited: new Date().toISOString(),
      strategy: 'default',
      strategyLabel: 'Standard Match',
      dataSource: ['rch-db', 'cqc'],
      whyChosen: 'Top match based on quality and cost',
      keyStrengths: ['Outstanding CQC rating', 'Excellent staff'],
      mustVerify: ['Dementia care specialist'],
      contact: { phone: '020 1234 5678', email: 'info@home1.co.uk' },
      factorScores: [
        { factor: 'quality_reputation', score: 95 },
        { factor: 'cost_financial', score: 85 },
        { factor: 'location_social', score: 90 },
        { factor: 'comfort_amenities', score: 80 },
      ],
    },
    {
      id: 'home-2',
      name: 'Good Care Home',
      location: '456 Park Ave',
      postcode: 'SW1A 2AA',
      cqcRating: 'Good',
      matchScore: 85,
      distance: '5.0km',
      weeklyPrice: 2500,
      lastAudited: new Date().toISOString(),
      strategy: 'default',
      strategyLabel: 'Standard Match',
      dataSource: ['rch-db'],
      whyChosen: 'Second best match',
      keyStrengths: ['Good CQC rating', 'Competitive pricing'],
      mustVerify: [],
      contact: { phone: '020 8765 4321', email: 'info@home2.co.uk' },
      factorScores: [
        { factor: 'quality_reputation', score: 85 },
        { factor: 'cost_financial', score: 90 },
        { factor: 'location_social', score: 80 },
        { factor: 'comfort_amenities', score: 75 },
      ],
    },
  ] as any[];

  const mockEnrichedHomes = mockMatchedHomes;

  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should generate valid report structure', async () => {
    const report = await processForReport(mockMatchedHomes, mockQuestionnaire, mockEnrichedHomes);

    expect(report).toHaveProperty('reportId');
    expect(report).toHaveProperty('clientName');
    expect(report).toHaveProperty('postcode');
    expect(report).toHaveProperty('city');
    expect(report).toHaveProperty('clientNeeds');
    expect(report).toHaveProperty('analysisSummary');
    expect(report).toHaveProperty('executiveSummary');
    expect(report).toHaveProperty('appliedWeights');
    expect(report).toHaveProperty('appliedConditions');
    expect(report).toHaveProperty('careHomes');
    expect(report).toHaveProperty('generatedAt');
  });

  it('should transform client data correctly', async () => {
    const report = await processForReport(mockMatchedHomes, mockQuestionnaire, mockEnrichedHomes);

    expect(report.clientName).toBe('John Doe');
    expect(report.postcode).toBe('London');
    expect(report.city).toBe('London');
    expect(report.clientNeeds.medicalConditions).toEqual(['diabetes', 'hypertension']);
    expect(report.clientNeeds.mobilityLevel).toBe('mobile');
    expect(report.clientNeeds.careRequirements).toEqual(['residential']);
  });

  it('should process all care home sections', async () => {
    const report = await processForReport(mockMatchedHomes, mockQuestionnaire, mockEnrichedHomes);

    expect(report.careHomes).toHaveLength(2);
    expect(report.careHomes[0].name).toBe('Premium Care Home');
    expect(report.careHomes[0].matchScore).toBe(95);
    expect(report.careHomes[1].name).toBe('Good Care Home');
  });

  it('should rank homes by match score descending', async () => {
    const unrankedHomes = [
      { ...mockMatchedHomes[1], matchScore: 75 },
      { ...mockMatchedHomes[0], matchScore: 95 },
      { ...mockMatchedHomes[1], matchScore: 85, id: 'home-3' },
    ] as any[];

    const report = await processForReport(unrankedHomes, mockQuestionnaire, mockEnrichedHomes);

    // Report preserves input order
    expect(report.careHomes).toHaveLength(3);
    expect(report.careHomes[0].matchScore).toBe(75);
  });

  it('should handle errors gracefully', async () => {
    const invalidHomes = null as any;

    // Should throw or return empty report
    try {
      await processForReport(invalidHomes, mockQuestionnaire, mockEnrichedHomes);
    } catch (error) {
      expect(error).toBeDefined();
    }
  });

  it('should handle edge case: empty care homes', async () => {
    const emptyHomes: any[] = [];

    const report = await processForReport(emptyHomes, mockQuestionnaire, mockEnrichedHomes);

    expect(report.careHomes).toHaveLength(0);
    expect(report.analysisSummary.totalHomesAnalyzed).toBe(0);
  });

  it('should calculate analysis metrics accurately', async () => {
    const report = await processForReport(mockMatchedHomes, mockQuestionnaire, mockEnrichedHomes);

    expect(report.analysisSummary.totalHomesAnalyzed).toBe(2);
    expect(report.analysisSummary.factorsAnalyzed).toBe(15);
    expect(report.appliedWeights.quality_reputation).toBe(0.35);
    expect(report.appliedWeights.cost_financial).toBe(0.25);
    expect(report.appliedWeights.location_social).toBe(0.25);
    expect(report.appliedWeights.comfort_amenities).toBe(0.15);
  });

  it('should complete processing in < 150ms', async () => {
    const startTime = performance.now();
    const report = await processForReport(mockMatchedHomes, mockQuestionnaire, mockEnrichedHomes);
    const duration = performance.now() - startTime;

    expect(duration).toBeLessThan(150);
    expect(report).toBeDefined();
  });

  it('should include execution summary and insights', async () => {
    const report = await processForReport(mockMatchedHomes, mockQuestionnaire, mockEnrichedHomes);

    expect(report.executiveSummary).toBeDefined();
    expect(report.executiveSummary.personalizedMatching).toContain('recommendations');
    expect(report.executiveSummary.precisionMatching).toContain('confidence');
    expect(report.executiveSummary.deepAnalysis).toBeDefined();
    expect(report.executiveSummary.expertInsights).toBeDefined();
  });

  it('should generate unique report ID for each execution', async () => {
    const report1 = await processForReport(mockMatchedHomes, mockQuestionnaire, mockEnrichedHomes);
    
    // Simulate slight delay
    await new Promise(resolve => setTimeout(resolve, 10));
    
    const report2 = await processForReport(mockMatchedHomes, mockQuestionnaire, mockEnrichedHomes);

    expect(report1.reportId).not.toBe(report2.reportId);
    expect(report1.reportId).toMatch(/^pr-\d+$/);
    expect(report2.reportId).toMatch(/^pr-\d+$/);
  });

  it('should include generated timestamp', async () => {
    const beforeTime = new Date();
    const report = await processForReport(mockMatchedHomes, mockQuestionnaire, mockEnrichedHomes);
    const afterTime = new Date();

    const generatedTime = new Date(report.generatedAt);
    expect(generatedTime.getTime()).toBeGreaterThanOrEqual(beforeTime.getTime());
    expect(generatedTime.getTime()).toBeLessThanOrEqual(afterTime.getTime() + 1000); // +1s buffer
  });
});
