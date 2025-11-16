import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
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
import Layout from './components/Layout';

function App() {
  return (
    <BrowserRouter>
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
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;

