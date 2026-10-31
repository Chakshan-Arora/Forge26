"""
Intelligence Service Adapter.

Connects the FastAPI platform with Person 2's regulatory intelligence engine
(PolicyIntelEngine), maintaining the synchronized in-memory temporal knowledge
graph and executing clause-level diffs, impact analyses, and conflict resolutions.
"""

from __future__ import annotations
import logging
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from intelligence.engine import PolicyIntelEngine
from shared.schemas import (
    Document,
    ChangeRecord,
    ImpactAnalysisReport,
    TemporalApplicabilityResult,
    ConflictReport,
)
from backend.services.persistence_service import (
    list_documents,
    save_change_records,
    save_impact_report,
)
from ingestion.corpus_loader import AuthenticCorpusLoader

logger = logging.getLogger(__name__)


class IntelligenceService:
    """Manages the shared PolicyIntelEngine instance and state transitions."""

    _instance: Optional[IntelligenceService] = None

    def __init__(self):
        self.engine = PolicyIntelEngine()
        self._initialized = False

    @classmethod
    def get_instance(cls) -> IntelligenceService:
        """Singleton accessor."""
        if cls._instance is None:
            cls._instance = IntelligenceService()
        return cls._instance

    def initialize(self, db: Optional[Session] = None) -> None:
        """Pre-loads authentic corpus and registered DB documents into engine."""
        if self._initialized:
            return

        # Always register authentic corpus
        corpus_docs = AuthenticCorpusLoader.load_all()
        for doc in corpus_docs:
            self.engine.register_document(doc)

        # Ingest pairwise comparisons for authentic corpus to populate knowledge graph
        self._precompute_authentic_changes()

        # If DB provided, register any additional stored documents
        if db:
            db_docs = list_documents(db)
            for d in db_docs:
                self.engine.register_document(d)

        self._initialized = True
        logger.info(f"Intelligence engine initialized with {len(self.engine.list_documents())} documents.")

    def _precompute_authentic_changes(self) -> None:
        """Precomputes known pairwise revisions to prime the Knowledge Graph."""
        pairs = [
            ("DOC-MoSJE-PMS-SC-2018", "DOC-MoSJE-PMS-SC-2020"),
            ("DOC-MoE-NMMSS-2017", "DOC-MoE-NMMSS-2022"),
            ("DOC-MoE-PMUSP-CSSS-2015", "DOC-MoE-PMUSP-CSSS-2022"),
        ]
        for base_id, target_id in pairs:
            try:
                base_doc = self.engine.get_document(base_id)
                target_doc = self.engine.get_document(target_id)
                if base_doc and target_doc:
                    self.engine.compare_documents(base_doc, target_doc, update_graph=True)
            except Exception as e:
                logger.warning(f"Failed to precompute change pair {base_id} -> {target_id}: {e}")

    def register_document(self, doc: Document) -> None:
        """Registers a newly ingested document into the intelligence engine."""
        self.engine.register_document(doc)

    def compare_documents(
        self,
        target_document_id: str,
        base_document_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Tuple[List[ChangeRecord], Dict[str, Any]]:
        """
        Executes clause-level change detection between revisions.
        Saves changes to DB if session provided.
        """
        self.initialize(db)
        changes, summary = self.engine.compare_documents(
            base_document_id=base_document_id,
            target_document_id=target_document_id,
            update_graph=True
        )

        if db and changes:
            save_change_records(db, changes)

        summary_dict = {
            "total_changes": summary.total_changes,
            "additions_count": summary.additions_count,
            "removals_count": summary.removals_count,
            "modifications_count": summary.modifications_count,
            "replacements_count": summary.replacements_count,
            "renumbered_count": summary.renumbered_count,
            "total_previous_clauses": summary.total_previous_clauses,
            "total_current_clauses": summary.total_current_clauses,
        }
        return changes, summary_dict

    def analyze_impact(
        self,
        target_document_id: str,
        base_document_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> ImpactAnalysisReport:
        """
        Executes multi-dimensional student impact analysis.
        Persists report to database if db session provided.
        """
        self.initialize(db)
        report = self.engine.analyze_impact(
            target_document_id=target_document_id,
            base_document_id=base_document_id
        )

        if db and report:
            save_impact_report(db, report)

        return report

    def query_temporal_applicability(
        self,
        scheme_name: str,
        query_date: str,
        db: Optional[Session] = None
    ) -> TemporalApplicabilityResult:
        """Resolves point-in-time regulatory applicability on a specific date."""
        self.initialize(db)
        return self.engine.query_eligibility_at_date(scheme_name, query_date)

    def detect_conflicts(
        self,
        scheme_name: str,
        db: Optional[Session] = None
    ) -> List[ConflictReport]:
        """Detects contradictions, competing amendments, or gaps in scheme regulations."""
        self.initialize(db)
        return self.engine.detect_conflicts(scheme_name)

    def get_knowledge_graph_data(self, db: Optional[Session] = None) -> Dict[str, Any]:
        """Returns JSON-serializable regulatory knowledge graph nodes and edges."""
        self.initialize(db)
        return self.engine.export_graph_dict()

    def get_subgraph_data(self, entity_id: str, db: Optional[Session] = None) -> Dict[str, Any]:
        """Returns the immediate neighborhood / subgraph for a given scheme, document, or clause."""
        self.initialize(db)
        full_graph = self.engine.export_graph_dict()
        nodes = full_graph.get("nodes", [])
        edges = full_graph.get("edges", [])

        # Filter nodes directly connected to entity_id
        relevant_node_ids = {entity_id}
        for e in edges:
            if e.get("source") == entity_id:
                relevant_node_ids.add(e.get("target"))
            elif e.get("target") == entity_id:
                relevant_node_ids.add(e.get("source"))

        sub_nodes = [n for n in nodes if n.get("id") in relevant_node_ids]
        sub_edges = [e for e in edges if e.get("source") in relevant_node_ids and e.get("target") in relevant_node_ids]

        return {
            "entity_id": entity_id,
            "nodes": sub_nodes,
            "edges": sub_edges,
            "node_count": len(sub_nodes),
            "edge_count": len(sub_edges),
        }
