import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { TrendingUp, ShieldAlert, DollarSign, Activity } from 'lucide-react';
import type { FinancialStability } from '../types';

interface FinancialStabilityChartProps {
  financialData: FinancialStability;
  homeName: string;
}

export default function FinancialStabilityChart({ financialData, homeName }: FinancialStabilityChartProps) {
  if (!financialData?.three_year_summary) {
    return (
      <div className="glass-card rounded-2xl p-8 border border-gray-100 text-center text-xs text-gray-400 italic">
        Comprehensive financial stability audit data not available for this entity.
      </div>
    );
  }

  // Prepare data for 3-year financial summary
  const summary = financialData.three_year_summary;

  const chartData = [
    {
      year: 'FY23',
      revenue: summary.revenue_year_1 || summary.revenue_3yr_avg || 0,
      profit: summary.profit_year_1 || summary.average_profit || 0,
      margin: summary.net_margin_3yr_avg ? summary.net_margin_3yr_avg * 100 : 0
    },
    {
      year: 'FY24',
      revenue: summary.revenue_year_2 || summary.revenue_3yr_avg || 0,
      profit: summary.profit_year_2 || summary.average_profit || 0,
      margin: summary.net_margin_3yr_avg ? summary.net_margin_3yr_avg * 100 : 0
    },
    {
      year: 'FY25',
      revenue: summary.revenue_year_3 || summary.revenue_3yr_avg || 0,
      profit: summary.profit_year_3 || summary.average_profit || 0,
      margin: summary.net_margin_3yr_avg ? summary.net_margin_3yr_avg * 100 : 0
    }
  ];

  const formatCurrency = (value: number) => {
    if (value >= 1000000) return `£${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `£${(value / 1000).toFixed(0)}k`;
    return `£${value}`;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Financial Performance Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-2 px-2">
        <div>
          <h5 className="text-sm font-bold text-[#1E2A44] uppercase tracking-wider">
            Fiscal Health Diagnostics
          </h5>
          <p className="text-[10px] text-gray-400 font-medium">3-year performance audit for {homeName}</p>
        </div>
        <div className="flex gap-2 mt-2 md:mt-0">
          <div className="flex items-center gap-1.5 px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-[10px] font-bold border border-blue-100">
            <DollarSign className="w-3 h-3" /> Revenue
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1 bg-emerald-50 text-emerald-700 rounded-full text-[10px] font-bold border border-emerald-100">
            <Activity className="w-3 h-3" /> Profit
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Revenue & Profit Trend */}
        <div className="glass-card rounded-2xl p-6 border border-gray-100 shadow-sm transition-all hover:border-blue-100">
          <div className="flex items-center justify-between mb-6">
            <h6 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Revenue vs Profit</h6>
            <TrendingUp className="w-4 h-4 text-gray-300" />
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
              <XAxis
                dataKey="year"
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 10, fill: '#647280', fontWeight: 600 }}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                stroke="#647280"
                tick={{ fontSize: 9, fill: '#647280', fontWeight: 500 }}
                tickFormatter={formatCurrency}
              />
              <Tooltip
                formatter={(value: number) => formatCurrency(value)}
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  backdropFilter: 'blur(8px)',
                  border: '1px solid #E2E8F0',
                  borderRadius: '12px',
                  fontSize: '11px',
                  fontWeight: 600,
                  boxShadow: '0 4px 12px rgba(0,0,0,0.05)'
                }}
              />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#6366F1"
                strokeWidth={4}
                name="Revenue"
                dot={{ r: 4, strokeWidth: 2, fill: '#fff' }}
                activeDot={{ r: 6, strokeWidth: 0 }}
                animationDuration={2000}
              />
              <Line
                type="monotone"
                dataKey="profit"
                stroke="#10B981"
                strokeWidth={4}
                name="Profit"
                dot={{ r: 4, strokeWidth: 2, fill: '#fff' }}
                activeDot={{ r: 6, strokeWidth: 0 }}
                animationDuration={2500}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Profit Margin Bar Chart */}
        <div className="glass-card rounded-2xl p-6 border border-gray-100 shadow-sm transition-all hover:border-indigo-100">
          <div className="flex items-center justify-between mb-6">
            <h6 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Operational Margin %</h6>
            <Activity className="w-4 h-4 text-gray-300" />
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
              <XAxis
                dataKey="year"
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 10, fill: '#647280', fontWeight: 600 }}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                stroke="#647280"
                tick={{ fontSize: 9, fill: '#647280', fontWeight: 500 }}
                tickFormatter={(value) => `${value}%`}
              />
              <Tooltip
                formatter={(value: number) => `${value.toFixed(1)}%`}
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  backdropFilter: 'blur(8px)',
                  border: '1px solid #E2E8F0',
                  borderRadius: '12px',
                  fontSize: '11px',
                  fontWeight: 600
                }}
              />
              <Bar dataKey="margin" radius={[6, 6, 6, 6]} barSize={32}>
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.margin > 12 ? '#10B981' : entry.margin > 7 ? '#6366F1' : '#F59E0B'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bankruptcy Risk Gauge */}
      {financialData.bankruptcy_risk_score !== null && financialData.bankruptcy_risk_score !== undefined && (
        <div className="glass-card rounded-3xl p-8 border border-gray-50 bg-gradient-to-r from-gray-50/50 to-transparent">
          <div className="flex items-start gap-6">
            <div className={`p-4 rounded-2xl ${financialData.bankruptcy_risk_score < 30 ? 'bg-emerald-100 text-emerald-600' :
              financialData.bankruptcy_risk_score < 60 ? 'bg-amber-100 text-amber-600' :
                'bg-rose-100 text-rose-600'
              }`}>
              <ShieldAlert className="w-8 h-8" />
            </div>

            <div className="flex-1">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h6 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Financial Risk Vector</h6>
                  <h4 className="text-xl font-bold text-[#1E2A44] mt-1">{financialData.bankruptcy_risk_level || 'Standard Assessment'}</h4>
                </div>
                <div className="text-right">
                  <span className="text-3xl font-black text-[#1E2A44]">{financialData.bankruptcy_risk_score}</span>
                  <span className="text-sm font-bold text-gray-300 ml-1">/ 100</span>
                </div>
              </div>

              <div className="relative w-full h-3 bg-gray-100 rounded-full overflow-hidden shadow-inner">
                <div
                  className={`absolute top-0 left-0 h-full transition-all duration-1000 ease-out rounded-full shadow-sm ${financialData.bankruptcy_risk_score < 30 ? 'bg-emerald-500' :
                    financialData.bankruptcy_risk_score < 60 ? 'bg-amber-500' :
                      'bg-rose-500'
                    }`}
                  style={{ width: `${Math.min(financialData.bankruptcy_risk_score, 100)}%` }}
                ></div>
              </div>

              <div className="flex justify-between mt-3 px-1">
                <span className="text-[10px] font-bold text-emerald-600 uppercase tracking-tighter">Optimal Stability</span>
                <span className="text-[10px] font-bold text-rose-600 uppercase tracking-tighter">Critical Insolvency</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

