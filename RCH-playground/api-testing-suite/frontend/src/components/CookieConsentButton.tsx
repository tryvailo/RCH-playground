import { useState } from 'react';
import { Cookie } from 'lucide-react';
import { useCookieConsentStore } from '../stores/cookieConsentStore';
import CookieConsentBanner from './CookieConsentBanner';

/**
 * Floating button to reopen cookie consent settings
 */
export default function CookieConsentButton() {
  const { hasConsented } = useCookieConsentStore();
  const [showBanner, setShowBanner] = useState(false);

  // Don't show if user hasn't consented yet (banner will show)
  if (!hasConsented) {
    return null;
  }

  return (
    <>
      <button
        onClick={() => setShowBanner(true)}
        className="fixed bottom-4 right-4 z-40 bg-blue-600 text-white p-3 rounded-full shadow-lg hover:bg-blue-700 transition-colors"
        aria-label="Cookie preferences"
        title="Cookie preferences"
      >
        <Cookie className="w-5 h-5" />
      </button>
      {showBanner && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-50" onClick={() => setShowBanner(false)}>
          <div onClick={(e) => e.stopPropagation()}>
            <CookieConsentBanner 
              forceShow={true} 
              onClose={() => setShowBanner(false)} 
            />
          </div>
        </div>
      )}
    </>
  );
}

