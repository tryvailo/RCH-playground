interface LoadingAnimationProps {
  progress: number;
}

export default function LoadingAnimation({ progress }: LoadingAnimationProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full mx-auto px-4">
        <div className="text-center mb-8">
          <div className="inline-block">
            <div className="w-16 h-16 border-4 border-[#1E2A44] border-t-transparent rounded-full animate-spin"></div>
          </div>
        </div>
        
        <h2 className="text-2xl font-bold text-gray-900 text-center mb-2">
          Generating Professional Report
        </h2>
        <p className="text-gray-600 text-center mb-6">
          Analyzing 156 data points across 5 care homes...
        </p>

        <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-semibold text-gray-700">Progress</span>
            <span className="text-sm font-bold text-[#1E2A44]">{Math.round(progress)}%</span>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-[#1E2A44] to-blue-600 h-full transition-all duration-300 ease-out"
              style={{ width: `${Math.min(progress, 100)}%` }}
            ></div>
          </div>

          <div className="mt-6 space-y-3">
            <div className="flex items-center text-sm">
              <div className={`w-5 h-5 rounded-full mr-3 flex items-center justify-center text-white text-xs font-bold ${progress > 20 ? 'bg-green-600' : 'bg-gray-400'}`}>
                ✓
              </div>
              <span className="text-gray-700">Loading care homes</span>
            </div>
            
            <div className="flex items-center text-sm">
              <div className={`w-5 h-5 rounded-full mr-3 flex items-center justify-center text-white text-xs font-bold ${progress > 50 ? 'bg-green-600' : 'bg-gray-400'}`}>
                {progress > 50 ? '✓' : progress > 20 ? '⏳' : ''}
              </div>
              <span className="text-gray-700">Enriching with external data</span>
            </div>
            
            <div className="flex items-center text-sm">
              <div className={`w-5 h-5 rounded-full mr-3 flex items-center justify-center text-white text-xs font-bold ${progress > 75 ? 'bg-green-600' : 'bg-gray-400'}`}>
                {progress > 75 ? '✓' : progress > 50 ? '⏳' : ''}
              </div>
              <span className="text-gray-700">Scoring and matching</span>
            </div>

            <div className="flex items-center text-sm">
              <div className={`w-5 h-5 rounded-full mr-3 flex items-center justify-center text-white text-xs font-bold ${progress > 90 ? 'bg-green-600' : 'bg-gray-400'}`}>
                {progress > 90 ? '✓' : progress > 75 ? '⏳' : ''}
              </div>
              <span className="text-gray-700">Preparing report</span>
            </div>
          </div>
        </div>

        <p className="text-center text-xs text-gray-500 mt-6">
          Please don't refresh the page
        </p>
      </div>
    </div>
  );
}
