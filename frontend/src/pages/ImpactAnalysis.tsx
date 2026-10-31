import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ImpactAnalysisReport, AffectedGroup, EvidenceRecord } from '../types';
import {
  TrendingUp,
  Users,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  ArrowRight,
  ShieldCheck,
  Calendar,
  Sparkles,
  ExternalLink,
} from 'lucide-react';
import { EvidenceModal } from '../components/EvidenceModal';

export const ImpactAnalysis: React.FC = () => {
  const [selectedScheme, setSelectedScheme] = useState<string>('Post-Matric Scholarship for SC Students');
  const [report, setReport] = useState<ImpactAnalysisReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceRecord | null>(null);

  const schemeOptions = [
    {
      name: 'Post-Matric Scholarship for SC Students',
      targetId: 'DOC-MoSJE-PMS-SC-2020',
      baseId: 'DOC-MoSJE-PMS-SC-2018',
    },
    {
      name: 'National Means-cum-Merit Scholarship Scheme',
      targetId: 'DOC-MoE-NMMSS-2022',
      baseId: 'DOC-MoE-NMMSS-2017',
    },
    {
      name: 'Central Sector Scheme of Scholarships for College and University Students',
      targetId: 'DOC-MoE-PMUSP-CSSS-2022',
      baseId: 'DOC-MoE-PMUSP-CSSS-2015',
    },
  ];

  useEffect(() => {
    async function loadImpact() {
      const match = schemeOptions.find((s) => s.name === selectedScheme);
      if (!match) return;

      try {
        setLoading(true);
        setError(null);
        const data = await api.analyzeImpact(match.targetId, match.baseId);
        setReport(data);
      } catch (err: any) {
        setError(err.message || 'Failed to generate impact analysis');
      } finally {
        setLoading(false);
      }
    }
    loadImpact();
  }, [selectedScheme]);

  const getImpactNatureBadge = (nature: string) => {
    switch (nature) {
      case 'EXPLICITLY_AFFECTED':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
      case 'POTENTIALLY_ELIGIBLE':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'POTENTIALLY_EXCLUDED':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'REQUIREMENTS_CHANGED':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      default:
        return 'bg-purple-500/10 text-purple-400 border-purple-500/30';
    }
  };

  return (
    <div className="space-y-6">
      <EvidenceModal
        evidence={selectedEvidence}
        onClose={() => setSelectedEvidence(null)}
      />

      {/* Header and Scheme Switcher */}
      <div className="bg-slate-900/80 p-5 rounded-xl border border-slate-800 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h1 className="text-xl font-bold text-white flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-indigo-400" />
              <span>Multi-Dimensional Student Impact Analysis</span>
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Evaluates cohort accessibility, deterministic eligibility interval shifts, and required student actions.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            {schemeOptions.map((opt) => (
              <button
                key={opt.name}
                onClick={() => setSelectedScheme(opt.name)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  selectedScheme === opt.name
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                {opt.name.split(' ')[0]}...
              </button>
            ))}
          </div>
        </div>

        {report && (
          <div className="p-4 bg-indigo-950/20 border border-indigo-900/40 rounded-lg">
            <span className="text-[10px] font-mono uppercase tracking-wider text-indigo-400 block mb-1">
              Executive Policy Impact Summary
            </span>
            <p className="text-xs text-slate-200 leading-relaxed font-sans">
              {report.summary}
            </p>
          </div>
        )}
      </div>

      {loading ? (
        <div className="flex items-center justify-center min-h-[40vh]">
          <div className="flex flex-col items-center space-y-3">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-xs font-mono text-slate-400">Computing Student Cohort Impact Deltas...</span>
          </div>
        </div>
      ) : error ? (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs">
          {error}
        </div>
      ) : report ? (
        <div className="space-y-6">
          {/* Cohorts Categorization Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* 1. Explicitly Affected */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                    Confirmed Affected Cohorts
                  </h3>
                </div>
                <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  {report.explicitly_affected_groups.length} Groups
                </span>
              </div>

              <div className="space-y-3">
                {report.explicitly_affected_groups.map((group, idx) => (
                  <div key={idx} className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-lg space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-slate-100">{group.group_name}</span>
                      <span className={`px-1.5 py-0.5 text-[9px] font-bold border rounded ${getImpactNatureBadge(group.impact_nature)}`}>
                        {group.impact_nature}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed">{group.details}</p>
                    {group.evidence.length > 0 && (
                      <button
                        onClick={() => setSelectedEvidence(group.evidence[0])}
                        className="text-[10px] text-indigo-400 hover:text-indigo-300 font-medium flex items-center space-x-1"
                      >
                        <ShieldCheck className="w-3 h-3" />
                        <span>Statutory Evidence Citation</span>
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* 2. Potentially Affected / Inferred */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div className="flex items-center space-x-2">
                  <Users className="w-4 h-4 text-indigo-400" />
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                    Newly Admitted / Inferred
                  </h3>
                </div>
                <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  {report.potentially_affected_groups.length} Groups
                </span>
              </div>

              <div className="space-y-3">
                {report.potentially_affected_groups.map((group, idx) => (
                  <div key={idx} className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-lg space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-slate-100">{group.group_name}</span>
                      <span className={`px-1.5 py-0.5 text-[9px] font-bold border rounded ${getImpactNatureBadge(group.impact_nature)}`}>
                        {group.impact_nature}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed">{group.details}</p>
                    {group.evidence.length > 0 && (
                      <button
                        onClick={() => setSelectedEvidence(group.evidence[0])}
                        className="text-[10px] text-indigo-400 hover:text-indigo-300 font-medium flex items-center space-x-1"
                      >
                        <ShieldCheck className="w-3 h-3" />
                        <span>Statutory Evidence Citation</span>
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* 3. Unresolved Ambiguities */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                    Unresolved Caveats
                  </h3>
                </div>
                <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  {report.unresolved_groups.length} Issues
                </span>
              </div>

              <div className="space-y-3">
                {report.unresolved_groups.length > 0 ? (
                  report.unresolved_groups.map((group, idx) => (
                    <div key={idx} className="p-3 bg-slate-950/60 border border-amber-950/50 rounded-lg space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold text-amber-200">{group.group_name}</span>
                        <span className="px-1.5 py-0.5 text-[9px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded">
                          CAVEAT
                        </span>
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed">{group.details}</p>
                    </div>
                  ))
                ) : (
                  <div className="p-4 text-center text-slate-400 text-xs font-mono">
                    No unresolved scope contradictions found.
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Actionable Recommendations for Affected Students */}
          {report.practical_consequences.length > 0 && (
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Actionable Steps for Applicants & Beneficiaries</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {report.practical_consequences.map((step, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-lg text-xs text-slate-200 flex items-start space-x-2.5"
                  >
                    <span className="px-1.5 py-0.5 rounded font-mono font-bold bg-indigo-600/30 text-indigo-300 text-[10px]">
                      {idx + 1}
                    </span>
                    <span className="leading-relaxed">{step}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
};
