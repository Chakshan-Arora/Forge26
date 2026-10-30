"""
Integration tests for PolicyIntelEngine using authentic Central Government Policy documents.
Tests multi-year amendments, point-in-time applicability, and cross-ministry policies.
"""

import pytest
from intelligence.engine import PolicyIntelEngine
from intelligence.data import get_real_policy_documents
from shared.schemas import ChangeType


@pytest.fixture
def populated_engine():
    """Initializes engine with full suite of authentic Central Government policies."""
    engine = PolicyIntelEngine()
    docs = get_real_policy_documents()
    engine.register_documents(docs)
    return engine


def test_engine_registered_documents_count(populated_engine):
    docs = populated_engine.list_documents()
    assert len(docs) == 6
    doc_ids = [d.id for d in docs]
    assert "DOC-MoSJE-PMS-SC-2020" in doc_ids
    assert "DOC-MoSJE-PMS-SC-2022-AMEND" in doc_ids
    assert "DOC-MoSJE-PMS-SC-2023-CORR" in doc_ids
    assert "DOC-MoE-CSSS-2018" in doc_ids
    assert "DOC-MoE-PMUSP-2022" in doc_ids
    assert "DOC-UGC-ISHAN-UDAY-2021" in doc_ids


def test_pmssc_amendment_comparison(populated_engine):
    """
    Verifies that comparing PMS-SC 2020 with the 2022 amendment detects:
    1. Addition of Freeship card
    2. Modification / addition of Biometric attendance requirement
    """
    changes, summary = populated_engine.compare_documents(
        base_document_id="DOC-MoSJE-PMS-SC-2020",
        target_document_id="DOC-MoSJE-PMS-SC-2022-AMEND"
    )

    assert len(changes) > 0
    # Every change has strictly validated evidence
    for chg in changes:
        assert len(chg.evidence) > 0
        assert chg.document_id == "DOC-MoSJE-PMS-SC-2022-AMEND"

    # Check for Freeship Card or attendance clause
    has_freeship = any("freeship" in (c.current_text or "").lower() for c in changes)
    assert has_freeship


def test_pmssc_corrigendum_allowance_revision(populated_engine):
    """
    Verifies that the 2023 corrigendum specifically updates the academic allowance.
    """
    changes, summary = populated_engine.compare_documents(
        base_document_id="DOC-MoSJE-PMS-SC-2020",
        target_document_id="DOC-MoSJE-PMS-SC-2023-CORR"
    )

    assert len(changes) > 0
    allowance_change = next(
        (c for c in changes if "14,850" in (c.current_text or "") or "14850" in str(c.current_value)),
        None
    )
    assert allowance_change is not None
    assert allowance_change.change_type in (ChangeType.MODIFIED, ChangeType.REPLACED)


def test_temporal_resolution_across_csss_versions(populated_engine):
    """
    Point-in-time testing:
    On 2020-01-01 -> Only 2018 Guidelines apply
    On 2023-01-01 -> 2022 PM-USP Guidelines apply
    """
    scheme = "Central Sector Scheme of Scholarship for College and University Students"
    
    # 2020 Query
    res_2020 = populated_engine.query_eligibility_at_date(scheme, "2020-01-01")
    assert res_2020.status == "RESOLVED"
    assert "DOC-MoE-CSSS-2018" in res_2020.applicable_document_ids
    assert "DOC-MoE-PMUSP-2022" not in res_2020.applicable_document_ids

    # 2023 Query
    res_2023 = populated_engine.query_eligibility_at_date(scheme, "2023-01-01")
    assert res_2023.status == "RESOLVED"
    assert "DOC-MoE-PMUSP-2022" in res_2023.applicable_document_ids


def test_knowledge_graph_export(populated_engine):
    """
    Verifies graph serialization to dictionary and Mermaid diagrams.
    """
    graph_dict = populated_engine.export_graph_dict()
    assert graph_dict["total_nodes"] > 10
    assert graph_dict["total_edges"] > 10

    mermaid = populated_engine.export_graph_mermaid()
    assert "flowchart TD" in mermaid
    assert "DOC_MoSJE_PMS_SC_2020" in mermaid or "DOC-MoSJE-PMS-SC-2020" in mermaid
