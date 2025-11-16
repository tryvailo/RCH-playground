import { useEffect, useState } from 'react';
import { DollarSign } from 'lucide-react';

interface CostBreakdown {
  api: string;
  calls: number;
  costPerCall: number;
  totalCost: number;
  currency: string;
}

export default function CostTracker() {
  const [sessionCost, setSessionCost] = useState(0);
  const [monthlyCost, setMonthlyCost] = useState(0);
  const [breakdown, setBreakdown] = useState<CostBreakdown[]>([]);

  useEffect(() => {
    // Load cost data from backend
    loadCosts();
  }, []);

  const loadCosts = async () => {
    try {
      // In production, this would come from backend
      // const response = await axios.get('/api/analyze/costs');
      // Mock data for now
      setSessionCost(0.45);
      setMonthlyCost(12.50);
      setBreakdown([
        { api: 'Google Places', calls: 5, costPerCall: 0.017, totalCost: 0.085, currency: 'GBP' },
        { api: 'Perplexity', calls: 3, costPerCall: 0.005, totalCost: 0.015, currency: 'GBP' },
        { api: 'BestTime', calls: 2, costPerCall: 0.008, totalCost: 0.016, currency: 'GBP' },
      ]);
    } catch (error) {
      console.error('Failed to load costs:', error);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center">
          <DollarSign className="w-5 h-5 text-gray-500 mr-2" />
          <h2 className="text-lg font-semibold text-gray-900">Cost Tracker</h2>
        </div>
      </div>
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Current Session</h3>
            <p className="text-3xl font-bold text-gray-900">£{sessionCost.toFixed(2)}</p>
          </div>
          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Monthly Total</h3>
            <p className="text-3xl font-bold text-gray-900">£{monthlyCost.toFixed(2)}</p>
          </div>
        </div>

        {breakdown.length > 0 && (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    API
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Calls
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cost/Call
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {breakdown.map((item) => (
                  <tr key={item.api}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {item.api}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.calls}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      £{item.costPerCall.toFixed(4)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      £{item.totalCost.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

