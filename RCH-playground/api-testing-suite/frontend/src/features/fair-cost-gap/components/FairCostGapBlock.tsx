/**
 * Fair Cost Gap Block
 * MOST EMOTIONAL AND CONVERSION-DRIVEN BLOCK
 * Shows family overpayment above government fair cost price
 */
import { AlertTriangle, ArrowRight, TrendingUp, Shield } from 'lucide-react';
import { AnimatedCounter } from './AnimatedCounter';
import { useFairCostGap } from '../hooks/useFairCostGap';
import type { CareType } from '../types';

interface FairCostGapBlockProps {
  marketPrice: number;
  localAuthority: string;
  careType: CareType;
  className?: string;
  onUpgradeClick?: () => void;
}

export function FairCostGapBlock({
  marketPrice,
  localAuthority,
  careType,
  className = '',
  onUpgradeClick,
}: FairCostGapBlockProps) {
  const {
    msifLower,
    gapWeekly,
    gapAnnual,
    gapFiveYear,
    gapPercent,
    isLoading,
    error,
  } = useFairCostGap({
    marketPrice,
    localAuthority,
    careType,
    enabled: !!marketPrice && !!localAuthority && !!careType,
  });

  // Government coverage range (32k-82k per year)
  const govCoverageMin = 32000;
  const govCoverageMax = 82000;

  if (isLoading) {
    return (
      <div className={`bg-gradient-to-br from-[#EF4444] via-red-600 to-[#DC2626] rounded-2xl shadow-2xl p-8 md:p-12 text-white relative overflow-hidden ${className}`}>
        <div className="flex items-center justify-center min-h-[300px]">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-xl font-semibold">Calculating your overpayment...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || gapWeekly <= 0) {
    return (
      <div className={`bg-gradient-to-br from-gray-600 to-gray-700 rounded-2xl shadow-xl p-8 md:p-12 text-white ${className}`}>
        <div className="flex items-center mb-4">
          <Shield className="w-8 h-8 mr-3" />
          <h2 className="text-3xl md:text-4xl font-bold">Fair Cost Gap Information</h2>
        </div>
        <p className="text-lg text-gray-200">
          {error || 'Insufficient data to calculate overpayment. Please check your input data.'}
        </p>
      </div>
    );
  }

  return (
    <div className={`bg-gradient-to-br from-[#EF4444] via-red-600 to-[#DC2626] rounded-2xl shadow-2xl p-6 md:p-8 lg:p-12 text-white relative overflow-hidden ${className}`}>
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
        <div className="flex items-center mb-4 md:mb-6">
          <AlertTriangle className="w-6 h-6 md:w-8 md:h-8 mr-2 md:mr-3 flex-shrink-0" />
          <h2 className="text-2xl md:text-4xl lg:text-5xl font-bold">
            YOUR CARE HOME COST ANALYSIS
          </h2>
        </div>

        {/* Market Average and Government Fair Cost */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 md:p-6 mb-4 border border-white/20">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-sm md:text-base text-gray-200 mb-1">Market Average (your area):</p>
              <p className="text-xl md:text-2xl lg:text-3xl font-bold">
                £{marketPrice.toLocaleString()}/week
              </p>
            </div>
            <div>
              <p className="text-sm md:text-base text-gray-200 mb-1">Government Fair Cost:</p>
              <p className="text-xl md:text-2xl lg:text-3xl font-bold">
                £{msifLower.toLocaleString()}/week
              </p>
            </div>
          </div>
        </div>

        {/* YOUR OVERPAYMENT */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 md:p-8 mb-6 border-2 border-white/30">
          <p className="text-base md:text-lg text-gray-200 mb-2 text-center">
            🔴 YOUR OVERPAYMENT:
          </p>
          <p className="text-4xl md:text-6xl lg:text-7xl font-bold mb-4 leading-tight text-center">
            £
            <AnimatedCounter
              value={Math.round(gapWeekly)}
              duration={2000}
              className="inline-block"
            />
            /week
          </p>
          
          {/* Cost Impact */}
          <div className="mt-4 pt-4 border-t border-white/20">
            <p className="text-base md:text-lg font-semibold mb-2 text-center">Cost Impact:</p>
            <div className="flex flex-col md:flex-row items-center justify-center gap-3 md:gap-4 text-lg md:text-xl font-semibold">
              <span>
                • Per year: £
                <AnimatedCounter
                  value={Math.round(gapAnnual)}
                  duration={2500}
                  className="inline-block"
                />
              </span>
              <span className="text-white/70 hidden md:inline">|</span>
              <span>
                • Over 5 years: £
                <AnimatedCounter
                  value={Math.round(gapFiveYear)}
                  duration={3000}
                  className="inline-block"
                />
              </span>
            </div>
          </div>
        </div>

        {/* Professional Report CTA Text */}
        <div className="mb-6">
          <p className="text-base md:text-lg text-gray-200 text-center">
            💡 Professional Report shows how to reduce this gap with negotiation strategies and funding options
          </p>
        </div>

        {/* CTA Button */}
        <button
          onClick={onUpgradeClick}
          className="w-full bg-[#10B981] hover:bg-[#059669] text-white font-bold py-4 md:py-5 px-6 md:px-8 rounded-xl text-lg md:text-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-[1.02] flex items-center justify-center gap-2"
        >
          <span>Learn how to close this gap → Professional £119</span>
          <ArrowRight className="w-5 h-5 md:w-6 md:h-6" />
        </button>
      </div>
    </div>
  );
}

