"""
Tests for SemanticComparator and ClauseMatcher.
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
