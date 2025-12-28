'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <main className="container mx-auto px-4 py-16 max-w-4xl">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 md:p-12">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
              RCH Admin Playground
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300">
              Next.js Migration - Care Reports API
            </p>
          </div>

          {/* Status Badge */}
          <div className="flex justify-center mb-8">
            <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
              API Server Running
            </span>
          </div>

          {/* API Endpoints */}
          <div className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              API Endpoints
            </h2>
            <div className="space-y-4">
              <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      Free Report API
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      Generate free care home matching report
                    </p>
                    <code className="text-xs text-blue-600 dark:text-blue-400 mt-2 block">
                      POST /api/free-report
                    </code>
                  </div>
                  <Link
                    href="/api/free-report"
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                  >
                    Test
                  </Link>
                </div>
              </div>

              <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      Professional Report API
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      Generate professional care home matching report with enrichment
                    </p>
                    <code className="text-xs text-blue-600 dark:text-blue-400 mt-2 block">
                      POST /api/professional-report
                    </code>
                  </div>
                  <Link
                    href="/api/professional-report"
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium"
                  >
                    Test
                  </Link>
                </div>
              </div>
            </div>
          </div>

          {/* Migration Status */}
          <div className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              Migration Status
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                <h3 className="font-semibold text-green-900 dark:text-green-200 mb-2">
                  ✅ Completed
                </h3>
                <ul className="text-sm text-green-800 dark:text-green-300 space-y-1">
                  <li>• Data Engine Core</li>
                  <li>• Free Report</li>
                  <li>• Professional Report</li>
                  <li>• Enrichment Services (6 services)</li>
                  <li>• Enrichment Orchestrator</li>
                </ul>
              </div>
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 dark:text-blue-200 mb-2">
                  📋 Features
                </h3>
                <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1">
                  <li>• TypeScript/Next.js</li>
                  <li>• Modular Architecture</li>
                  <li>• Error Handling</li>
                  <li>• Structured Logging</li>
                  <li>• Feature Flags</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Documentation
            </h2>
            <div className="flex flex-wrap gap-3">
              <a
                href="https://nextjs.org/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-sm"
              >
                Next.js Docs
              </a>
              <a
                href="https://vercel.com/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-sm"
              >
                Vercel Docs
              </a>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700 text-center text-sm text-gray-500 dark:text-gray-400">
            <p>Next.js Migration - Parallel Implementation</p>
            <p className="mt-1">Server running on http://localhost:3000</p>
          </div>
        </div>
      </main>
    </div>
  );
}
