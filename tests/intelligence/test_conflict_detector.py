"""
Tests for ConflictDetector: distinct scopes, partial amendments, and contradictions.
"""

import pytest
from shared.schemas import Document, Clause, ClauseType, DocumentType
from intelligence.conflict_detector import ConflictDetector
from data.real_policies import get_pmssc_2018_document, get_pmssc_2020_document


def test_conflict_detector_distinct_scopes_hosteller_vs_day_scholar():
    cl_hosteller = Clause(
        id="CL-H",
        document_id="DOC-1",
        clause_number="1",
        text="Maintenance allowance for hostellers shall be ₹ 13,500 per annum.",
        clause_type=ClauseType.ELIGIBILITY,
        structured_attributes={"numeric_amount": 13500.0}
    )
    cl_day_scholar = Clause(
        id="CL-D",
        document_id="DOC-2",
        clause_number="1",
        text="Maintenance allowance for day scholars shall be ₹ 7,000 per annum.",
        clause_type=ClauseType.ELIGIBILITY,
        structured_attributes={"numeric_amount": 7000.0}
    )

    doc_a = Document(
        id="DOC-A",
        title="Hosteller Scheme Order",
        scheme_name="Test Scheme",
        ministry="Ministry of Education",
        document_type=DocumentType.NOTIFICATION,
        clauses=[cl_hosteller]
    )
    doc_b = Document(
        id="DOC-B",
        title="Day Scholar Scheme Order",
        scheme_name="Test Scheme",
        ministry="Ministry of Education",
        document_type=DocumentType.NOTIFICATION,
        clauses=[cl_day_scholar]
    )

    detector = ConflictDetector([doc_a, doc_b])
    reports = detector.detect_conflicts_for_scheme("Test Scheme")

    assert len(reports) >= 1
    # Verify that this was recognized as DISTINCT_COHORTS_DISAMBIGUATION, not a genuine contradiction!
    disambiguation = next((r for r in reports if r.conflict_type == "DISTINCT_COHORTS_DISAMBIGUATION"), None)
    assert disambiguation is not None
    assert disambiguation.is_genuine_contradiction is False
    assert "Hostellers" in disambiguation.distinct_scopes_identified


def test_conflict_detector_missing_dependency():
    doc_with_ref = Document(
        id="DOC-AMEND-1",
        title="Amendment Order",
        scheme_name="Test Scheme",
        ministry="Ministry of Education",
        document_type=DocumentType.AMENDMENT,
        references=[
            {"target_document_id": "MISSING-PARENT-ORDER-2015", "relationship": "AMENDS"}
        ],
        clauses=[]
    )

    detector = ConflictDetector([doc_with_ref])
    reports = detector.detect_conflicts_for_scheme("Test Scheme")

    missing_rep = next((r for r in reports if r.conflict_type == "MISSING_HISTORICAL_DEPENDENCY"), None)
    assert missing_rep is not None
    assert "MISSING-PARENT-ORDER-2015" in missing_rep.description
    assert missing_rep.resolution_status == "REQUIRES_CLARIFICATION"
