import { useEffect, useState } from 'react';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c', '#34495e'];

export default function Analytics() {
  const [loading, setLoading] = useState(true);

  // Note: Currently using sample data. In production, this would come from backend analytics service
  // TODO: Connect to /api/analyze/coverage and /api/analyze/quality endpoints when implemented
  const apiReliabilityData = [
    { name: 'CQC', reliability: 95 },
    { name: 'FSA', reliability: 98 },
    { name: 'Companies House', reliability: 92 },
    { name: 'Google Places', reliability: 90 },
    { name: 'Perplexity', reliability: 88 },
    { name: 'BestTime', reliability: 75 },
    { name: 'Autumna', reliability: 70 },
  ];

  const responseTimeData = [
    { name: 'CQC', time: 0.8 },
    { name: 'FSA', time: 0.5 },
    { name: 'Companies House', time: 1.2 },
    { name: 'Google Places', time: 1.5 },
    { name: 'Perplexity', time: 3.0 },
    { name: 'BestTime', time: 5.0 },
    { name: 'Autumna', time: 8.0 },
  ];

  const costData = [
    { name: 'Google Places', value: 0.43 },
    { name: 'Perplexity', value: 0.25 },
    { name: 'BestTime', value: 0.40 },
    { name: 'Autumna', value: 0.50 },
  ];

  useEffect(() => {
    // Load analytics data from backend
    setLoading(false);
  }, []);

  if (loading) {
    return <div className="text-center py-12">Loading analytics...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
        <p className="mt-2 text-gray-600">Performance metrics and insights</p>
      </div>

      {/* API Reliability Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">API Reliability Over Time</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={apiReliabilityData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="reliability" fill="#3498db" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Response Time Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Response Time Comparison</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={responseTimeData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="time" fill="#2ecc71" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Cost Breakdown */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Cost Breakdown</h2>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={costData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {costData.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Insights */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Key Insights</h2>
        <div className="space-y-3">
          <div className="p-3 bg-success/10 rounded-lg">
            <p className="font-medium text-success">✓ Best Performing API</p>
            <p className="text-sm text-gray-700">FSA API has the highest reliability (98%)</p>
          </div>
          <div className="p-3 bg-warning/10 rounded-lg">
            <p className="font-medium text-warning">⚠ Most Expensive API</p>
            <p className="text-sm text-gray-700">Google Places accounts for the highest costs</p>
          </div>
          <div className="p-3 bg-info/10 rounded-lg">
            <p className="font-medium text-info">💡 Coverage Gaps</p>
            <p className="text-sm text-gray-700">BestTime and Autumna have lower coverage rates for rural locations</p>
          </div>
        </div>
      </div>
    </div>
  );
}

