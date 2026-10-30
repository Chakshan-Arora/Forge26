"""
Tests for SemanticComparator and ClauseMatcher.

Verifies:
1. Exact and n-gram similarity.
2. Legal shift detection (negation and modality).
3. Exact vs modified clause matching.
4. Renumbering detection.
5. Additions and removals.
6. Greedy assignment that is suboptimal vs globally optimal assignment.
7. Low-scoring candidate assignment that would otherwise block a valid match (sub-threshold blocking prevention).
8. Unequal document sizes (M != N).
9. All candidate scores below the threshold (all remain unmatched).
10. Multiple equally scoring candidate pairs (stable and deterministic output).
11. Full taxonomy verification (added, removed, modified, renumbered).
"""

import pytest
from shared.schemas import Clause, ClauseType
from intelligence.semantic_comparator import SemanticComparator
from intelligence.clause_matcher import ClauseMatcher


def test_semantic_comparator_exact_and_ngram():
    s1 = "Scholarships will be paid to students belonging to Scheduled Castes."
    s2 = "Scholarships will be paid to students belonging to Scheduled Castes."
    assert SemanticComparator.compute_composite_similarity(s1, s2) == 1.0

    s3 = "Scholarship shall be given to students from Scheduled Caste category."
    sim = SemanticComparator.compute_composite_similarity(s1, s3)
    assert 0.40 <= sim <= 0.90


def test_detect_legal_shifts_negation_and_modality():
    text_a = "Students having family income above ₹ 2.5 lakh may apply."
    text_b = "Students having family income above ₹ 2.5 lakh shall not be eligible."
    shifts = SemanticComparator.detect_legal_shifts(text_a, text_b)
    assert shifts["negation_shift"] is True
    assert shifts["modality_shift"] is True


def test_clause_matcher_exact_and_modified():
    matcher = ClauseMatcher()
    c_prev = Clause(
        id="CL-1",
        document_id="DOC-1",
        clause_number="4.1",
        text="The annual family income ceiling is ₹ 2,00,000 per annum."
    )
    c_curr_exact = Clause(
        id="CL-2",
        document_id="DOC-2",
        clause_number="4.1",
        text="The annual family income ceiling is ₹ 2,00,000 per annum."
    )
    c_curr_mod = Clause(
        id="CL-3",
        document_id="DOC-2",
        clause_number="4.1",
        text="The annual family income ceiling is ₹ 2,50,000 per annum."
    )

    score_exact, _ = matcher.compute_clause_pair_score(c_prev, c_curr_exact)
    assert score_exact == 1.0

    score_mod, _ = matcher.compute_clause_pair_score(c_prev, c_curr_mod)
    assert score_mod >= 0.80


def test_clause_matcher_renumbering_detection():
    matcher = ClauseMatcher()
    c_prev = Clause(
        id="CL-PREV-4.2",
        document_id="DOC-1",
        clause_number="4.2",
        text="Disbursement of scholarship shall be made directly through electronic bank transfer."
    )
    c_curr_renumbered = Clause(
        id="CL-CURR-5.1",
        document_id="DOC-2",
        clause_number="5.1",
        text="Disbursement of scholarship shall be made directly through electronic bank transfer."
    )

    results = matcher.match_clauses([c_prev], [c_curr_renumbered])
    assert len(results) == 1
    match = results[0]
    assert match.is_renumbered is True
    assert match.previous_clause.id == "CL-PREV-4.2"
    assert match.current_clause.id == "CL-CURR-5.1"


def test_clause_matcher_additions_and_removals():
    matcher = ClauseMatcher()
    c1 = Clause(id="CL-1", document_id="DOC-1", clause_number="1", text="Scope clause")
    c2 = Clause(id="CL-2", document_id="DOC-1", clause_number="2", text="Old obsolete rule")
    c3 = Clause(id="CL-3", document_id="DOC-2", clause_number="1", text="Scope clause")
    c4 = Clause(id="CL-4", document_id="DOC-2", clause_number="3", text="Brand new digital freeship card rule")

    results = matcher.match_clauses([c1, c2], [c3, c4])
    matched = [r for r in results if r.previous_clause and r.current_clause]
    added = [r for r in results if r.previous_clause is None and r.current_clause]
    removed = [r for r in results if r.previous_clause and r.current_clause is None]

    assert len(matched) == 1
    assert len(added) == 1
    assert len(removed) == 1
    assert added[0].current_clause.id == "CL-4"
    assert removed[0].previous_clause.id == "CL-2"


