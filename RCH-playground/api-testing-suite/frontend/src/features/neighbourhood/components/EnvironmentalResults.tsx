import { Activity, Volume2, Wind, AlertCircle, CheckCircle } from 'lucide-react';
import type { EnvironmentalData } from '../types';

// Environmental scores are inverted: lower = better
function getEnvironmentalScoreColor(score: number): string {
  if (score >= 70) return 'text-red-600';
  if (score >= 55) return 'text-orange-600';
  if (score >= 40) return 'text-yellow-600';
  if (score >= 25) return 'text-green-600';
  return 'text-emerald-600'; // Very low = excellent
}

interface Props {
  data: EnvironmentalData;
}

export default function EnvironmentalResults({ data }: Props) {
  const { noise, pollution, overall_environmental_score, overall_rating } = data;

  return (
    <div className="space-y-6">
      {/* Overall Environmental Score */}
      <div className="bg-gradient-to-r from-orange-50 to-amber-50 border border-orange-200 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Activity className="w-6 h-6 text-orange-600" />
            <h3 className="text-lg font-semibold text-gray-800">Overall Environmental Quality</h3>
          </div>
          <div className="text-right">
            <div className={`text-3xl font-bold ${getEnvironmentalScoreColor(overall_environmental_score)}`}>
              {overall_environmental_score.toFixed(1)}
            </div>
            <div className="text-sm text-gray-600">{overall_rating}</div>
          </div>
        </div>
        <p className="text-sm text-gray-700">
          Lower scores indicate better environmental conditions (less noise and pollution)
        </p>
      </div>

      {/* Noise Section */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <Volume2 className="w-5 h-5 text-blue-600" />
            <div>
              <h4 className="font-semibold text-gray-800">Noise Level</h4>
              <p className="text-xs text-gray-500">Traffic and environmental noise</p>
            </div>
          </div>
          {noise.error ? (
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm">Error</span>
            </div>
          ) : (
            <div className="text-right">
              <div className={`text-2xl font-bold ${getEnvironmentalScoreColor(noise.noise_score)}`}>
                {noise.noise_score.toFixed(1)}
              </div>
              <div className="text-sm text-gray-600">{noise.rating}</div>
            </div>
          )}
        </div>

        {noise.error ? (
          <div className="bg-red-50 border border-red-200 rounded p-3">
            <p className="text-sm text-red-700">{noise.error}</p>
          </div>
        ) : (
          <>
            <p className="text-sm text-gray-700 mb-4">{noise.description}</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-500 mb-1">Analysis Radius</div>
                <div className="font-medium">{noise.radius_analyzed_m}m</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-500 mb-1">Traffic Density</div>
                <div className="font-medium capitalize">{noise.factors.estimated_traffic_density}</div>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                {noise.factors.major_roads_nearby ? (
                  <AlertCircle className="w-4 h-4 text-orange-600" />
                ) : (
                  <CheckCircle className="w-4 h-4 text-green-600" />
                )}
                <span className={noise.factors.major_roads_nearby ? 'text-orange-700' : 'text-green-700'}>
                  {noise.factors.major_roads_nearby ? 'Major roads nearby' : 'No major roads nearby'}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                {noise.factors.urban_area ? (
                  <AlertCircle className="w-4 h-4 text-orange-600" />
                ) : (
                  <CheckCircle className="w-4 h-4 text-green-600" />
                )}
                <span className={noise.factors.urban_area ? 'text-orange-700' : 'text-green-700'}>
                  {noise.factors.urban_area ? 'Urban area' : 'Rural/suburban area'}
                </span>
              </div>
            </div>

            {noise.recommendations && noise.recommendations.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="text-sm font-medium text-gray-700 mb-2">Recommendations:</div>
                <ul className="text-sm text-gray-600 space-y-1">
                  {noise.recommendations.map((rec, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-orange-600 mt-0.5">•</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}
      </div>

      {/* Pollution Section */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <Wind className="w-5 h-5 text-green-600" />
            <div>
              <h4 className="font-semibold text-gray-800">Air Pollution Level</h4>
              <p className="text-xs text-gray-500">Air quality and pollution</p>
            </div>
          </div>
          {pollution.error ? (
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm">Error</span>
            </div>
          ) : (
            <div className="text-right">
              <div className={`text-2xl font-bold ${getEnvironmentalScoreColor(pollution.pollution_score)}`}>
                {pollution.pollution_score.toFixed(1)}
              </div>
              <div className="text-sm text-gray-600">{pollution.rating}</div>
            </div>
          )}
        </div>

        {pollution.error ? (
          <div className="bg-red-50 border border-red-200 rounded p-3">
            <p className="text-sm text-red-700">{pollution.error}</p>
          </div>
        ) : (
          <>
            <p className="text-sm text-gray-700 mb-4">{pollution.description}</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-500 mb-1">Analysis Radius</div>
                <div className="font-medium">{pollution.radius_analyzed_m}m</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-500 mb-1">Traffic Density</div>
                <div className="font-medium capitalize">{pollution.factors.traffic_density}</div>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                {pollution.factors.major_roads_nearby ? (
                  <AlertCircle className="w-4 h-4 text-orange-600" />
                ) : (
                  <CheckCircle className="w-4 h-4 text-green-600" />
                )}
                <span className={pollution.factors.major_roads_nearby ? 'text-orange-700' : 'text-green-700'}>
                  {pollution.factors.major_roads_nearby ? 'Major roads nearby' : 'No major roads nearby'}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                {pollution.factors.urban_area ? (
                  <AlertCircle className="w-4 h-4 text-orange-600" />
                ) : (
                  <CheckCircle className="w-4 h-4 text-green-600" />
                )}
                <span className={pollution.factors.urban_area ? 'text-orange-700' : 'text-green-700'}>
                  {pollution.factors.urban_area ? 'Urban area' : 'Rural/suburban area'}
                </span>
              </div>
            </div>

            {pollution.recommendations && pollution.recommendations.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="text-sm font-medium text-gray-700 mb-2">Recommendations:</div>
                <ul className="text-sm text-gray-600 space-y-1">
                  {pollution.recommendations.map((rec, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-green-600 mt-0.5">•</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

