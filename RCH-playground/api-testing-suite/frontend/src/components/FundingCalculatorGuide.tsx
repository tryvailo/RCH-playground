import { useState } from 'react';
import { HelpCircle, ChevronDown, ChevronUp, BookOpen, Info, TrendingUp, DollarSign, Shield, Heart, AlertCircle } from 'lucide-react';

export default function FundingCalculatorGuide() {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev);
      if (next.has(sectionId)) {
        next.delete(sectionId);
      } else {
        next.add(sectionId);
      }
      return next;
    });
  };

  const isExpanded = (sectionId: string) => expandedSections.has(sectionId);

  return (
    <div className="bg-white rounded-lg shadow p-6 space-y-4">
      <div className="flex items-center gap-3 mb-6">
        <BookOpen className="w-6 h-6 text-blue-600" />
        <h2 className="text-2xl font-bold text-gray-900">How the Funding Calculator Works</h2>
      </div>

      <p className="text-gray-700 mb-6">
        This guide explains how the Funding Eligibility Calculator works and how to interpret your results. 
        Understanding these concepts will help you make informed decisions about care home funding.
      </p>

      {/* Overview Section */}
      <div className="border border-gray-200 rounded-lg">
        <button
          onClick={() => toggleSection('overview')}
          className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <Info className="w-5 h-5 text-blue-600" />
            <span className="font-semibold text-gray-900">Overview: What This Calculator Does</span>
          </div>
          {isExpanded('overview') ? (
            <ChevronUp className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          )}
        </button>
        {isExpanded('overview') && (
          <div className="p-4 pt-0 border-t border-gray-200 space-y-3 text-sm text-gray-700">
            <p>
              The Funding Eligibility Calculator assesses your potential eligibility for three main types of funding:
            </p>
            <ul className="list-disc list-inside ml-4 space-y-2">
              <li>
                <strong>NHS Continuing Healthcare (CHC):</strong> Fully funded healthcare for individuals with primary health needs. 
                If eligible, the NHS covers 100% of care costs.
              </li>
              <li>
                <strong>Local Authority (LA) Support:</strong> Means-tested financial support from your local council. 
                The amount depends on your income, capital assets, and property.
              </li>
              <li>
                <strong>Deferred Payment Agreement (DPA):</strong> Option to defer care costs using your property as security. 
                Allows you to stay in your home while care costs are paid later.
              </li>
            </ul>
            <p>
              The calculator uses the official NHS Decision Support Tool (DST) 2025 framework and UK means test regulations 
              (2025-2026) to provide accurate estimates.
            </p>
          </div>
        )}
      </div>

      {/* DST Domains Section */}
      <div className="border border-gray-200 rounded-lg">
        <button
          onClick={() => toggleSection('domains')}
          className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <Heart className="w-5 h-5 text-red-600" />
            <span className="font-semibold text-gray-900">Understanding the 12 DST Domains</span>
          </div>
          {isExpanded('domains') ? (
            <ChevronUp className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          )}
        </button>
        {isExpanded('domains') && (
          <div className="p-4 pt-0 border-t border-gray-200 space-y-4 text-sm text-gray-700">
            <p>
              The NHS uses 12 care domains to assess CHC eligibility. Each domain is assessed at different levels:
            </p>
            <div className="bg-blue-50 rounded-lg p-3 mb-3">
              <p className="font-semibold text-blue-900 mb-2">Domain Levels (from lowest to highest):</p>
              <ul className="space-y-1 text-blue-800">
                <li><strong>No Needs:</strong> No care needs in this area</li>
                <li><strong>Low:</strong> Minor care needs</li>
                <li><strong>Moderate:</strong> Some care needs requiring support</li>
                <li><strong>High:</strong> Significant care needs</li>
                <li><strong>Severe:</strong> Very significant care needs</li>
                <li><strong>Priority:</strong> Critical care needs requiring immediate attention</li>
              </ul>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {[
                {
                  domain: 'Breathing',
                  desc: 'Respiratory needs, breathing difficulties, oxygen requirements',
                  example: 'Chronic obstructive pulmonary disease (COPD), asthma, respiratory failure'
                },
                {
                  domain: 'Nutrition',
                  desc: 'Eating and nutritional needs, swallowing difficulties',
                  example: 'Dysphagia, weight loss, tube feeding requirements'
                },
                {
                  domain: 'Continence',
                  desc: 'Bladder and bowel management needs',
                  example: 'Incontinence, catheter care, bowel management'
                },
                {
                  domain: 'Skin Integrity',
                  desc: 'Pressure care and skin health needs',
                  example: 'Pressure sores, wound care, risk of skin breakdown'
                },
                {
                  domain: 'Mobility',
                  desc: 'Movement and positioning needs',
                  example: 'Wheelchair use, bedbound, falls risk, transfers'
                },
                {
                  domain: 'Communication',
                  desc: 'Speech and communication needs',
                  example: 'Speech difficulties, hearing loss, communication aids'
                },
                {
                  domain: 'Psychological',
                  desc: 'Emotional and mental health needs',
                  example: 'Anxiety, depression, emotional support needs'
                },
                {
                  domain: 'Cognition',
                  desc: 'Memory and mental capacity needs',
                  example: 'Dementia, memory loss, confusion, decision-making capacity'
                },
                {
                  domain: 'Behaviour',
                  desc: 'Challenging behaviours',
                  example: 'Aggression, wandering, agitation, behavioural support'
                },
                {
                  domain: 'Drug Therapies',
                  desc: 'Medication and drug therapy needs',
                  example: 'Complex medication regimes, injections, IV therapy'
                },
                {
                  domain: 'Altered States',
                  desc: 'Consciousness changes',
                  example: 'Seizures, unconsciousness, altered awareness'
                },
                {
                  domain: 'Other Needs',
                  desc: 'Other significant care needs',
                  example: 'Specialist care, complex conditions, multiple needs'
                },
              ].map(({ domain, desc, example }) => (
                <div key={domain} className="border border-gray-200 rounded p-3">
                  <h4 className="font-semibold text-gray-900 mb-1">{domain}</h4>
                  <p className="text-gray-600 text-xs mb-2">{desc}</p>
                  <p className="text-gray-500 text-xs italic">Example: {example}</p>
                </div>
              ))}
            </div>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mt-3">
              <p className="text-yellow-800 text-xs">
                <strong>💡 Tip:</strong> Be honest and accurate when assessing each domain. Higher levels (Severe, Priority) 
                significantly increase CHC eligibility probability. If unsure, consult with healthcare professionals.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* CHC Results Section */}
      <div className="border border-gray-200 rounded-lg">
        <button
          onClick={() => toggleSection('chc')}
          className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <Shield className="w-5 h-5 text-green-600" />
            <span className="font-semibold text-gray-900">Understanding CHC Eligibility Results</span>
          </div>
          {isExpanded('chc') ? (
            <ChevronUp className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          )}
        </button>
        {isExpanded('chc') && (
          <div className="p-4 pt-0 border-t border-gray-200 space-y-3 text-sm text-gray-700">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-semibold text-green-900 mb-2">CHC Probability Percentage</h4>
              <p className="text-green-800 mb-3">
                This shows your estimated likelihood of being eligible for NHS Continuing Healthcare funding.
              </p>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-600 rounded-full"></div>
                  <span><strong>92-98% (Very High):</strong> Very likely eligible. Strongly recommended to apply.</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span><strong>82-91% (High):</strong> Likely eligible. Recommended to apply.</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <span><strong>70-81% (Moderate):</strong> Possibly eligible. Worth applying, but outcome uncertain.</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <span><strong>0-69% (Low):</strong> Unlikely eligible, but you can still apply if circumstances change.</span>
                </div>
              </div>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Domain Scores</h4>
              <p className="mb-2">
                Shows how each domain contributes to your CHC probability:
              </p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li><strong>Priority domains:</strong> +45% each (critical needs)</li>
                <li><strong>Severe domains:</strong> +20% each (very significant needs)</li>
                <li><strong>High domains:</strong> +9% each (significant needs)</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Bonuses Applied</h4>
              <p className="mb-2">
                Additional factors that increase your probability:
              </p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li><strong>Multiple Severe:</strong> +25% (2+ Severe domains in critical areas)</li>
                <li><strong>Unpredictability:</strong> +15% (unpredictable or fluctuating needs)</li>
                <li><strong>Multiple High:</strong> +10% (3+ High domains in behavioural areas)</li>
                <li><strong>Complex Therapies:</strong> +8% (PEG feeding, tracheostomy, ventilator, dialysis)</li>
              </ul>
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-blue-800 text-xs">
                <strong>📋 Next Steps:</strong> If your probability is 70% or higher, contact your local Integrated Care Board (ICB) 
                to request a CHC assessment. The assessment is free and can result in 100% funding of care costs.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* LA Support Results Section */}
      <div className="border border-gray-200 rounded-lg">
        <button
          onClick={() => toggleSection('la')}
          className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <DollarSign className="w-5 h-5 text-blue-600" />
            <span className="font-semibold text-gray-900">Understanding Local Authority Support Results</span>
          </div>
          {isExpanded('la') ? (
            <ChevronUp className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          )}
        </button>
        {isExpanded('la') && (
          <div className="p-4 pt-0 border-t border-gray-200 space-y-3 text-sm text-gray-700">
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Means Test Explained</h4>
              <p className="mb-3">
                Local Authority funding is based on a "means test" that assesses your financial situation:
              </p>
              <div className="bg-gray-50 rounded-lg p-3 space-y-2">
                <div>
                  <strong>Capital Assets:</strong> Your savings, investments, and other assets (excluding your main home in most cases)
                </div>
                <div>
                  <strong>Weekly Income:</strong> Your pensions, benefits, and other regular income
                </div>
                <div>
                  <strong>Property:</strong> Your main home (may be disregarded in certain circumstances)
                </div>
              </div>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Funding Thresholds (2025-2026)</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                  <div className="font-semibold text-green-900 mb-1">Below £14,250</div>
                  <div className="text-green-800 text-xs">Fully funded by Local Authority. No contribution required.</div>
                </div>
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                  <div className="font-semibold text-yellow-900 mb-1">£14,250 - £23,250</div>
                  <div className="text-yellow-800 text-xs">Partial funding. You contribute based on income and tariff income.</div>
                </div>
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                  <div className="font-semibold text-red-900 mb-1">Above £23,250</div>
                  <div className="text-red-800 text-xs">Self-funding. No LA support available until capital reduces.</div>
                </div>
              </div>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Means Test Breakdown</h4>
              <p className="mb-2">The breakdown shows:</p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li><strong>Raw Capital Assets:</strong> Your total assets before disregards</li>
                <li><strong>Asset Disregards:</strong> Assets that are not counted (personal possessions, life insurance, etc.)</li>
                <li><strong>Adjusted Capital Assets:</strong> Assets that count towards the means test</li>
                <li><strong>Tariff Income:</strong> Assumed income from capital (£1/week per £250 above £14,250)</li>
                <li><strong>Weekly Contribution:</strong> How much you would need to pay per week</li>
              </ul>
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-blue-800 text-xs">
                <strong>📋 Next Steps:</strong> Contact your Local Authority's Adult Social Care team to request a care needs 
                assessment and financial assessment. They will calculate your exact contribution based on your circumstances.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* DPA Section */}
      <div className="border border-gray-200 rounded-lg">
        <button
          onClick={() => toggleSection('dpa')}
          className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <TrendingUp className="w-5 h-5 text-purple-600" />
            <span className="font-semibold text-gray-900">Understanding Deferred Payment Agreement (DPA)</span>
          </div>
          {isExpanded('dpa') ? (
            <ChevronUp className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          )}
        </button>
        {isExpanded('dpa') && (
          <div className="p-4 pt-0 border-t border-gray-200 space-y-3 text-sm text-gray-700">
            <p>
              A Deferred Payment Agreement allows you to delay paying for care costs by using your property as security. 
              This means you don't need to sell your home immediately.
            </p>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">DPA Eligibility Requirements:</h4>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>You need permanent residential care (not temporary)</li>
                <li>Your property value exceeds £23,250</li>
                <li>Your non-property capital is below £23,250</li>
                <li>No qualifying relative lives in the property</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">How DPA Works:</h4>
              <ol className="list-decimal list-inside ml-4 space-y-1">
                <li>Local Authority pays your care costs</li>
                <li>Costs accumulate as a loan secured against your property</li>
                <li>You pay interest on the loan (typically around 2.5% per year)</li>
                <li>Loan is repaid when property is sold (usually after your death)</li>
              </ol>
            </div>
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
              <p className="text-purple-800 text-xs">
                <strong>💡 Benefit:</strong> DPA allows you to keep your home while receiving care, and your family can 
                inherit the property (minus the deferred amount) after your death.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Savings Section */}
      <div className="border border-gray-200 rounded-lg">
        <button
          onClick={() => toggleSection('savings')}
          className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <TrendingUp className="w-5 h-5 text-green-600" />
            <span className="font-semibold text-gray-900">Understanding Potential Savings</span>
          </div>
          {isExpanded('savings') ? (
            <ChevronUp className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          )}
        </button>
        {isExpanded('savings') && (
          <div className="p-4 pt-0 border-t border-gray-200 space-y-3 text-sm text-gray-700">
            <p>
              The savings calculation shows potential financial benefits from different funding options:
            </p>
            <div className="space-y-3">
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">CHC Savings</h4>
                <p>
                  If you're eligible for CHC funding, the NHS covers 100% of care costs. This means:
                </p>
                <ul className="list-disc list-inside ml-4 space-y-1 mt-2">
                  <li>No weekly care fees</li>
                  <li>No contribution from your income or assets</li>
                  <li>Potential savings of thousands of pounds per year</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">LA Top-up Savings</h4>
                <p>
                  If Local Authority funding is available, you may pay less than the full care home fee. 
                  The savings depend on:
                </p>
                <ul className="list-disc list-inside ml-4 space-y-1 mt-2">
                  <li>Your capital assets (lower assets = more support)</li>
                  <li>Your weekly income</li>
                  <li>The gap between LA funding and care home fees</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Time Periods</h4>
                <ul className="list-disc list-inside ml-4 space-y-1">
                  <li><strong>Weekly Savings:</strong> Amount saved per week</li>
                  <li><strong>Annual Savings:</strong> Total savings over 52 weeks</li>
                  <li><strong>5-Year Savings:</strong> Projected savings over 5 years (with inflation)</li>
                  <li><strong>Lifetime Estimate:</strong> Estimated total savings (assumes 10-year average)</li>
                </ul>
              </div>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-3">
              <p className="text-green-800 text-xs">
                <strong>💰 Remember:</strong> These are estimates based on current thresholds and your input. 
                Actual savings depend on official assessments and may change over time.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Income & Asset Disregards Section */}
      <div className="border border-gray-200 rounded-lg">
        <button
          onClick={() => toggleSection('disregards')}
          className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <Info className="w-5 h-5 text-orange-600" />
            <span className="font-semibold text-gray-900">Understanding Income & Asset Disregards</span>
          </div>
          {isExpanded('disregards') ? (
            <ChevronUp className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          )}
        </button>
        {isExpanded('disregards') && (
          <div className="p-4 pt-0 border-t border-gray-200 space-y-3 text-sm text-gray-700">
            <p>
              Certain income and assets are "disregarded" (not counted) in means test calculations. 
              This can significantly reduce your assessed contribution.
            </p>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Fully Disregarded Income:</h4>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li><strong>DLA Mobility Component:</strong> Always fully disregarded</li>
                <li><strong>PIP Mobility Component:</strong> Always fully disregarded</li>
                <li><strong>War Disablement Pension:</strong> Always fully disregarded</li>
                <li><strong>Earnings from Employment:</strong> Always fully disregarded</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Partially Disregarded Income:</h4>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li><strong>Attendance Allowance:</strong> Included but Disability-Related Expenditure (DRE) deductions apply</li>
                <li><strong>PIP Daily Living Component:</strong> Included but DRE deductions may apply</li>
                <li><strong>DLA Care Component:</strong> Included but DRE deductions apply</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Fully Disregarded Assets:</h4>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li><strong>Personal Possessions:</strong> Furniture, clothing, jewelry (unless purchased to reduce capital)</li>
                <li><strong>Life Insurance Surrender Value:</strong> Not counted in means test</li>
                <li><strong>Business Assets:</strong> Disregarded while being disposed of</li>
                <li><strong>Property (in certain cases):</strong> If qualifying relative lives there, or during 12-week disregard period</li>
              </ul>
            </div>
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
              <p className="text-orange-800 text-xs">
                <strong>💡 Important:</strong> Make sure to include all disregards in the calculator to get an accurate assessment. 
                Missing disregards can make you appear wealthier than you actually are for means test purposes.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Next Steps Section */}
      <div className="border border-gray-200 rounded-lg">
        <button
          onClick={() => toggleSection('next-steps')}
          className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-blue-600" />
            <span className="font-semibold text-gray-900">What to Do Next</span>
          </div>
          {isExpanded('next-steps') ? (
            <ChevronUp className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          )}
        </button>
        {isExpanded('next-steps') && (
          <div className="p-4 pt-0 border-t border-gray-200 space-y-4 text-sm text-gray-700">
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">1. For CHC Eligibility (if probability ≥70%):</h4>
              <ol className="list-decimal list-inside ml-4 space-y-1">
                <li>Contact your local Integrated Care Board (ICB) to request a CHC assessment</li>
                <li>Gather medical evidence and reports supporting your health needs</li>
                <li>Complete the Decision Support Tool (DST) assessment with healthcare professionals</li>
                <li>If approved, CHC funding covers 100% of care costs</li>
                <li>You can appeal if the decision is negative</li>
              </ol>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">2. For Local Authority Support:</h4>
              <ol className="list-decimal list-inside ml-4 space-y-1">
                <li>Contact your Local Authority's Adult Social Care team</li>
                <li>Request a care needs assessment (free and legally required)</li>
                <li>Complete a financial assessment (means test)</li>
                <li>Provide documentation of income, assets, and disregards</li>
                <li>Receive your personal budget and contribution amount</li>
              </ol>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">3. For Deferred Payment Agreement:</h4>
              <ol className="list-decimal list-inside ml-4 space-y-1">
                <li>Contact your Local Authority to discuss DPA eligibility</li>
                <li>Provide property valuation and ownership documents</li>
                <li>Sign the DPA agreement (legal document)</li>
                <li>Care costs are deferred and secured against your property</li>
                <li>Interest accrues on the deferred amount</li>
              </ol>
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-blue-800 text-xs">
                <strong>📞 Need Help?</strong> Contact RightCareHome support at support@rightcarehome.co.uk or consult 
                your local Citizens Advice for free guidance on funding applications.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Important Notes */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div className="space-y-2 text-sm text-amber-800">
            <p className="font-semibold">Important Notes:</p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>This calculator provides <strong>estimates only</strong>. Actual eligibility is determined by official NHS and Local Authority assessments.</li>
              <li>Results should <strong>not be considered as guarantees</strong> or official decisions.</li>
              <li>Always seek <strong>professional advice</strong> from qualified advisors for important financial and care decisions.</li>
              <li>Use this tool as part of a <strong>comprehensive assessment process</strong>, not as the sole basis for decisions.</li>
              <li>Thresholds and regulations may change. This calculator uses 2025-2026 thresholds.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