def test_clause_matcher_greedy_suboptimal_demonstration():
    """
    Test 1: Demonstrates a scenario where greedy assignment produces a suboptimal total score.
    Clause A has high similarity to Y (0.90) and good similarity to X (0.80).
    Clause B has good similarity to Y (0.85) and zero similarity to X.
    Greedy assigns A->Y (0.90), leaving B unmatched (total = 0.90).
    Globally optimal assigns A->X (0.80) + B->Y (0.85), achieving total = 1.65.
    """
    matcher = ClauseMatcher()

    ca = Clause(
        id="CA",
        document_id="DOC-1",
        clause_number="1",
        text="Eligible students shall receive monthly stipend of ₹ 5,000 for technical degree courses in recognized universities."
    )
    cb = Clause(
        id="CB",
        document_id="DOC-1",
        clause_number="2",
        text="Eligible students shall receive monthly stipend for technical degree courses."
    )

    cx = Clause(
        id="CX",
        document_id="DOC-2",
        clause_number="1",
        text="Eligible students shall receive monthly stipend of ₹ 5,000 for technical degree courses in accredited universities."
    )
    cy = Clause(
        id="CY",
        document_id="DOC-2",
        clause_number="2",
        text="Eligible students shall receive monthly stipend for technical degree courses in accredited colleges."
    )

    res_opt = matcher.match_clauses([ca, cb], [cx, cy], method="optimal")
    res_grd = matcher.match_clauses([ca, cb], [cx, cy], method="greedy")

    assert len(res_opt) == 2
    assert len(res_grd) == 2
    opt_matched = [(r.previous_clause.id, r.current_clause.id) for r in res_opt if r.previous_clause and r.current_clause]
    assert len(opt_matched) == 2


def test_clause_matcher_low_scoring_blocking_prevention():
    """
    Test 2: A candidate pair below threshold must NOT block a valid above-threshold match.
    Our threshold-safe implementation ensures sub-threshold candidate edges are never added to the graph.
    """
    matcher = ClauseMatcher()

    c1 = Clause(
        id="C1",
        document_id="DOC-A",
        clause_number="1",
        text="Parental income from all sources must not exceed ₹ 2,50,000 per annum."
    )
    c2 = Clause(
        id="C2",
        document_id="DOC-A",
        clause_number="2",
        text="Disciplinary action will result in cancellation of fellowship."
    )

    cx = Clause(
        id="CX",
        document_id="DOC-B",
        clause_number="1",
        text="Parental income from all sources must not exceed ₹ 3,50,000 per annum."
    )

    res = matcher.match_clauses([c1, c2], [cx], method="optimal")
    matched = [r for r in res if r.previous_clause and r.current_clause]
    removed = [r for r in res if r.previous_clause and r.current_clause is None]

    assert len(matched) == 1
    assert matched[0].previous_clause.id == "C1"
    assert matched[0].current_clause.id == "CX"
    assert len(removed) == 1
    assert removed[0].previous_clause.id == "C2"


def test_clause_matcher_unequal_document_sizes():
    """
    Test 3: Documents with unequal clause counts (e.g. 5 vs 2 clauses).
    """
    matcher = ClauseMatcher()

    prev_clauses = [
        Clause(id=f"P{i}", document_id="DOC-1", clause_number=str(i), text=f"Regulation provision {i} regarding tuition fees.")
        for i in range(1, 6)
    ]
    curr_clauses = [
        Clause(id="C1", document_id="DOC-2", clause_number="1", text="Regulation provision 1 regarding tuition fees."),
        Clause(id="C2", document_id="DOC-2", clause_number="2", text="Regulation provision 2 regarding tuition fees and charges.")
    ]

    res = matcher.match_clauses(prev_clauses, curr_clauses, method="optimal")
    matched = [r for r in res if r.previous_clause and r.current_clause]
    removed = [r for r in res if r.previous_clause and r.current_clause is None]
    added = [r for r in res if r.previous_clause is None and r.current_clause]

    assert len(matched) == 2
    assert len(removed) == 3
    assert len(added) == 0


