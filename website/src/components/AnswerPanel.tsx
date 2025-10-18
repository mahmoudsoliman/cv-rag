import { Copy, Check } from 'lucide-react';
import { useState } from 'react';

interface AnswerPanelProps {
  answer: string;
  elapsedMs?: number;
  sections: string[];
}

export function AnswerPanel({ answer, elapsedMs, sections }: AnswerPanelProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(answer);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-sm">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Answer</h2>
          <p className="text-xs text-slate-500 mt-1">
            {elapsedMs && `${elapsedMs}ms`} · Sections: {sections.join(', ')}
          </p>
        </div>
        <button
          onClick={handleCopy}
          aria-label="Copy answer"
          className="p-2 hover:bg-slate-100 rounded-md transition-colors"
        >
          {copied ? (
            <Check className="w-4 h-4 text-green-600" />
          ) : (
            <Copy className="w-4 h-4 text-slate-500" />
          )}
        </button>
      </div>
      <div
        className="prose prose-slate max-w-none prose-p:leading-relaxed prose-headings:mb-2 prose-headings:mt-4"
        dangerouslySetInnerHTML={{ __html: formatMarkdown(answer) }}
      />
    </div>
  );
}

function formatMarkdown(text: string): string {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/^(.+)$/gm, '<p>$1</p>')
    .replace(/<\/p><p>/g, '</p>\n<p>');
}
