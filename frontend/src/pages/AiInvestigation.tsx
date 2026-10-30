import React, { useState } from 'react';
import { api } from '../services/api';
import { AgentQueryResponse, EvidenceRecord } from '../types';
import {
  Sparkles,
  Send,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  GitCompare,
  BookOpen,
  ArrowRight,
  ExternalLink,
  Layers,
  Clock,
  HelpCircle,
} from 'lucide-react';
import { EvidenceModal } from '../components/EvidenceModal';

export const AiInvestigation: React.FC = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<AgentQueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceRecord | null>(null);

  const sampleQueries = [
    'What changed in the Post-Matric Scholarship for SC students guidelines?',
    'What was the applicable eligibility rule on 2019-06-01 for Post-Matric SC students?',
    'How did the income ceiling or scholarship amount change for NMMSS?',
    'What are the scholarship amounts for hostellers vs day scholars under PMS-SC?',
  ];

  const handleSearch = async (queryText: string) => {
    if (!queryText.trim()) return;
    try {
      setLoading(true);
      setError(null);
      const res = await api.queryAgent({ query: queryText });
      setResponse(res);
    } catch (err: any) {
      setError(err.message || 'Agent investigation failed');
    } finally {
      setLoading(false);
    }
  };

  const getReasoningBadge = (type: string) => {
    switch (type) {
      case 'DETERMINISTIC_CALCULATION':
        return {
          label: 'DETERMINISTIC CALCULATION',
          color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
          desc: 'Computed via exact mathematical & clause-level delta algorithms.',
        };
      case 'RETRIEVED_FACT':
        return {
          label: 'RETRIEVED STATUTORY FACT',
          color: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
          desc: 'Quoted verbatim directly from official government gazettes.',
        };
      case 'UNRESOLVED_AMBIGUITY':
      case 'UNRESOLVED':
        return {
          label: 'UNRESOLVED AMBIGUITY / CAVEAT',
          color: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
          desc: 'Statutory gap, temporal overlap, or missing transitional provision identified.',
        };
      default:
        return {
          label: 'AI SYNTHESIZED REASONING',
          color: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
          desc: 'Synthesized interpretation backed by multi-clause evidence trail.',
        };
    }
  };

  return (
    <div className="space-y-6">
      <EvidenceModal
        evidence={selectedEvidence}
        onClose={() => setSelectedEvidence(null)}
      />

      {/* Header and Query Input */}
      <div className="bg-slate-900/80 p-6 rounded-xl border border-slate-800 shadow-sm space-y-4">
        <div>
          <div className="inline-flex items-center space-x-2 px-2 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[10px] font-mono mb-2">
            <Sparkles className="w-3 h-3" />
            <span>LANGGRAPH STATE MACHINE INVESTIGATION AGENT</span>
          </div>
          <h1 className="text-xl font-bold text-white flex items-center space-x-2">
            <span>AI Policy Investigation Console</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Ask complex regulatory questions. The agent executes multi-step investigation, validates official
            evidence, and distinguishes factual deductions from legal caveats.
          </p>
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch(query);
          }}
          className="relative flex items-center"
        >
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. What changed in the Post-Matric SC scholarship guidelines?"
            className="w-full pl-4 pr-24 py-3 bg-slate-950 border border-slate-700 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-sans shadow-inner"
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="absolute right-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all shadow"
          >
            {loading ? (
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                <span>Investigate</span>
                <Send className="w-3 h-3" />
              </>
            )}
          </button>
        </form>

        {/* Sample Query Chips */}
        <div className="flex flex-wrap items-center gap-2 pt-2">
          <span className="text-[11px] text-slate-500 font-mono">Sample Inquiries:</span>
          {sampleQueries.map((sample, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuery(sample);
                handleSearch(sample);
              }}
              className="text-[11px] px-2.5 py-1 rounded-full bg-slate-800/80 hover:bg-slate-800 text-slate-300 border border-slate-700/80 transition-colors"
            >
              {sample}
            </button>
          ))}
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center min-h-[40vh]">
          <div className="flex flex-col items-center space-y-3">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-xs font-mono text-slate-400">Executing Multi-Step LangGraph Agent Workflow...</span>
            <span className="text-[11px] text-slate-500">Retrieving Documents &rarr; Comparing Clauses &rarr; Verifying Evidence</span>
          </div>
        </div>
      )}

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs">
          {error}
        </div>
      )}

      {response && !loading && (
        <div className="space-y-6">
          {/* Agent Workflow Execution Timeline (Steps Taken) */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold flex items-center space-x-1.5">
                <Clock className="w-3.5 h-3.5 text-indigo-400" />
                <span>Transparent Agentic Execution Audit ({response.steps_taken.length} Steps)</span>
              </span>
              <span className="text-[11px] font-mono text-slate-400">Session ID: {response.session_id}</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
              {response.steps_taken.map((step) => (
                <div
                  key={step.step_number}
                  className="p-3 bg-slate-950/70 border border-slate-800/80 rounded-lg space-y-1.5"
                >
                  <div className="flex items-center justify-between text-[10px] font-mono">
                    <span className="text-indigo-400 font-bold">Step {step.step_number}</span>
                    <span className="px-1 py-0.2 rounded bg-emerald-500/20 text-emerald-400 text-[8px] font-bold">
                      {step.status}
                    </span>
                  </div>
                  <h4 className="text-[11px] font-semibold text-slate-200">{step.step_name}</h4>
                  <p className="text-[10px] text-slate-400 line-clamp-3 leading-relaxed">
                    {step.description}
                  </p>
                  {step.tool_invoked && (
                    <span className="text-[9px] font-mono text-slate-500 block truncate">
                      Tool: {step.tool_invoked}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Direct Authoritative Answer Banner */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-md space-y-4">
            {/* Reasoning Distinction Badge */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                {(() => {
                  const badge = getReasoningBadge(response.reasoning_type);
                  return (
                    <div className="flex items-center space-x-2">
                      <span className={`px-2.5 py-1 rounded text-[10px] font-bold border ${badge.color}`}>
                        {badge.label}
                      </span>
                      <span className="text-xs text-slate-400 hidden sm:inline">({badge.desc})</span>
                    </div>
                  );
                })()}
              </div>

              <div className="flex items-center space-x-3 text-xs font-mono">
                <span className="text-slate-400">Verification Confidence:</span>
                <span className="font-bold text-emerald-400 text-sm">
                  {Math.round(response.verification_confidence * 100)}%
                </span>
              </div>
            </div>

            {/* Answer Text */}
            <div className="text-slate-100 text-sm leading-relaxed space-y-3 font-sans whitespace-pre-line">
              {response.direct_answer}
            </div>

            {/* Practical Actions Checklist */}
            {response.actionable_recommendations.length > 0 && (
              <div className="pt-4 border-t border-slate-800 space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center space-x-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Recommended Next Actions for Students</span>
                </h4>
                <div className="space-y-1.5">
                  {response.actionable_recommendations.map((action, i) => (
                    <div key={i} className="flex items-start space-x-2 text-xs text-slate-300">
                      <span className="text-emerald-400 font-bold">&bull;</span>
                      <span>{action}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Two Column Grid: Citations & Uncertainties */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Evidence Citations */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 flex items-center space-x-2">
                  <ShieldCheck className="w-4 h-4 text-indigo-400" />
                  <span>Supporting Statutory Evidence ({response.evidence_citations.length})</span>
                </h3>
                <span className="text-[10px] font-mono text-slate-400">Verifiable Audit Trail</span>
              </div>

              <div className="space-y-3 max-h-[420px] overflow-y-auto pr-1">
                {response.evidence_citations.map((ev, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-slate-950/70 border border-slate-800 rounded-lg space-y-2 hover:border-slate-700 transition-colors"
                  >
                    <div className="flex items-center justify-between text-[10px] font-mono">
                      <span className="text-indigo-400 font-semibold">{ev.document_id}</span>
                      <span className="text-slate-400">{ev.clause_id || 'General'}</span>
                    </div>
                    <p className="text-xs text-slate-300 font-serif italic pl-2 border-l-2 border-indigo-500/50">
                      "{ev.exact_supporting_text}"
                    </p>
                    <div className="flex items-center justify-between pt-1 text-[10px]">
                      <span className="text-emerald-400 font-mono">
                        Confidence: {Math.round(ev.confidence * 100)}%
                      </span>
                      <button
                        onClick={() => setSelectedEvidence(ev)}
                        className="text-indigo-400 hover:text-indigo-300 font-medium"
                      >
                        Inspect Citation Details &rarr;
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Caveats, Ambiguities & Source Documents */}
            <div className="space-y-6">
              {/* Uncertainties & Caveats */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 flex items-center space-x-2">
                    <AlertTriangle className="w-4 h-4 text-amber-400" />
                    <span>Regulatory Caveats & Ambiguities</span>
                  </h3>
                  <span className="text-[10px] font-mono text-amber-400">
                    {response.uncertainties.length} Flagged
                  </span>
                </div>

                <div className="space-y-2">
                  {response.uncertainties.length > 0 ? (
                    response.uncertainties.map((u, idx) => (
                      <div
                        key={idx}
                        className="p-2.5 bg-amber-950/20 border border-amber-900/40 rounded-lg text-xs text-amber-300 flex items-start space-x-2"
                      >
                        <HelpCircle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                        <span className="leading-relaxed">{u}</span>
                      </div>
                    ))
                  ) : (
                    <div className="p-4 text-center text-slate-500 text-xs font-mono">
                      No legal ambiguities or missing timeline dependencies detected.
                    </div>
                  )}
                </div>
              </div>

              {/* Source Documents Checked */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 flex items-center space-x-2 pb-2 border-b border-slate-800">
                  <BookOpen className="w-4 h-4 text-cyan-400" />
                  <span>Audited Official Documents ({response.source_documents.length})</span>
                </h3>
                <div className="space-y-2">
                  {response.source_documents.map((doc) => (
                    <div
                      key={doc.id}
                      className="p-2.5 bg-slate-950 rounded border border-slate-800 flex items-center justify-between text-xs"
                    >
                      <div>
                        <span className="font-semibold text-slate-200 block">{doc.title}</span>
                        <span className="text-[10px] font-mono text-slate-400">
                          {doc.id} &bull; v{doc.version || '1.0'}
                        </span>
                      </div>
                      {doc.source_url && (
                        <a
                          href={doc.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="p-1 text-slate-400 hover:text-indigo-300"
                          title="Open Original Document"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
