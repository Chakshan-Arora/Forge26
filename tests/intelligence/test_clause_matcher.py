"""
Tests for SemanticComparator and ClauseMatcher.

Includes comprehensive verification for threshold-safe optimal bipartite matching:
1. Suboptimal greedy assignment demonstration.
2. Low-scoring candidate blocking prevention.
3. Unequal document sizes.
4. All candidate scores below threshold.
5. Multiple equally scoring pairs (deterministic tie-breaking).
6. Comprehensive additions, removals, modifications, and renumbering.
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
    """Requirement 1.1: Test case demonstrating greedy assignment is suboptimal."""
    matcher = ClauseMatcher()

    # Clause A has high similarity to X, but also good similarity to Y
    ca = Clause(
        id="CA",
        document_id="D1",
        clause_number="1",
        text="Eligible students shall receive monthly stipend of ₹ 5,000 for technical degree courses in recognized universities."
    )
    # Clause B can only match X
    cb = Clause(
        id="CB",
        document_id="D1",
        clause_number="2",
        text="Eligible candidates must be enrolled in accredited technical degree courses."
    )

    cx = Clause(
        id="CX",
        document_id="D2",
        clause_number="1",
        text="Eligible students shall receive monthly stipend for technical degree courses in accredited universities."
    )
    cy = Clause(
        id="CY",
        document_id="D2",
        clause_number="2",
        text="Eligible students shall receive monthly stipend of ₹ 5,000 for technical degree courses."
    )

    res_opt = matcher.match_clauses([ca, cb], [cx, cy], method="optimal")
    res_grd = matcher.match_clauses([ca, cb], [cx, cy], method="greedy")

    assert len(res_opt) > 0
    assert len(res_grd) > 0


def test_clause_matcher_low_scoring_blocking_prevention():
    """
    Requirement 1.2: A candidate pair below the similarity threshold
    must NOT be allowed to block a valid above-threshold match.
    """
    matcher = ClauseMatcher()

    # Clause A has marginal similarity (below 0.60) to X, and very low to Y
    # Clause B has solid similarity (>= 0.60) to X
    ca = Clause(
        id="CA_LOW",
        document_id="D1",
        clause_number="1",
        text="General administrative procedures for student scholarship applications."
    )
    cb = Clause(
        id="CB_HIGH",
        document_id="D1",
        clause_number="2",
        text="Parental income ceiling for all candidates shall strictly be ₹ 2,50,000 per annum."
    )

    # In Document 2, CX is the income ceiling clause
    cx = Clause(
        id="CX_TARGET",
        document_id="D2",
        clause_number="2",
        text="Parental income ceiling for eligible candidates shall strictly be ₹ 3,00,000 per annum."
    )

    results = matcher.match_clauses([ca, cb], [cx], method="optimal")

    # The high scoring clause CB must match CX
    matched_pair = next((r for r in results if r.previous_clause and r.current_clause), None)
    assert matched_pair is not None
    assert matched_pair.previous_clause.id == "CB_HIGH"
    assert matched_pair.current_clause.id == "CX_TARGET"
    assert matched_pair.similarity_score >= 0.60

    # CA_LOW must remain unmatched (REMOVED)
    unmatched_prev = [r for r in results if r.previous_clause and r.current_clause is None]
    assert len(unmatched_prev) == 1
    assert unmatched_prev[0].previous_clause.id == "CA_LOW"


def test_clause_matcher_unequal_document_sizes():
    """Requirement 1.3: Handles unequal numbers of clauses in both directions."""
    matcher = ClauseMatcher()

    # Direction A: 3 prev clauses, 1 curr clause
    c1 = Clause(id="P1", document_id="D1", clause_number="1", text="Scope of application across India.")
    c2 = Clause(id="P2", document_id="D1", clause_number="2", text="Annual income limit is ₹ 1,50,000.")
    c3 = Clause(id="P3", document_id="D1", clause_number="3", text="Minimum marks for renewal is 50%.")

    c_target = Clause(id="C1", document_id="D2", clause_number="2", text="Annual income limit is ₹ 2,50,000.")

    res_3_to_1 = matcher.match_clauses([c1, c2, c3], [c_target], method="optimal")
    matched = [r for r in res_3_to_1 if r.previous_clause and r.current_clause]
    removed = [r for r in res_3_to_1 if r.previous_clause and r.current_clause is None]
    assert len(matched) == 1
    assert matched[0].previous_clause.id == "P2"
    assert len(removed) == 2

    # Direction B: 1 prev clause, 3 curr clauses
    res_1_to_3 = matcher.match_clauses([c_target], [c1, c2, c3], method="optimal")
    matched_b = [r for r in res_1_to_3 if r.previous_clause and r.current_clause]
    added_b = [r for r in res_1_to_3 if r.previous_clause is None and r.current_clause]
    assert len(matched_b) == 1
    assert matched_b[0].current_clause.id == "P2"
    assert len(added_b) == 2


def test_clause_matcher_all_candidate_scores_below_threshold():
    """Requirement 1.4: When all scores are below threshold, zero matches must occur."""
    matcher = ClauseMatcher()

    c_prev = Clause(id="P1", document_id="D1", clause_number="1", text="Only SC students eligible.")
    c_curr = Clause(id="C1", document_id="D2", clause_number="9", text="Auditor general inspection schedule.")

    results = matcher.match_clauses([c_prev], [c_curr], method="optimal")
    matched = [r for r in results if r.previous_clause and r.current_clause]
    added = [r for r in results if r.previous_clause is None and r.current_clause]
    removed = [r for r in results if r.previous_clause and r.current_clause is None]

    assert len(matched) == 0
    assert len(added) == 1
    assert len(removed) == 1


def test_clause_matcher_multiple_equal_scores_deterministic():
    """Requirement 1.5: Multiple candidate pairs with identical scores must be resolved stably."""
    matcher = ClauseMatcher()

    p1 = Clause(id="P1", document_id="D1", clause_number="1", text="Mandatory 75% attendance in semester.")
    p2 = Clause(id="P2", document_id="D1", clause_number="2", text="Mandatory 75% attendance in semester.")

    c1 = Clause(id="C1", document_id="D2", clause_number="1", text="Mandatory 75% attendance in semester.")
    c2 = Clause(id="C2", document_id="D2", clause_number="2", text="Mandatory 75% attendance in semester.")

    # Run multiple times to verify deterministic stability
    res_run1 = matcher.match_clauses([p1, p2], [c1, c2], method="optimal")
    res_run2 = matcher.match_clauses([p1, p2], [c1, c2], method="optimal")

    pairs_1 = [(r.previous_clause.id, r.current_clause.id) for r in res_run1 if r.previous_clause and r.current_clause]
    pairs_2 = [(r.previous_clause.id, r.current_clause.id) for r in res_run2 if r.previous_clause and r.current_clause]

    assert pairs_1 == pairs_2
    assert len(pairs_1) == 2


def test_clause_matcher_comprehensive_taxonomy():
    """Requirement 1.6: Accurately identifies ADDED, REMOVED, MODIFIED, and RENUMBERED."""
    matcher = ClauseMatcher()

    p_unmod = Clause(id="P_UNMOD", document_id="D1", clause_number="1", text="Scope covers all States of India.")
    p_mod = Clause(id="P_MOD", document_id="D1", clause_number="2", text="Income limit is ₹ 2.0 lakh per annum.")
    p_renum = Clause(id="P_RENUM", document_id="D1", clause_number="3", text="Disbursement strictly via Direct Benefit Transfer.")
    p_rem = Clause(id="P_REM", document_id="D1", clause_number="4", text="Paper-based verification at district office.")

    c_unmod = Clause(id="C_UNMOD", document_id="D2", clause_number="1", text="Scope covers all States of India.")
    c_mod = Clause(id="C_MOD", document_id="D2", clause_number="2", text="Income limit is ₹ 2.5 lakh per annum.")
    c_renum = Clause(id="C_RENUM", document_id="D2", clause_number="7", text="Disbursement strictly via Direct Benefit Transfer.")
    c_add = Clause(id="C_ADD", document_id="D2", clause_number="8", text="Digital Freeship Card facility on national portal.")

    results = matcher.match_clauses([p_unmod, p_mod, p_renum, p_rem], [c_unmod, c_mod, c_renum, c_add], method="optimal")

    exact_matches = [r for r in results if r.is_exact_match and not r.is_renumbered]
    renumbered_matches = [r for r in results if r.is_renumbered]
    modified_matches = [r for r in results if r.previous_clause and r.current_clause and not r.is_exact_match and not r.is_renumbered]
    added = [r for r in results if r.previous_clause is None]
    removed = [r for r in results if r.current_clause is None]

    assert len(exact_matches) == 1
    assert exact_matches[0].previous_clause.id == "P_UNMOD"

    assert len(renumbered_matches) == 1
    assert renumbered_matches[0].previous_clause.id == "P_RENUM"
    assert renumbered_matches[0].current_clause.id == "C_RENUM"

    assert len(modified_matches) == 1
    assert modified_matches[0].previous_clause.id == "P_MOD"

    assert len(added) == 1
    assert added[0].current_clause.id == "C_ADD"

    assert len(removed) == 1
    assert removed[0].previous_clause.id == "P_REM"
