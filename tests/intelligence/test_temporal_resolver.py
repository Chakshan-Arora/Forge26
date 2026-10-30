"""
Tests for TemporalResolver: point-in-time applicability, lineage, and pending amendments.
"""

import pytest
from intelligence.temporal_resolver import TemporalResolver
from data.real_policies import (
    get_nmmss_2017_document,
    get_nmmss_2022_document,
    get_pmssc_2018_document,
    get_pmssc_2020_document,
)


def test_temporal_applicability_point_in_time():
    resolver = TemporalResolver()
    doc_2017 = get_nmmss_2017_document()
    doc_2022 = get_nmmss_2022_document()

    resolver.register_document(doc_2017)
    resolver.register_document(doc_2022)

    scheme = "National Means-cum-Merit Scholarship Scheme"

    # Query in 2019 (before 2022 revision)
    res_2019 = resolver.resolve_applicability_at_date(scheme, "2019-08-01")
    assert res_2019.status == "RESOLVED"
    assert doc_2017.id in res_2019.applicable_document_ids
    assert doc_2022.id not in res_2019.applicable_document_ids

    # Query in 2023 (after 2022 revision)
    res_2023 = resolver.resolve_applicability_at_date(scheme, "2023-01-15")
    assert res_2023.status == "RESOLVED"
    assert doc_2022.id in res_2023.applicable_document_ids
    assert doc_2017.id not in res_2023.applicable_document_ids


def test_pending_amendment_detection():
    resolver = TemporalResolver()
    doc_2018 = get_pmssc_2018_document()
    doc_2020 = get_pmssc_2020_document()

    resolver.register_document(doc_2018)
    resolver.register_document(doc_2020)

    scheme = "Post-Matric Scholarship for SC Students"

    # Query on 2020-05-01 (doc_2018 was valid, doc_2020 not yet notified until 2020-12-23)
    res_2020_may = resolver.resolve_applicability_at_date(scheme, "2020-05-01")
    assert doc_2018.id in res_2020_may.applicable_document_ids
    assert doc_2020.id not in res_2020_may.applicable_document_ids


def test_trace_condition_origin():
    resolver = TemporalResolver()
    doc_2017 = get_nmmss_2017_document()
    doc_2022 = get_nmmss_2022_document()

    resolver.register_document(doc_2017)
    resolver.register_document(doc_2022)

    history = resolver.trace_condition_origin("National Means-cum-Merit Scholarship Scheme", "income_ceiling")
    assert len(history) == 2
    # Verify chronological sequence
    assert history[0]["document_id"] == doc_2017.id
    assert history[1]["document_id"] == doc_2022.id
