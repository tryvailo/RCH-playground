import { useState, useEffect } from 'react';
import { RefreshCw, Database, TrendingUp, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import axios from 'axios';

interface UpdateStatus {
  id: number;
  data_source: string;
  status: string;
  records_updated: number | null;
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
  error_message: string | null;
}

export default function DataIngestionAdmin() {
  const [loading, setLoading] = useState(false);
  const [statusLoading, setStatusLoading] = useState(false);
  const [updates, setUpdates] = useState<UpdateStatus[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const fetchStatus = async () => {
    setStatusLoading(true);
    try {
      const response = await axios.get('/api/rch-data/data-ingestion/status');
      if (response.data.status === 'success') {
        setUpdates(response.data.updates || []);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch status');
    } finally {
      setStatusLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleInitDB = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const response = await axios.post('/api/rch-data/data-ingestion/init-db');
      setSuccess(response.data.message || 'Database initialized successfully');
      await fetchStatus();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to initialize database');
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshMSIF = async (year: number) => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const response = await axios.post('/api/rch-data/data-ingestion/refresh-msif', { year });
      if (response.data.status === 'success') {
        setSuccess(
          `${response.data.data_source} updated successfully! Records: ${response.data.records_updated}`
        );
        await fetchStatus();
      } else {
        setError(response.data.error || 'Failed to refresh MSIF data');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to refresh MSIF data');
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshLottie = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const response = await axios.post('/api/rch-data/data-ingestion/refresh-lottie');
      if (response.data.status === 'success') {
        setSuccess(
          `${response.data.data_source} updated successfully! Records: ${response.data.records_updated}`
        );
        await fetchStatus();
      } else {
        setError(response.data.error || 'Failed to refresh Lottie data');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to refresh Lottie data');
    } finally {
      setLoading(false);
    }
  };

  const successCount = updates.filter((u) => u.status === 'success').length;
  const failedCount = updates.filter((u) => u.status === 'failed').length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">📊 Data Ingestion Admin</h1>
        <p className="mt-2 text-gray-600">Manage MSIF and Lottie data updates</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <span className="text-red-800">{error}</span>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-green-600" />
          <span className="text-green-800">{success}</span>
        </div>
      )}

      {/* Initialize Database */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <Database className="w-5 h-5 text-blue-600" />
          <h2 className="text-xl font-semibold">Database Initialization</h2>
        </div>
        <button
          onClick={handleInitDB}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
        >
          {loading ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <Database className="w-4 h-4" />
          )}
          Initialize Database Tables
        </button>
      </div>

      {/* MSIF Data Refresh */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">MSIF Data Refresh</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => handleRefreshMSIF(2025)}
            disabled={loading}
            className="px-4 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
            Refresh MSIF 2025-2026
          </button>
          <button
            onClick={() => handleRefreshMSIF(2024)}
            disabled={loading}
            className="px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
            Refresh MSIF 2024-2025
          </button>
        </div>
      </div>

      {/* Lottie Data Refresh */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Lottie Regional Averages</h2>
        <button
          onClick={handleRefreshLottie}
          disabled={loading}
          className="px-4 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark disabled:opacity-50 flex items-center gap-2"
        >
          {loading ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4" />
          )}
          Refresh Lottie Data
        </button>
      </div>

      {/* Update Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-green-600" />
            Update Status
          </h2>
          <button
            onClick={fetchStatus}
            disabled={statusLoading}
            className="px-3 py-1 text-sm bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 flex items-center gap-2"
          >
            {statusLoading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
            Refresh
          </button>
        </div>

        {updates.length > 0 ? (
          <>
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Total Updates</div>
                <div className="text-2xl font-bold">{updates.length}</div>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Successful</div>
                <div className="text-2xl font-bold text-green-600">
                  {successCount}/{updates.length}
                </div>
              </div>
              <div className="bg-red-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Failed</div>
                <div className="text-2xl font-bold text-red-600">{failedCount}</div>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      ID
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Data Source
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Status
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Records
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Started
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Completed
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Duration
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Error
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {updates.map((update) => (
                    <tr key={update.id}>
                      <td className="px-4 py-3 text-sm">{update.id}</td>
                      <td className="px-4 py-3 text-sm font-medium">{update.data_source}</td>
                      <td className="px-4 py-3 text-sm">
                        {update.status === 'success' ? (
                          <span className="flex items-center gap-1 text-green-600">
                            <CheckCircle className="w-4 h-4" />
                            Success
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-red-600">
                            <AlertCircle className="w-4 h-4" />
                            Failed
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm">{update.records_updated || 0}</td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {update.started_at
                          ? new Date(update.started_at).toLocaleString()
                          : 'N/A'}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {update.completed_at
                          ? new Date(update.completed_at).toLocaleString()
                          : 'N/A'}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {update.duration_seconds ? `${update.duration_seconds}s` : 'N/A'}
                      </td>
                      <td className="px-4 py-3 text-sm text-red-600">
                        {update.error_message || '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No update logs found. Run a refresh to see status.
          </div>
        )}
      </div>
    </div>
  );
}

