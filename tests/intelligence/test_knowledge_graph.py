"""
Tests for Temporal Regulatory Knowledge Graph.
"""

import pytest
from shared.schemas import NodeType, RelationshipType
from intelligence.knowledge_graph import NetworkXRegulatoryGraph
from intelligence.change_detector import ChangeDetector
from data.real_policies import get_pmssc_2018_document, get_pmssc_2020_document


def test_knowledge_graph_ingestion():
    kg = NetworkXRegulatoryGraph()
    doc_2018 = get_pmssc_2018_document()
    doc_2020 = get_pmssc_2020_document()

    kg.ingest_document(doc_2018)
    kg.ingest_document(doc_2020)

    # Check node creation
    doc_node = kg.get_node(doc_2020.id)
    assert doc_node is not None
    assert doc_node["node_type"] == NodeType.DOCUMENT.value

    # Check scheme node creation
    scheme_nodes = [n for n in kg.graph.nodes if n.startswith("SCHEME-")]
    assert len(scheme_nodes) >= 1

    # Check authority node creation
    auth_nodes = [n for n in kg.graph.nodes if n.startswith("AUTH-")]
    assert len(auth_nodes) >= 1

    # Check clause containment edges
    clause_edges = kg.get_edges(source_id=doc_2020.id, relationship=RelationshipType.CONTAINS)
    assert len(clause_edges) == len(doc_2020.clauses)

    # Check document reference edge (doc_2020 REPLACES doc_2018)
    ref_edges = kg.get_edges(source_id=doc_2020.id, target_id=doc_2018.id)
    assert len(ref_edges) >= 1
    assert ref_edges[0]["relationship"] == "REPLACES"


def test_knowledge_graph_change_record_integration():
    kg = NetworkXRegulatoryGraph()
    doc_2018 = get_pmssc_2018_document()
    doc_2020 = get_pmssc_2020_document()

    kg.ingest_document(doc_2018)
    kg.ingest_document(doc_2020)

    detector = ChangeDetector()
    changes = detector.compare_documents(doc_2018, doc_2020)

    for chg in changes:
        kg.ingest_change_record(chg)

    # Verify amendment nodes
    amendment_nodes = [
        n for n in kg.graph.nodes
        if kg.graph.nodes[n].get("node_type") == NodeType.AMENDMENT.value
    ]
    assert len(amendment_nodes) == len(changes)

    # Check serialization
    graph_dict = kg.to_dict()
    assert graph_dict["total_nodes"] > 0
    assert graph_dict["total_edges"] > 0

    # Check mermaid output
    mermaid_str = kg.to_mermaid()
    assert "flowchart TD" in mermaid_str
    assert "DOC_MoSJE_PMS_SC_2020" in mermaid_str
