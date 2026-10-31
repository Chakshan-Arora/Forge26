"""
Temporal Regulatory Knowledge Graph Module.

Provides an abstract interface and NetworkX implementation for managing
regulatory entities, relationships, temporal validity, and evidence trails.
Designed for seamless swapping to Neo4j in future iterations.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
import networkx as nx

from shared.schemas import (
    NodeType,
    RelationshipType,
    Document,
    Clause,
    ChangeRecord,
    EvidenceRecord,
    AffectedGroup,
)


class BaseRegulatoryGraph(ABC):
    """Abstract interface for regulatory knowledge graphs."""

    @abstractmethod
    def add_node(
        self,
        node_id: str,
        node_type: NodeType,
        properties: Optional[Dict[str, Any]] = None,
        temporal_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        pass

    @abstractmethod
    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship: RelationshipType,
        properties: Optional[Dict[str, Any]] = None,
        evidence: Optional[List[EvidenceRecord]] = None,
        temporal_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        pass

    @abstractmethod
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_edges(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relationship: Optional[RelationshipType] = None,
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass


class NetworkXRegulatoryGraph(BaseRegulatoryGraph):
    """
    NetworkX MultiDiGraph implementation of the Regulatory Knowledge Graph.
    Retains temporal metadata, evidence records, and regulatory relationship types.
    """

    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def add_node(
        self,
        node_id: str,
        node_type: NodeType,
        properties: Optional[Dict[str, Any]] = None,
        temporal_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        props = properties or {}
        temporal = temporal_info or {}
        
        self.graph.add_node(
            node_id,
            node_type=node_type.value if hasattr(node_type, "value") else str(node_type),
            properties=props,
            temporal=temporal,
            updated_at=datetime.utcnow().isoformat()
        )

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship: RelationshipType,
        properties: Optional[Dict[str, Any]] = None,
        evidence: Optional[List[EvidenceRecord]] = None,
        temporal_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        props = properties or {}
        temporal = temporal_info or {}
        ev_list = [e.model_dump() if hasattr(e, "model_dump") else e for e in (evidence or [])]
        rel_val = relationship.value if hasattr(relationship, "value") else str(relationship)

        self.graph.add_edge(
            source_id,
            target_id,
            key=f"{source_id}->{rel_val}->{target_id}",
            relationship=rel_val,
            properties=props,
            evidence=ev_list,
            temporal=temporal
        )

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        if self.graph.has_node(node_id):
            return dict(self.graph.nodes[node_id])
        return None

    def get_edges(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relationship: Optional[RelationshipType] = None,
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        rel_str = relationship.value if hasattr(relationship, "value") else (str(relationship) if relationship else None)

        for u, v, key, data in self.graph.edges(keys=True, data=True):
            if source_id and u != source_id:
                continue
            if target_id and v != target_id:
                continue
            if rel_str and data.get("relationship") != rel_str:
                continue
            results.append({
                "source": u,
                "target": v,
                "key": key,
                "relationship": data.get("relationship"),
                "properties": data.get("properties", {}),
                "evidence": data.get("evidence", []),
                "temporal": data.get("temporal", {})
            })
        return results

    def ingest_document(self, document: Document) -> None:
        """
        Populates graph with Document, Scheme, Authority, Clauses,
        and internal/external regulatory relationships.
        """
        doc_temporal = {
            "publication_date": document.publication_date,
            "effective_date": document.effective_date,
            "valid_until": document.valid_until,
        }

        # 1. DOCUMENT Node
        self.add_node(
            node_id=document.id,
            node_type=NodeType.DOCUMENT,
            properties={
                "title": document.title,
                "document_type": document.document_type.value,
                "order_number": document.order_number,
                "source_url": document.source_url,
                "version": document.version,
                "status": document.status
            },
            temporal_info=doc_temporal
        )

        # 2. SCHEME Node
        scheme_id = f"SCHEME-{document.scheme_name.replace(' ', '_').upper()}"
        self.add_node(
            node_id=scheme_id,
            node_type=NodeType.SCHEME,
            properties={"name": document.scheme_name}
        )
        self.add_edge(
            source_id=document.id,
            target_id=scheme_id,
            relationship=RelationshipType.REFERENCES,
            properties={"role": "governs_scheme"},
            temporal_info=doc_temporal
        )

        # 3. AUTHORITY Node
        if document.ministry:
            auth_id = f"AUTH-{document.ministry.replace(' ', '_').upper()}"
            self.add_node(
                node_id=auth_id,
                node_type=NodeType.AUTHORITY,
                properties={"name": document.ministry}
            )
            self.add_edge(
                source_id=document.id,
                target_id=auth_id,
                relationship=RelationshipType.ISSUED_BY,
                temporal_info=doc_temporal
            )

        # 4. CLAUSE Nodes and CONTAINS edges
        for clause in document.clauses:
            clause_temporal = dict(doc_temporal)
            self.add_node(
                node_id=clause.id,
                node_type=NodeType.CLAUSE,
                properties={
                    "clause_number": clause.clause_number,
                    "title": clause.title,
                    "section": clause.section,
                    "clause_type": clause.clause_type.value if hasattr(clause.clause_type, "value") else str(clause.clause_type),
                    "text": clause.text,
                    "structured_attributes": clause.structured_attributes,
                    "page_number": clause.page_number
                },
                temporal_info=clause_temporal
            )
            self.add_edge(
                source_id=document.id,
                target_id=clause.id,
                relationship=RelationshipType.CONTAINS,
                temporal_info=clause_temporal
            )

            # Check if this clause defines an ELIGIBILITY condition
            if clause.clause_type.value == "ELIGIBILITY" or "income_limit" in clause.structured_attributes:
                cond_id = f"COND-{clause.id}"
                self.add_node(
                    node_id=cond_id,
                    node_type=NodeType.ELIGIBILITY_CONDITION,
                    properties={
                        "condition_type": clause.structured_attributes.get("value_type", "eligibility_criterion"),
                        "raw_criteria": clause.structured_attributes
                    },
                    temporal_info=clause_temporal
                )
                self.add_edge(
                    source_id=clause.id,
                    target_id=cond_id,
                    relationship=RelationshipType.CONTAINS,
                    temporal_info=clause_temporal
                )

        # 5. External Document References (e.g. AMENDS, SUPERSEDES)
        for ref in document.references:
            target_doc_id = ref.get("target_document_id")
            rel_name = ref.get("relationship", "REFERENCES").upper()
            rel_type = getattr(RelationshipType, rel_name, RelationshipType.REFERENCES)
            if target_doc_id:
                self.add_edge(
                    source_id=document.id,
                    target_id=target_doc_id,
                    relationship=rel_type,
                    properties={"stated_in": document.id},
                    temporal_info=doc_temporal
                )

    def ingest_change_record(self, change: ChangeRecord) -> None:
        """
        Integrates a detected ChangeRecord into the graph, connecting previous
        and current clauses with MODIFIES, REPLACES, or AMENDS relationships.
        """
        # Node for the Amendment / Change event
        chg_node_id = change.change_id
        self.add_node(
            node_id=chg_node_id,
            node_type=NodeType.AMENDMENT,
            properties={
                "change_type": change.change_type.value,
                "confidence": change.confidence,
                "uncertainties": change.uncertainties,
                "previous_value": change.previous_value,
                "current_value": change.current_value,
            },
            temporal_info={"effective_from": change.effective_from}
        )

        # Connect current clause to amendment event
        self.add_edge(
            source_id=change.clause_id,
            target_id=chg_node_id,
            relationship=RelationshipType.RELATED_TO,
            evidence=change.evidence,
            temporal_info={"effective_from": change.effective_from}
        )

        # If previous document or clause is known, link them
        if change.previous_document_id:
            # Map change type to relationship
            rel = RelationshipType.MODIFIES
            if change.change_type.value == "REPLACED":
                rel = RelationshipType.REPLACES
            elif change.change_type.value == "ADDED":
                rel = RelationshipType.AMENDS

            self.add_edge(
                source_id=change.document_id,
                target_id=change.previous_document_id,
                relationship=rel,
                evidence=change.evidence,
                temporal_info={"effective_from": change.effective_from}
            )

        # Link Affected Groups to Clause / Change
        for grp in change.affected_groups:
            grp_name = grp.group_name if hasattr(grp, "group_name") else grp.get("group_name", "Unknown Cohort")
            grp_node_id = f"GRP-{grp_name.replace(' ', '_').upper()}"
            self.add_node(
                node_id=grp_node_id,
                node_type=NodeType.BENEFICIARY_GROUP,
                properties={"group_name": grp_name}
            )
            self.add_edge(
                source_id=change.clause_id,
                target_id=grp_node_id,
                relationship=RelationshipType.APPLIES_TO,
                evidence=change.evidence,
                temporal_info={"effective_from": change.effective_from}
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes knowledge graph to dictionary for API or persistence."""
        nodes_data = [
            {"id": n, **self.graph.nodes[n]}
            for n in self.graph.nodes
        ]
        edges_data = self.get_edges()
        return {
            "total_nodes": len(nodes_data),
            "total_edges": len(edges_data),
            "nodes": nodes_data,
            "edges": edges_data
        }

    def to_mermaid(self) -> str:
        """Exports graph in Mermaid syntax for markdown rendering."""
        lines = ["flowchart TD"]
        for u, v, data in self.graph.edges(data=True):
            rel = data.get("relationship", "RELATED_TO")
            u_clean = u.replace("-", "_").replace(" ", "_")
            v_clean = v.replace("-", "_").replace(" ", "_")
            lines.append(f'    {u_clean}["{u}"] -->|{rel}| {v_clean}["{v}"]')
        return "\n".join(lines)
