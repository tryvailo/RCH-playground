/**
 * Care Type Constants
 */

export const CARE_TYPES = {
  RESIDENTIAL: 'residential',
  NURSING: 'nursing',
  DEMENTIA: 'dementia',
  RESPITE: 'respite',
} as const;

export type CareType = typeof CARE_TYPES[keyof typeof CARE_TYPES];

export const CARE_TYPE_FIELDS: Record<string, string[]> = {
  residential: [
    'fee_residential_from',
    'weekly_cost_residential',
  ],
  nursing: [
    'fee_nursing_from',
    'weekly_cost_nursing',
  ],
  dementia: [
    'fee_dementia_from',
    'fee_dementia_residential_from',
    'fee_dementia_nursing_from',
    'weekly_cost_dementia',
  ],
  respite: [
    'fee_respite_from',
    'weekly_cost_respite',
  ],
};



