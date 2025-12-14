import type { ApiStatus } from '../types/api.types';
import { CheckCircle, XCircle, Loader, AlertCircle } from 'lucide-react';

interface StatusBadgeProps {
  status: ApiStatus;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const config = {
    connected: {
      icon: CheckCircle,
      color: 'text-success',
      bg: 'bg-success/10',
      label: 'Connected',
    },
    disconnected: {
      icon: XCircle,
      color: 'text-danger',
      bg: 'bg-danger/10',
      label: 'Disconnected',
    },
    testing: {
      icon: Loader,
      color: 'text-primary',
      bg: 'bg-primary/10',
      label: 'Testing',
    },
    error: {
      icon: AlertCircle,
      color: 'text-danger',
      bg: 'bg-danger/10',
      label: 'Error',
    },
  };

  const { icon: Icon, color, bg, label } = config[status];

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${bg} ${color}`}>
      <Icon className="w-3 h-3 mr-1" />
      {label}
    </span>
  );
}

