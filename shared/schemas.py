"""
Shared Pydantic Schemas for Policy Intel.

Maintained according to the team data contract for communication between:
- Person 1: Document Ingestion and Clause Extraction
- Person 2 (You): Regulatory Intelligence & Impact Analysis Engine
- Person 3: Platform API, State, and Graph/DB Persistence
"""

from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ChangeType(str, Enum):
    ADDED = "ADDED"
    REMOVED = "REMOVED"
    MODIFIED = "MODIFIED"
    REPLACED = "REPLACED"
    EXTENDED = "EXTENDED"
    EXEMPTED = "EXEMPTED"
    CLARIFIED = "CLARIFIED"
    UNKNOWN = "UNKNOWN"


class DocumentType(str, Enum):
    POLICY = "POLICY"
    GUIDELINES = "GUIDELINES"
    AMENDMENT = "AMENDMENT"
    NOTIFICATION = "NOTIFICATION"
    OFFICE_MEMORANDUM = "OFFICE_MEMORANDUM"
    GAZETTE = "GAZETTE"
    CIRCULAR = "CIRCULAR"
    CORRIGENDUM = "CORRIGENDUM"
    UNKNOWN = "UNKNOWN"


class ClauseType(str, Enum):
    ELIGIBILITY = "ELIGIBILITY"
    FINANCIAL = "FINANCIAL"
    DEADLINE = "DEADLINE"
    ADMINISTRATIVE = "ADMINISTRATIVE"
    SCOPE = "SCOPE"
    RENEWAL = "RENEWAL"
    EXEMPTION = "EXEMPTION"
    SELECTION_PROCESS = "SELECTION_PROCESS"
    GENERAL = "GENERAL"


class NodeType(str, Enum):
    POLICY = "POLICY"
    SCHEME = "SCHEME"
    NOTIFICATION = "NOTIFICATION"
    DOCUMENT = "DOCUMENT"
    CLAUSE = "CLAUSE"
    ELIGIBILITY_CONDITION = "ELIGIBILITY_CONDITION"
    AUTHORITY = "AUTHORITY"
    DEADLINE = "DEADLINE"
    BENEFICIARY_GROUP = "BENEFICIARY_GROUP"
    AMENDMENT = "AMENDMENT"


class RelationshipType(str, Enum):
    AMENDS = "AMENDS"
    REPLACES = "REPLACES"
    REFERENCES = "REFERENCES"
    ISSUED_BY = "ISSUED_BY"
    APPLIES_TO = "APPLIES_TO"
    CONTAINS = "CONTAINS"
    EFFECTIVE_FROM = "EFFECTIVE_FROM"
    SUPERSEDES = "SUPERSEDES"
    MODIFIES = "MODIFIES"
    RELATED_TO = "RELATED_TO"


class EvidenceRecord(BaseModel):
    """
    Evidence record supporting any regulatory deduction, change classification,
    impact projection or conflict detection.
    """
    document_id: str = Field(..., description="ID of source document")
    clause_id: Optional[str] = Field(None, description="Clause ID if applicable")
    source_url: Optional[str] = Field(None, description="Official URL of source document")
    exact_supporting_text: str = Field(..., description="Exact verbatim text snippet supporting the finding")
    page_or_section: Optional[str] = Field(None, description="Page number or section reference in document")
    is_inferred: bool = Field(False, description="Whether this conclusion is directly stated or logically inferred")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Verification confidence score (0.0 to 1.0)")
    notes: Optional[str] = Field(None, description="Optional reasoning notes")


class StructuredValue(BaseModel):
    """
    Structured extraction of numeric limits, financial thresholds, percentages,
    or categorical parameters from legal clauses.
    """
    value_type: str = Field(..., description="E.g. 'income_limit', 'scholarship_amount', 'percentage', 'ratio', 'date'")
    raw_text: Optional[str] = Field(None, description="Raw text snippet representing value")
    numeric_amount: Optional[float] = Field(None, description="Standardized numeric scalar (e.g. 250000.0)")
    currency: Optional[str] = Field("INR", description="Currency code (INR, etc.)")
    unit: Optional[str] = Field(None, description="Unit of measurement, e.g. 'per_annum', 'per_month', 'percent'")
    interval_min: Optional[float] = Field(None, description="Lower bound if interval")
    interval_max: Optional[float] = Field(None, description="Upper bound if interval")
    extra_attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional context attributes")


