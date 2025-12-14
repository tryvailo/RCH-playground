import { useState, useEffect } from 'react';
import { Settings, RotateCcw, Info, ChevronDown } from 'lucide-react';

export interface ScoringWeights {
  location: number;
  cqc: number;
  budget: number;
  careType: number;
  availability: number;
  googleReviews: number;
}

export interface ScoringThresholds {
  location: {
    within5Miles: number;
    within10Miles: number;
    within15Miles: number;
    over15Miles: number;
  };
  budget: {
    withinBudget: number;
    plus50: number;
    plus100: number;
    plus200: number;
  };
  googleReviews: {
    highRating: number;
    goodRatingManyReviews: number;
    goodRatingFewReviews: number;
    mediumRatingMany: number;
    mediumRatingFew: number;
  };
}

const DEFAULT_WEIGHTS: ScoringWeights = {
  location: 20,
  cqc: 25,
  budget: 20,
  careType: 15,
  availability: 10,
  googleReviews: 10,
};

const DEFAULT_THRESHOLDS: ScoringThresholds = {
  location: {
    within5Miles: 20,
    within10Miles: 15,
    within15Miles: 10,
    over15Miles: 5,
  },
  budget: {
    withinBudget: 20,
    plus50: 20,
    plus100: 15,
    plus200: 10,
  },
  googleReviews: {
    highRating: 10,
    goodRatingManyReviews: 7,
    goodRatingFewReviews: 5,
    mediumRatingMany: 4,
    mediumRatingFew: 2,
  },
};

interface ScoringSettingsProps {
  onSettingsChange?: (weights: ScoringWeights, thresholds: ScoringThresholds) => void;
}

