"""
Evidence Engine Module.

Guarantees evidentiary provenance for all regulatory conclusions, change records,
impact assessments, and conflict detections.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from shared.schemas import EvidenceRecord, Clause, Document


class EvidenceMissingError(ValueError):
    """Raised when a regulatory conclusion or change lacks mandatory supporting evidence."""
    pass


class EvidenceEngine:
    """Enforces strict evidence attachment and audits regulatory conclusions."""

    @staticmethod
    def create_evidence(
        document_id: str,
        exact_supporting_text: str,
        clause_id: Optional[str] = None,
        source_url: Optional[str] = None,
        page_or_section: Optional[str] = None,
        is_inferred: bool = False,
        confidence: float = 1.0,
        notes: Optional[str] = None
    ) -> EvidenceRecord:
        """Constructs and validates an EvidenceRecord."""
        if not exact_supporting_text or not exact_supporting_text.strip():
            raise EvidenceMissingError(f"Evidence text cannot be empty for document {document_id}")
            
        return EvidenceRecord(
            document_id=document_id,
            clause_id=clause_id,
            source_url=source_url,
            exact_supporting_text=exact_supporting_text.strip(),
            page_or_section=page_or_section,
            is_inferred=is_inferred,
            confidence=max(0.0, min(1.0, confidence)),
            notes=notes
        )

    @classmethod
    def from_clause(
        cls,
        clause: Clause,
        document: Optional[Document] = None,
        is_inferred: bool = False,
        confidence: float = 1.0,
        notes: Optional[str] = None
    ) -> EvidenceRecord:
        """Generates an EvidenceRecord directly from an existing Clause object."""
        doc_id = document.id if document else clause.document_id
        source_url = document.source_url if document else None
        page_sec = f"Page {clause.page_number}" if clause.page_number else clause.section
        
        return cls.create_evidence(
            document_id=doc_id,
            clause_id=clause.id,
            source_url=source_url,
            exact_supporting_text=clause.text,
            page_or_section=page_sec,
            is_inferred=is_inferred,
            confidence=confidence,
            notes=notes
        )

    @staticmethod
    def validate_records(evidence_list: List[EvidenceRecord], context_description: str = "") -> bool:
        """
        Validates that at least one verifiable evidence record is present.
        Raises EvidenceMissingError if evidence is missing.
        """
        if not evidence_list:
            msg = f"Regulatory conclusion lacks evidence! Context: {context_description}"
            raise EvidenceMissingError(msg)
            
        for ev in evidence_list:
            if not ev.document_id or not ev.exact_supporting_text:
                raise EvidenceMissingError(f"Malformed evidence record in context: {context_description}")
        return True

    @staticmethod
    def verify_verbatim_quote(document_text: str, quoted_snippet: str) -> bool:
        """Checks if the quoted evidence appears verbatim in the source document text."""
        if not document_text or not quoted_snippet:
            return False
            
        clean_doc = " ".join(document_text.split()).lower()
        clean_quote = " ".join(quoted_snippet.split()).lower()
        return clean_quote in clean_doc

    @staticmethod
    def format_audit_trail(evidence_list: List[EvidenceRecord]) -> str:
        """Formats evidence records into a readable markdown audit report."""
        if not evidence_list:
            return "No supporting evidence provided."
            
        lines = ["### Regulatory Evidence Audit Trail\n"]
        for idx, ev in enumerate(evidence_list, 1):
            inf_label = "[INFERRED]" if ev.is_inferred else "[DIRECT VERBATIM]"
            lines.append(f"**{idx}. {inf_label} Source: `{ev.document_id}` (Clause: `{ev.clause_id or 'General'}`)**")
            lines.append(f"> \"{ev.exact_supporting_text}\"")
            if ev.page_or_section:
                lines.append(f"- *Section/Page:* {ev.page_or_section}")
            if ev.source_url:
                lines.append(f"- *Official Portal:* {ev.source_url}")
            lines.append(f"- *Verification Confidence:* {ev.confidence * 100:.1f}%\n")
        return "\n".join(lines)
