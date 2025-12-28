import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Clock, Building2, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { CQCDeepDive } from '../types';

interface CQCRatingTrendChartProps {
  cqcData: CQCDeepDive;
  homeName: string;
}

const ratingToNumber = (rating: string): number => {
  const ratingMap: { [key: string]: number } = {
    'Outstanding': 4,
    'Good': 3,
    'Requires improvement': 2,
    'Inadequate': 1
  };
  return ratingMap[rating] || 0;
};

const numberToRating = (num: number): string => {
  const ratingMap: { [key: number]: string } = {
    4: 'Outstanding',
    3: 'Good',
    2: 'Requires improvement',
    1: 'Inadequate'
  };
  return ratingMap[num] || 'Unknown';
};

export default function CQCRatingTrendChart({ cqcData }: CQCRatingTrendChartProps) {
  if (!cqcData?.historical_ratings || cqcData.historical_ratings.length === 0) {
    return (
      <div className="glass-card rounded-2xl p-8 border border-gray-100 text-center text-xs text-gray-400 italic">
        Historical regulatory rating data not available for this location.
      </div>
    );
  }

  // Prepare data for chart - last 5 years with proper date handling
  const allRatings = [...(cqcData.historical_ratings || [])];

  if (cqcData.overall_rating && !allRatings.some(r => {
    const ratingDate = r.date || r.inspection_date;
    if (!ratingDate) return false;
    const date = new Date(ratingDate);
    const currentDate = new Date();
    return Math.abs(date.getTime() - currentDate.getTime()) < 90 * 24 * 60 * 60 * 1000;
  })) {
    allRatings.unshift({
      date: new Date().toISOString().split('T')[0],
      overall_rating: cqcData.overall_rating,
      rating: cqcData.overall_rating
    });
  }

  const sortedRatings = allRatings
    .filter(r => r.date || r.inspection_date)
    .sort((a, b) => {
      const dateA = new Date(a.date || a.inspection_date || '').getTime();
      const dateB = new Date(b.date || b.inspection_date || '').getTime();
      return dateB - dateA;
    });

  const fiveYearsAgo = new Date();
  fiveYearsAgo.setFullYear(fiveYearsAgo.getFullYear() - 5);

  const recentRatings = sortedRatings.filter(r => {
    const ratingDate = new Date(r.date || r.inspection_date || '');
    return ratingDate >= fiveYearsAgo;
  }).slice(0, 10);

  const chartData = recentRatings
    .map((rating) => {
      const date = new Date(rating.date || rating.inspection_date || '');
      return {
        year: date.getFullYear().toString(),
        date: date.toISOString().split('T')[0],
        fullDate: date.toLocaleDateString('en-GB', { year: 'numeric', month: 'short', day: 'numeric' }),
        rating: ratingToNumber(rating.rating || rating.overall_rating || ''),
        ratingLabel: rating.rating || rating.overall_rating || 'Unknown'
      };
    })
    .reverse();

  const getRatingColor = (rating: string): string => {
    switch (rating) {
      case 'Outstanding': return '#10B981';
      case 'Good': return '#6366F1';
      case 'Requires improvement': return '#F59E0B';
      case 'Inadequate': return '#EF4444';
      default: return '#94A3B8';
    }
  };

  const daysSinceInspection = cqcData.days_since_inspection;
  const currentRatingColor = getRatingColor(chartData[chartData.length - 1]?.ratingLabel || 'Good');

  return (
    <div className="glass-card rounded-2xl p-6 border border-gray-100 shadow-sm animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div>
          <h5 className="text-sm font-bold text-[#1E2A44] uppercase tracking-wider">
            Regulatory Performance History
          </h5>
          <p className="text-[10px] text-gray-400 font-medium">CQC trend analysis for 5-year period</p>
        </div>

        {cqcData.trend && (
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest ${cqcData.trend.toLowerCase().includes('improving') ? 'bg-green-100 text-green-700' :
            cqcData.trend.toLowerCase().includes('declining') ? 'bg-red-100 text-red-700' :
              'bg-gray-100 text-gray-700'
            }`}>
            {cqcData.trend.toLowerCase().includes('improving') ? <TrendingUp className="w-3 h-3 mr-1" /> :
              cqcData.trend.toLowerCase().includes('declining') ? <TrendingDown className="w-3 h-3 mr-1" /> :
                <Minus className="w-3 h-3 mr-1" />}
            Trend: {cqcData.trend}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {daysSinceInspection !== undefined && daysSinceInspection !== null && (
          <div className="p-4 rounded-xl bg-gray-50/50 border border-gray-100">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${daysSinceInspection <= 365 ? 'bg-green-100 text-green-600' :
                daysSinceInspection <= 730 ? 'bg-amber-100 text-amber-600' :
                  'bg-red-100 text-red-600'
                }`}>
                <Clock className="w-4 h-4" />
              </div>
              <div>
                <div className="text-[10px] font-bold text-gray-400 uppercase tracking-tighter">Last Inspection</div>
                <div className="text-sm font-bold text-gray-700">
                  {daysSinceInspection} days ago
                </div>
              </div>
            </div>
          </div>
        )}

        {cqcData.provider_locations_count !== undefined && (
          <div className="p-4 rounded-xl bg-gray-50/50 border border-gray-100">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-indigo-100 text-indigo-600">
                <Building2 className="w-4 h-4" />
              </div>
              <div>
                <div className="text-[10px] font-bold text-gray-400 uppercase tracking-tighter">Provider Network</div>
                <div className="text-sm font-bold text-gray-700">
                  {cqcData.provider_locations_count} Active Sites
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="h-[240px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorRating" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={currentRatingColor} stopOpacity={0.3} />
                <stop offset="95%" stopColor={currentRatingColor} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
            <XAxis
              dataKey="year"
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 10, fill: '#647280', fontWeight: 500 }}
              dy={10}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              domain={[0, 4]}
              ticks={[1, 2, 3, 4]}
              tick={{ fontSize: 9, fill: '#475569', fontWeight: 600 }}
              tickFormatter={(value) => numberToRating(value).charAt(0)}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                backdropFilter: 'blur(8px)',
                border: '1px solid #E2E8F0',
                borderRadius: '12px',
                fontSize: '11px',
                fontWeight: 600,
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
              }}
              formatter={(value: number) => [numberToRating(value), 'Rating']}
              labelFormatter={(label) => `Inspection Year: ${label}`}
            />
            <Area
              type="monotone"
              dataKey="rating"
              stroke={currentRatingColor}
              strokeWidth={3}
              fillOpacity={1}
              fill="url(#colorRating)"
              animationDuration={2000}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {recentRatings.length > 0 && (
        <div className="mt-8">
          <h6 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-4">Inspection Ledger</h6>
          <div className="space-y-2">
            {recentRatings.slice(0, 3).map((rating, idx) => {
              const val = rating.rating || rating.overall_rating || 'Unknown';
              const col = getRatingColor(val);
              return (
                <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-gray-50/30 border border-gray-100/50 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: col }}></div>
                    <span className="text-[11px] font-medium text-gray-600">
                      {new Date(rating.date || rating.inspection_date || '').toLocaleDateString('en-GB', { year: 'numeric', month: 'short', day: 'numeric' })}
                    </span>
                  </div>
                  <span className="text-[10px] font-bold px-2.5 py-1 rounded-lg uppercase tracking-wider"
                    style={{ color: col, backgroundColor: `${col}15` }}>
                    {val}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

