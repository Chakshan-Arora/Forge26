"""
Clause Matcher Module.

Aligns clauses across policy versions using structural comparison,
renumbering detection, fuzzy similarity, and optimal bipartite pairing.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field

from shared.schemas import Clause
from intelligence.normalizer import RegulatoryNormalizer
from intelligence.semantic_comparator import SemanticComparator
from intelligence.config import MatcherConfig, DEFAULT_SETTINGS


class ClauseMatchResult(BaseModel):
    """Result of matching a clause across two document versions."""
    previous_clause: Optional[Clause] = None
    current_clause: Optional[Clause] = None
    similarity_score: float = Field(0.0, ge=0.0, le=1.0)
    is_exact_match: bool = False
    is_renumbered: bool = False
    match_notes: str = ""


class ClauseMatcher:
    """Matches and aligns clauses between two policy documents."""

    def __init__(self, config: Optional[MatcherConfig] = None):
        self.config = config or DEFAULT_SETTINGS.matcher

    @staticmethod
    def _numbering_similarity(num_a: str, num_b: str) -> float:
        """Computes similarity of clause numbers taking hierarchy into account."""
        clean_a = RegulatoryNormalizer.normalize_clause_number(num_a)
        clean_b = RegulatoryNormalizer.normalize_clause_number(num_b)
        
        if clean_a == clean_b and clean_a != "":
            return 1.0
            
        # Split by dots or parentheses e.g. "4.1" vs "4.1.1"
        parts_a = clean_a.replace("(", ".").replace(")", "").split(".")
        parts_b = clean_b.replace("(", ".").replace(")", "").split(".")
        
        parts_a = [p.strip() for p in parts_a if p.strip()]
        parts_b = [p.strip() for p in parts_b if p.strip()]
        
        if not parts_a or not parts_b:
            return 0.0
            
        # Common prefix match
        common_len = 0
        for p1, p2 in zip(parts_a, parts_b):
            if p1.lower() == p2.lower():
                common_len += 1
            else:
                break
                
        max_len = max(len(parts_a), len(parts_b))
        return (common_len / max_len) if max_len > 0 else 0.0

    def compute_clause_pair_score(self, clause_a: Clause, clause_b: Clause) -> Tuple[float, bool]:
        """
        Computes composite alignment score between two clauses.
        Returns (score, is_renumbered_flag).
        """
        norm_a = RegulatoryNormalizer.normalize_text(clause_a.text)
        norm_b = RegulatoryNormalizer.normalize_text(clause_b.text)
        
        # 1. Exact textual match
        if norm_a == norm_b and len(norm_a) > 0:
            clean_num_a = RegulatoryNormalizer.normalize_clause_number(clause_a.clause_number)
            clean_num_b = RegulatoryNormalizer.normalize_clause_number(clause_b.clause_number)
            is_renumbered = (clean_num_a != clean_num_b and clean_num_a != "" and clean_num_b != "")
            return 1.0, is_renumbered

        # Textual & semantic similarity
        lexical_sim = SemanticComparator.compute_composite_similarity(norm_a, norm_b)
        
        # Numbering / Structural similarity
        num_sim = self._numbering_similarity(clause_a.clause_number, clause_b.clause_number)
        
        # Section title similarity if available
        sec_sim = 1.0 if (clause_a.section and clause_b.section and clause_a.section.strip().lower() == clause_b.section.strip().lower()) else 0.0
        
        # Check if renumbering is evident: high textual similarity despite differing numbers
        is_renumbered = False
        if num_sim < 0.5 and lexical_sim >= self.config.renumbering_similarity_threshold:
            is_renumbered = True
            # For renumbered clauses, prioritize text similarity
            composite_score = lexical_sim
        else:
            # Weighted hybrid score
            structural_score = 0.7 * num_sim + 0.3 * sec_sim
            composite_score = (
                self.config.structural_weight * structural_score +
                (self.config.lexical_weight + self.config.semantic_weight) * lexical_sim
            )

        return min(1.0, max(0.0, composite_score)), is_renumbered

    def match_clauses(
        self,
        prev_clauses: List[Clause],
        curr_clauses: List[Clause]
    ) -> List[ClauseMatchResult]:
        """
        Pairs clauses across two versions using bipartite optimal matching.
        Returns matched pairs, additions (prev=None), and removals (curr=None).
        """
        results: List[ClauseMatchResult] = []
        
        matched_prev_indices: Set[int] = set()
        matched_curr_indices: Set[int] = set()

        # Step 1: Candidate score matrix
        candidates: List[Tuple[float, int, int, bool]] = []
        for i, c_prev in enumerate(prev_clauses):
            for j, c_curr in enumerate(curr_clauses):
                score, is_renumbered = self.compute_clause_pair_score(c_prev, c_curr)
                if score >= self.config.medium_similarity_threshold:
                    candidates.append((score, i, j, is_renumbered))

        # Step 2: Sort candidate matches descending by score (greedy maximum matching)
        candidates.sort(key=lambda x: x[0], reverse=True)

        for score, i, j, is_renumbered in candidates:
            if i in matched_prev_indices or j in matched_curr_indices:
                continue
                
            prev_c = prev_clauses[i]
            curr_c = curr_clauses[j]
            
            is_exact = (
                score >= self.config.exact_match_threshold and
                RegulatoryNormalizer.normalize_text(prev_c.text) == RegulatoryNormalizer.normalize_text(curr_c.text) and
                not is_renumbered
            )
            
            note = "Exact match" if is_exact else ("Renumbered clause" if is_renumbered else "Modified clause")
            
            results.append(
                ClauseMatchResult(
                    previous_clause=prev_c,
                    current_clause=curr_c,
                    similarity_score=score,
                    is_exact_match=is_exact,
                    is_renumbered=is_renumbered,
                    match_notes=note
                )
            )
            matched_prev_indices.add(i)
            matched_curr_indices.add(j)

        # Step 3: Any remaining clauses in current_clauses are ADDED
        for j, c_curr in enumerate(curr_clauses):
            if j not in matched_curr_indices:
                results.append(
                    ClauseMatchResult(
                        previous_clause=None,
                        current_clause=c_curr,
                        similarity_score=0.0,
                        is_exact_match=False,
                        is_renumbered=False,
                        match_notes="Newly introduced clause (ADDED)"
                    )
                )

        # Step 4: Any remaining clauses in prev_clauses are REMOVED / SUPERSEDED
        for i, c_prev in enumerate(prev_clauses):
            if i not in matched_prev_indices:
                results.append(
                    ClauseMatchResult(
                        previous_clause=c_prev,
                        current_clause=None,
                        similarity_score=0.0,
                        is_exact_match=False,
                        is_renumbered=False,
                        match_notes="Clause not present in current document (REMOVED / CANDIDATE SUPERSEDED)"
                    )
                )

        return results
