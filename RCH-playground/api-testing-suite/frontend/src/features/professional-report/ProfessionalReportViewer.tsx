import { useState, useEffect, useRef, useCallback } from 'react';
import { FileText, Sparkles, AlertCircle, RefreshCw, Clock, CheckCircle2, Star, DollarSign, Home, Building2, BarChart3, FileText as FileTextIcon, ChevronDown, ChevronUp, BookOpen, TrendingUp, Shield, Target, Lightbulb, Info, Settings, User, Database } from 'lucide-react';
import QuestionLoader from './components/QuestionLoader';
import FiveYearProjectionsChart from './components/FiveYearProjectionsChart';
import ComparativeAnalysisTable from './components/ComparativeAnalysisTable';
import RiskAssessmentViewer from './components/RiskAssessmentViewer';
import NegotiationStrategyViewer from './components/NegotiationStrategyViewer';
import ExecutiveSummaryDashboard from './components/ExecutiveSummaryDashboard';
import MatchScoreRadarChart from './components/MatchScoreRadarChart';
import CQCRatingTrendChart from './components/CQCRatingTrendChart';
import FSAInspectionHistory from './components/FSAInspectionHistory';
import FinancialStabilityChart from './components/FinancialStabilityChart';
import StaffQualitySection from './components/StaffQualitySection';
import NeighbourhoodSection from './components/NeighbourhoodSection';
import PriceComparisonChart from './components/PriceComparisonChart';
import ReportNavigation from './components/ReportNavigation';
import QuestionnaireProfile from './components/QuestionnaireProfile';
import { ProfessionalReportGuide } from './components/ProfessionalReportGuide';
import CommunityReputationSection from './components/CommunityReputationSection';
import MedicalCareSection from './components/MedicalCareSection';
import ComfortLifestyleSection from './components/ComfortLifestyleSection';
import LifestyleDeepDiveSection from './components/LifestyleDeepDiveSection';
import SafetyAnalysisSection from './components/SafetyAnalysisSection';
import LocationWellbeingSection from './components/LocationWellbeingSection';
import AreaMapSection from './components/AreaMapSection';
import AppendixSection from './components/AppendixSection';
import LLMInsightsSection from './components/LLMInsightsSection';
import EnforcementActionsSection from './components/EnforcementActionsSection';
import RegulatedActivitiesSection from './components/RegulatedActivitiesSection';
import FootfallTrendsSection from './components/FootfallTrendsSection';
import ExecutiveSummarySection from './components/ExecutiveSummarySection';
import PrioritiesMatchSection from './components/PrioritiesMatchSection';
import FundingOptionsSection from './components/FundingOptionsSection';
import ActionPlanSection from './components/ActionPlanSection';
import VerdictBadge from './components/VerdictBadge';
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
  const sectionRefs = useRef<{ [key: string]: HTMLElement | null }>({});
  
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

  // FSA Rating helper functions (matching FSAExplorer style)
  const getFSARatingColor = (rating?: number | string | null) => {
    if (!rating) return 'text-gray-500';
    const numRating = typeof rating === 'string' ? parseFloat(rating) : rating;
    if (numRating >= 5) return 'text-green-600';
    if (numRating >= 4) return 'text-blue-600';
    if (numRating >= 3) return 'text-yellow-600';
    return 'text-red-600';
  };

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
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
      {/* Hero Header */}
      <div className="relative overflow-hidden bg-gradient-to-r from-[#1E2A44] via-[#2D3E5F] to-[#1E2A44]">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
            backgroundSize: '40px 40px',
          }}></div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
          <div className="text-center">
            <div className="inline-flex items-center px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full text-white text-sm font-medium mb-4">
              <Sparkles className="w-4 h-4 mr-2" />
              Professional Assessment Report
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              156-Point Matching Analysis
            </h1>
            <p className="text-xl text-gray-200 max-w-3xl mx-auto">
              Comprehensive intelligence for confident placement decisions. 
              Analyzing 15+ data sources including financial stability, staff quality, and medical capabilities.
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-4 text-sm text-gray-300">
              <div className="flex items-center">
                <CheckCircle2 className="w-4 h-4 mr-2" />
                5 Care Homes Analyzed
              </div>
              <div className="flex items-center">
                <CheckCircle2 className="w-4 h-4 mr-2" />
                93-95% Confidence Level
              </div>
              <div className="flex items-center">
                <CheckCircle2 className="w-4 h-4 mr-2" />
                30-35 Page PDF Report
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
                  className={`flex-1 py-4 px-6 text-center font-semibold text-sm md:text-base transition-colors border-b-2 ${
                    activeTab === 'report' && !isLoading && report
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
                  className={`flex-1 py-4 px-6 text-center font-semibold text-sm md:text-base transition-colors border-b-2 ${
                    activeTab === 'profile'
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
                  className={`flex-1 py-4 px-6 text-center font-semibold text-sm md:text-base transition-colors border-b-2 ${
                    activeTab === 'guide'
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
            <QuestionnaireProfile questionnaire={questionnaire} />
          </div>
        ) : activeTab === 'guide' ? (
          <div className="w-full">
            <ProfessionalReportGuide />
          </div>
        ) : null}

        {/* Report Display */}
        {report && activeTab === 'report' ? (
              <div className="w-full">
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                  {/* Navigation Sidebar - Left Menu */}
                  <div className="lg:col-span-1">
                    <ReportNavigation
                      sections={[
                        { id: 'executive-summary', label: 'Executive Summary', icon: <Home className="w-4 h-4" />, hasData: true },
                        { id: 'summary', label: 'Dashboard', icon: <BarChart3 className="w-4 h-4" />, hasData: true },
                        { id: 'priorities-match', label: 'Your Priorities Match', icon: <Target className="w-4 h-4" />, hasData: true },
                        { id: 'homes', label: 'Top 5 Homes', icon: <Building2 className="w-4 h-4" />, hasData: report.careHomes.length > 0 },
                        { id: 'funding', label: 'Funding Optimization', icon: <DollarSign className="w-4 h-4" />, hasData: !!report.fundingOptimization },
                        { id: 'cost-analysis', label: 'Cost Analysis', icon: <TrendingUp className="w-4 h-4" />, hasData: report.careHomes.length > 0 },
                        { 
                          id: 'fair-cost-gap', 
                          label: 'Fair Cost Gap', 
                          icon: <AlertCircle className="w-4 h-4" />, 
                          hasData: (() => {
                            const hasData = !!report.fairCostGapAnalysis;
                            console.log('Fair Cost Gap hasData check:', {
                              fairCostGapAnalysis: report.fairCostGapAnalysis,
                              hasData,
                              type: typeof report.fairCostGapAnalysis,
                              isNull: report.fairCostGapAnalysis === null,
                              isUndefined: report.fairCostGapAnalysis === undefined
                            });
                            return hasData;
                          })()
                        },
                        { id: 'comparative', label: 'Comparative Analysis', icon: <BarChart3 className="w-4 h-4" />, hasData: !!report.comparativeAnalysis },
                        { id: 'risks', label: 'Risk Assessment', icon: <AlertCircle className="w-4 h-4" />, hasData: !!report.riskAssessment },
                        { id: 'negotiation', label: 'Negotiation Strategy', icon: <FileTextIcon className="w-4 h-4" />, hasData: !!report.negotiationStrategy },
                        { id: 'funding-options', label: 'Funding Options', icon: <DollarSign className="w-4 h-4" />, hasData: true },
                        { id: 'actionplan', label: '14-Day Action Plan', icon: <CheckCircle2 className="w-4 h-4" />, hasData: true },
                        { id: 'nextsteps', label: 'Next Steps', icon: <CheckCircle2 className="w-4 h-4" />, hasData: !!report.nextSteps },
                      ]}
                      activeSection={activeSection}
                      onSectionClick={(sectionId) => {
                        setActiveSection(sectionId);
                        const element = sectionRefs.current[sectionId];
                        if (element) {
                          element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }
                      }}
                    />
                  </div>

                  {/* Main Report Content - Full Width */}
                  <div className="lg:col-span-3">
                    <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8 border border-gray-100">
                      <div className="mb-6">
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">Professional Report Generated</h2>
                        <p className="text-gray-600">Report ID: {report.reportId}</p>
                      </div>
                      
                      <div className="space-y-4">
                        {/* Executive Summary Section (Page 1) */}
                        <div 
                          id="executive-summary" 
                          ref={(el) => { sectionRefs.current['executive-summary'] = el; }}
                          className="scroll-mt-4 mb-6 p-4 bg-gradient-to-r from-gray-50 to-slate-50 rounded-lg border border-gray-200"
                        >
                          <ExecutiveSummarySection 
                            report={report} 
                            onNavigateToSection={(sectionId) => {
                              const el = sectionRefs.current[sectionId];
                              if (el) {
                                el.scrollIntoView({ behavior: 'smooth' });
                              }
                            }}
                          />
                        </div>

                        {/* Executive Summary Dashboard (Metrics) */}
                        <div 
                          id="summary" 
                          ref={(el) => { sectionRefs.current['summary'] = el; }}
                          className="scroll-mt-4 mb-6"
                        >
                          <ExecutiveSummaryDashboard report={report} />
                        </div>

                        {/* Your Priorities Match Section (Page 4) */}
                        <div 
                          id="priorities-match" 
                          ref={(el) => { sectionRefs.current['priorities-match'] = el; }}
                          className="scroll-mt-4 mb-6 p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-200"
                        >
                          <PrioritiesMatchSection 
                            report={report} 
                            questionnaire={questionnaire || undefined}
                          />
                        </div>


                        {/* Dynamic Weights Explanation */}
                        {report.appliedWeights && (
                          <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                            <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                              <Sparkles className="w-5 h-5 mr-2 text-blue-600" />
                              Match Score Explanation
                            </h3>
                            <p className="text-sm text-gray-700 mb-3">
                              Your match scores are calculated using adaptive weights based on your specific needs:
                            </p>
                            
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                              <div className="bg-white rounded-lg p-2 border border-blue-100">
                                <div className="text-xs text-gray-500">Medical</div>
                                <div className="text-lg font-bold text-blue-900">{report.appliedWeights.medical}%</div>
                              </div>
                              <div className="bg-white rounded-lg p-2 border border-blue-100">
                                <div className="text-xs text-gray-500">Safety</div>
                                <div className="text-lg font-bold text-blue-900">{report.appliedWeights.safety}%</div>
                              </div>
                              <div className="bg-white rounded-lg p-2 border border-blue-100">
                                <div className="text-xs text-gray-500">Location</div>
                                <div className="text-lg font-bold text-blue-900">{report.appliedWeights.location}%</div>
                              </div>
                              <div className="bg-white rounded-lg p-2 border border-blue-100">
                                <div className="text-xs text-gray-500">Financial</div>
                                <div className="text-lg font-bold text-blue-900">{report.appliedWeights.financial}%</div>
                              </div>
                              <div className="bg-white rounded-lg p-2 border border-blue-100">
                                <div className="text-xs text-gray-500">Staff</div>
                                <div className="text-lg font-bold text-blue-900">{report.appliedWeights.staff}%</div>
                              </div>
                              <div className="bg-white rounded-lg p-2 border border-blue-100">
                                <div className="text-xs text-gray-500">CQC</div>
                                <div className="text-lg font-bold text-blue-900">{report.appliedWeights.cqc}%</div>
                              </div>
                              <div className="bg-white rounded-lg p-2 border border-blue-100">
                                <div className="text-xs text-gray-500">Social</div>
                                <div className="text-lg font-bold text-blue-900">{report.appliedWeights.social}%</div>
                              </div>
                              <div className="bg-white rounded-lg p-2 border border-blue-100">
                                <div className="text-xs text-gray-500">Services</div>
                                <div className="text-lg font-bold text-blue-900">{report.appliedWeights.services}%</div>
                              </div>
                            </div>
                            
                            {report.appliedConditions && report.appliedConditions.length > 0 && (
                              <div className="mt-3 pt-3 border-t border-blue-200">
                                <div className="text-xs font-semibold text-gray-700 mb-1">Applied Conditions:</div>
                                <div className="flex flex-wrap gap-2">
                                  {report.appliedConditions.map((condition, idx) => (
                                    <span
                                      key={idx}
                                      className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full"
                                    >
                                      {condition.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                    </span>
                                  ))}
                                </div>
                                <p className="text-xs text-gray-600 mt-2 italic">
                                  These conditions triggered weight adjustments to prioritize factors most important for your profile.
                                </p>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Top 5 Recommendations Section */}
                        <div 
                          id="homes" 
                          ref={(el) => { sectionRefs.current['homes'] = el; }}
                          className="scroll-mt-4 mt-6"
                        >
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="font-semibold text-gray-900 text-xl">Top 5 Recommendations</h3>
                        <button
                          onClick={() => {
                            const allExpanded = report.careHomes.slice(0, 5).every(h => expandedHomes.has(h.id));
                            if (allExpanded) {
                              setExpandedHomes(new Set());
                            } else {
                              setExpandedHomes(new Set(report.careHomes.slice(0, 5).map(h => h.id)));
                            }
                          }}
                          className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                        >
                          {expandedHomes.size === report.careHomes.slice(0, 5).length ? (
                            <>
                              <ChevronUp className="w-3 h-3" />
                              Collapse All
                            </>
                          ) : (
                            <>
                              <ChevronDown className="w-3 h-3" />
                              Expand All
                            </>
                          )}
                        </button>
                      </div>
                      <div className="space-y-4">
                        {report.careHomes.slice(0, 5).map((home, index) => {
                          const isExpanded = expandedHomes.has(home.id);
                          return (
                            <div key={home.id} className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
                              {/* Collapsible Header */}
                              <button
                                onClick={() => {
                                  const newExpanded = new Set(expandedHomes);
                                  if (isExpanded) {
                                    newExpanded.delete(home.id);
                                  } else {
                                    newExpanded.add(home.id);
                                  }
                                  setExpandedHomes(newExpanded);
                                }}
                                className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
                              >
                                <div className="flex items-center gap-3 flex-1">
                                  <span className="text-xs font-semibold text-white bg-[#1E2A44] px-2 py-1 rounded">
                                    #{index + 1}
                                  </span>
                                  <div className="flex-1 text-left">
                                    <div className="flex items-center gap-2 flex-wrap">
                                      <div className="font-semibold text-gray-900 text-lg">{home.name}</div>
                                      {/* Category Winner Badges */}
                                      {home.category_labels && home.category_labels.length > 0 && (
                                        <div className="flex flex-wrap gap-1">
                                          {home.category_labels.map((label, idx) => {
                                            const isAutomatic = label.includes('Medical & Safety');
                                            return (
                                              <span
                                                key={idx}
                                                className={`text-xs font-semibold px-2 py-0.5 rounded ${
                                                  isAutomatic
                                                    ? 'bg-red-100 text-red-700 border border-red-300'
                                                    : 'bg-blue-100 text-blue-700 border border-blue-300'
                                                }`}
                                                title={isAutomatic ? 'Determined automatically from your medical needs' : 'Based on your priorities'}
                                              >
                                                {isAutomatic && '🏥 '}
                                                {label}
                                              </span>
                                            );
                                          })}
                                        </div>
                                      )}
                                    </div>
                                    <div className="text-sm text-gray-600">
                                      {home.location} • Match: <span className="font-semibold text-[#10B981]">{home.matchScore.toFixed(1)}%</span> • £{home.weeklyPrice}/week
                                      {home.value_ratio && home.value_ratio > 0 && (
                                        <span className="ml-2 text-xs text-emerald-600 font-medium">
                                          • Value: {home.value_ratio.toFixed(2)}x
                                        </span>
                                      )}
                                    </div>
                                    {/* Match Reason and Waiting List Status */}
                                    <div className="mt-1 flex flex-wrap items-center gap-2 text-xs">
                                      {home.matchReason && (
                                        <span className="text-blue-700 bg-blue-50 px-2 py-0.5 rounded">
                                          {home.matchReason}
                                        </span>
                                      )}
                                      {home.waitingListStatus && (
                                        <span className={`px-2 py-0.5 rounded font-semibold ${
                                          home.waitingListStatus === 'Available now' 
                                            ? 'text-green-700 bg-green-50' 
                                            : home.waitingListStatus === '2-4 weeks'
                                            ? 'text-yellow-700 bg-yellow-50'
                                            : 'text-red-700 bg-red-50'
                                        }`}>
                                          {home.waitingListStatus}
                                        </span>
                                      )}
                                    </div>
                                  </div>
                                </div>
                                {isExpanded ? (
                                  <ChevronUp className="w-5 h-5 text-gray-400" />
                                ) : (
                                  <ChevronDown className="w-5 h-5 text-gray-400" />
                                )}
                              </button>

                              {/* Expandable Content */}
                              {isExpanded && (
                                <div className="p-4 pt-0 border-t border-gray-200 space-y-4">
                                  {/* Photo */}
                                  <div className="relative h-48 bg-gradient-to-br from-gray-200 to-gray-300 rounded-lg overflow-hidden mb-4">
                                    {home.photo ? (
                                      <img
                                        src={home.photo}
                                        alt={home.name}
                                        className="w-full h-full object-cover"
                                        onError={(e) => {
                                          (e.target as HTMLImageElement).style.display = 'none';
                                        }}
                                      />
                                    ) : (
                                      <div className="w-full h-full flex items-center justify-center text-gray-400">
                                        <span className="text-4xl">🏠</span>
                                      </div>
                                    )}
                                    {/* Match Score Badge */}
                                    <div className="absolute top-3 right-3">
                                      <div className="bg-white/90 backdrop-blur-sm rounded-full px-3 py-1 shadow-md">
                                        <span className="text-sm font-bold text-[#1E2A44]">{home.matchScore.toFixed(1)}% Match</span>
                                      </div>
                                    </div>
                                    {/* CQC Rating Badge */}
                                    <div className="absolute top-3 left-3">
                                      <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-white/90 backdrop-blur-sm shadow-md text-gray-900">
                                        CQC: {home.cqcRating}
                                      </span>
                                    </div>
                                  </div>

                                  {/* Category Reasoning (if available) */}
                                  {home.category_reasoning && Object.keys(home.category_reasoning).length > 0 && (
                                    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
                                      <h5 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                                        <span className="text-blue-600">💡</span>
                                        Why This Home Was Recommended
                                      </h5>
                                      <div className="space-y-2">
                                        {Object.entries(home.category_reasoning).map(([categoryKey, reasons]) => {
                                          const categoryLabel = home.category_labels?.find((_, idx) => {
                                            const keys = Object.keys(home.category_reasoning || {});
                                            return keys[idx] === categoryKey;
                                          }) || categoryKey;
                                          
                                          return (
                                            <div key={categoryKey} className="text-sm">
                                              <div className="font-medium text-gray-800 mb-1">
                                                {categoryLabel}:
                                              </div>
                                              <ul className="list-disc list-inside text-gray-700 space-y-1 ml-2">
                                                {Array.isArray(reasons) ? reasons.map((reason, idx) => (
                                                  <li key={idx}>{reason}</li>
                                                )) : (
                                                  <li>{String(reasons)}</li>
                                                )}
                                              </ul>
                                            </div>
                                          );
                                        })}
                                      </div>
                                    </div>
                                  )}

                                  {/* Match Score Radar Chart */}
                                  <div className="mt-4">
                                    <MatchScoreRadarChart home={home} />
                                  </div>

                                  {/* FSA Detailed Ratings - Professional Tier Report Style */}
                                  <div className="bg-white rounded-lg shadow p-6 border-2 border-blue-200">
                                    <div className="flex items-center justify-between mb-4">
                                      <h4 className="text-xl font-semibold flex items-center gap-2">
                                        <FileText className="w-5 h-5 text-blue-600" />
                                        Food Hygiene Rating
                                      </h4>
                                      <span className="text-sm text-gray-500">Professional Analysis</span>
                                    </div>

                                    {/* Basic Rating */}
                                    <div className="mb-6">
                                      <p className="text-sm text-gray-600 mb-1">Food Hygiene Rating</p>
                                      <div className="flex items-center gap-3">
                                        {(() => {
                                          const rating = home.fsaDetailed?.rating;
                                          const ratingNum = rating !== null && rating !== undefined 
                                            ? (typeof rating === 'string' ? parseFloat(rating) : rating) 
                                            : null;
                                          return (
                                            <>
                                              <span className={`text-4xl font-bold ${getFSARatingColor(ratingNum)}`}>
                                                {ratingNum !== null ? `${ratingNum}/5` : 'N/A'}
                                              </span>
                                              <div>
                                                <p className="font-semibold">{getFSARatingLabel(ratingNum)}</p>
                                                {home.fsaDetailed?.rating_date && (
                                                  <p className="text-sm text-gray-500">
                                                    Inspected: {new Date(home.fsaDetailed.rating_date).toLocaleDateString()}
                                                  </p>
                                                )}
                                              </div>
                                            </>
                                          );
                                        })()}
                                      </div>
                                    </div>

                                    {/* Breakdown Scores - UNIFIED: Using RAW scores from FSA API */}
                                    {/* FSA scores are penalty points: lower is better (0 = best) */}
                                    {home.fsaDetailed?.breakdown_scores ? (
                                      <div className="mb-6">
                                        <h5 className="text-lg font-semibold mb-3">Detailed Breakdown Scores</h5>
                                        <p className="text-xs text-gray-500 mb-3">
                                          FSA penalty points (lower = better, 0 = excellent)
                                        </p>
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                          {/* Hygiene - RAW score directly from FSA API */}
                                          <div className="border-l-4 border-blue-500 pl-4">
                                            <p className="text-sm text-gray-600 mb-1">Hygiene</p>
                                            {(() => {
                                              const hygieneScore = home.fsaDetailed?.breakdown_scores?.hygiene;
                                              const hygieneLabel = home.fsaDetailed?.breakdown_scores?.hygiene_label;
                                              return (
                                                <>
                                                  <p className="text-2xl font-bold text-blue-600">
                                                    {hygieneScore !== null && hygieneScore !== undefined ? `${hygieneScore}/20` : 'N/A'}
                                                  </p>
                                                  {hygieneLabel && (
                                                    <p className="text-sm text-gray-600 mt-1">
                                                      {hygieneLabel}
                                                    </p>
                                                  )}
                                                </>
                                              );
                                            })()}
                                          </div>

                                          {/* Structural - RAW score directly from FSA API */}
                                          <div className="border-l-4 border-green-500 pl-4">
                                            <p className="text-sm text-gray-600 mb-1">Structural</p>
                                            {(() => {
                                              const structuralScore = home.fsaDetailed?.breakdown_scores?.structural;
                                              const structuralLabel = home.fsaDetailed?.breakdown_scores?.structural_label;
                                              return (
                                                <>
                                                  <p className="text-2xl font-bold text-green-600">
                                                    {structuralScore !== null && structuralScore !== undefined ? `${structuralScore}/20` : 'N/A'}
                                                  </p>
                                                  {structuralLabel && (
                                                    <p className="text-sm text-gray-600 mt-1">
                                                      {structuralLabel}
                                                    </p>
                                                  )}
                                                </>
                                              );
                                            })()}
                                          </div>

                                          {/* Management - RAW score directly from FSA API */}
                                          <div className="border-l-4 border-purple-500 pl-4">
                                            <p className="text-sm text-gray-600 mb-1">Management</p>
                                            {(() => {
                                              const managementScore = home.fsaDetailed?.breakdown_scores?.confidence_in_management;
                                              const managementLabel = home.fsaDetailed?.breakdown_scores?.confidence_label;
                                              return (
                                                <>
                                                  <p className="text-2xl font-bold text-purple-600">
                                                    {managementScore !== null && managementScore !== undefined ? `${managementScore}/30` : 'N/A'}
                                                  </p>
                                                  {managementLabel && (
                                                    <p className="text-sm text-gray-600 mt-1">
                                                      {managementLabel}
                                                    </p>
                                                  )}
                                                </>
                                              );
                                            })()}
                                          </div>
                                        </div>
                                      </div>
                                    ) : home.fsaDetailed?.data_available === false ? (
                                      <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                                        <p className="text-sm text-yellow-800">
                                          {home.fsaDetailed?.note || 'Food hygiene rating data is not available for this care home. This may be because the establishment does not have a registered kitchen or the data has not been updated in our system.'}
                                        </p>
                                      </div>
                                    ) : (
                                      <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
                                        <p className="text-sm text-gray-600">
                                          Detailed breakdown scores not available. Only overall rating shown above.
                                        </p>
                                      </div>
                                    )}

                                    {/* FSA Inspection History - Only show if historical data available */}
                                    {home.fsaDetailed && home.fsaDetailed.historical_ratings && home.fsaDetailed.historical_ratings.length > 0 && (
                                      <div className="mt-6 pt-6 border-t border-green-200">
                                        <FSAInspectionHistory fsaData={home.fsaDetailed} />
                                      </div>
                                    )}
                                  </div>

                                  {/* Financial Stability Summary - Always show, even if data is missing */}
                                  <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                                    <h4 className="text-xs font-semibold text-gray-900 mb-2">Financial Stability Analysis</h4>
                                    <div className="grid grid-cols-2 gap-2 text-xs">
                                      <div>
                                        <div className="text-gray-500">Altman Z-Score</div>
                                        <div className="font-semibold text-gray-900">
                                          {home.financialStability?.altman_z_score !== null && home.financialStability?.altman_z_score !== undefined
                                            ? home.financialStability.altman_z_score.toFixed(2)
                                            : 'NA'}
                                        </div>
                                      </div>
                                      <div>
                                        <div className="text-gray-500">Bankruptcy Risk</div>
                                        <div className="font-semibold text-gray-900">
                                          {home.financialStability?.bankruptcy_risk_score !== null && home.financialStability?.bankruptcy_risk_score !== undefined
                                            ? `${home.financialStability.bankruptcy_risk_score}/100`
                                            : 'NA'}
                                        </div>
                                        <div className="text-gray-400 text-xs">
                                          {home.financialStability?.bankruptcy_risk_level || 'NA'}
                                        </div>
                                      </div>
                                      <div>
                                        <div className="text-gray-500">3-Year Revenue Trend</div>
                                        <div className="font-semibold text-gray-900">
                                          {home.financialStability?.three_year_summary?.revenue_trend || 'NA'}
                                        </div>
                                      </div>
                                      <div>
                                        <div className="text-gray-500">Net Margin (3yr avg)</div>
                                        <div className="font-semibold text-gray-900">
                                          {home.financialStability?.three_year_summary?.net_margin_3yr_avg !== null && home.financialStability?.three_year_summary?.net_margin_3yr_avg !== undefined
                                            ? `${(home.financialStability.three_year_summary.net_margin_3yr_avg * 100).toFixed(1)}%`
                                            : 'NA'}
                                        </div>
                                      </div>
                                    </div>
                                    {home.financialStability?.red_flags && home.financialStability.red_flags.length > 0 && (
                                      <div className="mt-2 pt-2 border-t border-blue-200">
                                        <div className="text-xs text-red-600 font-semibold">Red Flags: {home.financialStability.red_flags.length}</div>
                                      </div>
                                    )}
                                  </div>

                                  {/* Staff Quality Analysis - Section 9 */}
                                  <StaffQualitySection staffQuality={home.staffQuality} homeName={home.name} />

                                  {/* Neighbourhood Analysis - Section 18 */}
                                  <NeighbourhoodSection neighbourhood={home.neighbourhood} homeName={home.name} />

                                  {/* Google Places Reviews & Sentiment & NEW API Insights - Always show, even if data is missing */}
                                  <div className="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                                      <h4 className="text-xs font-semibold text-gray-900 mb-2 flex items-center">
                                        <Star className="w-4 h-4 mr-1 text-yellow-600" />
                                        Google Places Insights (NEW API)
                                      </h4>
                                      
                                      {/* Basic Data */}
                                      <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                                        <div>
                                          <div className="text-gray-500">Rating</div>
                                          <div className="font-semibold text-gray-900">
                                            {home.googlePlaces?.rating !== null && home.googlePlaces?.rating !== undefined
                                              ? `${home.googlePlaces.rating}/5`
                                              : 'NA'}
                                          </div>
                                        </div>
                                        <div>
                                          <div className="text-gray-500">Review Count</div>
                                          <div className="font-semibold text-gray-900">
                                            {home.googlePlaces?.user_ratings_total !== null && home.googlePlaces?.user_ratings_total !== undefined
                                              ? home.googlePlaces.user_ratings_total
                                              : 'NA'}
                                          </div>
                                        </div>
                                        <div className="col-span-2">
                                          <div className="text-gray-500">Sentiment Analysis</div>
                                          <div className="font-semibold text-gray-900">
                                            {home.googlePlaces?.sentiment_analysis?.sentiment_label || 'NA'}
                                          </div>
                                          {home.googlePlaces?.sentiment_analysis?.sentiment_distribution && (
                                            <div className="text-xs text-gray-400 mt-1">
                                              Positive: {home.googlePlaces.sentiment_analysis.sentiment_distribution.positive || 0}% • 
                                              Negative: {home.googlePlaces.sentiment_analysis.sentiment_distribution.negative || 0}% • 
                                              Neutral: {home.googlePlaces.sentiment_analysis.sentiment_distribution.neutral || 0}%
                                            </div>
                                          )}
                                        </div>
                                      </div>
                                      
                                      {/* NEW API Insights */}
                                      {(home.googlePlaces?.average_dwell_time_minutes !== null && home.googlePlaces?.average_dwell_time_minutes !== undefined) ||
                                       (home.googlePlaces?.repeat_visitor_rate !== null && home.googlePlaces?.repeat_visitor_rate !== undefined) ||
                                       home.googlePlaces?.footfall_trend ||
                                       home.googlePlaces?.family_engagement_score ? (
                                        <div className="pt-2 border-t border-yellow-200">
                                          <div className="text-xs font-semibold text-gray-700 mb-2">Visitor Patterns (NEW API):</div>
                                          <div className="grid grid-cols-2 gap-2 text-xs">
                                            {home.googlePlaces?.average_dwell_time_minutes !== null && home.googlePlaces?.average_dwell_time_minutes !== undefined && (
                                              <div>
                                                <div className="text-gray-500">Dwell Time</div>
                                                <div className="font-semibold text-gray-900">
                                                  {home.googlePlaces.average_dwell_time_minutes.toFixed(1)} min
                                                </div>
                                              </div>
                                            )}
                                            {home.googlePlaces?.repeat_visitor_rate !== null && home.googlePlaces?.repeat_visitor_rate !== undefined && (
                                              <div>
                                                <div className="text-gray-500">Repeat Visitor Rate</div>
                                                <div className="font-semibold text-gray-900">
                                                  {(home.googlePlaces.repeat_visitor_rate * 100).toFixed(1)}%
                                                </div>
                                              </div>
                                            )}
                                            {home.googlePlaces?.footfall_trend && (
                                              <div>
                                                <div className="text-gray-500">Footfall Trend</div>
                                                <div className={`font-semibold ${
                                                  home.googlePlaces.footfall_trend === 'growing' ? 'text-green-700' :
                                                  home.googlePlaces.footfall_trend === 'declining' ? 'text-red-700' :
                                                  'text-gray-700'
                                                }`}>
                                                  {home.googlePlaces.footfall_trend.charAt(0).toUpperCase() + home.googlePlaces.footfall_trend.slice(1)}
                                                </div>
                                              </div>
                                            )}
                                            {home.googlePlaces?.family_engagement_score !== null && home.googlePlaces?.family_engagement_score !== undefined && (
                                              <div>
                                                <div className="text-gray-500">Family Engagement</div>
                                                <div className="font-semibold text-gray-900">
                                                  {home.googlePlaces.family_engagement_score.toFixed(1)}/100
                                                </div>
                                              </div>
                                            )}
                                          </div>
                                          {home.googlePlaces?.quality_indicator && (
                                            <div className="mt-2 pt-2 border-t border-yellow-100">
                                              <div className="text-xs">
                                                <span className="text-gray-500">Quality Indicator: </span>
                                                <span className="font-semibold text-gray-900">{home.googlePlaces.quality_indicator}</span>
                                              </div>
                                            </div>
                                          )}
                                        </div>
                                      ) : (
                                        <div className="pt-2 border-t border-yellow-200 text-xs text-gray-400">
                                          Visitor patterns data not available (NEW API insights)
                                        </div>
                                      )}
                                    </div>

                                  {/* Community Reputation (Section 10) */}
                                  {home.communityReputation && (
                                    <div className="mb-4 p-4 bg-white rounded-lg border border-purple-200">
                                      <CommunityReputationSection home={home} />
                                    </div>
                                  )}

                                  {/* Medical Care (Section 8) */}
                                  {home.medicalCare && (
                                    <div className="mb-4 p-4 bg-white rounded-lg border border-red-200">
                                      <MedicalCareSection home={home} />
                                    </div>
                                  )}

                                  {/* Comfort & Lifestyle (Section 16) */}
                                  {home.comfortLifestyle && (
                                    <div className="mb-4 p-4 bg-white rounded-lg border border-indigo-200">
                                      <ComfortLifestyleSection home={home} />
                                    </div>
                                  )}

                                  {/* Lifestyle Deep Dive (Section 17) */}
                                  {home.lifestyleDeepDive && (
                                    <div className="mb-4 p-4 bg-white rounded-lg border border-pink-200">
                                      <LifestyleDeepDiveSection home={home} />
                                    </div>
                                  )}

                                  {/* Safety Analysis (Section 6) */}
                                  {home.safetyAnalysis && (
                                    <div className="mb-4 p-4 bg-white rounded-lg border border-orange-200">
                                      <SafetyAnalysisSection home={home} />
                                    </div>
                                  )}

                                  {/* Location Wellbeing (Section 18) */}
                                  {home.locationWellbeing && (
                                    <div className="mb-4 p-4 bg-white rounded-lg border border-emerald-200">
                                      <LocationWellbeingSection home={home} />
                                    </div>
                                  )}

                                  {/* Area Map (Section 19) */}
                                  {home.areaMap && (
                                    <div className="mb-4 p-4 bg-white rounded-lg border border-teal-200">
                                      <AreaMapSection home={home} />
                                    </div>
                                  )}

                                  {/* Family Engagement (Section 11) */}
                                  {home.familyEngagement && (
                                    <div className="mb-4 p-4 bg-white rounded-lg border border-cyan-200">
                                      <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                                        <User className="w-5 h-5 text-cyan-600" />
                                        Family Engagement (Section 11)
                                      </h4>
                                      <div className="grid grid-cols-2 gap-4 text-sm">
                                        <div>
                                          <div className="text-gray-600 mb-1">Engagement Score</div>
                                          <div className="text-2xl font-bold text-cyan-600">
                                            {home.familyEngagement.engagement_score !== null && home.familyEngagement.engagement_score !== undefined
                                              ? `${home.familyEngagement.engagement_score.toFixed(1)}/100`
                                              : 'N/A'}
                                          </div>
                                        </div>
                                        <div>
                                          <div className="text-gray-600 mb-1">Data Source</div>
                                          <div className="font-semibold text-gray-900">
                                            {home.familyEngagement.data_source || 'N/A'}
                                          </div>
                                          <div className="text-xs text-gray-500 mt-1">
                                            Confidence: {home.familyEngagement.confidence || 'N/A'}
                                          </div>
                                        </div>
                                        {home.familyEngagement.dwell_time_minutes !== null && (
                                          <div>
                                            <div className="text-gray-600 mb-1">Average Dwell Time</div>
                                            <div className="font-semibold text-gray-900">
                                              {home.familyEngagement.dwell_time_minutes} minutes
                                            </div>
                                          </div>
                                        )}
                                        {home.familyEngagement.repeat_visitor_rate !== null && (
                                          <div>
                                            <div className="text-gray-600 mb-1">Repeat Visitor Rate</div>
                                            <div className="font-semibold text-gray-900">
                                              {(home.familyEngagement.repeat_visitor_rate * 100).toFixed(1)}%
                                            </div>
                                          </div>
                                        )}
                                        {home.familyEngagement.footfall_trend && (
                                          <div className="col-span-2">
                                            <div className="text-gray-600 mb-1">Footfall Trend</div>
                                            <div className="font-semibold text-gray-900 capitalize">
                                              {home.familyEngagement.footfall_trend}
                                            </div>
                                          </div>
                                        )}
                                        {home.familyEngagement.quality_indicator && (
                                          <div className="col-span-2">
                                            <div className="text-gray-600 mb-1">Quality Indicator</div>
                                            <div className="text-sm text-gray-700">
                                              {home.familyEngagement.quality_indicator}
                                            </div>
                                          </div>
                                        )}
                                        {home.familyEngagement.methodology_note && (
                                          <div className="col-span-2 pt-2 border-t border-gray-200">
                                            <div className="text-xs text-gray-500 italic">
                                              {home.familyEngagement.methodology_note}
                                            </div>
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  )}

                                  {/* Funding Options (Section 14) */}
                                  {home.fundingOptions && (
                                    <div className="mb-4 p-4 bg-white rounded-lg border border-green-200">
                                      <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                                        <DollarSign className="w-5 h-5 text-green-600" />
                                        Funding Options (Section 14)
                                      </h4>
                                      <div className="space-y-3 text-sm">
                                        {home.fundingOptions.chcEligibility && (
                                          <div className="p-3 bg-green-50 rounded-lg border border-green-100">
                                            <div className="font-semibold text-gray-900 mb-2">NHS Continuing Healthcare (CHC)</div>
                                            <div className="grid grid-cols-2 gap-2">
                                              <div>
                                                <div className="text-gray-600 text-xs">Eligibility Level</div>
                                                <div className="font-semibold text-gray-900 capitalize">
                                                  {home.fundingOptions.chcEligibility.eligibility_level?.replace(/_/g, ' ') || 'N/A'}
                                                </div>
                                              </div>
                                              <div>
                                                <div className="text-gray-600 text-xs">Probability</div>
                                                <div className="font-semibold text-green-700">
                                                  {home.fundingOptions.chcEligibility.probability_percent || 0}%
                                                </div>
                                              </div>
                                            </div>
                                          </div>
                                        )}
                                        {typeof home.fundingOptions.localAuthorityFunding === 'object' && home.fundingOptions.localAuthorityFunding && (
                                          <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
                                            <div className="font-semibold text-gray-900 mb-2">Local Authority Funding</div>
                                            <div className="grid grid-cols-2 gap-2 text-xs">
                                              <div>
                                                <div className="text-gray-600">Available</div>
                                                <div className="font-semibold text-gray-900">
                                                  {home.fundingOptions.localAuthorityFunding.available ? 'Yes' : 'No'}
                                                </div>
                                              </div>
                                              {home.fundingOptions.localAuthorityFunding.contribution_amount > 0 && (
                                                <div>
                                                  <div className="text-gray-600">Contribution</div>
                                                  <div className="font-semibold text-gray-900">
                                                    £{home.fundingOptions.localAuthorityFunding.contribution_amount.toLocaleString()}
                                                  </div>
                                                </div>
                                              )}
                                            </div>
                                          </div>
                                        )}
                                        {home.fundingOptions.selfFunding && (
                                          <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
                                            <div className="font-semibold text-gray-900">Self-Funding</div>
                                            <div className="text-xs text-gray-600 mt-1">Available for all care homes</div>
                                          </div>
                                        )}
                                        {home.fundingOptions.notes && (
                                          <div className="text-xs text-gray-500 italic pt-2 border-t border-gray-200">
                                            {home.fundingOptions.notes}
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  )}

                                  {/* CQC Deep Dive - Always show, even if data is missing */}
                                  <div className="mb-4 p-3 bg-purple-50 rounded-lg border border-purple-200">
                                    <h4 className="text-xs font-semibold text-gray-900 mb-2">CQC Deep Dive</h4>
                                    <div className="grid grid-cols-2 gap-2 text-xs">
                                      <div>
                                        <div className="text-gray-500">Trend (3-5 years)</div>
                                        <div className="font-semibold text-gray-900">
                                          {home.cqcDeepDive?.trend || 'NA'}
                                        </div>
                                      </div>
                                      <div>
                                        <div className="text-gray-500">Active Action Plans</div>
                                        <div className="font-semibold text-gray-900">
                                          {home.cqcDeepDive?.action_plans ? home.cqcDeepDive.action_plans.length : 'NA'}
                                        </div>
                                      </div>
                                      <div className="col-span-2">
                                        <div className="text-gray-500 mb-1">Detailed Ratings</div>
                                        <div className="grid grid-cols-5 gap-1 text-xs">
                                          <div>
                                            <div className="text-gray-400">Safe</div>
                                            <div className="font-medium">{home.cqcDeepDive?.detailed_ratings?.safe?.rating || 'NA'}</div>
                                          </div>
                                          <div>
                                            <div className="text-gray-400">Effective</div>
                                            <div className="font-medium">{home.cqcDeepDive?.detailed_ratings?.effective?.rating || 'NA'}</div>
                                          </div>
                                          <div>
                                            <div className="text-gray-400">Caring</div>
                                            <div className="font-medium">{home.cqcDeepDive?.detailed_ratings?.caring?.rating || 'NA'}</div>
                                          </div>
                                          <div>
                                            <div className="text-gray-400">Responsive</div>
                                            <div className="font-medium">{home.cqcDeepDive?.detailed_ratings?.responsive?.rating || 'NA'}</div>
                                          </div>
                                          <div>
                                            <div className="text-gray-400">Well-led</div>
                                            <div className="font-medium">{home.cqcDeepDive?.detailed_ratings?.well_led?.rating || 'NA'}</div>
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                    {/* CQC Rating Trend Chart - Only show if data available */}
                                    {home.cqcDeepDive && home.cqcDeepDive.historical_ratings && home.cqcDeepDive.historical_ratings.length > 0 && (
                                      <div className="mt-4">
                                        <CQCRatingTrendChart cqcData={home.cqcDeepDive} homeName={home.name} />
                                      </div>
                                    )}

                                    {/* CQC Enforcement Actions - Always show (green = no issues, red = problems) */}
                                    {home.cqcDeepDive && (
                                      <div className="mt-4">
                                        <EnforcementActionsSection cqcData={home.cqcDeepDive} homeName={home.name} />
                                      </div>
                                    )}

                                    {/* CQC Regulated Activities & Licenses */}
                                    {home.cqcDeepDive && (
                                      <div className="mt-4">
                                        <RegulatedActivitiesSection cqcData={home.cqcDeepDive} homeName={home.name} />
                                      </div>
                                    )}
                                  </div>

                                  {/* Footfall & Visitor Trends - from Google Places Insights - SEPARATE SECTION */}
                                  {home.googlePlaces && (
                                    <div className="mb-4 p-3 bg-amber-50 rounded-lg border border-amber-200">
                                      <FootfallTrendsSection googlePlacesData={home.googlePlaces} homeName={home.name} />
                                    </div>
                                  )}

                                  {/* Financial Stability Charts - SEPARATE SECTION */}
                                  {home.financialStability && (
                                    <div className="mb-4 p-3 bg-emerald-50 rounded-lg border border-emerald-200">
                                      <FinancialStabilityChart financialData={home.financialStability} homeName={home.name} />
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>

                        {/* Funding Optimization Section */}
                        {report.fundingOptimization && (
                    <div 
                      id="funding" 
                      ref={(el) => { sectionRefs.current['funding'] = el; }}
                      className="scroll-mt-4 mt-6"
                    >
                      <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
                        <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
                          <Sparkles className="w-5 h-5 mr-2 text-green-600" />
                          Funding Optimization Analysis
                        </h3>
                        
                        {/* CHC Eligibility - Enhanced */}
                        <div className="mb-4 p-3 bg-white rounded-lg border border-green-100">
                          <h4 className="text-sm font-semibold text-gray-900 mb-2">NHS Continuing Healthcare (CHC) Calculator</h4>
                          <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                            <div>
                              <div className="text-gray-500">Eligibility Probability</div>
                              <div className="font-semibold text-gray-900 text-lg">
                                {report.fundingOptimization.chc_eligibility.eligibility_probability}%
                              </div>
                              <div className="text-gray-400 text-xs">
                                {report.fundingOptimization.chc_eligibility.eligibility_level.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                              </div>
                            </div>
                            <div>
                              <div className="text-gray-500">Potential Annual Savings</div>
                              <div className="font-semibold text-green-700 text-lg">
                                £{report.fundingOptimization.chc_eligibility.estimated_annual_savings.probability_adjusted.toLocaleString()}
                              </div>
                              <div className="text-gray-400 text-xs">
                                If approved: £{report.fundingOptimization.chc_eligibility.estimated_annual_savings.if_approved.toLocaleString()}
                              </div>
                            </div>
                          </div>
                          
                          {/* DST Domain Scores */}
                          {report.fundingOptimization.chc_eligibility.dst_domains && (
                            <div className="mb-3 pt-2 border-t border-green-100">
                              <div className="text-xs font-semibold text-gray-700 mb-2">DST Domain Assessment (12 domains):</div>
                              <div className="grid grid-cols-3 gap-1 text-xs">
                                {Object.entries(report.fundingOptimization.chc_eligibility.dst_domains).slice(0, 6).map(([domain, data]: [string, any]) => (
                                  <div key={domain} className="flex items-center justify-between">
                                    <span className="text-gray-500 capitalize">{domain.replace(/_/g, ' ')}:</span>
                                    <span className={`font-medium ${
                                      data.severity === 'A' ? 'text-red-600' : 
                                      data.severity === 'B' ? 'text-orange-600' : 
                                      'text-gray-400'
                                    }`}>
                                      {data.severity}
                                    </span>
                                  </div>
                                ))}
                              </div>
                              <div className="grid grid-cols-3 gap-1 text-xs mt-1">
                                {Object.entries(report.fundingOptimization.chc_eligibility.dst_domains).slice(6).map(([domain, data]: [string, any]) => (
                                  <div key={domain} className="flex items-center justify-between">
                                    <span className="text-gray-500 capitalize">{domain.replace(/_/g, ' ')}:</span>
                                    <span className={`font-medium ${
                                      data.severity === 'A' ? 'text-red-600' : 
                                      data.severity === 'B' ? 'text-orange-600' : 
                                      'text-gray-400'
                                    }`}>
                                      {data.severity}
                                    </span>
                                  </div>
                                ))}
                              </div>
                              <div className="mt-2 text-xs text-gray-500">
                                Priority (A): {report.fundingOptimization.chc_eligibility.assessment_details.priority_domains_count} • 
                                Severe (B): {report.fundingOptimization.chc_eligibility.assessment_details.severe_domains_count}
                              </div>
                            </div>
                          )}
                          
                          {/* Primary Health Need Indicator */}
                          {report.fundingOptimization.chc_eligibility.primary_health_need_score !== undefined && (
                            <div className="mb-2 pt-2 border-t border-green-100">
                              <div className="text-xs">
                                <span className="text-gray-500">Primary Health Need Score: </span>
                                <span className={`font-semibold ${
                                  report.fundingOptimization.chc_eligibility.primary_health_need_score >= 0.5 ? 'text-green-700' : 'text-gray-600'
                                }`}>
                                  {(report.fundingOptimization.chc_eligibility.primary_health_need_score * 100).toFixed(0)}%
                                </span>
                                {report.fundingOptimization.chc_eligibility.assessment_details.primary_health_need_indicated && (
                                  <span className="ml-2 text-green-600 font-medium">✓ Indicated</span>
                                )}
                              </div>
                            </div>
                          )}
                          
                          <div className="mt-2 text-xs text-gray-600">
                            {report.fundingOptimization.chc_eligibility.recommendation}
                          </div>
                        </div>

                        {/* LA Funding - Enhanced */}
                        <div className="mb-4 p-3 bg-white rounded-lg border border-green-100">
                          <h4 className="text-sm font-semibold text-gray-900 mb-2">Local Authority Funding Calculator</h4>
                          <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                            <div>
                              <div className="text-gray-500">Funding Available</div>
                              <div className={`font-semibold text-lg ${report.fundingOptimization.la_funding.funding_available ? 'text-green-700' : 'text-red-600'}`}>
                                {report.fundingOptimization.la_funding.funding_available ? 'Yes' : 'No'}
                              </div>
                              <div className="text-gray-400 text-xs">
                                {report.fundingOptimization.la_funding.funding_level.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                              </div>
                            </div>
                            <div>
                              <div className="text-gray-500">LA Contribution</div>
                              <div className="font-semibold text-gray-900 text-lg">
                                {report.fundingOptimization.la_funding.funding_split.la_contribution_percent}%
                              </div>
                              <div className="text-gray-400 text-xs">
                                Self: {report.fundingOptimization.la_funding.funding_split.self_contribution_percent}%
                              </div>
                            </div>
                          </div>
                          
                          {report.fundingOptimization.la_funding.capital_assessment && (
                            <div className="mb-2 pt-2 border-t border-green-100">
                              <div className="text-xs font-semibold text-gray-700 mb-1">Capital Assessment:</div>
                              <div className="grid grid-cols-2 gap-1 text-xs">
                                <div>
                                  <span className="text-gray-500">Total Capital:</span>
                                  <span className="ml-1 font-medium">£{report.fundingOptimization.la_funding.capital_assessment.total_assessable_capital.toLocaleString()}</span>
                                </div>
                                <div>
                                  <span className="text-gray-500">Threshold:</span>
                                  <span className="ml-1 font-medium">£{report.fundingOptimization.la_funding.capital_assessment.threshold.toLocaleString()}</span>
                                </div>
                              </div>
                            </div>
                          )}
                          
                          <div className="mt-2 pt-2 border-t border-green-100">
                            <div className="text-xs text-gray-600">
                              {report.fundingOptimization.la_funding.funding_explanation}
                            </div>
                          </div>
                        </div>

                        {/* DPA Considerations - Enhanced */}
                        <div className="mb-4 p-3 bg-white rounded-lg border border-green-100">
                          <h4 className="text-sm font-semibold text-gray-900 mb-2">Deferred Payment Agreement (DPA) Calculator</h4>
                          <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                            <div>
                              <div className="text-gray-500">DPA Eligible</div>
                              <div className={`font-semibold text-lg ${report.fundingOptimization.dpa_considerations.dpa_eligible ? 'text-green-700' : 'text-red-600'}`}>
                                {report.fundingOptimization.dpa_considerations.dpa_eligible ? 'Yes' : 'No'}
                              </div>
                            </div>
                            <div>
                              <div className="text-gray-500">Available Deferral</div>
                              <div className="font-semibold text-gray-900 text-lg">
                                £{report.fundingOptimization.dpa_considerations.deferral_limits.available_deferral.toLocaleString()}
                              </div>
                              <div className="text-gray-400 text-xs">
                                {report.fundingOptimization.dpa_considerations.deferral_limits.years_coverable > 0 && (
                                  <>Covers {report.fundingOptimization.dpa_considerations.deferral_limits.years_coverable.toFixed(1)} years</>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* 5-Year Projections - Enhanced with Charts */}
                        {report.fundingOptimization.five_year_projections && (
                          <div className="mb-4 p-4 bg-white rounded-lg border border-green-100">
                            <h4 className="text-sm font-semibold text-gray-900 mb-4 flex items-center">
                              <Sparkles className="w-4 h-4 mr-2 text-green-600" />
                              5-Year Cost Projections
                            </h4>
                            
                            {/* Summary Cards */}
                            <div className="grid grid-cols-2 gap-3 mb-4">
                              <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                                <div className="text-xs text-gray-500 mb-1">Self-Funding (5yr)</div>
                                <div className="font-semibold text-gray-900 text-lg">
                                  £{report.fundingOptimization.five_year_projections.summary.average_5_year_cost_self_funding.toLocaleString()}
                                </div>
                                <div className="text-gray-400 text-xs mt-1">
                                  Avg: £{report.fundingOptimization.five_year_projections.summary.average_annual_cost_self_funding.toLocaleString()}/year
                                </div>
                              </div>
                              <div className="bg-green-50 rounded-lg p-3 border border-green-200">
                                <div className="text-xs text-gray-500 mb-1">Recommended (5yr)</div>
                                <div className="font-semibold text-green-700 text-lg">
                                  £{report.fundingOptimization.five_year_projections.summary.average_5_year_cost_recommended.toLocaleString()}
                                </div>
                                <div className="text-gray-400 text-xs mt-1">
                                  Avg: £{report.fundingOptimization.five_year_projections.summary.average_annual_cost_recommended.toLocaleString()}/year
                                </div>
                              </div>
                            </div>
                            
                            {/* Potential Savings */}
                            {report.fundingOptimization.five_year_projections.summary.potential_5_year_savings > 0 && (
                              <div className="mb-4 p-3 bg-green-50 rounded-lg border border-green-200">
                                <div className="text-xs font-semibold text-green-900 mb-1">Potential Savings</div>
                                <div className="text-sm">
                                  <span className="font-bold text-green-700 text-lg">
                                    £{report.fundingOptimization.five_year_projections.summary.potential_5_year_savings.toLocaleString()}
                                  </span>
                                  <span className="text-gray-600 ml-2">over 5 years</span>
                                </div>
                              </div>
                            )}
                            
                            {/* Charts */}
                            {report.fundingOptimization.five_year_projections.projections && 
                             report.fundingOptimization.five_year_projections.projections.length > 0 && (
                              <div className="mt-4">
                                <FiveYearProjectionsChart 
                                  projections={report.fundingOptimization.five_year_projections.projections} 
                                />
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                        {/* Cost Analysis Section */}
                        {report.careHomes.length > 0 && (
                          <div 
                            id="cost-analysis" 
                            ref={(el) => { sectionRefs.current['cost-analysis'] = el; }}
                            className="scroll-mt-4 mt-6"
                          >
                            <CostAnalysisBlock
                              careHomes={report.careHomes}
                              fundingOptimization={report.fundingOptimization}
                              region="england"
                              careType={
                                questionnaire?.section_3_medical_needs?.q8_care_types?.includes('specialised_dementia') 
                                  ? 'dementia' 
                                  : questionnaire?.section_3_medical_needs?.q8_care_types?.includes('medical_nursing')
                                  ? 'nursing'
                                  : 'residential'
                              }
                            />
                          </div>
                        )}

                        {/* Fair Cost Gap Analysis Section */}
                        {report.fairCostGapAnalysis && (
                          <div 
                            id="fair-cost-gap" 
                            ref={(el) => { sectionRefs.current['fair-cost-gap'] = el; }}
                            className="scroll-mt-4 mt-6"
                          >
                            <div className="p-6 bg-gradient-to-r from-red-50 to-orange-50 rounded-lg border border-red-200">
                              <div className="mb-6">
                                <h3 className="font-semibold text-gray-900 mb-2 flex items-center text-xl">
                                  <AlertCircle className="w-6 h-6 mr-2 text-red-600" />
                                  Fair Cost Gap Analysis
                                </h3>
                                <div className="flex flex-wrap gap-4 text-sm text-gray-600 mt-2">
                                  <div className="flex items-center">
                                    <span className="font-medium mr-1">Local Authority:</span>
                                    <span>{report.fairCostGapAnalysis.local_authority}</span>
                                    {report.fairCostGapAnalysis.region && (
                                      <span className="ml-2 text-gray-500">({report.fairCostGapAnalysis.region})</span>
                                    )}
                                  </div>
                                  <div className="flex items-center">
                                    <span className="font-medium mr-1">Care Type:</span>
                                    <span className="capitalize">{report.fairCostGapAnalysis.care_type.replace(/_/g, ' ')}</span>
                                  </div>
                                </div>
                              </div>

                              {/* MSIF Data & Local Authority Info */}
                              {(report.fairCostGapAnalysis.msif_data || report.fairCostGapAnalysis.local_authority_info) && (
                                <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                                  {report.fairCostGapAnalysis.msif_data && (
                                    <div className="bg-white rounded-lg p-4 shadow-sm border border-blue-200">
                                      <h5 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                                        <Info className="w-4 h-4 text-blue-600" />
                                        MSIF Fair Cost Data
                                      </h5>
                                      <div className="space-y-2 text-sm">
                                        {report.fairCostGapAnalysis.msif_data.fair_cost_weekly !== null && (
                                          <div className="flex justify-between">
                                            <span className="text-gray-600">Fair Cost (Weekly):</span>
                                            <span className="font-semibold text-blue-700">
                                              £{Math.round(report.fairCostGapAnalysis.msif_data.fair_cost_weekly).toLocaleString()}
                                            </span>
                                          </div>
                                        )}
                                        <div className="flex justify-between">
                                          <span className="text-gray-600">Source:</span>
                                          <span className="text-gray-700">{report.fairCostGapAnalysis.msif_data.source}</span>
                                        </div>
                                        <div className="flex justify-between">
                                          <span className="text-gray-600">Year:</span>
                                          <span className="text-gray-700">{report.fairCostGapAnalysis.msif_data.year}</span>
                                        </div>
                                        <div className="flex justify-between">
                                          <span className="text-gray-600">Care Type:</span>
                                          <span className="text-gray-700">{report.fairCostGapAnalysis.msif_data.care_type_display}</span>
                                        </div>
                                        <div className="flex items-center gap-2 mt-2 pt-2 border-t border-gray-200">
                                          {report.fairCostGapAnalysis.msif_data.local_authority_verified ? (
                                            <CheckCircle2 className="w-4 h-4 text-green-600" />
                                          ) : (
                                            <AlertCircle className="w-4 h-4 text-yellow-600" />
                                          )}
                                          <span className={`text-xs ${
                                            report.fairCostGapAnalysis.msif_data.local_authority_verified 
                                              ? 'text-green-700' 
                                              : 'text-yellow-700'
                                          }`}>
                                            {report.fairCostGapAnalysis.msif_data.local_authority_verified 
                                              ? 'Local Authority Verified' 
                                              : 'Local Authority Not Verified'}
                                          </span>
                                        </div>
                                      </div>
                                    </div>
                                  )}

                                  {report.fairCostGapAnalysis.local_authority_info && (
                                    <div className="bg-white rounded-lg p-4 shadow-sm border border-green-200">
                                      <h5 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                                        <Info className="w-4 h-4 text-green-600" />
                                        Local Authority Information
                                      </h5>
                                      <div className="space-y-2 text-sm">
                                        <div>
                                          <span className="text-gray-600">Name:</span>
                                          <span className="font-semibold text-gray-900 ml-2">
                                            {report.fairCostGapAnalysis.local_authority_info.name}
                                          </span>
                                        </div>
                                        {report.fairCostGapAnalysis.local_authority_info.code && (
                                          <div>
                                            <span className="text-gray-600">Code:</span>
                                            <span className="text-gray-700 ml-2">
                                              {report.fairCostGapAnalysis.local_authority_info.code}
                                            </span>
                                          </div>
                                        )}
                                        {report.fairCostGapAnalysis.local_authority_info.region && (
                                          <div>
                                            <span className="text-gray-600">Region:</span>
                                            <span className="text-gray-700 ml-2">
                                              {report.fairCostGapAnalysis.local_authority_info.region}
                                            </span>
                                          </div>
                                        )}
                                        <div className="mt-3 pt-3 border-t border-gray-200">
                                          <p className="text-xs text-gray-600 mb-1">
                                            {report.fairCostGapAnalysis.local_authority_info.contact_note}
                                          </p>
                                          <p className="text-xs text-blue-600 italic">
                                            {report.fairCostGapAnalysis.local_authority_info.website_hint}
                                          </p>
                                        </div>
                                      </div>
                                    </div>
                                  )}
                                </div>
                              )}

                              {/* Why Gap Exists - Enhanced with MSIF Context */}
                              {report.fairCostGapAnalysis.why_gap_exists && (
                                <div className="mb-6 bg-white rounded-lg p-4 shadow-sm border border-orange-200">
                                  <h5 className="text-sm font-semibold text-gray-900 mb-2">
                                    {report.fairCostGapAnalysis.why_gap_exists.title}
                                  </h5>
                                  <p className="text-sm text-gray-700 mb-3">
                                    {report.fairCostGapAnalysis.why_gap_exists.explanation}
                                  </p>
                                  {report.fairCostGapAnalysis.why_gap_exists.msif_context && (
                                    <div className="mb-3 p-3 bg-blue-50 rounded border border-blue-200">
                                      <p className="text-xs text-blue-800">
                                        <span className="font-semibold">MSIF Context:</span>{' '}
                                        {report.fairCostGapAnalysis.why_gap_exists.msif_context}
                                      </p>
                                    </div>
                                  )}
                                  {report.fairCostGapAnalysis.why_gap_exists.market_dynamics && 
                                   report.fairCostGapAnalysis.why_gap_exists.market_dynamics.length > 0 && (
                                    <div>
                                      <div className="text-xs font-semibold text-gray-600 mb-1">Market Dynamics:</div>
                                      <ul className="list-disc list-inside text-xs text-gray-700 space-y-1">
                                        {report.fairCostGapAnalysis.why_gap_exists.market_dynamics.map((dynamic, idx) => (
                                          <li key={idx}>{dynamic}</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                </div>
                              )}

                              {/* Average Gap Summary Cards */}
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                                <div className="bg-white rounded-lg p-4 shadow-sm border border-red-200">
                                  <p className="text-xs text-gray-500 mb-1">Average Weekly Gap</p>
                                  <p className="text-2xl font-bold text-red-600">
                                    £{Math.round(report.fairCostGapAnalysis.average_gap_weekly).toLocaleString()}
                                  </p>
                                  <p className="text-xs text-gray-500 mt-1">
                                    {report.fairCostGapAnalysis.homes.length > 0 && (
                                      <span>
                                        {((report.fairCostGapAnalysis.average_gap_weekly / 
                                          report.fairCostGapAnalysis.homes[0].fair_cost_msif) * 100).toFixed(1)}% above fair cost
                                      </span>
                                    )}
                                  </p>
                                </div>
                                <div className="bg-white rounded-lg p-4 shadow-sm border border-red-200">
                                  <p className="text-xs text-gray-500 mb-1">Average Annual Gap</p>
                                  <p className="text-2xl font-bold text-red-600">
                                    £{Math.round(report.fairCostGapAnalysis.average_gap_annual).toLocaleString()}
                                  </p>
                                  <p className="text-xs text-gray-500 mt-1">Per year overpayment</p>
                                </div>
                                <div className="bg-white rounded-lg p-4 shadow-sm border border-red-200">
                                  <p className="text-xs text-gray-500 mb-1">Average 5-Year Gap</p>
                                  <p className="text-2xl font-bold text-red-600">
                                    £{Math.round(report.fairCostGapAnalysis.average_gap_5year).toLocaleString()}
                                  </p>
                                  <p className="text-xs text-gray-500 mt-1">Total potential overpayment</p>
                                </div>
                              </div>
                      
                              {/* Per-Home Gap Table */}
                              <div className="mb-6">
                                <h4 className="text-sm font-semibold text-gray-900 mb-3">Per-Home Gap Breakdown</h4>
                                <div className="overflow-x-auto bg-white rounded-lg shadow-sm border border-gray-200">
                                  <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-50">
                                      <tr>
                                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Home</th>
                                        <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Their Price/wk</th>
                                        <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Fair Cost (MSIF)/wk</th>
                                        <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Gap/wk</th>
                                        <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Gap %</th>
                                        <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Gap/year</th>
                                        <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Gap/5 years</th>
                                      </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                      {report.fairCostGapAnalysis.homes.map((home, idx) => (
                                        <tr key={home.home_id} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                                          <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">{home.home_name}</td>
                                          <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 text-right">£{Number(home.their_price.toFixed(2)).toLocaleString()}</td>
                                          <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 text-right">£{Number(home.fair_cost_msif.toFixed(2)).toLocaleString()}</td>
                                          <td className="px-4 py-3 whitespace-nowrap text-sm text-red-600 font-semibold text-right">£{Number(home.gap_weekly.toFixed(2)).toLocaleString()}</td>
                                          <td className="px-4 py-3 whitespace-nowrap text-sm text-red-600 font-semibold text-right">
                                            {home.gap_percent ? `${home.gap_percent.toFixed(1)}%` : '—'}
                                          </td>
                                        <td className="px-4 py-3 whitespace-nowrap text-sm text-red-600 text-right">£{Math.round(home.gap_annual).toLocaleString()}</td>
                                        <td className="px-4 py-3 whitespace-nowrap text-sm text-red-600 font-semibold text-right">£{Math.round(home.gap_5year).toLocaleString()}</td>
                                        </tr>
                                      ))}
                                      <tr className="bg-gray-100 font-semibold">
                                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">Average</td>
                                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 text-right">—</td>
                                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 text-right">—</td>
                                        <td className="px-4 py-3 whitespace-nowrap text-sm text-red-600 text-right">£{Number(report.fairCostGapAnalysis.average_gap_weekly.toFixed(2)).toLocaleString()}</td>
                                        <td className="px-4 py-3 whitespace-nowrap text-sm text-red-600 text-right">
                                          {report.fairCostGapAnalysis.homes.length > 0 && (
                                            <span>
                                              {((report.fairCostGapAnalysis.average_gap_weekly / 
                                                report.fairCostGapAnalysis.homes[0].fair_cost_msif) * 100).toFixed(1)}%
                                            </span>
                                          )}
                                        </td>
                                        <td className="px-4 py-3 whitespace-nowrap text-sm text-red-600 text-right">£{Math.round(report.fairCostGapAnalysis.average_gap_annual).toLocaleString()}</td>
                                        <td className="px-4 py-3 whitespace-nowrap text-sm text-red-600 text-right">£{Math.round(report.fairCostGapAnalysis.average_gap_5year).toLocaleString()}</td>
                                      </tr>
                                    </tbody>
                                  </table>
                                </div>
                              </div>

                              {/* Why Gap Exists */}
                              <div className="mb-6 p-4 bg-white rounded-lg border border-red-200 shadow-sm">
                                <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                                  <AlertCircle className="w-5 h-5 mr-2 text-red-600" />
                                  {report.fairCostGapAnalysis.why_gap_exists.title}
                                </h4>
                                <p className="text-sm text-gray-700 mb-4 leading-relaxed">{report.fairCostGapAnalysis.why_gap_exists.explanation}</p>
                                <div className="bg-red-50 rounded-lg p-4 border border-red-100">
                                  <h5 className="text-sm font-semibold text-gray-900 mb-2">Market Dynamics:</h5>
                                  <ul className="list-disc list-inside text-sm text-gray-700 space-y-2">
                                    {report.fairCostGapAnalysis.why_gap_exists.market_dynamics.map((dynamic, idx) => (
                                      <li key={idx} className="leading-relaxed">{dynamic}</li>
                                    ))}
                                  </ul>
                                </div>
                              </div>

                              {/* Strategies to Reduce Gap */}
                              <div className="mb-4">
                                <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                                  <Sparkles className="w-5 h-5 mr-2 text-blue-600" />
                                  Strategies to Reduce Your Gap
                                </h4>
                                <div className="space-y-4">
                                  {report.fairCostGapAnalysis.strategies_to_reduce_gap.map((strategy) => (
                                    <div key={strategy.strategy_number} className="p-5 bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                                      <div className="flex items-start gap-4">
                                        <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-red-100 to-orange-100 rounded-full flex items-center justify-center font-bold text-red-700 text-base shadow-sm">
                                          {strategy.strategy_number}
                                        </div>
                                        <div className="flex-1">
                                          <h5 className="text-lg font-semibold text-gray-900 mb-2">{strategy.title}</h5>
                                          <p className="text-sm text-gray-700 mb-3 leading-relaxed">{strategy.description}</p>
                                          {strategy.potential_savings && (
                                            <div className="inline-flex items-center px-3 py-1.5 bg-green-50 border border-green-200 rounded-lg text-sm font-semibold text-green-700 mb-3">
                                              <DollarSign className="w-4 h-4 mr-1" />
                                              Potential Savings: {strategy.potential_savings}
                                            </div>
                                          )}
                                          <div className="mt-3">
                                            <h6 className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-2">Action Items:</h6>
                                            <ul className="list-disc list-inside text-sm text-gray-600 space-y-1.5">
                                              {strategy.action_items.map((item, idx) => (
                                                <li key={idx} className="leading-relaxed">{item}</li>
                                              ))}
                                            </ul>
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Comparative Analysis Section */}
                        {report.comparativeAnalysis && (
                    <div 
                      id="comparative" 
                      ref={(el) => { sectionRefs.current['comparative'] = el; }}
                      className="scroll-mt-4 mt-6 p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-200"
                    >
                      <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
                        <Sparkles className="w-5 h-5 mr-2 text-indigo-600" />
                        Comparative Analysis
                      </h3>
                      <ComparativeAnalysisTable analysis={report.comparativeAnalysis} />
                    </div>
                  )}

                        {/* Red Flags & Risk Assessment Section */}
                        {report.riskAssessment && (
                    <div 
                      id="risks" 
                      ref={(el) => { sectionRefs.current['risks'] = el; }}
                      className="scroll-mt-4 mt-6 p-4 bg-gradient-to-r from-red-50 to-orange-50 rounded-lg border border-red-200"
                    >
                      <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
                        <AlertCircle className="w-5 h-5 mr-2 text-red-600" />
                        Red Flags & Risk Assessment
                      </h3>
                      <RiskAssessmentViewer assessment={report.riskAssessment} />
                    </div>
                  )}

                        {/* Negotiation Strategy Section */}
                        {report.negotiationStrategy && (
                          <div 
                            id="negotiation" 
                            ref={(el) => { sectionRefs.current['negotiation'] = el; }}
                            className="scroll-mt-4 mt-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200"
                          >
                            <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
                              <DollarSign className="w-5 h-5 mr-2 text-blue-600" />
                              Negotiation Strategy
                            </h3>
                            <NegotiationStrategyViewer strategy={report.negotiationStrategy} />
                          </div>
                        )}

                        {/* Funding Options Section (Page 14) */}
                        <div 
                          id="funding-options" 
                          ref={(el) => { sectionRefs.current['funding-options'] = el; }}
                          className="scroll-mt-4 mt-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200"
                        >
                          <FundingOptionsSection 
                            report={report} 
                            questionnaire={questionnaire || undefined}
                          />
                        </div>

                        {/* 14-Day Action Plan Section (Page 15) */}
                        <div 
                          id="actionplan" 
                          ref={(el) => { sectionRefs.current['actionplan'] = el; }}
                          className="scroll-mt-4 mt-6 p-4 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-lg border border-emerald-200"
                        >
                          <ActionPlanSection report={report} />
                        </div>

                        {/* Next Steps Section */}
                        <div 
                          id="nextsteps" 
                          ref={(el) => { sectionRefs.current['nextsteps'] = el; }}
                          className="scroll-mt-4 mt-6 p-4 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-lg border border-emerald-200"
                        >
                    <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
                      <CheckCircle2 className="w-5 h-5 mr-2 text-emerald-600" />
                      Next Steps
                    </h3>
                    
                    {/* Recommended Actions */}
                    <div className="mb-6">
                      <h4 className="text-lg font-semibold text-gray-900 mb-3">Recommended Actions</h4>
                      {report.nextSteps?.recommendedActions && report.nextSteps.recommendedActions.length > 0 ? (
                        <div className="space-y-3">
                          {report.nextSteps.recommendedActions.map((actionItem, index) => (
                            <div key={index} className="bg-white rounded-lg p-4 border border-emerald-100 shadow-sm">
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-2">
                                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                                      actionItem.priority === 'high' ? 'bg-red-100 text-red-800' :
                                      actionItem.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                      'bg-gray-100 text-gray-800'
                                    }`}>
                                      Home {actionItem.homeRank}
                                    </span>
                                    <span className="font-semibold text-gray-900">{actionItem.homeName}</span>
                                  </div>
                                  <p className="text-sm text-gray-700 mb-1">{actionItem.action}</p>
                                  <div className="flex flex-wrap items-center gap-2 mt-2">
                                    <p className="text-xs text-gray-500">Timeline: {actionItem.timeline}</p>
                                    {actionItem.peakVisitingHours && actionItem.peakVisitingHours.length > 0 && (
                                      <span className="text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                                        Best times: {actionItem.peakVisitingHours.slice(0, 2).join(', ')}
                                      </span>
                                    )}
                                    {actionItem.localAuthority && (
                                      <span className="text-xs text-gray-500">
                                        LA: {actionItem.localAuthority}
                                      </span>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        // Fallback to generated actions if nextSteps not available
                        <div className="space-y-3">
                          {report.careHomes.slice(0, 5).map((home, index) => {
                            const priority: 'high' | 'medium' | 'low' = index === 0 ? 'high' : index === 1 ? 'high' : 'medium';
                            const timeline = index === 0 ? 'Within 7 days' : 'Within 14 days';
                            const action = index === 0
                              ? `Schedule a personal tour of ${home.name}`
                              : index === 1
                              ? `Call ${home.name} to discuss funding options and availability`
                              : `Review contract terms for ${home.name}`;
                            
                            return (
                              <div key={home.id} className="bg-white rounded-lg p-4 border border-emerald-100 shadow-sm">
                                <div className="flex items-start justify-between">
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-2">
                                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                                        priority === 'high' ? 'bg-red-100 text-red-800' :
                                        priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                        'bg-gray-100 text-gray-800'
                                      }`}>
                                        Home {index + 1}
                                      </span>
                                      <span className="font-semibold text-gray-900">{home.name}</span>
                                    </div>
                                    <p className="text-sm text-gray-700 mb-1">{action}</p>
                                    <p className="text-xs text-gray-500">Timeline: {timeline}</p>
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      )}
                      {report.nextSteps?.localAuthority && (
                        <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                          <p className="text-xs text-gray-600">
                            <span className="font-semibold">Local Authority:</span> {report.nextSteps.localAuthority}
                          </p>
                        </div>
                      )}
                    </div>

                    {/* Questions for Home Manager */}
                    <div className="mb-6">
                      <h4 className="text-lg font-semibold text-gray-900 mb-3">Questions for Home Manager</h4>
                      {report.nextSteps?.questionsForHomeManager ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {report.nextSteps.questionsForHomeManager.medicalCare && report.nextSteps.questionsForHomeManager.medicalCare.length > 0 && (
                            <div className="bg-white rounded-lg p-4 border border-emerald-100">
                              <h5 className="font-semibold text-sm text-gray-900 mb-2">Medical Care Provision</h5>
                              <ul className="text-xs text-gray-600 space-y-1">
                                {report.nextSteps.questionsForHomeManager.medicalCare.map((question, idx) => (
                                  <li key={idx}>• {question}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {report.nextSteps.questionsForHomeManager.staffQualifications && report.nextSteps.questionsForHomeManager.staffQualifications.length > 0 && (
                            <div className="bg-white rounded-lg p-4 border border-emerald-100">
                              <h5 className="font-semibold text-sm text-gray-900 mb-2">Staff Qualifications</h5>
                              <ul className="text-xs text-gray-600 space-y-1">
                                {report.nextSteps.questionsForHomeManager.staffQualifications.map((question, idx) => (
                                  <li key={idx}>• {question}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {report.nextSteps.questionsForHomeManager.cqcFeedback && report.nextSteps.questionsForHomeManager.cqcFeedback.length > 0 && (
                            <div className="bg-white rounded-lg p-4 border border-emerald-100">
                              <h5 className="font-semibold text-sm text-gray-900 mb-2">Recent CQC Feedback</h5>
                              <ul className="text-xs text-gray-600 space-y-1">
                                {report.nextSteps.questionsForHomeManager.cqcFeedback.map((question, idx) => (
                                  <li key={idx}>• {question}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {report.nextSteps.questionsForHomeManager.financialStability && report.nextSteps.questionsForHomeManager.financialStability.length > 0 && (
                            <div className="bg-white rounded-lg p-4 border border-emerald-100">
                              <h5 className="font-semibold text-sm text-gray-900 mb-2">Financial Stability</h5>
                              <ul className="text-xs text-gray-600 space-y-1">
                                {report.nextSteps.questionsForHomeManager.financialStability.map((question, idx) => (
                                  <li key={idx}>• {question}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {report.nextSteps.questionsForHomeManager.trialPeriod && report.nextSteps.questionsForHomeManager.trialPeriod.length > 0 && (
                            <div className="bg-white rounded-lg p-4 border border-emerald-100">
                              <h5 className="font-semibold text-sm text-gray-900 mb-2">Trial Period Availability</h5>
                              <ul className="text-xs text-gray-600 space-y-1">
                                {report.nextSteps.questionsForHomeManager.trialPeriod.map((question, idx) => (
                                  <li key={idx}>• {question}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {report.nextSteps.questionsForHomeManager.cancellationTerms && report.nextSteps.questionsForHomeManager.cancellationTerms.length > 0 && (
                            <div className="bg-white rounded-lg p-4 border border-emerald-100">
                              <h5 className="font-semibold text-sm text-gray-900 mb-2">Cancellation Terms</h5>
                              <ul className="text-xs text-gray-600 space-y-1">
                                {report.nextSteps.questionsForHomeManager.cancellationTerms.map((question, idx) => (
                                  <li key={idx}>• {question}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      ) : (
                        // Fallback to default questions
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="bg-white rounded-lg p-4 border border-emerald-100">
                            <h5 className="font-semibold text-sm text-gray-900 mb-2">Medical Care Provision</h5>
                            <ul className="text-xs text-gray-600 space-y-1">
                              <li>• How do you manage {report.clientNeeds?.medicalConditions?.[0] || 'specific medical conditions'}?</li>
                              <li>• What medical equipment is available on-site?</li>
                              <li>• How quickly can you respond to medical emergencies?</li>
                            </ul>
                          </div>
                          <div className="bg-white rounded-lg p-4 border border-emerald-100">
                            <h5 className="font-semibold text-sm text-gray-900 mb-2">Staff Qualifications</h5>
                            <ul className="text-xs text-gray-600 space-y-1">
                              <li>• What qualifications do your care staff hold?</li>
                              <li>• How many registered nurses are on duty?</li>
                              <li>• What is your staff-to-resident ratio?</li>
                            </ul>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Premium Upgrade Offer */}
                    <div className="bg-gradient-to-r from-[#1E2A44] to-[#2D3E5F] rounded-lg p-6 text-white">
                      <h4 className="text-xl font-bold mb-2">Upgrade to PREMIUM for £249</h4>
                      <p className="text-sm text-gray-200 mb-4">
                        Get ongoing monitoring and real-time alerts for your chosen care home
                      </p>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                        <div className="flex items-start gap-2">
                          <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                          <div>
                            <div className="font-semibold text-sm">7-Week Monitoring</div>
                            <div className="text-xs text-gray-300">Weekly updates on care home status</div>
                          </div>
                        </div>
                        <div className="flex items-start gap-2">
                          <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                          <div>
                            <div className="font-semibold text-sm">Real-Time Alert System</div>
                            <div className="text-xs text-gray-300">Immediate notifications of critical changes</div>
                          </div>
                        </div>
                        <div className="flex items-start gap-2">
                          <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                          <div>
                            <div className="font-semibold text-sm">Deep Research Updates</div>
                            <div className="text-xs text-gray-300">Weekly deep research per home</div>
                          </div>
                        </div>
                        <div className="flex items-start gap-2">
                          <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                          <div>
                            <div className="font-semibold text-sm">Post-Placement Support</div>
                            <div className="text-xs text-gray-300">4-hour response time for concerns</div>
                          </div>
                        </div>
                      </div>
                      <button className="w-full bg-white text-[#1E2A44] font-semibold py-3 px-6 rounded-lg hover:bg-gray-100 transition-colors">
                        Upgrade to PREMIUM
                      </button>
                    </div>
                  </div>

                        {/* LLM Insights Section */}
                        {report.llmInsights && (
                          <div 
                            id="llm-insights" 
                            ref={(el) => { sectionRefs.current['llm-insights'] = el; }}
                            className="scroll-mt-4 mt-6"
                          >
                            <LLMInsightsSection insights={report.llmInsights} />
                          </div>
                        )}

                        {/* Appendix Section (Section 23) */}
                        {report.appendix && (
                          <div 
                            id="appendix" 
                            ref={(el) => { sectionRefs.current['appendix'] = el; }}
                            className="scroll-mt-4 mt-6 p-4 bg-gradient-to-r from-gray-50 to-slate-50 rounded-lg border border-gray-200"
                          >
                            <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
                              <Database className="w-5 h-5 mr-2 text-gray-600" />
                              Appendix: Data Sources & Metadata
                            </h3>
                            <AppendixSection report={report} />
                          </div>
                        )}

                        {/* Generate New Report Button */}
                        <div className="text-center pt-4">
                    <p className="text-sm text-gray-500 mb-4">
                      Full report with detailed analysis, financial stability assessment, and staff quality metrics will be available here.
                    </p>
                    <button
                      onClick={() => {
                        setReport(null);
                        setQuestionnaire(null);
                        setSelectedFile(undefined);
                      }}
                      className="text-sm text-[#1E2A44] hover:underline"
                    >
                      Generate New Report
                    </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : null}
      </div>
    </div>
  );
}

