// Cost Analysis Types

export interface HiddenFee {
  fee_id: string;
  display_name: string;
  description: string;
  category: string;
  frequency: 'one_time' | 'weekly' | 'monthly' | 'annual_percent' | 'per_occurrence';
  estimated_amount: number;
  range_low: number;
  range_high: number;
  weekly_equivalent: number;
  annual_impact: number;
  likelihood: number;
  negotiable: boolean;
  refundable?: boolean;
  included_sometimes?: boolean;
  risk_level: 'high' | 'medium' | 'low';
}

export interface FeeCategory {
  display_name: string;
  description: string;
  icon: string;
  fees: HiddenFee[];
  total_weekly: number;
  total_annual: number;
}

export interface HiddenFeesSummary {
  total_one_time_fees: number;
  total_weekly_hidden: number;
  total_annual_hidden: number;
  hidden_fee_percent: number;
  true_weekly_cost: number;
  true_annual_cost: number;
  first_year_total: number;
  fee_count: number;
  negotiable_fees_count: number;
  potential_negotiation_savings: number;
}

export interface RiskAssessmentCost {
  overall_risk: 'high' | 'medium' | 'low';
  transparency_score: number;
  predictability_score: number;
}

export interface FeeWarning {
  severity: 'high' | 'medium' | 'low';
  title: string;
  message: string;
}

export interface NegotiationTip {
  title: string;
  tip: string;
}

export interface HiddenFeesAnalysis {
  home_id: string;
  home_name: string;
  advertised_weekly_price: number;
  care_type: string;
  region: string;
  detected_fees: HiddenFee[];
  fees_by_category: Record<string, FeeCategory>;
  summary: HiddenFeesSummary;
  risk_assessment: RiskAssessmentCost;
  warnings: FeeWarning[];
  negotiation_tips: NegotiationTip[];
  questions_to_ask: string[];
  analyzed_at: string;
}

// Cost vs Funding Scenarios
export interface FundingScenario {
  scenario_id: 'self_funding' | 'chc_funding' | 'la_funding' | 'dpa' | 'hybrid';
  scenario_name: string;
  description: string;
  funding_source: string;
  weekly_cost: number;
  annual_cost: number;
  five_year_cost: number;
  out_of_pocket_weekly: number;
  out_of_pocket_annual: number;
  funding_coverage_percent: number;
  probability: number;
  eligibility_level?: string;
  la_contribution_weekly?: number;
  la_contribution_annual?: number;
  deferred_weekly?: number;
  deferred_annual?: number;
  interest_rate_percent?: number;
  pros: string[];
  cons: string[];
  color: string;
}

export interface HomeScenarios {
  home_id: string;
  home_name: string;
  advertised_weekly: number;
  hidden_fees_weekly: number;
  true_weekly_cost: number;
  scenarios: FundingScenario[];
}

export interface FundingContext {
  chc_probability: number;
  la_available: boolean;
  la_contribution_percent: number;
  dpa_available: boolean;
}

export interface FundingRecommendation {
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  action: string;
}

export interface CostVsFundingScenarios {
  homes: HomeScenarios[];
  summary: {
    average_self_funding_5yr: number;
    average_best_case_5yr: number;
    potential_5yr_savings: number;
    average_hidden_fees_weekly: number;
    homes_analyzed: number;
  };
  funding_context: FundingContext;
  recommendations: FundingRecommendation[];
  generated_at: string;
}

// Enhanced Projections
export interface YearProjectionEnhanced {
  year: number;
  advertised_weekly: number;
  true_weekly: number;
  hidden_fees_weekly: number;
  advertised_annual: number;
  true_annual: number;
  hidden_fees_annual: number;
  cumulative_advertised: number;
  cumulative_true: number;
  cumulative_hidden: number;
  inflation_factor: number;
}

export interface HomeProjectionEnhanced {
  home_id: string;
  home_name: string;
  base_advertised_weekly: number;
  base_true_weekly: number;
  one_time_fees: number;
  years: YearProjectionEnhanced[];
  summary: {
    total_5_year_advertised: number;
    total_5_year_true: number;
    total_5_year_hidden: number;
    hidden_fees_percent: number;
  };
}

export interface EnhancedProjections {
  projections: HomeProjectionEnhanced[];
  overall_summary: {
    average_5_year_advertised: number;
    average_5_year_true: number;
    average_hidden_impact: number;
    inflation_rate_used: number;
  };
}

// Executive Summary
export interface KeyFinding {
  type: 'warning' | 'opportunity' | 'info';
  title: string;
  detail: string;
}

export interface CostAnalysisExecutiveSummary {
  headline: string;
  key_findings: KeyFinding[];
  average_hidden_fee_percent: number;
  average_true_weekly_cost: number;
  potential_5_year_savings: number;
  homes_analyzed: number;
}

// Main Cost Analysis Response
export interface CostAnalysisData {
  hidden_fees_analysis: HiddenFeesAnalysis[];
  cost_vs_funding_scenarios: CostVsFundingScenarios;
  enhanced_projections: EnhancedProjections;
  executive_summary: CostAnalysisExecutiveSummary;
  care_type_analyzed: string;
  region: string;
  generated_at: string;
}
