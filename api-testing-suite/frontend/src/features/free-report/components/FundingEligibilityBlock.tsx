/**
 * Funding Eligibility Block
 * Shows simplified funding eligibility estimates for Free Report
 * Drives upgrade to Professional Report for detailed analysis
 */
import { DollarSign, ArrowRight, CheckCircle2, AlertCircle } from 'lucide-react';
import type { FundingEligibility } from '../types';

interface FundingEligibilityBlockProps {
  fundingEligibility: FundingEligibility;
  className?: string;
  onUpgradeClick?: () => void;
}

export function FundingEligibilityBlock({
  fundingEligibility,
  className = '',
  onUpgradeClick,
}: FundingEligibilityBlockProps) {
  return (
    <div className={`bg-gradient-to-br from-[#10B981] via-green-600 to-[#059669] rounded-2xl shadow-2xl p-6 md:p-8 lg:p-12 text-white relative overflow-hidden ${className}`}>
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage:
              'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
            backgroundSize: '40px 40px',
          }}
        ></div>
      </div>

      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-center mb-6">
          <DollarSign className="w-6 h-6 md:w-8 md:h-8 mr-3 flex-shrink-0" />
          <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold">
            GOVERNMENT FUNDING ELIGIBILITY
          </h2>
        </div>

        <p className="text-base md:text-lg text-gray-100 mb-6">
          Based on your questionnaire answers:
        </p>

        {/* Funding Cards */}
        <div className="space-y-4 mb-6">
          {/* CHC Card */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 md:p-6 border border-white/20">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 md:w-6 md:h-6 text-green-300 flex-shrink-0 mt-1" />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-green-300 text-lg">🟢</span>
                  <h3 className="text-lg md:text-xl font-semibold">NHS CHC Probability</h3>
                </div>
                <p className="text-2xl md:text-3xl font-bold mb-2">
                  {fundingEligibility.chc.probability_range}
                </p>
                <p className="text-sm md:text-base text-gray-200">
                  Potential savings: <span className="font-semibold">{fundingEligibility.chc.savings_range}</span>
                </p>
              </div>
            </div>
          </div>

          {/* LA Funding Card */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 md:p-6 border border-white/20">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 md:w-6 md:h-6 text-green-300 flex-shrink-0 mt-1" />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-green-300 text-lg">🟢</span>
                  <h3 className="text-lg md:text-xl font-semibold">Council Funding Probability</h3>
                </div>
                <p className="text-2xl md:text-3xl font-bold mb-2">
                  {fundingEligibility.la.probability}
                </p>
                <p className="text-sm md:text-base text-gray-200">
                  Potential savings: <span className="font-semibold">{fundingEligibility.la.savings_range}</span>
                </p>
              </div>
            </div>
          </div>

          {/* DPA Card */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 md:p-6 border border-white/20">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 md:w-6 md:h-6 text-green-300 flex-shrink-0 mt-1" />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-green-300 text-lg">🟢</span>
                  <h3 className="text-lg md:text-xl font-semibold">Deferred Payment Eligible</h3>
                </div>
                <p className="text-2xl md:text-3xl font-bold mb-2">
                  {fundingEligibility.dpa.probability}
                </p>
                <p className="text-sm md:text-base text-gray-200">
                  Cash flow relief: <span className="font-semibold">{fundingEligibility.dpa.cash_flow_relief}</span>
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Professional Report Benefits */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 md:p-6 mb-6 border border-white/20">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 md:w-6 md:h-6 text-yellow-300 flex-shrink-0 mt-1" />
            <div>
              <p className="text-base md:text-lg font-semibold mb-2">💡 Professional Report includes:</p>
              <ul className="list-disc list-inside text-sm md:text-base text-gray-200 space-y-1">
                <li>Detailed eligibility breakdown (12 health domains)</li>
                <li>Application templates for CHC/LA/DPA</li>
                <li>Exact savings calculations for your situation</li>
              </ul>
            </div>
          </div>
        </div>

        {/* CTA Button */}
        <button
          onClick={onUpgradeClick}
          className="w-full bg-white hover:bg-gray-100 text-[#10B981] font-bold py-4 md:py-5 px-6 md:px-8 rounded-xl text-lg md:text-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-[1.02] flex items-center justify-center gap-2"
        >
          <span>🚀 Upgrade to Professional (£119) to access full analysis</span>
          <ArrowRight className="w-5 h-5 md:w-6 md:h-6" />
        </button>

        {/* Disclaimer */}
        <div className="mt-6 pt-6 border-t border-white/20">
          <p className="text-xs md:text-sm text-gray-200 text-center">
            * These are simplified estimates based on limited questionnaire data. 
            <span className="font-semibold"> Professional Report provides exact calculations</span> with detailed 12-domain CHC assessment, 
            full means test, and personalized application templates.
          </p>
        </div>
      </div>
    </div>
  );
}

