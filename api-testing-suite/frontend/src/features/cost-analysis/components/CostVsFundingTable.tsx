import { useState } from 'react';
import type { CostVsFundingScenarios, FundingScenario, HomeScenarios } from '../types';

interface CostVsFundingTableProps {
  scenarios: CostVsFundingScenarios | null | undefined;
  selectedHomeId?: string;
}

const safeNumber = (value: unknown, defaultValue = 0): number => {
  if (value === null || value === undefined) return defaultValue;
  const num = Number(value);
  return isNaN(num) ? defaultValue : num;
};

export default function CostVsFundingTable({ scenarios, selectedHomeId }: CostVsFundingTableProps) {
  const [expandedScenario, setExpandedScenario] = useState<string | null>(null);
  const [comparisonMode, setComparisonMode] = useState<'weekly' | 'annual' | '5year'>('annual');

  if (!scenarios?.homes || scenarios.homes.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg border border-gray-200 p-4 text-center text-gray-500">
        No funding scenarios available
      </div>
    );
  }

  const selectedHome = selectedHomeId
    ? scenarios.homes.find(h => h?.home_id === selectedHomeId)
    : scenarios.homes[0];

  if (!selectedHome?.scenarios || selectedHome.scenarios.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg border border-gray-200 p-4 text-center text-gray-500">
        No scenarios available for selected home
      </div>
    );
  }

  const fundingContext = scenarios.funding_context || {
    chc_probability: 0,
    la_available: false,
    la_contribution_percent: 0,
    dpa_available: false
  };

  const formatCurrency = (amount: number) => `£${amount.toLocaleString()}`;

  const getScenarioValue = (scenario: FundingScenario) => {
    switch (comparisonMode) {
      case 'weekly': return scenario.out_of_pocket_weekly;
      case 'annual': return scenario.out_of_pocket_annual;
      case '5year': return scenario.five_year_cost;
    }
  };

  const getLabel = () => {
    switch (comparisonMode) {
      case 'weekly': return 'Your Cost/Week';
      case 'annual': return 'Your Cost/Year';
      case '5year': return 'Your 5-Year Cost';
    }
  };

  const sortedScenarios = [...selectedHome.scenarios].sort(
    (a, b) => getScenarioValue(a) - getScenarioValue(b)
  );

  const bestScenario = sortedScenarios[0];
  const worstScenario = sortedScenarios[sortedScenarios.length - 1];
  const potentialSavings = getScenarioValue(worstScenario) - getScenarioValue(bestScenario);

  return (
    <div className="space-y-4">
      {/* Summary Header */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h4 className="font-semibold text-lg text-gray-900">{selectedHome.home_name}</h4>
            <p className="text-sm text-gray-600">
              Advertised: {formatCurrency(selectedHome.advertised_weekly)}/week • 
              True Cost: {formatCurrency(selectedHome.true_weekly_cost)}/week
            </p>
          </div>
          <div className="flex gap-1 bg-white rounded-lg p-1 shadow-sm">
            {(['weekly', 'annual', '5year'] as const).map(mode => (
              <button
                key={mode}
                onClick={() => setComparisonMode(mode)}
                className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${
                  comparisonMode === mode
                    ? 'bg-blue-500 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {mode === 'weekly' ? 'Weekly' : mode === 'annual' ? 'Annual' : '5-Year'}
              </button>
            ))}
          </div>
        </div>

        {/* Savings Highlight */}
        {potentialSavings > 0 && (
          <div className="flex items-center gap-4 bg-white rounded-lg p-3">
            <div className="flex-1">
              <div className="text-sm text-gray-600">Potential Savings</div>
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(potentialSavings)}
              </div>
              <div className="text-xs text-gray-500">
                {bestScenario.scenario_name} vs {worstScenario.scenario_name}
              </div>
            </div>
            {bestScenario.probability < 100 && (
              <div className="text-right">
                <div className="text-xs text-gray-500">Best scenario probability</div>
                <div className="text-lg font-semibold text-blue-600">
                  {bestScenario.probability}%
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Funding Context */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className={`rounded-lg p-3 border ${
          safeNumber(fundingContext.chc_probability) > 50 
            ? 'bg-green-50 border-green-200' 
            : 'bg-gray-50 border-gray-200'
        }`}>
          <div className="text-xs text-gray-600">CHC Eligibility</div>
          <div className={`text-lg font-bold ${
            safeNumber(fundingContext.chc_probability) > 50 ? 'text-green-600' : 'text-gray-700'
          }`}>
            {safeNumber(fundingContext.chc_probability)}%
          </div>
        </div>
        <div className={`rounded-lg p-3 border ${
          fundingContext.la_available 
            ? 'bg-blue-50 border-blue-200' 
            : 'bg-gray-50 border-gray-200'
        }`}>
          <div className="text-xs text-gray-600">LA Funding</div>
          <div className={`text-lg font-bold ${
            fundingContext.la_available ? 'text-blue-600' : 'text-gray-500'
          }`}>
            {fundingContext.la_available 
              ? `${safeNumber(fundingContext.la_contribution_percent)}%` 
              : 'Not Available'}
          </div>
        </div>
        <div className={`rounded-lg p-3 border ${
          fundingContext.dpa_available 
            ? 'bg-amber-50 border-amber-200' 
            : 'bg-gray-50 border-gray-200'
        }`}>
          <div className="text-xs text-gray-600">DPA Option</div>
          <div className={`text-lg font-bold ${
            fundingContext.dpa_available ? 'text-amber-600' : 'text-gray-500'
          }`}>
            {fundingContext.dpa_available ? 'Available' : 'Not Available'}
          </div>
        </div>
        <div className="rounded-lg p-3 border bg-purple-50 border-purple-200">
          <div className="text-xs text-gray-600">Hidden Fees/Week</div>
          <div className="text-lg font-bold text-purple-600">
            +{formatCurrency(safeNumber(selectedHome.hidden_fees_weekly))}
          </div>
        </div>
      </div>

      {/* Scenarios Comparison */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-100">
          <h5 className="font-semibold text-sm text-gray-900">Funding Scenarios Comparison</h5>
          <p className="text-xs text-gray-500 mt-1">Click a scenario to see details</p>
        </div>

        <div className="divide-y divide-gray-100">
          {sortedScenarios.map((scenario, index) => {
            const isExpanded = expandedScenario === scenario.scenario_id;
            const isBest = index === 0 && scenario.out_of_pocket_annual < worstScenario.out_of_pocket_annual;
            const savings = getScenarioValue(worstScenario) - getScenarioValue(scenario);

            return (
              <div key={scenario.scenario_id}>
                <button
                  onClick={() => setExpandedScenario(isExpanded ? null : scenario.scenario_id)}
                  className="w-full px-4 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div 
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: scenario.color }}
                    />
                    <div className="text-left">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-gray-900">{scenario.scenario_name}</span>
                        {isBest && (
                          <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                            Best Option
                          </span>
                        )}
                        {scenario.probability < 100 && (
                          <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                            {scenario.probability}% likely
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-gray-500">{scenario.description}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-lg font-bold text-gray-900">
                        {formatCurrency(getScenarioValue(scenario))}
                      </div>
                      <div className="text-xs text-gray-500">{getLabel()}</div>
                    </div>
                    {savings > 0 && (
                      <div className="text-right">
                        <div className="text-sm font-semibold text-green-600">
                          Save {formatCurrency(savings)}
                        </div>
                      </div>
                    )}
                    <svg
                      className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </button>

                {isExpanded && (
                  <div className="px-4 pb-4 bg-gray-50">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      {/* Cost Breakdown */}
                      <div className="bg-white rounded-lg p-3 border border-gray-200">
                        <h6 className="text-xs font-semibold text-gray-700 mb-2">Cost Breakdown</h6>
                        <div className="space-y-1 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Weekly Cost</span>
                            <span className="font-medium">{formatCurrency(scenario.weekly_cost)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Your Weekly</span>
                            <span className="font-medium">{formatCurrency(scenario.out_of_pocket_weekly)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Your Annual</span>
                            <span className="font-medium">{formatCurrency(scenario.out_of_pocket_annual)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">5-Year Total</span>
                            <span className="font-bold">{formatCurrency(scenario.five_year_cost)}</span>
                          </div>
                          <div className="flex justify-between pt-1 border-t border-gray-200">
                            <span className="text-gray-600">Funding Coverage</span>
                            <span className="font-semibold text-green-600">
                              {scenario.funding_coverage_percent}%
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Pros */}
                      <div className="bg-white rounded-lg p-3 border border-gray-200">
                        <h6 className="text-xs font-semibold text-green-700 mb-2">✓ Pros</h6>
                        <ul className="space-y-1">
                          {(scenario.pros || []).map((pro, i) => (
                            <li key={i} className="text-sm text-gray-600 flex items-start gap-1">
                              <span className="text-green-500">•</span>
                              {pro}
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Cons */}
                      <div className="bg-white rounded-lg p-3 border border-gray-200">
                        <h6 className="text-xs font-semibold text-red-700 mb-2">✗ Cons</h6>
                        <ul className="space-y-1">
                          {(scenario.cons || []).map((con, i) => (
                            <li key={i} className="text-sm text-gray-600 flex items-start gap-1">
                              <span className="text-red-500">•</span>
                              {con}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {/* Additional Details for specific scenarios */}
                    {scenario.scenario_id === 'la_funding' && scenario.la_contribution_weekly && (
                      <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
                        <div className="text-sm">
                          <span className="font-medium text-blue-700">LA Contribution:</span>{' '}
                          <span className="text-blue-600">
                            {formatCurrency(scenario.la_contribution_weekly)}/week 
                            ({formatCurrency(scenario.la_contribution_annual || 0)}/year)
                          </span>
                        </div>
                      </div>
                    )}

                    {scenario.scenario_id === 'dpa' && scenario.interest_rate_percent && (
                      <div className="bg-amber-50 rounded-lg p-3 border border-amber-200">
                        <div className="text-sm">
                          <span className="font-medium text-amber-700">Deferred Amount:</span>{' '}
                          <span className="text-amber-600">
                            {formatCurrency(scenario.deferred_weekly || 0)}/week @ {scenario.interest_rate_percent}% interest
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Recommendations */}
      {(scenarios.recommendations || []).length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h5 className="font-semibold text-sm text-gray-900 mb-3">Recommended Actions</h5>
          <div className="space-y-3">
            {(scenarios.recommendations || []).map((rec, i) => (
              <div
                key={i}
                className={`p-3 rounded-lg border ${
                  rec.priority === 'high'
                    ? 'bg-red-50 border-red-200'
                    : rec.priority === 'medium'
                    ? 'bg-amber-50 border-amber-200'
                    : 'bg-gray-50 border-gray-200'
                }`}
              >
                <div className="flex items-start gap-2">
                  <span className={`text-xs font-medium px-2 py-0.5 rounded ${
                    rec.priority === 'high'
                      ? 'bg-red-100 text-red-700'
                      : rec.priority === 'medium'
                      ? 'bg-amber-100 text-amber-700'
                      : 'bg-gray-200 text-gray-700'
                  }`}>
                    {rec.priority.toUpperCase()}
                  </span>
                  <div>
                    <div className="font-medium text-sm text-gray-900">{rec.title}</div>
                    <div className="text-sm text-gray-600">{rec.description}</div>
                    <div className="text-xs text-blue-600 mt-1 font-medium">
                      Action: {rec.action}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
