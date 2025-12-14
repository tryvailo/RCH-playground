import { useState, useEffect } from 'react';
import { X, Cookie, Settings, CheckCircle } from 'lucide-react';
import { useCookieConsentStore } from '../stores/cookieConsentStore';

interface CookieConsentBannerProps {
  forceShow?: boolean;
  onClose?: () => void;
}

export default function CookieConsentBanner({ forceShow = false, onClose }: CookieConsentBannerProps) {
  const { hasConsented, setConsent, analyticsEnabled, marketingEnabled } = useCookieConsentStore();
  const [showBanner, setShowBanner] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [localAnalytics, setLocalAnalytics] = useState(false);
  const [localMarketing, setLocalMarketing] = useState(false);

  useEffect(() => {
    // Show banner if forced or if user hasn't consented yet
    if (forceShow || !hasConsented) {
      // Small delay for better UX (only if not forced)
      const timer = setTimeout(() => {
        setShowBanner(true);
      }, forceShow ? 0 : 1000);
      return () => clearTimeout(timer);
    }
  }, [hasConsented, forceShow]);

  const handleAcceptAll = () => {
    setConsent(true, true);
    setShowBanner(false);
    setShowSettings(false);
    if (onClose) onClose();
  };

  const handleRejectAll = () => {
    setConsent(false, false);
    setShowBanner(false);
    setShowSettings(false);
    if (onClose) onClose();
  };

  const handleSavePreferences = () => {
    setConsent(localAnalytics, localMarketing);
    setShowBanner(false);
    setShowSettings(false);
    if (onClose) onClose();
  };

  const handleCustomize = () => {
    setLocalAnalytics(analyticsEnabled);
    setLocalMarketing(marketingEnabled);
    setShowSettings(true);
  };

  if (!showBanner) {
    return null;
  }

  if (showSettings) {
    return (
      <div className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 shadow-2xl">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <Settings className="w-6 h-6 text-blue-600" />
              <h3 className="text-lg font-semibold text-gray-900">Cookie Preferences</h3>
            </div>
            <button
              onClick={() => setShowSettings(false)}
              className="text-gray-400 hover:text-gray-600"
              aria-label="Close settings"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="space-y-6">
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-700 mb-4">
                We use cookies to enhance your experience, analyze site usage, and assist in our marketing efforts. 
                You can customize your preferences below.
              </p>
            </div>

            {/* Essential Cookies */}
            <div className="border-b pb-4">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h4 className="font-semibold text-gray-900">Essential Cookies</h4>
                  <p className="text-sm text-gray-600">Always active - Required for the website to function</p>
                </div>
                <div className="flex items-center gap-2 text-green-600">
                  <CheckCircle className="w-5 h-5" />
                  <span className="text-sm font-medium">Always On</span>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                These cookies are necessary for the website to function and cannot be switched off. 
                They include session management, security, and preference storage.
              </p>
            </div>

            {/* Analytics Cookies */}
            <div className="border-b pb-4">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900">Analytics Cookies</h4>
                  <p className="text-sm text-gray-600">Help us understand how visitors interact with our website</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={localAnalytics}
                    onChange={(e) => setLocalAnalytics(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                These cookies allow us to count visits and traffic sources so we can measure and improve the performance of our site. 
                They help us know which pages are most and least popular.
              </p>
            </div>

            {/* Marketing Cookies */}
            <div className="pb-4">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900">Marketing Cookies</h4>
                  <p className="text-sm text-gray-600">Used to track visitors across websites for marketing purposes</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={localMarketing}
                    onChange={(e) => setLocalMarketing(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                These cookies may be set through our site by our advertising partners. They may be used to build a profile 
                of your interests and show you relevant content on other sites.
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-3 pt-4">
              <button
                onClick={handleSavePreferences}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
              >
                Save Preferences
              </button>
              <button
                onClick={handleRejectAll}
                className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium"
              >
                Reject All
              </button>
              <button
                onClick={handleAcceptAll}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
              >
                Accept All
              </button>
            </div>

            <div className="text-xs text-gray-500 pt-2 border-t">
              <p>
                You can change your cookie preferences at any time by clicking the cookie icon in the bottom right corner. 
                For more information, see our{' '}
                <a href="/privacy-policy" className="text-blue-600 hover:underline">
                  Privacy Policy
                </a>
                .
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 shadow-2xl animate-slide-up">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-start gap-3 flex-1">
            <Cookie className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 mb-1">We Value Your Privacy</h3>
              <p className="text-sm text-gray-700">
                We use cookies to enhance your browsing experience, analyze site traffic, and personalize content. 
                By clicking "Accept All", you consent to our use of cookies. You can customize your preferences or 
                learn more in our{' '}
                <a href="/privacy-policy" className="text-blue-600 hover:underline font-medium">
                  Privacy Policy
                </a>
                .
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handleCustomize}
              className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium text-sm whitespace-nowrap"
            >
              <Settings className="w-4 h-4 inline mr-1" />
              Customize
            </button>
            <button
              onClick={handleRejectAll}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium text-sm whitespace-nowrap"
            >
              Reject All
            </button>
            <button
              onClick={handleAcceptAll}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-sm whitespace-nowrap"
            >
              Accept All
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

