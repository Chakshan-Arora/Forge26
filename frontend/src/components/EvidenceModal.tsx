import React from 'react';
import { EvidenceRecord } from '../types';
import { X, ShieldCheck, AlertCircle, ExternalLink, BookOpen } from 'lucide-react';

interface EvidenceModalProps {
  evidence: EvidenceRecord | null;
  onClose: () => void;
}

export const EvidenceModal: React.FC<EvidenceModalProps> = ({ evidence, onClose }) => {
  if (!evidence) return null;

  const confidencePct = Math.round(evidence.confidence * 100);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-700 rounded-xl shadow-2xl p-6 text-slate-100">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <BookOpen className="w-5 h-5 text-indigo-400" />
            <h3 className="text-base font-semibold text-slate-100">
              Official Statutory Evidence Citation
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="mt-4 space-y-4">
          {/* Metadata Grid */}
          <div className="grid grid-cols-2 gap-3 text-xs bg-slate-800/60 p-3 rounded-lg border border-slate-700/60">
            <div>
              <span className="text-slate-400 block font-mono text-[10px] uppercase">Document Identifier</span>
              <span className="font-semibold text-indigo-300">{evidence.document_id}</span>
            </div>
            <div>
              <span className="text-slate-400 block font-mono text-[10px] uppercase">Clause Reference</span>
              <span className="font-semibold text-slate-200">{evidence.clause_id || 'General Section'}</span>
            </div>
            <div>
              <span className="text-slate-400 block font-mono text-[10px] uppercase">Section / Page</span>
              <span className="text-slate-300">{evidence.page_or_section || 'N/A'}</span>
            </div>
            <div>
              <span className="text-slate-400 block font-mono text-[10px] uppercase">Verification Confidence</span>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-emerald-400">{confidencePct}%</span>
                <span className={`px-1.5 py-0.5 text-[9px] rounded font-semibold ${
                  evidence.is_inferred
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                }`}>
                  {evidence.is_inferred ? 'AI INFERRED' : 'DIRECT VERBATIM'}
                </span>
              </div>
            </div>
          </div>

          {/* Exact Verbatim Text */}
          <div>
            <label className="text-xs font-mono uppercase tracking-wider text-slate-400 block mb-1">
              Exact Supporting Statutory Snippet
            </label>
            <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg text-sm text-slate-200 font-serif italic leading-relaxed border-l-4 border-l-indigo-500">
              "{evidence.exact_supporting_text}"
            </div>
          </div>

          {/* Reasoning Notes if present */}
          {evidence.notes && (
            <div className="p-3 bg-indigo-950/30 border border-indigo-900/40 rounded-lg text-xs text-indigo-200">
              <span className="font-semibold block mb-0.5">Analyst / Regulatory Note:</span>
              {evidence.notes}
            </div>
          )}

          {/* Official Source Link */}
          {evidence.source_url && (
            <div className="pt-2 flex justify-end">
              <a
                href={evidence.source_url}
                target="_blank"
                rel="noreferrer"
                className="flex items-center space-x-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-medium transition-colors"
              >
                <span>Verify on Government Portal</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
