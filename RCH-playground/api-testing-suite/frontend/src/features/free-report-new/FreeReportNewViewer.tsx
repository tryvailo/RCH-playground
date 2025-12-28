import { useState, useEffect } from 'react';
import { FileText, Sparkles, AlertCircle, RefreshCw } from 'lucide-react';
import QuestionLoader from '../free-report/components/QuestionLoader';
import ReportRenderer from './components/ReportRenderer';
import LoadingAnimation from './components/LoadingAnimation';
import { useFreeReportNew } from './hooks/useFreeReportNew';
import { useFreeReportStream } from './hooks/useFreeReportStream';
import type { QuestionnaireResponse, FreeReportData } from './types';

export default function FreeReportNewViewer() {
  const [questionnaire, setQuestionnaire] = useState<QuestionnaireResponse | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | undefined>();
  const [report, setReport] = useState<FreeReportData | null>(null);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [showLoader, setShowLoader] = useState(false);
  const [useStreaming, setUseStreaming] = useState(true); // Toggle for SSE vs regular
  
  // Use streaming hook for real-time progress
  const streamReport = useFreeReportStream();
  // Fallback to regular hook if streaming is disabled
  const generateReport = useFreeReportNew();

  // Update progress from streaming or simulate for regular mode
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    let timeout: NodeJS.Timeout | null = null;
    
    if (useStreaming && streamReport.isLoading) {
      // Use real-time progress from SSE
      setShowLoader(true);
      if (streamReport.progress) {
        setLoadingProgress(streamReport.progress.progress);
      } else if (loadingProgress === 0) {
        // Initialize progress if not set yet
        setLoadingProgress(1);
      }
      
      // Update report when ready
      if (streamReport.report) {
        setReport(streamReport.report);
        setLoadingProgress(100);
        timeout = setTimeout(() => setShowLoader(false), 500);
      }
      
      // Handle errors
      if (streamReport.error) {
        setShowLoader(false);
        setLoadingProgress(0);
      }
    } else if (!useStreaming && generateReport.isPending) {
      // Simulate progress for regular mode
      setShowLoader(true);
      if (loadingProgress === 0) {
        setLoadingProgress(1);
      }
      
      interval = setInterval(() => {
        setLoadingProgress((prev) => {
          if (prev >= 95) {
            return 95;
          }
          return prev + Math.random() * 3;
        });
      }, 500);
    } else if (!useStreaming && !generateReport.isPending && report) {
      // Report completed in regular mode
      setLoadingProgress(100);
      timeout = setTimeout(() => setShowLoader(false), 500);
    } else if (!useStreaming && !generateReport.isPending && generateReport.isError) {
      // Error in regular mode
      setShowLoader(false);
      setLoadingProgress(0);
    }

    return () => {
      if (interval) clearInterval(interval);
      if (timeout) clearTimeout(timeout);
    };
  }, [useStreaming, streamReport.isLoading, streamReport.progress, streamReport.report, streamReport.error, generateReport.isPending, generateReport.isError, report, loadingProgress]);

  // Update report when stream completes
  useEffect(() => {
    if (useStreaming && streamReport.report) {
      setReport(streamReport.report);
    }
  }, [useStreaming, streamReport.report]);

  const handleLoadQuestionnaire = (data: QuestionnaireResponse) => {
    setQuestionnaire(data);
    setReport(null);
  };

  const handleGenerateReport = async () => {
    if (!questionnaire) {
      console.warn('Cannot generate report: questionnaire is null');
      return;
    }
    
    // Show loader immediately when button is clicked
    setShowLoader(true);
    setLoadingProgress(0);
    setReport(null);
    
    console.log('🚀 Starting free report generation (new version):', {
      postcode: questionnaire.postcode,
      care_type: questionnaire.care_type,
      budget: questionnaire.budget,
      useStreaming,
    });
    
    if (useStreaming) {
      // Use SSE streaming for real-time progress
      // Note: streamReport.generateReport sets isLoading: true internally,
      // but we also set showLoader here to ensure immediate UI feedback
      try {
        await streamReport.generateReport(questionnaire);
        // Report will be set via useEffect when streamReport.report changes
      } catch (error) {
        console.error('❌ Failed to generate report via SSE:', error);
        setShowLoader(false);
        setLoadingProgress(0);
      }
    } else {
      // Use regular endpoint
      generateReport.mutate(questionnaire, {
        onSuccess: (data) => {
          console.log('✅ Free report generated successfully:', data);
          setReport(data);
        },
        onError: (error) => {
          console.error('❌ Failed to generate report:', error);
          setShowLoader(false);
          setLoadingProgress(0);
        },
      });
    }
  };

  const handleRetry = () => {
    if (questionnaire) {
      handleGenerateReport();
    }
  };

  // Show loading animation
  const isLoading = useStreaming ? streamReport.isLoading : generateReport.isPending;
  const hasError = useStreaming ? (streamReport.error !== null) : generateReport.isError;
  const errorMessage = useStreaming 
    ? (streamReport.error instanceof Error ? streamReport.error.message : String(streamReport.error || ''))
    : (generateReport.error instanceof Error ? generateReport.error.message : String(generateReport.error || ''));
  
  if (showLoader && isLoading) {
    const progressMessage = useStreaming && streamReport.progress 
      ? streamReport.progress.message 
      : undefined;
    return <LoadingAnimation progress={loadingProgress} message={progressMessage} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
      {/* Hero Header */}
      <div className="relative overflow-hidden bg-gradient-to-r from-[#1E2A44] via-[#2D3E5F] to-[#1E2A44]">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
            backgroundSize: '40px 40px',
            animation: 'float 20s ease-in-out infinite'
          }}></div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
          <div className="text-center">
            {/* Beta Badge */}
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-amber-500/20 border border-amber-500/30 mb-6">
              <Sparkles className="w-4 h-4 text-amber-500 mr-2" />
              <span className="text-amber-600 font-semibold text-sm">BETA - Data Engine Version</span>
            </div>

            <h1 className="text-4xl md:text-6xl font-bold text-white mb-4 animate-fade-in">
              Personal Care Home Report (New)
            </h1>
            <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
              React-powered report generation using{' '}
              <span className="text-amber-300 font-bold">Data Engine</span>
            </p>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto mt-12">
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                <div className="text-3xl font-bold text-white mb-2">3</div>
                <div className="text-gray-300 text-sm">Top Recommendations</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                <div className="text-3xl font-bold text-amber-300 mb-2">3-7s</div>
                <div className="text-gray-300 text-sm">Generation Time</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                <div className="text-3xl font-bold text-white mb-2">Fast</div>
                <div className="text-gray-300 text-sm">Real-time Progress</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
        <main className="w-full">
          {/* Error State */}
          {hasError && (
            <div className="mb-6 bg-red-50 border-2 border-red-200 rounded-xl p-6 flex items-start animate-shake">
              <AlertCircle className="w-6 h-6 text-red-600 mr-4 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-red-800 mb-2">Report Generation Error</h3>
                <p className="text-sm text-red-700 mb-4">
                  {errorMessage || 'An unexpected error occurred. Please try again.'}
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

          {/* Questionnaire Section */}
          {!report && !isLoading && !hasError && (
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
                    <FileText className="w-4 h-4 mr-2 text-amber-500" />
                    Loaded Questionnaire
                  </h3>
                  <div className="space-y-2 text-sm bg-gray-50 rounded-lg p-4">
                    {Object.entries(questionnaire).map(([key, value]) => {
                      if (value === null || value === undefined) return null;
                      
                      const formatKey = (k: string) => {
                        return k.split('_').map(word => 
                          word.charAt(0).toUpperCase() + word.slice(1)
                        ).join(' ');
                      };
                      
                      if (typeof value === 'object' && !Array.isArray(value)) {
                        return (
                          <div key={key} className="space-y-1">
                            <div className="font-semibold text-gray-700 mb-1">{formatKey(key)}:</div>
                            <div className="ml-4 space-y-1 border-l-2 border-amber-500/30 pl-3">
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
                        return (
                          <div key={key} className="flex justify-between">
                            <span className="text-gray-600">{formatKey(key)}:</span>
                            <span className="font-semibold text-gray-900">{value.join(', ')}</span>
                          </div>
                        );
                      } else {
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
                              key === 'chc_probability' ? 'text-amber-500' : 'text-gray-900'
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
                  disabled={!questionnaire || isLoading}
                  className={`w-full py-4 px-6 rounded-xl font-semibold text-white transition-all transform ${
                    !questionnaire || isLoading
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 hover:scale-105 shadow-lg hover:shadow-xl'
                  }`}
                >
                  {isLoading ? (
                    <span className="flex items-center justify-center">
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                      {useStreaming && streamReport.progress 
                        ? streamReport.progress.message || 'Generating...'
                        : 'Generating...'}
                    </span>
                  ) : (
                    <span className="flex items-center justify-center">
                      <Sparkles className="w-5 h-5 mr-2" />
                      Generate Report {useStreaming ? '(Real-time Progress)' : ''}
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
        .animate-fade-in {
          animation: fade-in 0.6s ease-out;
        }
        .animate-shake {
          animation: shake 0.5s ease-in-out;
        }
      `}</style>
    </div>
  );
}

