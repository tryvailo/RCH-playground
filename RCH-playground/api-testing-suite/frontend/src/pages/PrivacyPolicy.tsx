import { Shield, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function PrivacyPolicy() {
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <Link to="/funding-calculator" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800">
        <ArrowLeft className="w-4 h-4" />
        Back to Funding Calculator
      </Link>

      <div className="bg-white rounded-lg shadow p-8">
        <div className="flex items-center gap-3 mb-6">
          <Shield className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">Privacy Policy</h1>
        </div>

        <div className="prose max-w-none space-y-6 text-gray-700">
          <div>
            <p className="text-sm text-gray-500 mb-4">Last Updated: January 2025</p>
            
            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">1. Introduction</h2>
            <p>
              RightCareHome ("we", "us", "our") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, store, and protect your personal information when you use the Funding Eligibility Calculator.
            </p>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">2. Information We Collect</h2>
            <p>When you use the Funding Eligibility Calculator, we may collect:</p>
            
            <h3 className="text-xl font-semibold text-gray-900 mt-4 mb-2">2.1 Information You Provide</h3>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>Age and demographic information</li>
              <li>Health and medical information (domain assessments, conditions, therapies)</li>
              <li>Financial information (capital assets, income, property details)</li>
              <li>Care preferences and requirements</li>
              <li>Contact information (if provided)</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-900 mt-4 mb-2">2.2 Automatically Collected Information</h3>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>IP address and device information</li>
              <li>Browser type and version</li>
              <li>Usage data and analytics</li>
              <li>Error logs and debugging information</li>
            </ul>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">3. How We Use Your Information</h2>
            <p>We use your information to:</p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>Calculate funding eligibility estimates</li>
              <li>Provide and improve the Service</li>
              <li>Respond to your inquiries and support requests</li>
              <li>Analyze usage patterns and improve user experience</li>
              <li>Ensure security and prevent fraud</li>
              <li>Comply with legal obligations</li>
            </ul>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">4. Data Storage and Security</h2>
            <p>
              We implement appropriate technical and organizational measures to protect your personal information:
            </p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>Encryption of sensitive data in transit and at rest</li>
              <li>Secure servers and databases</li>
              <li>Access controls and authentication</li>
              <li>Regular security audits and updates</li>
            </ul>
            <p className="mt-4">
              However, no method of transmission over the internet is 100% secure. While we strive to protect your information, we cannot guarantee absolute security.
            </p>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">5. Data Retention</h2>
            <p>
              We retain your information only for as long as necessary to:
            </p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>Provide the Service</li>
              <li>Comply with legal obligations</li>
              <li>Resolve disputes and enforce agreements</li>
            </ul>
            <p className="mt-4">
              You may request deletion of your data at any time by contacting us at support@rightcarehome.co.uk.
            </p>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">6. Your Rights (GDPR)</h2>
            <p>Under GDPR, you have the right to:</p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li><strong>Access:</strong> Request a copy of your personal data</li>
              <li><strong>Rectification:</strong> Correct inaccurate or incomplete data</li>
              <li><strong>Erasure:</strong> Request deletion of your data</li>
              <li><strong>Restriction:</strong> Request limitation of processing</li>
              <li><strong>Portability:</strong> Receive your data in a structured format</li>
              <li><strong>Objection:</strong> Object to processing of your data</li>
            </ul>
            <p className="mt-4">
              To exercise these rights, contact us at support@rightcarehome.co.uk.
            </p>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">7. Third-Party Services</h2>
            <p>
              We may use third-party services for analytics, hosting, and other functions. These services have their own privacy policies and may collect information independently.
            </p>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">8. Cookies and Tracking</h2>
            <p>
              We may use cookies and similar technologies to:
            </p>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li>Remember your preferences</li>
              <li>Analyze usage patterns</li>
              <li>Improve service functionality</li>
            </ul>
            <p className="mt-4">
              You can control cookies through your browser settings.
            </p>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">9. Children's Privacy</h2>
            <p>
              The Service is not intended for users under 18 years of age. We do not knowingly collect personal information from children.
            </p>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">10. Changes to Privacy Policy</h2>
            <p>
              We may update this Privacy Policy from time to time. Changes will be posted on this page with an updated "Last Updated" date.
            </p>

            <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-4">11. Contact Us</h2>
            <p>
              For questions about this Privacy Policy or to exercise your rights, please contact:
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

