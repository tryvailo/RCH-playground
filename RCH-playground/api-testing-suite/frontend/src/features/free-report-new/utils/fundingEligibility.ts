/**
 * Funding Eligibility calculation utilities
 * Generates funding eligibility data based on questionnaire
 */

import type { QuestionnaireResponse, FundingEligibility } from '../types';

/**
 * Calculate funding eligibility based on questionnaire
 * Uses chc_probability to determine CHC and LA probabilities
 * 
 * @param questionnaire - User questionnaire with chc_probability
 * @returns FundingEligibility object with calculated probabilities
 */
export const calculateFundingEligibility = (
  questionnaire: QuestionnaireResponse
): FundingEligibility => {
  const chcProb = questionnaire.chc_probability || 35;
  
  // CHC probability range based on questionnaire
  let chcRange: string;
  let chcSavings: string;
  
  if (chcProb >= 75) {
    chcRange = '75-90%';
    chcSavings = '£78,000-£130,000/year';
  } else if (chcProb >= 50) {
    chcRange = '50-75%';
    chcSavings = '£52,000-£78,000/year';
  } else if (chcProb >= 25) {
    chcRange = '25-50%';
    chcSavings = '£26,000-£52,000/year';
  } else {
    chcRange = '10-25%';
    chcSavings = '£10,000-£26,000/year';
  }

  // LA funding probability (typically 60-80% for most applicants)
  // Formula: 50% base + 0.4 * chc_probability, capped at 95%
  const laProb = Math.min(95, 50 + (chcProb * 0.4));
  
  // DPA probability (usually high if property owner)
  const dpaProb = 85;

  return {
    chc: {
      probability_range: chcRange,
      savings_range: chcSavings,
    },
    la: {
      probability: `${Math.round(laProb)}%`,
      savings_range: '£20,000-£50,000/year',
    },
    dpa: {
      probability: `${dpaProb}%`,
      cash_flow_relief: '£2,000+/week deferred',
    },
  };
};