class AffectedGroup(BaseModel):
    """
    Represents a specific demographic, financial, or academic group affected by a policy change.
    """
    group_name: str = Field(..., description="E.g. 'Undergraduate SC Students', 'Annual Income INR 2.0L - 2.5L'")
    category_type: str = Field(
        ...,
        description="Category dimension: 'income_level', 'social_category', 'education_level', 'institution_type', 'applicant_status'"
    )
    impact_nature: str = Field(
        ...,
        description="'EXPLICITLY_AFFECTED', 'POTENTIALLY_ELIGIBLE', 'POTENTIALLY_EXCLUDED', 'REQUIREMENTS_CHANGED', 'UNRESOLVED'"
    )
    details: str = Field(..., description="Clear explanation of how this group is impacted")
    criteria_delta: Optional[Dict[str, Any]] = Field(None, description="Deterministic delta if applicable")
    evidence: List[EvidenceRecord] = Field(default_factory=list, description="Evidence trail supporting impact")


class Clause(BaseModel):
    """
    Extracted clause structure provided by Person 1's ingestion pipeline.
    """
    id: str = Field(..., description="Unique clause identifier (e.g. 'PMS-SC-2020-CL-4.1')")
    document_id: str = Field(..., description="Parent document identifier")
    clause_number: str = Field(..., description="Clause or paragraph number, e.g. '4.1', 'Section 3(a)'")
    title: Optional[str] = Field(None, description="Clause title or heading if available")
    section: Optional[str] = Field(None, description="Parent section or chapter")
    text: str = Field(..., description="Original clause text")
    normalized_text: Optional[str] = Field(None, description="Normalized clause text for comparison")
    parent_clause_id: Optional[str] = Field(None, description="Parent clause ID if hierarchical")
    clause_type: ClauseType = Field(default=ClauseType.GENERAL, description="Regulatory clause classification")
    structured_attributes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parsed values: income_limit, marks_threshold, amount, age_limit, target_categories, etc."
    )
    page_number: Optional[int] = Field(None, description="Page number in original PDF/gazette")
    subclauses: List[str] = Field(default_factory=list, description="List of child clause IDs")


class Document(BaseModel):
    """
    Structured policy document containing metadata and clauses from Person 1.
    """
    id: str = Field(..., description="Unique document ID (e.g. 'DOC-MoSJE-PMS-SC-2020')")
    title: str = Field(..., description="Full legal title of the document/notification")
    scheme_name: str = Field(..., description="Standardized scheme name (e.g. 'Post-Matric Scholarship for SC')")
    ministry: str = Field(..., description="Issuing Ministry / Department")
    document_type: DocumentType = Field(..., description="Type of regulatory document")
    order_number: Optional[str] = Field(None, description="Official file or order number (e.g. '11014/01/2018-SCD-I')")
    publication_date: Optional[str] = Field(None, description="Publication date (YYYY-MM-DD)")
    effective_date: Optional[str] = Field(None, description="Effective date when provisions take effect (YYYY-MM-DD)")
    valid_until: Optional[str] = Field(None, description="Validity end date or FY (e.g. '2025-26')")
    source_url: Optional[str] = Field(None, description="Official government portal URL")
    version: Optional[str] = Field("1.0", description="Policy version string")
    status: Optional[str] = Field("ACTIVE", description="Legal status: 'ACTIVE', 'AMENDED', 'SUPERSEDED', 'PROVISIONAL'")
    clauses: List[Clause] = Field(default_factory=list, description="Extracted clauses")
    references: List[Dict[str, str]] = Field(
        default_factory=list,
        description="References to older documents: [{'target_document_id': '...', 'relationship': 'AMENDS'}]"
    )


