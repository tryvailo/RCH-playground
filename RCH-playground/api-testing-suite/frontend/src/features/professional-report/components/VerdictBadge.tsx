import React from 'react';
import { Award, CheckCircle2, ThumbsUp, AlertCircle } from 'lucide-react';

interface VerdictBadgeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  showScore?: boolean;
}

interface VerdictInfo {
  label: string;
  color: string;
  bgClass: string;
  borderClass: string;
  icon: React.ReactNode;
  description: string;
}

const getVerdictInfo = (score: number): VerdictInfo => {
  if (score >= 85) {
    return {
      label: 'Excellent Match',
      color: 'text-green-800',
      bgClass: 'bg-gradient-to-r from-green-100 to-emerald-100',
      borderClass: 'border-green-300',
      icon: <Award className="w-5 h-5 text-green-600" />,
      description: 'Highly recommended based on your requirements'
    };
  } else if (score >= 70) {
    return {
      label: 'Good Match',
      color: 'text-blue-800',
      bgClass: 'bg-gradient-to-r from-blue-100 to-indigo-100',
      borderClass: 'border-blue-300',
      icon: <ThumbsUp className="w-5 h-5 text-blue-600" />,
      description: 'Meets most of your requirements'
    };
  } else if (score >= 50) {
    return {
      label: 'Fair Match',
      color: 'text-yellow-800',
      bgClass: 'bg-gradient-to-r from-yellow-100 to-amber-100',
      borderClass: 'border-yellow-300',
      icon: <CheckCircle2 className="w-5 h-5 text-yellow-600" />,
      description: 'Consider carefully - some requirements may not be fully met'
    };
  } else {
    return {
      label: 'Limited Match',
      color: 'text-orange-800',
      bgClass: 'bg-gradient-to-r from-orange-100 to-red-100',
      borderClass: 'border-orange-300',
      icon: <AlertCircle className="w-5 h-5 text-orange-600" />,
      description: 'May not fully meet your requirements'
    };
  }
};

const getSizeClasses = (size: 'sm' | 'md' | 'lg') => {
  switch (size) {
    case 'sm':
      return {
        container: 'px-3 py-1.5',
        text: 'text-sm',
        icon: 'w-4 h-4',
        score: 'text-xs'
      };
    case 'md':
      return {
        container: 'px-4 py-2',
        text: 'text-base',
        icon: 'w-5 h-5',
        score: 'text-sm'
      };
    case 'lg':
      return {
        container: 'px-6 py-3',
        text: 'text-lg',
        icon: 'w-6 h-6',
        score: 'text-base'
      };
  }
};

export default function VerdictBadge({ 
  score, 
  size = 'md', 
  showIcon = true,
  showScore = true 
}: VerdictBadgeProps) {
  const verdict = getVerdictInfo(score);
  const sizeClasses = getSizeClasses(size);

  return (
    <div
      className={`inline-flex items-center gap-2 rounded-full border-2 font-semibold ${verdict.bgClass} ${verdict.borderClass} ${sizeClasses.container}`}
      title={verdict.description}
    >
      {showIcon && (
        <span className={sizeClasses.icon}>
          {verdict.icon}
        </span>
      )}
      <span className={`${verdict.color} ${sizeClasses.text}`}>
        {verdict.label}
      </span>
      {showScore && (
        <span className={`${verdict.color} ${sizeClasses.score} opacity-75`}>
          ({score.toFixed(0)}%)
        </span>
      )}
    </div>
  );
}

// Export utility function for use in other components
export { getVerdictInfo };
