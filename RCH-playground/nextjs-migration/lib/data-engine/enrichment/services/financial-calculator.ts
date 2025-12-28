/**
 * Financial Calculator
 * Calculates Altman Z-score and bankruptcy risk from Companies House data
 */

import { AccountsData, CompanyProfile, FilingHistory } from './companies-house-client';

export interface FinancialMetrics {
  revenue?: number;
  totalAssets?: number;
  workingCapital?: number;
  retainedEarnings?: number;
  ebit?: number; // Earnings Before Interest and Taxes
  marketValue?: number;
  totalLiabilities?: number;
  shareholdersFunds?: number;
}

export interface FinancialAnalysis {
  altmanZScore: number | null;
  bankruptcyRisk: number; // 0-1, where 1 = highest risk
  financialHealth: 'safe' | 'gray' | 'distress';
  threeYearSummary?: {
    revenueTrend: 'growing' | 'stable' | 'declining';
    revenueGrowthRate?: number;
    profitabilityTrend: 'improving' | 'stable' | 'declining';
    netMargin3yrAvg?: number;
    workingCapitalTrend: 'improving' | 'stable' | 'declining';
    currentRatio3yrAvg?: number;
  };
  redFlags: string[];
}

/**
 * UK Care Home Industry Benchmarks
 */
const UK_CARE_HOME_BENCHMARKS = {
  revenue_growth_3yr_avg: 0.05, // 5% average annual growth
  net_margin_avg: 0.12, // 12% average net margin
  current_ratio_avg: 1.5, // 1.5 average current ratio
  debt_to_equity_avg: 0.6, // 0.6 average debt-to-equity
  working_capital_avg: 0.15, // 15% of revenue average
  altman_z_safe: 2.99, // Safe zone threshold
  altman_z_gray: 1.81, // Gray zone threshold
};

/**
 * Calculate Altman Z-score for UK companies
 * 
 * Altman Z-score formula (UK version):
 * Z = 1.2X1 + 1.4X2 + 3.3X3 + 0.6X4 + 1.0X5
 * 
 * Where:
 * X1 = Working Capital / Total Assets
 * X2 = Retained Earnings / Total Assets
 * X3 = EBIT / Total Assets
 * X4 = Market Value of Equity / Total Liabilities
 * X5 = Sales / Total Assets
 */
export function calculateAltmanZScore(metrics: FinancialMetrics): number | null {
  const {
    workingCapital = 0,
    totalAssets = 0,
    retainedEarnings = 0,
    ebit = 0,
    marketValue = 0,
    totalLiabilities = 0,
    revenue = 0,
  } = metrics;

  // Need total assets for calculation
  if (totalAssets <= 0) {
    return null;
  }

  // X1: Working Capital / Total Assets
  const x1 = workingCapital / totalAssets;

  // X2: Retained Earnings / Total Assets
  const x2 = retainedEarnings / totalAssets;

  // X3: EBIT / Total Assets
  const x3 = ebit / totalAssets;

  // X4: Market Value of Equity / Total Liabilities
  // If market value not available, use shareholders funds as proxy
  const equityValue = marketValue > 0 ? marketValue : metrics.shareholdersFunds || 0;
  const x4 = totalLiabilities > 0 ? equityValue / totalLiabilities : 0;

  // X5: Sales / Total Assets
  const x5 = revenue / totalAssets;

  // Calculate Z-score
  const zScore = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5;

  return zScore;
}

/**
 * Calculate bankruptcy risk from Altman Z-score
 */
export function calculateBankruptcyRisk(zScore: number | null): number {
  if (zScore === null) {
    return 0.5; // Unknown risk
  }

  // Risk mapping based on Z-score zones
  if (zScore >= UK_CARE_HOME_BENCHMARKS.altman_z_safe) {
    // Safe zone (>2.99)
    return 0.05; // 5% risk
  } else if (zScore >= UK_CARE_HOME_BENCHMARKS.altman_z_gray) {
    // Gray zone (1.81-2.99)
    return 0.3; // 30% risk
  } else {
    // Distress zone (<1.81)
    return 0.7; // 70% risk
  }
}

