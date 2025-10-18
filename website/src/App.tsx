import { useState, useCallback } from 'react';
import { AppShell } from './components/AppShell';
import { QueryForm } from './components/QueryForm';
import { AnswerPanel } from './components/AnswerPanel';
import { EvidencePanel } from './components/EvidencePanel';
import { HistoryList } from './components/HistoryList';
import { ErrorBanner } from './components/ErrorBanner';
import { askQuestion } from './api';
import { AskResponse, HistoryItem } from './types';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [response, setResponse] = useState<AskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [startTime, setStartTime] = useState<number | null>(null);

  const handleSubmit = useCallback(async (question: string) => {
    setCurrentQuestion(question);
    setIsLoading(true);
    setError(null);
    setStartTime(Date.now());

    try {
      const result = await askQuestion(question);
      setResponse(result);

      const historyItem: HistoryItem = {
        id: Date.now().toString(),
        question,
        timestamp: Date.now(),
        response: result,
      };

      setHistory((prev) => [historyItem, ...prev]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleRetry = useCallback(() => {
    if (currentQuestion) {
      handleSubmit(currentQuestion);
    }
  }, [currentQuestion, handleSubmit]);

  const handleHistorySelect = useCallback((question: string) => {
    handleSubmit(question);
  }, [handleSubmit]);

  const elapsedMs = startTime && !isLoading ? Date.now() - startTime : undefined;

  return (
    <AppShell>
      <div className="flex gap-8">
        <div className="flex-1 max-w-3xl space-y-6">
          <QueryForm onSubmit={handleSubmit} isLoading={isLoading} />

          {error && (
            <ErrorBanner
              message={error}
              onRetry={handleRetry}
              onDismiss={() => setError(null)}
            />
          )}

          {isLoading && (
            <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                <span className="text-slate-600" aria-live="polite">
                  Finding answers...
                </span>
              </div>
            </div>
          )}

          {response && response.answer && !isLoading && (
            <>
              <AnswerPanel
                answer={response.answer}
                elapsedMs={elapsedMs}
                sections={response.sections}
              />
              <EvidencePanel facts={response.facts} snippets={response.docs} />
            </>
          )}
        </div>

        <aside className="hidden lg:block w-80 flex-shrink-0 space-y-6">
          <HistoryList history={history} onSelect={handleHistorySelect} />

          {response && (
            <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-4">
              <h3 className="text-sm font-semibold text-slate-900 mb-3">Query Info</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-600">Response time:</span>
                  <span className="font-medium text-slate-900">
                    {elapsedMs ? `${elapsedMs}ms` : '-'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Facts found:</span>
                  <span className="font-medium text-slate-900">{response.facts.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Snippets found:</span>
                  <span className="font-medium text-slate-900">{response.docs.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Sections used:</span>
                  <span className="font-medium text-slate-900">{response.sections.length}</span>
                </div>
              </div>
            </div>
          )}
        </aside>
      </div>
    </AppShell>
  );
}

export default App;
