import { useState, useEffect } from 'react';
import { FileText, Sparkles, AlertCircle, RefreshCw, Building2, BarChart3, Target, Info, User, DollarSign, CheckCircle2, ChevronDown, ChevronUp, Search, Database, TrendingUp, AlertTriangle } from 'lucide-react';
import QuestionLoader from '../professional-report/components/QuestionLoader';
import ExecutiveSummaryDashboard from '../professional-report/components/ExecutiveSummaryDashboard';
import ExecutiveSummarySection from '../professional-report/components/ExecutiveSummarySection';
import PrioritiesMatchSection from '../professional-report/components/PrioritiesMatchSection';
import QuestionnaireProfile from '../professional-report/components/QuestionnaireProfile';
import { ProfessionalReportGuide } from '../professional-report/components/ProfessionalReportGuide';
import CommunityReputationSection from '../professional-report/components/CommunityReputationSection';
import MedicalCareSection from '../professional-report/components/MedicalCareSection';
import SafetyAnalysisSection from '../professional-report/components/SafetyAnalysisSection';
import LocationWellbeingSection from '../professional-report/components/LocationWellbeingSection';
import AreaMapSection from '../professional-report/components/AreaMapSection';
import MatchScoreRadarChart from '../professional-report/components/MatchScoreRadarChart';
import StaffQualitySection from '../professional-report/components/StaffQualitySection';
import NeighbourhoodSection from '../professional-report/components/NeighbourhoodSection';
import LLMInsightsSection from '../professional-report/components/LLMInsightsSection';
import AppendixSection from '../professional-report/components/AppendixSection';
import { CostAnalysisBlock } from '../cost-analysis';

// Charts and specific views
import CQCRatingTrendChart from '../professional-report/components/CQCRatingTrendChart';
import FinancialStabilityChart from '../professional-report/components/FinancialStabilityChart';

// New sections for full parity
import FundingOptionsSection from '../professional-report/components/FundingOptionsSection';
import ActionPlanSection from '../professional-report/components/ActionPlanSection';
import RiskAssessmentViewer from '../professional-report/components/RiskAssessmentViewer';
import NegotiationStrategyViewer from '../professional-report/components/NegotiationStrategyViewer';
import ComparativeAnalysisTable from '../professional-report/components/ComparativeAnalysisTable';

import { useProfessionalReportNew } from './hooks/useProfessionalReportNew';
import type { ProfessionalQuestionnaireResponse, ProfessionalReportData } from './types';

