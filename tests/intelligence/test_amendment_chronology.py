"""
Amendment Chronology and Legal Relationships Test Suite.

Explicitly tests:
1. Comparison between two versions where an intermediate version is missing (e.g. CSSS 2015 to 2022).
2. An amendment that modifies conditions without explicitly establishing a supersession relationship.
3. A clause that disappears in a subsequent version without an explicit statutory repeal (verifying uncertainty note).
4. Two amendments with different effective dates.
5. A query date falling between publication date and effective date of an amendment.
"""

import pytest
from shared.schemas import (
    Document,
    Clause,
    DocumentType,
    ClauseType,
    ChangeType,
)
from intelligence import (
    PolicyIntelEngine,
    ChangeDetector,
    ConflictDetector,
    TemporalResolver,
)
from data.real_policies import (
    get_pmusp_csss_2015_document,
    get_pmusp_csss_2022_document,
)


def test_missing_intermediate_version_comparison():
    """
    Comparison between two policy versions where an intermediate statutory revision is missing.
    In real policy history, CSSS had an intermediate 2018 revision raising the income ceiling to ₹8.0 lakh
    before the 2022 PM-USP umbrella guidelines standardized it to ₹4.5 lakh.
    """
    engine = PolicyIntelEngine()
    doc_2015 = get_pmusp_csss_2015_document()
    doc_2022 = get_pmusp_csss_2022_document()

    # Direct comparison across versions spanning the missing 2018 revision
    changes, summary = engine.compare_documents(doc_2015, doc_2022)
    assert summary.total_changes > 0

    # Verify income ceiling shift detected (6.0L -> 4.5L)
    income_change = next(
        (c for c in changes if c.previous_value and c.previous_value.get("numeric_amount") == 600000.0),
        None
    )
    assert income_change is not None
    assert income_change.current_value.get("numeric_amount") == 450000.0

    # Test missing dependency detection when an intermediate version is referenced but absent
    doc_v3_with_missing_ref = Document(
        id="DOC-V3-GAP",
        title="Scheme Guidelines 2024",
        scheme_name="Gap Scheme",
        ministry="Ministry of Education",
        document_type=DocumentType.GUIDELINES,
        effective_date="2024-04-01",
        references=[
            {"target_document_id": "DOC-V2-MISSING", "relationship": "AMENDS"}
        ],
        clauses=[
            Clause(id="C-GAP-1", document_id="DOC-V3-GAP", clause_number="1", text="Income ceiling ₹ 3,00,000 p.a.")
        ]
    )
    detector = ConflictDetector([doc_v3_with_missing_ref])
    conflicts = detector.detect_conflicts_for_scheme("Gap Scheme")
    assert len(conflicts) >= 1
    dep_conflict = next((c for c in conflicts if c.conflict_type == "MISSING_HISTORICAL_DEPENDENCY"), None)
    assert dep_conflict is not None
    assert "DOC-V2-MISSING" in dep_conflict.description
    assert dep_conflict.resolution_status == "REQUIRES_CLARIFICATION"


