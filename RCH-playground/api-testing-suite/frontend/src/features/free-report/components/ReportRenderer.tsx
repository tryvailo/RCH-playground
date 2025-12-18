import { useState, useEffect } from 'react';
import { 
  MapPin, 
  AlertTriangle, 
  CheckCircle2, 
  ArrowRight, 
  Star,
  Shield,
  DollarSign,
  Navigation,
  Award,
  Phone,
  Globe,
  Download,
  Info,
  FileText,
  Settings
} from 'lucide-react';
import { pdf } from '@react-pdf/renderer';
import FreeReportPDF from './FreeReportPDF';
import { FairCostGapBlock } from '../../fair-cost-gap/components/FairCostGapBlock';
import { FundingEligibilityBlock } from './FundingEligibilityBlock';
import { AreaProfileBlock } from './AreaProfileBlock';
import { AreaMapBlock } from './AreaMapBlock';
import { ReportGuide } from './ReportGuide';
import ScoringSettings from './ScoringSettings';
import FreeReportLLMInsights from './FreeReportLLMInsights';
import type { FreeReportData, CareHomeData, QuestionnaireResponse } from '../types';

interface ReportRendererProps {
  report: FreeReportData;
  questionnaire?: QuestionnaireResponse;
}

// Animated Counter Component
function AnimatedCounter({ value, duration = 2000 }: { value: number; duration?: number }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTime: number;
    const startValue = 0;
    const endValue = value;

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);
      
      // Easing function (ease-out)
      const easeOut = 1 - Math.pow(1 - progress, 3);
      setCount(Math.floor(startValue + (endValue - startValue) * easeOut));

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        setCount(endValue);
      }
    };

    requestAnimationFrame(animate);
  }, [value, duration]);

  return <span>{count.toLocaleString()}</span>;
}

const getFSAColorClass = (color: string) => {
  switch (color) {
    case 'green':
      return 'bg-[#10B981]';
    case 'yellow':
      return 'bg-yellow-500';
    case 'red':
      return 'bg-[#EF4444]';
    default:
      return 'bg-gray-400';
  }
};

