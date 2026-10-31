"""
Evidence Service for Policy Intel.

Manages evidence verification, citation formatting, provenance tracking,
confidence scoring, and regulatory audit trail generation.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from shared.schemas import EvidenceRecord
from shared.constants import (
    HIGH_CONFIDENCE_THRESHOLD,
    MEDIUM_CONFIDENCE_THRESHOLD,
    REASONING_FACTUAL,
    REASONING_DETERMINISTIC,
    REASONING_INFERRED,
    REASONING_UNRESOLVED,
)


class EvidenceService:
    """Provides evidence verification and reasoning classification helpers."""

    @staticmethod
    def classify_reasoning(
        evidence_list: List[EvidenceRecord],
        is_calculation: bool = False,
        has_unresolved: bool = False
    ) -> str:
        """
        Determines the explicit reasoning category for an answer or finding:
        - RETRIEVED_FACT: Directly quoted from official gazette or clause.
        - DETERMINISTIC_CALCULATION: Derived from exact math comparison (e.g. ₹2.5L to ₹3.5L delta).
        - AI_INFERRED_INTERPRETATION: Synthesized inference based on legal wording.
        - UNRESOLVED_AMBIGUITY: Multiple conflicting clauses or missing statutory timeline.
        """
        if has_unresolved:
            return REASONING_UNRESOLVED
        if is_calculation:
            return REASONING_DETERMINISTIC
        if any(e.is_inferred for e in evidence_list):
            return REASONING_INFERRED
        return REASONING_FACTUAL

    @staticmethod
    def calculate_aggregate_confidence(evidence_list: List[EvidenceRecord]) -> float:
        """Computes aggregate confidence score across all supporting evidence."""
        if not evidence_list:
            return 0.5
        scores = [e.confidence for e in evidence_list if e.confidence is not None]
        if not scores:
            return 0.5
        return round(sum(scores) / len(scores), 2)

    @staticmethod
    def format_citation(evidence: EvidenceRecord) -> str:
        """Formats a single evidence record into an official legal citation."""
        loc = f", Page/Section: {evidence.page_or_section}" if evidence.page_or_section else ""
        cl = f", Clause: {evidence.clause_id}" if evidence.clause_id else ""
        return f"[{evidence.document_id}{cl}{loc}] \"{evidence.exact_supporting_text.strip()}\""

    @staticmethod
    def build_evidence_dossier(evidence_list: List[EvidenceRecord]) -> List[Dict[str, Any]]:
        """Constructs rich evidence cards for UI presentation."""
        dossier = []
        for ev in evidence_list:
            confidence_level = (
                "HIGH" if ev.confidence >= HIGH_CONFIDENCE_THRESHOLD
                else "MEDIUM" if ev.confidence >= MEDIUM_CONFIDENCE_THRESHOLD
                else "LOW"
            )
            dossier.append({
                "document_id": ev.document_id,
                "clause_id": ev.clause_id,
                "source_url": ev.source_url,
                "exact_supporting_text": ev.exact_supporting_text,
                "page_or_section": ev.page_or_section,
                "is_inferred": ev.is_inferred,
                "confidence": ev.confidence,
                "confidence_level": confidence_level,
                "notes": ev.notes,
            })
        return dossier
