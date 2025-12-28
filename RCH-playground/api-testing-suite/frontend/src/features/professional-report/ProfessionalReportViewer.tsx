import { useState, useEffect, useRef, useCallback } from 'react';
import { FileText, Sparkles, AlertCircle, RefreshCw, CheckCircle2, Star, DollarSign, Building2, BarChart3, Search, ChevronDown, ChevronUp, Target, Info, User, Database, TrendingUp, AlertTriangle } from 'lucide-react';
import QuestionLoader from './components/QuestionLoader';
import ComparativeAnalysisTable from './components/ComparativeAnalysisTable';
import RiskAssessmentViewer from './components/RiskAssessmentViewer';
import NegotiationStrategyViewer from './components/NegotiationStrategyViewer';
import ExecutiveSummaryDashboard from './components/ExecutiveSummaryDashboard';
import MatchScoreRadarChart from './components/MatchScoreRadarChart';
import StaffQualitySection from './components/StaffQualitySection';
import NeighbourhoodSection from './components/NeighbourhoodSection';
import QuestionnaireProfile from './components/QuestionnaireProfile';
import { ProfessionalReportGuide } from './components/ProfessionalReportGuide';
import CommunityReputationSection from './components/CommunityReputationSection';
import MedicalCareSection from './components/MedicalCareSection';
import ComfortLifestyleSection from './components/ComfortLifestyleSection';
import LifestyleDeepDiveSection from './components/LifestyleDeepDiveSection';
import SafetyAnalysisSection from './components/SafetyAnalysisSection';
import GooglePlacesInsightsSection from './components/GooglePlacesInsightsSection';
import AppendixSection from './components/AppendixSection';
import ExecutiveSummarySection from './components/ExecutiveSummarySection';
import PrioritiesMatchSection from './components/PrioritiesMatchSection';
import FundingOptionsSection from './components/FundingOptionsSection';
import ActionPlanSection from './components/ActionPlanSection';
import { useGenerateProfessionalReport, usePollProfessionalReport } from './hooks/useProfessionalReport';
import { CostAnalysisBlock } from '../cost-analysis';
import type { ProfessionalQuestionnaireResponse, ProfessionalReportData } from './types';

