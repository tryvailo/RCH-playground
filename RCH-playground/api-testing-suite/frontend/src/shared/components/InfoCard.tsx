import type { ReactNode } from 'react';

interface InfoCardProps {
  icon?: ReactNode;
  title: string;
  items: string[];
  className?: string;
}

export function InfoCard({ icon, title, items, className = '' }: InfoCardProps) {
  return (
    <div className={`bg-white rounded-lg p-4 shadow-sm ${className}`}>
      <div className="flex items-center gap-2 mb-3">
        {icon}
        <span className="font-medium">{title}</span>
      </div>
      <ul className="text-sm text-gray-600 space-y-1">
        {items.map((item, i) => (
          <li key={i} className="flex items-center gap-2">
            <span className="w-1 h-1 bg-gray-400 rounded-full flex-shrink-0" />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default InfoCard;
