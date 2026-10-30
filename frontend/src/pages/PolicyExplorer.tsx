import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Document, Clause, ClauseType } from '../types';
import {
  Search,
  FileText,
  Building2,
  Calendar,
  ExternalLink,
  ChevronRight,
  Shield,
  Layers,
  BookOpen,
} from 'lucide-react';

interface PolicyExplorerProps {
  initialScheme?: string;
  onOpenEvidence?: (clause: Clause) => void;
}

export const PolicyExplorer: React.FC<PolicyExplorerProps> = ({ initialScheme }) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [selectedClause, setSelectedClause] = useState<Clause | null>(null);
  const [searchQuery, setSearchQuery] = useState(initialScheme || '');
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDocs() {
      try {
        setLoading(true);
        const docs = await api.getDocuments();
        setDocuments(docs);
        if (docs.length > 0) {
          // Select initial scheme or first document
          if (initialScheme) {
            const match = docs.find((d) => d.scheme_name.toLowerCase().includes(initialScheme.toLowerCase()));
            setSelectedDocId(match ? match.id : docs[0].id);
          } else {
            setSelectedDocId(docs[0].id);
          }
        }
      } catch (err) {
        console.error('Failed to load documents', err);
      } finally {
        setLoading(false);
      }
    }
    loadDocs();
  }, [initialScheme]);

  const filteredDocs = documents.filter((d) => {
    const matchesSearch =
      d.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.scheme_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.ministry.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = selectedType === 'ALL' || d.document_type === selectedType;
    return matchesSearch && matchesType;
  });

  const activeDoc = documents.find((d) => d.id === selectedDocId) || filteredDocs[0];

  const getClauseBadgeColor = (type: ClauseType) => {
    switch (type) {
      case 'ELIGIBILITY':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
      case 'FINANCIAL':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'DEADLINE':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'SCOPE':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/30';
      case 'RENEWAL':
        return 'bg-teal-500/10 text-teal-400 border-teal-500/30';
      default:
        return 'bg-slate-700/30 text-slate-300 border-slate-600/30';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header and Filter Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-slate-900/80 p-4 rounded-xl border border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center space-x-2">
            <BookOpen className="w-5 h-5 text-indigo-400" />
            <span>Official Policy & Clause Explorer</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Browse structured regulatory documents, inspect clause hierarchy, and verify statutory sources.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
          {/* Search Box */}
          <div className="relative flex-1 sm:w-64">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search scheme or keyword..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 bg-slate-950 border border-slate-700/80 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>

          {/* Type Filter */}
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-3 py-1.5 bg-slate-950 border border-slate-700/80 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
          >
            <option value="ALL">All Document Types</option>
            <option value="GUIDELINES">Guidelines</option>
            <option value="NOTIFICATION">Notification</option>
            <option value="AMENDMENT">Amendment</option>
          </select>
        </div>
      </div>

      {/* Two Pane Explorer Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Documents List (4 cols) */}
        <div className="lg:col-span-4 space-y-3">
          <div className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center justify-between px-1">
            <span>Official Documents ({filteredDocs.length})</span>
          </div>

          <div className="space-y-2 max-h-[750px] overflow-y-auto pr-1">
            {filteredDocs.map((doc) => {
              const isSelected = doc.id === activeDoc?.id;
              return (
                <div
                  key={doc.id}
                  onClick={() => {
                    setSelectedDocId(doc.id);
                    setSelectedClause(null);
                  }}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-indigo-950/40 border-indigo-500/60 shadow-md ring-1 ring-indigo-500/30'
                      : 'bg-slate-900/60 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] font-mono text-indigo-400 font-bold">{doc.id}</span>
                    <span className="px-1.5 py-0.5 text-[9px] font-semibold rounded bg-slate-800 text-slate-300">
                      v{doc.version || '1.0'}
                    </span>
                  </div>

                  <h3 className="text-xs font-semibold text-slate-100 line-clamp-2 mb-2 leading-relaxed">
                    {doc.title}
                  </h3>

                  <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
                    <span className="truncate max-w-[160px]">{doc.scheme_name}</span>
                    <span>{doc.clauses.length} clauses</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Selected Document Details & Clauses (8 cols) */}
        <div className="lg:col-span-8 space-y-4">
          {activeDoc ? (
            <div className="space-y-4">
              {/* Document Metadata Banner */}
              <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-sm">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800 mb-3">
                  <div>
                    <span className="text-[10px] font-mono text-indigo-400 block font-semibold">{activeDoc.id}</span>
                    <h2 className="text-base font-bold text-white mt-0.5">{activeDoc.title}</h2>
                  </div>
                  {activeDoc.source_url && (
                    <a
                      href={activeDoc.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-indigo-500/30 rounded-lg text-xs font-medium transition-colors whitespace-nowrap"
                    >
                      <span>Official Source Portal</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  )}
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs bg-slate-950/50 p-3 rounded-lg border border-slate-800/80">
                  <div>
                    <span className="text-slate-500 block font-mono text-[10px] uppercase">Issuing Ministry</span>
                    <span className="font-medium text-slate-200">{activeDoc.ministry}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block font-mono text-[10px] uppercase">Order / Gazette No.</span>
                    <span className="font-medium text-slate-200 font-mono">{activeDoc.order_number || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block font-mono text-[10px] uppercase">Publication Date</span>
                    <span className="font-medium text-slate-200 font-mono">{activeDoc.publication_date || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block font-mono text-[10px] uppercase">Statutory Status</span>
                    <span className={`inline-block px-1.5 py-0.5 text-[10px] font-semibold rounded mt-0.5 ${
                      activeDoc.status === 'ACTIVE'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {activeDoc.status}
                    </span>
                  </div>
                </div>
              </div>

              {/* Clauses Breakdown */}
              <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                  <h3 className="text-sm font-semibold text-white flex items-center space-x-2">
                    <Layers className="w-4 h-4 text-indigo-400" />
                    <span>Extracted Legal Clauses ({activeDoc.clauses.length})</span>
                  </h3>
                  <span className="text-xs text-slate-400 font-mono">Structured Hierarchy</span>
                </div>

                <div className="space-y-3 max-h-[580px] overflow-y-auto pr-1">
                  {activeDoc.clauses.map((clause) => {
                    const isClauseSelected = selectedClause?.id === clause.id;
                    const hasAttrs = Object.keys(clause.structured_attributes || {}).length > 0;

                    return (
                      <div
                        key={clause.id}
                        onClick={() => setSelectedClause(clause)}
                        className={`p-4 rounded-xl border transition-all cursor-pointer ${
                          isClauseSelected
                            ? 'bg-slate-800/90 border-indigo-500 shadow-md ring-1 ring-indigo-500/30'
                            : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <span className="px-2 py-0.5 text-xs font-mono font-bold bg-slate-800 text-indigo-300 rounded border border-slate-700">
                              {clause.clause_number}
                            </span>
                            <span className="text-xs font-semibold text-slate-200">
                              {clause.title || `Clause ${clause.clause_number}`}
                            </span>
                          </div>
                          <span
                            className={`px-2 py-0.5 text-[10px] font-semibold border rounded-full ${getClauseBadgeColor(
                              clause.clause_type
                            )}`}
                          >
                            {clause.clause_type}
                          </span>
                        </div>

                        {/* Verbatim Clause Text */}
                        <p className="text-xs text-slate-300 leading-relaxed font-serif pl-2 border-l-2 border-indigo-500/40 my-2">
                          "{clause.text}"
                        </p>

                        {/* Structured Attributes Tags (Income, Amount, etc.) */}
                        {hasAttrs && (
                          <div className="mt-3 pt-2 border-t border-slate-800/80 flex flex-wrap gap-2">
                            {Object.entries(clause.structured_attributes).map(([k, v]) => (
                              <span
                                key={k}
                                className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-mono bg-slate-900 text-slate-300 border border-slate-700"
                              >
                                <span className="text-slate-500">{k}:</span>
                                <span className="font-semibold text-indigo-300">
                                  {typeof v === 'number' ? v.toLocaleString('en-IN') : String(v)}
                                </span>
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center text-slate-400 font-mono text-xs">
              Select a document to inspect clauses.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
