import React, { useState } from 'react';
import { 
  PoundSterling, 
  Heart, 
  Building2, 
  Phone, 
  ExternalLink, 
  CheckCircle2, 
  AlertCircle,
  ChevronDown,
  ChevronUp,
  HelpCircle,
  Calculator,
  Info
} from 'lucide-react';
import type { ProfessionalReportData } from '../types';

interface FundingOptionsSectionProps {
  report: ProfessionalReportData;
  questionnaire?: {
    section_3_medical_needs?: {
      q8_care_types?: string[];
      q9_medical_conditions?: string[];
      q10_mobility_level?: string;
      q11_medication_management?: string;
    };
  };
}

interface CHCEligibility {
  probability: 'High' | 'Medium' | 'Low';
  score: number;
  matchedCriteria: string[];
  weeklyValue: string;
  annualValue: string;
  nextSteps: string[];
}

interface CouncilFunding {
  localAuthorityName: string;
  localAuthorityPhone: string;
  capitalLimit: number;
  lowerLimit: number;
  propertyDisregard: boolean;
  meansTestInfo: string;
  deferredPaymentAvailable: boolean;
  nextSteps: string[];
}

interface AttendanceAllowance {
  higherRate: string;
  lowerRate: string;
  estimatedRate: 'higher' | 'lower';
  annualValue: string;
}

const getProbabilityBadgeStyle = (probability: string) => {
  switch (probability) {
    case 'High':
      return 'bg-green-100 text-green-800 border-green-300';
    case 'Medium':
      return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    default:
      return 'bg-red-100 text-red-800 border-red-300';
  }
};

