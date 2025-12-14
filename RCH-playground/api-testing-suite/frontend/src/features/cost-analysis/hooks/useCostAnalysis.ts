import { useState, useCallback, useMemo } from 'react';
import type {
  CostAnalysisData,
  HiddenFeesAnalysis,
  CostVsFundingScenarios,
  EnhancedProjections,
  CostAnalysisExecutiveSummary,
  HiddenFee,
  FundingScenario
} from '../types';
import type { ProfessionalCareHome, FundingOptimization } from '../../professional-report/types';

interface UseCostAnalysisOptions {
  careHomes: ProfessionalCareHome[];
  fundingOptimization?: FundingOptimization;
  region?: string;
  careType?: string;
}

interface UseCostAnalysisResult {
  costAnalysis: CostAnalysisData | null;
  isLoading: boolean;
  error: string | null;
  calculateCostAnalysis: () => void;
  getHomeAnalysis: (homeId: string) => HiddenFeesAnalysis | null;
  getHomeScenarios: (homeId: string) => FundingScenario[] | null;
  getBestScenario: (homeId: string) => FundingScenario | null;
  getTotalHiddenFees: () => number;
  getPotentialSavings: () => number;
}

// Hidden fees database - UK care home industry estimates
const HIDDEN_FEES_DATABASE: Record<string, Omit<HiddenFee, 'fee_id'>> = {
  admission_fee: {
    display_name: 'Admission/Registration Fee',
    description: 'One-time fee charged when moving in',
    category: 'move_in',
    frequency: 'one_time',
    estimated_amount: 1000,
    range_low: 500,
    range_high: 2000,
    weekly_equivalent: 0,
    annual_impact: 1000,
    likelihood: 65,
    negotiable: true,
    risk_level: 'medium'
  },
  deposit: {
    display_name: 'Security Deposit',
    description: 'Refundable deposit for room and belongings',
    category: 'move_in',
    frequency: 'one_time',
    estimated_amount: 2000,
    range_low: 500,
    range_high: 4000,
    weekly_equivalent: 0,
    annual_impact: 2000,
    likelihood: 80,
    negotiable: false,
    refundable: true,
    risk_level: 'low'
  },
  top_up_fee: {
    display_name: 'Top-Up Fee',
    description: 'Additional fee for premium room or location',
    category: 'accommodation',
    frequency: 'weekly',
    estimated_amount: 120,
    range_low: 50,
    range_high: 250,
    weekly_equivalent: 120,
    annual_impact: 6240,
    likelihood: 55,
    negotiable: true,
    risk_level: 'high'
  },
  personal_care_extras: {
    display_name: 'Personal Care Extras',
    description: 'Additional personal care beyond standard package',
    category: 'care',
    frequency: 'weekly',
    estimated_amount: 50,
    range_low: 30,
    range_high: 100,
    weekly_equivalent: 50,
    annual_impact: 2600,
    likelihood: 40,
    negotiable: false,
    risk_level: 'medium'
  },
  laundry_service: {
    display_name: 'Laundry Service',
    description: 'Washing and ironing personal clothing',
    category: 'services',
    frequency: 'weekly',
    estimated_amount: 25,
    range_low: 15,
    range_high: 45,
    weekly_equivalent: 25,
    annual_impact: 1300,
    likelihood: 35,
    negotiable: false,
    included_sometimes: true,
    risk_level: 'low'
  },
  hairdressing: {
    display_name: 'Hairdressing',
    description: 'Hair styling and grooming services',
    category: 'personal',
    frequency: 'monthly',
    estimated_amount: 40,
    range_low: 25,
    range_high: 60,
    weekly_equivalent: 9.23,
    annual_impact: 480,
    likelihood: 90,
    negotiable: false,
    risk_level: 'low'
  },
  chiropody: {
    display_name: 'Chiropody/Podiatry',
    description: 'Foot care services',
    category: 'personal',
    frequency: 'monthly',
    estimated_amount: 40,
    range_low: 30,
    range_high: 50,
    weekly_equivalent: 9.23,
    annual_impact: 480,
    likelihood: 85,
    negotiable: false,
    risk_level: 'low'
  },
  toiletries: {
    display_name: 'Toiletries',
    description: 'Soap, shampoo, toothpaste, etc.',
    category: 'personal',
    frequency: 'weekly',
    estimated_amount: 15,
    range_low: 10,
    range_high: 30,
    weekly_equivalent: 15,
    annual_impact: 780,
    likelihood: 50,
    negotiable: false,
    included_sometimes: true,
    risk_level: 'low'
  },
  newspapers_magazines: {
    display_name: 'Newspapers & Magazines',
    description: 'Daily newspapers and magazine subscriptions',
    category: 'lifestyle',
    frequency: 'weekly',
    estimated_amount: 25,
    range_low: 15,
    range_high: 40,
    weekly_equivalent: 25,
    annual_impact: 1300,
    likelihood: 60,
    negotiable: false,
    risk_level: 'low'
  },
  telephone: {
    display_name: 'Telephone Line',
    description: 'Private telephone line in room',
    category: 'services',
    frequency: 'weekly',
    estimated_amount: 15,
    range_low: 10,
    range_high: 25,
    weekly_equivalent: 15,
    annual_impact: 780,
    likelihood: 70,
    negotiable: false,
    risk_level: 'low'
  },
  tv_license: {
    display_name: 'TV License',
    description: 'BBC TV license fee',
    category: 'services',
    frequency: 'weekly',
    estimated_amount: 3.5,
    range_low: 3,
    range_high: 4,
    weekly_equivalent: 3.5,
    annual_impact: 182,
    likelihood: 95,
    negotiable: false,
    risk_level: 'low'
  },
  outings_transport: {
    display_name: 'Outings & Transport',
    description: 'Trips out and transportation costs',
    category: 'lifestyle',
    frequency: 'monthly',
    estimated_amount: 80,
    range_low: 40,
    range_high: 150,
    weekly_equivalent: 18.48,
    annual_impact: 960,
    likelihood: 75,
    negotiable: false,
    risk_level: 'low'
  }
};

