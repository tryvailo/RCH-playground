import { ChevronDown, ChevronUp } from 'lucide-react';
import type { ReactNode } from 'react';

export type CollapsibleColor = 'gray' | 'blue' | 'purple' | 'green' | 'red' | 'orange';

interface CollapsibleSectionProps {
  title: string;
  icon?: ReactNode;
  color?: CollapsibleColor;
  badge?: ReactNode;
  expanded: boolean;
  onToggle: () => void;
  children: ReactNode;
  className?: string;
}

const headerColors: Record<CollapsibleColor, string> = {
  gray: 'bg-gray-50 hover:bg-gray-100',
  blue: 'bg-blue-50 hover:bg-blue-100',
  purple: 'bg-purple-50 hover:bg-purple-100',
  green: 'bg-green-50 hover:bg-green-100',
  red: 'bg-red-50 hover:bg-red-100',
  orange: 'bg-orange-50 hover:bg-orange-100',
};

export function CollapsibleSection({
  title,
  icon,
  color = 'gray',
  badge,
  expanded,
  onToggle,
  children,
  className = '',
}: CollapsibleSectionProps) {
  return (
    <div className={`bg-white rounded-lg shadow overflow-hidden ${className}`}>
      <button
        onClick={onToggle}
        className={`w-full px-6 py-4 flex items-center justify-between ${headerColors[color]} transition-colors`}
      >
        <div className="flex items-center gap-2">
          {icon}
          <span className="font-semibold text-gray-900">{title}</span>
        </div>
        <div className="flex items-center gap-4">
          {badge}
          {expanded ? (
            <ChevronUp className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          )}
        </div>
      </button>

      {expanded && <div className="p-6 border-t">{children}</div>}
    </div>
  );
}

export default CollapsibleSection;
