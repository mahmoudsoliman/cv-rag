import { useState, FormEvent, KeyboardEvent } from 'react';
import { Send } from 'lucide-react';

interface QueryFormProps {
  onSubmit: (question: string) => void;
  isLoading: boolean;
}

export function QueryForm({ onSubmit, isLoading }: QueryFormProps) {
  const [question, setQuestion] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (question.trim() && !isLoading) {
      onSubmit(question.trim());
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (question.trim() && !isLoading) {
        onSubmit(question.trim());
      }
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about resumes..."
          disabled={isLoading}
          aria-label="Question input"
          className="w-full px-6 py-4 text-lg border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-slate-100 disabled:text-slate-500"
        />
        <button
          type="submit"
          disabled={!question.trim() || isLoading}
          aria-label="Submit question"
          className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-md bg-blue-600 text-white hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </button>
      </div>
    </form>
  );
}
