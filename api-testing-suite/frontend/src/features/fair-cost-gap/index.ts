/**
 * Fair Cost Gap Module - Public API
 * Экспортирует все публичные компоненты и хуки
 */

export { FairCostGapBlock } from './components/FairCostGapBlock';
export { AnimatedCounter } from './components/AnimatedCounter';
export { useFairCostGap } from './hooks/useFairCostGap';
export { useMSIFStore } from './stores/msifStore';
export { getFairCostLower, preloadMSIFData } from './msifLoader';
export type {
  FairCostGapData,
  FairCostGapResult,
  MSIFData,
  CareType,
} from './types';

