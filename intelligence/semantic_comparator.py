"""
Semantic Comparator for Regulatory Policies.

Combines deterministic lexical, n-gram, and token-level semantic matching
with legal obligation/negation change detection and optional LLM hooks.
"""

from __future__ import annotations
import math
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import Counter


class SemanticComparator:
    """Computes similarity and identifies legal semantic shifts between clause texts."""

    MODALITY_WORDS: Set[str] = {"shall", "must", "mandatory", "required", "compulsory", "may", "optional", "discretionary"}
    NEGATION_WORDS: Set[str] = {"not", "never", "ineligible", "neither", "nor", "excluded", "prohibited", "debarred"}

    @classmethod
    def tokenize(cls, text: str) -> List[str]:
        """Extracts normalized alphanumeric tokens."""
        if not text:
            return []
        return re.findall(r"\b[a-zA-Z0-9_\.]+\b", text.lower())

    @classmethod
    def jaccard_similarity(cls, text_a: str, text_b: str) -> float:
        """Computes Jaccard similarity of unique word tokens."""
        tokens_a = set(cls.tokenize(text_a))
        tokens_b = set(cls.tokenize(text_b))
        if not tokens_a and not tokens_b:
            return 1.0
        if not tokens_a or not tokens_b:
            return 0.0
        intersection = len(tokens_a.intersection(tokens_b))
        union = len(tokens_a.union(tokens_b))
        return intersection / union

    @classmethod
    def ngram_cosine_similarity(cls, text_a: str, text_b: str, n: int = 3) -> float:
        """
        Computes character n-gram cosine similarity (TF representation).
        Extremely effective for regulatory texts with varying numbering or slight rephrasings.
        """
        if not text_a and not text_b:
            return 1.0
        if not text_a or not text_b:
            return 0.0
            
        def get_ngrams(s: str) -> Counter:
            clean = re.sub(r"\s+", " ", s.lower()).strip()
            if len(clean) < n:
                return Counter([clean])
            return Counter([clean[i:i+n] for i in range(len(clean) - n + 1)])

        counts_a = get_ngrams(text_a)
        counts_b = get_ngrams(text_b)
        
        all_keys = set(counts_a.keys()).union(set(counts_b.keys()))
        dot = sum(counts_a[k] * counts_b[k] for k in all_keys)
        mag_a = math.sqrt(sum(v * v for v in counts_a.values()))
        mag_b = math.sqrt(sum(v * v for v in counts_b.values()))
        
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)

    @classmethod
    def token_overlap_ratio(cls, text_a: str, text_b: str) -> float:
        """Computes symmetric token multiset overlap ratio (Dice coefficient)."""
        tokens_a = Counter(cls.tokenize(text_a))
        tokens_b = Counter(cls.tokenize(text_b))
        if not tokens_a and not tokens_b:
            return 1.0
        if not tokens_a or not tokens_b:
            return 0.0
            
        common = sum((tokens_a & tokens_b).values())
        total = sum(tokens_a.values()) + sum(tokens_b.values())
        return (2.0 * common) / total if total > 0 else 0.0

    @classmethod
    def compute_composite_similarity(cls, text_a: str, text_b: str) -> float:
        """
        Blended similarity score combining:
        - 40% character n-gram cosine (syntax/structure)
        - 40% token overlap ratio (lexical tokens)
        - 20% Jaccard similarity (vocabulary alignment)
        """
        if text_a.strip() == text_b.strip():
            return 1.0
        c_ngram = cls.ngram_cosine_similarity(text_a, text_b, n=3)
        t_overlap = cls.token_overlap_ratio(text_a, text_b)
        j_sim = cls.jaccard_similarity(text_a, text_b)
        return 0.40 * c_ngram + 0.40 * t_overlap + 0.20 * j_sim

    @classmethod
    def detect_legal_shifts(cls, text_a: str, text_b: str) -> Dict[str, Any]:
        """
        Detects significant regulatory shifts between two clause versions:
        - Negation flips (e.g. eligible -> ineligible)
        - Modality shifts (e.g. may -> shall)
        - Word additions/removals
        """
        tokens_a = set(cls.tokenize(text_a))
        tokens_b = set(cls.tokenize(text_b))
        
        # Check negations
        neg_a = tokens_a.intersection(cls.NEGATION_WORDS)
        neg_b = tokens_b.intersection(cls.NEGATION_WORDS)
        negation_shift = (len(neg_a) == 0 and len(neg_b) > 0) or (len(neg_a) > 0 and len(neg_b) == 0)
        
        # Check modalities
        mod_a = tokens_a.intersection(cls.MODALITY_WORDS)
        mod_b = tokens_b.intersection(cls.MODALITY_WORDS)
        modality_shift = mod_a != mod_b
        
        added_keywords = tokens_b - tokens_a
        removed_keywords = tokens_a - tokens_b
        
        return {
            "negation_shift": negation_shift,
            "modality_shift": modality_shift,
            "previous_modality": list(mod_a),
            "current_modality": list(mod_b),
            "added_keywords": list(added_keywords)[:15],
            "removed_keywords": list(removed_keywords)[:15],
        }

    @classmethod
    def interpret_complex_change(
        cls,
        prev_text: str,
        curr_text: str,
        llm_client: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Interprets complex changes. Uses deterministic logic first,
        with fallback/escalation to LLM if a client is provided.
        """
        sim = cls.compute_composite_similarity(prev_text, curr_text)
        shifts = cls.detect_legal_shifts(prev_text, curr_text)
        
        # If an LLM client is available and change is legally nuanced
        if llm_client is not None and 0.40 <= sim < 0.95:
            try:
                # LLM structured prompt
                prompt = (
                    "Analyze the legal differences between these two regulatory clauses:\n\n"
                    f"Previous Clause:\n{prev_text}\n\n"
                    f"Current Clause:\n{curr_text}\n\n"
                    "Specify:\n1. Nature of change\n2. Any changed condition or threshold\n3. Who is affected\n"
                )
                response = llm_client.generate(prompt)
                return {
                    "method": "llm_assisted",
                    "similarity": sim,
                    "interpretation": response,
                    "shifts": shifts
                }
            except Exception:
                pass # Gracefully degrade to deterministic reasoning
                
        # Deterministic interpretation
        summary_reasons = []
        if shifts["negation_shift"]:
            summary_reasons.append("Reversal in eligibility/prohibition status detected.")
        if shifts["modality_shift"]:
            summary_reasons.append(f"Legal obligation level shifted from {shifts['previous_modality']} to {shifts['current_modality']}.")
        if not summary_reasons:
            if sim >= 0.85:
                summary_reasons.append("Minor text adjustments or clarifications.")
            elif sim >= 0.60:
                summary_reasons.append("Substantial modification of wording or conditions.")
            else:
                summary_reasons.append("Major rewrite or replacement of regulatory provision.")

        return {
            "method": "deterministic",
            "similarity": sim,
            "summary": " ".join(summary_reasons),
            "shifts": shifts
        }
