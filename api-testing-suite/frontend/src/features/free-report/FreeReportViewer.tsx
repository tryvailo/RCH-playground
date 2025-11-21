import { useState, useEffect } from 'react';
import { FileText, Sparkles, AlertCircle, RefreshCw } from 'lucide-react';
import QuestionLoader from './components/QuestionLoader';
import ReportRenderer from './components/ReportRenderer';
import LoadingAnimation from './components/LoadingAnimation';
import ScoringSettings, { ScoringWeights, ScoringThresholds } from './components/ScoringSettings';
import { useGenerateFreeReport } from './hooks/useFreeReport';
import type { QuestionnaireResponse, FreeReportData } from './types';

export default function FreeReportViewer() {
  const [questionnaire, setQuestionnaire] = useState<QuestionnaireResponse | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | undefined>();
  const [report, setReport] = useState<FreeReportData | null>(null);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [showLoader, setShowLoader] = useState(false);
  const [scoringWeights, setScoringWeights] = useState<ScoringWeights | null>(null);
  const [scoringThresholds, setScoringThresholds] = useState<ScoringThresholds | null>(null);
  
  const generateReport = useGenerateFreeReport();

  // Simulate loading progress (30 seconds)
  useEffect(() => {
    if (generateReport.isPending) {
      setShowLoader(true);
      setLoadingProgress(0);
      
      const interval = setInterval(() => {
        setLoadingProgress((prev) => {
          if (prev >= 95) {
            clearInterval(interval);
            return 95;
          }
          return prev + Math.random() * 3;
        });
      }, 500);

      return () => clearInterval(interval);
    } else {
      if (report) {
        setLoadingProgress(100);
        setTimeout(() => setShowLoader(false), 500);
      }
    }
  }, [generateReport.isPending, report]);

  const handleLoadQuestionnaire = (data: QuestionnaireResponse) => {
    setQuestionnaire(data);
    setReport(null);
  };

  const handleGenerateReport = () => {
    if (!questionnaire) return;
    
    // Load scoring settings from localStorage (set in Scoring Settings tab)
    const savedWeights = localStorage.getItem('scoring_weights');
    const savedThresholds = localStorage.getItem('scoring_thresholds');
    
    // Include scoring settings in request if available
    const requestData: any = { ...questionnaire };
    if (savedWeights) {
      try {
        requestData.scoring_weights = JSON.parse(savedWeights);
      } catch (e) {
        console.error('Failed to parse scoring weights:', e);
      }
    } else if (scoringWeights) {
      requestData.scoring_weights = scoringWeights;
    }
    if (savedThresholds) {
      try {
        requestData.scoring_thresholds = JSON.parse(savedThresholds);
      } catch (e) {
        console.error('Failed to parse scoring thresholds:', e);
      }
    } else if (scoringThresholds) {
      requestData.scoring_thresholds = scoringThresholds;
    }
    
    generateReport.mutate(requestData as QuestionnaireResponse, {
      onSuccess: (data) => {
        setReport(data);
      },
      onError: (error) => {
        console.error('Failed to generate report:', error);
        setShowLoader(false);
      },
    });
  };

  const handleRetry = () => {
    if (questionnaire) {
      handleGenerateReport();
    }
  };

  // Show loading animation
  if (showLoader && generateReport.isPending) {
    return <LoadingAnimation progress={loadingProgress} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
      {/* Hero Header - WOW Effect */}
      <div className="relative overflow-hidden bg-gradient-to-r from-[#1E2A44] via-[#2D3E5F] to-[#1E2A44]">
        {/* Animated Background */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
            backgroundSize: '40px 40px',
            animation: 'float 20s ease-in-out infinite'
          }}></div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
          <div className="text-center">
            {/* Badge */}
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-[#10B981]/20 border border-[#10B981]/30 mb-6">
              <Sparkles className="w-4 h-4 text-[#10B981] mr-2" />
              <span className="text-[#10B981] font-semibold text-sm">100% Free</span>
            </div>

            <h1 className="text-4xl md:text-6xl font-bold text-white mb-4 animate-fade-in">
              Personal Care Home Report
            </h1>
            <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
              Get detailed Fair Cost Gap analysis and top 3 recommended homes for{' '}
              <span className="text-[#10B981] font-bold">free</span>
            </p>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto mt-12">
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                <div className="text-3xl font-bold text-white mb-2">3</div>
                <div className="text-gray-300 text-sm">Recommended Homes</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                <div className="text-3xl font-bold text-[#10B981] mb-2">£50k+</div>
                <div className="text-gray-300 text-sm">Potential Savings</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                <div className="text-3xl font-bold text-white mb-2">100%</div>
                <div className="text-gray-300 text-sm">Free</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
        {/* Main Content - Full Width */}
        <main className="w-full">
            {/* Error State */}
            {generateReport.isError && (
              <div className="mb-6 bg-red-50 border-2 border-red-200 rounded-xl p-6 flex items-start animate-shake">
                <AlertCircle className="w-6 h-6 text-red-600 mr-4 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-red-800 mb-2">Report Generation Error</h3>
                  <p className="text-sm text-red-700 mb-4">
                    {generateReport.error instanceof Error
                      ? generateReport.error.message
                      : 'An unexpected error occurred. Please try again.'}
                  </p>
                  <button
                    onClick={handleRetry}
                    className="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Try Again
                  </button>
                </div>
              </div>
            )}

            {/* Questionnaire Section - Central */}
            {!report && !generateReport.isPending && !generateReport.isError && (
              <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8 border border-gray-100">
                <div className="mb-6 text-center">
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Load Questionnaire</h2>
                  <p className="text-gray-600 text-sm">
                    Choose an example or upload your own JSON file
                  </p>
                </div>

                <QuestionLoader
                  onLoad={handleLoadQuestionnaire}
                  selectedFile={selectedFile}
                  onFileSelect={setSelectedFile}
                />

                {/* Questionnaire Preview */}
                {questionnaire && (
                  <div className="mt-6 pt-6 border-t border-gray-200">
                    <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                      <FileText className="w-4 h-4 mr-2 text-[#10B981]" />
                      Loaded Questionnaire
                    </h3>
                    <div className="space-y-2 text-sm bg-gray-50 rounded-lg p-4">
                      {Object.entries(questionnaire).map(([key, value]) => {
                        // Skip null/undefined values
                        if (value === null || value === undefined) return null;
                        
                        // Format key name
                        const formatKey = (k: string) => {
                          return k.split('_').map(word => 
                            word.charAt(0).toUpperCase() + word.slice(1)
                          ).join(' ');
                        };
                        
                        // Handle different value types
                        if (typeof value === 'object' && !Array.isArray(value)) {
                          // Nested object (e.g., preferences)
                          return (
                            <div key={key} className="space-y-1">
                              <div className="font-semibold text-gray-700 mb-1">{formatKey(key)}:</div>
                              <div className="ml-4 space-y-1 border-l-2 border-[#10B981]/30 pl-3">
                                {Object.entries(value).map(([nestedKey, nestedValue]) => {
                                  if (nestedValue === null || nestedValue === undefined) return null;
                                  return (
                                    <div key={nestedKey} className="flex justify-between">
                                      <span className="text-gray-600">{formatKey(nestedKey)}:</span>
                                      <span className="font-semibold text-gray-900">
                                        {typeof nestedValue === 'boolean' 
                                          ? nestedValue ? '✓' : '✗'
                                          : String(nestedValue)}
                                      </span>
                                    </div>
                                  );
                                })}
                              </div>
                            </div>
                          );
                        } else if (Array.isArray(value)) {
                          // Array values
                          return (
                            <div key={key} className="flex justify-between">
                              <span className="text-gray-600">{formatKey(key)}:</span>
                              <span className="font-semibold text-gray-900">{value.join(', ')}</span>
                            </div>
                          );
                        } else {
                          // Simple values
                          let displayValue: string;
                          if (key === 'budget') {
                            displayValue = `£${Number(value).toLocaleString()}/week`;
                          } else if (key === 'chc_probability') {
                            displayValue = `${value}%`;
                          } else if (key === 'care_type') {
                            displayValue = String(value).charAt(0).toUpperCase() + String(value).slice(1);
                          } else if (typeof value === 'number') {
                            displayValue = value.toString();
                          } else {
                            displayValue = String(value);
                          }
                          
                          return (
                            <div key={key} className="flex justify-between">
                              <span className="text-gray-600">{formatKey(key)}:</span>
                              <span className={`font-semibold ${
                                key === 'chc_probability' ? 'text-[#10B981]' : 'text-gray-900'
                              }`}>
                                {displayValue}
                              </span>
                            </div>
                          );
                        }
                      })}
                    </div>
                  </div>
                )}

                {/* Generate Button */}
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <button
                    onClick={handleGenerateReport}
                    disabled={!questionnaire || generateReport.isPending}
                    className={`w-full py-4 px-6 rounded-xl font-semibold text-white transition-all transform ${
                      !questionnaire || generateReport.isPending
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-gradient-to-r from-[#10B981] to-[#059669] hover:from-[#059669] hover:to-[#10B981] hover:scale-105 shadow-lg hover:shadow-xl'
                    }`}
                  >
                    {generateReport.isPending ? (
                      <span className="flex items-center justify-center">
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                        Generating...
                      </span>
                    ) : (
                      <span className="flex items-center justify-center">
                        <Sparkles className="w-5 h-5 mr-2" />
                        Generate Report
                      </span>
                    )}
                  </button>
                </div>
              </div>
            )}

            {/* Report */}
            {report && !generateReport.isPending && (
              <ReportRenderer report={report} questionnaire={questionnaire || undefined} />
            )}
          </main>
      </div>

      {/* Add custom animations */}
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-20px); }
        }
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-5px); }
          75% { transform: translateX(5px); }
        }
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        .animate-fade-in {
          animation: fade-in 0.6s ease-out;
        }
        .animate-shake {
          animation: shake 0.5s ease-in-out;
        }
        .animate-shimmer {
          animation: shimmer 2s infinite;
        }
        .animate-spin-slow {
          animation: spin 3s linear infinite;
        }
      `}</style>
    </div>
  );
}
