export type DocumentType =
  | 'POLICY'
  | 'GUIDELINES'
  | 'AMENDMENT'
  | 'NOTIFICATION'
  | 'OFFICE_MEMORANDUM'
  | 'GAZETTE'
  | 'CIRCULAR'
  | 'CORRIGENDUM'
  | 'UNKNOWN';

export type ClauseType =
  | 'ELIGIBILITY'
  | 'FINANCIAL'
  | 'DEADLINE'
  | 'ADMINISTRATIVE'
  | 'SCOPE'
  | 'RENEWAL'
  | 'EXEMPTION'
  | 'SELECTION_PROCESS'
  | 'GENERAL';

export type ChangeType =
  | 'ADDED'
  | 'REMOVED'
  | 'MODIFIED'
  | 'REPLACED'
  | 'EXTENDED'
  | 'EXEMPTED'
  | 'CLARIFIED'
  | 'UNKNOWN';

export interface EvidenceRecord {
  document_id: string;
  clause_id?: string | null;
  source_url?: string | null;
  exact_supporting_text: string;
  page_or_section?: string | null;
  is_inferred: boolean;
  confidence: number;
  notes?: string | null;
}

export interface Clause {
  id: string;
  document_id: string;
  clause_number: string;
  title?: string | null;
  section?: string | null;
  text: string;
  normalized_text?: string | null;
  clause_type: ClauseType;
  structured_attributes: Record<string, any>;
  page_number?: number | null;
  subclauses?: string[];
}

export interface Document {
  id: string;
  title: string;
  scheme_name: string;
  ministry: string;
  document_type: DocumentType;
  order_number?: string | null;
  publication_date?: string | null;
  effective_date?: string | null;
  valid_until?: string | null;
  source_url?: string | null;
  version?: string;
  status?: string;
  clauses: Clause[];
  references?: Array<Record<string, string>>;
}

export interface AffectedGroup {
  group_name: string;
  category_type: string;
  impact_nature: string;
  details: string;
  criteria_delta?: Record<string, any> | null;
  evidence: EvidenceRecord[];
}

export interface ChangeRecord {
  change_id: string;
  document_id: string;
  previous_document_id?: string | null;
  clause_id: string;
  change_type: ChangeType;
  previous_text?: string | null;
  current_text?: string | null;
  previous_value?: any;
  current_value?: any;
  effective_from?: string | null;
  affected_groups: AffectedGroup[];
  evidence: EvidenceRecord[];
  confidence?: number | null;
  uncertainties: string[];
}

export interface ImpactAnalysisReport {
  report_id: string;
  scheme_name: string;
  base_document_id?: string | null;
  target_document_id: string;
  summary: string;
  explicitly_affected_groups: AffectedGroup[];
  potentially_affected_groups: AffectedGroup[];
  unresolved_groups: AffectedGroup[];
  deterministic_deltas: Array<Record<string, any>>;
  practical_consequences: string[];
  evidence_trail: EvidenceRecord[];
  generated_at: string;
}

export interface AgentInvestigationStep {
  step_number: number;
  step_name: string;
  description: string;
  tool_invoked?: string | null;
  status: string;
  details: Record<string, any>;
}

export interface AgentQueryResponse {
  session_id: string;
  query: string;
  scheme_name?: string | null;
  direct_answer: string;
  reasoning_type: string;
  steps_taken: AgentInvestigationStep[];
  detected_changes: ChangeRecord[];
  impact_summary?: string | null;
  affected_groups: AffectedGroup[];
  evidence_citations: EvidenceRecord[];
  verification_confidence: number;
  uncertainties: string[];
  actionable_recommendations: string[];
  source_documents: Array<{
    id: string;
    title: string;
    scheme_name: string;
    version?: string;
    source_url?: string;
    publication_date?: string;
  }>;
}

export interface SystemStats {
  total_documents: number;
  total_schemes: number;
  total_changes_detected: number;
  knowledge_graph_nodes: number;
  knowledge_graph_edges: number;
  active_schemes: string[];
}

export interface SchemeSummary {
  scheme_name: string;
  ministry: string;
  total_documents: number;
  versions: Array<{
    document_id: string;
    version: string;
    document_type: string;
    status: string;
    publication_date?: string;
    effective_date?: string;
    clause_count: number;
  }>;
  active_version?: string;
  latest_publication_date?: string;
  portal_url?: string;
}

export interface GraphNode {
  id: string;
  type: string;
  name?: string;
  label?: string;
  data?: Record<string, any>;
}

export interface GraphEdge {
  source: string;
  target: string;
  type?: string;
  relationship?: string;
  label?: string;
}

export interface GraphData {
  format: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  node_count: number;
  edge_count: number;
}
