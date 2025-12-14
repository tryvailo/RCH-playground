// Cost Analysis Module - Public API

// Components
export { default as CostAnalysisBlock } from './components/CostAnalysisBlock';
export { default as HiddenFeesDetector } from './components/HiddenFeesDetector';
export { default as CostProjectionChart } from './components/CostProjectionChart';
export { default as CostVsFundingTable } from './components/CostVsFundingTable';

// Hooks
export { useCostAnalysis } from './hooks/useCostAnalysis';

// Types
export type {
  CostAnalysisData,
  HiddenFeesAnalysis,
  HiddenFee,
  FeeCategory,
  HiddenFeesSummary,
  RiskAssessmentCost,
  FeeWarning,
  NegotiationTip,
  CostVsFundingScenarios,
  HomeScenarios,
  FundingScenario,
  FundingContext,
  FundingRecommendation,
  EnhancedProjections,
  HomeProjectionEnhanced,
  YearProjectionEnhanced,
  CostAnalysisExecutiveSummary,
  KeyFinding
} from './types';