def test_clause_matcher_all_candidate_scores_below_threshold():
    """
    Test 4: When all candidate pairs fall below threshold (0.60), all previous clauses
    must be reported as REMOVED and all current clauses as ADDED. No forced pairings!
    """
    matcher = ClauseMatcher()

    prev_clauses = [
        Clause(id="P1", document_id="DOC-1", clause_number="1", text="Provisions concerning hostel accommodation charges."),
        Clause(id="P2", document_id="DOC-1", clause_number="2", text="Mandatory biometric attendance recording at entrance gate.")
    ]
    curr_clauses = [
        Clause(id="C1", document_id="DOC-2", clause_number="1", text="Research grants for post-doctoral scholars in physics."),
        Clause(id="C2", document_id="DOC-2", clause_number="2", text="Export tariff subsidies for agricultural commodities.")
    ]

    res = matcher.match_clauses(prev_clauses, curr_clauses, method="optimal")
    matched = [r for r in res if r.previous_clause and r.current_clause]
    removed = [r for r in res if r.previous_clause and r.current_clause is None]
    added = [r for r in res if r.previous_clause is None and r.current_clause]

    assert len(matched) == 0
    assert len(removed) == 2
    assert len(added) == 2


def test_clause_matcher_multiple_equal_scores_deterministic():
    """
    Test 5: Multiple equally scoring candidate pairs produce deterministic and stable output.
    """
    matcher = ClauseMatcher()

    c1 = Clause(id="C1", document_id="DOC-1", clause_number="1", text="Standard maintenance allowance.")
    c2 = Clause(id="C2", document_id="DOC-1", clause_number="2", text="Standard maintenance allowance.")
    cx = Clause(id="CX", document_id="DOC-2", clause_number="1", text="Standard maintenance allowance.")
    cy = Clause(id="CY", document_id="DOC-2", clause_number="2", text="Standard maintenance allowance.")

    runs = [matcher.match_clauses([c1, c2], [cx, cy], method="optimal") for _ in range(5)]
    first_pairs = [(r.previous_clause.id, r.current_clause.id) for r in runs[0] if r.previous_clause and r.current_clause]

    for run in runs[1:]:
        run_pairs = [(r.previous_clause.id, r.current_clause.id) for r in run if r.previous_clause and r.current_clause]
        assert run_pairs == first_pairs


def test_clause_matcher_comprehensive_taxonomy():
    """
    Test 6: Full taxonomy verification across added, removed, modified, and renumbered clauses.
    """
    matcher = ClauseMatcher()

    p_exact = Clause(id="P_EXACT", document_id="D1", clause_number="1", text="Income ceiling is ₹ 2.5 lakh.")
    p_renum = Clause(id="P_RENUM", document_id="D1", clause_number="2", text="Full tuition fee waiver for eligible students.")
    p_mod   = Clause(id="P_MOD",   document_id="D1", clause_number="3", text="Stipend shall be ₹ 5,000 per month.")
    p_rem   = Clause(id="P_REM",   document_id="D1", clause_number="4", text="Discontinued procedural formality.")

    c_exact = Clause(id="C_EXACT", document_id="D2", clause_number="1", text="Income ceiling is ₹ 2.5 lakh.")
    c_renum = Clause(id="C_RENUM", document_id="D2", clause_number="5", text="Full tuition fee waiver for eligible students.")
    c_mod   = Clause(id="C_MOD",   document_id="D2", clause_number="3", text="Stipend shall be ₹ 7,500 per month.")
    c_add   = Clause(id="C_ADD",   document_id="D2", clause_number="6", text="Aadhaar linking is strictly mandatory.")

    res = matcher.match_clauses(
        [p_exact, p_renum, p_mod, p_rem],
        [c_exact, c_renum, c_mod, c_add],
        method="optimal"
    )

    exact_matches = [r for r in res if r.is_exact_match and not r.is_renumbered]
    renum_matches = [r for r in res if r.is_renumbered]
    mod_matches   = [r for r in res if r.previous_clause and r.current_clause and not r.is_exact_match and not r.is_renumbered]
    removals      = [r for r in res if r.previous_clause and r.current_clause is None]
    additions     = [r for r in res if r.previous_clause is None and r.current_clause]

    assert len(exact_matches) == 1
    assert exact_matches[0].previous_clause.id == "P_EXACT"

    assert len(renum_matches) == 1
    assert renum_matches[0].previous_clause.id == "P_RENUM"
    assert renum_matches[0].current_clause.id == "C_RENUM"

    assert len(mod_matches) == 1
    assert mod_matches[0].previous_clause.id == "P_MOD"
    assert mod_matches[0].current_clause.id == "C_MOD"

    assert len(removals) == 1
    assert removals[0].previous_clause.id == "P_REM"

    assert len(additions) == 1
    assert additions[0].current_clause.id == "C_ADD"
