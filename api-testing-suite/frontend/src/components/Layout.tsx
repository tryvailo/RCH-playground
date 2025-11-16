import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Home, Settings, Play, BarChart3, Search, MapPin, Building2, Sparkles, Shield, Globe } from 'lucide-react';

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
  ];

  // Split nav items into two rows
  const firstRow = navItems.slice(0, 6); // First 6 items
  const secondRow = navItems.slice(6); // Remaining items

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
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
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
    </div>
  );
}

