import { Clock } from 'lucide-react';
import { HistoryItem } from '../types';

interface HistoryListProps {
  history: HistoryItem[];
  onSelect: (question: string) => void;
}

export function HistoryList({ history, onSelect }: HistoryListProps) {
  if (history.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-4">
      <div className="flex items-center gap-2 mb-3">
        <Clock className="w-4 h-4 text-slate-500" />
        <h3 className="text-sm font-semibold text-slate-900">Recent Questions</h3>
      </div>
      <div className="space-y-2">
        {history.slice(0, 5).map((item) => (
          <button
            key={item.id}
            onClick={() => onSelect(item.question)}
            className="w-full text-left px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 rounded-md transition-colors line-clamp-2"
          >
            {item.question}
          </button>
        ))}
      </div>
    </div>
  );
}
