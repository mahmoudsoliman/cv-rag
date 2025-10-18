import { AlertCircle, X } from 'lucide-react';

interface ErrorBannerProps {
  message: string;
  onRetry: () => void;
  onDismiss: () => void;
}

export function ErrorBanner({ message, onRetry, onDismiss }: ErrorBannerProps) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start justify-between gap-4">
      <div className="flex items-start gap-3 flex-1">
        <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-red-900 mb-1">Error</h3>
          <p className="text-sm text-red-700">{message}</p>
          <button
            onClick={onRetry}
            className="mt-2 text-sm font-medium text-red-600 hover:text-red-700 underline"
          >
            Try again
          </button>
        </div>
      </div>
      <button
        onClick={onDismiss}
        aria-label="Dismiss error"
        className="p-1 hover:bg-red-100 rounded transition-colors"
      >
        <X className="w-4 h-4 text-red-600" />
      </button>
    </div>
  );
}
