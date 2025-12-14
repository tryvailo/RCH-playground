import { useState, useEffect } from 'react';
import HiddenFeesDetector from './HiddenFeesDetector';
import CostProjectionChart from './CostProjectionChart';
import CostVsFundingTable from './CostVsFundingTable';
import { useCostAnalysis } from '../hooks/useCostAnalysis';
import type { ProfessionalCareHome, FundingOptimization } from '../../professional-report/types';
import type { CostAnalysisData } from '../types';

interface CostAnalysisBlockProps {
  careHomes: ProfessionalCareHome[];
  fundingOptimization?: FundingOptimization;
  region?: string;
  careType?: string;
  preCalculatedData?: CostAnalysisData;
}

type TabId = 'overview' | 'hidden-fees' | 'projections' | 'scenarios';

export default function CostAnalysisBlock({
  careHomes,
  fundingOptimization,
  region = 'england',
  careType = 'residential',
  preCalculatedData
}: CostAnalysisBlockProps) {
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [selectedHomeId, setSelectedHomeId] = useState<string | null>(null);

  const {
    costAnalysis,
    isLoading,
    error,
    calculateCostAnalysis
  } = useCostAnalysis({
    careHomes,
    fundingOptimization,
    region,
    careType
  });

  const data = preCalculatedData || costAnalysis;

  useEffect(() => {
    if (!preCalculatedData && careHomes.length > 0) {
      calculateCostAnalysis();
    }
  }, [careHomes, fundingOptimization, preCalculatedData, calculateCostAnalysis]);

  useEffect(() => {
    if (careHomes.length > 0 && !selectedHomeId) {
      setSelectedHomeId(careHomes[0].id);
    }
  }, [careHomes, selectedHomeId]);

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-8">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
          <span className="ml-3 text-gray-600">Analyzing costs...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 rounded-xl border border-red-200 p-6">
        <div className="flex items-center gap-2 text-red-700">
          <span className="text-xl">⚠️</span>
          <span>Error: {error}</span>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-gray-50 rounded-xl border border-gray-200 p-8 text-center">
        <div className="text-gray-500">
          <span className="text-2xl mb-2 block">📊</span>
          <p>No cost analysis data available</p>
          {careHomes.length === 0 && (
            <p className="text-sm mt-1">Add care homes to generate analysis</p>
          )}
        </div>
      </div>
    );
  }

  const executiveSummary = data.executive_summary || {
    average_true_weekly_cost: 0,
    average_hidden_fee_percent: 0,
    headline: 'Cost analysis pending',
    key_findings: [],
    homes_analyzed: 0,
    potential_5_year_savings: 0
  };

  const tabs: { id: TabId; label: string; icon: string }[] = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'hidden-fees', label: 'Hidden Fees', icon: '🔍' },
    { id: 'projections', label: '5-Year Projection', icon: '📈' },
    { id: 'scenarios', label: 'Funding Scenarios', icon: '💰' }
  ];

  const formatCurrency = (amount: number) => `£${amount.toLocaleString()}`;

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-white">Cost Analysis</h3>
            <p className="text-indigo-100 text-sm">
              Hidden fees, projections & funding scenarios
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-white">
              {formatCurrency(executiveSummary.average_true_weekly_cost)}/week
            </div>
            <div className="text-indigo-100 text-sm">
              True average cost (+{executiveSummary.average_hidden_fee_percent}% hidden)
            </div>
          </div>
        </div>
      </div>

      {/* Executive Summary */}
      <div className="bg-gradient-to-b from-indigo-50 to-white px-6 py-4 border-b border-gray-200">
        <div className="text-center mb-4">
          <p className="text-lg text-gray-700">{executiveSummary.headline}</p>
        </div>
        
        {(executiveSummary.key_findings || []).length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {(executiveSummary.key_findings || []).map((finding, i) => (
              <div
                key={i}
                className={`p-3 rounded-lg border ${
                  finding.type === 'warning'
                    ? 'bg-amber-50 border-amber-200'
                    : finding.type === 'opportunity'
                    ? 'bg-green-50 border-green-200'
                    : 'bg-blue-50 border-blue-200'
                }`}
              >
                <div className="flex items-start gap-2">
                  <span className="text-lg">
                    {finding.type === 'warning' ? '⚠️' : finding.type === 'opportunity' ? '💡' : 'ℹ️'}
                  </span>
                  <div>
                    <div className={`font-semibold text-sm ${
                      finding.type === 'warning'
                        ? 'text-amber-800'
                        : finding.type === 'opportunity'
                        ? 'text-green-800'
                        : 'text-blue-800'
                    }`}>
                      {finding.title}
                    </div>
                    <div className="text-sm text-gray-600">{finding.detail}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-6 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-indigo-600 text-indigo-600 bg-indigo-50'
                  : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <span>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Home Selector (for multi-home views) */}
      {careHomes.length > 1 && activeTab !== 'overview' && (
        <div className="px-6 py-3 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-600">Select Care Home:</span>
            <select
              value={selectedHomeId || ''}
              onChange={(e) => setSelectedHomeId(e.target.value)}
              className="flex-1 max-w-xs px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              {careHomes.map(home => (
                <option key={home.id} value={home.id}>
                  {home.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <OverviewTab
            data={data}
            careHomes={careHomes}
            onSelectHome={(id) => {
              setSelectedHomeId(id);
              setActiveTab('hidden-fees');
            }}
          />
        )}

        {activeTab === 'hidden-fees' && selectedHomeId && (
          <div className="space-y-6">
            {(() => {
              const filtered = (data.hidden_fees_analysis || []).filter(h => h?.home_id === selectedHomeId);
              if (filtered.length === 0) {
                return (
                  <div className="bg-gray-50 rounded-lg border border-gray-200 p-4 text-center text-gray-500">
                    No hidden fees analysis available for selected home
                  </div>
                );
              }
              return filtered.map(analysis => (
                <HiddenFeesDetector key={analysis.home_id} analysis={analysis} />
              ));
            })()}
          </div>
        )}

        {activeTab === 'projections' && (
          <CostProjectionChart
            projections={data.enhanced_projections}
            selectedHomeId={selectedHomeId || undefined}
          />
        )}

        {activeTab === 'scenarios' && (
          <CostVsFundingTable
            scenarios={data.cost_vs_funding_scenarios}
            selectedHomeId={selectedHomeId || undefined}
          />
        )}
      </div>
    </div>
  );
}

// Overview Tab Component
interface OverviewTabProps {
  data: CostAnalysisData;
  careHomes: ProfessionalCareHome[];
  onSelectHome: (id: string) => void;
}

function OverviewTab({ data, careHomes, onSelectHome }: OverviewTabProps) {
  const formatCurrency = (amount: number) => `£${(amount || 0).toLocaleString()}`;
  
  const costScenarios = data.cost_vs_funding_scenarios || { summary: {}, funding_context: {} };
  const scenariosSummary = costScenarios.summary || {};
  const fundingContext = costScenarios.funding_context || {};
  const executiveSummary = data.executive_summary || {};
  const hiddenFeesAnalysis = data.hidden_fees_analysis || [];
  const enhancedProjections = data.enhanced_projections || { projections: [] };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-4 border border-red-200">
          <div className="text-sm text-red-600 mb-1">Avg Hidden Fees/Week</div>
          <div className="text-2xl font-bold text-red-700">
            +{formatCurrency(scenariosSummary.average_hidden_fees_weekly || 0)}
          </div>
        </div>
        <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-lg p-4 border border-amber-200">
          <div className="text-sm text-amber-600 mb-1">Hidden Fee Impact</div>
          <div className="text-2xl font-bold text-amber-700">
            +{executiveSummary.average_hidden_fee_percent || 0}%
          </div>
        </div>
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
          <div className="text-sm text-green-600 mb-1">Potential 5-Year Savings</div>
          <div className="text-2xl font-bold text-green-700">
            {formatCurrency(scenariosSummary.potential_5yr_savings || 0)}
          </div>
        </div>
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
          <div className="text-sm text-blue-600 mb-1">Homes Analyzed</div>
          <div className="text-2xl font-bold text-blue-700">
            {executiveSummary.homes_analyzed || 0}
          </div>
        </div>
      </div>

      {/* Quick Comparison Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-100">
          <h4 className="font-semibold text-gray-900">Care Homes Quick Comparison</h4>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Care Home</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">Advertised</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">Hidden Fees</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">True Cost</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">5-Year Total</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">Risk</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {hiddenFeesAnalysis.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-gray-500">
                    No care homes to display
                  </td>
                </tr>
              ) : (
                hiddenFeesAnalysis.filter(Boolean).map(analysis => {
                  const summary = analysis.summary || {};
                  const riskAssessment = analysis.risk_assessment || { overall_risk: 'low' };
                  const projection = (enhancedProjections.projections || []).find(p => p?.home_id === analysis.home_id);
                  
                  return (
                    <tr key={analysis.home_id} className="hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium text-gray-900">
                        {analysis.home_name || 'Unknown'}
                      </td>
                      <td className="text-right py-3 px-4 text-gray-600">
                        {formatCurrency(analysis.advertised_weekly_price || 0)}/wk
                      </td>
                      <td className="text-right py-3 px-4 text-amber-600 font-medium">
                        +{formatCurrency(summary.total_weekly_hidden || 0)}/wk
                      </td>
                      <td className="text-right py-3 px-4 font-bold text-gray-900">
                        {formatCurrency(summary.true_weekly_cost || 0)}/wk
                      </td>
                      <td className="text-right py-3 px-4 text-gray-700">
                        {formatCurrency(projection?.summary?.total_5_year_true || 0)}
                      </td>
                      <td className="text-center py-3 px-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          riskAssessment.overall_risk === 'high'
                            ? 'bg-red-100 text-red-700'
                            : riskAssessment.overall_risk === 'medium'
                            ? 'bg-amber-100 text-amber-700'
                            : 'bg-green-100 text-green-700'
                        }`}>
                          {(riskAssessment.overall_risk || 'low').toUpperCase()}
                        </span>
                      </td>
                      <td className="text-center py-3 px-4">
                        <button
                          onClick={() => onSelectHome(analysis.home_id)}
                          className="text-indigo-600 hover:text-indigo-800 font-medium"
                        >
                          View →
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Funding Options Summary */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-4 border border-indigo-200">
        <h4 className="font-semibold text-indigo-900 mb-3">Funding Options Available</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className={`p-3 rounded-lg ${
            (fundingContext.chc_probability || 0) > 50
              ? 'bg-green-100 border border-green-200'
              : 'bg-white border border-gray-200'
          }`}>
            <div className="font-medium text-sm">CHC Funding</div>
            <div className={`text-lg font-bold ${
              (fundingContext.chc_probability || 0) > 50
                ? 'text-green-600'
                : 'text-gray-600'
            }`}>
              {fundingContext.chc_probability || 0}% likely
            </div>
          </div>
          <div className={`p-3 rounded-lg ${
            fundingContext.la_available
              ? 'bg-blue-100 border border-blue-200'
              : 'bg-white border border-gray-200'
          }`}>
            <div className="font-medium text-sm">LA Funding</div>
            <div className={`text-lg font-bold ${
              fundingContext.la_available
                ? 'text-blue-600'
                : 'text-gray-500'
            }`}>
              {fundingContext.la_available
                ? `${fundingContext.la_contribution_percent || 0}% contribution`
                : 'Not Available'}
            </div>
          </div>
          <div className={`p-3 rounded-lg ${
            fundingContext.dpa_available
              ? 'bg-amber-100 border border-amber-200'
              : 'bg-white border border-gray-200'
          }`}>
            <div className="font-medium text-sm">DPA Option</div>
            <div className={`text-lg font-bold ${
              fundingContext.dpa_available
                ? 'text-amber-600'
                : 'text-gray-500'
            }`}>
              {fundingContext.dpa_available
                ? 'Available'
                : 'Not Available'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
