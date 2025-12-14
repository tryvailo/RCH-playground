import type { ApiTestResult } from '../types/api.types';

interface ResultsTableProps {
  results: Record<string, ApiTestResult>;
}

export default function ResultsTable({ results }: ResultsTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              API
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Response Time
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Data Returned
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Quality
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Cost
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {Object.entries(results).map(([apiName, result]) => (
            <tr key={apiName}>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {apiName}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 py-1 text-xs rounded ${
                  result.status === 'success' ? 'bg-success/10 text-success' :
                  result.status === 'failure' ? 'bg-danger/10 text-danger' :
                  'bg-warning/10 text-warning'
                }`}>
                  {result.status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {result.responseTime.toFixed(2)}s
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                <span className={result.dataReturned ? 'text-success' : 'text-danger'}>
                  {result.dataReturned ? 'Yes' : 'No'}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {result.dataQuality.completeness}%
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                £{result.costIncurred.toFixed(4)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

