import { useState, useEffect } from 'react';
import { Save, CheckCircle2, AlertCircle, Plus, Eye, EyeOff } from 'lucide-react';
import axios from 'axios';
import { useApiStore } from '../stores/apiStore';
import type { ApiCredentials } from '../types/api.types';

export default function ApiConfig() {
  const { credentials, setCredentials } = useApiStore();
  const [formData, setFormData] = useState<ApiCredentials>(credentials || {});
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<Record<string, boolean>>({});
  const [showPasswords, setShowPasswords] = useState<Record<string, boolean>>({});
  const [hasChanges, setHasChanges] = useState(false);

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
          openai: {
            apiKey: creds.openai?.apiKey || '',
          },
          firecrawl: {
            apiKey: creds.firecrawl?.apiKey || '',
          },
        };
        
        setFormData(loadedCreds);
        setCredentials(loadedCreds);
        setHasChanges(false); // Reset changes flag after loading
      }
    } catch (error) {
      console.error('Failed to load credentials:', error);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Convert camelCase to snake_case and filter out empty credentials
      const cleanedData: any = {};
      
      // CQC - snake_case
      if (formData.cqc && (
        formData.cqc.partnerCode?.trim() ||
        formData.cqc.primarySubscriptionKey?.trim() ||
        formData.cqc.secondarySubscriptionKey?.trim() ||
        formData.cqc.useWithoutCode !== undefined
      )) {
        cleanedData.cqc = {
          partnerCode: formData.cqc.partnerCode || '',
          primarySubscriptionKey: formData.cqc.primarySubscriptionKey || '',
          secondarySubscriptionKey: formData.cqc.secondarySubscriptionKey || '',
          useWithoutCode: formData.cqc.useWithoutCode ?? true,
        };
      }
      
      // Companies House - convert to snake_case
      if (formData.companiesHouse?.apiKey?.trim()) {
        cleanedData.companies_house = {
          api_key: formData.companiesHouse.apiKey,
        };
      }
      
      // Google Places - convert to snake_case
      if (formData.googlePlaces?.apiKey?.trim()) {
        cleanedData.google_places = {
          api_key: formData.googlePlaces.apiKey,
        };
      }
      
      // Perplexity - convert to snake_case
      if (formData.perplexity?.apiKey?.trim()) {
        cleanedData.perplexity = {
          api_key: formData.perplexity.apiKey,
        };
      }
      
      // OpenAI - convert to snake_case
      if (formData.openai?.apiKey?.trim()) {
        cleanedData.openai = {
          api_key: formData.openai.apiKey,
        };
      }
      
      // Firecrawl - convert to snake_case
      if (formData.firecrawl?.apiKey?.trim()) {
        cleanedData.firecrawl = {
          api_key: formData.firecrawl.apiKey,
        };
      }
      
      console.log('Saving credentials with snake_case:', Object.keys(cleanedData));
      console.log('Cleaned data structure:', JSON.stringify(cleanedData, null, 2));
      
      // Don't send empty object - require at least one API
      if (Object.keys(cleanedData).length === 0) {
        alert('❌ Please configure at least one API');
        setSaving(false);
        return;
      }
      
      const response = await axios.post('/api/config/credentials', cleanedData);
      console.log('Save response:', response.data);
      
      // Reload credentials from server to ensure they were saved correctly
      await loadCredentials();
      alert('✅ Credentials saved successfully!\n\n' + response.data.message);
    } catch (error: any) {
      console.error('Save error:', error.response?.data || error);
      let errorMessage = 'Unknown error occurred';
      
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        
        if (Array.isArray(detail)) {
          // FastAPI validation errors
          errorMessage = 'Validation errors:\n' + detail
            .map((err: any) => {
              const field = err.loc?.join('.') || 'unknown field';
              return `• ${field}: ${err.msg || 'validation error'}`;
            })
            .join('\n');
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (typeof detail === 'object') {
          errorMessage = detail.message || detail.error || JSON.stringify(detail);
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      console.error('Detailed error:', errorMessage);
      alert(`❌ Save failed:\n\n${errorMessage}`);
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
    setHasChanges(true);
  };

  const togglePasswordVisibility = (fieldId: string) => {
    setShowPasswords({
      ...showPasswords,
      [fieldId]: !showPasswords[fieldId],
    });
  };

  const hasApiKey = (section: keyof ApiCredentials, field: string = 'apiKey'): boolean => {
    const sectionData = formData[section] as any;
    if (!sectionData) return false;
    const value = sectionData[field];
    return value && value.trim().length > 0;
  };

  const getStatusBadge = (hasKey: boolean) => {
    if (hasKey) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          <CheckCircle2 className="w-3 h-3 mr-1" />
          Configured
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
        <AlertCircle className="w-3 h-3 mr-1" />
        Not Configured
      </span>
    );
  };

  const PasswordInput = ({ 
    value, 
    onChange, 
    placeholder, 
    fieldId,
    showToggle = true 
  }: { 
    value: string; 
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void; 
    placeholder: string;
    fieldId: string;
    showToggle?: boolean;
  }) => {
    const isVisible = showPasswords[fieldId] || false;
    return (
      <div className="relative">
        <input
          type={isVisible ? "text" : "password"}
          value={value}
          onChange={onChange}
          className="w-full border border-gray-300 rounded-md px-3 py-2 pr-10"
          placeholder={placeholder}
        />
        {showToggle && (
          <button
            type="button"
            onClick={() => togglePasswordVisibility(fieldId)}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
          >
            {isVisible ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">API Configuration</h1>
        <p className="mt-2 text-gray-600">Configure credentials for all API services</p>
      </div>

      {/* CQC */}
      <div className={`bg-white rounded-lg shadow p-6 border-l-4 ${hasApiKey('cqc', 'primarySubscriptionKey') ? 'border-green-500' : 'border-yellow-500'}`}>
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold">CQC API</h2>
            {getStatusBadge(hasApiKey('cqc', 'primarySubscriptionKey'))}
          </div>
          <button
            onClick={() => handleTest('cqc')}
            className="text-sm text-blue-600 hover:text-blue-700 disabled:opacity-50"
            disabled={testing === 'cqc' || !hasApiKey('cqc', 'primarySubscriptionKey')}
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
            <PasswordInput
              value={formData.cqc?.primarySubscriptionKey || ''}
              onChange={(e) => updateField('cqc', 'primarySubscriptionKey', e.target.value)}
              placeholder="Enter your Primary Subscription Key"
              fieldId="cqc-primary"
            />
            <p className="text-xs text-gray-500 mt-1">
              Required for new CQC API. Get it from your API Portal profile.
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Secondary Subscription Key (Optional)
            </label>
            <PasswordInput
              value={formData.cqc?.secondarySubscriptionKey || ''}
              onChange={(e) => updateField('cqc', 'secondarySubscriptionKey', e.target.value)}
              placeholder="Enter your Secondary Subscription Key (optional)"
              fieldId="cqc-secondary"
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
      <div className={`bg-white rounded-lg shadow p-6 border-l-4 ${hasApiKey('companiesHouse') ? 'border-green-500' : 'border-yellow-500'}`}>
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold">Companies House API</h2>
            {getStatusBadge(hasApiKey('companiesHouse'))}
          </div>
          <button
            onClick={() => handleTest('companies_house')}
            className="text-sm text-blue-600 hover:text-blue-700 disabled:opacity-50"
            disabled={testing === 'companies_house' || !hasApiKey('companiesHouse')}
          >
            {testing === 'companies_house' ? 'Testing...' : 'Test Connection'}
          </button>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            API Key {!hasApiKey('companiesHouse') && <span className="text-red-500">*</span>}
          </label>
          <PasswordInput
            value={formData.companiesHouse?.apiKey || ''}
            onChange={(e) => updateField('companiesHouse', 'apiKey', e.target.value)}
            placeholder="Enter your Companies House API key"
            fieldId="companies-house"
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
      <div className={`bg-white rounded-lg shadow p-6 border-l-4 ${hasApiKey('googlePlaces') ? 'border-green-500' : 'border-yellow-500'}`}>
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold">Google Places API</h2>
            {getStatusBadge(hasApiKey('googlePlaces'))}
          </div>
          <button
            onClick={() => handleTest('google_places')}
            className="text-sm text-blue-600 hover:text-blue-700 disabled:opacity-50"
            disabled={testing === 'google_places' || !hasApiKey('googlePlaces')}
          >
            {testing === 'google_places' ? 'Testing...' : 'Test Connection'}
          </button>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            API Key {!hasApiKey('googlePlaces') && <span className="text-red-500">*</span>}
          </label>
          <PasswordInput
            value={formData.googlePlaces?.apiKey || ''}
            onChange={(e) => updateField('googlePlaces', 'apiKey', e.target.value)}
            placeholder="Enter your Google Places API key"
            fieldId="google-places"
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
      <div className={`bg-white rounded-lg shadow p-6 border-l-4 ${hasApiKey('perplexity') ? 'border-green-500' : 'border-yellow-500'}`}>
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold">Perplexity API</h2>
            {getStatusBadge(hasApiKey('perplexity'))}
          </div>
          <button
            onClick={() => handleTest('perplexity')}
            className="text-sm text-blue-600 hover:text-blue-700 disabled:opacity-50"
            disabled={testing === 'perplexity' || !hasApiKey('perplexity')}
          >
            {testing === 'perplexity' ? 'Testing...' : 'Test Connection'}
          </button>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            API Key {!hasApiKey('perplexity') && <span className="text-red-500">*</span>}
          </label>
          <PasswordInput
            value={formData.perplexity?.apiKey || ''}
            onChange={(e) => updateField('perplexity', 'apiKey', e.target.value)}
            placeholder="Enter your Perplexity API key"
            fieldId="perplexity"
          />
          <p className="text-xs text-gray-500 mt-1">
            Pay-as-you-go. Get your key at{' '}
            <a href="https://www.perplexity.ai/settings/api" target="_blank" className="text-info">
              Perplexity Settings
            </a>
          </p>
        </div>
      </div>

      {/* OpenAI */}
      <div className={`bg-white rounded-lg shadow p-6 border-l-4 ${hasApiKey('openai') ? 'border-green-500' : 'border-yellow-500'}`}>
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold">OpenAI API</h2>
            {getStatusBadge(hasApiKey('openai'))}
          </div>
        </div>
        <p className="text-sm text-gray-600 mb-4">
          Used for AI-powered insights in Funding Calculator and Professional Report analysis
        </p>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              API Key {!hasApiKey('openai') && <span className="text-red-500">*</span>}
            </label>
            <PasswordInput
              value={formData.openai?.apiKey || ''}
              onChange={(e) => updateField('openai', 'apiKey', e.target.value)}
              placeholder="Enter your OpenAI API key (sk-...)"
              fieldId="openai"
            />
            <p className="mt-1 text-xs text-gray-500">
              Get your API key from <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">OpenAI Platform</a>
            </p>
          </div>
        </div>
      </div>

      {/* Firecrawl */}
      <div className={`bg-white rounded-lg shadow p-6 border-l-4 ${hasApiKey('firecrawl') ? 'border-green-500' : 'border-yellow-500'}`}>
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold">Firecrawl API</h2>
            {getStatusBadge(hasApiKey('firecrawl'))}
          </div>
        </div>
        <p className="text-sm text-gray-600 mb-4">
          Used for website scraping and analysis of care home websites. Combines with Google Places for unified analysis.
        </p>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              API Key {!hasApiKey('firecrawl') && <span className="text-red-500">*</span>}
            </label>
            <PasswordInput
              value={formData.firecrawl?.apiKey || ''}
              onChange={(e) => updateField('firecrawl', 'apiKey', e.target.value)}
              placeholder="Enter your Firecrawl API key (fc-...)"
              fieldId="firecrawl"
            />
            <p className="mt-1 text-xs text-gray-500">
              Get your API key from <a href="https://firecrawl.dev" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Firecrawl.dev</a>
            </p>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-between items-center bg-white rounded-lg shadow p-6 border-t-4 border-blue-500">
        <div>
          {hasChanges && (
            <p className="text-sm text-yellow-600 flex items-center">
              <AlertCircle className="w-4 h-4 mr-1" />
              You have unsaved changes
            </p>
          )}
          {!hasChanges && (
            <p className="text-sm text-green-600 flex items-center">
              <CheckCircle2 className="w-4 h-4 mr-1" />
              All changes saved
            </p>
          )}
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="inline-flex items-center px-6 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Save className="w-4 h-4 mr-2" />
          {saving ? 'Saving...' : 'Save All Credentials'}
        </button>
      </div>
    </div>
  );
}

