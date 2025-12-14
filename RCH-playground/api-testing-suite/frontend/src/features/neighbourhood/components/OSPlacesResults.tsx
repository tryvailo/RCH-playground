import { Building2, MapPin, Hash, Map, Clock, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';
import type { OSPlacesResult, OSPlacesAddress } from '../types';

interface Props {
  data: OSPlacesResult;
}

export default function OSPlacesResults({ data }: Props) {
  const [showAllAddresses, setShowAllAddresses] = useState(false);
  
  if (data.error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <Building2 className="w-5 h-5 text-red-600" />
          </div>
          <div className="flex-1">
            <h4 className="font-medium text-red-800 mb-1">OS Places API Error</h4>
            <p className="text-sm text-red-700">{data.error}</p>
            {data.error === 'Invalid API key' && (
              <div className="mt-3 space-y-2">
                <p className="text-xs text-red-600 font-medium">To fix this issue:</p>
                <ol className="text-xs text-red-600 list-decimal list-inside space-y-1 ml-2">
                  <li>Get an OS Data Hub API key from <a href="https://osdatahub.os.uk/" target="_blank" rel="noopener noreferrer" className="underline">osdatahub.os.uk</a></li>
                  <li>Add it to <code className="bg-red-100 px-1 rounded">backend/config.json</code> in the <code className="bg-red-100 px-1 rounded">os_places</code> section:</li>
                </ol>
                <pre className="text-xs bg-red-100 p-2 rounded mt-2 overflow-x-auto">
{`{
  "os_places": {
    "api_key": "YOUR_API_KEY",
    "api_secret": "YOUR_API_SECRET"
  }
}`}
                </pre>
                <p className="text-xs text-gray-600 mt-2">
                  <strong>Note:</strong> If OS Places is not available, the system will attempt to use ONS data for coordinates when analyzing neighbourhoods.
                </p>
              </div>
            )}
            {data.error !== 'Invalid API key' && data.error.includes('API key') && (
              <p className="text-xs text-red-600 mt-2">
                Please check your OS Places API key configuration in <code className="bg-red-100 px-1 rounded">backend/config.json</code>
              </p>
            )}
            {data.postcode && (
              <p className="text-xs text-gray-600 mt-2">Postcode: {data.postcode}</p>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Ensure addresses array exists
  const addresses = data.addresses || [];
  const displayAddresses = showAllAddresses 
    ? addresses 
    : addresses.slice(0, 5);

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center gap-2 text-blue-600 mb-1">
            <MapPin className="w-4 h-4" />
            <span className="text-sm font-medium">Postcode</span>
          </div>
          <div className="text-xl font-bold">{data.postcode}</div>
        </div>
        
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center gap-2 text-blue-600 mb-1">
            <Building2 className="w-4 h-4" />
            <span className="text-sm font-medium">Addresses Found</span>
          </div>
          <div className="text-xl font-bold">{data.address_count || 0}</div>
        </div>
        
        {data.centroid && (
          <>
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center gap-2 text-blue-600 mb-1">
                <Map className="w-4 h-4" />
                <span className="text-sm font-medium">Latitude</span>
              </div>
              <div className="text-lg font-mono">{data.centroid.latitude.toFixed(6)}</div>
            </div>
            
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center gap-2 text-blue-600 mb-1">
                <Map className="w-4 h-4" />
                <span className="text-sm font-medium">Longitude</span>
              </div>
              <div className="text-lg font-mono">{data.centroid.longitude.toFixed(6)}</div>
            </div>
          </>
        )}
      </div>

      {/* Addresses Table */}
      {addresses.length > 0 && (
        <div>
          <h4 className="font-medium text-gray-700 mb-3">Address Details</h4>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">UPRN</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Address</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Classification</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Local Authority</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Coordinates</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {displayAddresses.map((addr, index) => (
                  <AddressRow key={addr.uprn || index} address={addr} />
                ))}
              </tbody>
            </table>
          </div>
          
          {addresses.length > 5 && (
            <button
              onClick={() => setShowAllAddresses(!showAllAddresses)}
              className="mt-3 flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800"
            >
              {showAllAddresses ? (
                <>
                  <ChevronUp className="w-4 h-4" />
                  Show less
                </>
              ) : (
                <>
                  <ChevronDown className="w-4 h-4" />
                  Show all {addresses.length} addresses
                </>
              )}
            </button>
          )}
        </div>
      )}

      {/* Metadata */}
      {data.fetched_at && (
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Clock className="w-4 h-4" />
          Fetched: {new Date(data.fetched_at).toLocaleString()}
        </div>
      )}
      
      {/* Empty state */}
      {!data.error && addresses.length === 0 && (
        <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg text-center">
          <p className="text-gray-600">No addresses found for this postcode.</p>
        </div>
      )}
    </div>
  );
}

function AddressRow({ address }: { address: OSPlacesAddress }) {
  return (
    <tr className="hover:bg-gray-50">
      <td className="px-4 py-2 text-sm font-mono text-gray-600">
        {address.uprn || '-'}
      </td>
      <td className="px-4 py-2">
        <div className="text-sm font-medium">{address.address || '-'}</div>
        {address.building_name && (
          <div className="text-xs text-gray-500">{address.building_name}</div>
        )}
      </td>
      <td className="px-4 py-2">
        {address.classification_description && (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
            {address.classification_description}
          </span>
        )}
      </td>
      <td className="px-4 py-2 text-sm text-gray-600">
        {address.local_authority || '-'}
      </td>
      <td className="px-4 py-2 text-xs font-mono text-gray-500">
        {address.latitude && address.longitude
          ? `${address.latitude.toFixed(5)}, ${address.longitude.toFixed(5)}`
          : '-'}
      </td>
    </tr>
  );
}
