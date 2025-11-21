import React, { useState } from 'react';
import { 
  Home, 
  Building2, 
  DollarSign, 
  BarChart3, 
  AlertTriangle, 
  FileText,
  ChevronRight,
  ChevronDown
} from 'lucide-react';

interface Section {
  id: string;
  label: string;
  icon: React.ReactNode;
  hasData: boolean;
}

interface ReportNavigationProps {
  sections: Section[];
  activeSection: string;
  onSectionClick: (sectionId: string) => void;
}

export default function ReportNavigation({ sections, activeSection, onSectionClick }: ReportNavigationProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm sticky top-4">
      <div 
        className="p-3 border-b border-gray-200 cursor-pointer flex items-center justify-between"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <h3 className="text-sm font-semibold text-gray-900">Report Sections</h3>
        {isExpanded ? (
          <ChevronDown className="w-4 h-4 text-gray-500" />
        ) : (
          <ChevronRight className="w-4 h-4 text-gray-500" />
        )}
      </div>
      
      {isExpanded && (
        <nav className="p-2">
          <ul className="space-y-1">
            {sections.map((section) => (
              <li key={section.id}>
                <button
                  onClick={() => onSectionClick(section.id)}
                  className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                    activeSection === section.id
                      ? 'bg-blue-50 text-blue-700 font-semibold'
                      : 'text-gray-700 hover:bg-gray-50'
                  } ${!section.hasData ? 'opacity-50' : ''}`}
                >
                  <span className={`${activeSection === section.id ? 'text-blue-600' : 'text-gray-500'}`}>
                    {section.icon}
                  </span>
                  <span className="flex-1 text-left">{section.label}</span>
                  {!section.hasData && (
                    <span className="text-xs text-gray-400">N/A</span>
                  )}
                </button>
              </li>
            ))}
          </ul>
        </nav>
      )}
    </div>
  );
}