def test_amendment_without_explicit_supersession():
    """
    An amendment modifies conditions without explicitly establishing a supersession relationship.
    Engine must not invent a total repeal, but recognize temporal precedence and partial modification.
    """
    base_doc = Document(
        id="DOC-BASE-ATTEND",
        title="University Regulations 2022",
        scheme_name="Scholarship Code",
        ministry="Ministry of Education",
        document_type=DocumentType.GUIDELINES,
        effective_date="2022-01-01",
        clauses=[
            Clause(
                id="CL-ATT-BASE",
                document_id="DOC-BASE-ATTEND",
                clause_number="5.1",
                text="Mandatory minimum attendance shall be 75% in all academic semesters.",
                clause_type=ClauseType.ELIGIBILITY,
                structured_attributes={"percentage": 75.0}
            ),
            Clause(
                id="CL-OTHER-BASE",
                document_id="DOC-BASE-ATTEND",
                clause_number="5.2",
                text="Candidates must maintain good conduct and character.",
                clause_type=ClauseType.ELIGIBILITY
            )
        ]
    )

    amendment_doc = Document(
        id="DOC-AMEND-ATTEND",
        title="Attendance Revision Order 2023",
        scheme_name="Scholarship Code",
        ministry="Ministry of Education",
        document_type=DocumentType.AMENDMENT,
        effective_date="2023-01-01",
        # No references with SUPERSEDES or REPLACES
        references=[],
        clauses=[
            Clause(
                id="CL-ATT-MOD",
                document_id="DOC-AMEND-ATTEND",
                clause_number="1",
                text="Mandatory minimum attendance shall be 80% in all academic semesters.",
                clause_type=ClauseType.ELIGIBILITY,
                structured_attributes={"percentage": 80.0}
            )
        ]
    )

    detector = ConflictDetector([base_doc, amendment_doc])
    conflicts = detector.detect_conflicts_for_scheme("Scholarship Code")

    # Partial amendment detected
    part_conflict = next((c for c in conflicts if c.conflict_type == "PARTIAL_AMENDMENT"), None)
    assert part_conflict is not None
    assert part_conflict.resolution_status == "RESOLVED_BY_TEMPORAL_PRECEDENCE"

    # In TemporalResolver, both documents remain active unless explicit supersession or expiry occurs
    resolver = TemporalResolver()
    resolver.register_document(base_doc)
    resolver.register_document(amendment_doc)
    res = resolver.resolve_applicability_at_date("Scholarship Code", "2023-06-01")
    assert base_doc.id in res.applicable_document_ids
    assert amendment_doc.id in res.applicable_document_ids
    assert any(c.id == "CL-OTHER-BASE" for c in res.applicable_clauses)


def test_clause_disappearing_without_statutory_repeal():
    """
    A clause disappears in a subsequent policy version without explicit statutory repeal.
    The engine must record the clause as REMOVED and note legal uncertainty rather than inventing a repeal.
    """
    doc_v1 = Document(
        id="DOC-POLICY-V1",
        title="Scheme 2021",
        scheme_name="Omission Scheme",
        ministry="Ministry of Education",
        document_type=DocumentType.GUIDELINES,
        effective_date="2021-01-01",
        clauses=[
            Clause(
                id="CL-V1-A",
                document_id="DOC-POLICY-V1",
                clause_number="1",
                text="Income limit shall not exceed ₹ 2,50,000 per annum."
            ),
            Clause(
                id="CL-V1-B",
                document_id="DOC-POLICY-V1",
                clause_number="2",
                text="Mandatory submission of caste validity certificate from District Collectorate."
            )
        ]
    )

    doc_v2 = Document(
        id="DOC-POLICY-V2",
        title="Scheme 2023",
        scheme_name="Omission Scheme",
        ministry="Ministry of Education",
        document_type=DocumentType.GUIDELINES,
        effective_date="2023-01-01",
        clauses=[
            Clause(
                id="CL-V2-A",
                document_id="DOC-POLICY-V2",
                clause_number="1",
                text="Income limit shall not exceed ₹ 3,00,000 per annum."
            )
            # Clause CL-V1-B omitted silently without explicit repeal language
        ]
    )

    detector = ChangeDetector()
    changes = detector.compare_documents(doc_v1, doc_v2)

    removed_chg = next((c for c in changes if c.change_type == ChangeType.REMOVED), None)
    assert removed_chg is not None
    assert removed_chg.clause_id == "CL-V1-B"
    assert any(
        "does not legally confirm total repeal" in u.lower()
        for u in removed_chg.uncertainties
    )


