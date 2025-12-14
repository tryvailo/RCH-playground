import { AlertTriangle, FileText, Shield, RefreshCw } from 'lucide-react';

interface LegalDisclaimerProps {
  className?: string;
  compact?: boolean;
}

export default function LegalDisclaimer({ className = '', compact = false }: LegalDisclaimerProps) {
  if (compact) {
    return (
      <div className={`text-xs text-gray-500 space-y-1 ${className}`}>
        <p>
          <strong>Disclaimer:</strong> This calculator provides estimates only. Actual eligibility is determined by official NHS and Local Authority assessments.
        </p>
        <div className="flex flex-wrap gap-2">
          <a href="/terms-of-service" className="hover:underline">Terms of Service</a>
          <span>•</span>
          <a href="/privacy-policy" className="hover:underline">Privacy Policy</a>
          <span>•</span>
          <a href="/refund-policy" className="hover:underline">Refund Policy</a>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-amber-50 border border-amber-200 rounded-lg p-6 space-y-4 ${className}`}>
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h3 className="font-semibold text-amber-900 mb-2">Important Legal Disclaimer</h3>
          
          <div className="space-y-3 text-sm text-amber-800">
            <p>
              <strong>This calculator provides estimates and guidance only.</strong> Actual eligibility for funding is determined by official NHS and Local Authority assessments. Results should not be considered as guarantees or official decisions.
            </p>
            
            <p>
              <strong>Not Financial or Legal Advice:</strong> This tool is for informational purposes only and does not constitute financial, legal, or professional advice. Always seek professional advice from qualified advisors for important financial and care decisions.
            </p>
            
            <p>
              <strong>No Guarantees:</strong> RightCareHome makes no warranties or representations regarding the accuracy, completeness, or reliability of the calculations. Actual funding outcomes may vary based on individual circumstances and official assessments.
            </p>
            
            <p>
              <strong>Limitation of Liability:</strong> RightCareHome is not responsible for decisions made based on calculator results. Use this tool as part of a comprehensive assessment process, not as the sole basis for decisions. RightCareHome shall not be liable for any losses, damages, or consequences arising from the use of this calculator.
            </p>
            
            <p>
              <strong>Official Assessments Required:</strong> This calculator cannot replace official NHS Continuing Healthcare (CHC) assessments or Local Authority means tests. Always consult with your local Integrated Care Board (ICB) for CHC assessments and your Local Authority for means-tested support.
            </p>
          </div>
          
          <div className="mt-4 pt-4 border-t border-amber-200">
            <div className="flex flex-wrap items-center gap-4 text-sm">
              <a 
                href="/terms-of-service" 
                className="flex items-center gap-1 text-amber-700 hover:text-amber-900 hover:underline"
              >
                <FileText className="w-4 h-4" />
                Terms of Service
              </a>
              <a 
                href="/privacy-policy" 
                className="flex items-center gap-1 text-amber-700 hover:text-amber-900 hover:underline"
              >
                <Shield className="w-4 h-4" />
                Privacy Policy
              </a>
              <a 
                href="/refund-policy" 
                className="flex items-center gap-1 text-amber-700 hover:text-amber-900 hover:underline"
              >
                <RefreshCw className="w-4 h-4" />
                Refund Policy
              </a>
            </div>
          </div>
          
          <div className="mt-4 text-xs text-amber-700">
            <p>
              <strong>Last Updated:</strong> January 2025 | 
              <strong> Calculator Version:</strong> 2025-2026 | 
              <strong> Based On:</strong> NHS National Framework 2022 (current 2025), MSIF 2025-2026, Care Act 2014
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