class ChangeRecord(BaseModel):
    """
    The authoritative change record defined in Section 4 of the project specifications.
    Consumed by Person 3 for state management and API delivery.
    """
    change_id: str = Field(..., description="Unique identifier for this detected change")
    document_id: str = Field(..., description="Current document ID where change appears")
    previous_document_id: Optional[str] = Field(None, description="Previous document ID being compared against")
    clause_id: str = Field(..., description="Affected clause ID in current or previous document")
    change_type: ChangeType = Field(..., description="Classification of regulatory change")
    previous_text: Optional[str] = Field(None, description="Previous clause text")
    current_text: Optional[str] = Field(None, description="Current clause text")
    previous_value: Optional[Any] = Field(None, description="Previous structured value or threshold")
    current_value: Optional[Any] = Field(None, description="Current structured value or threshold")
    effective_from: Optional[str] = Field(None, description="Date from which change is legally effective (YYYY-MM-DD)")
    affected_groups: List[Any] = Field(default_factory=list, description="List of AffectedGroup objects or dicts")
    evidence: List[EvidenceRecord] = Field(default_factory=list, description="Supporting evidence records")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in change detection (0.0 to 1.0)")
    uncertainties: List[str] = Field(default_factory=list, description="Specific uncertainties or caveats identified")


class ConflictReport(BaseModel):
    """
    Identifies conflicting provisions, supersession questions, or unresolved ambiguities.
    """
    conflict_id: str = Field(..., description="Unique conflict identifier")
    conflict_type: str = Field(
        ...,
        description="'DIRECT_CONTRADICTION', 'COMPETING_AMENDMENT', 'AMBIGUOUS_SCOPE', 'POTENTIAL_SUPERSEDED', 'UNRESOLVED_TEMPORAL_OVERLAP'"
    )
    description: str = Field(..., description="Clear explanation of the tension or conflict")
    conflicting_clause_ids: List[str] = Field(default_factory=list, description="IDs of clauses in conflict")
    document_ids: List[str] = Field(default_factory=list, description="IDs of documents involved")
    scheme_name: str = Field(..., description="Scheme name")
    is_genuine_contradiction: bool = Field(
        ...,
        description="True if actual legal contradiction, False if provisions address distinct cohorts/temporal windows"
    )
    distinct_scopes_identified: Optional[str] = Field(
        None,
        description="Explanation if conflict is resolved by distinct target groups, levels, or temporal scopes"
    )
    resolution_status: str = Field(
        "UNRESOLVED",
        description="'RESOLVED_BY_TEMPORAL_PRECEDENCE', 'RESOLVED_BY_SPECIALITY', 'UNRESOLVED', 'REQUIRES_CLARIFICATION'"
    )
    uncertainties: List[str] = Field(default_factory=list, description="Unresolved legal questions")
    evidence: List[EvidenceRecord] = Field(default_factory=list, description="Evidence trail")


class ImpactAnalysisReport(BaseModel):
    """
    User-facing regulatory impact report explaining who is affected,
    deterministic eligibility deltas, and practical consequences.
    """
    report_id: str = Field(..., description="Unique impact report ID")
    scheme_name: str = Field(..., description="Target scheme name")
    base_document_id: Optional[str] = Field(None, description="Baseline policy document ID")
    target_document_id: str = Field(..., description="Amending / new policy document ID")
    summary: str = Field(..., description="Executive summary of policy changes and impact")
    explicitly_affected_groups: List[AffectedGroup] = Field(default_factory=list)
    potentially_affected_groups: List[AffectedGroup] = Field(default_factory=list)
    unresolved_groups: List[AffectedGroup] = Field(default_factory=list)
    deterministic_deltas: List[Dict[str, Any]] = Field(default_factory=list)
    practical_consequences: List[str] = Field(default_factory=list)
    evidence_trail: List[EvidenceRecord] = Field(default_factory=list)
    generated_at: str = Field(..., description="ISO 8601 timestamp of report generation")


