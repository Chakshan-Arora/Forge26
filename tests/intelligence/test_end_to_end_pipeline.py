"""
End-to-End Pipeline Integration Tests for Policy Intel Intelligence Engine.

Exercises the full intelligence workflow:
1. Document ingestion and normalization.
2. Clause alignment and change detection.
3. Knowledge graph construction and relationship extraction.
4. Point-in-time temporal applicability resolution.
5. Evidence-backed impact analysis.
6. Conflict and dependency detection.
"""

import pytest
from shared.schemas import (
    ChangeType,
    NodeType,
    RelationshipType,
    EvidenceRecord,
)
from intelligence import (
    ChangeDetector,
    KnowledgeGraph,
    TemporalResolver,
    ImpactAnalyzer,
    ConflictDetector,
    EvidenceEngine,
    NetworkXRegulatoryGraph,
)
from data.real_policies import (
    get_pmssc_2018_document,
    get_pmssc_2020_document,
    get_nmmss_2017_document,
    get_nmmss_2022_document,
    get_pmusp_csss_2015_document,
    get_pmusp_csss_2022_document,
)


def test_full_pipeline_nmmss_end_to_end():
    # Step 1: Ingestion
    doc_2017 = get_nmmss_2017_document()
    doc_2022 = get_nmmss_2022_document()

    # Step 2: Clause-level Change Detection
    detector = ChangeDetector()
    changes = detector.compare_documents(doc_2017, doc_2022)
    assert len(changes) >= 2

    # Verify every change record satisfies the shared data contract
    for chg in changes:
        assert chg.change_id.startswith("CHG-")
        assert chg.document_id == doc_2022.id
        assert chg.previous_document_id == doc_2017.id
        assert chg.change_type in (ChangeType.MODIFIED, ChangeType.ADDED, ChangeType.REPLACED, ChangeType.EXEMPTED)
        assert len(chg.evidence) > 0
        assert chg.confidence is not None

    # Step 3: Knowledge Graph Integration
    kg = NetworkXRegulatoryGraph()
    kg.ingest_document(doc_2017)
    kg.ingest_document(doc_2022)
    for chg in changes:
        kg.ingest_change_record(chg)

    # Verify KG contents
    graph_dict = kg.to_dict()
    assert graph_dict["total_nodes"] > 10
    assert graph_dict["total_edges"] > 10

    # Step 4: Temporal Applicability Query
    resolver = TemporalResolver(graph=kg)
    resolver.register_document(doc_2017)
    resolver.register_document(doc_2022)

    # Query before amendment
    res_before = resolver.resolve_applicability_at_date(doc_2017.scheme_name, "2020-01-01")
    assert res_before.status == "RESOLVED"
    assert doc_2017.id in res_before.applicable_document_ids
    assert doc_2022.id not in res_before.applicable_document_ids

    # Query after amendment
    res_after = resolver.resolve_applicability_at_date(doc_2022.scheme_name, "2024-06-01")
    assert res_after.status == "RESOLVED"
    assert doc_2022.id in res_after.applicable_document_ids
    assert doc_2017.id not in res_after.applicable_document_ids

    # Step 5: Impact Analysis
    analyzer = ImpactAnalyzer()
    report = analyzer.analyze_document_changes(target_document=doc_2022, changes=changes, base_document=doc_2017)

    assert report.scheme_name == doc_2022.scheme_name
    assert len(report.deterministic_deltas) > 0
    assert len(report.potentially_affected_groups) > 0
    assert len(report.practical_consequences) > 0
    assert len(report.evidence_trail) > 0

    # Step 6: Conflict Detection
    conflict_detector = ConflictDetector([doc_2017, doc_2022])
    conflict_reports = conflict_detector.detect_conflicts_for_scheme(doc_2017.scheme_name)
    assert isinstance(conflict_reports, list)


def test_full_pipeline_pmssc_end_to_end():
    doc_2018 = get_pmssc_2018_document()
    doc_2020 = get_pmssc_2020_document()

    detector = ChangeDetector()
    changes = detector.compare_documents(doc_2018, doc_2020)

    kg = NetworkXRegulatoryGraph()
    kg.ingest_document(doc_2018)
    kg.ingest_document(doc_2020)
    for chg in changes:
        kg.ingest_change_record(chg)

    analyzer = ImpactAnalyzer()
    report = analyzer.analyze_document_changes(target_document=doc_2020, changes=changes, base_document=doc_2018)

    # Check that Freeship Card and DBT are flagged in practical consequences
    has_freeship = any("freeship" in pc.lower() for pc in report.practical_consequences)
    has_dbt = any("aadhaar" in pc.lower() or "dbt" in pc.lower() for pc in report.practical_consequences)
    assert has_freeship is True
    assert has_dbt is True
