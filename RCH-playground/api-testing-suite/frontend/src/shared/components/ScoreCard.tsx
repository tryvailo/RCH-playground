import type { ReactNode } from 'react';

export type ScoreCardColor = 'gray' | 'blue' | 'purple' | 'green' | 'red' | 'orange' | 'pink';

interface ScoreCardProps {
  title: string;
  score?: number | string;
  maxScore?: number;
  suffix?: string;
  color?: ScoreCardColor;
  icon?: ReactNode;
  subtitle?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const colorClasses: Record<ScoreCardColor, string> = {
  gray: 'bg-gray-50 text-gray-600',
  blue: 'bg-blue-50 text-blue-600',
  purple: 'bg-purple-50 text-purple-600',
  green: 'bg-green-50 text-green-600',
  red: 'bg-red-50 text-red-600',
  orange: 'bg-orange-50 text-orange-600',
  pink: 'bg-pink-50 text-pink-600',
};

const sizeClasses = {
  sm: {
    container: 'p-3',
    title: 'text-xs',
    score: 'text-lg',
    maxScore: 'text-xs',
  },
  md: {
    container: 'p-4',
    title: 'text-sm',
    score: 'text-2xl',
    maxScore: 'text-sm',
  },
  lg: {
    container: 'p-6',
    title: 'text-base',
    score: 'text-4xl',
    maxScore: 'text-lg',
  },
};

export function ScoreCard({
  title,
  score,
  maxScore,
  suffix = '',
  color = 'gray',
  icon,
  subtitle,
  size = 'md',
  className = '',
}: ScoreCardProps) {
  const sizes = sizeClasses[size];

  return (
    <div className={`rounded-lg ${sizes.container} ${colorClasses[color]} ${className}`}>
      <div className={`${sizes.title} mb-1 flex items-center gap-2`}>
        {icon}
        <span>{title}</span>
      </div>
      <div className={`${sizes.score} font-bold`}>
        {score !== undefined ? `${score}${suffix}` : 'N/A'}
        {maxScore !== undefined && (
          <span className={`${sizes.maxScore} font-normal`}>/{maxScore}</span>
        )}
      </div>
      {subtitle && <div className="text-xs mt-1 opacity-75">{subtitle}</div>}
    </div>
  );
}

export default ScoreCard;
