"""
Tests for ImpactAnalyzer: deterministic deltas, affected cohorts, and practical consequences.
"""

import pytest
from intelligence.change_detector import ChangeDetector
from intelligence.impact_analyzer import ImpactAnalyzer
from data.real_policies import (
    get_nmmss_2017_document,
    get_nmmss_2022_document,
    get_pmusp_csss_2015_document,
    get_pmusp_csss_2022_document,
    get_pmssc_2018_document,
    get_pmssc_2020_document,
)


def test_impact_analysis_nmmss_income_relaxation():
    detector = ChangeDetector()
    analyzer = ImpactAnalyzer()

    doc_2017 = get_nmmss_2017_document()
    doc_2022 = get_nmmss_2022_document()

    changes = detector.compare_documents(doc_2017, doc_2022)
    report = analyzer.analyze_document_changes(target_document=doc_2022, changes=changes, base_document=doc_2017)

    # Check that deterministic deltas were calculated
    assert len(report.deterministic_deltas) > 0
    income_delta = next(
        (d for d in report.deterministic_deltas if d.get("type") == "INCOME_CEILING_RELAXATION"),
        None
    )
    assert income_delta is not None
    assert income_delta["previous_limit"] == 150000.0
    assert income_delta["current_limit"] == 350000.0
    assert income_delta["newly_eligible_interval"]["min_exclusive"] == 150000.0
    assert income_delta["newly_eligible_interval"]["max_inclusive"] == 350000.0

    # Check potential groups
    newly_eligible_grp = next(
        (g for g in report.potentially_affected_groups if "150,000 to ₹350,000" in g.group_name),
        None
    )
    assert newly_eligible_grp is not None
    assert newly_eligible_grp.impact_nature == "POTENTIALLY_ELIGIBLE"

    # Check practical consequences
    assert any("income ceiling relaxed" in pc.lower() for pc in report.practical_consequences)


def test_impact_analysis_csss_income_restriction_and_rate_increase():
    detector = ChangeDetector()
    analyzer = ImpactAnalyzer()

    doc_2015 = get_pmusp_csss_2015_document()
    doc_2022 = get_pmusp_csss_2022_document()

    changes = detector.compare_documents(doc_2015, doc_2022)
    report = analyzer.analyze_document_changes(target_document=doc_2022, changes=changes, base_document=doc_2015)

    # Income restriction delta
    income_delta = next(
        (d for d in report.deterministic_deltas if d.get("type") == "INCOME_CEILING_RESTRICTION"),
        None
    )
    assert income_delta is not None
    assert income_delta["previous_limit"] == 600000.0
    assert income_delta["current_limit"] == 450000.0

    # Scholarship rate increase delta (+2000)
    rate_delta = next(
        (d for d in report.deterministic_deltas if d.get("type") == "SCHOLARSHIP_RATE_REVISION"),
        None
    )
    assert rate_delta is not None
    assert rate_delta["previous_amount"] == 10000.0
    assert rate_delta["current_amount"] == 12000.0
    assert rate_delta["net_change"] == 2000.0

    # Aadhaar seeding practical consequence
    assert any("aadhaar" in pc.lower() for pc in report.practical_consequences)


def test_impact_analysis_pmssc_procedural_updates():
    detector = ChangeDetector()
    analyzer = ImpactAnalyzer()

    doc_2018 = get_pmssc_2018_document()
    doc_2020 = get_pmssc_2020_document()

    changes = detector.compare_documents(doc_2018, doc_2020)
    report = analyzer.analyze_document_changes(target_document=doc_2020, changes=changes, base_document=doc_2018)

    # Check Freeship card consequence
    assert any("freeship card" in pc.lower() for pc in report.practical_consequences)
    # Check DBT Aadhaar consequence
    assert any("aadhaar" in pc.lower() for pc in report.practical_consequences)