def test_two_amendments_with_different_effective_dates():
    """
    Two amendments notified to a base document with staggered future effective dates.
    Engine must activate provisions sequentially according to point-in-time query dates.
    """
    resolver = TemporalResolver()

    base_doc = Document(
        id="DOC-BASE-STAGGER",
        title="Base Fellowship Guidelines",
        scheme_name="Staggered Fellowship Scheme",
        ministry="Ministry of Education",
        document_type=DocumentType.GUIDELINES,
        publication_date="2024-01-01",
        effective_date="2024-01-01",
        clauses=[
            Clause(id="CL-BASE-STAG", document_id="DOC-BASE-STAGGER", clause_number="1", text="Stipend is ₹ 10,000 p.m.")
        ]
    )

    amend_1 = Document(
        id="DOC-AMEND-PHASE1",
        title="Phase 1 Fellowship Enhancement",
        scheme_name="Staggered Fellowship Scheme",
        ministry="Ministry of Education",
        document_type=DocumentType.NOTIFICATION,
        publication_date="2024-03-01",
        effective_date="2024-04-01",
        clauses=[
            Clause(id="CL-AMEND-1", document_id="DOC-AMEND-PHASE1", clause_number="1", text="Stipend is ₹ 12,000 p.m.")
        ]
    )

    amend_2 = Document(
        id="DOC-AMEND-PHASE2",
        title="Phase 2 Fellowship Enhancement",
        scheme_name="Staggered Fellowship Scheme",
        ministry="Ministry of Education",
        document_type=DocumentType.NOTIFICATION,
        publication_date="2024-03-01",
        effective_date="2024-10-01",
        clauses=[
            Clause(id="CL-AMEND-2", document_id="DOC-AMEND-PHASE2", clause_number="1", text="Stipend is ₹ 15,000 p.m.")
        ]
    )

    resolver.register_document(base_doc)
    resolver.register_document(amend_1)
    resolver.register_document(amend_2)

    # Point-in-time 1: 2024-02-15 (Before both amendments take effect)
    res_feb = resolver.resolve_applicability_at_date("Staggered Fellowship Scheme", "2024-02-15")
    assert base_doc.id in res_feb.applicable_document_ids
    assert amend_1.id not in res_feb.applicable_document_ids
    assert amend_2.id not in res_feb.applicable_document_ids

    # Point-in-time 2: 2024-06-01 (Phase 1 effective, Phase 2 still pending)
    res_jun = resolver.resolve_applicability_at_date("Staggered Fellowship Scheme", "2024-06-01")
    assert amend_1.id in res_jun.applicable_document_ids
    assert amend_2.id not in res_jun.applicable_document_ids
    assert len(res_jun.active_amendments) == 1
    assert res_jun.active_amendments[0]["document_id"] == amend_2.id
    assert res_jun.active_amendments[0]["status"] == "NOTIFIED_PENDING_ENFORCEMENT"

    # Point-in-time 3: 2024-11-01 (Phase 2 also effective)
    res_nov = resolver.resolve_applicability_at_date("Staggered Fellowship Scheme", "2024-11-01")
    assert amend_1.id in res_nov.applicable_document_ids
    assert amend_2.id in res_nov.applicable_document_ids
    assert len(res_nov.active_amendments) == 0


def test_query_date_between_publication_and_effective_date():
    """
    A notification published on 2025-01-15 but legally effective on 2025-07-01.
    Query at 2025-04-01 must not enforce new provisions, but must report the pending amendment.
    """
    resolver = TemporalResolver()

    base_doc = Document(
        id="DOC-ACTIVE-NOW",
        title="Standard Scholarship Scheme",
        scheme_name="Interim Check Scheme",
        ministry="Ministry of Education",
        document_type=DocumentType.GUIDELINES,
        publication_date="2023-01-01",
        effective_date="2023-01-01",
        clauses=[
            Clause(id="CL-ACT-1", document_id="DOC-ACTIVE-NOW", clause_number="1", text="Income limit ₹ 2.0 lakh.")
        ]
    )

    future_amend = Document(
        id="DOC-FUTURE-NOTIFIED",
        title="Revision Notification 2025",
        scheme_name="Interim Check Scheme",
        ministry="Ministry of Education",
        document_type=DocumentType.NOTIFICATION,
        publication_date="2025-01-15",
        effective_date="2025-07-01",
        clauses=[
            Clause(id="CL-FUT-1", document_id="DOC-FUTURE-NOTIFIED", clause_number="1", text="Income limit ₹ 3.5 lakh.")
        ]
    )

    resolver.register_document(base_doc)
    resolver.register_document(future_amend)

    # Query between publication and enforcement: 2025-04-01
    res = resolver.resolve_applicability_at_date("Interim Check Scheme", "2025-04-01")

    assert res.status == "RESOLVED"
    assert base_doc.id in res.applicable_document_ids
    assert future_amend.id not in res.applicable_document_ids

    # Pending amendment captured with legal status
    assert len(res.active_amendments) == 1
    pending = res.active_amendments[0]
    assert pending["document_id"] == "DOC-FUTURE-NOTIFIED"
    assert pending["status"] == "NOTIFIED_PENDING_ENFORCEMENT"
    assert "2025-01-15" in pending["notes"]
    assert "2025-07-01" in pending["notes"]
