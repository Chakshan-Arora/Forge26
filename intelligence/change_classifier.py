"""
Change Classifier Module.

Classifies regulatory changes into authoritative change types:
ADDED, REMOVED, MODIFIED, REPLACED, EXTENDED, EXEMPTED, CLARIFIED, UNKNOWN.
Extracts structured delta values, effective dates, uncertainties, and evidence.
"""

from __future__ import annotations
import re
import uuid
from typing import Any, Dict, List, Optional, Tuple

from shared.schemas import (
    ChangeRecord,
    ChangeType,
    Clause,
    Document,
    EvidenceRecord,
    StructuredValue,
)
from intelligence.clause_matcher import ClauseMatchResult
from intelligence.normalizer import RegulatoryNormalizer
from intelligence.semantic_comparator import SemanticComparator
from intelligence.evidence_engine import EvidenceEngine


class ChangeClassifier:
    """Classifies matched clause pairs into ChangeRecord instances."""

    REPLACEMENT_PATTERNS = [
        re.compile(r"\b(?:substituted|stands\s+substituted|replaces|shall\s+be\s+substituted)\b", re.IGNORECASE),
        re.compile(r"\bin\s+supersession\s+of\b", re.IGNORECASE),
    ]

    EXTENSION_PATTERNS = [
        re.compile(r"\b(?:extended|extension\s+of|valid\s+up\s+to|extended\s+till|prolonged)\b", re.IGNORECASE),
    ]

    EXEMPTION_PATTERNS = [
        re.compile(r"\b(?:exempted|exemption|relaxation|relaxed|concession|waiver|waived)\b", re.IGNORECASE),
        re.compile(r"\bprovided\s+(?:further\s+)?that\s+for\b", re.IGNORECASE),
    ]

    CLARIFICATION_PATTERNS = [
        re.compile(r"\b(?:clarified|clarification|for\s+the\s+removal\s+of\s+doubts?|avoidance\s+of\s+doubt)\b", re.IGNORECASE),
    ]

    @classmethod
    def _detect_change_type(
        cls,
        prev_clause: Optional[Clause],
        curr_clause: Optional[Clause],
        match_result: ClauseMatchResult
    ) -> ChangeType:
        """Determines the exact ChangeType based on legal heuristics."""
        # 1. Clause Added
        if prev_clause is None and curr_clause is not None:
            text = curr_clause.text
            for pat in cls.REPLACEMENT_PATTERNS:
                if pat.search(text):
                    return ChangeType.REPLACED
            for pat in cls.EXEMPTION_PATTERNS:
                if pat.search(text):
                    return ChangeType.EXEMPTED
            for pat in cls.CLARIFICATION_PATTERNS:
                if pat.search(text):
                    return ChangeType.CLARIFIED
            return ChangeType.ADDED

        # 2. Clause Removed
        if prev_clause is not None and curr_clause is None:
            return ChangeType.REMOVED

        # 3. Clause Modified / Replaced / Extended / Exempted / Clarified
        if prev_clause is not None and curr_clause is not None:
            curr_text = curr_clause.text
            
            # Check for explicit substitution formula
            for pat in cls.REPLACEMENT_PATTERNS:
                if pat.search(curr_text):
                    return ChangeType.REPLACED
                    
            # Check for extension
            for pat in cls.EXTENSION_PATTERNS:
                if pat.search(curr_text) and not pat.search(prev_clause.text):
                    return ChangeType.EXTENDED
                    
            # Check for newly introduced exemptions
            for pat in cls.EXEMPTION_PATTERNS:
                if pat.search(curr_text) and not pat.search(prev_clause.text):
                    return ChangeType.EXEMPTED
                    
            # Check for clarification
            for pat in cls.CLARIFICATION_PATTERNS:
                if pat.search(curr_text) and not pat.search(prev_clause.text):
                    return ChangeType.CLARIFIED

            return ChangeType.MODIFIED

        return ChangeType.UNKNOWN

    @classmethod
    def _extract_values_pair(
        cls,
        prev_clause: Optional[Clause],
        curr_clause: Optional[Clause]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Extracts and formats previous and current structured values."""
        prev_vals = RegulatoryNormalizer.extract_structured_values(prev_clause.text) if prev_clause else []
        curr_vals = RegulatoryNormalizer.extract_structured_values(curr_clause.text) if curr_clause else []

        prev_val_dict = prev_vals[0].model_dump() if prev_vals else (prev_clause.structured_attributes if prev_clause and prev_clause.structured_attributes else None)
        curr_val_dict = curr_vals[0].model_dump() if curr_vals else (curr_clause.structured_attributes if curr_clause and curr_clause.structured_attributes else None)

        return prev_val_dict, curr_val_dict

    @classmethod
    def build_change_record(
        cls,
        match: ClauseMatchResult,
        curr_document: Document,
        prev_document: Optional[Document] = None
    ) -> Optional[ChangeRecord]:
        """
        Builds a validated ChangeRecord for a matched pair or addition/removal.
        Returns None if clauses are completely identical with no renumbering.
        """
        if match.is_exact_match and not match.is_renumbered:
            # Completely unchanged clause; no regulatory modification to record
            return None

        prev_c = match.previous_clause
        curr_c = match.current_clause
        
        change_type = cls._detect_change_type(prev_c, curr_c, match)
        prev_val, curr_val = cls._extract_values_pair(prev_c, curr_c)
        
        # Determine clause ID
        clause_id = curr_c.id if curr_c else (prev_c.id if prev_c else "UNKNOWN_CLAUSE")
        
        # Effective date resolution
        effective_from = None
        if curr_document and curr_document.effective_date:
            effective_from = curr_document.effective_date
        elif curr_document and curr_document.publication_date:
            effective_from = curr_document.publication_date

        evidence_list: List[EvidenceRecord] = []
        uncertainties: List[str] = []

        # Construct Evidence
        if curr_c:
            evidence_list.append(
                EvidenceEngine.from_clause(
                    curr_c,
                    document=curr_document,
                    is_inferred=False,
                    confidence=0.95,
                    notes=f"Current provision in document {curr_document.id}"
                )
            )
        if prev_c:
            evidence_list.append(
                EvidenceEngine.from_clause(
                    prev_c,
                    document=prev_document,
                    is_inferred=False,
                    confidence=0.95,
                    notes=f"Previous provision in document {prev_document.id if prev_document else 'BASE'}"
                )
            )

        # Confidence calculation
        if change_type == ChangeType.ADDED:
            confidence = 0.95
        elif change_type == ChangeType.REMOVED:
            confidence = 0.85
            uncertainties.append(
                "Clause absent in current document. Does not legally confirm total repeal without an explicit supersession notification."
            )
        elif match.is_renumbered:
            confidence = 0.90
            uncertainties.append(
                f"Clause renumbered from {prev_c.clause_number if prev_c else '?'} to {curr_c.clause_number if curr_c else '?'}; core text retained."
            )
        else:
            confidence = min(0.98, max(0.60, match.similarity_score))

        # Check numeric shift
        if prev_val and curr_val and prev_val.get("value_type") == curr_val.get("value_type"):
            p_num = prev_val.get("numeric_amount")
            c_num = curr_val.get("numeric_amount")
            if p_num is not None and c_num is not None and p_num != c_num:
                uncertainties.append(
                    f"Quantitative threshold shift: {prev_val.get('value_type')} changed from {p_num} to {c_num} {curr_val.get('unit', '')}"
                )

        unique_id = f"CHG-{uuid.uuid4().hex[:10].upper()}"

        return ChangeRecord(
            change_id=unique_id,
            document_id=curr_document.id,
            previous_document_id=prev_document.id if prev_document else None,
            clause_id=clause_id,
            change_type=change_type,
            previous_text=prev_c.text if prev_c else None,
            current_text=curr_c.text if curr_c else None,
            previous_value=prev_val,
            current_value=curr_val,
            effective_from=effective_from,
            affected_groups=[],
            evidence=evidence_list,
            confidence=confidence,
            uncertainties=uncertainties
        )
