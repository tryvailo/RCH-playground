/**
 * Report Guide Component
 * Explains each section of the Free Report and its benefits for the client
 */
import { 
  Home, 
  Building2, 
  AlertTriangle, 
  DollarSign, 
  BarChart3, 
  CheckCircle2, 
  ArrowRight,
  Info,
  Target,
  TrendingUp,
  Shield,
  FileText,
  Sparkles,
  Zap,
  Award
} from 'lucide-react';

interface ReportGuideProps {
  className?: string;
}

export function ReportGuide({ className = '' }: ReportGuideProps) {
  const sections = [
    {
      id: 'header',
      icon: <Home className="w-5 h-5" />,
      title: 'Personal Summary',
      description: 'Overview of your care requirements and location',
      whatItShows: [
        'Your postcode and preferred location',
        'Care type needed (residential, nursing, dementia)',
        'Budget range',
        'CHC funding probability (if available)'
      ],
      benefits: [
        'Quick understanding of your situation at a glance',
        'Confirms your requirements are correctly captured',
        'Sets context for all recommendations'
      ],
      color: 'blue'
    },
      {
      id: 'homes',
      icon: <Building2 className="w-5 h-5" />,
      title: 'Top 3 Recommended Care Homes',
      description: 'Best-matched care homes based on your needs',
      whatItShows: [
        '3 carefully selected homes (Safe Bet, Best Value, Premium)',
        'Match scores and why each home was chosen',
        'Key features: CQC ratings, FSA food hygiene, distance, pricing',
        'Photos and contact information',
        'Detailed profiles with strengths and considerations'
      ],
      benefits: [
        'Save 20+ hours of research time',
        'Get homes pre-screened for quality and safety',
        'Understand why each home matches your needs',
        'Compare options side-by-side',
        'Make informed decisions faster'
      ],
      proTip: 'Professional Report includes 5 homes (vs 3) with deep-dive analysis: financial stability scores, staff turnover rates, Google Places insights (dwell time, repeat visitor patterns), and comprehensive risk assessments.',
      color: 'green'
    },
      {
      id: 'fair-cost-gap',
      icon: <AlertTriangle className="w-5 h-5" />,
      title: 'Fair Cost Gap Analysis',
      description: 'Reveals how much you may be overpaying',
      whatItShows: [
        'Market average price in your area',
        'Government fair cost (MSIF 2025-2026)',
        'Your weekly/annual/5-year overpayment',
        'Percentage above fair cost'
      ],
      benefits: [
        'Discover potential overpayment (£550-£864/week average)',
        'Understand the systemic market gap',
        'See long-term financial impact (5-year projections)',
        'Get motivation to negotiate or seek funding',
        'Save £28k-£45k per year if gap is closed'
      ],
      proTip: 'Professional Report provides per-home gap breakdown, negotiation templates with exact talking points, and strategies to reduce the gap using MSIF data. Plus: Autumna pricing integration for real-time market rates.',
      color: 'red'
    },
      {
      id: 'funding',
      icon: <DollarSign className="w-5 h-5" />,
      title: 'Government Funding Eligibility',
      description: 'Estimates your potential for government funding',
      whatItShows: [
        'NHS CHC probability range (e.g., 68-87%)',
        'Council funding probability',
        'Deferred Payment Agreement (DPA) eligibility',
        'Potential savings ranges for each funding type'
      ],
      benefits: [
        'Discover if you may qualify for £78k-£130k/year in CHC funding',
        'Understand LA funding options (£20k-£50k/year potential)',
        'Learn about DPA for cash flow relief',
        'Get motivated to apply for funding',
        'Save £50k-£100k+ per year if eligible'
      ],
      proTip: 'Professional Report provides exact calculations (not ranges): detailed 12-domain CHC assessment with severity scores, full means test breakdown, personalized application templates, and 5-year cost projections for all funding scenarios. This is the difference between "maybe 68-87%" and knowing exactly what to apply for.',
      color: 'green'
    },
      {
      id: 'comparison',
      icon: <BarChart3 className="w-5 h-5" />,
      title: 'Comparison Table',
      description: 'Side-by-side comparison of all 3 homes',
      whatItShows: [
        'Key metrics: price, distance, CQC rating, FSA rating',
        'Match types and scores',
        'Features and care types offered',
        'Quick visual comparison'
      ],
      benefits: [
        'Compare all options in one place',
        'Identify best value quickly',
        'See trade-offs between homes',
        'Make data-driven decisions',
        'Save time on manual comparison'
      ],
      proTip: 'Professional Report includes 5 homes with advanced metrics: financial stability (Altman Z-score), staff quality research (Glassdoor, LinkedIn, job boards), Google Places behavioral insights, and comprehensive risk assessments. Plus: key differentiators highlighting what makes each home unique.',
      color: 'indigo'
    },
    {
      id: 'checklist',
      icon: <CheckCircle2 className="w-5 h-5" />,
      title: 'Checklist & Next Steps',
      description: 'Action plan to move forward',
      whatItShows: [
        'What to do now (immediate actions)',
        'Next steps (short-term actions)',
        'Prioritized task list',
        'Key deadlines and considerations'
      ],
      benefits: [
        'Clear action plan to follow',
        'Don\'t miss important steps',
        'Prioritize your time effectively',
        'Stay organized during decision-making',
        'Reduce stress with structured guidance'
      ],
      color: 'purple'
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
          <h2 className="text-2xl md:text-3xl font-bold">Report Guide</h2>
        </div>
        <p className="text-lg text-gray-200">
          Understand each section of your report and how it helps you make the best care home decision
        </p>
      </div>

      {/* Introduction */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
        <div className="flex items-start gap-4">
          <Target className="w-6 h-6 text-[#10B981] flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">How This Report Helps You</h3>
            <p className="text-gray-700 mb-4">
              This free report provides essential insights to help you find the right care home. Each section 
              is designed to save you time, money, and stress while ensuring you make an informed decision.
            </p>
            
            {/* Subtle Professional Report Mention */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200 mb-4">
              <div className="flex items-start gap-3">
                <Sparkles className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-semibold text-blue-900 mb-1">
                    Looking for more precision?
                  </p>
                  <p className="text-sm text-blue-800">
                    Throughout this guide, you'll see <span className="font-semibold">Pro Tips</span> highlighting 
                    how Professional Report provides exact calculations, deeper analysis, and actionable strategies 
                    that could save you £50k-£130k+ per year.
                  </p>
                </div>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
              <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                  <span className="font-semibold text-green-900">Save Time</span>
                </div>
                <p className="text-sm text-green-700">
                  20+ hours of research condensed into one report
                </p>
              </div>
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign className="w-5 h-5 text-blue-600" />
                  <span className="font-semibold text-blue-900">Save Money</span>
                </div>
                <p className="text-sm text-blue-700">
                  Potential savings of £50k-£100k+ per year
                </p>
              </div>
              <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                <div className="flex items-center gap-2 mb-2">
                  <Shield className="w-5 h-5 text-purple-600" />
                  <span className="font-semibold text-purple-900">Make Safe Choices</span>
                </div>
                <p className="text-sm text-purple-700">
                  Pre-screened homes with verified quality data
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

                {/* Pro Tip - Subtle Upsell */}
                {section.proTip && (
                  <div className="mt-6 pt-6 border-t border-gray-200">
                    <div className="bg-gradient-to-r from-amber-50 to-yellow-50 rounded-lg p-4 border border-amber-200">
                      <div className="flex items-start gap-3">
                        <Sparkles className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-xs font-semibold text-amber-800 bg-amber-100 px-2 py-0.5 rounded">PRO TIP</span>
                            <span className="text-sm font-semibold text-amber-900">Want More Detail?</span>
                          </div>
                          <p className="text-sm text-amber-800 leading-relaxed">
                            {section.proTip}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Comparison Table: Free vs Professional */}
      <div className="bg-white rounded-xl shadow-lg border-2 border-gray-200 overflow-hidden">
        <div className="bg-gradient-to-r from-[#1E2A44] to-[#2D3E5F] p-6 text-white">
          <div className="flex items-center gap-3 mb-2">
            <Award className="w-6 h-6 md:w-8 md:h-8" />
            <h3 className="text-2xl md:text-3xl font-bold">Free Report vs Professional Report</h3>
          </div>
          <p className="text-gray-200">See what you get with each tier</p>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Feature</th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-gray-900">Free Report</th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-[#10B981] bg-green-50">Professional Report</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              <tr>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">Recommended Homes</td>
                <td className="px-6 py-4 text-center text-sm text-gray-600">3 homes</td>
                <td className="px-6 py-4 text-center text-sm font-semibold text-[#10B981]">5 homes</td>
              </tr>
              <tr className="bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">Funding Eligibility</td>
                <td className="px-6 py-4 text-center text-sm text-gray-600">Ranges (e.g., 68-87%)</td>
                <td className="px-6 py-4 text-center text-sm font-semibold text-[#10B981]">Exact calculations</td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">CHC Assessment</td>
                <td className="px-6 py-4 text-center text-sm text-gray-600">Simplified estimate</td>
                <td className="px-6 py-4 text-center text-sm font-semibold text-[#10B981]">12-domain detailed assessment</td>
              </tr>
              <tr className="bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">Financial Analysis</td>
                <td className="px-6 py-4 text-center text-sm text-gray-600">Not included</td>
                <td className="px-6 py-4 text-center text-sm font-semibold text-[#10B981]">Altman Z-score, bankruptcy risk, 3-year trends</td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">Staff Quality Research</td>
                <td className="px-6 py-4 text-center text-sm text-gray-600">Not included</td>
                <td className="px-6 py-4 text-center text-sm font-semibold text-[#10B981]">Glassdoor, LinkedIn, job boards analysis</td>
              </tr>
              <tr className="bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">Google Places Insights</td>
                <td className="px-6 py-4 text-center text-sm text-gray-600">Basic ratings</td>
                <td className="px-6 py-4 text-center text-sm font-semibold text-[#10B981]">Dwell time, repeat visitors, footfall trends</td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">Negotiation Strategy</td>
                <td className="px-6 py-4 text-center text-sm text-gray-600">Not included</td>
                <td className="px-6 py-4 text-center text-sm font-semibold text-[#10B981]">Templates, talking points, email drafts</td>
              </tr>
              <tr className="bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">Risk Assessment</td>
                <td className="px-6 py-4 text-center text-sm text-gray-600">Not included</td>
                <td className="px-6 py-4 text-center text-sm font-semibold text-[#10B981]">Red flags, compliance issues, staff turnover</td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">5-Year Cost Projections</td>
                <td className="px-6 py-4 text-center text-sm text-gray-600">Not included</td>
                <td className="px-6 py-4 text-center text-sm font-semibold text-[#10B981]">All funding scenarios with inflation</td>
              </tr>
              <tr className="bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">Application Templates</td>
                <td className="px-6 py-4 text-center text-sm text-gray-600">Not included</td>
                <td className="px-6 py-4 text-center text-sm font-semibold text-[#10B981]">CHC, LA, DPA ready-to-use templates</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* What You're Missing - Unique Value Props */}
      <div className="bg-gradient-to-br from-purple-50 via-indigo-50 to-blue-50 rounded-xl border-2 border-purple-200 p-6 md:p-8">
        <div className="flex items-center gap-3 mb-4">
          <Zap className="w-6 h-6 md:w-8 md:h-8 text-purple-600" />
          <h3 className="text-2xl md:text-3xl font-bold text-gray-900">What Makes Professional Report Unique</h3>
        </div>
        <p className="text-gray-700 mb-6 text-lg">
          While this free report gives you a great starting point, Professional Report unlocks insights that could save you tens of thousands of pounds:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white rounded-lg p-5 border border-purple-200 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <DollarSign className="w-5 h-5 text-purple-600" />
              <h4 className="font-bold text-gray-900">Exact Funding Calculations</h4>
            </div>
            <p className="text-sm text-gray-700 mb-2">
              Instead of "maybe 68-87%", get your exact CHC probability with detailed 12-domain breakdown. 
              Know exactly what to apply for and how much you'll save.
            </p>
            <p className="text-xs text-purple-700 font-semibold">Potential value: £50k-£130k/year if eligible</p>
          </div>
          
          <div className="bg-white rounded-lg p-5 border border-purple-200 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <Shield className="w-5 h-5 text-purple-600" />
              <h4 className="font-bold text-gray-900">Financial Risk Detection</h4>
            </div>
            <p className="text-sm text-gray-700 mb-2">
              Altman Z-score analysis reveals which homes are financially stable. Avoid homes at risk of closure 
              or cost-cutting that could impact care quality.
            </p>
            <p className="text-xs text-purple-700 font-semibold">Potential value: Avoid costly mistakes</p>
          </div>
          
          <div className="bg-white rounded-lg p-5 border border-purple-200 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="w-5 h-5 text-purple-600" />
              <h4 className="font-bold text-gray-900">Negotiation Power</h4>
            </div>
            <p className="text-sm text-gray-700 mb-2">
              Ready-to-use email templates and talking points based on MSIF data. Negotiate from a position of 
              knowledge, not guesswork.
            </p>
            <p className="text-xs text-purple-700 font-semibold">Potential value: £20k-£40k/year savings</p>
          </div>
          
          <div className="bg-white rounded-lg p-5 border border-purple-200 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <Building2 className="w-5 h-5 text-purple-600" />
              <h4 className="font-bold text-gray-900">Behavioral Insights</h4>
            </div>
            <p className="text-sm text-gray-700 mb-2">
              Google Places NEW API reveals dwell time, repeat visitor rates, and family engagement scores. 
              See which homes families actually visit and return to.
            </p>
            <p className="text-xs text-purple-700 font-semibold">Potential value: Choose homes with proven family satisfaction</p>
          </div>
        </div>
      </div>

      {/* Upgrade CTA - Enhanced */}
      <div className="bg-gradient-to-r from-[#10B981] via-[#059669] to-[#047857] rounded-xl shadow-2xl p-8 md:p-12 text-white relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div
            className="absolute inset-0"
            style={{
              backgroundImage:
                'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
              backgroundSize: '40px 40px',
            }}
          ></div>
        </div>
        
        <div className="relative z-10">
          <div className="text-center mb-8">
            <div className="inline-flex items-center gap-2 bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full mb-4">
              <Award className="w-5 h-5" />
              <span className="text-sm font-semibold">30-35 Page Comprehensive Analysis</span>
            </div>
            <h3 className="text-3xl md:text-4xl font-bold mb-4">
              Ready to Make the Best Decision?
            </h3>
            <p className="text-xl text-green-50 mb-2 max-w-3xl mx-auto">
              Professional Report transforms estimates into exact calculations, giving you the confidence 
              to negotiate better deals and secure maximum funding.
            </p>
            <p className="text-lg text-green-100 font-semibold">
              Investment: £119 | Potential Savings: £50k-£130k+ per year
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
              <div className="flex items-center gap-2 mb-4">
                <Zap className="w-6 h-6 text-yellow-300" />
                <h4 className="text-xl font-bold">What You Get</h4>
              </div>
              <ul className="space-y-3 text-left">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-300 flex-shrink-0 mt-0.5" />
                  <span>Exact CHC/LA/DPA calculations (not ranges)</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-300 flex-shrink-0 mt-0.5" />
                  <span>5 recommended homes with deep-dive analysis</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-300 flex-shrink-0 mt-0.5" />
                  <span>Ready-to-use negotiation templates & email drafts</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-300 flex-shrink-0 mt-0.5" />
                  <span>Financial stability & risk assessment for each home</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-300 flex-shrink-0 mt-0.5" />
                  <span>Staff quality research (Glassdoor, LinkedIn, job boards)</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-300 flex-shrink-0 mt-0.5" />
                  <span>5-year cost projections for all funding scenarios</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-300 flex-shrink-0 mt-0.5" />
                  <span>Google Places behavioral insights (dwell time, repeat visitors)</span>
                </li>
              </ul>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
              <div className="flex items-center gap-2 mb-4">
                <Target className="w-6 h-6 text-yellow-300" />
                <h4 className="text-xl font-bold">Why It Matters</h4>
              </div>
              <ul className="space-y-3 text-left">
                <li className="flex items-start gap-2">
                  <ArrowRight className="w-5 h-5 text-green-300 flex-shrink-0 mt-0.5" />
                  <span><strong>Know your exact funding eligibility</strong> - no more guessing if you qualify</span>
                </li>
                <li className="flex items-start gap-2">
                  <ArrowRight className="w-5 h-5 text-green-300 flex-shrink-0 mt-0.5" />
                  <span><strong>Negotiate from strength</strong> - use MSIF data to justify lower rates</span>
                </li>
                <li className="flex items-start gap-2">
                  <ArrowRight className="w-5 h-5 text-green-300 flex-shrink-0 mt-0.5" />
                  <span><strong>Avoid financial risks</strong> - identify homes at risk of closure</span>
                </li>
                <li className="flex items-start gap-2">
                  <ArrowRight className="w-5 h-5 text-green-300 flex-shrink-0 mt-0.5" />
                  <span><strong>Save time on applications</strong> - use ready-made templates</span>
                </li>
                <li className="flex items-start gap-2">
                  <ArrowRight className="w-5 h-5 text-green-300 flex-shrink-0 mt-0.5" />
                  <span><strong>Make confident decisions</strong> - comprehensive data on all 5 homes</span>
                </li>
                <li className="flex items-start gap-2">
                  <ArrowRight className="w-5 h-5 text-green-300 flex-shrink-0 mt-0.5" />
                  <span><strong>Plan long-term</strong> - 5-year projections help budget effectively</span>
                </li>
              </ul>
            </div>
          </div>

          <div className="text-center">
            <div className="inline-block bg-white/20 backdrop-blur-sm rounded-lg px-6 py-3 mb-4 border border-white/30">
              <p className="text-sm text-green-100">
                <span className="font-bold">ROI Example:</span> If you save just £50k/year through better funding or negotiation, 
                your £119 investment pays for itself in less than 1 day.
              </p>
            </div>
            <button className="bg-white hover:bg-gray-100 text-[#10B981] font-bold py-4 px-8 rounded-xl text-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 flex items-center gap-2 mx-auto">
              <span>Upgrade to Professional Report - £119</span>
              <ArrowRight className="w-5 h-5" />
            </button>
            <p className="text-sm text-green-100 mt-4">
              30-day money-back guarantee • Delivered within 24-48 hours
            </p>
          </div>
        </div>
      </div>

      {/* Tips Section */}
      <div className="bg-blue-50 rounded-xl border border-blue-200 p-6">
        <div className="flex items-start gap-3">
          <Info className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-semibold text-blue-900 mb-2">💡 Tips for Using This Report</h3>
            <ul className="space-y-2 text-sm text-blue-800">
              <li className="flex items-start gap-2">
                <span className="font-semibold">1.</span>
                <span>Start with the Top 3 Homes section - these are pre-screened for quality and match your needs</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-semibold">2.</span>
                <span>Review the Fair Cost Gap - this shows potential overpayment you may be able to negotiate</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-semibold">3.</span>
                <span>Check Funding Eligibility - you may qualify for £50k-£100k+ per year in government funding</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-semibold">4.</span>
                <span>Use the Comparison Table to quickly identify the best value option</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-semibold">5.</span>
                <span>Follow the Checklist & Next Steps to ensure you don't miss important actions</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-semibold">6.</span>
                <span>Consider upgrading to Professional Report for exact calculations and detailed analysis</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

