"""
Tests for PolicyIntelEngine facade methods.
"""

import pytest
from intelligence.engine import PolicyIntelEngine
from data.real_policies import get_nmmss_2017_document, get_nmmss_2022_document


def test_policy_intel_engine_facade():
    engine = PolicyIntelEngine()
    doc_2017 = get_nmmss_2017_document()
    doc_2022 = get_nmmss_2022_document()

    # Ingest documents
    engine.ingest_documents([doc_2017, doc_2022])

    # Run comparison
    changes, summary = engine.compare_documents(doc_2017, doc_2022, update_graph=True)
    assert len(changes) >= 2
    assert summary.total_changes == len(changes)

    # Resolve applicability
    app = engine.resolve_applicability(doc_2017.scheme_name, "2024-01-01")
    assert app.status == "RESOLVED"
    assert doc_2022.id in app.applicable_document_ids

    # Analyze impact
    impact = engine.analyze_impact(target_document=doc_2022, base_document=doc_2017, changes=changes)
    assert len(impact.deterministic_deltas) > 0
    assert len(impact.practical_consequences) > 0

    # Conflict check
    conflicts = engine.detect_conflicts(doc_2017.scheme_name)
    assert isinstance(conflicts, list)

    # Graph exports
    g_dict = engine.get_graph_dict()
    assert g_dict["total_nodes"] > 0
    m_str = engine.get_graph_mermaid()
    assert "flowchart TD" in m_str
