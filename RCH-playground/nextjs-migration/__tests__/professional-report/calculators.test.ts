/**
 * Professional Report Calculators Tests
 * Compare with Python implementation
 */

import {
  MedicalCalculator,
  SafetyCalculator,
  LocationCalculator,
  FinancialCalculator,
  StaffCalculator,
  CQCCalculator,
  SocialCalculator,
  ServicesCalculator,
} from '@/lib/reports/professional-report/matching/calculators';

describe('Category Calculators', () => {
  describe('MedicalCalculator', () => {
    let calculator: MedicalCalculator;

    beforeEach(() => {
      calculator = new MedicalCalculator();
    });

    it('should score dementia care match', async () => {
      const home = {
        name: 'Dementia Care Home',
        care_types: ['dementia', 'residential'],
      };
      const userProfile = {
        section_3_medical_needs: {
          q9_medical_conditions: ['dementia_alzheimers'],
        },
      };

      const score = await calculator.calculate(home, userProfile, {});
      expect(score).toBeGreaterThan(0);
      expect(score).toBeLessThanOrEqual(1.0);
    });

    it('should return normalized score (0-1.0)', async () => {
      const score = await calculator.calculate({}, {}, {});
      expect(score).toBeGreaterThanOrEqual(0);
      expect(score).toBeLessThanOrEqual(1.0);
    });
  });

  describe('SafetyCalculator', () => {
    let calculator: SafetyCalculator;

    beforeEach(() => {
      calculator = new SafetyCalculator();
    });

    it('should score Outstanding CQC rating highly', async () => {
      const home = {
        cqc_rating_overall: 'Outstanding',
      };
      const score = await calculator.calculate(home, {}, {});
      expect(score).toBeGreaterThan(0.7); // Outstanding should score high
    });

    it('should score Good CQC rating moderately', async () => {
      const home = {
        cqc_rating_overall: 'Good',
      };
      const score = await calculator.calculate(home, {}, {});
      expect(score).toBeGreaterThan(0.5);
      expect(score).toBeLessThan(0.8);
    });

    it('should handle FSA rating', async () => {
      const home = {
        fsa_rating: 5, // Excellent
      };
      const enrichedData = {
        fsa: {
          fsa_rating: 5,
        },
      };
      const score = await calculator.calculate(home, {}, enrichedData);
      expect(score).toBeGreaterThan(0);
    });
  });

  describe('LocationCalculator', () => {
    let calculator: LocationCalculator;

    beforeEach(() => {
      calculator = new LocationCalculator();
    });

    it('should score close homes highly', async () => {
      const home = {
        distance_km: 3, // Close
      };
      const userProfile = {
        section_2_location_budget: {
          q6_max_distance: 'within_5km',
        },
      };
      const score = await calculator.calculate(home, userProfile, {});
      expect(score).toBeGreaterThan(0.5);
    });

    it('should score far homes lower', async () => {
      const home = {
        distance_km: 50, // Far
      };
      const userProfile = {
        section_2_location_budget: {
          q6_max_distance: 'within_5km',
        },
      };
      const score = await calculator.calculate(home, userProfile, {});
      expect(score).toBeLessThan(0.5);
    });
  });

  describe('FinancialCalculator', () => {
    let calculator: FinancialCalculator;

    beforeEach(() => {
      calculator = new FinancialCalculator();
    });

    it('should score price match correctly', async () => {
      const home = {
        weekly_cost: 1000,
        fee_residential_from: 1000,
      };
      const userProfile = {
        section_2_location_budget: {
          q7_budget_range: '£1000-£1200',
        },
      };
      const score = await calculator.calculate(home, userProfile, {});
      expect(score).toBeGreaterThan(0);
    });

    it('should handle financial stability', async () => {
      const enrichedData = {
        financial: {
          altman_z_score: 3.5, // Safe
          bankruptcy_risk: 0.05, // Low risk
        },
      };
      const score = await calculator.calculate({}, {}, enrichedData);
      expect(score).toBeGreaterThan(0);
    });
  });

  describe('CQCCalculator', () => {
    let calculator: CQCCalculator;

    beforeEach(() => {
      calculator = new CQCCalculator();
    });

    it('should score Outstanding highest', async () => {
      const home = {
        cqc_rating_overall: 'Outstanding',
      };
      const score = await calculator.calculate(home, {}, {});
      expect(score).toBeGreaterThan(0.6);
    });

    it('should score Good moderately', async () => {
      const home = {
        cqc_rating_overall: 'Good',
      };
      const score = await calculator.calculate(home, {}, {});
      expect(score).toBeGreaterThan(0.4);
      expect(score).toBeLessThan(0.7);
    });
  });

  describe('All Calculators', () => {
    it('should all return normalized scores (0-1.0)', async () => {
      const calculators = [
        new MedicalCalculator(),
        new SafetyCalculator(),
        new LocationCalculator(),
        new FinancialCalculator(),
        new StaffCalculator(),
        new CQCCalculator(),
        new SocialCalculator(),
        new ServicesCalculator(),
      ];

      for (const calc of calculators) {
        const score = await calc.calculate({}, {}, {});
        expect(score).toBeGreaterThanOrEqual(0);
        expect(score).toBeLessThanOrEqual(1.0);
      }
    });
  });
});



