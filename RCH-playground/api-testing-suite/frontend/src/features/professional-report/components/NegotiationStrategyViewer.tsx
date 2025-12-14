import React, { useState } from 'react';
import { DollarSign, FileText, Mail, HelpCircle, TrendingUp, CheckCircle2, AlertTriangle, Copy, Check } from 'lucide-react';
import type { NegotiationStrategy } from '../types';

interface NegotiationStrategyViewerProps {
  strategy: NegotiationStrategy;
}

export default function NegotiationStrategyViewer({ strategy }: NegotiationStrategyViewerProps) {
  const [copiedTemplate, setCopiedTemplate] = useState<string | null>(null);

  const copyToClipboard = (text: string, templateType: string) => {
    navigator.clipboard.writeText(text);
    setCopiedTemplate(templateType);
    setTimeout(() => setCopiedTemplate(null), 2000);
  };

  const getNegotiationPotentialColor = (potential: string) => {
    switch (potential) {
      case 'high':
        return 'text-green-700 bg-green-50 border-green-200';
      case 'medium':
        return 'text-yellow-700 bg-yellow-50 border-yellow-200';
      case 'low':
        return 'text-gray-700 bg-gray-50 border-gray-200';
      default:
        return 'text-gray-700 bg-gray-50 border-gray-200';
    }
  };

  const getPositioningColor = (positioning: string) => {
    if (positioning.includes('Premium') || positioning.includes('Above')) {
      return 'text-purple-700';
    } else if (positioning.includes('Market')) {
      return 'text-blue-700';
    } else if (positioning.includes('Below') || positioning.includes('Budget')) {
      return 'text-green-700';
    }
    return 'text-gray-700';
  };

  return (
    <div className="space-y-6">
      {/* Market Rate Analysis */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h4 className="text-sm font-semibold text-gray-900 mb-4 flex items-center">
          <TrendingUp className="w-4 h-4 mr-2 text-blue-600" />
          Market Rate Analysis
        </h4>
        
        {/* Market Averages */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
            <div className="text-xs text-gray-500 mb-1">UK Average</div>
            <div className="font-semibold text-gray-900 text-lg">
              £{strategy.market_rate_analysis.uk_average_weekly.toLocaleString()}/week
            </div>
            <div className="text-xs text-gray-400 mt-1 capitalize">
              {strategy.market_rate_analysis.care_type?.replace('_', ' ') || strategy.market_rate_analysis.care_type || 'N/A'}
            </div>
          </div>
          <div className="bg-green-50 rounded-lg p-3 border border-green-200">
            <div className="text-xs text-gray-500 mb-1">Regional Average</div>
            <div className="font-semibold text-gray-900 text-lg">
              £{strategy.market_rate_analysis.regional_average_weekly.toLocaleString()}/week
            </div>
            <div className="text-xs text-gray-400 mt-1 capitalize">
              {strategy.market_rate_analysis.region?.replace('_', ' ') || strategy.market_rate_analysis.region || 'N/A'}
            </div>
          </div>
          <div className="bg-purple-50 rounded-lg p-3 border border-purple-200">
            <div className="text-xs text-gray-500 mb-1">Market Range</div>
            <div className="font-semibold text-gray-900 text-sm">
              £{strategy.market_rate_analysis.market_price_range.minimum.toLocaleString()} - 
              £{strategy.market_rate_analysis.market_price_range.maximum.toLocaleString()}
            </div>
            <div className="text-xs text-gray-400 mt-1">
              Avg: £{strategy.market_rate_analysis.market_price_range.average.toLocaleString()}
            </div>
          </div>
        </div>

        {/* Price Comparison Table */}
        <div className="mb-4">
          <h5 className="text-xs font-semibold text-gray-700 mb-2">Price Comparison by Home</h5>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left py-2 px-3 font-semibold text-gray-900">Home</th>
                  <th className="text-right py-2 px-3 font-semibold text-gray-900">Weekly Price</th>
                  <th className="text-right py-2 px-3 font-semibold text-gray-900">vs Regional</th>
                  <th className="text-right py-2 px-3 font-semibold text-gray-900">vs UK</th>
                  <th className="text-center py-2 px-3 font-semibold text-gray-900">Positioning</th>
                  <th className="text-center py-2 px-3 font-semibold text-gray-900">Negotiation</th>
                </tr>
              </thead>
              <tbody>
                {strategy.market_rate_analysis.price_comparison.map((home, idx) => (
                  <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-2 px-3 font-medium text-gray-900">{home.home_name}</td>
                    <td className="py-2 px-3 text-right font-semibold text-gray-900">
                      £{home.weekly_price.toLocaleString()}
                    </td>
                    <td className={`py-2 px-3 text-right ${
                      home.vs_regional_average > 0 ? 'text-red-600' : 
                      home.vs_regional_average < 0 ? 'text-green-600' : 
                      'text-gray-600'
                    }`}>
                      {home.vs_regional_average > 0 ? '+' : ''}{home.vs_regional_average.toFixed(1)}%
                    </td>
                    <td className={`py-2 px-3 text-right ${
                      home.vs_uk_average > 0 ? 'text-red-600' : 
                      home.vs_uk_average < 0 ? 'text-green-600' : 
                      'text-gray-600'
                    }`}>
                      {home.vs_uk_average > 0 ? '+' : ''}{home.vs_uk_average.toFixed(1)}%
                    </td>
                    <td className="py-2 px-3 text-center">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPositioningColor(home.positioning)}`}>
                        {home.positioning}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-center">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getNegotiationPotentialColor(home.negotiation_potential?.potential || 'low')}`}>
                        {home.negotiation_potential?.potential?.toUpperCase() || 'N/A'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Value Positioning */}
        {strategy.market_rate_analysis.value_positioning.best_value && (
          <div className="mb-4 p-3 bg-green-50 rounded-lg border border-green-200">
            <div className="text-xs font-semibold text-green-900 mb-2">Best Value Option</div>
            <div className="text-sm">
              <span className="font-semibold">{strategy.market_rate_analysis.value_positioning.best_value.home_name}</span>
              <span className="text-gray-600 ml-2">
                (£{strategy.market_rate_analysis.value_positioning.best_value.weekly_price.toLocaleString()}/week, 
                Match: {strategy.market_rate_analysis.value_positioning.best_value.match_score}%)
              </span>
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Value Score: {strategy.market_rate_analysis.value_positioning.best_value.value_score}
            </div>
          </div>
        )}

        {/* Autumna Data */}
        {strategy.market_rate_analysis.autumna_data && (
          <div className="mb-4 p-3 bg-purple-50 rounded-lg border border-purple-200">
            <div className="text-xs font-semibold text-purple-900 mb-2 flex items-center">
              <span className="mr-2">📊</span>
              Autumna Market Data
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div>
                <div className="text-gray-500">Sample Size</div>
                <div className="font-semibold text-gray-900">
                  {strategy.market_rate_analysis.autumna_data.sample_size} homes
                </div>
              </div>
              <div>
                <div className="text-gray-500">Market Range</div>
                <div className="font-semibold text-gray-900">
                  £{strategy.market_rate_analysis.autumna_data.market_range.minimum.toLocaleString()} - 
                  £{strategy.market_rate_analysis.autumna_data.market_range.maximum.toLocaleString()}
                </div>
              </div>
              <div>
                <div className="text-gray-500">Average</div>
                <div className="font-semibold text-gray-900">
                  £{strategy.market_rate_analysis.autumna_data.market_range.average.toLocaleString()}/week
                </div>
              </div>
            </div>
            <div className="text-xs text-gray-500 mt-2 italic">
              {strategy.market_rate_analysis.autumna_data.note}
            </div>
          </div>
        )}

        {/* Market Insights */}
        {strategy.market_rate_analysis.market_insights && strategy.market_rate_analysis.market_insights.length > 0 && (
          <div className="pt-3 border-t border-gray-200">
            <div className="text-xs font-semibold text-gray-700 mb-2">Market Insights</div>
            <ul className="space-y-1">
              {strategy.market_rate_analysis.market_insights.map((insight, idx) => (
                <li key={idx} className="text-xs text-gray-600 flex items-start">
                  <span className="text-blue-600 mr-2">•</span>
                  <span>{insight}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Discount Negotiation Points */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h4 className="text-sm font-semibold text-gray-900 mb-4 flex items-center">
          <DollarSign className="w-4 h-4 mr-2 text-green-600" />
          Discount Negotiation Points
        </h4>

        {/* Total Potential Discount */}
        <div className="mb-4 p-3 bg-green-50 rounded-lg border border-green-200">
          <div className="text-xs font-semibold text-green-900 mb-2">Total Potential Discount</div>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div>
              <div className="text-gray-500">Conservative</div>
              <div className="font-semibold text-gray-900">{strategy.discount_negotiation_points.total_potential_discount.conservative_range}</div>
            </div>
            <div>
              <div className="text-gray-500">Optimistic</div>
              <div className="font-semibold text-gray-900">{strategy.discount_negotiation_points.total_potential_discount.optimistic_range}</div>
            </div>
            <div>
              <div className="text-gray-500">Realistic</div>
              <div className="font-semibold text-green-700">{strategy.discount_negotiation_points.total_potential_discount.realistic_expectation}</div>
            </div>
          </div>
          <div className="text-xs text-gray-500 mt-2 italic">
            {strategy.discount_negotiation_points.total_potential_discount.note}
          </div>
        </div>

        {/* Available Discounts */}
        <div className="space-y-3 mb-4">
          {strategy.discount_negotiation_points.available_discounts.map((discount, idx) => (
            <div key={idx} className={`p-3 rounded-lg border ${
              discount.priority === 'high' ? 'bg-green-50 border-green-200' :
              discount.priority === 'medium' ? 'bg-yellow-50 border-yellow-200' :
              'bg-gray-50 border-gray-200'
            }`}>
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h5 className="text-xs font-semibold text-gray-900">{discount.title}</h5>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      discount.priority === 'high' ? 'bg-green-200 text-green-800' :
                      discount.priority === 'medium' ? 'bg-yellow-200 text-yellow-800' :
                      'bg-gray-200 text-gray-800'
                    }`}>
                      {discount.priority?.toUpperCase() || 'N/A'}
                    </span>
                    <span className="text-xs font-semibold text-green-700">{discount.potential_discount}</span>
                  </div>
                  <div className="text-xs text-gray-600 mt-1">{discount.description}</div>
                </div>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                <span className="font-semibold">Reasoning: </span>
                {discount.reasoning}
              </div>
              <div className="text-xs text-gray-700 mt-2 font-medium">
                How to negotiate: {discount.how_to_negotiate}
              </div>
            </div>
          ))}
        </div>

        {/* Negotiation Strategy Guide */}
        <div className="pt-3 border-t border-gray-200">
          <h5 className="text-xs font-semibold text-gray-700 mb-2">Negotiation Strategy</h5>
          <div className="space-y-2 text-xs">
            <div>
              <span className="font-semibold text-gray-700">Opening Strategy: </span>
              <ul className="list-disc list-inside ml-2 mt-1 space-y-1">
                {strategy.discount_negotiation_points.negotiation_strategy.opening_strategy.map((strategy, idx) => (
                  <li key={idx} className="text-gray-600">{strategy}</li>
                ))}
              </ul>
            </div>
            <div>
              <span className="font-semibold text-gray-700">Key Talking Points: </span>
              <ul className="list-disc list-inside ml-2 mt-1 space-y-1">
                {strategy.discount_negotiation_points.negotiation_strategy.key_talking_points.map((point, idx) => (
                  <li key={idx} className="text-gray-600">{point}</li>
                ))}
              </ul>
            </div>
            <div className="text-gray-600">
              <span className="font-semibold">Timing: </span>
              {strategy.discount_negotiation_points.negotiation_strategy.timing}
            </div>
            <div className="text-gray-600">
              <span className="font-semibold">Approach: </span>
              {strategy.discount_negotiation_points.negotiation_strategy.approach}
            </div>
            <div className="pt-2 border-t border-gray-100">
              <span className="font-semibold text-red-700">Red Flags: </span>
              <ul className="list-disc list-inside ml-2 mt-1 space-y-1">
                {strategy.discount_negotiation_points.negotiation_strategy.red_flags.map((flag, idx) => (
                  <li key={idx} className="text-red-600">{flag}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Contract Review Checklist */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h4 className="text-sm font-semibold text-gray-900 mb-4 flex items-center">
          <FileText className="w-4 h-4 mr-2 text-purple-600" />
          Contract Review Checklist
        </h4>

        {/* Essential Terms */}
        <div className="mb-4">
          <h5 className="text-xs font-semibold text-gray-700 mb-3">Essential Terms to Review</h5>
          <div className="space-y-3">
            {strategy.contract_review_checklist.essential_terms.map((term, idx) => (
              <div key={idx} className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-start justify-between mb-2">
                  <h6 className="text-xs font-semibold text-gray-900">{term.term}</h6>
                  <CheckCircle2 className="w-4 h-4 text-gray-400" />
                </div>
                <div className="text-xs text-gray-600 mb-2">
                  <span className="font-medium">What to check: </span>
                  {term.what_to_check}
                </div>
                {term.red_flags && term.red_flags.length > 0 && (
                  <div className="pt-2 border-t border-gray-200">
                    <div className="text-xs font-semibold text-red-700 mb-1">Red Flags:</div>
                    <ul className="list-disc list-inside ml-2 space-y-0.5">
                      {term.red_flags.map((flag, flagIdx) => (
                        <li key={flagIdx} className="text-xs text-red-600">{flag}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Recommended Additions */}
        {strategy.contract_review_checklist.recommended_additions && strategy.contract_review_checklist.recommended_additions.length > 0 && (
          <div className="mb-4 pt-3 border-t border-gray-200">
            <h5 className="text-xs font-semibold text-gray-700 mb-2">Recommended Additions</h5>
            <ul className="space-y-1">
              {strategy.contract_review_checklist.recommended_additions.map((addition, idx) => (
                <li key={idx} className="text-xs text-gray-600 flex items-start">
                  <span className="text-green-600 mr-2">✓</span>
                  <span>{addition}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Negotiation Leverage Points */}
        {strategy.contract_review_checklist.negotiation_leverage_points && strategy.contract_review_checklist.negotiation_leverage_points.length > 0 && (
          <div className="pt-3 border-t border-gray-200">
            <h5 className="text-xs font-semibold text-gray-700 mb-2">Negotiation Leverage Points</h5>
            <div className="space-y-2">
              {strategy.contract_review_checklist.negotiation_leverage_points.map((point, idx) => (
                <div key={idx} className="p-2 bg-yellow-50 rounded border border-yellow-200">
                  <div className="text-xs font-semibold text-gray-900">{point.home_name}</div>
                  <div className="text-xs text-gray-600 mt-1">
                    <span className="font-medium">Leverage: </span>
                    {point.leverage}
                  </div>
                  <div className="text-xs text-gray-700 mt-1">
                    <span className="font-medium">Suggestion: </span>
                    {point.suggestion}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Email Templates */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h4 className="text-sm font-semibold text-gray-900 mb-4 flex items-center">
          <Mail className="w-4 h-4 mr-2 text-blue-600" />
          Email Templates
        </h4>

        <div className="space-y-4">
          {/* Initial Inquiry */}
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <div className="bg-blue-50 px-4 py-2 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h5 className="text-xs font-semibold text-gray-900">Initial Inquiry</h5>
                <div className="text-xs text-gray-500 mt-0.5">
                  {strategy.email_templates.initial_inquiry.when_to_use}
                </div>
              </div>
              <button
                onClick={() => copyToClipboard(strategy.email_templates.initial_inquiry.template, 'initial')}
                className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center gap-1"
              >
                {copiedTemplate === 'initial' ? (
                  <>
                    <Check className="w-3 h-3" />
                    Copied
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3" />
                    Copy
                  </>
                )}
              </button>
            </div>
            <div className="p-4 bg-gray-50">
              <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono">
                {strategy.email_templates.initial_inquiry.template}
              </pre>
              <div className="text-xs text-gray-500 mt-2 italic">
                {strategy.email_templates.initial_inquiry.customization_notes}
              </div>
            </div>
          </div>

          {/* Negotiation Follow-up */}
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <div className="bg-green-50 px-4 py-2 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h5 className="text-xs font-semibold text-gray-900">Negotiation Follow-up</h5>
                <div className="text-xs text-gray-500 mt-0.5">
                  {strategy.email_templates.negotiation_followup.when_to_use}
                </div>
              </div>
              <button
                onClick={() => copyToClipboard(strategy.email_templates.negotiation_followup.template, 'negotiation')}
                className="text-xs px-2 py-1 bg-green-600 text-white rounded hover:bg-green-700 flex items-center gap-1"
              >
                {copiedTemplate === 'negotiation' ? (
                  <>
                    <Check className="w-3 h-3" />
                    Copied
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3" />
                    Copy
                  </>
                )}
              </button>
            </div>
            <div className="p-4 bg-gray-50">
              <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono">
                {strategy.email_templates.negotiation_followup.template}
              </pre>
              <div className="text-xs text-gray-500 mt-2 italic">
                {strategy.email_templates.negotiation_followup.customization_notes}
              </div>
            </div>
          </div>

          {/* Contract Clarification */}
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <div className="bg-purple-50 px-4 py-2 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h5 className="text-xs font-semibold text-gray-900">Contract Clarification</h5>
                <div className="text-xs text-gray-500 mt-0.5">
                  {strategy.email_templates.contract_clarification.when_to_use}
                </div>
              </div>
              <button
                onClick={() => copyToClipboard(strategy.email_templates.contract_clarification.template, 'contract')}
                className="text-xs px-2 py-1 bg-purple-600 text-white rounded hover:bg-purple-700 flex items-center gap-1"
              >
                {copiedTemplate === 'contract' ? (
                  <>
                    <Check className="w-3 h-3" />
                    Copied
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3" />
                    Copy
                  </>
                )}
              </button>
            </div>
            <div className="p-4 bg-gray-50">
              <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono">
                {strategy.email_templates.contract_clarification.template}
              </pre>
              <div className="text-xs text-gray-500 mt-2 italic">
                {strategy.email_templates.contract_clarification.customization_notes}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Questions to Ask at Visit */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h4 className="text-sm font-semibold text-gray-900 mb-4 flex items-center">
          <HelpCircle className="w-4 h-4 mr-2 text-orange-600" />
          Questions to Ask at Visit
        </h4>

        {/* Questions by Category */}
        <div className="space-y-4 mb-4">
          {Object.entries(strategy.questions_to_ask_at_visit.questions_by_category).map(([category, questions]) => (
            <div key={category} className="border border-gray-200 rounded-lg overflow-hidden">
              <div className="bg-gray-50 px-3 py-2 border-b border-gray-200">
                <h5 className="text-xs font-semibold text-gray-900 capitalize">
                  {category?.replace('_', ' ') || category || 'N/A'}
                </h5>
              </div>
              <div className="p-3">
                <ul className="space-y-2">
                  {questions.map((question, idx) => (
                    <li key={idx} className="text-xs text-gray-700 flex items-start">
                      <span className="text-blue-600 mr-2">•</span>
                      <span>{question}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>

        {/* Priority Questions */}
        {strategy.questions_to_ask_at_visit.priority_questions && strategy.questions_to_ask_at_visit.priority_questions.length > 0 && (
          <div className="mb-4 pt-3 border-t border-gray-200">
            <h5 className="text-xs font-semibold text-orange-700 mb-2 flex items-center">
              <AlertTriangle className="w-3 h-3 mr-1" />
              Priority Questions
            </h5>
            <ul className="space-y-1">
              {strategy.questions_to_ask_at_visit.priority_questions.map((question, idx) => (
                <li key={idx} className="text-xs text-orange-700 flex items-start">
                  <span className="text-orange-600 mr-2">⚠</span>
                  <span>{question}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Red Flag Questions */}
        {strategy.questions_to_ask_at_visit.red_flag_questions && strategy.questions_to_ask_at_visit.red_flag_questions.length > 0 && (
          <div className="pt-3 border-t border-gray-200">
            <h5 className="text-xs font-semibold text-red-700 mb-2 flex items-center">
              <AlertTriangle className="w-3 h-3 mr-1" />
              Red Flag Questions
            </h5>
            <ul className="space-y-1">
              {strategy.questions_to_ask_at_visit.red_flag_questions.map((question, idx) => (
                <li key={idx} className="text-xs text-red-600 flex items-start">
                  <span className="text-red-600 mr-2">🚩</span>
                  <span>{question}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

