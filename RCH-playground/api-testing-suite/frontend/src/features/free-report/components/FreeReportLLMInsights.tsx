import React from 'react';
import { Lightbulb, CheckCircle2, AlertTriangle, Info } from 'lucide-react';

interface HomeInsight {
  home_name: string;
  match_type: 'Safe Bet' | 'Best Value' | 'Premium';
  why_selected: string;
  key_strengths: string[];
  considerations?: string[];
}

interface LLMInsights {
  generated_at: string;
  method: string;
  insights: {
    overall_explanation: {
      summary: string;
      key_findings: string[];
      confidence_level: string;
    };
    home_insights: HomeInsight[];
  };
}

interface FreeReportLLMInsightsProps {
  llmInsights: LLMInsights;
}

const getMatchTypeColor = (matchType: string) => {
  switch (matchType) {
    case 'Safe Bet':
      return 'bg-blue-100 text-blue-800 border-blue-200';
    case 'Best Value':
      return 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]/20';
    case 'Premium':
      return 'bg-purple-100 text-purple-800 border-purple-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

const getConfidenceColor = (confidence: string) => {
  switch (confidence?.toLowerCase()) {
    case 'high':
      return 'bg-green-100 text-green-800';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800';
    case 'low':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export default function FreeReportLLMInsights({ llmInsights }: FreeReportLLMInsightsProps) {
  if (!llmInsights || !llmInsights.insights) {
    return null;
  }

  const { overall_explanation, home_insights } = llmInsights.insights;

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-[#10B981]/10 rounded-lg">
          <Lightbulb className="w-6 h-6 text-[#10B981]" />
        </div>
        <div>
          <h3 className="text-2xl font-bold text-gray-900">AI-Powered Insights</h3>
          <p className="text-sm text-gray-600">
            Expert analysis of why each home was selected for you
          </p>
        </div>
      </div>

      {/* Overall Explanation */}
      {overall_explanation && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 mb-6 border border-blue-100">
          <div className="flex items-start gap-3 mb-4">
            <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="text-lg font-semibold text-gray-900 mb-2">Overall Analysis</h4>
              <p className="text-gray-700 leading-relaxed mb-4">{overall_explanation.summary}</p>
              
              {overall_explanation.key_findings && overall_explanation.key_findings.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm font-semibold text-gray-700">Key Findings:</span>
                    {overall_explanation.confidence_level && (
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getConfidenceColor(overall_explanation.confidence_level)}`}>
                        {overall_explanation.confidence_level.toUpperCase()} Confidence
                      </span>
                    )}
                  </div>
                  <ul className="space-y-2">
                    {overall_explanation.key_findings.map((finding, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-gray-700">
                        <CheckCircle2 className="w-4 h-4 text-[#10B981] flex-shrink-0 mt-0.5" />
                        <span className="text-sm">{finding}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Home Insights */}
      {home_insights && home_insights.length > 0 && (
        <div className="space-y-6">
          <h4 className="text-xl font-semibold text-gray-900 mb-4">Why Each Home Was Selected</h4>
          
          {home_insights.map((insight, idx) => (
            <div
              key={idx}
              className="border-2 border-gray-200 rounded-lg p-6 hover:border-[#10B981]/30 transition-colors"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h5 className="text-lg font-bold text-gray-900 mb-2">{insight.home_name}</h5>
                  <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold border ${getMatchTypeColor(insight.match_type)}`}>
                    {insight.match_type}
                  </span>
                </div>
              </div>

              {/* Why Selected */}
              {insight.why_selected && (
                <div className="mb-4">
                  <h6 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                    <Lightbulb className="w-4 h-4 text-[#10B981]" />
                    Why This Home
                  </h6>
                  <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                    {insight.why_selected}
                  </p>
                </div>
              )}

              {/* Key Strengths */}
              {insight.key_strengths && insight.key_strengths.length > 0 && (
                <div className="mb-4">
                  <h6 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-[#10B981]" />
                    Key Strengths
                  </h6>
                  <ul className="space-y-2">
                    {insight.key_strengths.map((strength, strengthIdx) => (
                      <li key={strengthIdx} className="flex items-start gap-2 text-gray-700">
                        <CheckCircle2 className="w-4 h-4 text-[#10B981] flex-shrink-0 mt-0.5" />
                        <span className="text-sm">{strength}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Considerations */}
              {insight.considerations && insight.considerations.length > 0 && (
                <div>
                  <h6 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-yellow-600" />
                    Considerations
                  </h6>
                  <ul className="space-y-2">
                    {insight.considerations.map((consideration, considerationIdx) => (
                      <li key={considerationIdx} className="flex items-start gap-2 text-gray-600">
                        <AlertTriangle className="w-4 h-4 text-yellow-600 flex-shrink-0 mt-0.5" />
                        <span className="text-sm">{consideration}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Method indicator */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          Analysis method: {llmInsights.method || 'data_driven_analysis'} • 
          Generated: {llmInsights.generated_at ? new Date(llmInsights.generated_at).toLocaleString() : 'N/A'}
        </p>
      </div>
    </div>
  );
}