class TemporalApplicabilityResult(BaseModel):
    """
    Point-in-time regulatory applicability result.
    Answers: 'What were the eligibility requirements on date X?'
    """
    query_date: str = Field(..., description="Target query date (YYYY-MM-DD)")
    scheme_name: str = Field(..., description="Scheme queried")
    status: str = Field(..., description="'RESOLVED', 'PARTIALLY_RESOLVED', 'UNRESOLVED'")
    applicable_document_ids: List[str] = Field(default_factory=list)
    applicable_clauses: List[Clause] = Field(default_factory=list)
    superseded_clauses: List[Dict[str, Any]] = Field(default_factory=list)
    active_amendments: List[Dict[str, Any]] = Field(default_factory=list)
    unresolved_reasons: List[str] = Field(default_factory=list)
    evidence: List[EvidenceRecord] = Field(default_factory=list)


class AgentInvestigationStep(BaseModel):
    """Execution step log in the multi-step regulatory investigation agent."""
    step_number: int
    step_name: str
    description: str
    tool_invoked: Optional[str] = None
    status: str = "COMPLETED"
    details: Dict[str, Any] = Field(default_factory=dict)


class AgentQueryRequest(BaseModel):
    """User inquiry request to the AI regulatory investigation agent."""
    query: str = Field(..., description="Natural language question regarding government scholarship policy")
    scheme_name: Optional[str] = Field(None, description="Target scheme if known")
    target_date: Optional[str] = Field(None, description="Target evaluation date (YYYY-MM-DD) if applicable")
    beneficiary_group: Optional[str] = Field(None, description="Specific applicant demographic or economic cohort")
    session_id: Optional[str] = Field(None, description="Optional conversational session identifier")


class AgentQueryResponse(BaseModel):
    """Structured response from the agentic regulatory investigation."""
    session_id: str
    query: str
    scheme_name: Optional[str] = None
    direct_answer: str = Field(..., description="Authoritative, evidence-backed answer")
    reasoning_type: str = Field("FACTUAL_DETERMINISTIC", description="Reasoning distinction: RETRIEVED_FACT, DETERMINISTIC_CALCULATION, AI_INFERRED, or UNRESOLVED")
    steps_taken: List[AgentInvestigationStep] = Field(default_factory=list)
    detected_changes: List[ChangeRecord] = Field(default_factory=list)
    impact_summary: Optional[str] = None
    affected_groups: List[AffectedGroup] = Field(default_factory=list)
    evidence_citations: List[EvidenceRecord] = Field(default_factory=list)
    verification_confidence: float = Field(1.0, ge=0.0, le=1.0)
    uncertainties: List[str] = Field(default_factory=list)
    actionable_recommendations: List[str] = Field(default_factory=list)
    source_documents: List[Dict[str, Any]] = Field(default_factory=list)


class DocumentIngestRequest(BaseModel):
    """Payload for submitting new official policy documents or raw text for extraction."""
    raw_text: Optional[str] = Field(None, description="Raw text of the gazette / notification")
    file_name: Optional[str] = Field(None, description="Original filename (e.g. pms_sc_2020.pdf)")
    document_type: DocumentType = Field(default=DocumentType.NOTIFICATION)
    scheme_name: str = Field(..., description="Target scheme name")
    ministry: str = Field(..., description="Issuing Ministry")
    order_number: Optional[str] = None
    publication_date: Optional[str] = None
    effective_date: Optional[str] = None
    source_url: Optional[str] = None
    version: Optional[str] = "1.0"
    structured_document: Optional[Document] = Field(None, description="Pre-structured Document from Person 1 if already parsed")


class CompareRequest(BaseModel):
    """Request to compare two policy document versions."""
    base_document_id: Optional[str] = Field(None, description="Baseline policy document ID")
    target_document_id: str = Field(..., description="Target / amending document ID")
    scheme_name: Optional[str] = None


class ImpactRequest(BaseModel):
    """Request to generate impact analysis for a scheme or revision."""
    target_document_id: str = Field(..., description="Target policy document ID")
    base_document_id: Optional[str] = Field(None, description="Baseline policy document ID")
    scheme_name: Optional[str] = None
