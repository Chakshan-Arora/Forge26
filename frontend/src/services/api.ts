import {
  Document,
  ChangeRecord,
  ImpactAnalysisReport,
  AgentQueryResponse,
  SystemStats,
  SchemeSummary,
  GraphData,
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const fullUrl = `${API_BASE}${url}`;
  const response = await fetch(fullUrl, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    let errorDetail = response.statusText;
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errorDetail;
    } catch {
      // Ignore JSON parse failure
    }
    throw new Error(errorDetail || `HTTP Error ${response.status}`);
  }

  return response.json();
}

export const api = {
  // System
  getHealth: () => fetchJson<{ status: string; service: string; registered_documents: number }>('/api/health'),
  getStats: () => fetchJson<SystemStats>('/api/stats'),

  // Documents
  getDocuments: (params?: { scheme_name?: string; ministry?: string; document_type?: string }) => {
    const q = new URLSearchParams();
    if (params?.scheme_name) q.set('scheme_name', params.scheme_name);
    if (params?.ministry) q.set('ministry', params.ministry);
    if (params?.document_type) q.set('document_type', params.document_type);
    const qs = q.toString() ? `?${q.toString()}` : '';
    return fetchJson<Document[]>(`/api/documents${qs}`);
  },
  getDocumentById: (id: string) => fetchJson<Document>(`/api/documents/${id}`),
  ingestDocument: (payload: {
    raw_text?: string;
    scheme_name: string;
    ministry: string;
    document_type?: string;
    order_number?: string;
    publication_date?: string;
    version?: string;
  }) => fetchJson<Document>('/api/documents/ingest', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),

  // Policies
  getPolicies: () => fetchJson<SchemeSummary[]>('/api/policies'),
  getPolicyHistory: (schemeName: string) =>
    fetchJson<{ scheme_name: string; timeline_events: any[]; total_versions: number }>(
      `/api/policies/${encodeURIComponent(schemeName)}/history`
    ),

  // Changes
  getChanges: (params?: { document_id?: string; change_type?: string }) => {
    const q = new URLSearchParams();
    if (params?.document_id) q.set('document_id', params.document_id);
    if (params?.change_type) q.set('change_type', params.change_type);
    const qs = q.toString() ? `?${q.toString()}` : '';
    return fetchJson<ChangeRecord[]>(`/api/changes${qs}`);
  },
  getChangeById: (id: string) => fetchJson<ChangeRecord>(`/api/changes/${id}`),
  comparePolicies: (baseId: string, targetId: string) =>
    fetchJson<{ target_document_id: string; base_document_id: string; summary: any; changes: ChangeRecord[]; change_count: number }>(
      '/api/changes/compare',
      {
        method: 'POST',
        body: JSON.stringify({ base_document_id: baseId, target_document_id: targetId }),
      }
    ),

  // Impact
  analyzeImpact: (targetId: string, baseId?: string) =>
    fetchJson<ImpactAnalysisReport>('/api/impact/analyze', {
      method: 'POST',
      body: JSON.stringify({ target_document_id: targetId, base_document_id: baseId }),
    }),
  getImpactById: (id: string) => fetchJson<ImpactAnalysisReport>(`/api/impact/${id}`),

  // Knowledge Graph
  getGraph: (format: 'json' | 'mermaid' = 'json') =>
    fetchJson<GraphData>(`/api/graph?format=${format}`),
  getEntitySubgraph: (entityId: string) =>
    fetchJson<{ entity_id: string; nodes: any[]; edges: any[]; node_count: number; edge_count: number }>(
      `/api/graph/${encodeURIComponent(entityId)}`
    ),

  // Agent Investigation
  queryAgent: (payload: {
    query: string;
    scheme_name?: string;
    target_date?: string;
    beneficiary_group?: string;
    session_id?: string;
  }) =>
    fetchJson<AgentQueryResponse>('/api/agent/query', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getAgentHistory: (limit: number = 10) =>
    fetchJson<Array<{ id: number; session_id: string; query: string; direct_answer: string; created_at?: string }>>(
      `/api/agent/history?limit=${limit}`
    ),
};
