import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Home, Settings, Play, BarChart3, Search, MapPin, Building2, Sparkles, Shield, Globe, Database, Calculator, Heart, FileText, Award, List, Navigation, Map, Users } from 'lucide-react';
import CookieConsentBanner from './CookieConsentBanner';
import CookieConsentButton from './CookieConsentButton';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();
  const navigate = useNavigate();

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/config', icon: Settings, label: 'API Config' },
    { path: '/test', icon: Play, label: 'Test Runner' },
    { path: '/cqc', icon: Search, label: 'CQC Explorer' },
    { path: '/fsa', icon: Shield, label: 'FSA Explorer' },
    { path: '/google-places', icon: MapPin, label: 'Google Places' },
    { path: '/companies-house', icon: Building2, label: 'Companies House' },
    { path: '/perplexity', icon: Sparkles, label: 'Perplexity' },
    { path: '/firecrawl', icon: Globe, label: 'Firecrawl' },
    { path: '/firecrawl-search', icon: Search, label: 'Firecrawl Search' },
    { path: '/analytics', icon: BarChart3, label: 'Analytics' },
    // RCH-data modules
    { path: '/data-ingestion', icon: Database, label: 'Data Admin' },
    { path: '/all-locations', icon: List, label: 'All Locations' },
    { path: '/postcode-calculator', icon: Calculator, label: 'Postcode Calculator' },
    { path: '/price-calculator', icon: Calculator, label: 'Price Calculator' },
    { path: '/postcode-tester', icon: Navigation, label: 'Postcode Tester' },
    { path: '/funding-calculator', icon: Heart, label: 'Funding Calculator' },
    { path: '/neighbourhood', icon: Map, label: 'Neighbourhood' },
    { path: '/staff-quality', icon: Users, label: 'Staff Quality Data' },
    // Reports
    { path: '/free-report', icon: FileText, label: 'Free Report' },
    { path: '/professional-report', icon: Award, label: 'Professional Report' },
  ];

  // Split nav items into rows
  const firstRow = navItems.slice(0, 6); // First 6 items
  const secondRow = navItems.slice(6, 12); // Next 6 items
  const thirdRow = navItems.slice(12, 18); // RCH-data modules (Data Admin, All Locations, Postcode Calculator, Price Calculator, Postcode Tester, Funding Calculator)
  const fourthRow = navItems.slice(18); // Reports (Free Report, Professional Report)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-2">
            {/* Title */}
            <div className="flex items-center mb-2">
              <h1 className="text-xl font-bold text-primary">RightCareHome API Testing</h1>
            </div>
            {/* Navigation Rows */}
            <div className="hidden sm:block">
              {/* First Row */}
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mb-1">
                {firstRow.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path;
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`inline-flex items-center px-2 py-1 border-b-2 text-sm font-medium ${
                        isActive
                          ? 'border-primary text-gray-900'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                    >
                      <Icon className="w-4 h-4 mr-1.5" />
                      {item.label}
                    </Link>
                  );
                })}
              </div>
              {/* Second Row */}
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mb-1">
                {secondRow.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path;
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`inline-flex items-center px-2 py-1 border-b-2 text-sm font-medium ${
                        isActive
                          ? 'border-primary text-gray-900'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                    >
                      <Icon className="w-4 h-4 mr-1.5" />
                      {item.label}
                    </Link>
                  );
                })}
              </div>
              {/* Third Row - RCH-data modules */}
              {thirdRow.length > 0 && (
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 border-t pt-1 mt-1">
                  {thirdRow.map((item) => {
                    const Icon = item.icon;
                    const isActive = location.pathname === item.path;
                    return (
                      <Link
                        key={item.path}
                        to={item.path}
                        className={`inline-flex items-center px-2 py-1 border-b-2 text-sm font-medium ${
                          isActive
                            ? 'border-primary text-gray-900'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`}
                      >
                        <Icon className="w-4 h-4 mr-1.5" />
                        {item.label}
                      </Link>
                    );
                  })}
                </div>
              )}
              {/* Fourth Row - Reports */}
              {fourthRow.length > 0 && (
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 border-t pt-1 mt-1">
                  {fourthRow.map((item) => {
                    const Icon = item.icon;
                    const isActive = location.pathname === item.path;
                    return (
                      <Link
                        key={item.path}
                        to={item.path}
                        className={`inline-flex items-center px-2 py-1 border-b-2 text-sm font-medium ${
                          isActive
                            ? 'border-primary text-gray-900'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`}
                      >
                        <Icon className="w-4 h-4 mr-1.5" />
                        {item.label}
                      </Link>
                    );
                  })}
                </div>
              )}
            </div>
            {/* Mobile menu */}
            <div className="sm:hidden">
              <select
                value={location.pathname}
                onChange={(e) => navigate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                {navItems.map((item) => (
                  <option key={item.path} value={item.path}>
                    {item.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Cookie Consent Banner */}
      <CookieConsentBanner />
      
      {/* Cookie Consent Button (floating) */}
      <CookieConsentButton />
    </div>
  );
}

