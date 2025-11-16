import { useState, useEffect } from 'react';
import { Save } from 'lucide-react';
import axios from 'axios';
import { useApiStore } from '../stores/apiStore';
import type { ApiCredentials } from '../types/api.types';

export default function ApiConfig() {
  const { credentials, setCredentials } = useApiStore();
  const [formData, setFormData] = useState<ApiCredentials>(credentials || {});
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<Record<string, boolean>>({});

  useEffect(() => {
    loadCredentials();
  }, []);

  const loadCredentials = async () => {
    try {
      const response = await axios.get('/api/config/credentials');
      if (response.data && response.data.credentials) {
        const creds = response.data.credentials;
        
        // Load credentials from backend - always include all sections
        const loadedCreds: ApiCredentials = {
          cqc: {
            partnerCode: creds.cqc?.partnerCode || '',
            useWithoutCode: creds.cqc?.useWithoutCode ?? true,
            primarySubscriptionKey: creds.cqc?.primarySubscriptionKey || '',
            secondarySubscriptionKey: creds.cqc?.secondarySubscriptionKey || '',
          },
          companiesHouse: {
            apiKey: creds.companiesHouse?.apiKey || '',
          },
          googlePlaces: {
            apiKey: creds.googlePlaces?.apiKey || '',
          },
          perplexity: {
            apiKey: creds.perplexity?.apiKey || '',
          },
          besttime: {
            privateKey: creds.besttime?.privateKey || '',
            publicKey: creds.besttime?.publicKey || '',
          },
          autumna: {
            proxyUrl: creds.autumna?.proxyUrl || '',
            useProxy: creds.autumna?.useProxy || false,
          },
          openai: {
            apiKey: creds.openai?.apiKey || '',
          },
          firecrawl: {
            apiKey: creds.firecrawl?.apiKey || '',
          },
        };
        
        setFormData(loadedCreds);
        setCredentials(loadedCreds);
      }
    } catch (error) {
      console.error('Failed to load credentials:', error);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.post('/api/config/credentials', formData);
      setCredentials(formData);
      alert('Credentials saved successfully!');
    } catch (error: any) {
      alert(`Failed to save: ${error.response?.data?.detail || error.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async (apiName: string) => {
    setTesting(apiName);
    try {
      await axios.post('/api/config/validate');
      setTestResults({ ...testResults, [apiName]: true });
    } catch (error) {
      setTestResults({ ...testResults, [apiName]: false });
    } finally {
      setTesting(null);
    }
  };

  const updateField = (section: keyof ApiCredentials, field: string, value: any) => {
    setFormData({
      ...formData,
      [section]: {
        ...(formData[section] as any),
        [field]: value,
      },
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">API Configuration</h1>
        <p className="mt-2 text-gray-600">Configure credentials for all API services</p>
      </div>

      {/* CQC */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">CQC API</h2>
          <button
            onClick={() => handleTest('cqc')}
            className="text-sm text-info hover:text-blue-700"
            disabled={testing === 'cqc'}
          >
            {testing === 'cqc' ? 'Testing...' : 'Test Connection'}
          </button>
        </div>
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-md p-3 mb-4">
            <p className="text-sm text-blue-800">
              <strong>New API (2024-2025):</strong> CQC API now requires subscription keys. 
              Register at{' '}
              <a href="https://api-portal.service.cqc.org.uk/" target="_blank" className="underline font-semibold">
                CQC API Portal
              </a>{' '}
              to get your subscription keys.
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Primary Subscription Key <span className="text-red-500">*</span>
            </label>
            <input
              type="password"
              value={formData.cqc?.primarySubscriptionKey || ''}
              onChange={(e) => updateField('cqc', 'primarySubscriptionKey', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              placeholder="e96322da6d094f0ebec30c526a74205a"
            />
            <p className="text-xs text-gray-500 mt-1">
              Required for new CQC API. Get it from your API Portal profile.
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Secondary Subscription Key (Optional)
            </label>
            <input
              type="password"
              value={formData.cqc?.secondarySubscriptionKey || ''}
              onChange={(e) => updateField('cqc', 'secondarySubscriptionKey', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              placeholder="b9dfa372a9ec40cf96fa4d5e1c1dbc23"
            />
            <p className="text-xs text-gray-500 mt-1">
              Used for key rotation without service interruption.
            </p>
          </div>
          <div className="border-t pt-4 mt-4">
            <p className="text-xs text-gray-500 mb-2 font-semibold">Legacy Settings (Deprecated):</p>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Partner Code (Deprecated)
              </label>
              <input
                type="text"
                value={formData.cqc?.partnerCode || ''}
                onChange={(e) => updateField('cqc', 'partnerCode', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                placeholder="Legacy partner code (not recommended)"
              />
            </div>
            <div className="flex items-center mt-2">
              <input
                type="checkbox"
                checked={formData.cqc?.useWithoutCode ?? true}
                onChange={(e) => updateField('cqc', 'useWithoutCode', e.target.checked)}
                className="mr-2"
              />
              <label className="text-sm text-gray-700">Use API without partner code</label>
            </div>
          </div>
        </div>
      </div>

      {/* Companies House */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Companies House API</h2>
          <button
            onClick={() => handleTest('companies_house')}
            className="text-sm text-info hover:text-blue-700"
            disabled={testing === 'companies_house'}
          >
            {testing === 'companies_house' ? 'Testing...' : 'Test Connection'}
          </button>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            API Key
          </label>
          <input
            type="password"
            value={formData.companiesHouse?.apiKey || ''}
            onChange={(e) => updateField('companiesHouse', 'apiKey', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2"
            placeholder="Your Companies House API key"
          />
          <p className="text-xs text-gray-500 mt-1">
            Free API. Get your key at{' '}
            <a
              href="https://developer.company-information.service.gov.uk/"
              target="_blank"
              className="text-info"
            >
              Companies House Developer Hub
            </a>
          </p>
        </div>
      </div>

      {/* Google Places */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Google Places API</h2>
          <button
            onClick={() => handleTest('google_places')}
            className="text-sm text-info hover:text-blue-700"
            disabled={testing === 'google_places'}
          >
            {testing === 'google_places' ? 'Testing...' : 'Test Connection'}
          </button>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            API Key
          </label>
          <input
            type="password"
            value={formData.googlePlaces?.apiKey || ''}
            onChange={(e) => updateField('googlePlaces', 'apiKey', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2"
            placeholder="Your Google Places API key"
          />
          <p className="text-xs text-gray-500 mt-1">
            $200 free credits/month. Get your key at{' '}
            <a
              href="https://console.cloud.google.com/"
              target="_blank"
              className="text-info"
            >
              Google Cloud Console
            </a>
          </p>
        </div>
      </div>

      {/* Perplexity */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Perplexity API</h2>
          <button
            onClick={() => handleTest('perplexity')}
            className="text-sm text-info hover:text-blue-700"
            disabled={testing === 'perplexity'}
          >
            {testing === 'perplexity' ? 'Testing...' : 'Test Connection'}
          </button>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            API Key
          </label>
          <input
            type="password"
            value={formData.perplexity?.apiKey || ''}
            onChange={(e) => updateField('perplexity', 'apiKey', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2"
            placeholder="Your Perplexity API key"
          />
          <p className="text-xs text-gray-500 mt-1">
            Pay-as-you-go. Get your key at{' '}
            <a href="https://www.perplexity.ai/settings/api" target="_blank" className="text-info">
              Perplexity Settings
            </a>
          </p>
        </div>
      </div>

      {/* BestTime */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">BestTime.app API</h2>
          <button
            onClick={() => handleTest('besttime')}
            className="text-sm text-info hover:text-blue-700"
            disabled={testing === 'besttime'}
          >
            {testing === 'besttime' ? 'Testing...' : 'Test Connection'}
          </button>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Private Key
            </label>
            <input
              type="password"
              value={formData.besttime?.privateKey || ''}
              onChange={(e) => updateField('besttime', 'privateKey', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              placeholder="pri_..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Public Key
            </label>
            <input
              type="password"
              value={formData.besttime?.publicKey || ''}
              onChange={(e) => updateField('besttime', 'publicKey', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              placeholder="pub_..."
            />
          </div>
          <p className="text-xs text-gray-500">
            Get your keys at{' '}
            <a href="https://besttime.app" target="_blank" className="text-info">
              besttime.app
            </a>
          </p>
        </div>
      </div>

      {/* Autumna */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Autumna Scraping</h2>
        <div className="space-y-4">
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={formData.autumna?.useProxy ?? false}
              onChange={(e) => updateField('autumna', 'useProxy', e.target.checked)}
              className="mr-2"
            />
            <label className="text-sm text-gray-700">Use proxy for scraping</label>
          </div>
          {formData.autumna?.useProxy && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Proxy URL
              </label>
              <input
                type="text"
                value={formData.autumna?.proxyUrl || ''}
                onChange={(e) => updateField('autumna', 'proxyUrl', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                placeholder="http://user:pass@proxy:port"
              />
            </div>
          )}
        </div>
      </div>

      {/* OpenAI */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">OpenAI API</h2>
        <p className="text-sm text-gray-600 mb-4">
          Used for AI-powered analysis of Google Places Insights data for care homes
        </p>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              API Key
            </label>
            <input
              type="password"
              value={formData.openai?.apiKey || ''}
              onChange={(e) => updateField('openai', 'apiKey', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              placeholder="sk-proj-..."
            />
            <p className="mt-1 text-xs text-gray-500">
              Get your API key from <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">OpenAI Platform</a>
            </p>
          </div>
        </div>
      </div>

      {/* Firecrawl */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Firecrawl API</h2>
        <p className="text-sm text-gray-600 mb-4">
          Used for website scraping and analysis of care home websites. Combines with Google Places for unified analysis.
        </p>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              API Key
            </label>
            <input
              type="password"
              value={formData.firecrawl?.apiKey || ''}
              onChange={(e) => updateField('firecrawl', 'apiKey', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              placeholder="fc-..."
            />
            <p className="mt-1 text-xs text-gray-500">
              Get your API key from <a href="https://firecrawl.dev" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Firecrawl.dev</a>
            </p>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={saving}
          className="inline-flex items-center px-6 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-purple-700 disabled:opacity-50"
        >
          <Save className="w-4 h-4 mr-2" />
          {saving ? 'Saving...' : 'Save Credentials'}
        </button>
      </div>
    </div>
  );
}

