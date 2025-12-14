import { RefreshCw, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function RefundPolicy() {
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <Link to="/funding-calculator" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800">
        <ArrowLeft className="w-4 h-4" />
        Back to Funding Calculator
      </Link>

      <div className="bg-white rounded-lg shadow p-8">
        <div className="flex items-center gap-3 mb-6">
          <RefreshCw className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">Refund Policy</h1>
        </div>

        <div className="prose max-w-none space-y-6 text-gray-700">
          <div>
            <p className="text-sm text-gray-500 mb-4">Last Updated: January 2025</p>
            
            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">1. Overview</h2>
            <p>
              This Refund Policy applies to paid services provided by RightCareHome, including but not limited to the Funding Eligibility Calculator and related reports.
            </p>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">2. Free Services</h2>
            <p>
              The Funding Eligibility Calculator is currently provided as a free service. No refunds are applicable for free services.
            </p>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">3. Paid Services</h2>
            <p>For paid services (if applicable in the future), the following refund policy applies:</p>

            <h3 className="text-xl font-semibold text-gray-900 mt-4 mb-2">3.1 Eligibility for Refund</h3>
            <p>You may be eligible for a refund if:</p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>The service was not delivered as described</li>
              <li>Technical errors prevented you from accessing the service</li>
              <li>You cancel within 14 days of purchase (UK Consumer Rights)</li>
              <li>We are unable to provide the service due to our error</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-900 mt-4 mb-2">3.2 Non-Refundable Situations</h3>
            <p>Refunds will not be provided for:</p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>Dissatisfaction with calculation results or estimates</li>
              <li>Changes in personal circumstances after purchase</li>
              <li>Incorrect information provided by you</li>
              <li>Services that have been fully delivered and accessed</li>
              <li>Requests made more than 30 days after purchase</li>
            </ul>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">4. Refund Process</h2>
            <p>To request a refund:</p>
            <ol className="list-decimal list-inside ml-4 space-y-1">
              <li>Contact us at support@rightcarehome.co.uk within the eligible timeframe</li>
              <li>Provide your order number or transaction details</li>
              <li>Explain the reason for your refund request</li>
              <li>We will review your request within 5 business days</li>
              <li>If approved, refunds will be processed within 10 business days</li>
            </ol>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">5. Refund Method</h2>
            <p>
              Refunds will be issued to the original payment method used for the purchase. Processing times may vary depending on your payment provider.
            </p>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">6. Partial Refunds</h2>
            <p>
              In some cases, we may offer partial refunds if only part of the service was not delivered or accessed.
            </p>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">7. Disputes</h2>
            <p>
              If you are not satisfied with our refund decision, you may:
            </p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>Contact us for further review</li>
              <li>File a complaint with your payment provider</li>
              <li>Seek advice from Citizens Advice or Trading Standards</li>
            </ul>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">8. Changes to Refund Policy</h2>
            <p>
              We reserve the right to modify this Refund Policy at any time. Changes will be effective immediately upon posting.
            </p>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">9. Contact Us</h2>
            <p>
              For refund requests or questions about this policy, please contact:
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

