import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface CookieConsentState {
  hasConsented: boolean;
  consentDate: string | null;
  analyticsEnabled: boolean;
  marketingEnabled: boolean;
  setConsent: (analytics: boolean, marketing: boolean) => void;
  clearConsent: () => void;
}

const COOKIE_CONSENT_KEY = 'cookie-consent';

export const useCookieConsentStore = create<CookieConsentState>()(
  persist(
    (set) => ({
      hasConsented: false,
      consentDate: null,
      analyticsEnabled: false,
      marketingEnabled: false,
      setConsent: (analytics: boolean, marketing: boolean) => {
        set({
          hasConsented: true,
          consentDate: new Date().toISOString(),
          analyticsEnabled: analytics,
          marketingEnabled: marketing,
        });
      },
      clearConsent: () => {
        set({
          hasConsented: false,
          consentDate: null,
          analyticsEnabled: false,
          marketingEnabled: false,
        });
        localStorage.removeItem(COOKIE_CONSENT_KEY);
      },
    }),
    {
      name: COOKIE_CONSENT_KEY,
      version: 1,
    }
  )
);

