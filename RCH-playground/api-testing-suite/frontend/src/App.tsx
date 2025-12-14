import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from './pages/Dashboard';
import ApiConfig from './pages/ApiConfig';
import TestRunner from './pages/TestRunner';
import Results from './pages/Results';
import Analytics from './pages/Analytics';
import CQCExplorer from './pages/CQCExplorer';
import GooglePlacesExplorer from './pages/GooglePlacesExplorer';
import CompaniesHouseExplorer from './pages/CompaniesHouseExplorer';
import PerplexityExplorer from './pages/PerplexityExplorer';
import FSAExplorer from './pages/FSAExplorer';
import FirecrawlExplorer from './pages/FirecrawlExplorer';
import FirecrawlSearchExplorer from './pages/FirecrawlSearchExplorer';
import DataIngestionAdmin from './pages/DataIngestionAdmin';
import PriceCalculator from './pages/PriceCalculator';
import FundingCalculator from './pages/FundingCalculator';
import FreeReportViewer from './features/free-report/FreeReportViewer';
import ProfessionalReportViewer from './features/professional-report/ProfessionalReportViewer';
import NeighbourhoodExplorer from './features/neighbourhood/NeighbourhoodExplorer';
import AllLocations from './pages/AllLocations';
import PostcodeCalculator from './pages/PostcodeCalculator';
import PostcodeTester from './pages/PostcodeTester';
import StaffQualityData from './pages/StaffQualityData';
import TermsOfService from './pages/TermsOfService';
import PrivacyPolicy from './pages/PrivacyPolicy';
import RefundPolicy from './pages/RefundPolicy';
import Layout from './components/Layout';

// Create a QueryClient instance
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 1000 * 60 * 5, // 5 minutes
    },
    mutations: {
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/config" element={<ApiConfig />} />
          <Route path="/test" element={<TestRunner />} />
          <Route path="/results/:jobId" element={<Results />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/cqc" element={<CQCExplorer />} />
          <Route path="/google-places" element={<GooglePlacesExplorer />} />
          <Route path="/companies-house" element={<CompaniesHouseExplorer />} />
          <Route path="/perplexity" element={<PerplexityExplorer />} />
          <Route path="/fsa" element={<FSAExplorer />} />
          <Route path="/firecrawl" element={<FirecrawlExplorer />} />
          <Route path="/firecrawl-search" element={<FirecrawlSearchExplorer />} />
            <Route path="/data-ingestion" element={<DataIngestionAdmin />} />
            <Route path="/price-calculator" element={<PriceCalculator />} />
            <Route path="/funding-calculator" element={<FundingCalculator />} />
            <Route path="/neighbourhood" element={<NeighbourhoodExplorer />} />
            <Route path="/free-report" element={<FreeReportViewer />} />
            <Route path="/professional-report" element={<ProfessionalReportViewer />} />
            <Route path="/all-locations" element={<AllLocations />} />
            <Route path="/postcode-calculator" element={<PostcodeCalculator />} />
            <Route path="/postcode-tester" element={<PostcodeTester />} />
            <Route path="/staff-quality" element={<StaffQualityData />} />
            <Route path="/terms-of-service" element={<TermsOfService />} />
            <Route path="/privacy-policy" element={<PrivacyPolicy />} />
            <Route path="/refund-policy" element={<RefundPolicy />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;