export default function ProfessionalReportNewViewer() {
  const [questionnaire, setQuestionnaire] = useState<ProfessionalQuestionnaireResponse | null>(null);
  const [report, setReport] = useState<ProfessionalReportData | null>(null);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [loadingStep, setLoadingStep] = useState<string>('Initializing...');
  const [activeTab, setActiveTab] = useState<'report' | 'profile' | 'guide'>('profile');
  const [activeSection, setActiveSection] = useState<string>('summary');
  const [selectedFile, setSelectedFile] = useState<string>('');
  const [expandedHomes, setExpandedHomes] = useState<Set<string>>(new Set());

  // ✅ FIX: Real progress tracking instead of simulation
  const handleProgress = (progress: number, step: string) => {
    setLoadingProgress(progress);
    setLoadingStep(step);
    console.log(`📊 Progress: ${progress}% - ${step}`);
  };

  const generateReport = useProfessionalReportNew(handleProgress);

  // ✅ FIX: Update progress based on actual generation state
  useEffect(() => {
    if (generateReport.isPending) {
      // Progress is now updated via callback, but set initial state
      if (loadingProgress === 0) {
        setLoadingProgress(5); // Initial state
      }
    } else if (report) {
      setLoadingProgress(100);
      setTimeout(() => setLoadingProgress(0), 1000);
    } else if (generateReport.isError) {
      // Keep progress at current state on error
      // Don't reset immediately to show where it failed
    }
  }, [generateReport.isPending, generateReport.isError, report, loadingProgress]);

  const handleLoadQuestionnaire = (data: ProfessionalQuestionnaireResponse) => {
    setQuestionnaire(data);
    setReport(null);
  };

  const handleGenerateReport = () => {
    if (!questionnaire) return;

    generateReport.mutate(questionnaire, {
      onSuccess: (data) => {
        setReport(data);
        setActiveTab('report');
      },
      onError: (error) => {
        console.error('Failed to generate report:', error);
      },
    });
  };

  const handleRetry = () => {
    if (questionnaire) {
      setLoadingProgress(0);
      handleGenerateReport();
    }
  };

  // Helper for FSA rating label
  const getFSARatingLabel = (rating: number | null | undefined) => {
    if (rating === null || rating === undefined) return 'N/A';
    if (rating >= 5) return 'Very Good';
    if (rating >= 4) return 'Good';
    if (rating >= 3) return 'Generally Satisfactory';
    if (rating >= 2) return 'Improvement Necessary';
    if (rating >= 1) return 'Major Improvement Necessary';
    return 'Urgent Improvement Necessary';
  };

  return (
    <div className="bg-gray-50/50">
      {/* Tab Navigation */}
      {(questionnaire || report || generateReport.isPending) && (
        <div className="sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-gray-200 shadow-sm">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex items-center justify-between h-16">
              <div className="flex gap-8 h-full">
                {[
                  { id: 'report', label: 'Professional Report', icon: FileText, disabled: !report },
                  { id: 'profile', label: 'User Profile', icon: User, disabled: false },
                  { id: 'guide', label: 'User Guide', icon: Info, disabled: false }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => !tab.disabled && setActiveTab(tab.id as any)}
                    disabled={tab.disabled}
                    className={`flex items-center gap-2 px-1 border-b-2 transition-all duration-200 ${activeTab === tab.id
                      ? 'border-[#1E2A44] text-[#1E2A44] font-bold'
                      : tab.disabled
                        ? 'border-transparent text-gray-300 cursor-not-allowed'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                  >
                    <tab.icon className={`w-4 h-4 ${activeTab === tab.id ? 'text-[#1E2A44]' : ''}`} />
                    <span className="text-sm">{tab.label}</span>
                  </button>
                ))}
              </div>
              {report && (
                <div className="flex items-center gap-2 px-3 py-1 bg-indigo-50 rounded-full border border-indigo-100">
                  <Sparkles className="w-3 h-3 text-indigo-600" />
                  <span className="text-[10px] font-bold text-indigo-700 uppercase tracking-wider">Data Engine V2</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Loading / Progress State */}
        {generateReport.isPending && (
          <div className="max-w-3xl mx-auto mb-12">
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 text-center">
              <div className="mb-6 relative inline-block">
                <div className="w-20 h-20 border-4 border-indigo-50 rounded-full"></div>
                <div className="w-20 h-20 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin absolute top-0 left-0"></div>
                <div className="absolute inset-0 flex items-center justify-center font-bold text-indigo-600">
                  {Math.round(loadingProgress)}%
                </div>
              </div>
              <h3 className="text-xl font-bold text-[#1E2A44] mb-2">Synchronizing with RCH Data Engine...</h3>
              <p className="text-gray-500 text-sm mb-6">
                {/* ✅ FIX: Show real progress step */}
                {loadingStep || 'Analyzing 15+ real-time medical and financial sources for 156-point matching.'}
              </p>
              <div className="w-full bg-gray-100 rounded-full h-3 mb-2 overflow-hidden">
                <div
                  className="bg-indigo-600 h-full transition-all duration-300 ease-out shadow-[0_0_10px_rgba(79,70,229,0.5)]"
                  style={{ width: `${loadingProgress}%` }}
                ></div>
              </div>
            </div>
          </div>
        )}

        {/* Error State */}
        {generateReport.isError && (
          <div className="max-w-3xl mx-auto mb-12">
            <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-8 flex items-start shadow-lg">
              <AlertCircle className="w-8 h-8 text-red-600 mr-4 flex-shrink-0 mt-1" />
              <div>
                <h3 className="text-xl font-bold text-red-800 mb-2">Analysis Engine Error</h3>
                <p className="text-red-700 mb-6">{generateReport.error.message}</p>
                <button
                  onClick={handleRetry}
                  className="inline-flex items-center px-6 py-3 bg-red-600 text-white font-bold rounded-xl hover:bg-red-700 transition-all shadow-md active:scale-95"
                >
                  <RefreshCw className="w-4 h-4 mr-2" /> Retry Analysis
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Initial Profile Selection */}
        {!report && !generateReport.isPending && activeTab === 'profile' && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-[2rem] shadow-2xl p-8 md:p-12 border border-blue-50 relative overflow-hidden">
              <div className="absolute top-0 right-0 p-12 opacity-5">
                <FileText className="w-64 h-64" />
              </div>
              <div className="relative z-10">
                <div className="flex items-center gap-3 mb-8">
                  <div className="w-12 h-12 bg-indigo-100 rounded-2xl flex items-center justify-center">
                    <User className="w-6 h-6 text-indigo-600" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-[#1E2A44]">Load Client Profile</h2>
                    <p className="text-gray-500 text-sm">Select a diagnostic questionnaire to begin analysis</p>
                  </div>
                </div>
                <QuestionLoader
                  onLoad={handleLoadQuestionnaire}
                  selectedFile={selectedFile}
                  onFileSelect={setSelectedFile}
                />
                {questionnaire && (
                  <div className="mt-12 pt-8 border-t border-gray-100 flex flex-col items-center">
                    <button
                      onClick={handleGenerateReport}
                      className="group relative px-12 py-5 bg-[#1E2A44] text-white rounded-[1.5rem] font-black text-lg shadow-2xl hover:shadow-[0_20px_50px_rgba(30,42,68,0.3)] transition-all hover:-translate-y-1 active:scale-95 overflow-hidden"
                    >
                      <div className="absolute inset-0 bg-gradient-to-r from-indigo-600 to-blue-600 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                      <span className="relative flex items-center gap-3">
                        <Sparkles className="w-6 h-6" />
                        RUN ENGINE ANALYSIS
                      </span>
                    </button>
                    <p className="mt-4 text-xs text-gray-400 font-medium uppercase tracking-widest flex items-center gap-2">
                      <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                      Ready for 156-point matching
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tab Content - Profile and Guide (shown during loading or when report is ready) */}
        {activeTab === 'profile' && questionnaire && report ? (
          <div className="max-w-7xl mx-auto">
            <QuestionnaireProfile questionnaire={questionnaire!} />
          </div>
        ) : activeTab === 'guide' ? (
          <div className="max-w-7xl mx-auto">
            <ProfessionalReportGuide />
          </div>
        ) : null}

        {/* Main Report View */}
        {report && activeTab === 'report' && (
          <div className="animate-fade-in">
            {/* Internal Report Section Sub-Navigation */}
            <div className="flex flex-wrap items-center gap-2 mb-8 bg-gray-100/50 p-1.5 rounded-2xl border border-gray-200/50 w-fit max-w-full">
              {[
                { id: 'summary', label: 'Summary', icon: BarChart3 },
                { id: 'priorities', label: 'Priorities', icon: Target },
                { id: 'homes', label: 'Top Homes', icon: Building2 },
                { id: 'analysis', label: 'Analysis', icon: Search },
                { id: 'risks', label: 'Risks', icon: AlertCircle },
                { id: 'funding', label: 'Funding', icon: DollarSign },
                { id: 'negotiation', label: 'Strategy', icon: FileText },
                { id: 'actionplan', label: 'Action Plan', icon: CheckCircle2 }
              ].map((section) => (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-sm transition-all duration-200 ${activeSection === section.id
                    ? 'bg-white text-[#1E2A44] shadow-md shadow-gray-200/50 scale-[1.02]'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-white/50'
                    }`}
                >
                  <section.icon className="w-4 h-4" />
                  {section.label}
                </button>
              ))}
            </div>

            {/* Active Section Content */}
            <div className="bg-white rounded-[2.5rem] p-8 md:p-12 shadow-xl border border-gray-100 min-h-[600px]">
              <div className="max-w-5xl mx-auto">
                {activeSection === 'summary' && (
                  <div className="animate-fade-in space-y-12">
                    <ExecutiveSummarySection report={report} />
                    <ExecutiveSummaryDashboard report={report} />
                  </div>
                )}

                {activeSection === 'priorities' && (
                  <div className="animate-fade-in space-y-6">
                    <PrioritiesMatchSection report={report!} questionnaire={questionnaire!} />
                  </div>
                )}

                {activeSection === 'homes' && (
                  <div className="animate-fade-in space-y-12">
                    <div className="flex items-center justify-between mb-8">
                      <h3 className="text-2xl font-bold text-gray-900">Deep-Dive Intelligence Analysis</h3>
                      <button
                        onClick={() => {
                          const allExpanded = expandedHomes.size === Math.min(report!.careHomes.length, 5);
                          if (allExpanded) {
                            setExpandedHomes(new Set());
                          } else {
                            setExpandedHomes(new Set(report!.careHomes.slice(0, 5).map(h => h.id)));
                          }
                        }}
                        className="text-xs text-blue-600 hover:text-blue-700 font-bold flex items-center gap-1 bg-blue-50 px-3 py-1.5 rounded-full border border-blue-100 transition-colors"
                      >
                        {expandedHomes.size === Math.min(report!.careHomes.length, 5) ? (
                          <><ChevronUp className="w-3 h-3" /> Collapse All</>
                        ) : (
                          <><ChevronDown className="w-3 h-3" /> Expand All</>
                        )}
                      </button>
                    </div>

                    <div className="space-y-6">
                      {report!.careHomes.slice(0, 5).map((home, index) => (
                        <div key={home.id} className="bg-white rounded-3xl border border-gray-200 shadow-sm overflow-hidden hover:border-indigo-100 transition-all">
                          <div
                            className={`p-6 flex items-center justify-between cursor-pointer hover:bg-gray-50/50 transition-colors ${expandedHomes.has(home.id) ? 'bg-indigo-50/30' : ''}`}
                            onClick={() => {
                              const next = new Set(expandedHomes);
                              if (next.has(home.id)) next.delete(home.id);
                              else next.add(home.id);
                              setExpandedHomes(next);
                            }}
                          >
                            <div className="flex items-center gap-6">
                              <div className="w-12 h-12 bg-[#1E2A44] rounded-2xl flex items-center justify-center text-white font-black text-xl shadow-lg">
                                {index + 1}
                              </div>
                              <div>
                                <h4 className="text-xl font-bold text-[#1E2A44] mb-1">{home.name}</h4>
                                <p className="text-sm text-gray-500 font-medium">{home.location}</p>
                              </div>
                            </div>
                            <div className="flex items-center gap-8">
                              <div className="text-right">
                                <span className="text-3xl font-black text-indigo-600 leading-none">{home.matchScore}%</span>
                                <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mt-1">Match Grade</p>
                              </div>
                              {expandedHomes.has(home.id) ? <ChevronUp className="w-6 h-6 text-gray-400" /> : <ChevronDown className="w-6 h-6 text-gray-400" />}
                            </div>
                          </div>

                          {expandedHomes.has(home.id) && (
                            <div className="p-8 border-t border-gray-100 animate-slide-down space-y-12">
                              {/* LLM Insights - Why This Home Was Recommended */}
                              {report.llmInsights?.insights?.top_home_analysis && (() => {
                                const homeInsight = report.llmInsights.insights.top_home_analysis.find(
                                  (insight) => insight.home_name === home.name || insight.rank === index + 1
                                );
                                if (homeInsight) {
                                  return (
                                    <div className="bg-gradient-to-r from-green-50/50 to-emerald-50/50 rounded-2xl p-6 border border-green-200 shadow-sm">
                                      <h5 className="font-bold text-gray-900 mb-3 flex items-center gap-2 text-lg">
                                        <Target className="w-5 h-5 text-green-600" />
                                        Why This Home Was Recommended
                                      </h5>
                                      <p className="text-gray-700 mb-4 leading-relaxed text-base">{homeInsight.why_recommended}</p>
                                      
                                      {homeInsight.match_score_explanation && (
                                        <p className="text-sm text-gray-600 italic mb-4 border-l-3 border-green-400 pl-3">
                                          {homeInsight.match_score_explanation}
                                        </p>
                                      )}
                                      
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
                                }
                                return null;
                              })()}

                              {/* ✅ FIX: Indicate partial data if enrichment incomplete */}
                              {(!home.cqcDeepDive || !home.fsaDetailed || !home.financialStability) && (
                                <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-4">
                                  <div className="flex items-start gap-3">
                                    <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                                    <div className="flex-1">
                                      <p className="text-sm font-semibold text-yellow-800 mb-1">Partial Data Available</p>
                                      <p className="text-xs text-yellow-700">
                                        Some enrichment data could not be loaded for this home. 
                                        {!home.cqcDeepDive && ' CQC data missing. '}
                                        {!home.fsaDetailed && ' FSA data missing. '}
                                        {!home.financialStability && ' Financial data missing.'}
                                        The report may be incomplete.
                                      </p>
                                    </div>
                                  </div>
                                </div>
                              )}
                              
                              {/* Integrated Section: FSA Rating */}
                              <div className="bg-gray-50 rounded-2xl p-6 border border-gray-100">
                                <div className="flex flex-col md:flex-row gap-8 items-center">
                                  <div className="flex-shrink-0">
                                    <div className="flex items-center gap-4">
                                      <span className="text-5xl font-bold text-[#1E2A44]">{home.fsaDetailed?.rating || 'N/A'}</span>
                                      <div>
                                        <p className="font-bold">Rating: {getFSARatingLabel(home.fsaDetailed?.rating)}</p>
                                        <p className="text-xs text-gray-500 italic">Official Food Standards Agency Data</p>
                                      </div>
                                    </div>
                                  </div>
                                  <div className="flex-1 text-sm text-gray-600 leading-relaxed border-l border-gray-200 pl-8">
                                    <p>{home.fsaDetailed?.breakdown_scores?.hygiene_label ? `Hygiene: ${home.fsaDetailed.breakdown_scores.hygiene_label}. ` : ''}
                                      {home.fsaDetailed?.breakdown_scores?.structural_label ? `Structural: ${home.fsaDetailed.breakdown_scores.structural_label}. ` : ''}
                                      {home.fsaDetailed?.breakdown_scores?.confidence_label ? `Management: ${home.fsaDetailed.breakdown_scores.confidence_label}.` : ''}</p>
                                  </div>
                                </div>
                              </div>

                              <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                                <div className="space-y-8">
                                  <MatchScoreRadarChart home={home} />
                                  <div className="pt-8 border-t border-gray-100">
                                    <CQCRatingTrendChart cqcData={home.cqcDeepDive!} homeName={home.name} />
                                  </div>
                                </div>
                                <div className="space-y-8">
                                  <FinancialStabilityChart financialData={home.financialStability!} homeName={home.name} />
                                  <div className="pt-8 border-t border-gray-100">
                                    <StaffQualitySection staffQuality={home.staffQuality} homeName={home.name} />
                                  </div>
                                </div>
                              </div>

                              <NeighbourhoodSection neighbourhood={home.neighbourhood} homeName={home.name} />
                              {home.communityReputation && <CommunityReputationSection home={home} />}
                              {home.medicalCare && <MedicalCareSection home={home} />}
                              {home.safetyAnalysis && <SafetyAnalysisSection home={home} />}
                              {home.locationWellbeing && <LocationWellbeingSection home={home} />}
                              {home.areaMap && <AreaMapSection home={home} />}
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
                    <ActionPlanSection report={report!} />

                    {report.llmInsights && (
                      <div className="pt-8 border-t border-gray-100">
                        <LLMInsightsSection insights={report.llmInsights!} />
                      </div>
                    )}

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
                  <AppendixSection report={report!} />
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
