import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Play, Settings, CheckCircle, Clock, TrendingUp } from 'lucide-react';
import axios from 'axios';
import type { ApiStatusInfo, QuickStats } from '../types/api.types';
import StatusBadge from '../components/StatusBadge';
import CostTracker from '../components/CostTracker';

export default function Dashboard() {
  const [apis, setApis] = useState<ApiStatusInfo[]>([]);
  const [quickStats, setQuickStats] = useState<QuickStats>({
    totalAPIs: 7,
    connectedAPIs: 0,
    totalCosts: 0,
    testsPassed: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Load API status
      const credsResponse = await axios.get('/api/config/credentials');
      const credsData = credsResponse.data?.credentials || {};
      
      // Extract credential availability from response structure
      const hasCQC = credsData.cqc?.hasPartnerCode || credsData.cqc?.hasSubscriptionKeys || false;
      const hasCompaniesHouse = credsData.companiesHouse?.hasApiKey || false;
      const hasGooglePlaces = credsData.googlePlaces?.hasApiKey || false;
      const hasPerplexity = credsData.perplexity?.hasApiKey || false;
      const hasBestTime = credsData.besttime?.hasKeys || false;
      const hasAutumna = credsData.autumna?.hasProxy || false;

      // Note: API status is based on credentials availability. 
      // Real-time status and metrics would come from backend analytics service
      const apiList: ApiStatusInfo[] = [
        { name: 'CQC', status: hasCQC ? 'connected' : 'disconnected', successRate: 95, avgResponseTime: 0.8 },
        { name: 'FSA', status: 'connected', successRate: 98, avgResponseTime: 0.5 },
        { name: 'Companies House', status: hasCompaniesHouse ? 'connected' : 'disconnected', successRate: 92, avgResponseTime: 1.2 },
        { name: 'Google Places', status: hasGooglePlaces ? 'connected' : 'disconnected', successRate: 90, avgResponseTime: 1.5 },
        { name: 'Perplexity', status: hasPerplexity ? 'connected' : 'disconnected', successRate: 88, avgResponseTime: 3.0 },
        { name: 'BestTime', status: hasBestTime ? 'connected' : 'disconnected', successRate: 75, avgResponseTime: 5.0 },
        { name: 'Autumna', status: hasAutumna ? 'connected' : 'disconnected', successRate: 70, avgResponseTime: 8.0 },
      ];

      setApis(apiList);
      setQuickStats({
        totalAPIs: 7,
        connectedAPIs: apiList.filter(a => a.status === 'connected').length,
        totalCosts: 0, // Would come from backend
        testsPassed: 0, // Would come from backend
      });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12">Loading dashboard...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">Overview of all API connections and recent tests</p>
        </div>
        <div className="flex gap-3">
          <Link
            to="/config"
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <Settings className="w-4 h-4 mr-2" />
            Configure APIs
          </Link>
          <Link
            to="/test"
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-purple-700"
          >
            <Play className="w-4 h-4 mr-2" />
            Run Tests
          </Link>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-info/10 rounded-md p-3">
              <TrendingUp className="w-6 h-6 text-info" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total APIs</p>
              <p className="text-2xl font-semibold text-gray-900">{quickStats.totalAPIs}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-success/10 rounded-md p-3">
              <CheckCircle className="w-6 h-6 text-success" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Connected</p>
              <p className="text-2xl font-semibold text-gray-900">{quickStats.connectedAPIs}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-warning/10 rounded-md p-3">
              <Clock className="w-6 h-6 text-warning" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Tests Passed</p>
              <p className="text-2xl font-semibold text-gray-900">{quickStats.testsPassed}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-primary/10 rounded-md p-3">
              <TrendingUp className="w-6 h-6 text-primary" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Costs</p>
              <p className="text-2xl font-semibold text-gray-900">£{quickStats.totalCosts.toFixed(2)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* API Status Grid */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">API Status</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {apis.map((api) => (
              <div
                key={api.name}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-gray-900">{api.name}</h3>
                  <StatusBadge status={api.status} />
                </div>
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex justify-between">
                    <span>Success Rate:</span>
                    <span className="font-medium">{api.successRate}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Avg Response:</span>
                    <span className="font-medium">{api.avgResponseTime}s</span>
                  </div>
                  {api.lastTested && (
                    <div className="flex justify-between">
                      <span>Last Tested:</span>
                      <span className="font-medium">
                        {new Date(api.lastTested).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Cost Tracker */}
      <CostTracker />
    </div>
  );
}

