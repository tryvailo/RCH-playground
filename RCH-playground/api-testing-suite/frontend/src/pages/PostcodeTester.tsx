import { useState } from 'react';
import { MapPin, Search, AlertCircle, CheckCircle, Upload } from 'lucide-react';
import axios from 'axios';

interface PostcodeInfo {
  postcode: string;
  local_authority: string;
  region: string;
  latitude?: number;
  longitude?: number;
  country?: string;
  county?: string;
}

export default function PostcodeTester() {
  const [loading, setLoading] = useState(false);
  const [batchLoading, setBatchLoading] = useState(false);
  const [singleResult, setSingleResult] = useState<PostcodeInfo | null>(null);
  const [batchResults, setBatchResults] = useState<PostcodeInfo[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [batchError, setBatchError] = useState<string | null>(null);

  const [singlePostcode, setSinglePostcode] = useState('B15 2HQ');
  const [batchPostcodes, setBatchPostcodes] = useState('');

  const handleSingleResolve = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSingleResult(null);

    try {
      const response = await axios.post('/api/rch-data/postcode/resolve', {
        postcode: singlePostcode,
      });
      setSingleResult(response.data);
    } catch (err: any) {
      console.error('Error resolving postcode:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to resolve postcode';
      
      if (errorMessage.includes('not available') || err.response?.status === 503) {
        setError(
          'Postcode resolver module is not available. Please ensure RCH-data package is installed: pip install -e ../RCH-data'
        );
      } else if (!err.response) {
        setError('Cannot connect to backend server. Please ensure the server is running on http://localhost:8000');
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleBatchResolve = async (e: React.FormEvent) => {
    e.preventDefault();
    setBatchLoading(true);
    setBatchError(null);
    setBatchResults([]);

    try {
      const postcodes = batchPostcodes
        .split('\n')
        .map((p) => p.trim())
        .filter((p) => p.length > 0);

      if (postcodes.length === 0) {
        setBatchError('Please enter at least one postcode');
        return;
      }

      const response = await axios.post('/api/rch-data/postcode/batch', {
        postcodes,
      });
      // BatchPostcodeResponse has structure: { results: [...], total: N, found: N, not_found: N }
      const results = response.data.results || [];
      setBatchResults(Array.isArray(results) ? results.filter(r => r !== null) : []);
    } catch (err: any) {
      console.error('Error resolving postcodes batch:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to resolve postcodes';
      
      if (errorMessage.includes('not available') || err.response?.status === 503) {
        setBatchError(
          'Postcode resolver module is not available. Please ensure RCH-data package is installed: pip install -e ../RCH-data'
        );
      } else if (!err.response) {
        setBatchError('Cannot connect to backend server. Please ensure the server is running on http://localhost:8000');
      } else {
        setBatchError(errorMessage);
      }
    } finally {
      setBatchLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <MapPin className="w-8 h-8" />
          Postcode Resolver Tester
        </h1>
        <p className="mt-2 text-gray-600">
          Resolve UK postcodes to Local Authority and Region with map visualization
        </p>
      </div>

      {/* Single Postcode Resolver */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Single Postcode Resolver</h2>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2 mb-4">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <span className="text-red-800">{error}</span>
          </div>
        )}

        <form onSubmit={handleSingleResolve} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Enter UK Postcode
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={singlePostcode}
                onChange={(e) => setSinglePostcode(e.target.value.toUpperCase())}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="e.g., B15 2HQ, SW1A 1AA, M1 1AA"
                required
              />
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark disabled:opacity-50 flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Resolving...
                  </>
                ) : (
                  <>
                    <Search className="w-5 h-5" />
                    Resolve
                  </>
                )}
              </button>
            </div>
          </div>
        </form>

        {singleResult && (
          <div className="mt-6 space-y-4">
            <div className="flex items-center gap-2 text-green-600">
              <CheckCircle className="w-5 h-5" />
              <span className="font-semibold">Postcode resolved successfully!</span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Local Authority</div>
                <div className="text-lg font-semibold">{singleResult.local_authority}</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Region</div>
                <div className="text-lg font-semibold">{singleResult.region}</div>
              </div>
              {singleResult.latitude && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Latitude</div>
                  <div className="text-lg font-semibold">{singleResult.latitude.toFixed(6)}</div>
                </div>
              )}
              {singleResult.longitude && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-600">Longitude</div>
                  <div className="text-lg font-semibold">{singleResult.longitude.toFixed(6)}</div>
                </div>
              )}
            </div>

            {singleResult.latitude && singleResult.longitude && (
              <div className="mt-4">
                <div className="text-sm text-gray-600 mb-2">Map Location</div>
                <div className="bg-gray-100 rounded-lg p-4 text-center">
                  <a
                    href={`https://www.google.com/maps?q=${singleResult.latitude},${singleResult.longitude}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline flex items-center justify-center gap-2"
                  >
                    <MapPin className="w-5 h-5" />
                    View on Google Maps
                  </a>
                </div>
              </div>
            )}

            <div className="mt-4">
              <details className="bg-gray-50 rounded-lg p-4">
                <summary className="cursor-pointer font-medium">Full Details</summary>
                <pre className="mt-2 text-xs overflow-auto">
                  {JSON.stringify(singleResult, null, 2)}
                </pre>
              </details>
            </div>
          </div>
        )}
      </div>

      {/* Batch Postcode Resolver */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Batch Postcode Resolver</h2>

        {batchError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2 mb-4">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <span className="text-red-800">{batchError}</span>
          </div>
        )}

        <form onSubmit={handleBatchResolve} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Enter Postcodes (one per line)
            </label>
            <textarea
              value={batchPostcodes}
              onChange={(e) => setBatchPostcodes(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm"
              rows={6}
              placeholder="B15 2HQ&#10;SW1A 1AA&#10;M1 1AA&#10;..."
            />
            <p className="mt-1 text-xs text-gray-500">
              Enter one postcode per line. Empty lines will be ignored.
            </p>
          </div>

          <button
            type="submit"
            disabled={batchLoading}
            className="w-full px-4 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {batchLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Resolving...
              </>
            ) : (
              <>
                <Upload className="w-5 h-5" />
                Resolve Batch
              </>
            )}
          </button>
        </form>

        {batchResults.length > 0 && (
          <div className="mt-6">
            <div className="flex items-center gap-2 text-green-600 mb-4">
              <CheckCircle className="w-5 h-5" />
              <span className="font-semibold">
                Resolved {batchResults.length} postcode{batchResults.length !== 1 ? 's' : ''}
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Postcode
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Local Authority
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Region
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Coordinates
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {batchResults.map((result, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium">{result.postcode}</td>
                      <td className="px-4 py-3 text-sm">{result.local_authority}</td>
                      <td className="px-4 py-3 text-sm">{result.region}</td>
                      <td className="px-4 py-3 text-sm">
                        {result.latitude && result.longitude ? (
                          <a
                            href={`https://www.google.com/maps?q=${result.latitude},${result.longitude}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary hover:underline"
                          >
                            {result.latitude.toFixed(4)}, {result.longitude.toFixed(4)}
                          </a>
                        ) : (
                          'N/A'
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

