import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { SystemStats, SchemeSummary, Document, ChangeRecord } from '../types';
import {
  FileText,
  Scale,
  GitCompare,
  Share2,
  Calendar,
  Building2,
  CheckCircle2,
  ArrowRight,
  ExternalLink,
  AlertTriangle,
  Clock,
} from 'lucide-react';

interface DashboardProps {
  onNavigate: (tab: string, context?: any) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [schemes, setSchemes] = useState<SchemeSummary[]>([]);
  const [recentDocs, setRecentDocs] = useState<Document[]>([]);
  const [recentChanges, setRecentChanges] = useState<ChangeRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        const [statsData, schemesData, docsData, changesData] = await Promise.all([
          api.getStats(),
          api.getPolicies(),
          api.getDocuments(),
          api.getChanges(),
        ]);
        setStats(statsData);
        setSchemes(schemesData);
        setRecentDocs(docsData.slice(0, 5));
        setRecentChanges(changesData.slice(0, 5));
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-mono text-slate-400">Loading Official Regulatory Records...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Platform Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/70 to-slate-900 p-6 border border-slate-800 shadow-xl">
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center space-x-2 px-2.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-mono mb-3">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>INDIAN CENTRAL EDUCATION & SCHOLARSHIP REGULATORY MONITOR</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mb-2">
            Regulatory Change Intelligence Engine
          </h1>
          <p className="text-sm text-slate-300 leading-relaxed">
            Continuously monitors and parses official policy notifications, revisions, and guidelines
            from the Ministry of Social Justice and Empowerment (MoSJE) and Ministry of Education (MoE).
            Provides clause-level temporal reasoning and deterministic student impact analysis.
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            <button
              onClick={() => onNavigate('investigation')}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-md transition-all flex items-center space-x-1.5"
            >
              <span>Ask AI Policy Investigator</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => onNavigate('compare')}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-semibold transition-all flex items-center space-x-1.5"
            >
              <span>Compare Revisions</span>
              <GitCompare className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-mono uppercase tracking-wider">Official Documents</span>
            <FileText className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white">{stats?.total_documents ?? 0}</div>
          <span className="text-[11px] text-emerald-400 font-mono">100% Authentic Government Gazette</span>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-mono uppercase tracking-wider">Flagship Schemes</span>
            <Scale className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white">{stats?.total_schemes ?? 0}</div>
          <span className="text-[11px] text-slate-400 font-mono">PMS-SC, NMMSS, PM-USP CSSS</span>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-mono uppercase tracking-wider">Knowledge Graph</span>
            <Share2 className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-white">{stats?.knowledge_graph_nodes ?? 0}</div>
          <span className="text-[11px] text-slate-400 font-mono">{stats?.knowledge_graph_edges ?? 0} Temporal & Legal Edges</span>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-mono uppercase tracking-wider">Detected Revisions</span>
            <GitCompare className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-white">{stats?.total_changes_detected || recentChanges.length}</div>
          <span className="text-[11px] text-amber-400 font-mono">Clause Modifications Tracked</span>
        </div>
      </div>

      {/* Flagship Schemes Section */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
          <div>
            <h2 className="text-base font-semibold text-white flex items-center space-x-2">
              <Scale className="w-4 h-4 text-indigo-400" />
              <span>Registered Central Government Scholarship Frameworks</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Authentic schemes monitored directly from the National Scholarship Portal and Ministry Gazette.
            </p>
          </div>
          <button
            onClick={() => onNavigate('explorer')}
            className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center space-x-1"
          >
            <span>Explore all clauses</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {schemes.map((scheme) => (
            <div
              key={scheme.scheme_name}
              className="bg-slate-950/60 border border-slate-800/80 hover:border-indigo-500/50 transition-all rounded-lg p-4 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="px-2 py-0.5 text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded">
                    ACTIVE
                  </span>
                  <span className="text-[11px] font-mono text-slate-400">
                    {scheme.total_documents} Versions
                  </span>
                </div>
                <h3 className="text-sm font-semibold text-slate-100 line-clamp-2 mb-1">
                  {scheme.scheme_name}
                </h3>
                <p className="text-xs text-slate-400 flex items-center space-x-1 mb-3">
                  <Building2 className="w-3 h-3 text-slate-500" />
                  <span className="truncate">{scheme.ministry}</span>
                </p>

                <div className="space-y-1 mb-4">
                  {scheme.versions.map((v) => (
                    <div
                      key={v.document_id}
                      className="flex items-center justify-between text-[11px] font-mono bg-slate-900 px-2 py-1 rounded text-slate-300"
                    >
                      <span>v{v.version} ({v.publication_date?.slice(0, 4) || 'Ref'})</span>
                      <span className="text-slate-500">{v.clause_count} clauses</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
                <button
                  onClick={() => onNavigate('explorer', { scheme: scheme.scheme_name })}
                  className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center space-x-1"
                >
                  <span>Inspect Clauses</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
                {scheme.portal_url && (
                  <a
                    href={scheme.portal_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-slate-400 hover:text-slate-200"
                    title="Open Official Portal"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Two Column Layout: Official Documents & Detected Changes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recently Ingested Documents */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
            <h2 className="text-sm font-semibold text-white flex items-center space-x-2">
              <FileText className="w-4 h-4 text-cyan-400" />
              <span>Official Government Notifications</span>
            </h2>
            <span className="text-[11px] font-mono text-slate-400">Authentic Corpus</span>
          </div>

          <div className="space-y-3">
            {recentDocs.map((doc) => (
              <div
                key={doc.id}
                className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-lg hover:border-slate-700 transition-colors"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-mono text-indigo-400 font-semibold">{doc.id}</span>
                  <span className="text-[10px] text-slate-400 font-mono flex items-center space-x-1">
                    <Calendar className="w-2.5 h-2.5" />
                    <span>Effective: {doc.effective_date || doc.publication_date || 'N/A'}</span>
                  </span>
                </div>
                <h4 className="text-xs font-medium text-slate-200 line-clamp-2 mb-1.5">
                  {doc.title}
                </h4>
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-400">{doc.ministry}</span>
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-300">
                    {doc.clauses.length} clauses extracted
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recently Detected Regulatory Changes */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
            <h2 className="text-sm font-semibold text-white flex items-center space-x-2">
              <GitCompare className="w-4 h-4 text-amber-400" />
              <span>Key Clause Modifications Detected</span>
            </h2>
            <button
              onClick={() => onNavigate('compare')}
              className="text-xs text-amber-400 hover:text-amber-300 font-medium flex items-center space-x-1"
            >
              <span>View Diff</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-3">
            {recentChanges.length > 0 ? (
              recentChanges.map((chg) => (
                <div
                  key={chg.change_id}
                  className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-lg"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="px-1.5 py-0.5 text-[9px] font-bold rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      {chg.change_type}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">
                      Clause {chg.clause_id}
                    </span>
                  </div>
                  {chg.current_text && (
                    <p className="text-xs text-slate-300 line-clamp-2 font-serif italic mb-2">
                      "{chg.current_text}"
                    </p>
                  )}
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span>Evidence: {chg.evidence.length} citation(s)</span>
                    <span className="text-emerald-400 font-mono">
                      Conf: {Math.round((chg.confidence || 1.0) * 100)}%
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-slate-400 text-xs font-mono">
                Launch "Policy Comparison" to inspect live pairwise diffs.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