/**
 * Determine financial health category
 */
export function determineFinancialHealth(zScore: number | null): FinancialAnalysis['financialHealth'] {
  if (zScore === null) {
    return 'gray';
  }

  if (zScore >= UK_CARE_HOME_BENCHMARKS.altman_z_safe) {
    return 'safe';
  } else if (zScore >= UK_CARE_HOME_BENCHMARKS.altman_z_gray) {
    return 'gray';
  } else {
    return 'distress';
  }
}

/**
 * Extract financial metrics from Companies House data
 */
export function extractFinancialMetrics(
  accounts: AccountsData | null,
  profile: CompanyProfile | null
): FinancialMetrics {
  if (!accounts || !accounts.accounts) {
    return {};
  }

  const balanceSheet = accounts.accounts.balance_sheet;
  const profitLoss = accounts.accounts.profit_and_loss;
  const otherAccounts = accounts.accounts.other_accounts;

  // Revenue (turnover)
  const revenue = profitLoss?.turnover || 0;

  // Total Assets
  const totalAssets =
    balanceSheet?.total_assets_less_current_liabilities ||
    otherAccounts?.total_assets ||
    profitLoss?.total_assets ||
    0;

  // Working Capital = Current Assets - Current Liabilities
  const currentAssets = balanceSheet?.current_assets?.total_current_assets || 0;
  const currentLiabilities =
    balanceSheet?.creditors_amounts_falling_due_within_one_year || 0;
  const workingCapital = currentAssets - currentLiabilities;

  // Retained Earnings (approximation from net assets)
  const retainedEarnings = balanceSheet?.total_net_assets || otherAccounts?.shareholders_funds || 0;

  // EBIT (Earnings Before Interest and Taxes)
  // Approximation: Profit before tax
  const ebit = profitLoss?.profit_or_loss_before_tax || 0;

  // Total Liabilities
  const totalLiabilities = otherAccounts?.total_liabilities || 0;

  // Shareholders Funds
  const shareholdersFunds = otherAccounts?.shareholders_funds || balanceSheet?.total_net_assets || 0;

  return {
    revenue,
    totalAssets,
    workingCapital,
    retainedEarnings,
    ebit,
    totalLiabilities,
    shareholdersFunds,
  };
}

/**
 * Analyze financial data and generate comprehensive analysis
 */
export function analyzeFinancialData(
  accounts: AccountsData | null,
  profile: CompanyProfile | null,
  filingHistory: FilingHistory | null
): FinancialAnalysis {
  const metrics = extractFinancialMetrics(accounts, profile);
  const zScore = calculateAltmanZScore(metrics);
  const bankruptcyRisk = calculateBankruptcyRisk(zScore);
  const financialHealth = determineFinancialHealth(zScore);

  // Detect red flags
  const redFlags: string[] = [];

  if (zScore !== null && zScore < UK_CARE_HOME_BENCHMARKS.altman_z_gray) {
    redFlags.push('Low Altman Z-score indicates financial distress');
  }

  if (metrics.totalAssets && metrics.totalLiabilities) {
    const debtToEquity = metrics.totalLiabilities / (metrics.shareholdersFunds || 1);
    if (debtToEquity > 1.0) {
      redFlags.push('High debt-to-equity ratio');
    }
  }

  if (metrics.workingCapital && metrics.workingCapital < 0) {
    redFlags.push('Negative working capital');
  }

  if (metrics.ebit && metrics.ebit < 0) {
    redFlags.push('Negative EBIT (operating losses)');
  }

  // Check filing history for concerning patterns
  if (filingHistory) {
    const recentFilings = filingHistory.items
      .filter((item) => {
        const filingDate = new Date(item.date);
        const oneYearAgo = new Date();
        oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
        return filingDate > oneYearAgo;
      })
      .map((item) => item.type);

    if (recentFilings.includes('liquidation')) {
      redFlags.push('Recent liquidation filing');
    }
    if (recentFilings.includes('insolvency')) {
      redFlags.push('Recent insolvency filing');
    }
  }

  return {
    altmanZScore: zScore,
    bankruptcyRisk,
    financialHealth,
    redFlags,
  };
}