const getMatchTypeColor = (matchType: string) => {
  switch (matchType) {
    case 'Safe Bet':
      return 'bg-blue-100 text-blue-800 border-blue-200';
    case 'Best Value':
      return 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]/20';
    case 'Premium':
      return 'bg-purple-100 text-purple-800 border-purple-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

const getRatingColor = (rating?: string) => {
  switch (rating?.toLowerCase()) {
    case 'outstanding':
      return 'text-[#10B981]';
    case 'good':
      return 'text-blue-600';
    case 'requires improvement':
      return 'text-yellow-600';
    case 'inadequate':
      return 'text-[#EF4444]';
    default:
      return 'text-gray-600';
  }
};

// Care Home Card Component
function CareHomeCard({ home, index }: { home: CareHomeData; index: number }) {
  const avgPrice = (home.price_range.min + home.price_range.max) / 2;
  const whyText = home.why_this_home || `This home is selected as ${home.match_type} based on quality, value, and location.`;

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200 hover:shadow-xl transition-all duration-300">
      {/* Photo */}
      <div className="relative h-56 bg-gradient-to-br from-gray-200 to-gray-300 overflow-hidden">
        {home.photo ? (
          <img
            src={home.photo}
            alt={home.name}
            className="w-full h-full object-cover"
            onError={(e) => {
              // If image fails to load, show placeholder
              const target = e.target as HTMLImageElement;
              target.style.display = 'none';
              const placeholder = target.parentElement?.querySelector('.photo-placeholder') as HTMLElement;
              if (placeholder) {
                placeholder.style.display = 'flex';
              }
            }}
          />
        ) : null}
        <div className={`w-full h-full flex items-center justify-center text-gray-400 ${home.photo ? 'photo-placeholder hidden' : ''}`}>
          <Award className="w-16 h-16" />
        </div>
        {/* Band Badge */}
        <div className="absolute top-4 right-4">
          <div className="bg-white/90 backdrop-blur-sm rounded-full px-3 py-1 shadow-md">
            <span className="text-sm font-bold text-[#1E2A44]">Band {home.band}/5</span>
          </div>
        </div>
        {/* Match Type Badge */}
        <div className="absolute top-4 left-4">
          <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold border ${getMatchTypeColor(home.match_type)}`}>
            {home.match_type}
          </span>
        </div>
      </div>

      <div className="p-6">
        {/* Header */}
        <div className="mb-4">
          <h3 className="text-2xl font-bold text-gray-900 mb-2">{home.name}</h3>
          {home.address && (
            <div className="flex items-start text-gray-600 text-sm">
              <MapPin className="w-4 h-4 mr-1 mt-0.5 flex-shrink-0" />
              <span>{home.address}{home.city && `, ${home.city}`}</span>
            </div>
          )}
        </div>

        {/* Price Range */}
        <div className="mb-4 pb-4 border-b border-gray-200">
          <div className="flex items-baseline justify-between">
            <div>
              <p className="text-sm text-gray-500 mb-1">Weekly Cost</p>
              <p className="text-3xl font-bold text-[#1E2A44]">£{avgPrice.toLocaleString()}</p>
            </div>
            {home.fsa_color && (
              <div 
                className={`w-5 h-5 rounded-full ${getFSAColorClass(home.fsa_color)}`} 
                title={`FSA Rating: ${home.fsa_rating != null ? `${home.fsa_rating}/5` : home.fsa_color || 'N/A'}`}
              />
            )}
          </div>
          <p className="text-xs text-gray-500 mt-1">
            £{home.price_range.min.toLocaleString()} - £{home.price_range.max.toLocaleString()}/week
          </p>
        </div>

        {/* Why This Home */}
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center">
            <Star className="w-4 h-4 mr-1 text-[#10B981]" />
            Why This Home
          </h4>
          <p className="text-sm text-gray-700 leading-relaxed">{whyText}</p>
        </div>

        {/* Quick Details */}
        <div className="space-y-2 text-sm">
          <div className="flex justify-between items-center">
            <span className="text-gray-600 flex items-center">
              <Navigation className="w-4 h-4 mr-1" />
              Distance
            </span>
            <span className="font-medium text-gray-900">{home.distance.toFixed(1)} km</span>
          </div>
          {home.rating && (
            <div className="flex justify-between items-center">
              <span className="text-gray-600 flex items-center">
                <Shield className="w-4 h-4 mr-1" />
                CQC Rating
              </span>
              <span className={`font-medium ${getRatingColor(home.rating)}`}>{home.rating}</span>
            </div>
          )}
          {home.fsa_color && (
            <div className="flex justify-between items-center">
              <span className="text-gray-600 flex items-center">
                <div className={`w-3 h-3 rounded-full mr-1 ${getFSAColorClass(home.fsa_color)}`} />
                FSA Rating
              </span>
              <div className="flex flex-col items-end gap-1">
                <div className="flex items-center gap-2">
                  {home.fsa_rating != null && (
                    <span className="font-medium text-gray-900">
                      {typeof home.fsa_rating === 'number' ? `${home.fsa_rating}/5` : home.fsa_rating}
                    </span>
                  )}
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium capitalize ${
                    home.fsa_color === 'green' ? 'bg-green-100 text-green-800' :
                    home.fsa_color === 'yellow' ? 'bg-yellow-100 text-yellow-800' :
                    home.fsa_color === 'red' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {home.fsa_color}
                  </span>
                </div>
                {(home as any).fsa_rating_date && (
                  <span className="text-xs text-gray-500">
                    Inspected: {new Date((home as any).fsa_rating_date).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
          )}
          <div className="flex justify-between items-center">
            <span className="text-gray-600 flex items-center">
              <DollarSign className="w-4 h-4 mr-1" />
              Value Score
            </span>
            <span className="font-medium text-gray-900">
              {home.match_type === 'Best Value' ? 'High' : home.match_type === 'Premium' ? 'Premium' : 'Good'}
            </span>
          </div>
        </div>

        {/* Key Features */}
        {home.features && home.features.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-semibold text-gray-900 mb-2">Key Features</h4>
            <div className="flex flex-wrap gap-2">
              {home.features.slice(0, 6).map((feature, idx) => (
                <span key={idx} className="px-2 py-1 bg-gray-100 rounded text-xs text-gray-700">
                  {feature}
                </span>
              ))}
              {home.features.length > 6 && (
                <span className="px-2 py-1 bg-gray-100 rounded text-xs text-gray-500">
                  +{home.features.length - 6} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Contact */}
        {(home.contact_phone || home.website) && (
          <div className="mt-4 pt-4 border-t border-gray-200 flex gap-3">
            {home.contact_phone && (
              <a
                href={`tel:${home.contact_phone}`}
                className="flex-1 flex items-center justify-center px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-md text-sm text-gray-700 transition-colors"
              >
                <Phone className="w-4 h-4 mr-1" />
                Call
              </a>
            )}
            {home.website && (
              <a
                href={home.website}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 flex items-center justify-center px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-md text-sm text-gray-700 transition-colors"
              >
                <Globe className="w-4 h-4 mr-1" />
                Website
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  );
}


// Comparison Table Component
function ComparisonTable({ homes }: { homes: CareHomeData[] }) {
  const criteria = [
    {
      name: 'Weekly Cost',
      home1: `£${((homes[0]?.price_range.min + homes[0]?.price_range.max) / 2).toLocaleString()}`,
      home2: `£${((homes[1]?.price_range.min + homes[1]?.price_range.max) / 2).toLocaleString()}`,
      home3: `£${((homes[2]?.price_range.min + homes[2]?.price_range.max) / 2).toLocaleString()}`,
    },
    {
      name: 'Price Band',
      home1: `${homes[0]?.band}/5`,
      home2: `${homes[1]?.band}/5`,
      home3: `${homes[2]?.band}/5`,
    },
    {
      name: 'Distance',
      home1: `${homes[0]?.distance.toFixed(1)} km`,
      home2: `${homes[1]?.distance.toFixed(1)} km`,
      home3: `${homes[2]?.distance.toFixed(1)} km`,
    },
    {
      name: 'FSA Rating',
      home1: homes[0]?.fsa_rating != null 
        ? `${homes[0].fsa_rating}/5 (${homes[0].fsa_color || 'N/A'})` 
        : homes[0]?.fsa_color || 'N/A',
      home2: homes[1]?.fsa_rating != null 
        ? `${homes[1].fsa_rating}/5 (${homes[1].fsa_color || 'N/A'})` 
        : homes[1]?.fsa_color || 'N/A',
      home3: homes[2]?.fsa_rating != null 
        ? `${homes[2].fsa_rating}/5 (${homes[2].fsa_color || 'N/A'})` 
        : homes[2]?.fsa_color || 'N/A',
    },
    {
      name: 'CQC Rating',
      home1: homes[0]?.rating || 'N/A',
      home2: homes[1]?.rating || 'N/A',
      home3: homes[2]?.rating || 'N/A',
    },
    {
      name: 'Match Type',
      home1: homes[0]?.match_type || 'N/A',
      home2: homes[1]?.match_type || 'N/A',
      home3: homes[2]?.match_type || 'N/A',
    },
  ];

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
        <h3 className="text-xl font-bold text-gray-900">Comparison Table</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Criterion</th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">{homes[0]?.name}</th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">{homes[1]?.name}</th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">{homes[2]?.name}</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {criteria.map((criterion, idx) => (
              <tr key={idx} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{criterion.name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 text-center">{criterion.home1}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 text-center">{criterion.home2}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 text-center">{criterion.home3}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function ReportRenderer({ report, questionnaire }: ReportRendererProps) {
  const { homes, fairCostGap, chcTeaserPercent } = report;
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  const [activeTab, setActiveTab] = useState<'report' | 'scoring-settings' | 'guide'>('report');

  // Calculate government coverage range (32k-82k per year)
  const govCoverageMin = 32000;
  const govCoverageMax = 82000;

  const handleDownloadPDF = async () => {
    setIsGeneratingPDF(true);
    try {
      const blob = await pdf(
        <FreeReportPDF data={report} questionnaire={questionnaire} />
      ).toBlob();

      // Create download link
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `RightCareHome-Report-${questionnaire?.postcode || 'report'}-${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Error generating PDF. Please try again.');
    } finally {
      setIsGeneratingPDF(false);
    }
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Tabs Navigation */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('report')}
              className={`flex-1 py-4 px-6 text-center font-semibold text-sm md:text-base transition-colors border-b-2 ${
                activeTab === 'report'
                  ? 'border-[#1E2A44] text-[#1E2A44] bg-blue-50'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-center gap-2">
                <FileText className="w-4 h-4 md:w-5 md:h-5" />
                <span>Report</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('scoring-settings')}
              className={`flex-1 py-4 px-6 text-center font-semibold text-sm md:text-base transition-colors border-b-2 ${
                activeTab === 'scoring-settings'
                  ? 'border-[#1E2A44] text-[#1E2A44] bg-blue-50'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-center gap-2">
                <Settings className="w-4 h-4 md:w-5 md:h-5" />
                <span>Scoring Settings</span>
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

      {/* Tab Content */}
      {activeTab === 'report' ? (
        <>
          {/* PDF Download Button */}
          <div className="flex justify-end mb-6">
            <button
              onClick={handleDownloadPDF}
              disabled={isGeneratingPDF}
              className={`inline-flex items-center px-4 py-2 md:px-6 md:py-3 rounded-lg font-semibold text-white transition-all shadow-lg text-sm md:text-base ${
                isGeneratingPDF
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-[#1E2A44] hover:bg-[#2D3E5F] hover:scale-105'
              }`}
            >
              <Download className={`w-4 h-4 md:w-5 md:h-5 mr-2 ${isGeneratingPDF ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline">{isGeneratingPDF ? 'Generating PDF...' : 'Download PDF Report'}</span>
              <span className="sm:hidden">{isGeneratingPDF ? 'PDF...' : 'PDF'}</span>
            </button>
          </div>

          {/* Section 1: Header + Personal Summary */}
      <div className="bg-gradient-to-r from-[#1E2A44] to-[#2D3E5F] rounded-xl shadow-xl text-white p-8">
        <h1 className="text-4xl font-bold mb-6">Your Personal Report</h1>
        {questionnaire && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <p className="text-sm text-gray-300 mb-1">Postcode</p>
              <p className="text-2xl font-bold">{questionnaire.postcode}</p>
            </div>
            {questionnaire.care_type && (
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                <p className="text-sm text-gray-300 mb-1">Care Type</p>
                <p className="text-2xl font-bold capitalize">{questionnaire.care_type}</p>
              </div>
            )}
            {questionnaire.budget && (
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                <p className="text-sm text-gray-300 mb-1">Budget</p>
                <p className="text-2xl font-bold">£{questionnaire.budget.toLocaleString()}/week</p>
              </div>
            )}
          </div>
        )}
        {chcTeaserPercent > 0 && (
          <div className="mt-6 bg-[#10B981]/20 backdrop-blur-sm rounded-lg p-4 border border-[#10B981]/30">
            <p className="text-sm text-gray-200 mb-1">CHC Probability</p>
            <p className="text-3xl font-bold text-[#10B981]">{chcTeaserPercent.toFixed(1)}%</p>
          </div>
        )}

        {/* Client Preferences Section */}
        {questionnaire && (
          <div className="mt-6 bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
            <h3 className="text-xl font-semibold mb-4 text-white">Your Preferences</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Priority Order & Weights */}
              {questionnaire.priority_order && questionnaire.priority_weights && (
                <div className="bg-white/5 rounded-lg p-4">
                  <p className="text-sm text-gray-300 mb-2">Priority Order</p>
                  <div className="space-y-2">
                    {questionnaire.priority_order.map((priority, idx) => {
                      const weight = questionnaire.priority_weights?.[idx] || 0;
                      const priorityLabels: Record<string, string> = {
                        quality: 'Quality',
                        cost: 'Cost',
                        proximity: 'Proximity'
                      };
                      return (
                        <div key={idx} className="flex items-center justify-between">
                          <span className="text-white capitalize">
                            {priorityLabels[priority] || priority}
                          </span>
                          <span className="text-[#10B981] font-semibold">{weight}%</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Timeline */}
              {questionnaire.timeline && (
                <div className="bg-white/5 rounded-lg p-4">
                  <p className="text-sm text-gray-300 mb-1">Timeline</p>
                  <p className="text-white font-semibold capitalize">
                    {questionnaire.timeline.replace(/_/g, ' ')}
                  </p>
                </div>
              )}

              {/* Max Distance */}
              {questionnaire.max_distance_km && (
                <div className="bg-white/5 rounded-lg p-4">
                  <p className="text-sm text-gray-300 mb-1">Max Distance</p>
                  <p className="text-white font-semibold">{questionnaire.max_distance_km} km</p>
                </div>
              )}

              {/* Funding Type */}
              {questionnaire.funding_type && (
                <div className="bg-white/5 rounded-lg p-4">
                  <p className="text-sm text-gray-300 mb-1">Funding Type</p>
                  <p className="text-white font-semibold capitalize">
                    {questionnaire.funding_type.replace(/_/g, ' ')}
                  </p>
                </div>
              )}

              {/* Duration Type */}
              {questionnaire.duration_type && (
                <div className="bg-white/5 rounded-lg p-4">
                  <p className="text-sm text-gray-300 mb-1">Duration</p>
                  <p className="text-white font-semibold capitalize">
                    {questionnaire.duration_type.replace(/_/g, ' ')}
                  </p>
                </div>
              )}

              {/* Medical Conditions */}
              {questionnaire.medical_conditions && questionnaire.medical_conditions.length > 0 && (
                <div className="bg-white/5 rounded-lg p-4">
                  <p className="text-sm text-gray-300 mb-2">Medical Conditions</p>
                  <div className="flex flex-wrap gap-2">
                    {questionnaire.medical_conditions.map((condition, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-[#10B981]/20 text-[#10B981] rounded text-sm capitalize"
                      >
                        {condition.replace(/_/g, ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Additional Preferences */}
            {questionnaire.preferences && Object.keys(questionnaire.preferences).length > 0 && (
              <div className="mt-4 bg-white/5 rounded-lg p-4">
                <p className="text-sm text-gray-300 mb-3">Additional Preferences</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {Object.entries(questionnaire.preferences).map(([key, value]) => {
                    if (value === false || value === null || value === '') return null;
                    const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    return (
                      <div key={key} className="flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-[#10B981]" />
                        <span className="text-white text-sm">
                          {label}: {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Sections 2-4: 3 Care Home Cards */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900 mb-6">Recommended Care Homes</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {homes.map((home, idx) => (
            <CareHomeCard key={idx} home={home} index={idx} />
          ))}
        </div>
      </div>

      {/* Section 5: Fair Cost Gap - Large Red Block */}
      {questionnaire && report.fairCostGap && (() => {
        // Use Fair Cost Gap data from backend if available
        const fcg = report.fairCostGap;
        
        // If we have backend data, use it directly
        if (fcg && fcg.weekly > 0 && fcg.annual > 0) {
          const msifLower = (fcg as any).msifLower || 700;
          const marketPrice = fcg.weekly + msifLower;
          
          return (
            <div className="bg-gradient-to-br from-[#EF4444] via-red-600 to-[#DC2626] rounded-2xl shadow-2xl p-6 md:p-8 lg:p-12 text-white relative overflow-hidden">
              {/* Background Pattern */}
              <div className="absolute inset-0 opacity-10">
                <div
                  className="absolute inset-0"
                  style={{
                    backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
                    backgroundSize: '40px 40px',
                  }}
                ></div>
              </div>

              <div className="relative z-10">
                {/* Header */}
                <div className="flex items-center mb-4 md:mb-6">
                  <AlertTriangle className="w-6 h-6 md:w-8 md:h-8 mr-2 md:mr-3 flex-shrink-0" />
                  <h2 className="text-2xl md:text-4xl lg:text-5xl font-bold">
                    YOUR CARE HOME COST ANALYSIS
                  </h2>
                </div>

                {/* Market Average and Government Fair Cost */}
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 md:p-6 mb-4 border border-white/20">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm md:text-base text-gray-200 mb-1">Market Average (your area):</p>
                      <p className="text-xl md:text-2xl lg:text-3xl font-bold">
                        £{Math.round(marketPrice).toLocaleString()}/week
                      </p>
                    </div>
                    <div>
                      <p className="text-sm md:text-base text-gray-200 mb-1">Government Fair Cost:</p>
                      <p className="text-xl md:text-2xl lg:text-3xl font-bold">
                        £{Math.round(msifLower).toLocaleString()}/week
                      </p>
                    </div>
                  </div>
                </div>

                {/* YOUR OVERPAYMENT */}
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 md:p-8 mb-6 border-2 border-white/30">
                  <p className="text-base md:text-lg text-gray-200 mb-2 text-center">
                    🔴 YOUR OVERPAYMENT:
                  </p>
                  <p className="text-4xl md:text-6xl lg:text-7xl font-bold mb-4 leading-tight text-center">
                    £{Math.round(fcg.weekly).toLocaleString()}/week
                  </p>
                  
                  {/* Cost Impact */}
                  <div className="mt-4 pt-4 border-t border-white/20">
                    <p className="text-base md:text-lg font-semibold mb-2 text-center">Cost Impact:</p>
                    <div className="flex flex-col md:flex-row items-center justify-center gap-3 md:gap-4 text-lg md:text-xl font-semibold">
                      <span>• Per year: £{Math.round(fcg.annual).toLocaleString()}</span>
                      <span className="text-white/70 hidden md:inline">|</span>
                      <span>• Over 5 years: £{Math.round(fcg.fiveYear).toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                {/* Professional Report CTA Text */}
                <div className="mb-6">
                  <p className="text-base md:text-lg text-gray-200 text-center">
                    💡 Professional Report shows how to reduce this gap with negotiation strategies and funding options
                  </p>
                </div>

                {/* CTA Button */}
                <button
                  onClick={() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })}
                  className="w-full bg-[#10B981] hover:bg-[#059669] text-white font-bold py-4 md:py-5 px-6 md:px-8 rounded-xl text-lg md:text-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-[1.02] flex items-center justify-center gap-2"
                >
                  <span>Learn how to close this gap → Professional £119</span>
                  <ArrowRight className="w-5 h-5 md:w-6 md:h-6" />
                </button>
              </div>
            </div>
          );
        }
        
        // Fallback to FairCostGapBlock component if data not available
        const avgMarketPrice = homes.length > 0
          ? homes.reduce((sum, h) => sum + (h.price_range.min + h.price_range.max) / 2, 0) / homes.length
          : questionnaire.budget || 1000;
        
        const mapCareType = (ct?: string): 'residential' | 'nursing' | 'residential_dementia' | 'nursing_dementia' => {
          if (!ct) return 'residential';
          if (ct === 'dementia') return 'residential_dementia';
          if (ct === 'nursing') return 'nursing';
          return 'residential';
        };
        
        const localAuthority = questionnaire.city || 'Birmingham';
        
        return (
          <FairCostGapBlock
            marketPrice={avgMarketPrice}
            localAuthority={localAuthority}
            careType={mapCareType(questionnaire.care_type)}
            onUpgradeClick={() => {
              window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            }}
          />
        );
      })()}

      {/* Section 6: Funding Eligibility - Green Block */}
      {report.fundingEligibility && (
        <FundingEligibilityBlock
          fundingEligibility={report.fundingEligibility}
          onUpgradeClick={() => {
            // Scroll to CTA or trigger upgrade modal
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
          }}
        />
      )}

      {/* Section 7: Area Profile - Local Area Context */}
      {report.areaProfile && (
        <AreaProfileBlock areaProfile={report.areaProfile} />
      )}

      {/* Section 8: Area Map - Geographic Visualization */}
      {report.areaMap && (
        <AreaMapBlock mapData={report.areaMap} />
      )}

      {/* Section 9: Comparison Table */}
      <ComparisonTable homes={homes} />

      {/* Section 10: LLM Insights */}
      {report.llmInsights && (
        <FreeReportLLMInsights llmInsights={report.llmInsights} />
      )}

      {/* Section 11: Checklist + Next Steps */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
        <h3 className="text-2xl font-bold text-gray-900 mb-6">Checklist and Next Steps</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
              <CheckCircle2 className="w-5 h-5 mr-2 text-[#10B981]" />
              What to Do Now
            </h4>
            <ul className="space-y-3">
              <li className="flex items-start">
                <CheckCircle2 className="w-5 h-5 text-[#10B981] mr-2 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700">Check eligibility for CHC funding</span>
              </li>
              <li className="flex items-start">
                <CheckCircle2 className="w-5 h-5 text-[#10B981] mr-2 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700">Contact recommended homes</span>
              </li>
              <li className="flex items-start">
                <CheckCircle2 className="w-5 h-5 text-[#10B981] mr-2 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700">Request detailed pricing information</span>
              </li>
              <li className="flex items-start">
                <CheckCircle2 className="w-5 h-5 text-[#10B981] mr-2 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700">Organize visits to top 3 homes</span>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
              <ArrowRight className="w-5 h-5 mr-2 text-[#1E2A44]" />
              Next Steps
            </h4>
            <ul className="space-y-3">
              <li className="flex items-start">
                <span className="w-5 h-5 text-[#1E2A44] mr-2 mt-0.5 flex-shrink-0 font-bold">1.</span>
                <span className="text-gray-700">Apply for CHC assessment</span>
              </li>
              <li className="flex items-start">
                <span className="w-5 h-5 text-[#1E2A44] mr-2 mt-0.5 flex-shrink-0 font-bold">2.</span>
                <span className="text-gray-700">Compare offers from different homes</span>
              </li>
              <li className="flex items-start">
                <span className="w-5 h-5 text-[#1E2A44] mr-2 mt-0.5 flex-shrink-0 font-bold">3.</span>
                <span className="text-gray-700">Discuss funding with local authority</span>
              </li>
              <li className="flex items-start">
                <span className="w-5 h-5 text-[#1E2A44] mr-2 mt-0.5 flex-shrink-0 font-bold">4.</span>
                <span className="text-gray-700">Make a decision based on complete information</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Section 8: CTA Block */}
      <div className="bg-gradient-to-r from-[#10B981] to-[#059669] rounded-xl shadow-xl p-8 md:p-12 text-white text-center">
        <h3 className="text-3xl md:text-4xl font-bold mb-4">Save £50k+?</h3>
        <p className="text-xl mb-8 text-green-50">Get professional analysis and personal recommendations</p>
        <button className="bg-white text-[#10B981] px-8 py-4 rounded-lg text-lg font-bold hover:bg-gray-100 transition-colors shadow-lg flex items-center mx-auto">
          Professional £119
          <ArrowRight className="w-5 h-5 ml-2" />
        </button>
        <p className="text-sm text-green-50 mt-4">Includes deep analysis of all homes and funding strategy</p>
      </div>

        </>
      ) : activeTab === 'scoring-settings' ? (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Scoring Settings</h2>
            <p className="text-gray-600 mb-6">
              Customize how care homes are scored and ranked. Adjust the weights for different factors 
              and set thresholds for location, budget, and review ratings.
            </p>
            <ScoringSettings />
          </div>
        </div>
      ) : (
        <ReportGuide />
      )}
    </div>
  );
}
