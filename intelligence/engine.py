"""
Policy Intel Intelligence Engine - Unified Integration Interface.

This module provides the authoritative high-level facade (PolicyIntelEngine)
consumed by Person 3 (Backend API / FastAPI) and other platform services.

Authoritative Method Signatures:
- ingest_document(document: Document) -> None (alias: register_document)
- ingest_documents(documents: List[Document]) -> None (alias: register_documents)
- compare_documents(base_document, target_document, update_graph=True, method="optimal")
    -> Tuple[List[ChangeRecord], ChangeDetectionSummary]
- detect_changes(base_document, target_document, update_graph=True, method="optimal")
    -> List[ChangeRecord]
- resolve_applicability(scheme_name: str, query_date: str) -> TemporalApplicabilityResult
    (alias: query_eligibility_at_date)
- trace_condition_origin(scheme_name: str, condition_keyword: str) -> List[Dict[str, Any]]
    (alias: trace_condition)
- analyze_impact(target_document, base_document=None, changes=None) -> ImpactAnalysisReport
- detect_conflicts(scheme_name: str) -> List[ConflictReport]
- export_graph_dict() -> Dict[str, Any] (alias: get_graph_dict)
- export_graph_mermaid() -> str (alias: get_graph_mermaid)
- get_audit_trail(evidence_list: List[EvidenceRecord]) -> str
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Union

from shared.schemas import (
    Document,
    Clause,
    ChangeRecord,
    ConflictReport,
    ImpactAnalysisReport,
    TemporalApplicabilityResult,
    EvidenceRecord,
)
from intelligence.config import IntelligenceSettings, DEFAULT_SETTINGS
from intelligence.change_detector import ChangeDetector, ChangeDetectionSummary
from intelligence.change_classifier import ChangeClassifier
from intelligence.clause_matcher import ClauseMatcher
from intelligence.knowledge_graph import BaseRegulatoryGraph, NetworkXRegulatoryGraph
from intelligence.temporal_resolver import TemporalResolver
from intelligence.impact_analyzer import ImpactAnalyzer
from intelligence.conflict_detector import ConflictDetector
from intelligence.evidence_engine import EvidenceEngine


class PolicyIntelEngine:
    """
    Authoritative unified intelligence facade for the Policy Intel platform.
    Connects ingestion inputs from Person 1 with API endpoints for Person 3.
    """

    def __init__(
        self,
        settings: Optional[IntelligenceSettings] = None,
        graph_backend: Optional[BaseRegulatoryGraph] = None
    ):
        self.settings = settings or DEFAULT_SETTINGS
        self.graph = graph_backend or NetworkXRegulatoryGraph()
        
        # Sub-engines
        self.matcher = ClauseMatcher(config=self.settings.matcher)
        self.detector = ChangeDetector(matcher_config=self.settings.matcher)
        self.temporal_resolver = TemporalResolver(graph=self.graph)
        self.impact_analyzer = ImpactAnalyzer()
        self.conflict_detector = ConflictDetector()

        # In-memory document storage
        self._documents: Dict[str, Document] = {}

    # -------------------------------------------------------------------------
    # 1. Document Ingestion & Registration
    # -------------------------------------------------------------------------

    def ingest_document(self, document: Document) -> None:
        """
        Authoritative: Registers a structured policy document from Person 1,
        ingesting it into the knowledge graph and temporal resolver.
        """
        self._documents[document.id] = document
        self.temporal_resolver.register_document(document)
        self.conflict_detector.register_documents([document])

    def ingest_documents(self, documents: List[Document]) -> None:
        """Batch registers multiple documents."""
        for doc in documents:
            self.ingest_document(doc)

    # Aliases
    register_document = ingest_document
    register_documents = ingest_documents

    def get_document(self, document_id: str) -> Optional[Document]:
        """Retrieves a registered document by its unique ID."""
        return self._documents.get(document_id)

    def list_documents(self) -> List[Document]:
        """Returns all currently registered documents."""
        return list(self._documents.values())

    # -------------------------------------------------------------------------
    # 2. Clause-Level Policy Comparison
    # -------------------------------------------------------------------------

    def compare_documents(
        self,
        base_document: Optional[Union[str, Document]] = None,
        target_document: Optional[Union[str, Document]] = None,
        update_graph: bool = True,
        method: str = "optimal",
        base_document_id: Optional[str] = None,
        target_document_id: Optional[str] = None,
    ) -> Tuple[List[ChangeRecord], ChangeDetectionSummary]:
        """
        Authoritative: Compares two policy documents at clause level.
        Accepts either document IDs (str), Document objects, or keyword args.
        Returns a tuple of (List[ChangeRecord], ChangeDetectionSummary).
        """
        target = target_document or target_document_id
        base = base_document or base_document_id

        if target is None:
            raise ValueError("Target document or target_document_id must be provided.")

        if isinstance(target, Document):
            self.ingest_document(target)
            target_doc = target
        else:
            target_doc = self.get_document(target)
            if not target_doc:
                raise ValueError(f"Target document '{target}' not found in engine.")

        if isinstance(base, Document):
            self.ingest_document(base)
            base_doc = base
        elif base:
            base_doc = self.get_document(base)
            if not base_doc:
                raise ValueError(f"Base document '{base}' not found in engine.")
        else:
            base_doc = None

        # Execute clause-level change detection (optimal Kuhn-Munkres or greedy)
        changes = self.detector.compare_documents(
            previous_doc=base_doc,
            current_doc=target_doc,
            method=method
        )

        # Ingest detected changes into the regulatory knowledge graph
        if update_graph:
            for chg in changes:
                if isinstance(self.graph, NetworkXRegulatoryGraph):
                    self.graph.ingest_change_record(chg)

        # Compute statistical summary
        summary = self.detector.summarize_changes(
            previous_doc=base_doc,
            current_doc=target_doc,
            changes=changes
        )

        return changes, summary

    def detect_changes(
        self,
        base_document: Optional[Union[str, Document]] = None,
        target_document: Optional[Union[str, Document]] = None,
        update_graph: bool = True,
        method: str = "optimal",
        base_document_id: Optional[str] = None,
        target_document_id: Optional[str] = None,
    ) -> List[ChangeRecord]:
        """Convenience method returning solely the List[ChangeRecord]."""
        changes, _ = self.compare_documents(
            base_document=base_document,
            target_document=target_document,
            update_graph=update_graph,
            method=method,
            base_document_id=base_document_id,
            target_document_id=target_document_id
        )
        return changes

    def get_change_summary(
        self,
        base_document: Optional[Union[str, Document]],
        target_document: Union[str, Document],
        changes: List[ChangeRecord]
    ) -> ChangeDetectionSummary:
        """Returns statistical metrics on detected changes."""
        base_doc = base_document if isinstance(base_document, Document) else (self.get_document(base_document) if base_document else None)
        target_doc = target_document if isinstance(target_document, Document) else self.get_document(target_document)
        return self.detector.summarize_changes(base_doc, target_doc, changes)

    # -------------------------------------------------------------------------
    # 3. Multi-Dimensional Impact Analysis
    # -------------------------------------------------------------------------

    def analyze_impact(
        self,
        target_document: Optional[Union[str, Document]] = None,
        base_document: Optional[Union[str, Document]] = None,
        changes: Optional[List[ChangeRecord]] = None,
        target_document_id: Optional[str] = None,
        base_document_id: Optional[str] = None,
    ) -> ImpactAnalysisReport:
        """
        Authoritative: Executes end-to-end impact analysis for a policy document or amendment.
        Identifies affected student cohorts, deterministic interval shifts, and practical actions.
        """
        target = target_document or target_document_id
        base = base_document or base_document_id

        if target is None:
            raise ValueError("Target document or target_document_id must be provided.")

        if isinstance(target, Document):
            self.ingest_document(target)
            target_doc = target
        else:
            target_doc = self.get_document(target)
            if not target_doc:
                raise ValueError(f"Target document '{target}' not found in engine.")

        if isinstance(base, Document):
            self.ingest_document(base)
            base_doc = base
        elif base:
            base_doc = self.get_document(base)
        else:
            base_doc = None

        # Detect changes if not provided
        if changes is None and base_doc is not None:
            changes, _ = self.compare_documents(
                base_document=base_doc,
                target_document=target_doc
            )
        elif changes is None:
            changes = []

        # Synthesize into an ImpactAnalysisReport
        return self.impact_analyzer.analyze_document_changes(
            target_document=target_doc,
            changes=changes,
            base_document=base_doc
        )

    # -------------------------------------------------------------------------
    # 4. Temporal Applicability & Provenance
    # -------------------------------------------------------------------------

    def resolve_applicability(
        self,
        scheme_name: str,
        query_date: str
    ) -> TemporalApplicabilityResult:
        """
        Authoritative: Point-in-time regulatory query:
        Answers: 'What were the eligibility requirements on date X?'
        """
        return self.temporal_resolver.resolve_applicability_at_date(
            scheme_name=scheme_name,
            query_date_str=query_date
        )

    # Alias
    query_eligibility_at_date = resolve_applicability

    def trace_condition_origin(
        self,
        scheme_name: str,
        condition_keyword: str
    ) -> List[Dict[str, Any]]:
        """
        Authoritative: Provenance query:
        Answers: 'Which notification introduced this particular condition?'
        """
        return self.temporal_resolver.trace_condition_origin(
            scheme_name=scheme_name,
            condition_keyword=condition_keyword
        )

    # Alias
    trace_condition = trace_condition_origin

    # -------------------------------------------------------------------------
    # 5. Conflict & Dependency Auditing
    # -------------------------------------------------------------------------

    def detect_conflicts(self, scheme_name: str) -> List[ConflictReport]:
        """
        Authoritative: Scans all documents under a scheme for contradictions,
        competing amendments, distinct scope rules, and missing historical dependencies.
        """
        return self.conflict_detector.detect_conflicts_for_scheme(scheme_name=scheme_name)

    # -------------------------------------------------------------------------
    # 6. Knowledge Graph & Evidentiary Exports
    # -------------------------------------------------------------------------

    def export_graph_dict(self) -> Dict[str, Any]:
        """Authoritative: Exports the regulatory knowledge graph to a JSON-serializable dictionary."""
        return self.graph.to_dict()

    get_graph_dict = export_graph_dict

    def export_graph_mermaid(self) -> str:
        """Authoritative: Exports the regulatory knowledge graph in Mermaid syntax for markdown rendering."""
        if isinstance(self.graph, NetworkXRegulatoryGraph):
            return self.graph.to_mermaid()
        return "flowchart TD\n    NodeA --> NodeB"

    get_graph_mermaid = export_graph_mermaid

    def get_audit_trail(self, evidence_list: List[EvidenceRecord]) -> str:
        """Authoritative: Generates a formatted human-readable evidence audit trail."""
        return EvidenceEngine.format_audit_trail(evidence_list)