export default function ProfessionalReportViewer() {
  const [questionnaire, setQuestionnaire] = useState<ProfessionalQuestionnaireResponse | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | undefined>();
  const [report, setReport] = useState<ProfessionalReportData | null>(null);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [expandedHomes, setExpandedHomes] = useState<Set<string>>(new Set());
  const [activeSection, setActiveSection] = useState<string>('summary');
  const [activeTab, setActiveTab] = useState<'report' | 'profile' | 'guide'>('profile');

  const generateReport = useGenerateProfessionalReport();
  const [jobId, setJobId] = useState<string | null>(null);
  const progressIntervalRef = useRef<number | null>(null);
  const simulatedProgressRef = useRef<number>(0);

  // Stable callbacks for polling - must be defined before usePollProfessionalReport
  const handleReportComplete = useCallback((data: ProfessionalReportData) => {
    console.log('Professional Report Data:', data);
    console.log('Fair Cost Gap Analysis:', data.fairCostGapAnalysis);
    if (data.fairCostGapAnalysis) {
      console.log('Fair Cost Gap homes:', data.fairCostGapAnalysis.homes);
      console.log('Fair Cost Gap homes length:', data.fairCostGapAnalysis.homes?.length);
    }
    // Stop progress simulation
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current);
      progressIntervalRef.current = null;
    }
    setLoadingProgress(100); // Set to 100% first
    setReport(data);
    // Small delay to show 100% before switching tabs and clearing jobId
    setTimeout(() => {
      setJobId(null);
      setActiveTab('report');
      // Clear loading progress after a short delay to hide progress bar
      setTimeout(() => {
        setLoadingProgress(0);
      }, 1000);
    }, 500);
  }, []);

  const handleReportError = useCallback((error: Error) => {
    console.error('Failed to generate report:', error);
    // Stop progress simulation on error
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current);
      progressIntervalRef.current = null;
    }
    setLoadingProgress(0);
    setJobId(null);
    // Set error message for display
    setServerError(error.message || 'Failed to generate report. Please try again.');
  }, []);

  // Poll for report status when job is started
  const { status: jobStatus, progress: jobProgress, message: jobMessage, isError: jobIsError, error: jobError } = usePollProfessionalReport(
    jobId,
    handleReportComplete,
    handleReportError
  );

  // Track server error state
  const [serverError, setServerError] = useState<string | null>(null);

  // Smooth progress simulation - gradually increase progress when loading
  useEffect(() => {
    // Clear any existing interval
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current);
      progressIntervalRef.current = null;
    }

    // Start progress simulation if loading
    const shouldSimulate = (generateReport.isPending || loadingProgress > 0) && loadingProgress < 90;
    if (shouldSimulate) {
      const startProgress = loadingProgress || 1;
      const targetProgress = 90; // Don't go above 90% until we get real progress
      const steps = 300; // Update every 100ms (30 seconds total)
      const increment = (targetProgress - startProgress) / steps;
      let currentStep = 0;

      progressIntervalRef.current = window.setInterval(() => {
        currentStep++;
        const newProgress = Math.min(
          startProgress + (increment * currentStep),
          targetProgress
        );

        // Only update if we don't have real progress from backend or real progress is less
        if (!jobId || !jobProgress || jobProgress < newProgress) {
          simulatedProgressRef.current = newProgress;
          setLoadingProgress(newProgress);
        }

        if (currentStep >= steps || newProgress >= targetProgress) {
          if (progressIntervalRef.current) {
            clearInterval(progressIntervalRef.current);
            progressIntervalRef.current = null;
          }
        }
      }, 100);
    }

    return () => {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
      }
    };
  }, [generateReport.isPending, loadingProgress, jobId, jobProgress]);

  // Log progress updates for debugging
  useEffect(() => {
    if (jobId) {
      console.log('JobId set:', jobId);
    }
  }, [jobId]);

  useEffect(() => {
    if (jobId && jobStatus) {
      console.log('Job status update:', { jobId, jobStatus, jobProgress, jobMessage });
    }
  }, [jobId, jobStatus, jobProgress, jobMessage]);

  // Update loading progress based on job status
  useEffect(() => {
    if (jobId && (jobStatus === 'processing' || jobStatus === 'queued' || jobStatus === 'pending')) {
      // Use real progress from backend if available, otherwise keep simulated progress
      const realProgress = jobProgress ?? simulatedProgressRef.current;
      const progress = Math.max(realProgress, simulatedProgressRef.current);
      setLoadingProgress(progress);
      simulatedProgressRef.current = progress; // Update simulated progress to match
      console.log('Progress update:', { jobStatus, jobProgress, progress, jobMessage, simulated: simulatedProgressRef.current });
      // Switch to Profile tab during loading if Report tab is active
      if (activeTab === 'report') {
        setActiveTab('profile');
      }
    } else if (jobStatus === 'completed') {
      // Stop simulation and set to 100%
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
      }
      setLoadingProgress(100);
      // Switch to Report tab when completed
      setActiveTab('report');
    } else if (jobStatus === 'failed') {
      // Stop simulation on failure
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
      }
      setLoadingProgress(0);
    }
  }, [jobId, jobStatus, jobProgress, jobMessage, activeTab]);

  // Switch to Report tab when report is loaded
  useEffect(() => {
    if (report && !jobId) {
      setActiveTab('report');
    }
  }, [report, jobId]);

  // Auto-expand all homes when report is loaded
  useEffect(() => {
    if (report && report.careHomes && report.careHomes.length > 0) {
      // Expand all homes (top 5) by default
      const allHomeIds = new Set(report.careHomes.slice(0, 5).map(h => h.id));
      setExpandedHomes(allHomeIds);
    }
  }, [report]);

  const handleLoadQuestionnaire = (data: ProfessionalQuestionnaireResponse) => {
    setQuestionnaire(data);
    setReport(null);
  };

  const handleGenerateReport = () => {
    if (!questionnaire) {
      console.warn('Cannot generate report: questionnaire is null');
      return;
    }

    // Don't start a new request if one is already in progress
    if (generateReport.isPending) {
      console.warn('Report generation already in progress, ignoring duplicate request');
      return;
    }

    console.log('handleGenerateReport called with questionnaire:', questionnaire);
    console.log('generateReport mutation state:', { isPending: generateReport.isPending, isError: generateReport.isError });

    // Clear any existing progress simulation
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current);
      progressIntervalRef.current = null;
    }

    // Clear any previous errors
    setServerError(null);

    // Initialize progress immediately when button is clicked
    simulatedProgressRef.current = 1;
    setLoadingProgress(1);
    setActiveTab('profile');

    console.log('Calling generateReport.mutate...');
    generateReport.mutate(questionnaire, {
      onSuccess: (data) => {
        console.log('Job started - Full response:', JSON.stringify(data, null, 2));
        console.log('Job started - response keys:', Object.keys(data || {}));

        // Check if response has job_id (async mode) or report (sync mode - legacy)
        // First check for job_id field (async mode)
        if (data && typeof data === 'object' && 'job_id' in data && data.job_id) {
          // Async mode - job started
          console.log('✅ Job started - job_id:', data.job_id);
          console.log('Job started - status:', (data as any).status);
          setJobId(data.job_id);
          simulatedProgressRef.current = 5;
          setLoadingProgress(5); // Show 5% when job is accepted, simulation will continue
          setActiveTab('profile');
        } else if (data && typeof data === 'object' && 'report' in data && (data as any).report) {
          // Sync mode - report already completed (immediate response)
          console.log('✅ Report generated successfully (sync mode)');
          // Stop simulation
          if (progressIntervalRef.current) {
            clearInterval(progressIntervalRef.current);
            progressIntervalRef.current = null;
          }
          setLoadingProgress(100); // Show 100% before setting report
          // Small delay to show 100% before setting report and switching tabs
          setTimeout(() => {
            setReport(data.report);
            setActiveTab('report');
            // Clear loading progress after a short delay to hide progress bar
            setTimeout(() => {
              setLoadingProgress(0);
            }, 1000);
          }, 500);
        } else {
          console.error('❌ No job_id or report in response:', data);
          console.error('Response type:', typeof data);
          console.error('Response keys:', data ? Object.keys(data) : 'data is null/undefined');
          if (progressIntervalRef.current) {
            clearInterval(progressIntervalRef.current);
            progressIntervalRef.current = null;
          }
          setLoadingProgress(0);
          setServerError('Invalid response from server. Expected job_id or report field.');
        }
      },
      onError: (error) => {
        console.error('❌ Failed to start report generation - onError callback triggered');
        console.error('Error object:', error);
        console.error('Error type:', typeof error);
        console.error('Error constructor:', error?.constructor?.name);

        if (error instanceof Error) {
          console.error('Error message:', error.message);
          console.error('Error stack:', error.stack);
          console.error('Error name:', error.name);
          // Set error message for display
          const errorMessage = error.message || 'Failed to start report generation. Please check if the server is running.';
          console.error('Setting server error:', errorMessage);
          setServerError(errorMessage);
        } else {
          console.error('Unknown error type:', typeof error, error);
          const errorMessage = String(error) || 'Failed to start report generation. Please check if the server is running.';
          setServerError(errorMessage);
        }
        // Stop simulation on error
        if (progressIntervalRef.current) {
          clearInterval(progressIntervalRef.current);
          progressIntervalRef.current = null;
        }
        setLoadingProgress(0);
        setJobId(null);
      },
    });
  };

  const handleRetry = () => {
    if (questionnaire) {
      handleGenerateReport();
    }
  };

  // Determine if report is loading - show progress bar during any loading state
  // Don't show progress if there's a server error
  const isLoading = !serverError && !jobIsError && ((jobId && (jobStatus === 'processing' || jobStatus === 'queued' || jobStatus === 'pending')) || generateReport.isPending || loadingProgress > 0);

  // Clear error when starting new generation
  useEffect(() => {
    if (generateReport.isPending) {
      setServerError(null);
    }
  }, [generateReport.isPending]);

  // Update error from polling
  useEffect(() => {
    if (jobIsError && jobError) {
      const errorMessage = jobError instanceof Error ? jobError.message : String(jobError);
      setServerError(errorMessage);
    }
  }, [jobIsError, jobError]);

  // Use jobProgress directly if available and > 0, otherwise fallback to loadingProgress
  // Always show at least 1% if loading, to ensure progress bar is visible
  const currentProgress = (() => {
    if (jobProgress !== undefined && jobProgress > 0) {
      return Math.max(jobProgress, 1); // Ensure at least 1% when job is processing
    }
    if (loadingProgress > 0) {
      return Math.max(loadingProgress, 1); // Ensure at least 1% when loading
    }
    if (isLoading) {
      return 1; // Show 1% minimum when loading starts
    }
    return 0;
  })();

  // Debug logging
  useEffect(() => {
    console.log('Loading state:', {
      isLoading,
      jobId,
      jobStatus,
      jobProgress,
      currentProgress,
      generateReportIsPending: generateReport.isPending
    });
  }, [isLoading, jobId, jobStatus, jobProgress, currentProgress, generateReport.isPending]);

  const getFSARatingLabel = (rating?: number | string | null) => {
    if (!rating) return 'Not Rated';
    const numRating = typeof rating === 'string' ? parseFloat(rating) : rating;
    if (numRating === 5) return 'Excellent';
    if (numRating === 4) return 'Good';
    if (numRating === 3) return 'Satisfactory';
    if (numRating === 2) return 'Needs Improvement';
    if (numRating === 1) return 'Needs Significant Improvement';
    return 'Needs Urgent Improvement';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Professional Report</h1>
          <p className="mt-2 text-gray-600">Comprehensive intelligence and 156-point matching analysis</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto py-4">
        {/* Error Message - Show when server error occurs */}
        {(serverError || (jobIsError && jobError)) && (
          <div className="w-full mb-6 bg-red-50 border-2 border-red-200 rounded-xl shadow-lg p-6">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                  <AlertCircle className="w-6 h-6 text-red-600" />
                </div>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-red-900 mb-2">Server Connection Error</h3>
                <p className="text-sm text-red-800 mb-4">
                  {serverError || (jobError instanceof Error ? jobError.message : String(jobError))}
                </p>
                <div className="flex gap-3">
                  <button
                    onClick={handleRetry}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
                  >
                    Retry
                  </button>
                  <button
                    onClick={() => {
                      setServerError(null);
                      setJobId(null);
                      setLoadingProgress(0);
                    }}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors text-sm font-medium"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Progress Bar - Show during loading (only if no error) */}
        {isLoading && !serverError && !jobIsError && (
          <div className="w-full mb-6 bg-white rounded-xl shadow-lg border border-gray-200 p-4">
            <div className="mb-2 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-[#1E2A44] border-t-transparent rounded-full animate-spin"></div>
                <span className="text-sm font-semibold text-gray-900">Generating Professional Report</span>
              </div>
              <span className="text-sm font-medium text-gray-600">
                {Math.round(currentProgress)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 mb-2 relative">
              <div
                className="bg-gradient-to-r from-[#1E2A44] to-[#10B981] h-2.5 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${Math.max(Math.min(currentProgress, 100), 0)}%` }}
              ></div>
            </div>
            {jobMessage && (
              <p className="text-xs text-gray-500 mt-1">{jobMessage}</p>
            )}
            {!jobMessage && isLoading && (
              <p className="text-xs text-gray-400 mt-1 italic">
                {jobStatus === 'queued' ? 'Report generation queued...' : 'Processing your report...'}
              </p>
            )}
            <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
              <div className="flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-green-600" />
                <span>156-point analysis</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-green-600" />
                <span>15+ data sources</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-green-600" />
                <span>5 care homes</span>
              </div>
            </div>
          </div>
        )}

        {/* Tabs Navigation - Show when questionnaire is loaded or report exists */}
        {(questionnaire || report) && (
          <div className="w-full mb-6">
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
              <nav className="flex">
                <button
                  onClick={() => !isLoading && setActiveTab('report')}
                  disabled={isLoading || !report}
                  className={`flex-1 py-4 px-6 text-center font-semibold text-sm md:text-base transition-colors border-b-2 ${activeTab === 'report' && !isLoading && report
                    ? 'border-[#1E2A44] text-[#1E2A44] bg-blue-50'
                    : isLoading || !report
                      ? 'border-transparent text-gray-400 bg-gray-50 cursor-not-allowed'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                >
                  <div className="flex items-center justify-center gap-2">
                    <FileText className="w-4 h-4 md:w-5 md:h-5" />
                    <span>Report</span>
                    {isLoading && (
                      <span className="text-xs text-gray-400">(Loading...)</span>
                    )}
                  </div>
                </button>
                <button
                  onClick={() => setActiveTab('profile')}
                  className={`flex-1 py-4 px-6 text-center font-semibold text-sm md:text-base transition-colors border-b-2 ${activeTab === 'profile'
                    ? 'border-[#1E2A44] text-[#1E2A44] bg-blue-50'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                >
                  <div className="flex items-center justify-center gap-2">
                    <User className="w-4 h-4 md:w-5 md:h-5" />
                    <span>Profile</span>
                  </div>
                </button>
                <button
                  onClick={() => setActiveTab('guide')}
                  className={`flex-1 py-4 px-6 text-center font-semibold text-sm md:text-base transition-colors border-b-2 ${activeTab === 'guide'
                    ? 'border-[#1E2A44] text-[#1E2A44] bg-blue-50'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                >
                  <div className="flex items-center justify-center gap-2">
                    <Info className="w-4 h-4 md:w-5 md:h-5" />
                    <span>Guide</span>
                  </div>
                </button>
              </nav>
            </div>
          </div>
        )}

        {/* Tab Content */}
        {!report ? (
          <div className="w-full">
            {/* Error Display */}
            {generateReport.isError && (
              <div className="mb-6 bg-red-50 border border-red-200 rounded-xl p-4 flex items-start">
                <AlertCircle className="w-5 h-5 text-red-600 mr-3 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-red-900 mb-1">Error Generating Report</h3>
                  <p className="text-sm text-red-800 mb-3">
                    {generateReport.error?.message || 'An error occurred while generating the report'}
                  </p>
                  <button
                    onClick={handleRetry}
                    className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-red-900 bg-red-100 rounded-md hover:bg-red-200"
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Retry
                  </button>
                </div>
              </div>
            )}

            {/* Questionnaire Section - Only show when not loading and no questionnaire loaded yet */}
            {!questionnaire && !generateReport.isPending && !generateReport.isError && (
              <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8 border border-gray-100">
                <div className="mb-6 text-center">
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Load Professional Questionnaire</h2>
                  <p className="text-gray-600 text-sm">
                    Choose from 6 sample profiles or upload your own JSON file
                  </p>
                </div>

                <QuestionLoader
                  onLoad={handleLoadQuestionnaire}
                  selectedFile={selectedFile}
                  onFileSelect={setSelectedFile}
                />

                {/* Generate Button */}
                {questionnaire && (
                  <div className="mt-6 pt-6 border-t border-gray-200">
                    <button
                      onClick={handleGenerateReport}
                      disabled={generateReport.isPending}
                      className="w-full bg-gradient-to-r from-[#1E2A44] to-[#2D3E5F] text-white font-semibold py-3 px-6 rounded-lg hover:from-[#2D3E5F] hover:to-[#1E2A44] transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {generateReport.isPending ? 'Generating...' : 'Generate Professional Report (£119)'}
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Generate Button - Show when questionnaire loaded but not generating yet */}
            {questionnaire && !isLoading && !generateReport.isPending && !generateReport.isError && (
              <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8 border border-gray-100">
                <div className="text-center">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">Ready to Generate Report</h2>
                  <button
                    onClick={handleGenerateReport}
                    className="w-full bg-gradient-to-r from-[#1E2A44] to-[#2D3E5F] text-white font-semibold py-3 px-6 rounded-lg hover:from-[#2D3E5F] hover:to-[#1E2A44] transition-all shadow-lg hover:shadow-xl"
                  >
                    Generate Professional Report (£119)
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : null}

        {/* Tab Content - Profile and Guide (shown during loading or when report is ready) */}
        {activeTab === 'profile' && questionnaire ? (
          <div className="w-full">
            <QuestionnaireProfile questionnaire={questionnaire!} />
          </div>
        ) : activeTab === 'guide' ? (
          <div className="w-full">
            <ProfessionalReportGuide />
          </div>
        ) : null}

        {report && activeTab === 'report' && (
          <div className="w-full space-y-6">
            {/* Horizontal Section Tabs */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="border-b border-gray-200">
                <nav className="flex overflow-x-auto no-scrollbar py-1">
                  {[
                    { id: 'summary', label: 'Summary', icon: <BarChart3 className="w-4 h-4" /> },
                    { id: 'priorities', label: 'Priorities', icon: <Target className="w-4 h-4" /> },
                    { id: 'homes', label: 'Top Homes', icon: <Building2 className="w-4 h-4" /> },
                    { id: 'analysis', label: 'Analysis', icon: <Search className="w-4 h-4" /> },
                    { id: 'risks', label: 'Risks', icon: <AlertCircle className="w-4 h-4" /> },
                    { id: 'funding', label: 'Funding', icon: <DollarSign className="w-4 h-4" /> },
                    { id: 'negotiation', label: 'Strategy', icon: <FileText className="w-4 h-4" /> },
                    { id: 'actionplan', label: 'Action Plan', icon: <CheckCircle2 className="w-4 h-4" /> },
                  ].map((section) => (
                    <button
                      key={section.id}
                      onClick={() => setActiveSection(section.id)}
                      className={`flex items-center gap-2 py-4 px-6 text-center font-semibold text-sm transition-colors border-b-2 whitespace-nowrap ${activeSection === section.id
                        ? 'border-[#1E2A44] text-[#1E2A44] bg-blue-50'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`}
                    >
                      {section.icon}
                      <span>{section.label}</span>
                    </button>
                  ))}
                </nav>
              </div>
            </div>

            {/* Section Content */}
            <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8 border border-gray-100">
              <div className="max-w-5xl mx-auto">
                {activeSection === 'summary' && (
                  <div className="animate-fade-in space-y-12">
                    <ExecutiveSummarySection report={report!} />
                    <ExecutiveSummaryDashboard report={report!} />
                  </div>
                )}

                {activeSection === 'priorities' && (
                  <div className="animate-fade-in space-y-6">
                    <PrioritiesMatchSection report={report!} questionnaire={questionnaire!} />
                  </div>
                )}

                {activeSection === 'homes' && (
                  <div className="animate-fade-in space-y-6">
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-xl font-bold text-gray-900">Recommended Care Homes</h3>
                      <button
                        onClick={() => {
                          const allExpanded = report.careHomes.slice(0, 5).every(h => expandedHomes.has(h.id));
                          if (allExpanded) {
                            setExpandedHomes(new Set());
                          } else {
                            setExpandedHomes(new Set(report!.careHomes.slice(0, 5).map(h => h.id)));
                          }
                        }}
                        className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                      >
                        {expandedHomes.size === Math.min(report!.careHomes.length, 5) ? (
                          <><ChevronUp className="w-3 h-3" /> Collapse All</>
                        ) : (
                          <><ChevronDown className="w-3 h-3" /> Expand All</>
                        )}
                      </button>
                    </div>

                    <div className="space-y-4">
                      {report!.careHomes.slice(0, 5).map((home, index) => (
                        <div key={home.id} className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                          <div
                            className="p-4 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors"
                            onClick={() => {
                              const newExpanded = new Set(expandedHomes);
                              if (newExpanded.has(home.id)) newExpanded.delete(home.id);
                              else newExpanded.add(home.id);
                              setExpandedHomes(newExpanded);
                            }}
                          >
                            <div className="flex items-center gap-4">
                              <span className="w-8 h-8 rounded-full bg-[#1E2A44] text-white flex items-center justify-center font-bold">
                                {index + 1}
                              </span>
                              <div>
                                <h4 className="font-bold text-gray-900">{home.name}</h4>
                                <p className="text-sm text-gray-500">{home.location} • Match Score: <span className="text-emerald-600 font-bold">{home.matchScore.toFixed(1)}%</span></p>
                              </div>
                            </div>
                            {expandedHomes.has(home.id) ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
                          </div>

                          {expandedHomes.has(home.id) && (
                            <div className="p-6 pt-0 border-t border-gray-100 space-y-8 animate-fade-in mt-4">
                              {/* LLM Insights - Why This Home Was Recommended */}
                              {(() => {
                                // Debug: Log available data
                                console.log('🔍 LLM Insights Debug for home:', home.name, {
                                  hasLlmInsights: !!report.llmInsights,
                                  hasInsights: !!report.llmInsights?.insights,
                                  hasTopHomeAnalysis: !!report.llmInsights?.insights?.top_home_analysis,
                                  topHomeAnalysisLength: report.llmInsights?.insights?.top_home_analysis?.length || 0,
                                  homeName: home.name,
                                  homeIndex: index + 1,
                                  topHomeAnalysis: report.llmInsights?.insights?.top_home_analysis
                                });
                                
                                // Try to find LLM insight
                                let homeInsight = null;
                                if (report.llmInsights?.insights?.top_home_analysis) {
                                  // ✅ FIX: Try multiple matching strategies with better logging
                                  const topHomeAnalysis = report.llmInsights.insights.top_home_analysis;
                                  
                                  // Strategy 1: Rank match (most reliable)
                                  homeInsight = topHomeAnalysis.find(
                                    (insight) => insight.rank === index + 1
                                  );
                                  
                                  if (homeInsight) {
                                    console.log(`✅ Found LLM insight by rank ${index + 1} for home: ${home.name}`);
                                  } else {
                                    // Strategy 2: Exact name match
                                    homeInsight = topHomeAnalysis.find(
                                      (insight) => {
                                        if (!insight.home_name || !home.name) return false;
                                        const insightName = insight.home_name.toLowerCase().trim();
                                        const homeName = home.name.toLowerCase().trim();
                                        return insightName === homeName;
                                      }
                                    );
                                    
                                    if (homeInsight) {
                                      console.log(`✅ Found LLM insight by exact name match for home: ${home.name}`);
                                    } else {
                                      // Strategy 3: Partial name match (more flexible)
                                      homeInsight = topHomeAnalysis.find(
                                        (insight) => {
                                          if (!insight.home_name || !home.name) return false;
                                          const insightName = insight.home_name.toLowerCase().trim();
                                          const homeName = home.name.toLowerCase().trim();
                                          return homeName.includes(insightName) || insightName.includes(homeName);
                                        }
                                      );
                                      
                                      if (homeInsight) {
                                        console.log(`✅ Found LLM insight by partial name match for home: ${home.name}`);
                                      } else {
                                        // Strategy 4: Try to match by first word or key words
                                        const homeNameWords = home.name.toLowerCase().split(/\s+/);
                                        homeInsight = topHomeAnalysis.find(
                                          (insight) => {
                                            if (!insight.home_name) return false;
                                            const insightNameWords = insight.home_name.toLowerCase().split(/\s+/);
                                            // Check if first word matches
                                            if (homeNameWords[0] && insightNameWords[0] && 
                                                homeNameWords[0] === insightNameWords[0]) {
                                              return true;
                                            }
                                            // Check if any key word matches (words longer than 3 chars)
                                            const homeKeyWords = homeNameWords.filter(w => w.length > 3);
                                            const insightKeyWords = insightNameWords.filter(w => w.length > 3);
                                            return homeKeyWords.some(w => insightKeyWords.includes(w));
                                          }
                                        );
                                        
                                        if (homeInsight) {
                                          console.log(`✅ Found LLM insight by word match for home: ${home.name}`);
                                        } else {
                                          console.log(`⚠️ No LLM insight found for home: ${home.name} (rank ${index + 1})`);
                                          console.log(`   Available insights:`, topHomeAnalysis.map(i => ({ rank: i.rank, name: i.home_name })));
                                        }
                                      }
                                    }
                                  }
                                } else {
                                  console.log(`⚠️ No top_home_analysis available in LLM Insights for home: ${home.name}`);
                                  console.log(`   LLM Insights structure:`, {
                                    hasLlmInsights: !!report.llmInsights,
                                    hasInsights: !!report.llmInsights?.insights,
                                    hasTopHomeAnalysis: !!report.llmInsights?.insights?.top_home_analysis,
                                    model: report.llmInsights?.model,
                                    method: report.llmInsights?.method
                                  });
                                }
                                
                                // Fallback: Use home data if no LLM insight available
                                if (!homeInsight) {
                                  console.log('⚠️ Using fallback insight for home:', home.name);
                                  // Create fallback insight from home data
                                  homeInsight = {
                                    home_name: home.name,
                                    rank: index + 1,
                                    why_recommended: home.whyChosen || home.matchReason || `This home scored ${home.matchScore.toFixed(1)}% based on comprehensive analysis of your requirements.`,
                                    key_strengths: home.keyStrengths || [],
                                    considerations: home.mustVerify || [],
                                    match_score_explanation: `Match score of ${home.matchScore.toFixed(1)}% indicates ${home.matchScore >= 80 ? 'excellent' : home.matchScore >= 60 ? 'strong' : 'good'} alignment with your needs.`
                                  };
                                }
                                
                                if (!homeInsight) {
                                  return null;
                                }
                                
                                return (
                                  <div className="bg-gradient-to-r from-green-50/50 to-emerald-50/50 rounded-xl p-6 border border-green-200 shadow-sm mb-6">
                                    <h5 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                                      <Target className="w-5 h-5 text-green-600" />
                                      Why This Home Was Recommended
                                    </h5>
                                    <p className="text-gray-700 mb-4 leading-relaxed">{homeInsight.why_recommended}</p>
                                    
                                    {/* Data Sources Explanation */}
                                    {homeInsight.data_sources_explanation && (
                                      <div className="mb-4 p-4 bg-blue-50/50 rounded-lg border border-blue-100">
                                        <div className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
                                          <Database className="w-4 h-4 text-blue-600" />
                                          Data Sources Used:
                                        </div>
                                        <p className="text-sm text-gray-700 leading-relaxed">{homeInsight.data_sources_explanation}</p>
                                      </div>
                                    )}
                                    
                                    {/* Key Benefits (if available) */}
                                    {homeInsight.key_benefits && homeInsight.key_benefits.length > 0 && (
                                      <div className="mb-4 p-4 bg-emerald-50/50 rounded-lg border border-emerald-100">
                                        <div className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
                                          <Star className="w-4 h-4 text-emerald-600 fill-emerald-600" />
                                          Key Benefits & Value:
                                        </div>
                                        <ul className="space-y-2">
                                          {homeInsight.key_benefits.map((benefit, bIdx) => (
                                            <li key={bIdx} className="flex items-start gap-2 text-sm text-gray-700">
                                              <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                                              <span>{benefit}</span>
                                            </li>
                                          ))}
                                        </ul>
                                      </div>
                                    )}
                                    
                                    {/* Match Score Explanation */}
                                    {homeInsight.match_score_explanation && (
                                      <p className="text-sm text-gray-600 italic mb-4 border-l-3 border-green-400 pl-3">
                                        {homeInsight.match_score_explanation}
                                      </p>
                                    )}
                                    
                                    {/* Key Strengths and Considerations */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                                      {homeInsight.key_strengths && homeInsight.key_strengths.length > 0 && (
                                        <div>
                                          <div className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                                            <TrendingUp className="w-4 h-4 text-green-600" />
                                            Key Strengths:
                                          </div>
                                          <ul className="space-y-1">
                                            {homeInsight.key_strengths.map((strength, sIdx) => (
                                              <li key={sIdx} className="flex items-start gap-2 text-sm text-gray-600">
                                                <span className="text-green-600 mt-0.5">•</span>
                                                <span>{strength}</span>
                                              </li>
                                            ))}
                                          </ul>
                                        </div>
                                      )}
                                      
                                      {homeInsight.considerations && homeInsight.considerations.length > 0 && (
                                        <div>
                                          <div className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                                            <AlertTriangle className="w-4 h-4 text-yellow-600" />
                                            Things to Consider:
                                          </div>
                                          <ul className="space-y-1">
                                            {homeInsight.considerations.map((consideration, cIdx) => (
                                              <li key={cIdx} className="flex items-start gap-2 text-sm text-gray-600">
                                                <span className="text-yellow-600 mt-0.5">•</span>
                                                <span>{consideration}</span>
                                              </li>
                                            ))}
                                          </ul>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                );
                              })()}

                              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div className="space-y-6">
                                  <MatchScoreRadarChart home={home} />
                                  <StaffQualitySection staffQuality={home.staffQuality} homeName={home.name} />
                                </div>
                                <div className="space-y-6">
                                  <div className="glass-card rounded-xl p-6 bg-gray-50/50">
                                    <h5 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                                      <Star className="w-5 h-5 text-yellow-500" />
                                      Food Hygiene Rating
                                    </h5>
                                    <div className="flex items-center gap-4">
                                      <span className="text-5xl font-bold text-[#1E2A44]">{home.fsaDetailed?.rating || 'N/A'}</span>
                                      <div>
                                        <p className="font-bold">Rating: {getFSARatingLabel(home.fsaDetailed?.rating)}</p>
                                        <p className="text-xs text-gray-500 italic">Official Food Standards Agency Data</p>
                                      </div>
                                    </div>
                                  </div>
                                  <NeighbourhoodSection neighbourhood={home.neighbourhood} homeName={home.name} />
                                </div>
                              </div>

                              {/* Additional Home Sections */}
                              <div className="space-y-6 pt-6 border-t border-gray-100">
                                {home.communityReputation && <CommunityReputationSection home={home} />}
                                <GooglePlacesInsightsSection home={home} />
                                {home.medicalCare && <MedicalCareSection home={home} />}
                                {home.comfortLifestyle && <ComfortLifestyleSection home={home} />}
                                {home.lifestyleDeepDive && <LifestyleDeepDiveSection home={home} />}
                                {home.safetyAnalysis && <SafetyAnalysisSection home={home} />}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeSection === 'analysis' && (
                  <div className="animate-fade-in space-y-12">
                    {report.comparativeAnalysis && (
                      <div className="space-y-4">
                        <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                          <Building2 className="w-6 h-6 text-[#1E2A44]" />
                          Comparative Analysis
                        </h3>
                        <ComparativeAnalysisTable analysis={report.comparativeAnalysis!} />
                      </div>
                    )}

                    {report.fairCostGapAnalysis && (
                      <div className="p-8 bg-gradient-to-r from-red-50/50 to-orange-50/50 rounded-2xl border border-red-100 shadow-sm">
                        <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                          <AlertCircle className="w-6 h-6 text-red-600" />
                          Fair Cost Gap Analysis
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm mb-8">
                          <div className="flex items-center gap-3 p-3 bg-white rounded-lg border border-red-50 shadow-sm">
                            <span className="font-semibold text-gray-900">Local Authority:</span>
                            <span className="text-gray-600">{report.fairCostGapAnalysis!.local_authority}</span>
                          </div>
                          <div className="flex items-center gap-3 p-3 bg-white rounded-lg border border-red-50 shadow-sm">
                            <span className="font-semibold text-gray-900">Care Type:</span>
                            <span className="capitalize text-gray-600">{report.fairCostGapAnalysis!.care_type.replace(/_/g, ' ')}</span>
                          </div>
                        </div>
                        <CostAnalysisBlock
                          careHomes={report.careHomes}
                          fundingOptimization={report.fundingOptimization}
                          region="england"
                          careType={questionnaire?.section_3_medical_needs?.q8_care_types?.includes('specialised_dementia') ? 'dementia' : 'residential'}
                        />
                      </div>
                    )}
                  </div>
                )}

                {activeSection === 'risks' && (
                  <div className="animate-fade-in space-y-6">
                    {report.riskAssessment && (
                      <RiskAssessmentViewer assessment={report.riskAssessment!} />
                    )}
                  </div>
                )}

                {activeSection === 'funding' && (
                  <div className="animate-fade-in space-y-6">
                    {report.fundingOptimization && (
                      <FundingOptionsSection report={report!} />
                    )}
                  </div>
                )}

                {activeSection === 'negotiation' && (
                  <div className="animate-fade-in space-y-6">
                    {report.negotiationStrategy && (
                      <NegotiationStrategyViewer strategy={report.negotiationStrategy!} />
                    )}
                  </div>
                )}

                {activeSection === 'actionplan' && (
                  <div className="animate-fade-in space-y-12">
                    <ActionPlanSection report={report} />

                    {/* Premium Upgrade Block */}
                    <div className="bg-gradient-to-r from-[#1E2A44] to-[#2D3E5F] rounded-2xl p-8 text-white shadow-xl overflow-hidden relative group">
                      <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-110 transition-transform duration-500">
                        <Sparkles className="w-32 h-32" />
                      </div>
                      <div className="max-w-2xl relative z-10">
                        <h4 className="text-2xl font-bold mb-4">Upgrade to PREMIUM for £249</h4>
                        <p className="text-gray-200 mb-6 leading-relaxed">
                          Get ongoing monitoring and real-time alerts for your chosen care home. Includes 7-week monitoring, real-time alerts, and dedicated post-placement support.
                        </p>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8">
                          {[
                            { title: '7-Week Monitoring', desc: 'Weekly updates on status' },
                            { title: 'Real-Time Alerts', desc: 'Immediate critical changes' },
                            { title: 'Research Updates', desc: 'Continuous deep research' },
                            { title: 'Dedicated Support', desc: '4h rapid response team' }
                          ].map((feature, i) => (
                            <div key={i} className="flex items-start gap-3">
                              <CheckCircle2 className="w-5 h-5 text-emerald-400 mt-0.5 flex-shrink-0" />
                              <div>
                                <div className="font-semibold text-sm">{feature.title}</div>
                                <div className="text-xs text-gray-400">{feature.desc}</div>
                              </div>
                            </div>
                          ))}
                        </div>
                        <button className="bg-white text-[#1E2A44] font-bold py-4 px-8 rounded-xl hover:bg-gray-100 transition-all hover:shadow-lg active:scale-95 shadow-xl">
                          Upgrade to PREMIUM
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Appendix at the bottom of the content area */}
              <div className="mt-16 pt-8 border-t border-gray-100">
                <div className="max-w-5xl mx-auto">
                  <h3 className="font-bold text-gray-900 mb-6 flex items-center gap-2">
                    <Database className="w-5 h-5 text-gray-400" />
                    Appendix: Data Sources & Methodology
                  </h3>
                  <AppendixSection report={report} />
                </div>
              </div>

              {/* Generate New Report Button */}
              <div className="text-center mt-12 pt-12 border-t border-gray-100 pb-4">
                <p className="text-sm text-gray-500 mb-6">
                  This report was generated using the RCH Intelligent Care Engine.
                </p>
                <button
                  onClick={() => {
                    setReport(null);
                    setQuestionnaire(null);
                    setSelectedFile('');
                  }}
                  className="inline-flex items-center gap-2 px-6 py-2.5 text-sm font-semibold text-[#1E2A44] bg-white border border-[#1E2A44] rounded-lg hover:bg-gray-50 transition-all shadow-sm"
                >
                  <RefreshCw className="w-4 h-4" />
                  Generate New Report
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

