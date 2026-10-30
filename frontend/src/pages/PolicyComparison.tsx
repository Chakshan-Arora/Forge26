import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ChangeRecord, SchemeSummary, EvidenceRecord } from '../types';
import {
  GitCompare,
  ArrowRight,
  ShieldCheck,
  AlertCircle,
  TrendingUp,
  FileText,
  Search,
  ExternalLink,
  Info,
} from 'lucide-react';
import { EvidenceModal } from '../components/EvidenceModal';

export const PolicyComparison: React.FC = () => {
  const [schemes, setSchemes] = useState<SchemeSummary[]>([]);
  const [selectedScheme, setSelectedScheme] = useState<string>('Post-Matric Scholarship for SC Students');
  const [changes, setChanges] = useState<ChangeRecord[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceRecord | null>(null);

  // Pre-configured official revision pairs
  const revisionPairs: Record<string, { baseId: string; targetId: string; label: string }> = {
    'Post-Matric Scholarship for SC Students': {
      baseId: 'DOC-MoSJE-PMS-SC-2018',
      targetId: 'DOC-MoSJE-PMS-SC-2020',
      label: '2018 Guidelines vs 2020 Revision',
    },
    'National Means-cum-Merit Scholarship Scheme': {
      baseId: 'DOC-MoE-NMMSS-2017',
      targetId: 'DOC-MoE-NMMSS-2022',
      label: '2017 Guidelines vs 2022 Revision',
    },
    'Central Sector Scheme of Scholarships for College and University Students': {
      baseId: 'DOC-MoE-PMUSP-CSSS-2015',
      targetId: 'DOC-MoE-PMUSP-CSSS-2022',
      label: '2015 Guidelines vs 2022 Revision',
    },
  };

  useEffect(() => {
    async function loadSchemes() {
      try {
        const scList = await api.getPolicies();
        setSchemes(scList);
      } catch (err) {
        console.error('Failed to load schemes', err);
      }
    }
    loadSchemes();
  }, []);

  useEffect(() => {
    async function executeComparison() {
      const pair = revisionPairs[selectedScheme];
      if (!pair) return;

      try {
        setLoading(true);
        setError(null);
        const res = await api.comparePolicies(pair.baseId, pair.targetId);
        setChanges(res.changes);
        setSummary(res.summary);
      } catch (err: any) {
        setError(err.message || 'Comparison failed');
      } finally {
        setLoading(false);
      }
    }
    executeComparison();
  }, [selectedScheme]);

  const getChangeBadge = (type: string) => {
    switch (type) {
      case 'MODIFIED':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'ADDED':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'REMOVED':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'REPLACED':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
      default:
        return 'bg-slate-700/30 text-slate-300 border-slate-600/30';
    }
  };

  return (
    <div className="space-y-6">
      {/* Evidence Modal Popup */}
      <EvidenceModal
        evidence={selectedEvidence}
        onClose={() => setSelectedEvidence(null)}
      />

      {/* Header and Scheme Selector */}
      <div className="bg-slate-900/80 p-5 rounded-xl border border-slate-800 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h1 className="text-xl font-bold text-white flex items-center space-x-2">
              <GitCompare className="w-5 h-5 text-indigo-400" />
              <span>Clause-by-Clause Policy Comparison</span>
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Side-by-side regulatory diffing across revisions with deterministic numeric and threshold tracking.
            </p>
          </div>

          {/* Scheme Select Buttons */}
          <div className="flex flex-wrap gap-2">
            {Object.keys(revisionPairs).map((name) => {
              const isSelected = selectedScheme === name;
              return (
                <button
                  key={name}
                  onClick={() => setSelectedScheme(name)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    isSelected
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  {name.split(' ')[0]}... ({revisionPairs[name].label.split(' ')[0]})
                </button>
              );
            })}
          </div>
        </div>

        {/* Active Comparison Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-800/80 text-xs">
          <div className="flex items-center space-x-2">
            <span className="text-slate-400">Comparing:</span>
            <span className="font-semibold text-slate-200">{selectedScheme}</span>
            <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              {revisionPairs[selectedScheme]?.label}
            </span>
          </div>

          {summary && (
            <div className="flex items-center space-x-3 text-[11px] font-mono text-slate-400">
              <span>{summary.total_changes ?? changes.length} Total Changes</span>
              <span className="text-emerald-400">+{summary.additions_count ?? 0} Added</span>
              <span className="text-amber-400">~{summary.modifications_count ?? changes.length} Modified</span>
              <span className="text-rose-400">-{summary.removals_count ?? 0} Removed</span>
            </div>
          )}
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center min-h-[40vh]">
          <div className="flex flex-col items-center space-y-3">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-xs font-mono text-slate-400">Executing Clause-Level Alignment & Diff...</span>
          </div>
        </div>
      ) : error ? (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs">
          {error}
        </div>
      ) : (
        <div className="space-y-4">
          {changes.map((chg, idx) => {
            const hasPrev = !!chg.previous_text;
            const hasCurr = !!chg.current_text;

            return (
              <div
                key={chg.change_id || idx}
                className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4"
              >
                {/* Change Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800">
                  <div className="flex items-center space-x-2">
                    <span
                      className={`px-2 py-0.5 text-[10px] font-bold border rounded ${getChangeBadge(
                        chg.change_type
                      )}`}
                    >
                      {chg.change_type}
                    </span>
                    <span className="text-xs font-mono font-bold text-indigo-300">
                      Clause {chg.clause_id}
                    </span>
                  </div>

                  <div className="flex items-center space-x-3 text-xs">
                    {chg.effective_from && (
                      <span className="text-slate-400 font-mono text-[11px]">
                        Effective From: <strong className="text-slate-200">{chg.effective_from}</strong>
                      </span>
                    )}
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      Conf: {Math.round((chg.confidence || 1.0) * 100)}%
                    </span>
                    {chg.evidence.length > 0 && (
                      <button
                        onClick={() => setSelectedEvidence(chg.evidence[0])}
                        className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-indigo-500/30 rounded text-[11px] font-medium flex items-center space-x-1"
                      >
                        <ShieldCheck className="w-3 h-3" />
                        <span>View Evidence ({chg.evidence.length})</span>
                      </button>
                    )}
                  </div>
                </div>

                {/* Diff Viewer Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Previous Clause (Baseline) */}
                  <div className="p-3.5 bg-slate-950/70 border border-slate-800 rounded-lg space-y-2">
                    <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 border-b border-slate-800/80 pb-1.5">
                      <span className="uppercase text-rose-400 font-semibold">Previous Baseline Provision</span>
                      <span>{chg.previous_document_id || 'Prior Guidelines'}</span>
                    </div>
                    {hasPrev ? (
                      <p className="text-xs text-slate-300 font-serif leading-relaxed line-through decoration-rose-500/60 opacity-85">
                        "{chg.previous_text}"
                      </p>
                    ) : (
                      <p className="text-xs text-slate-500 italic font-mono">
                        (No prior clause - Newly introduced statutory provision)
                      </p>
                    )}
                  </div>

                  {/* Current Clause (Target Revision) */}
                  <div className="p-3.5 bg-slate-950/70 border border-emerald-950/60 rounded-lg space-y-2">
                    <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 border-b border-slate-800/80 pb-1.5">
                      <span className="uppercase text-emerald-400 font-semibold">Amended / Current Provision</span>
                      <span>{chg.document_id}</span>
                    </div>
                    {hasCurr ? (
                      <p className="text-xs text-slate-100 font-serif leading-relaxed bg-emerald-950/20 p-2 rounded border-l-2 border-emerald-500">
                        "{chg.current_text}"
                      </p>
                    ) : (
                      <p className="text-xs text-rose-400 italic font-mono">
                        (Provision revoked / repealed in current revision)
                      </p>
                    )}
                  </div>
                </div>

                {/* Caveats / Uncertainties if present */}
                {chg.uncertainties && chg.uncertainties.length > 0 && (
                  <div className="p-2.5 bg-amber-500/10 border border-amber-500/20 rounded-lg text-xs text-amber-300 flex items-start space-x-2">
                    <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-semibold block text-[11px]">Regulatory Interpretation Note:</span>
                      <ul className="list-disc pl-4 space-y-0.5 text-[11px]">
                        {chg.uncertainties.map((u, i) => (
                          <li key={i}>{u}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
