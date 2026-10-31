"""
Change Detector Module.

Main orchestrator for clause-level policy comparison. Compares document versions,
tracks modifications, renumbering, additions, and quantitative threshold shifts.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from shared.schemas import ChangeRecord, Document, Clause
from intelligence.clause_matcher import ClauseMatcher
from intelligence.change_classifier import ChangeClassifier
from intelligence.config import MatcherConfig, DEFAULT_SETTINGS
from intelligence.evidence_engine import EvidenceEngine


class ChangeDetectionSummary(BaseModel):
    """Statistical summary of changes detected between two documents."""
    previous_document_id: Optional[str] = None
    current_document_id: str
    total_previous_clauses: int
    total_current_clauses: int
    total_changes: int
    additions_count: int
    removals_count: int
    modifications_count: int
    replacements_count: int
    extensions_count: int
    exemptions_count: int
    clarifications_count: int
    renumbered_count: int


class ChangeDetector:
    """Clause-level comparison engine for regulatory documents."""

    def __init__(self, matcher_config: Optional[MatcherConfig] = None):
        self.matcher = ClauseMatcher(config=matcher_config)
        self.classifier = ChangeClassifier()

    def compare_documents(
        self,
        previous_doc: Optional[Document],
        current_doc: Document,
        method: str = "optimal"
    ) -> List[ChangeRecord]:
        """
        Compares two policy documents at clause level.
        Produces authoritative ChangeRecord items conforming to shared contract.

        Args:
            previous_doc: Predecessor document version.
            current_doc: Successor/amending document version.
            method: 'optimal' (default Kuhn-Munkres) or 'greedy'.
        """
        if previous_doc is None:
            # Baseline document: all clauses are treated as initial ADDED provisions
            records: List[ChangeRecord] = []
            for clause in current_doc.clauses:
                from intelligence.clause_matcher import ClauseMatchResult
                add_match = ClauseMatchResult(
                    previous_clause=None,
                    current_clause=clause,
                    similarity_score=0.0,
                    is_exact_match=False,
                    is_renumbered=False,
                    match_notes="Initial baseline clause"
                )
                rec = self.classifier.build_change_record(add_match, current_doc, None)
                if rec:
                    records.append(rec)
            return records

        # Pair clauses using bipartite matcher (optimal or greedy)
        match_results = self.matcher.match_clauses(
            prev_clauses=previous_doc.clauses,
            curr_clauses=current_doc.clauses,
            method=method
        )

        records: List[ChangeRecord] = []
        for match in match_results:
            change_rec = self.classifier.build_change_record(
                match=match,
                curr_document=current_doc,
                prev_document=previous_doc
            )
            if change_rec:
                # Strictly enforce evidence presence
                EvidenceEngine.validate_records(
                    change_rec.evidence,
                    context_description=f"ChangeRecord {change_rec.change_id} for clause {change_rec.clause_id}"
                )
                records.append(change_rec)

        return records

    def summarize_changes(
        self,
        previous_doc: Optional[Document],
        current_doc: Document,
        changes: List[ChangeRecord]
    ) -> ChangeDetectionSummary:
        """Computes statistical summary of detected changes."""
        counts = {
            "ADDED": 0,
            "REMOVED": 0,
            "MODIFIED": 0,
            "REPLACED": 0,
            "EXTENDED": 0,
            "EXEMPTED": 0,
            "CLARIFIED": 0,
            "UNKNOWN": 0,
        }
        renumbered = 0
        for c in changes:
            counts[c.change_type.value] = counts.get(c.change_type.value, 0) + 1
            if any("renumbered" in u.lower() for u in c.uncertainties):
                renumbered += 1

        return ChangeDetectionSummary(
            previous_document_id=previous_doc.id if previous_doc else None,
            current_document_id=current_doc.id,
            total_previous_clauses=len(previous_doc.clauses) if previous_doc else 0,
            total_current_clauses=len(current_doc.clauses),
            total_changes=len(changes),
            additions_count=counts["ADDED"],
            removals_count=counts["REMOVED"],
            modifications_count=counts["MODIFIED"],
            replacements_count=counts["REPLACED"],
            extensions_count=counts["EXTENDED"],
            exemptions_count=counts["EXEMPTED"],
            clarifications_count=counts["CLARIFIED"],
            renumbered_count=renumbered
        )
