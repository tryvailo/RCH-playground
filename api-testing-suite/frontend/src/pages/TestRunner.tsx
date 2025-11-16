import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, Loader } from 'lucide-react';
import axios from 'axios';
import { useTestStore } from '../stores/testStore';
import { TEST_HOMES } from '../types/api.types';
import type { ComprehensiveTestRequest } from '../types/api.types';

const AVAILABLE_APIS = [
  { id: 'cqc', name: 'CQC', description: 'Care Quality Commission' },
  { id: 'fsa', name: 'FSA', description: 'Food Standards Agency' },
  { id: 'companies_house', name: 'Companies House', description: 'Company financial data' },
  { id: 'google_places', name: 'Google Places', description: 'Reviews and ratings' },
  { id: 'perplexity', name: 'Perplexity', description: 'News and reputation' },
  { id: 'besttime', name: 'BestTime', description: 'Footfall analytics' },
  { id: 'autumna', name: 'Autumna', description: 'Pricing and amenities' },
];

export default function TestRunner() {
  const navigate = useNavigate();
  const { setCurrentTest } = useTestStore();
  const [selectedApis, setSelectedApis] = useState<string[]>(AVAILABLE_APIS.map(a => a.id));
  const [homeData, setHomeData] = useState({
    name: TEST_HOMES[0].name,
    address: TEST_HOMES[0].address || '',
    city: TEST_HOMES[0].city || '',
    postcode: TEST_HOMES[0].postcode || '',
  });
  const [useTestData, setUseTestData] = useState(true);
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentApi, setCurrentApi] = useState<string | null>(null);

  const handleApiToggle = (apiId: string) => {
    setSelectedApis((prev) =>
      prev.includes(apiId) ? prev.filter((id) => id !== apiId) : [...prev, apiId]
    );
  };

  const handleLoadTestData = (home: typeof TEST_HOMES[0]) => {
    setHomeData({
      name: home.name,
      address: home.address || '',
      city: home.city || '',
      postcode: home.postcode || '',
    });
  };

  const handleRunTest = async () => {
    if (selectedApis.length === 0) {
      alert('Please select at least one API to test');
      return;
    }

    setRunning(true);
    setProgress(0);
    setCurrentApi(null);

    try {
      const request: ComprehensiveTestRequest = {
        homeName: homeData.name,
        address: homeData.address || undefined,
        city: homeData.city || undefined,
        postcode: homeData.postcode || undefined,
        apisToTest: selectedApis,
      };

      const response = await axios.post('/api/test/comprehensive', request);
      const jobId = response.data.job_id;

      // Set up WebSocket connection for progress updates
      const ws = new WebSocket(`ws://localhost:8000/ws/test-progress`);
      
      ws.onmessage = async (event) => {
        const data = JSON.parse(event.data);
        if (data.job_id === jobId) {
          if (data.event === 'progress') {
            setProgress(data.data.progress || 0);
            setCurrentApi(data.data.current_api || null);
          } else if (data.event === 'completed') {
            setProgress(100);
            setRunning(false);
            ws.close();
            
            // Load results and navigate
            try {
              const resultsResponse = await axios.get(`/api/test/results/${jobId}`);
              setCurrentTest(resultsResponse.data);
              navigate(`/results/${jobId}`);
            } catch (error) {
              console.error('Failed to load results:', error);
              alert('Test completed but failed to load results');
            }
          } else if (data.event === 'failed') {
            setRunning(false);
            ws.close();
            alert(`Test failed: ${data.data.error}`);
          }
        }
      };

      // Poll for results if WebSocket fails
      const pollInterval = setInterval(async () => {
        try {
          const statusResponse = await axios.get(`/api/test/status/${jobId}`);
          const status = statusResponse.data.status;
          
          if (status === 'completed') {
            clearInterval(pollInterval);
            setProgress(100);
            setRunning(false);
            const resultsResponse = await axios.get(`/api/test/results/${jobId}`);
            setCurrentTest(resultsResponse.data);
            navigate(`/results/${jobId}`);
          } else if (status === 'failed') {
            clearInterval(pollInterval);
            setRunning(false);
            alert(`Test failed: ${statusResponse.data.error}`);
          } else {
            setProgress(statusResponse.data.progress || 0);
            setCurrentApi(statusResponse.data.current_api || null);
          }
        } catch (error) {
          console.error('Polling error:', error);
        }
      }, 2000);

      // Cleanup polling after 5 minutes
      setTimeout(() => clearInterval(pollInterval), 300000);

    } catch (error: any) {
      setRunning(false);
      alert(`Failed to start test: ${error.response?.data?.detail || error.message}`);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Test Runner</h1>
        <p className="mt-2 text-gray-600">Run comprehensive tests across all APIs</p>
      </div>

      {/* API Selection */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Select APIs to Test</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {AVAILABLE_APIS.map((api) => (
            <label
              key={api.id}
              className="flex items-center p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50"
            >
              <input
                type="checkbox"
                checked={selectedApis.includes(api.id)}
                onChange={() => handleApiToggle(api.id)}
                className="mr-3"
              />
              <div>
                <div className="font-medium text-gray-900">{api.name}</div>
                <div className="text-sm text-gray-500">{api.description}</div>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Test Data */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Test Data</h2>
        
        <div className="mb-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={useTestData}
              onChange={(e) => setUseTestData(e.target.checked)}
              className="mr-2"
            />
            <span className="text-sm text-gray-700">Use test data</span>
          </label>
        </div>

        {useTestData && (
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <p className="text-sm font-medium text-gray-700 mb-2">Quick Select:</p>
            <div className="flex flex-wrap gap-2">
              {TEST_HOMES.map((home, idx) => (
                <button
                  key={idx}
                  onClick={() => handleLoadTestData(home)}
                  className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-100"
                >
                  {home.name}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Home Name *
            </label>
            <input
              type="text"
              value={homeData.name}
              onChange={(e) => setHomeData({ ...homeData, name: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
            <input
              type="text"
              value={homeData.city}
              onChange={(e) => setHomeData({ ...homeData, city: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
            <input
              type="text"
              value={homeData.address}
              onChange={(e) => setHomeData({ ...homeData, address: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Postcode</label>
            <input
              type="text"
              value={homeData.postcode}
              onChange={(e) => setHomeData({ ...homeData, postcode: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>
        </div>
      </div>

      {/* Progress */}
      {running && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-semibold">Running Tests...</h3>
            <span className="text-sm text-gray-500">{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
            <div
              className="bg-primary h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          {currentApi && (
            <p className="text-sm text-gray-600">Testing: {currentApi}</p>
          )}
        </div>
      )}

      {/* Run Button */}
      <div className="flex justify-end">
        <button
          onClick={handleRunTest}
          disabled={running || selectedApis.length === 0}
          className="inline-flex items-center px-6 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-purple-700 disabled:opacity-50"
        >
          {running ? (
            <>
              <Loader className="w-4 h-4 mr-2 animate-spin" />
              Running...
            </>
          ) : (
            <>
              <Play className="w-4 h-4 mr-2" />
              Run Comprehensive Test
            </>
          )}
        </button>
      </div>
    </div>
  );
}