const CARE_TYPE_MODIFIERS: Record<string, number> = {
  residential: 1.0,
  nursing: 1.15,
  dementia: 1.25,
  respite: 1.10
};

const INFLATION_RATE = 0.04;

// Safe number helper
const safeNumber = (value: unknown, defaultValue = 0): number => {
  if (value === null || value === undefined) return defaultValue;
  const num = Number(value);
  return isNaN(num) ? defaultValue : num;
};

// Safe string helper
const safeString = (value: unknown, defaultValue = ''): string => {
  if (value === null || value === undefined) return defaultValue;
  return String(value);
};

export function useCostAnalysis({
  careHomes,
  fundingOptimization,
  region = 'england',
  careType = 'residential'
}: UseCostAnalysisOptions): UseCostAnalysisResult {
  const [costAnalysis, setCostAnalysis] = useState<CostAnalysisData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const calculateHiddenFees = useCallback((home: ProfessionalCareHome): HiddenFeesAnalysis => {
    const weeklyPrice = safeNumber(home?.weeklyPrice, 0);
    const homeId = safeString(home?.id, '');
    const homeName = safeString(home?.name, 'Unknown');
    const careModifier = CARE_TYPE_MODIFIERS[(careType || 'residential').toLowerCase()] || 1.0;
    
    const detectedFees: HiddenFee[] = [];
    const feesByCategory: Record<string, any> = {};
    
    Object.entries(HIDDEN_FEES_DATABASE).forEach(([feeId, feeData]) => {
      const adjustedAmount = Math.round(feeData.estimated_amount * careModifier);
      const adjustedLow = Math.round(feeData.range_low * careModifier);
      const adjustedHigh = Math.round(feeData.range_high * careModifier);
      
      let weeklyEquivalent = 0;
      let annualImpact = 0;
      
      if (feeData.frequency === 'weekly') {
        weeklyEquivalent = adjustedAmount;
        annualImpact = adjustedAmount * 52;
      } else if (feeData.frequency === 'monthly') {
        weeklyEquivalent = adjustedAmount / 4.33;
        annualImpact = adjustedAmount * 12;
      } else if (feeData.frequency === 'one_time') {
        weeklyEquivalent = 0;
        annualImpact = adjustedAmount;
      }
      
      const fee: HiddenFee = {
        fee_id: feeId,
        ...feeData,
        estimated_amount: adjustedAmount,
        range_low: adjustedLow,
        range_high: adjustedHigh,
        weekly_equivalent: Math.round(weeklyEquivalent * 100) / 100,
        annual_impact: Math.round(annualImpact)
      };
      
      detectedFees.push(fee);
      
      const category = feeData.category;
      if (!feesByCategory[category]) {
        feesByCategory[category] = {
          display_name: category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
          fees: [],
          total_weekly: 0,
          total_annual: 0
        };
      }
      feesByCategory[category].fees.push(fee);
      feesByCategory[category].total_weekly += weeklyEquivalent;
      feesByCategory[category].total_annual += annualImpact;
    });
    
    const totalOneTime = detectedFees
      .filter(f => f.frequency === 'one_time')
      .reduce((sum, f) => sum + f.estimated_amount, 0);
    
    const totalWeekly = detectedFees.reduce((sum, f) => sum + f.weekly_equivalent, 0);
    const totalAnnual = detectedFees.reduce((sum, f) => sum + f.annual_impact, 0);
    const hiddenPercent = weeklyPrice > 0 ? (totalWeekly / weeklyPrice) * 100 : 0;
    
    return {
      home_id: homeId,
      home_name: homeName,
      advertised_weekly_price: weeklyPrice,
      care_type: careType || 'residential',
      region: region || 'england',
      detected_fees: detectedFees,
      fees_by_category: feesByCategory,
      summary: {
        total_one_time_fees: totalOneTime,
        total_weekly_hidden: Math.round(totalWeekly * 100) / 100,
        total_annual_hidden: Math.round(totalAnnual),
        hidden_fee_percent: Math.round(hiddenPercent * 10) / 10,
        true_weekly_cost: Math.round((weeklyPrice + totalWeekly) * 100) / 100,
        true_annual_cost: Math.round((weeklyPrice + totalWeekly) * 52),
        first_year_total: Math.round((weeklyPrice + totalWeekly) * 52 + totalOneTime),
        fee_count: detectedFees.length,
        negotiable_fees_count: detectedFees.filter(f => f.negotiable).length,
        potential_negotiation_savings: Math.round(
          detectedFees.filter(f => f.negotiable).reduce((sum, f) => sum + f.annual_impact * 0.3, 0)
        )
      },
      risk_assessment: {
        overall_risk: hiddenPercent > 20 ? 'high' : hiddenPercent > 10 ? 'medium' : 'low',
        transparency_score: Math.max(0, 100 - detectedFees.length * 3),
        predictability_score: Math.max(0, 100 - detectedFees.filter(f => f.frequency === 'per_occurrence').length * 10)
      },
      warnings: hiddenPercent > 15 ? [{
        severity: 'high',
        title: 'High Hidden Fee Risk',
        message: `Estimated hidden fees add ${hiddenPercent.toFixed(1)}% to advertised price`
      }] : [],
      negotiation_tips: [
        { title: 'Request Full Fee Schedule', tip: 'Ask for complete written breakdown before signing' },
        { title: 'Compare Included Services', tip: 'Some homes include services others charge for' }
      ],
      questions_to_ask: [
        'Can you provide a complete written schedule of all charges?',
        'What services are included in the weekly fee?',
        'Are there any one-time fees such as admission or registration fees?'
      ],
      analyzed_at: new Date().toISOString()
    };
  }, [careType, region]);

  const calculateScenarios = useCallback((
    homes: ProfessionalCareHome[],
    hiddenFeesAnalysis: HiddenFeesAnalysis[],
    funding: FundingOptimization | undefined
  ): CostVsFundingScenarios => {
    // Safe extraction with fallbacks
    const chcProbability = safeNumber(funding?.chc_eligibility?.eligibility_probability, 0) / 100;
    const laAvailable = funding?.la_funding?.funding_available ?? false;
    const laContributionPct = safeNumber(funding?.la_funding?.funding_split?.la_contribution_percent, 0) / 100;
    const dpaAvailable = funding?.dpa_considerations?.dpa_eligible ?? false;
    
    const homeScenarios = (homes || []).filter(Boolean).map((home, i) => {
      const hiddenFees = hiddenFeesAnalysis?.[i];
      const weeklyPrice = safeNumber(home?.weeklyPrice, 0);
      const hiddenWeekly = safeNumber(hiddenFees?.summary?.total_weekly_hidden, 0);
      const trueWeekly = weeklyPrice + hiddenWeekly;
      const trueAnnual = trueWeekly * 52;
      
      const scenarios: FundingScenario[] = [];
      
      // Self-funding
      scenarios.push({
        scenario_id: 'self_funding',
        scenario_name: 'Self-Funding',
        description: 'You pay 100% of care costs',
        funding_source: 'Personal savings/assets',
        weekly_cost: trueWeekly,
        annual_cost: trueAnnual,
        five_year_cost: calculate5YearCost(trueWeekly),
        out_of_pocket_weekly: trueWeekly,
        out_of_pocket_annual: trueAnnual,
        funding_coverage_percent: 0,
        probability: 100,
        pros: ['Full choice of care home', 'No means testing required', 'No bureaucracy or delays'],
        cons: ['Highest out-of-pocket cost', 'Assets depleted over time', 'No financial support'],
        color: '#EF4444'
      });
      
      // CHC Funding
      if (chcProbability > 0.1) {
        scenarios.push({
          scenario_id: 'chc_funding',
          scenario_name: 'CHC Funding',
          description: 'NHS covers 100% of care costs',
          funding_source: 'NHS',
          weekly_cost: trueWeekly,
          annual_cost: trueAnnual,
          five_year_cost: 0,
          out_of_pocket_weekly: 0,
          out_of_pocket_annual: 0,
          funding_coverage_percent: 100,
          probability: chcProbability * 100,
          eligibility_level: funding?.chc_eligibility?.eligibility_level,
          pros: ['No personal cost for care', 'NHS pays entire fee', 'Preserves personal assets'],
          cons: ['Strict eligibility criteria', 'Complex application process', 'May limit care home choice'],
          color: '#10B981'
        });
      }
      
      // LA Funding
      if (laAvailable) {
        const laWeekly = laContributionPct * trueWeekly;
        const selfWeekly = trueWeekly - laWeekly;
        scenarios.push({
          scenario_id: 'la_funding',
          scenario_name: 'Local Authority Funding',
          description: `LA contributes ${(laContributionPct * 100).toFixed(0)}%`,
          funding_source: 'Local Authority',
          weekly_cost: trueWeekly,
          annual_cost: trueAnnual,
          five_year_cost: calculate5YearCost(selfWeekly),
          out_of_pocket_weekly: selfWeekly,
          out_of_pocket_annual: selfWeekly * 52,
          la_contribution_weekly: laWeekly,
          la_contribution_annual: laWeekly * 52,
          funding_coverage_percent: laContributionPct * 100,
          probability: 100,
          pros: ['Reduced personal cost', 'Means-tested support', 'Can access care sooner'],
          cons: ['Means testing required', 'May limit care home choice', 'Top-up fees may apply'],
          color: '#3B82F6'
        });
      }
      
      // DPA
      if (dpaAvailable) {
        const interestRate = (funding?.dpa_considerations?.costs?.interest_rate_percent || 2.5) / 100;
        const adminFeeWeekly = funding?.dpa_considerations?.costs?.administration_fee_weekly || 2.77;
        scenarios.push({
          scenario_id: 'dpa',
          scenario_name: 'Deferred Payment',
          description: 'Pay from property value later',
          funding_source: 'Property equity (deferred)',
          weekly_cost: trueWeekly,
          annual_cost: trueAnnual,
          five_year_cost: calculate5YearCost(trueWeekly, true, interestRate),
          out_of_pocket_weekly: adminFeeWeekly,
          out_of_pocket_annual: adminFeeWeekly * 52,
          deferred_weekly: trueWeekly,
          deferred_annual: trueAnnual,
          interest_rate_percent: interestRate * 100,
          funding_coverage_percent: 100,
          probability: 100,
          pros: ['No immediate large payments', 'Stay in care without selling home', 'Interest at reasonable rate'],
          cons: ['Interest accumulates', 'Reduces inheritance', 'Property may need to be sold later'],
          color: '#F59E0B'
        });
      }
      
      return {
        home_id: home.id,
        home_name: home.name,
        advertised_weekly: weeklyPrice,
        hidden_fees_weekly: hiddenWeekly,
        true_weekly_cost: trueWeekly,
        scenarios
      };
    });
    
    const allSelfFunding = homeScenarios.map(h => 
      h.scenarios.find(s => s.scenario_id === 'self_funding')?.five_year_cost || 0
    );
    const allBestCase = homeScenarios.map(h => {
      const viable = h.scenarios.filter(s => s.probability > 50);
      return viable.length > 0 
        ? Math.min(...viable.map(s => s.out_of_pocket_annual * 5))
        : h.scenarios[0]?.out_of_pocket_annual * 5 || 0;
    });
    
    return {
      homes: homeScenarios,
      summary: {
        average_self_funding_5yr: allSelfFunding.reduce((a, b) => a + b, 0) / allSelfFunding.length,
        average_best_case_5yr: allBestCase.reduce((a, b) => a + b, 0) / allBestCase.length,
        potential_5yr_savings: (allSelfFunding.reduce((a, b) => a + b, 0) - allBestCase.reduce((a, b) => a + b, 0)) / allSelfFunding.length,
        average_hidden_fees_weekly: hiddenFeesAnalysis.reduce((a, b) => a + b.summary.total_weekly_hidden, 0) / hiddenFeesAnalysis.length,
        homes_analyzed: homes.length
      },
      funding_context: {
        chc_probability: chcProbability * 100,
        la_available: laAvailable,
        la_contribution_percent: laContributionPct * 100,
        dpa_available: dpaAvailable
      },
      recommendations: [
        ...(chcProbability > 0.5 ? [{
          priority: 'high' as const,
          title: 'Apply for CHC Assessment',
          description: `With ${(chcProbability * 100).toFixed(0)}% eligibility probability, CHC could save significant costs.`,
          action: 'Contact local ICB for CHC assessment'
        }] : []),
        {
          priority: 'medium' as const,
          title: 'Request Full Fee Breakdown',
          description: 'Ask each care home for complete fee schedule including all extras.',
          action: 'Send written request to shortlisted homes'
        }
      ],
      generated_at: new Date().toISOString()
    };
  }, []);

  const calculateEnhancedProjections = useCallback((
    homes: ProfessionalCareHome[],
    hiddenFeesAnalysis: HiddenFeesAnalysis[]
  ): EnhancedProjections => {
    const projections = homes.map((home, i) => {
      const weeklyPrice = home.weeklyPrice || 0;
      const hiddenFees = hiddenFeesAnalysis[i];
      const hiddenWeekly = hiddenFees?.summary.total_weekly_hidden || 0;
      const oneTimeFees = hiddenFees?.summary.total_one_time_fees || 0;
      const trueWeekly = weeklyPrice + hiddenWeekly;
      
      const years = [];
      let cumulativeAdvertised = 0;
      let cumulativeTrue = 0;
      
      for (let year = 1; year <= 5; year++) {
        const inflationFactor = Math.pow(1 + INFLATION_RATE, year - 1);
        let advertisedAnnual = weeklyPrice * 52 * inflationFactor;
        let trueAnnual = trueWeekly * 52 * inflationFactor;
        
        if (year === 1) {
          trueAnnual += oneTimeFees;
        }
        
        cumulativeAdvertised += advertisedAnnual;
        cumulativeTrue += trueAnnual;
        
        years.push({
          year,
          advertised_weekly: Math.round(weeklyPrice * inflationFactor * 100) / 100,
          true_weekly: Math.round(trueWeekly * inflationFactor * 100) / 100,
          hidden_fees_weekly: Math.round(hiddenWeekly * inflationFactor * 100) / 100,
          advertised_annual: Math.round(advertisedAnnual),
          true_annual: Math.round(trueAnnual),
          hidden_fees_annual: Math.round(trueAnnual - advertisedAnnual),
          cumulative_advertised: Math.round(cumulativeAdvertised),
          cumulative_true: Math.round(cumulativeTrue),
          cumulative_hidden: Math.round(cumulativeTrue - cumulativeAdvertised),
          inflation_factor: Math.round(inflationFactor * 10000) / 10000
        });
      }
      
      return {
        home_id: home.id,
        home_name: home.name,
        base_advertised_weekly: weeklyPrice,
        base_true_weekly: Math.round(trueWeekly * 100) / 100,
        one_time_fees: oneTimeFees,
        years,
        summary: {
          total_5_year_advertised: Math.round(cumulativeAdvertised),
          total_5_year_true: Math.round(cumulativeTrue),
          total_5_year_hidden: Math.round(cumulativeTrue - cumulativeAdvertised),
          hidden_fees_percent: cumulativeAdvertised > 0 
            ? Math.round((cumulativeTrue - cumulativeAdvertised) / cumulativeAdvertised * 1000) / 10
            : 0
        }
      };
    });
    
    const totalAdvertised = projections.reduce((a, p) => a + p.summary.total_5_year_advertised, 0);
    const totalTrue = projections.reduce((a, p) => a + p.summary.total_5_year_true, 0);
    
    return {
      projections,
      overall_summary: {
        average_5_year_advertised: Math.round(totalAdvertised / projections.length),
        average_5_year_true: Math.round(totalTrue / projections.length),
        average_hidden_impact: Math.round((totalTrue - totalAdvertised) / projections.length),
        inflation_rate_used: INFLATION_RATE * 100
      }
    };
  }, []);

  const calculateCostAnalysis = useCallback(() => {
    if (careHomes.length === 0) {
      setError('No care homes to analyze');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const hiddenFeesAnalysis = careHomes.map(home => calculateHiddenFees(home));
      const costVsFunding = calculateScenarios(careHomes, hiddenFeesAnalysis, fundingOptimization);
      const enhancedProjections = calculateEnhancedProjections(careHomes, hiddenFeesAnalysis);
      
      const avgHiddenPercent = hiddenFeesAnalysis.reduce((a, h) => a + h.summary.hidden_fee_percent, 0) / hiddenFeesAnalysis.length;
      const avgTrueWeekly = hiddenFeesAnalysis.reduce((a, h) => a + h.summary.true_weekly_cost, 0) / hiddenFeesAnalysis.length;
      
      const executiveSummary: CostAnalysisExecutiveSummary = {
        headline: `True weekly cost averages £${avgTrueWeekly.toFixed(0)} (hidden fees add ${avgHiddenPercent.toFixed(1)}%)`,
        key_findings: [
          ...(avgHiddenPercent > 10 ? [{
            type: 'warning' as const,
            title: 'Significant Hidden Costs Detected',
            detail: `Hidden fees add an average of ${avgHiddenPercent.toFixed(1)}% to advertised prices`
          }] : []),
          ...(costVsFunding.summary.potential_5yr_savings > 10000 ? [{
            type: 'opportunity' as const,
            title: 'Major Savings Potential',
            detail: `Funding options could save up to £${costVsFunding.summary.potential_5yr_savings.toFixed(0)} over 5 years`
          }] : [])
        ],
        average_hidden_fee_percent: avgHiddenPercent,
        average_true_weekly_cost: avgTrueWeekly,
        potential_5_year_savings: costVsFunding.summary.potential_5yr_savings,
        homes_analyzed: careHomes.length
      };
      
      setCostAnalysis({
        hidden_fees_analysis: hiddenFeesAnalysis,
        cost_vs_funding_scenarios: costVsFunding,
        enhanced_projections: enhancedProjections,
        executive_summary: executiveSummary,
        care_type_analyzed: careType,
        region,
        generated_at: new Date().toISOString()
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to calculate cost analysis');
    } finally {
      setIsLoading(false);
    }
  }, [careHomes, fundingOptimization, careType, region, calculateHiddenFees, calculateScenarios, calculateEnhancedProjections]);

  const getHomeAnalysis = useCallback((homeId: string): HiddenFeesAnalysis | null => {
    return costAnalysis?.hidden_fees_analysis.find(h => h.home_id === homeId) || null;
  }, [costAnalysis]);

  const getHomeScenarios = useCallback((homeId: string): FundingScenario[] | null => {
    const home = costAnalysis?.cost_vs_funding_scenarios.homes.find(h => h.home_id === homeId);
    return home?.scenarios || null;
  }, [costAnalysis]);

  const getBestScenario = useCallback((homeId: string): FundingScenario | null => {
    const scenarios = getHomeScenarios(homeId);
    if (!scenarios) return null;
    
    const viable = scenarios.filter(s => s.probability > 50);
    if (viable.length === 0) return scenarios[0] || null;
    
    return viable.reduce((best, current) => 
      current.out_of_pocket_annual < best.out_of_pocket_annual ? current : best
    );
  }, [getHomeScenarios]);

  const getTotalHiddenFees = useCallback((): number => {
    return costAnalysis?.hidden_fees_analysis.reduce((sum, h) => sum + h.summary.total_weekly_hidden, 0) || 0;
  }, [costAnalysis]);

  const getPotentialSavings = useCallback((): number => {
    return costAnalysis?.cost_vs_funding_scenarios.summary.potential_5yr_savings || 0;
  }, [costAnalysis]);

  return {
    costAnalysis,
    isLoading,
    error,
    calculateCostAnalysis,
    getHomeAnalysis,
    getHomeScenarios,
    getBestScenario,
    getTotalHiddenFees,
    getPotentialSavings
  };
}

function calculate5YearCost(
  weeklyAmount: number,
  includeInterest = false,
  interestRate = 0.025
): number {
  let total = 0;
  const annualCost = weeklyAmount * 52;
  
  for (let year = 0; year < 5; year++) {
    const inflationFactor = Math.pow(1 + INFLATION_RATE, year);
    let yearCost = annualCost * inflationFactor;
    
    if (includeInterest) {
      let accumulated = 0;
      for (let y = 0; y <= year; y++) {
        accumulated += annualCost * Math.pow(1 + INFLATION_RATE, y);
      }
      yearCost += accumulated * interestRate;
    }
    
    total += yearCost;
  }
  
  return Math.round(total);
}

export default useCostAnalysis;
