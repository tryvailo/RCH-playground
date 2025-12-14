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
    console.log('🚀 handleRunTest called');
    console.log('📋 Selected APIs:', selectedApis);
    console.log('📋 Home data:', homeData);
    
    if (selectedApis.length === 0) {
      alert('Please select at least one API to test');
      return;
    }

    if (!homeData.name || homeData.name.trim() === '') {
      alert('Please enter a home name');
      return;
    }

    setRunning(true);
    setProgress(0);
    setCurrentApi(null);

    try {
      // Check if backend is available first (try through proxy)
      console.log('🔍 Checking backend availability on /health...');
      try {
        const healthCheck = await axios.get('/health', { 
          timeout: 3000,
          validateStatus: (status) => status < 500 // Accept any status < 500 as "available"
        });
        console.log('✅ Backend is available on port 8000:', healthCheck.data);
      } catch (healthError: any) {
        console.error('❌ Backend is not available');
        console.error('Health check error:', healthError.message);
        console.error('Error code:', healthError.code);
        setRunning(false);
        alert('Backend server is not running or not accessible on port 8000.\n\nPlease ensure the backend server is started with:\n\ncd api-testing-suite/backend\n./venv/bin/python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000\n\nOr check if the server is already running on a different port.');
        return;
      }

      const request: ComprehensiveTestRequest = {
        homeName: homeData.name.trim(),
        address: homeData.address?.trim() || undefined,
        city: homeData.city?.trim() || undefined,
        postcode: homeData.postcode?.trim() || undefined,
        apisToTest: selectedApis,
      };

      console.log('📤 Sending request to /api/test/comprehensive:', request);
      console.log('📤 Request URL:', '/api/test/comprehensive');
      console.log('📤 Request timestamp:', new Date().toISOString());
      
      // Add timeout to prevent hanging
      const requestStartTime = Date.now();
      let response;
      try {
        response = await axios.post('/api/test/comprehensive', request, {
          timeout: 30000, // 30 seconds timeout
          headers: {
            'Content-Type': 'application/json',
          },
        });
        const requestDuration = Date.now() - requestStartTime;
        console.log(`✅ Response received in ${requestDuration}ms`);
        console.log('✅ Response status:', response.status);
        console.log('✅ Response data:', response.data);
      } catch (axiosError: any) {
        const requestDuration = Date.now() - requestStartTime;
        console.error(`❌ Request failed after ${requestDuration}ms`);
        console.error('❌ Axios error:', axiosError);
        console.error('❌ Error message:', axiosError.message);
        console.error('❌ Error response:', axiosError.response);
        console.error('❌ Error code:', axiosError.code);
        throw axiosError; // Re-throw to be caught by outer catch
      }
      const jobId = response.data.job_id;
      console.log('✅ Test started with job_id:', jobId);
      console.log('📋 Response:', response.data);

      // Set up WebSocket connection for progress updates (optional - polling is fallback)
      let ws: WebSocket | null = null;
      let wsConnected = false;
      
      try {
        // Use direct backend connection (more reliable than vite proxy for WebSocket)
        const wsProtocol = 'ws:';
        const backendHost = 'localhost:8000';
        ws = new WebSocket(`${wsProtocol}//${backendHost}/ws/test-progress`);
        
        ws.onerror = (error) => {
          console.warn('WebSocket connection failed, using polling instead');
          console.debug('WebSocket error details:', error);
          wsConnected = false;
          // Don't stop execution - polling will handle it
        };

        ws.onopen = () => {
          console.log('WebSocket connected for job:', jobId);
          wsConnected = true;
          // Send job_id to subscribe to updates
          try {
            ws?.send(JSON.stringify({ job_id: jobId }));
          } catch (e) {
            console.warn('Failed to send job_id to WebSocket:', e);
          }
        };

        ws.onclose = (event) => {
          console.log('WebSocket closed', event.code, event.reason);
          wsConnected = false;
        };

        ws.onmessage = async (event) => {
          try {
            const data = JSON.parse(event.data);
            
            // Handle initial connection message
            if (data.type === 'connected') {
              console.log('WebSocket connection confirmed');
              return;
            }
            
            if (data.job_id === jobId) {
              if (data.event === 'progress') {
                setProgress(data.data.progress || 0);
                setCurrentApi(data.data.current_api || null);
              } else if (data.event === 'completed') {
                setProgress(100);
                setRunning(false);
                ws?.close();
                ws = null;
                
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
                ws?.close();
                ws = null;
                alert(`Test failed: ${data.data.error}`);
              }
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };
      } catch (error) {
        console.warn('Failed to create WebSocket, using polling only:', error);
        ws = null;
        wsConnected = false;
      }

      // Poll for results (always runs, WebSocket is optional enhancement)
      const pollInterval = setInterval(async () => {
        try {
          console.log(`📊 Polling status for job: ${jobId}`);
          const statusResponse = await axios.get(`/api/test/status/${jobId}`);
          const status = statusResponse.data.status;
          console.log(`📈 Status: ${status}, Progress: ${statusResponse.data.progress}%`);
          
          if (status === 'completed') {
            clearInterval(pollInterval);
            if (ws) {
              ws.close();
              ws = null;
            }
            setProgress(100);
            setRunning(false);
            const resultsResponse = await axios.get(`/api/test/results/${jobId}`);
            setCurrentTest(resultsResponse.data);
            navigate(`/results/${jobId}`);
          } else if (status === 'failed') {
            clearInterval(pollInterval);
            if (ws) {
              ws.close();
              ws = null;
            }
            setRunning(false);
            alert(`Test failed: ${statusResponse.data.error}`);
          } else {
            // Update progress if available (only if WebSocket didn't update it)
            if (!wsConnected) {
              setProgress(statusResponse.data.progress || 0);
              setCurrentApi(statusResponse.data.current_api || null);
            }
          }
        } catch (error) {
          console.error('❌ Polling error:', error);
          console.error('Error details:', {
            message: error.message,
            status: error.response?.status,
            statusText: error.response?.statusText,
            data: error.response?.data,
            jobId: jobId
          });
        }
      }, 2000);

      // Cleanup polling after 5 minutes
      setTimeout(() => clearInterval(pollInterval), 300000);

    } catch (error: any) {
      console.error('❌ Error in handleRunTest:', error);
      console.error('Error details:', {
        message: error.message,
        code: error.code,
        response: error.response,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        stack: error.stack
      });
      setRunning(false);
      setProgress(0);
      setCurrentApi(null);
      
      // Handle network errors specifically
      if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
        alert('Network Error: Cannot connect to backend server.\n\nPlease ensure:\n1. Backend server is running on port 8000\n2. No firewall is blocking the connection\n3. Try restarting the backend server');
        return;
      }
      
      if (error.code === 'ECONNREFUSED' || error.message?.includes('ERR_CONNECTION_REFUSED')) {
        alert('Connection Refused: Backend server is not running.\n\nPlease start the backend server with:\ncd backend && ./venv/bin/python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000');
        return;
      }
      
      if (error.code === 'ETIMEDOUT' || error.message?.includes('timeout')) {
        alert('Request Timeout: Backend server did not respond in time.\n\nThis might indicate:\n1. Backend server is overloaded\n2. Backend server is stuck processing a request\n3. Network issues\n\nTry restarting the backend server.');
        return;
      }
      
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Unknown error';
      alert(`Failed to start test: ${errorMessage}`);
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
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('🔘 Button clicked, calling handleRunTest');
            handleRunTest();
          }}
          disabled={running || selectedApis.length === 0 || !homeData.name?.trim()}
          className="inline-flex items-center px-6 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
          type="button"
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

