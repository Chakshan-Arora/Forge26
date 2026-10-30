"""
Policy Intel Intelligence Engine - Unified Integration Interface.

This module provides the primary high-level facade (PolicyIntelEngine)
consumed by Person 3 (Backend API / FastAPI) and other services.

Features:
- Document registration and repository management
- Automated clause-level change detection between revisions
- Temporal regulatory knowledge graph maintenance
- Point-in-time eligibility and applicability queries
- Evidence-backed student impact analysis
- Conflict, supersession, and dependency gap detection
- Regulatory audit trail extraction
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

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
    Unified intelligence facade for the Policy Intel platform.
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

    def register_document(self, document: Document) -> None:
        """
        Registers a structured policy document from Person 1 into the engine,
        ingesting it into the knowledge graph and temporal resolver.
        """
        self._documents[document.id] = document
        self.temporal_resolver.register_document(document)
        self.conflict_detector.register_documents([document])

    def register_documents(self, documents: List[Document]) -> None:
        """Batch registers multiple documents."""
        for doc in documents:
            self.register_document(doc)

    # Aliases for flexible integration
    ingest_document = register_document
    ingest_documents = register_documents

    def get_document(self, document_id: str) -> Optional[Document]:
        """Retrieves a registered document by its unique ID."""
        return self._documents.get(document_id)

    def list_documents(self) -> List[Document]:
        """Returns all currently registered documents."""
        return list(self._documents.values())

    def compare_documents(
        self,
        base_document: Optional[Union[str, Document]] = None,
        target_document: Optional[Union[str, Document]] = None,
        update_graph: bool = True,
        base_document_id: Optional[str] = None,
        target_document_id: Optional[str] = None,
    ) -> Tuple[List[ChangeRecord], ChangeDetectionSummary]:
        """
        Compares two policy documents at clause level.
        Accepts either document IDs (str), Document objects, or base/target_document_id keyword arguments.
        Produces authoritative ChangeRecords and updates the regulatory knowledge graph.
        """
        target = target_document or target_document_id
        base = base_document or base_document_id

        if target is None:
            raise ValueError("Target document or target_document_id must be provided.")

        if isinstance(target, Document):
            self.register_document(target)
            target_doc = target
        else:
            target_doc = self.get_document(target)
            if not target_doc:
                raise ValueError(f"Target document '{target}' not found in engine.")

        if isinstance(base, Document):
            self.register_document(base)
            base_doc = base
        elif base:
            base_doc = self.get_document(base)
            if not base_doc:
                raise ValueError(f"Base document '{base}' not found in engine.")
        else:
            base_doc = None

        # Execute clause-level change detection
        changes = self.detector.compare_documents(
            previous_doc=base_doc,
            current_doc=target_doc
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

    def analyze_impact(
        self,
        target_document: Union[str, Document],
        base_document: Optional[Union[str, Document]] = None,
        changes: Optional[List[ChangeRecord]] = None
    ) -> ImpactAnalysisReport:
        """
        Executes end-to-end impact analysis for a policy document or amendment.
        Identifies affected student cohorts, deterministic interval shifts, and practical actions.
        """
        if isinstance(target_document, Document):
            self.register_document(target_document)
            target_doc = target_document
        else:
            target_doc = self.get_document(target_document)
            if not target_doc:
                raise ValueError(f"Target document '{target_document}' not found in engine.")

        if isinstance(base_document, Document):
            self.register_document(base_document)
            base_doc = base_document
        elif base_document:
            base_doc = self.get_document(base_document)
        else:
            base_doc = None

        # Detect changes if not provided
        if changes is None and base_doc is not None:
            changes = self.detector.compare_documents(
                previous_doc=base_doc,
                current_doc=target_doc
            )
        elif changes is None:
            changes = []

        # Synthesize into an ImpactAnalysisReport
        return self.impact_analyzer.analyze_document_changes(
            target_document=target_doc,
            changes=changes,
            base_document=base_doc
        )

    def query_eligibility_at_date(
        self,
        scheme_name: str,
        query_date: str
    ) -> TemporalApplicabilityResult:
        """
        Point-in-time regulatory query:
        Answers: 'What were the eligibility requirements on date X?'
        """
        return self.temporal_resolver.resolve_applicability_at_date(
            scheme_name=scheme_name,
            query_date_str=query_date
        )

    resolve_applicability = query_eligibility_at_date

    def trace_condition(
        self,
        scheme_name: str,
        condition_keyword: str
    ) -> List[Dict[str, Any]]:
        """
        Provenance query:
        Answers: 'Which notification introduced this particular condition?'
        """
        return self.temporal_resolver.trace_condition_origin(
            scheme_name=scheme_name,
            condition_keyword=condition_keyword
        )

    trace_condition_origin = trace_condition

    def detect_conflicts(self, scheme_name: str) -> List[ConflictReport]:
        """
        Scans all documents under a scheme for contradictions, competing amendments,
        and missing historical version dependencies.
        """
        return self.conflict_detector.detect_conflicts_for_scheme(scheme_name=scheme_name)

    def export_graph_dict(self) -> Dict[str, Any]:
        """Exports the regulatory knowledge graph to a JSON-serializable dictionary."""
        return self.graph.to_dict()

    get_graph_dict = export_graph_dict

    def export_graph_mermaid(self) -> str:
        """Exports the regulatory knowledge graph in Mermaid syntax for markdown rendering."""
        if isinstance(self.graph, NetworkXRegulatoryGraph):
            return self.graph.to_mermaid()
        return "flowchart TD\n    NodeA --> NodeB"

    get_graph_mermaid = export_graph_mermaid

    def get_audit_trail(self, evidence_list: List[EvidenceRecord]) -> str:
        """Generates a formatted human-readable evidence audit trail."""
        return EvidenceEngine.format_audit_trail(evidence_list)
