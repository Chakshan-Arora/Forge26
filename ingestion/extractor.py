"""
Policy Document Extractor.

Responsible for parsing raw government notifications, guidelines, and office memorandums
into structured Document and Clause representations with deterministic metadata,
clause segmentation, and structured value extraction.
"""

from __future__ import annotations
import re
import uuid
from typing import List, Dict, Any, Optional
from shared.schemas import Document, Clause, DocumentType, ClauseType
from intelligence.normalizer import RegulatoryNormalizer


class PolicyDocumentExtractor:
    """
    Deterministic rule-based extractor for Indian government policy documents.
    Segments raw text into structured clauses and extracts key regulatory attributes.
    """

    # Regex patterns for clause demarcation in Indian notifications
    CLAUSE_PATTERN = re.compile(
        r"(?:^|\n)\s*(?P<number>(?:Clause\s+)?(?:[A-ZIVXLCDM]+\.(?:\d+)?|\d+(?:\.\d+)*|[A-Z]\.|\([a-z0-9]+\)))\s*[:.-]?\s*(?P<content>.*?)(?=(?:\n\s*(?:Clause\s+)?(?:[A-ZIVXLCDM]+\.(?:\d+)?|\d+(?:\.\d+)*|[A-Z]\.|\([a-z0-9]+\))\s*[:.-]?)|\Z)",
        re.DOTALL
    )

    def __init__(self):
        self.normalizer = RegulatoryNormalizer()

    def extract_from_text(
        self,
        raw_text: str,
        document_id: Optional[str] = None,
        title: str = "Government Notification",
        scheme_name: str = "Central Scholarship Scheme",
        ministry: str = "Ministry of Education",
        document_type: DocumentType = DocumentType.NOTIFICATION,
        order_number: Optional[str] = None,
        publication_date: Optional[str] = None,
        effective_date: Optional[str] = None,
        valid_until: Optional[str] = None,
        source_url: Optional[str] = None,
        version: str = "1.0",
        status: str = "ACTIVE"
    ) -> Document:
        """
        Parses raw text into a structured Document object with segmented clauses.
        """
        doc_id = document_id or f"DOC-{uuid.uuid4().hex[:8].upper()}"
        clauses = self._segment_clauses(raw_text, doc_id)

        # If regex segmentation yielded no sub-clauses, create a single root clause
        if not clauses and raw_text.strip():
            clauses = [
                Clause(
                    id=f"{doc_id}-CL-1",
                    document_id=doc_id,
                    clause_number="1.0",
                    title="General Provisions",
                    section="General",
                    text=raw_text.strip(),
                    normalized_text=self.normalizer.normalize_text(raw_text),
                    clause_type=self._classify_clause(raw_text),
                    structured_attributes=self._extract_attributes(raw_text)
                )
            ]

        return Document(
            id=doc_id,
            title=title,
            scheme_name=scheme_name,
            ministry=ministry,
            document_type=document_type,
            order_number=order_number,
            publication_date=publication_date,
            effective_date=effective_date,
            valid_until=valid_until,
            source_url=source_url,
            version=version,
            status=status,
            clauses=clauses,
            references=[]
        )

    def _segment_clauses(self, text: str, document_id: str) -> List[Clause]:
        """Segments text into individual clauses using structural numbering."""
        clauses: List[Clause] = []
        matches = list(self.CLAUSE_PATTERN.finditer(text))

        for idx, match in enumerate(matches):
            raw_num = match.group("number").strip()
            content = match.group("content").strip()
            if not content:
                continue

            # Clean clause number
            clause_num = re.sub(r"^Clause\s+", "", raw_num).strip(".:- ")
            clause_id = f"{document_id}-CL-{clause_num.replace('.', '-').replace('(', '').replace(')', '')}"

            # Derive title if first sentence is short
            title = None
            first_line = content.split("\n")[0].strip()
            if len(first_line) < 80 and not first_line.endswith("."):
                title = first_line
                body = "\n".join(content.split("\n")[1:]).strip()
                if body:
                    content = body

            clause_type = self._classify_clause(content)
            structured_attrs = self._extract_attributes(content)

            clause = Clause(
                id=clause_id,
                document_id=document_id,
                clause_number=clause_num,
                title=title or f"Clause {clause_num}",
                section=self._infer_section(clause_type),
                text=content,
                normalized_text=self.normalizer.normalize_text(content),
                clause_type=clause_type,
                structured_attributes=structured_attrs,
                page_number=idx + 1
            )
            clauses.append(clause)

        return clauses

    def _classify_clause(self, text: str) -> ClauseType:
        """Determines regulatory clause category based on explicit keywords."""
        lower = text.lower()
        if any(w in lower for w in ["eligibility", "eligible", "income ceiling", "annual income", "domicile", "parental income", "sc category"]):
            return ClauseType.ELIGIBILITY
        elif any(w in lower for w in ["maintenance allowance", "scholarship amount", "rate of scholarship", "disbursement", "dbt", "tuition fee"]):
            return ClauseType.FINANCIAL
        elif any(w in lower for w in ["deadline", "last date", "cut-off", "cut off", "timeline", "closing date"]):
            return ClauseType.DEADLINE
        elif any(w in lower for w in ["scope", "objective", "applicable to all", "coverage"]):
            return ClauseType.SCOPE
        elif any(w in lower for w in ["renewal", "subsequent year", "promotion", "continuity"]):
            return ClauseType.RENEWAL
        elif any(w in lower for w in ["exemption", "exception", "relaxed"]):
            return ClauseType.EXEMPTION
        elif any(w in lower for w in ["selection", "merit list", "quota", "slot"]):
            return ClauseType.SELECTION_PROCESS
        elif any(w in lower for w in ["nodal officer", "state government", "portal", "monitoring"]):
            return ClauseType.ADMINISTRATIVE
        return ClauseType.GENERAL

    def _infer_section(self, clause_type: ClauseType) -> str:
        """Maps clause type to a readable policy section name."""
        mapping = {
            ClauseType.ELIGIBILITY: "Eligibility Conditions",
            ClauseType.FINANCIAL: "Rates and Value of Scholarship",
            ClauseType.DEADLINE: "Timelines and Deadlines",
            ClauseType.SCOPE: "Scope and Objectives",
            ClauseType.RENEWAL: "Renewal Conditions",
            ClauseType.EXEMPTION: "Exemptions and Relaxations",
            ClauseType.SELECTION_PROCESS: "Selection Procedure",
            ClauseType.ADMINISTRATIVE: "Administrative Architecture",
            ClauseType.GENERAL: "General Provisions",
        }
        return mapping.get(clause_type, "General")

    def _extract_attributes(self, text: str) -> Dict[str, Any]:
        """Extracts structured legal entities like currency ceilings and percentages."""
        attrs: Dict[str, Any] = {}
        
        # Income ceiling extraction
        income_match = re.search(r"(?:income|ceiling).*?(?:₹|rs\.?|inr)\s*([\d,]+(?:\.\d+)?)\s*(?:/-)?\s*(?:per\s+(?:annum|year))?", text, re.IGNORECASE)
        if income_match:
            raw_val = income_match.group(1).replace(",", "")
            try:
                attrs["income_ceiling"] = float(raw_val)
                attrs["unit"] = "per_annum"
            except ValueError:
                pass

        # Percentage or marks extraction
        marks_match = re.search(r"(\d+(?:\.\d+)?)\s*%\s*(?:marks|aggregate)?", text, re.IGNORECASE)
        if marks_match:
            try:
                attrs["marks_threshold"] = float(marks_match.group(1))
            except ValueError:
                pass

        return attrs
