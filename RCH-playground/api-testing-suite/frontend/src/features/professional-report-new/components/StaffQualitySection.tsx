import React from 'react';
import { Users, Star, TrendingUp, TrendingDown, AlertCircle, CheckCircle2 } from 'lucide-react';
import type { StaffQualityData } from '../types';

interface StaffQualitySectionProps {
  staffQuality?: StaffQualityData | null;
  homeName: string;
}

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'EXCELLENT': return { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-300' };
    case 'GOOD': return { bg: 'bg-blue-100', text: 'text-blue-800', border: 'border-blue-300' };
    case 'ADEQUATE': return { bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-300' };
    case 'CONCERNING': return { bg: 'bg-orange-100', text: 'text-orange-800', border: 'border-orange-300' };
    case 'POOR': return { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-300' };
    default: return { bg: 'bg-gray-100', text: 'text-gray-800', border: 'border-gray-300' };
  }
};

const getScoreColor = (score: number | null) => {
  if (score === null) return 'bg-gray-200';
  if (score >= 80) return 'bg-green-500';
  if (score >= 60) return 'bg-blue-500';
  if (score >= 40) return 'bg-yellow-500';
  if (score >= 20) return 'bg-orange-500';
  return 'bg-red-500';
};

const getConfidenceLabel = (confidence: string) => {
  switch (confidence) {
    case 'high': return { text: 'High confidence', icon: CheckCircle2, color: 'text-green-600' };
    case 'medium': return { text: 'Medium confidence', icon: AlertCircle, color: 'text-yellow-600' };
    case 'low': return { text: 'Low confidence', icon: AlertCircle, color: 'text-orange-600' };
    default: return { text: 'Unknown', icon: AlertCircle, color: 'text-gray-600' };
  }
};

export default function StaffQualitySection({ staffQuality, homeName }: StaffQualitySectionProps) {
  if (!staffQuality) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 text-center text-xs text-gray-500">
        Staff quality data not available
      </div>
    );
  }

  const categoryColors = getCategoryColor(staffQuality.category);
  const confidenceInfo = getConfidenceLabel(staffQuality.confidence);
  const ConfidenceIcon = confidenceInfo.icon;

  const componentLabels: Record<string, string> = {
    cqc_well_led: 'CQC Well-Led',
    cqc_effective: 'CQC Effective',
    cqc_staff_sentiment: 'CQC Staff Sentiment',
    employee_sentiment: 'Employee Reviews',
  };

  return (
    <div className="space-y-4">
      {/* Overall Score Header */}
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-indigo-600" />
            <h5 className="text-xs font-semibold text-gray-900">
              Staff Quality Assessment - {homeName}
            </h5>
          </div>
          <div className={`px-2 py-1 rounded text-xs font-medium ${categoryColors.bg} ${categoryColors.text} ${categoryColors.border} border`}>
            {staffQuality.category}
          </div>
        </div>

        {/* Score Gauge */}
        <div className="mb-3">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-gray-600">Overall Score</span>
            <span className="text-sm font-semibold text-gray-900">{staffQuality.overallScore}/100</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all duration-500 ${getScoreColor(staffQuality.overallScore)}`}
              style={{ width: `${Math.min(staffQuality.overallScore, 100)}%` }}
            />
          </div>
        </div>

        {/* Confidence Indicator */}
        <div className={`flex items-center gap-1 text-xs ${confidenceInfo.color}`}>
          <ConfidenceIcon className="h-3 w-3" />
          <span>{confidenceInfo.text}</span>
          {staffQuality.dataQuality?.has_insufficient_data && (
            <span className="ml-2 text-orange-600">(Limited data)</span>
          )}
        </div>
      </div>

      {/* Component Breakdown */}
      {staffQuality.components && Object.keys(staffQuality.components).length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-xs font-semibold text-gray-900 mb-3">Component Breakdown</h5>
          <div className="space-y-3">
            {Object.entries(staffQuality.components).map(([key, component]) => {
              if (!component) return null;
              return (
                <div key={key} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-700">{componentLabels[key] || key}</span>
                    <div className="flex items-center gap-2">
                      {component.rating && (
                        <span className="text-gray-500">({component.rating})</span>
                      )}
                      <span className="font-medium text-gray-900">
                        {component.score !== null ? `${component.score}%` : 'N/A'}
                      </span>
                      <span className="text-gray-400 text-[10px]">
                        w:{(component.weight * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${getScoreColor(component.score)}`}
                      style={{ width: `${component.score !== null ? Math.min(component.score, 100) : 0}%` }}
                    />
                  </div>
                  {component.note && (
                    <p className="text-[10px] text-gray-500 italic">{component.note}</p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Themes */}
      {staffQuality.themes && (staffQuality.themes.positive?.length > 0 || staffQuality.themes.negative?.length > 0) && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-xs font-semibold text-gray-900 mb-3">Key Themes</h5>
          <div className="grid grid-cols-2 gap-4">
            {/* Positive Themes */}
            {staffQuality.themes.positive?.length > 0 && (
              <div>
                <div className="flex items-center gap-1 mb-2">
                  <TrendingUp className="h-3 w-3 text-green-600" />
                  <span className="text-xs font-medium text-green-700">Positive</span>
                </div>
                <ul className="space-y-1">
                  {staffQuality.themes.positive.slice(0, 5).map((theme, i) => (
                    <li key={i} className="text-xs text-gray-600 flex items-start gap-1">
                      <span className="text-green-500 mt-0.5">•</span>
                      {theme}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {/* Negative Themes */}
            {staffQuality.themes.negative?.length > 0 && (
              <div>
                <div className="flex items-center gap-1 mb-2">
                  <TrendingDown className="h-3 w-3 text-red-600" />
                  <span className="text-xs font-medium text-red-700">Areas for Improvement</span>
                </div>
                <ul className="space-y-1">
                  {staffQuality.themes.negative.slice(0, 5).map((theme, i) => (
                    <li key={i} className="text-xs text-gray-600 flex items-start gap-1">
                      <span className="text-red-500 mt-0.5">•</span>
                      {theme}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Sample Reviews */}
      {staffQuality.reviews && staffQuality.reviews.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h5 className="text-xs font-semibold text-gray-900 mb-3">
            Sample Reviews ({staffQuality.reviewCount || staffQuality.reviews.length} total)
          </h5>
          <div className="space-y-3">
            {staffQuality.reviews.slice(0, 3).map((review, i) => (
              <div key={i} className="border-l-2 border-gray-200 pl-3">
                <div className="flex items-center gap-2 mb-1">
                  <div className="flex items-center">
                    {[...Array(5)].map((_, idx) => (
                      <Star
                        key={idx}
                        className={`h-3 w-3 ${idx < review.rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`}
                      />
                    ))}
                  </div>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                    review.sentiment === 'positive' ? 'bg-green-100 text-green-700' :
                    review.sentiment === 'negative' ? 'bg-red-100 text-red-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {review.sentiment}
                  </span>
                  <span className="text-[10px] text-gray-400">{review.source}</span>
                </div>
                <p className="text-xs text-gray-600 line-clamp-2">{review.text}</p>
                {(review.author || review.date) && (
                  <p className="text-[10px] text-gray-400 mt-1">
                    {review.author && <span>{review.author}</span>}
                    {review.author && review.date && <span> • </span>}
                    {review.date && <span>{review.date}</span>}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Data Quality & Sources */}
      <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
        <h6 className="text-[10px] font-medium text-gray-700 mb-2">Data Sources</h6>
        <div className="flex flex-wrap gap-2 text-[10px] text-gray-500">
          {staffQuality.cqcData && (
            <span className="bg-white px-2 py-1 rounded border border-gray-200">
              CQC {staffQuality.cqcData.last_inspection_date && `(${staffQuality.cqcData.last_inspection_date})`}
            </span>
          )}
          {staffQuality.carehomeCoUk && (
            <span className="bg-white px-2 py-1 rounded border border-gray-200">
              carehome.co.uk ({staffQuality.carehomeCoUk.review_count || 0} reviews)
            </span>
          )}
          {staffQuality.reviews && staffQuality.reviews.some((r: any) => r.source === 'Google') && (
            <span className="bg-white px-2 py-1 rounded border border-gray-200">
              Google ({staffQuality.reviews.filter((r: any) => r.source === 'Google').length} reviews)
            </span>
          )}
          {staffQuality.indeed && (
            <span className="bg-white px-2 py-1 rounded border border-gray-200">
              Indeed ({staffQuality.indeed.review_count || 0} reviews)
            </span>
          )}
          {staffQuality.dataQuality?.cqc_data_age && (
            <span className="text-gray-400">Data age: {staffQuality.dataQuality.cqc_data_age}</span>
          )}
        </div>
      </div>
    </div>
  );
}
