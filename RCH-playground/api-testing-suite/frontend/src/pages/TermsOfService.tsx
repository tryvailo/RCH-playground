import { FileText, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function TermsOfService() {
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <Link to="/funding-calculator" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800">
        <ArrowLeft className="w-4 h-4" />
        Back to Funding Calculator
      </Link>

      <div className="bg-white rounded-lg shadow p-8">
        <div className="flex items-center gap-3 mb-6">
          <FileText className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">Terms of Service</h1>
        </div>

        <div className="prose max-w-none space-y-6 text-gray-700">
          <div>
            <p className="text-sm text-gray-500 mb-4">Last Updated: January 2025</p>
            
            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">1. Acceptance of Terms</h2>
            <p>
              By accessing and using the RightCareHome Funding Eligibility Calculator ("the Service"), you accept and agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use the Service.
            </p>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">2. Description of Service</h2>
            <p>
              The Funding Eligibility Calculator is an informational tool designed to provide estimates of potential funding eligibility for care home placements. The Service calculates estimates for:
            </p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>NHS Continuing Healthcare (CHC) eligibility probability</li>
              <li>Local Authority (LA) support and means-tested funding</li>
              <li>Deferred Payment Agreement (DPA) eligibility</li>
              <li>Potential savings and cost projections</li>
            </ul>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">3. Not Professional Advice</h2>
            <p>
              <strong>The Service does not provide financial, legal, or professional advice.</strong> The calculations and estimates provided are for informational purposes only and should not be considered as:
            </p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>Official NHS or Local Authority assessments</li>
              <li>Guarantees of funding eligibility</li>
              <li>Substitutes for professional financial or legal advice</li>
              <li>Binding commitments or promises</li>
            </ul>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">4. No Warranties</h2>
            <p>
              RightCareHome makes no warranties or representations regarding:
            </p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>The accuracy, completeness, or reliability of calculations</li>
              <li>The suitability of the Service for your specific circumstances</li>
              <li>The availability or uninterrupted operation of the Service</li>
              <li>The absence of errors or defects in the Service</li>
            </ul>
            <p className="mt-4">
              The Service is provided "as is" and "as available" without warranties of any kind, either express or implied.
            </p>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">5. Limitation of Liability</h2>
            <p>
              To the fullest extent permitted by law, RightCareHome shall not be liable for:
            </p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>Any losses, damages, or consequences arising from the use of the Service</li>
              <li>Decisions made based on calculator results</li>
              <li>Incorrect or incomplete information provided by users</li>
              <li>Changes in legislation, regulations, or funding thresholds</li>
              <li>Technical failures, interruptions, or errors in the Service</li>
            </ul>
            <p className="mt-4">
              RightCareHome's total liability, if any, shall not exceed the amount paid by you for the Service (if applicable).
            </p>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">6. User Responsibilities</h2>
            <p>You agree to:</p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>Provide accurate and complete information when using the Service</li>
              <li>Use the Service only for lawful purposes</li>
              <li>Not rely solely on calculator results for important decisions</li>
              <li>Seek professional advice for financial and care decisions</li>
              <li>Consult official NHS and Local Authority sources for actual assessments</li>
            </ul>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">7. Official Assessments Required</h2>
            <p>
              This calculator cannot replace official assessments. You must:
            </p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>Contact your local Integrated Care Board (ICB) for CHC assessments</li>
              <li>Contact your Local Authority for means-tested support assessments</li>
              <li>Follow official application processes and procedures</li>
              <li>Provide required documentation and evidence</li>
            </ul>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">8. Intellectual Property</h2>
            <p>
              The Service, including its design, algorithms, calculations, and content, is the property of RightCareHome and is protected by copyright and other intellectual property laws. You may not reproduce, distribute, or create derivative works without permission.
            </p>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">9. Changes to Terms</h2>
            <p>
              RightCareHome reserves the right to modify these Terms of Service at any time. Changes will be effective immediately upon posting. Your continued use of the Service constitutes acceptance of modified terms.
            </p>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">10. Contact Information</h2>
            <p>
              For questions about these Terms of Service, please contact:
            </p>
            <p className="ml-4">
              <strong>RightCareHome</strong><br />
              Email: support@rightcarehome.co.uk<br />
              Website: www.rightcarehome.co.uk
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

