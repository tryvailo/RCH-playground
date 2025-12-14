import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { CheckCircle, XCircle, AlertCircle, Download, DollarSign } from 'lucide-react';
import axios from 'axios';
import type { TestResult, ApiTestResult } from '../types/api.types';
import StatusBadge from '../components/StatusBadge';

export default function Results() {
  const { jobId } = useParams<{ jobId: string }>();
  const [testResult, setTestResult] = useState<TestResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'details' | 'fusion' | 'export'>('overview');

  useEffect(() => {
    if (jobId) {
      loadResults(jobId);
    }
  }, [jobId]);

  const loadResults = async (id: string) => {
    try {
      const response = await axios.get(`/api/test/results/${id}`);
      setTestResult(response.data);
    } catch (error: any) {
      if (error.response?.status === 400) {
        // Test still running, poll again
        setTimeout(() => loadResults(id), 2000);
      } else {
        alert(`Failed to load results: ${error.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12">Loading results...</div>;
  }

  if (!testResult) {
    return <div className="text-center py-12">Results not found</div>;
  }

  const successful = Object.values(testResult.results).filter(r => r.status === 'success').length;
  const failed = Object.values(testResult.results).filter(r => r.status === 'failure').length;
  const partial = Object.values(testResult.results).filter(r => r.status === 'partial').length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Test Results</h1>
        <p className="mt-2 text-gray-600">Job ID: {jobId}</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {(['overview', 'details', 'fusion', 'export'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                activeTab === tab
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <CheckCircle className="w-8 h-8 text-success mr-3" />
                <div>
                  <p className="text-sm text-gray-500">Successful</p>
                  <p className="text-2xl font-bold">{successful}</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <AlertCircle className="w-8 h-8 text-warning mr-3" />
                <div>
                  <p className="text-sm text-gray-500">Partial</p>
                  <p className="text-2xl font-bold">{partial}</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <XCircle className="w-8 h-8 text-danger mr-3" />
                <div>
                  <p className="text-sm text-gray-500">Failed</p>
                  <p className="text-2xl font-bold">{failed}</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <DollarSign className="w-8 h-8 text-primary mr-3" />
                <div>
                  <p className="text-sm text-gray-500">Total Cost</p>
                  <p className="text-2xl font-bold">£{testResult.totalCost.toFixed(2)}</p>
                </div>
              </div>
            </div>
          </div>

          {testResult.fusionAnalysis && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">Risk Assessment</h2>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Overall Risk Score:</span>
                  <span className="font-bold">
                    {testResult.fusionAnalysis.risk_assessment?.overall_score || 0}/100
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Risk Level:</span>
                  <span className={`font-bold ${
                    testResult.fusionAnalysis.risk_assessment?.risk_level === 'HIGH' ? 'text-danger' :
                    testResult.fusionAnalysis.risk_assessment?.risk_level === 'MEDIUM' ? 'text-warning' :
                    'text-success'
                  }`}>
                    {testResult.fusionAnalysis.risk_assessment?.risk_level || 'LOW'}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Details Tab */}
      {activeTab === 'details' && (
        <div className="space-y-4">
          {Object.entries(testResult.results).map(([apiName, result]) => (
            <ApiResultCard key={apiName} apiName={apiName} result={result} />
          ))}
        </div>
      )}

      {/* Fusion Tab */}
      {activeTab === 'fusion' && testResult.fusionAnalysis && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Data Fusion Analysis</h2>
          <pre className="bg-gray-50 p-4 rounded-lg overflow-auto">
            {JSON.stringify(testResult.fusionAnalysis, null, 2)}
          </pre>
        </div>
      )}

      {/* Export Tab */}
      {activeTab === 'export' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Export Results</h2>
          <div className="flex gap-4">
            <button
              onClick={() => {
                const dataStr = JSON.stringify(testResult, null, 2);
                const dataBlob = new Blob([dataStr], { type: 'application/json' });
                const url = URL.createObjectURL(dataBlob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `test-results-${jobId}.json`;
                link.click();
              }}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <Download className="w-4 h-4 mr-2" />
              Export JSON
            </button>
            <button
              onClick={() => {
                // CSV export would go here
                alert('CSV export coming soon');
              }}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function ApiResultCard({ apiName, result }: { apiName: string; result: ApiTestResult }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-semibold">{apiName}</h3>
            <StatusBadge status={result.status === 'success' ? 'connected' : result.status === 'failure' ? 'error' : 'testing'} />
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Response Time:</span>
              <span className="ml-2 font-medium">{result.responseTime.toFixed(2)}s</span>
            </div>
            <div>
              <span className="text-gray-500">Data Returned:</span>
              <span className={`ml-2 font-medium ${result.dataReturned ? 'text-success' : 'text-danger'}`}>
                {result.dataReturned ? 'Yes' : 'No'}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Quality:</span>
              <span className="ml-2 font-medium">{result.dataQuality.completeness}%</span>
            </div>
            <div>
              <span className="text-gray-500">Cost:</span>
              <span className="ml-2 font-medium">£{result.costIncurred.toFixed(4)}</span>
            </div>
          </div>
          {result.errors.length > 0 && (
            <div className="mt-3 p-3 bg-danger/10 rounded-md">
              <p className="text-sm font-medium text-danger">Errors:</p>
              <ul className="list-disc list-inside text-sm text-gray-700 mt-1">
                {result.errors.map((error, idx) => (
                  <li key={idx}>{error}</li>
                ))}
              </ul>
            </div>
          )}
          {result.warnings.length > 0 && (
            <div className="mt-3 p-3 bg-warning/10 rounded-md">
              <p className="text-sm font-medium text-warning">Warnings:</p>
              <ul className="list-disc list-inside text-sm text-gray-700 mt-1">
                {result.warnings.map((warning, idx) => (
                  <li key={idx}>{warning}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="ml-4 text-sm text-info hover:text-blue-700"
        >
          {expanded ? 'Hide' : 'Show'} Raw
        </button>
      </div>
      {expanded && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <pre className="text-xs overflow-auto">
            {JSON.stringify(result.rawResponse, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