export default function ScoringSettings({ onSettingsChange }: ScoringSettingsProps) {
  const [isExpanded, setIsExpanded] = useState(true); // Expanded by default
  const [weights, setWeights] = useState<ScoringWeights>(DEFAULT_WEIGHTS);
  const [thresholds, setThresholds] = useState<ScoringThresholds>(DEFAULT_THRESHOLDS);

  // Load from localStorage on mount
  useEffect(() => {
    const savedWeights = localStorage.getItem('scoring_weights');
    const savedThresholds = localStorage.getItem('scoring_thresholds');
    
    if (savedWeights) {
      try {
        setWeights(JSON.parse(savedWeights));
      } catch (e) {
        console.error('Failed to load scoring weights:', e);
      }
    }
    
    if (savedThresholds) {
      try {
        setThresholds(JSON.parse(savedThresholds));
      } catch (e) {
        console.error('Failed to load scoring thresholds:', e);
      }
    }
  }, []);

  // Save to localStorage and notify parent
  useEffect(() => {
    localStorage.setItem('scoring_weights', JSON.stringify(weights));
    localStorage.setItem('scoring_thresholds', JSON.stringify(thresholds));
    onSettingsChange?.(weights, thresholds);
  }, [weights, thresholds, onSettingsChange]);

  const handleWeightChange = (key: keyof ScoringWeights, value: number) => {
    setWeights(prev => ({ ...prev, [key]: Math.max(0, Math.min(100, value)) }));
  };

  const handleThresholdChange = (
    category: keyof ScoringThresholds,
    key: string,
    value: number
  ) => {
    setThresholds(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: Math.max(0, Math.min(100, value)),
      },
    }));
  };

  const handleReset = () => {
    setWeights(DEFAULT_WEIGHTS);
    setThresholds(DEFAULT_THRESHOLDS);
    localStorage.removeItem('scoring_weights');
    localStorage.removeItem('scoring_thresholds');
  };

  const totalWeight = Object.values(weights).reduce((sum, val) => sum + val, 0);
  const weightWarning = totalWeight !== 100;

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors rounded-t-lg"
      >
        <div className="flex items-center">
          <Settings className="w-5 h-5 text-[#1E2A44] mr-2" />
          <span className="font-semibold text-gray-900">Scoring Settings</span>
          {weightWarning && (
            <span className="ml-2 px-2 py-0.5 bg-yellow-100 text-yellow-800 text-xs rounded-full">
              Total: {totalWeight}%
            </span>
          )}
        </div>
        <div className={`transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
          <ChevronDown className="w-5 h-5 text-gray-500" />
        </div>
      </button>

      {/* Content */}
      {isExpanded && (
        <div className="px-4 pb-4 space-y-6 border-t border-gray-200">
          {/* Reset Button */}
          <div className="flex justify-end pt-3">
            <button
              onClick={handleReset}
              className="text-sm text-gray-600 hover:text-gray-900 flex items-center"
            >
              <RotateCcw className="w-4 h-4 mr-1" />
              Reset to Defaults
            </button>
          </div>

          {/* Weight Warning */}
          {weightWarning && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 flex items-start">
              <Info className="w-5 h-5 text-yellow-600 mr-2 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-yellow-800">
                <p className="font-semibold mb-1">Weights don't sum to 100%</p>
                <p>Current total: {totalWeight}%. Adjust weights so they sum to 100%.</p>
              </div>
            </div>
          )}

          {/* Category Weights */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-3">Category Weights (Total: {totalWeight}%)</h4>
            <div className="space-y-3">
              {Object.entries(weights).map(([key, value]) => (
                <div key={key}>
                  <div className="flex items-center justify-between mb-1">
                    <label className="text-sm text-gray-700 capitalize">
                      {key === 'cqc' ? 'CQC Rating' : key === 'careType' ? 'Care Type' : key === 'googleReviews' ? 'Google Reviews' : key}
                    </label>
                    <span className="text-sm font-semibold text-[#1E2A44]">{value}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={value}
                    onChange={(e) => handleWeightChange(key as keyof ScoringWeights, parseInt(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#1E2A44]"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Location Thresholds */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-3">Location Scoring</h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs text-gray-600">≤5 miles</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={thresholds.location.within5Miles}
                  onChange={(e) => handleThresholdChange('location', 'within5Miles', parseInt(e.target.value) || 0)}
                  className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#1E2A44]"
                />
              </div>
              <div className="flex items-center justify-between">
                <label className="text-xs text-gray-600">≤10 miles</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={thresholds.location.within10Miles}
                  onChange={(e) => handleThresholdChange('location', 'within10Miles', parseInt(e.target.value) || 0)}
                  className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#1E2A44]"
                />
              </div>
              <div className="flex items-center justify-between">
                <label className="text-xs text-gray-600">≤15 miles</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={thresholds.location.within15Miles}
                  onChange={(e) => handleThresholdChange('location', 'within15Miles', parseInt(e.target.value) || 0)}
                  className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#1E2A44]"
                />
              </div>
              <div className="flex items-center justify-between">
                <label className="text-xs text-gray-600">{'>'}15 miles</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={thresholds.location.over15Miles}
                  onChange={(e) => handleThresholdChange('location', 'over15Miles', parseInt(e.target.value) || 0)}
                  className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#1E2A44]"
                />
              </div>
            </div>
          </div>

          {/* Budget Thresholds */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-3">Budget Match Scoring</h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs text-gray-600">Within budget</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={thresholds.budget.withinBudget}
                  onChange={(e) => handleThresholdChange('budget', 'withinBudget', parseInt(e.target.value) || 0)}
                  className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#1E2A44]"
                />
              </div>
              <div className="flex items-center justify-between">
                <label className="text-xs text-gray-600">+£0-50</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={thresholds.budget.plus50}
                  onChange={(e) => handleThresholdChange('budget', 'plus50', parseInt(e.target.value) || 0)}
                  className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#1E2A44]"
                />
              </div>
              <div className="flex items-center justify-between">
                <label className="text-xs text-gray-600">+£50-100</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={thresholds.budget.plus100}
                  onChange={(e) => handleThresholdChange('budget', 'plus100', parseInt(e.target.value) || 0)}
                  className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#1E2A44]"
                />
              </div>
              <div className="flex items-center justify-between">
                <label className="text-xs text-gray-600">+£100-200</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={thresholds.budget.plus200}
                  onChange={(e) => handleThresholdChange('budget', 'plus200', parseInt(e.target.value) || 0)}
                  className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#1E2A44]"
                />
              </div>
            </div>
          </div>

          {/* Google Reviews Thresholds */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-3">Google Reviews Scoring</h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs text-gray-600">≥4.5 rating</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={thresholds.googleReviews.highRating}
                  onChange={(e) => handleThresholdChange('googleReviews', 'highRating', parseInt(e.target.value) || 0)}
                  className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#1E2A44]"
                />
              </div>
              <div className="flex items-center justify-between">
                <label className="text-xs text-gray-600">≥4.0 (≥20 reviews)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={thresholds.googleReviews.goodRatingManyReviews}
                  onChange={(e) => handleThresholdChange('googleReviews', 'goodRatingManyReviews', parseInt(e.target.value) || 0)}
                  className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#1E2A44]"
                />
              </div>
              <div className="flex items-center justify-between">
                <label className="text-xs text-gray-600">≥4.0 ({'<'}20 reviews)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={thresholds.googleReviews.goodRatingFewReviews}
                  onChange={(e) => handleThresholdChange('googleReviews', 'goodRatingFewReviews', parseInt(e.target.value) || 0)}
                  className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#1E2A44]"
                />
              </div>
              <div className="flex items-center justify-between">
                <label className="text-xs text-gray-600">≥3.5 (≥10 reviews)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={thresholds.googleReviews.mediumRatingMany}
                  onChange={(e) => handleThresholdChange('googleReviews', 'mediumRatingMany', parseInt(e.target.value) || 0)}
                  className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#1E2A44]"
                />
              </div>
              <div className="flex items-center justify-between">
                <label className="text-xs text-gray-600">≥3.5 ({'<'}10 reviews)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={thresholds.googleReviews.mediumRatingFew}
                  onChange={(e) => handleThresholdChange('googleReviews', 'mediumRatingFew', parseInt(e.target.value) || 0)}
                  className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#1E2A44]"
                />
              </div>
            </div>
          </div>

          {/* Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-start">
              <Info className="w-4 h-4 text-blue-600 mr-2 flex-shrink-0 mt-0.5" />
              <p className="text-xs text-blue-800">
                Settings are saved automatically and will be used for the next report generation.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

