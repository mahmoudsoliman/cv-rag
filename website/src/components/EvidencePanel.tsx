import { useState } from 'react';
import { ChevronDown, ChevronRight, MapPin, Briefcase, GraduationCap, Award } from 'lucide-react';
import { CandidateProfile, Snippet } from '../types';

interface EvidencePanelProps {
  facts: CandidateProfile[];
  snippets: Snippet[];
}

export function EvidencePanel({ facts, snippets }: EvidencePanelProps) {
  const [factsOpen, setFactsOpen] = useState(false);
  const [snippetsOpen, setSnippetsOpen] = useState(false);
  const [expandedSnippets, setExpandedSnippets] = useState<Set<number>>(new Set());

  const toggleSnippet = (index: number) => {
    const newExpanded = new Set(expandedSnippets);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedSnippets(newExpanded);
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
      <div className="border-b border-slate-200">
        <button
          onClick={() => setFactsOpen(!factsOpen)}
          className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors"
          aria-expanded={factsOpen}
        >
          <h3 className="text-base font-semibold text-slate-900">
            Facts (SQL) · {facts.length}
          </h3>
          {factsOpen ? (
            <ChevronDown className="w-5 h-5 text-slate-500" />
          ) : (
            <ChevronRight className="w-5 h-5 text-slate-500" />
          )}
        </button>
        {factsOpen && (
          <div className="px-6 pb-6 space-y-4">
            {facts.map((fact, idx) => (
              <CandidateCard key={idx} candidate={fact} />
            ))}
          </div>
        )}
      </div>

      <div>
        <button
          onClick={() => setSnippetsOpen(!snippetsOpen)}
          className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors"
          aria-expanded={snippetsOpen}
        >
          <h3 className="text-base font-semibold text-slate-900">
            Snippets (Vector) · {snippets.length}
          </h3>
          {snippetsOpen ? (
            <ChevronDown className="w-5 h-5 text-slate-500" />
          ) : (
            <ChevronRight className="w-5 h-5 text-slate-500" />
          )}
        </button>
        {snippetsOpen && (
          <div className="px-6 pb-6 space-y-4">
            {snippets.map((snippet, idx) => (
              <SnippetCard
                key={idx}
                snippet={snippet}
                expanded={expandedSnippets.has(idx)}
                onToggle={() => toggleSnippet(idx)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function CandidateCard({ candidate }: { candidate: CandidateProfile }) {
  return (
    <div className="border border-slate-200 rounded-lg p-4 space-y-3">
      <div>
        <h4 className="font-semibold text-slate-900">{candidate.full_name || 'Unknown'}</h4>
        {candidate.location && (
          <div className="flex items-center gap-1 text-sm text-slate-600 mt-1">
            <MapPin className="w-3.5 h-3.5" />
            {candidate.location}
          </div>
        )}
      </div>

      {candidate.experience && candidate.experience.length > 0 && (
        <div>
          <div className="flex items-center gap-1.5 text-xs font-medium text-slate-700 mb-1.5">
            <Briefcase className="w-3.5 h-3.5" />
            Experience
          </div>
          {candidate.experience.slice(0, 2).map((exp, idx) => (
            <div key={idx} className="text-sm text-slate-700 mb-1">
              <span className="font-medium">{exp.title || 'Position'}</span> at {exp.company}
              {(exp.start || exp.end) && (
                <span className="text-slate-500 text-xs ml-2">
                  {exp.start} - {exp.end || 'Present'}
                </span>
              )}
            </div>
          ))}
        </div>
      )}

      {candidate.education && candidate.education.length > 0 && (
        <div>
          <div className="flex items-center gap-1.5 text-xs font-medium text-slate-700 mb-1.5">
            <GraduationCap className="w-3.5 h-3.5" />
            Education
          </div>
          <div className="text-sm text-slate-700">
            {candidate.education[0].degree && `${candidate.education[0].degree} in `}
            {candidate.education[0].field || 'Field of Study'} · {candidate.education[0].institution}
          </div>
        </div>
      )}

      {candidate.skills && candidate.skills.length > 0 && (
        <div>
          <div className="flex items-center gap-1.5 text-xs font-medium text-slate-700 mb-1.5">
            <Award className="w-3.5 h-3.5" />
            Skills
          </div>
          <div className="flex flex-wrap gap-1.5">
            {candidate.skills.slice(0, 10).map((skill, idx) => (
              <span
                key={idx}
                className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded-full"
              >
                {skill}
              </span>
            ))}
            {candidate.skills.length > 10 && (
              <span className="px-2 py-0.5 text-slate-500 text-xs">
                +{candidate.skills.length - 10} more
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function SnippetCard({
  snippet,
  expanded,
  onToggle,
}: {
  snippet: Snippet;
  expanded: boolean;
  onToggle: () => void;
}) {
  const { metadata, score } = snippet;
  const text = snippet.text.length > 1500 ? snippet.text.slice(0, 1500) + '...' : snippet.text;
  const needsExpansion = text.split('\n').length > 8;

  return (
    <div className="border border-slate-200 rounded-lg p-4 space-y-2">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 bg-slate-100 text-slate-700 text-xs font-medium rounded">
            {metadata.section || 'unknown'}
          </span>
          {metadata.company && (
            <span className="text-xs text-slate-500">{metadata.company}</span>
          )}
          {metadata.institution && (
            <span className="text-xs text-slate-500">{metadata.institution}</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {score?.similarity != null && (
            <span className="px-2 py-0.5 bg-green-50 text-green-700 text-xs rounded">
              sim: {score.similarity.toFixed(2)}
            </span>
          )}
          {score?.distance != null && (
            <span className="px-2 py-0.5 bg-amber-50 text-amber-700 text-xs rounded">
              dist: {score.distance.toFixed(2)}
            </span>
          )}
        </div>
      </div>

      <pre
        className={`text-sm text-slate-700 whitespace-pre-wrap font-sans bg-slate-50 p-3 rounded ${
          !expanded && needsExpansion ? 'line-clamp-8' : ''
        }`}
      >
        {text}
      </pre>

      {needsExpansion && (
        <button
          onClick={onToggle}
          className="text-xs text-blue-600 hover:text-blue-700 font-medium"
        >
          {expanded ? 'Show less' : 'Expand'}
        </button>
      )}

      {metadata.candidate_name && (
        <div className="text-xs text-slate-500">
          Candidate: {metadata.candidate_name}
        </div>
      )}
    </div>
  );
}
