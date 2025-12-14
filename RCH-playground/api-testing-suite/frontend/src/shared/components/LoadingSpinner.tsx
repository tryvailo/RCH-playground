import { Loader2 } from 'lucide-react';

type SpinnerSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

interface LoadingSpinnerProps {
  label?: string;
  size?: SpinnerSize;
  className?: string;
  inline?: boolean;
}

const sizeClasses: Record<SpinnerSize, string> = {
  xs: 'w-3 h-3',
  sm: 'w-4 h-4',
  md: 'w-5 h-5',
  lg: 'w-6 h-6',
  xl: 'w-8 h-8',
};

const textSizeClasses: Record<SpinnerSize, string> = {
  xs: 'text-xs',
  sm: 'text-sm',
  md: 'text-sm',
  lg: 'text-base',
  xl: 'text-lg',
};

export function LoadingSpinner({
  label,
  size = 'md',
  className = '',
  inline = false,
}: LoadingSpinnerProps) {
  const containerClass = inline
    ? 'inline-flex items-center gap-2'
    : 'flex items-center justify-center gap-2';

  return (
    <div className={`${containerClass} text-gray-600 ${className}`}>
      <Loader2 className={`${sizeClasses[size]} animate-spin`} />
      {label && <span className={textSizeClasses[size]}>{label}</span>}
    </div>
  );
}

export default LoadingSpinner;
