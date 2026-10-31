"""
Tests for ChangeDetector on authentic government policy documents.
"""

import pytest
from shared.schemas import ChangeType
from intelligence.change_detector import ChangeDetector
from data.real_policies import (
    get_pmssc_2018_document,
    get_pmssc_2020_document,
    get_nmmss_2017_document,
    get_nmmss_2022_document,
    get_pmusp_csss_2015_document,
    get_pmusp_csss_2022_document,
)


def test_compare_pmssc_real_documents():
    detector = ChangeDetector()
    doc_2018 = get_pmssc_2018_document()
    doc_2020 = get_pmssc_2020_document()

    changes = detector.compare_documents(doc_2018, doc_2020)
    summary = detector.summarize_changes(doc_2018, doc_2020, changes)

    assert len(changes) > 0
    assert summary.total_changes == len(changes)

    # Verify that every change has non-empty evidence
    for chg in changes:
        assert len(chg.evidence) > 0
        assert chg.document_id == doc_2020.id

    # Check that Freeship Card (PMS-SC-2020-CL-VIII) was detected as an ADDED / EXEMPTED clause
    freeship_chg = next((c for c in changes if c.clause_id == "PMS-SC-2020-CL-VIII"), None)
    assert freeship_chg is not None
    assert freeship_chg.change_type in (ChangeType.ADDED, ChangeType.EXEMPTED)

    # Check maintenance allowance change (Group 1 rate changed)
    allowance_chg = next((c for c in changes if c.clause_id == "PMS-SC-2020-CL-V-1"), None)
    assert allowance_chg is not None
    assert allowance_chg.change_type == ChangeType.MODIFIED
    assert allowance_chg.current_value is not None


def test_compare_nmmss_real_documents():
    detector = ChangeDetector()
    doc_2017 = get_nmmss_2017_document()
    doc_2022 = get_nmmss_2022_document()

    changes = detector.compare_documents(doc_2017, doc_2022)

    # Verify income ceiling shift: ₹1,50,000 -> ₹3,50,000
    income_chg = next((c for c in changes if c.clause_id == "NMMSS-2022-CL-2"), None)
    assert income_chg is not None
    assert income_chg.change_type == ChangeType.MODIFIED
    assert income_chg.previous_value.get("numeric_amount") == 150000.0
    assert income_chg.current_value.get("numeric_amount") == 350000.0

    # Verify renewal clause was added in 2022
    renewal_chg = next((c for c in changes if c.clause_id == "NMMSS-2022-CL-5"), None)
    assert renewal_chg is not None
    assert renewal_chg.change_type == ChangeType.ADDED


def test_compare_pmusp_csss_real_documents():
    detector = ChangeDetector()
    doc_2015 = get_pmusp_csss_2015_document()
    doc_2022 = get_pmusp_csss_2022_document()

    changes = detector.compare_documents(doc_2015, doc_2022)

    # Income ceiling revised from ₹6,00,000 to ₹4,50,000
    income_chg = next((c for c in changes if c.clause_id == "CSSS-2022-CL-2"), None)
    assert income_chg is not None
    assert income_chg.previous_value.get("numeric_amount") == 600000.0
    assert income_chg.current_value.get("numeric_amount") == 450000.0

    # Rate revised from ₹10,000 to ₹12,000 at graduation level
    rate_chg = next((c for c in changes if c.clause_id == "CSSS-2022-CL-3"), None)
    assert rate_chg is not None
    assert rate_chg.previous_value.get("numeric_amount") == 10000.0
    assert rate_chg.current_value.get("numeric_amount") == 12000.0