export default function FundingOptionsSection({ report, questionnaire }: FundingOptionsSectionProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['chc', 'council']));

  const toggleSection = (section: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(section)) {
        newSet.delete(section);
      } else {
        newSet.add(section);
      }
      return newSet;
    });
  };

  // Calculate CHC eligibility based on questionnaire data
  const calculateCHCEligibility = (): CHCEligibility => {
    const medicalNeeds = questionnaire?.section_3_medical_needs;
    let score = 0;
    const matchedCriteria: string[] = [];

    // Dementia/Alzheimer's
    if (medicalNeeds?.q9_medical_conditions?.includes('dementia_alzheimers')) {
      score += 3;
      matchedCriteria.push("Dementia/Alzheimer's diagnosis");
    }

    // Mobility level
    if (medicalNeeds?.q10_mobility_level === 'wheelchair_permanent') {
      score += 2;
      matchedCriteria.push("Permanent wheelchair use");
    }

    // Medication management
    if (medicalNeeds?.q11_medication_management === 'many_complex_routine') {
      score += 2;
      matchedCriteria.push("Complex medication management required");
    }

    // Nursing care type
    if (medicalNeeds?.q8_care_types?.includes('medical_nursing')) {
      score += 2;
      matchedCriteria.push("Medical/Nursing care required");
    }

    // Multiple conditions
    const conditionCount = medicalNeeds?.q9_medical_conditions?.length || 0;
    if (conditionCount >= 3) {
      score += 2;
      matchedCriteria.push(`Multiple health conditions (${conditionCount})`);
    }

    // Heart conditions
    if (medicalNeeds?.q9_medical_conditions?.includes('heart_conditions')) {
      score += 1;
      matchedCriteria.push("Heart condition requiring monitoring");
    }

    // Diabetes
    if (medicalNeeds?.q9_medical_conditions?.includes('diabetes')) {
      score += 1;
      matchedCriteria.push("Diabetes requiring management");
    }

    let probability: 'High' | 'Medium' | 'Low';
    if (score >= 6) {
      probability = 'High';
    } else if (score >= 3) {
      probability = 'Medium';
    } else {
      probability = 'Low';
    }

    return {
      probability,
      score,
      matchedCriteria,
      weeklyValue: '£500-1,500',
      annualValue: 'Up to £78,000',
      nextSteps: [
        'Request CHC checklist from GP or hospital discharge team',
        'Complete the Decision Support Tool (DST)',
        'Attend multidisciplinary assessment meeting',
        'Appeal if initially rejected (40% succeed on appeal)'
      ]
    };
  };

  // Get council funding info (using report data if available)
  const getCouncilFunding = (): CouncilFunding => {
    const localAuthority = report.fairCostGapAnalysis?.local_authority || report.city;
    
    return {
      localAuthorityName: localAuthority || 'Your Local Council',
      localAuthorityPhone: report.fairCostGapAnalysis?.local_authority_info?.contact_note || 'Contact via council website',
      capitalLimit: 23250,
      lowerLimit: 14250,
      propertyDisregard: true,
      meansTestInfo: 'If your capital (savings and assets) is above £23,250, you will need to self-fund. Between £14,250 and £23,250, you may receive partial funding.',
      deferredPaymentAvailable: true,
      nextSteps: [
        `Contact ${localAuthority || 'your local council'} Adult Social Care team`,
        'Request a Care Needs Assessment',
        'Complete Financial Assessment form',
        'Ask about 12-week property disregard if applicable',
        'Enquire about Deferred Payment Agreement if selling property'
      ]
    };
  };

  const getAttendanceAllowance = (): AttendanceAllowance => {
    const hasSevereCare = questionnaire?.section_3_medical_needs?.q10_mobility_level === 'wheelchair_permanent' ||
                          questionnaire?.section_3_medical_needs?.q11_medication_management === 'many_complex_routine';
    
    return {
      higherRate: '£101.75',
      lowerRate: '£68.10',
      estimatedRate: hasSevereCare ? 'higher' : 'lower',
      annualValue: hasSevereCare ? '£5,291' : '£3,541'
    };
  };

  const chc = calculateCHCEligibility();
  const council = getCouncilFunding();
  const attendance = getAttendanceAllowance();

  // Calculate total potential funding
  const minWeekly = parseFloat(attendance.lowerRate.replace('£', ''));
  const maxWeekly = parseFloat(chc.weeklyValue.split('-')[1].replace('£', '').replace(',', '')) + 
                    parseFloat(attendance.higherRate.replace('£', ''));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-gradient-to-br from-green-100 to-emerald-100 rounded-full flex items-center justify-center">
          <PoundSterling className="w-5 h-5 text-green-600" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-900">Funding Options</h3>
          <p className="text-sm text-gray-600">What help is available to pay for care?</p>
        </div>
      </div>

      {/* Total Potential Funding Summary */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-5 border-2 border-green-200">
        <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Calculator className="w-5 h-5 text-green-600" />
          Total Potential Funding Available
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4 border border-green-200">
            <div className="text-sm text-gray-600 mb-1">Weekly (Low Estimate)</div>
            <div className="text-2xl font-bold text-green-700">£{minWeekly.toFixed(2)}</div>
          </div>
          <div className="bg-white rounded-lg p-4 border border-green-200">
            <div className="text-sm text-gray-600 mb-1">Weekly (High Estimate)</div>
            <div className="text-2xl font-bold text-green-700">Up to £{maxWeekly.toLocaleString()}</div>
          </div>
          <div className="bg-white rounded-lg p-4 border border-green-200">
            <div className="text-sm text-gray-600 mb-1">Annual (Max Potential)</div>
            <div className="text-2xl font-bold text-green-700">£{(maxWeekly * 52).toLocaleString()}</div>
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-3 flex items-start gap-1">
          <Info className="w-3 h-3 mt-0.5 flex-shrink-0" />
          Estimates based on your care needs profile. Actual amounts depend on assessment outcomes.
        </p>
      </div>

      {/* NHS Continuing Healthcare (CHC) */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <button
          onClick={() => toggleSection('chc')}
          className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <Heart className="w-5 h-5 text-blue-600" />
            </div>
            <div className="text-left">
              <h4 className="font-semibold text-gray-900">NHS Continuing Healthcare (CHC)</h4>
              <p className="text-sm text-gray-500">Free NHS funding for complex health needs</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${getProbabilityBadgeStyle(chc.probability)}`}>
              {chc.probability} Eligibility
            </span>
            {expandedSections.has('chc') ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </div>
        </button>

        {expandedSections.has('chc') && (
          <div className="p-4 pt-0 border-t border-gray-100">
            {/* Value Cards */}
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
                <div className="text-xs text-blue-600 mb-1">Weekly Value</div>
                <div className="text-xl font-bold text-blue-800">{chc.weeklyValue}</div>
              </div>
              <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
                <div className="text-xs text-blue-600 mb-1">Annual Value</div>
                <div className="text-xl font-bold text-blue-800">{chc.annualValue}</div>
              </div>
            </div>

            {/* Matched Criteria */}
            {chc.matchedCriteria.length > 0 && (
              <div className="mb-4">
                <h5 className="text-sm font-semibold text-gray-900 mb-2">Your Qualifying Factors:</h5>
                <div className="space-y-2">
                  {chc.matchedCriteria.map((criteria, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-sm">
                      <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
                      <span className="text-gray-700">{criteria}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {chc.matchedCriteria.length === 0 && (
              <div className="mb-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                <div className="flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-yellow-800">
                    Based on your profile, CHC eligibility appears limited. However, you should still request a checklist assessment as circumstances can change.
                  </p>
                </div>
              </div>
            )}

            {/* Next Steps */}
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h5 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <HelpCircle className="w-4 h-4 text-blue-600" />
                How to Apply for CHC
              </h5>
              <ol className="space-y-2">
                {chc.nextSteps.map((step, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm">
                    <span className="w-5 h-5 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-semibold text-blue-700">
                      {idx + 1}
                    </span>
                    <span className="text-gray-700">{step}</span>
                  </li>
                ))}
              </ol>
            </div>
          </div>
        )}
      </div>

      {/* Council Funding */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <button
          onClick={() => toggleSection('council')}
          className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
              <Building2 className="w-5 h-5 text-purple-600" />
            </div>
            <div className="text-left">
              <h4 className="font-semibold text-gray-900">Local Authority Funding</h4>
              <p className="text-sm text-gray-500">{council.localAuthorityName}</p>
            </div>
          </div>
          {expandedSections.has('council') ? (
            <ChevronUp className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          )}
        </button>

        {expandedSections.has('council') && (
          <div className="p-4 pt-0 border-t border-gray-100">
            {/* Capital Thresholds */}
            <div className="mb-4">
              <h5 className="text-sm font-semibold text-gray-900 mb-3">Means Test Thresholds (2024/25)</h5>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-purple-50 rounded-lg p-3 border border-purple-200">
                  <div className="text-xs text-purple-600 mb-1">Upper Capital Limit</div>
                  <div className="text-xl font-bold text-purple-800">£{council.capitalLimit.toLocaleString()}</div>
                  <div className="text-xs text-gray-500 mt-1">Above = Self-fund</div>
                </div>
                <div className="bg-purple-50 rounded-lg p-3 border border-purple-200">
                  <div className="text-xs text-purple-600 mb-1">Lower Capital Limit</div>
                  <div className="text-xl font-bold text-purple-800">£{council.lowerLimit.toLocaleString()}</div>
                  <div className="text-xs text-gray-500 mt-1">Below = Full support</div>
                </div>
              </div>
            </div>

            {/* Means Test Info */}
            <div className="mb-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
              <p className="text-sm text-gray-700">{council.meansTestInfo}</p>
            </div>

            {/* Special Schemes */}
            <div className="mb-4 grid grid-cols-2 gap-3">
              <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg border border-green-200">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                <div>
                  <div className="text-sm font-semibold text-gray-900">12-Week Property Disregard</div>
                  <div className="text-xs text-gray-500">Property ignored initially</div>
                </div>
              </div>
              <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg border border-green-200">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                <div>
                  <div className="text-sm font-semibold text-gray-900">Deferred Payment</div>
                  <div className="text-xs text-gray-500">Pay after property sale</div>
                </div>
              </div>
            </div>

            {/* Contact & Next Steps */}
            <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
              <h5 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Phone className="w-4 h-4 text-purple-600" />
                Contact {council.localAuthorityName}
              </h5>
              <p className="text-sm text-gray-600 mb-3">{council.localAuthorityPhone}</p>
              <ol className="space-y-2">
                {council.nextSteps.slice(0, 3).map((step, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm">
                    <span className="w-5 h-5 bg-purple-200 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-semibold text-purple-700">
                      {idx + 1}
                    </span>
                    <span className="text-gray-700">{step}</span>
                  </li>
                ))}
              </ol>
            </div>
          </div>
        )}
      </div>

      {/* Attendance Allowance */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <button
          onClick={() => toggleSection('attendance')}
          className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
              <PoundSterling className="w-5 h-5 text-orange-600" />
            </div>
            <div className="text-left">
              <h4 className="font-semibold text-gray-900">Attendance Allowance</h4>
              <p className="text-sm text-gray-500">Tax-free benefit for care needs (65+)</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="px-3 py-1 rounded-full text-sm font-semibold border bg-orange-100 text-orange-800 border-orange-300">
              {attendance.estimatedRate === 'higher' ? 'Higher Rate' : 'Lower Rate'} Likely
            </span>
            {expandedSections.has('attendance') ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </div>
        </button>

        {expandedSections.has('attendance') && (
          <div className="p-4 pt-0 border-t border-gray-100">
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className={`rounded-lg p-3 border ${attendance.estimatedRate === 'higher' ? 'bg-orange-100 border-orange-300' : 'bg-gray-50 border-gray-200'}`}>
                <div className="text-xs text-gray-600 mb-1">Higher Rate (Weekly)</div>
                <div className={`text-xl font-bold ${attendance.estimatedRate === 'higher' ? 'text-orange-800' : 'text-gray-600'}`}>
                  {attendance.higherRate}
                </div>
                <div className="text-xs text-gray-500 mt-1">Day & night care needed</div>
              </div>
              <div className={`rounded-lg p-3 border ${attendance.estimatedRate === 'lower' ? 'bg-orange-100 border-orange-300' : 'bg-gray-50 border-gray-200'}`}>
                <div className="text-xs text-gray-600 mb-1">Lower Rate (Weekly)</div>
                <div className={`text-xl font-bold ${attendance.estimatedRate === 'lower' ? 'text-orange-800' : 'text-gray-600'}`}>
                  {attendance.lowerRate}
                </div>
                <div className="text-xs text-gray-500 mt-1">Day or night care needed</div>
              </div>
            </div>

            <div className="p-3 bg-orange-50 rounded-lg border border-orange-200">
              <p className="text-sm text-gray-700">
                <span className="font-semibold">Annual Value:</span> Up to {attendance.annualValue}/year. 
                Not means-tested — you can receive it regardless of savings or income.
              </p>
            </div>

            <div className="mt-4">
              <a
                href="https://www.gov.uk/attendance-allowance"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm text-orange-700 hover:text-orange-800 font-medium"
              >
                <ExternalLink className="w-4 h-4" />
                Apply on GOV.UK
              </a>
            </div>
          </div>
        )}
      </div>

      {/* Disclaimer */}
      <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-xs text-gray-500 leading-relaxed">
          <strong>Important:</strong> Funding eligibility depends on individual circumstances and assessments by NHS and local authority teams. 
          This guidance is for informational purposes only. We recommend seeking professional financial advice for complex situations. 
          Rates shown are 2024/25 figures and may change.
        </p>
      </div>
    </div>
  );
}
