/**
 * Professional Report Guide Component
 * Explains each section of the Professional Report and its benefits
 */
import { 
  Home, 
  Building2, 
  DollarSign, 
  BarChart3, 
  AlertTriangle,
  CheckCircle2, 
  ArrowRight,
  Info,
  Target,
  TrendingUp,
  Shield,
  FileText,
  Award,
  Sparkles,
  Zap
} from 'lucide-react';

interface ProfessionalReportGuideProps {
  className?: string;
}

export function ProfessionalReportGuide({ className = '' }: ProfessionalReportGuideProps) {
  const sections = [
    {
      id: 'summary',
      icon: <Home className="w-5 h-5" />,
      title: 'Executive Summary',
      description: 'High-level overview of your personalized matching analysis',
      whatItShows: [
        '156-point matching algorithm results',
        'Personalized matching explanation',
        'Precision matching details',
        'Deep analysis summary',
        'Expert insights'
      ],
      benefits: [
        'Quick understanding of the analysis approach',
        'See how your profile influenced matching',
        'Understand the depth of analysis performed',
        'Get confidence in the recommendations'
      ],
      color: 'blue'
    },
    {
      id: 'homes',
      icon: <Building2 className="w-5 h-5" />,
      title: 'Top 5 Recommended Care Homes',
      description: 'Comprehensive analysis of 5 best-matched care homes',
      whatItShows: [
        '5 carefully selected homes with detailed profiles',
        'Match scores with 8-factor breakdown (radar charts)',
        'FSA detailed ratings (3 sub-scores)',
        'Financial stability analysis (Altman Z-score, bankruptcy risk)',
        'Google Places insights (dwell time, repeat visitors, footfall)',
        'CQC deep dive (historical ratings, trends, action plans)',
        'Staff quality research (Glassdoor, LinkedIn, job boards)',
        'Photos and contact information'
      ],
      benefits: [
        'Get 5 pre-screened homes (vs 3 in Free Report)',
        'See detailed financial stability scores',
        'Understand staff quality and turnover',
        'View behavioral insights from Google Places',
        'Access comprehensive CQC history and trends',
        'Make informed decisions with complete data'
      ],
      color: 'green'
    },
    {
      id: 'funding',
      icon: <DollarSign className="w-5 h-5" />,
      title: 'Funding Optimization',
      description: 'Exact calculations for all government funding options',
      whatItShows: [
        'CHC eligibility: 12-domain detailed assessment with exact probability',
        'LA funding: Full means test breakdown with exact savings',
        'DPA considerations: Property assessment, deferral limits, cost projections',
        'Estimated funding outcomes for each scenario',
        '5-year cost projections with inflation for all funding types'
      ],
      benefits: [
        'Know your exact CHC eligibility (not ranges)',
        'Get personalized application templates',
        'See exact savings calculations (£50k-£130k+ per year)',
        'Plan long-term with 5-year projections',
        'Understand all funding options clearly'
      ],
      color: 'green'
    },
    {
      id: 'fair-cost-gap',
      icon: <AlertTriangle className="w-5 h-5" />,
      title: 'Fair Cost Gap Analysis',
      description: 'Per-home breakdown of overpayment vs government fair cost',
      whatItShows: [
        'Per-home gap breakdown (weekly, annual, 5-year)',
        'Average gap across all recommended homes',
        'Why the gap exists (systemic market issue)',
        '4 strategies to reduce the gap with potential savings'
      ],
      benefits: [
        'See exactly how much you may overpay per home',
        'Understand the systemic market gap',
        'Get actionable strategies to reduce costs',
        'Use MSIF data for negotiation leverage'
      ],
      color: 'red'
    },
    {
      id: 'comparative',
      icon: <BarChart3 className="w-5 h-5" />,
      title: 'Comparative Analysis',
      description: 'Side-by-side comparison of all 5 homes',
      whatItShows: [
        'Comprehensive comparison table with all metrics',
        'Match score rankings',
        'Price comparison and value analysis',
        'Key differentiators for each home',
        'Overall recommendation'
      ],
      benefits: [
        'Compare all 5 homes in one place',
        'Identify best value quickly',
        'See unique selling points for each home',
        'Make data-driven decisions',
        'Understand trade-offs between options'
      ],
      color: 'indigo'
    },
    {
      id: 'risks',
      icon: <Shield className="w-5 h-5" />,
      title: 'Risk Assessment',
      description: 'Comprehensive risk analysis for each care home',
      whatItShows: [
        'Financial stability warnings (Altman Z-score, bankruptcy risk)',
        'CQC compliance issues (ratings, trends, action plans)',
        'Staff turnover concerns (Glassdoor, LinkedIn, job boards)',
        'Pricing increases history',
        'Overall risk score and level for each home'
      ],
      benefits: [
        'Identify homes at financial risk',
        'Avoid homes with compliance issues',
        'Understand staff stability',
        'See pricing trends',
        'Make safer decisions'
      ],
      color: 'purple'
    },
    {
      id: 'negotiation',
      icon: <FileText className="w-5 h-5" />,
      title: 'Negotiation Strategy',
      description: 'Ready-to-use templates and strategies for negotiation',
      whatItShows: [
        'Market-rate analysis with Autumna pricing data',
        'Discount negotiation points with potential savings',
        'Contract review checklist (key terms and red flags)',
        'Email templates (inquiry, negotiation, clarification)',
        'Questions to ask at visit (organized by category)'
      ],
      benefits: [
        'Negotiate from a position of knowledge',
        'Use ready-made email templates',
        'Know what to look for in contracts',
        'Ask the right questions during visits',
        'Save £20k-£40k+ per year through negotiation'
      ],
      color: 'orange'
    }
  ];

  const getColorClasses = (color: string) => {
    const colors: Record<string, { bg: string; border: string; text: string; icon: string }> = {
      blue: {
        bg: 'bg-blue-50',
        border: 'border-blue-200',
        text: 'text-blue-700',
        icon: 'text-blue-600'
      },
      green: {
        bg: 'bg-green-50',
        border: 'border-green-200',
        text: 'text-green-700',
        icon: 'text-green-600'
      },
      red: {
        bg: 'bg-red-50',
        border: 'border-red-200',
        text: 'text-red-700',
        icon: 'text-red-600'
      },
      indigo: {
        bg: 'bg-indigo-50',
        border: 'border-indigo-200',
        text: 'text-indigo-700',
        icon: 'text-indigo-600'
      },
      purple: {
        bg: 'bg-purple-50',
        border: 'border-purple-200',
        text: 'text-purple-700',
        icon: 'text-purple-600'
      },
      orange: {
        bg: 'bg-orange-50',
        border: 'border-orange-200',
        text: 'text-orange-700',
        icon: 'text-orange-600'
      }
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-[#1E2A44] to-[#2D3E5F] rounded-xl shadow-xl text-white p-6 md:p-8">
        <div className="flex items-center gap-3 mb-4">
          <Info className="w-8 h-8 md:w-10 md:h-10" />
          <h2 className="text-2xl md:text-3xl font-bold">Professional Report Guide</h2>
        </div>
        <p className="text-lg text-gray-200">
          Understand each section of your comprehensive 30-35 page professional report
        </p>
      </div>

      {/* Introduction */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
        <div className="flex items-start gap-4">
          <Target className="w-6 h-6 text-[#10B981] flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">How This Report Helps You</h3>
            <p className="text-gray-700 mb-4">
              This professional report provides comprehensive analysis using a 156-point matching algorithm 
              across 15+ data sources. Each section is designed to give you complete confidence in your care home decision.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
              <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                  <span className="font-semibold text-green-900">Save Money</span>
                </div>
                <p className="text-sm text-green-700">
                  Potential savings of £50k-£130k+ per year through funding and negotiation
                </p>
              </div>
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <div className="flex items-center gap-2 mb-2">
                  <Shield className="w-5 h-5 text-blue-600" />
                  <span className="font-semibold text-blue-900">Make Safe Choices</span>
                </div>
                <p className="text-sm text-blue-700">
                  Comprehensive risk assessment and financial stability analysis
                </p>
              </div>
              <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                <div className="flex items-center gap-2 mb-2">
                  <Award className="w-5 h-5 text-purple-600" />
                  <span className="font-semibold text-purple-900">Expert Analysis</span>
                </div>
                <p className="text-sm text-purple-700">
                  156-point algorithm with 15+ data sources and behavioral insights
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Sections Guide */}
      <div className="space-y-6">
        {sections.map((section, index) => {
          const colors = getColorClasses(section.color);
          return (
            <div
              key={section.id}
              className={`bg-white rounded-xl shadow-lg border-2 ${colors.border} overflow-hidden`}
            >
              {/* Section Header */}
              <div className={`${colors.bg} p-4 md:p-6 border-b ${colors.border}`}>
                <div className="flex items-center gap-3 mb-2">
                  <div className={`${colors.icon} flex-shrink-0`}>
                    {section.icon}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-gray-500">Section {index + 1}</span>
                      <span className="text-gray-400">•</span>
                      <h3 className={`text-xl md:text-2xl font-bold ${colors.text}`}>
                        {section.title}
                      </h3>
                    </div>
                    <p className="text-gray-600 mt-1">{section.description}</p>
                  </div>
                </div>
              </div>

              {/* Section Content */}
              <div className="p-4 md:p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* What It Shows */}
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <FileText className="w-5 h-5 text-gray-600" />
                      <h4 className="font-semibold text-gray-900">What It Shows</h4>
                    </div>
                    <ul className="space-y-2">
                      {section.whatItShows.map((item, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                          <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Benefits */}
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <Target className="w-5 h-5 text-[#10B981]" />
                      <h4 className="font-semibold text-gray-900">Benefits for You</h4>
                    </div>
                    <ul className="space-y-2">
                      {section.benefits.map((benefit, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                          <ArrowRight className="w-4 h-4 text-[#10B981] flex-shrink-0 mt-0.5" />
                          <span>{benefit}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Key Differentiators */}
      <div className="bg-gradient-to-br from-purple-50 via-indigo-50 to-blue-50 rounded-xl border-2 border-purple-200 p-6 md:p-8">
        <div className="flex items-center gap-3 mb-4">
          <Zap className="w-6 h-6 md:w-8 md:h-8 text-purple-600" />
          <h3 className="text-2xl md:text-3xl font-bold text-gray-900">What Makes This Report Unique</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white rounded-lg p-5 border border-purple-200 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="w-5 h-5 text-purple-600" />
              <h4 className="font-bold text-gray-900">156-Point Matching Algorithm</h4>
            </div>
            <p className="text-sm text-gray-700">
              Dynamic weights adjust based on your specific needs. High fall risk? Safety scores get priority. 
              Low budget? Financial factors weigh more heavily.
            </p>
          </div>
          
          <div className="bg-white rounded-lg p-5 border border-purple-200 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="w-5 h-5 text-purple-600" />
              <h4 className="font-bold text-gray-900">15+ Data Sources</h4>
            </div>
            <p className="text-sm text-gray-700">
              CQC, FSA, Companies House, Google Places NEW API, Glassdoor, LinkedIn, Job Boards, 
              Autumna pricing, and proprietary analysis combined for comprehensive insights.
            </p>
          </div>
          
          <div className="bg-white rounded-lg p-5 border border-purple-200 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <DollarSign className="w-5 h-5 text-purple-600" />
              <h4 className="font-bold text-gray-900">Exact Funding Calculations</h4>
            </div>
            <p className="text-sm text-gray-700">
              Not ranges - exact CHC probability with 12-domain breakdown, full means test, 
              and personalized application templates ready to use.
            </p>
          </div>
          
          <div className="bg-white rounded-lg p-5 border border-purple-200 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <Shield className="w-5 h-5 text-purple-600" />
              <h4 className="font-bold text-gray-900">Risk Detection</h4>
            </div>
            <p className="text-sm text-gray-700">
              Financial stability scores (Altman Z-score), staff turnover analysis, CQC compliance tracking, 
              and pricing trend monitoring to avoid costly mistakes.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

