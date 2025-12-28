/**
 * Free Report
 * Main exports
 */

export { FreeReportGenerator } from './generator';
export { FreeReportMatchingService, getFreeReportMatchingService } from './matching-service';
export { FairCostGapService, getFairCostGapService } from './fair-cost-gap';

export type {
  FreeReportRequest,
  FreeReportResponse,
  FreeReportCareHome,
  FairCostGap,
  MatchedHomes,
} from './types';



