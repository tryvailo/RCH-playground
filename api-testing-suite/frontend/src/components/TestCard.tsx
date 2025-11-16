import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import type { ApiTestResult } from '../types/api.types';

interface TestCardProps {
  result: ApiTestResult;
}

export default function TestCard({ result }: TestCardProps) {
  const getStatusIcon = () => {
    switch (result.status) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-success" />;
      case 'failure':
        return <XCircle className="w-5 h-5 text-danger" />;
      case 'partial':
        return <AlertCircle className="w-5 h-5 text-warning" />;
      default:
        return null;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <h3 className="font-semibold text-gray-900">{result.apiName}</h3>
        </div>
        <span className={`text-xs px-2 py-1 rounded ${
          result.status === 'success' ? 'bg-success/10 text-success' :
          result.status === 'failure' ? 'bg-danger/10 text-danger' :
          'bg-warning/10 text-warning'
        }`}>
          {result.status}
        </span>
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div>
          <span className="text-gray-500">Time:</span>
          <span className="ml-1 font-medium">{result.responseTime.toFixed(2)}s</span>
        </div>
        <div>
          <span className="text-gray-500">Cost:</span>
          <span className="ml-1 font-medium">£{result.costIncurred.toFixed(4)}</span>
        </div>
        <div>
          <span className="text-gray-500">Data:</span>
          <span className={`ml-1 font-medium ${result.dataReturned ? 'text-success' : 'text-danger'}`}>
            {result.dataReturned ? 'Yes' : 'No'}
          </span>
        </div>
        <div>
          <span className="text-gray-500">Quality:</span>
          <span className="ml-1 font-medium">{result.dataQuality.completeness}%</span>
        </div>
      </div>

      {result.errors.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <p className="text-xs font-medium text-danger mb-1">Errors:</p>
          <ul className="text-xs text-gray-600 space-y-1">
            {result.errors.map((error, idx) => (
              <li key={idx}>• {error}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

