"""
Temporal Resolver Module.

Performs point-in-time regulatory applicability resolution, distinguishing
publication date, effective date, validity periods, pending amendments, and supersessions.
"""

from __future__ import annotations
import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple
from dateutil import parser as date_parser

from shared.schemas import (
    Document,
    Clause,
    TemporalApplicabilityResult,
    EvidenceRecord,
)
from intelligence.knowledge_graph import BaseRegulatoryGraph, NetworkXRegulatoryGraph
from intelligence.evidence_engine import EvidenceEngine


class TemporalResolver:
    """Resolves point-in-time regulatory applicability and tracks regulatory lineage."""

    def __init__(self, graph: Optional[BaseRegulatoryGraph] = None):
        self.graph = graph or NetworkXRegulatoryGraph()
        self.documents_by_id: Dict[str, Document] = {}

    def register_document(self, document: Document) -> None:
        """Registers document in resolver repository and ingests into knowledge graph."""
        self.documents_by_id[document.id] = document
        if isinstance(self.graph, NetworkXRegulatoryGraph):
            self.graph.ingest_document(document)

    @classmethod
    def parse_iso_or_fuzzy_date(cls, date_str: Optional[str]) -> Optional[date]:
        """Parses date string or financial year into a Python date."""
        if not date_str:
            return None
            
        clean = date_str.strip()
        
        # Check standard ISO YYYY-MM-DD first to prevent dayfirst ambiguity
        if re.match(r"^\d{4}-\d{2}-\d{2}$", clean):
            try:
                return date.fromisoformat(clean)
            except ValueError:
                pass

        # Check financial year pattern e.g. "2020-21" or "2025-26"
        fy_match = re.match(r"^(\d{4})-(\d{2})$", clean)
        if fy_match:
            start_year = int(fy_match.group(1))
            # Start of Indian financial year is 1st April
            return date(start_year, 4, 1)

        if re.match(r'^\d{4}-\d{2}-\d{2}$', clean):
            try:
                return date.fromisoformat(clean)
            except ValueError:
                pass

        try:
            dt = date_parser.parse(clean, dayfirst=True)
            return dt.date()
        except Exception:
            return None

    @classmethod
    def parse_validity_end_date(cls, valid_until_str: Optional[str]) -> Optional[date]:
        """Parses expiry date or end of financial year."""
        if not valid_until_str:
            return None
            
        clean = valid_until_str.strip()

        # Check standard ISO YYYY-MM-DD first
        if re.match(r"^\d{4}-\d{2}-\d{2}$", clean):
            try:
                return date.fromisoformat(clean)
            except ValueError:
                pass

        fy_match = re.match(r"^(\d{4})-(\d{2})$", clean)
        if fy_match:
            end_short = int(fy_match.group(2))
            century = int(clean[:2]) * 100
            end_year = century + end_short
            # End of Indian financial year is 31st March
            return date(end_year, 3, 31)

        try:
            dt = date_parser.parse(clean, dayfirst=True)
            return dt.date()
        except Exception:
            return None

    def resolve_applicability_at_date(
        self,
        scheme_name: str,
        query_date_str: str
    ) -> TemporalApplicabilityResult:
        """
        Determines the exact regulatory provisions applicable to a scheme on a given query date.
        Distinguishes publication date vs effective date vs validity period.
        """
        target_date = self.parse_iso_or_fuzzy_date(query_date_str)
        if not target_date:
            return TemporalApplicabilityResult(
                query_date=query_date_str,
                scheme_name=scheme_name,
                status="UNRESOLVED",
                unresolved_reasons=[f"Invalid date format: '{query_date_str}'"]
            )

        # Retrieve documents matching scheme
        scheme_docs = [
            doc for doc in self.documents_by_id.values()
            if doc.scheme_name.strip().lower() == scheme_name.strip().lower()
        ]

        if not scheme_docs:
            return TemporalApplicabilityResult(
                query_date=query_date_str,
                scheme_name=scheme_name,
                status="UNRESOLVED",
                unresolved_reasons=[f"No registered documents found for scheme '{scheme_name}'"]
            )

        applicable_docs: List[Document] = []
        superseded_docs: List[Document] = []
        pending_amendments: List[Dict[str, Any]] = []
        unresolved_reasons: List[str] = []
        evidence_trail: List[EvidenceRecord] = []

        # Analyze each document's timeline relative to target_date
        for doc in scheme_docs:
            pub_date = self.parse_iso_or_fuzzy_date(doc.publication_date)
            eff_date = self.parse_iso_or_fuzzy_date(doc.effective_date)
            valid_end = self.parse_validity_end_date(doc.valid_until)

            # Check if effective date is explicitly known
            if eff_date is None:
                if pub_date is not None:
                    # Caution: Do not blindly assume pub_date == eff_date
                    unresolved_reasons.append(
                        f"Document '{doc.id}' has publication date {doc.publication_date} but no explicit effective date. Applicability cannot be legally guaranteed."
                    )
                else:
                    unresolved_reasons.append(
                        f"Document '{doc.id}' has neither publication date nor effective date recorded."
                    )
                continue

            # Case 1: Published / Notified, but effective date is in the future
            if eff_date > target_date:
                if pub_date and pub_date <= target_date:
                    pending_amendments.append({
                        "document_id": doc.id,
                        "title": doc.title,
                        "publication_date": doc.publication_date,
                        "effective_date": doc.effective_date,
                        "status": "NOTIFIED_PENDING_ENFORCEMENT",
                        "notes": f"Published on {doc.publication_date}, but only takes legal effect on {doc.effective_date}."
                    })
                continue

            # Case 2: In the past, check if expired by validity end date
            if valid_end and target_date > valid_end:
                superseded_docs.append(doc)
                continue

            # Document is in force on query date
            applicable_docs.append(doc)
            evidence_trail.append(
                EvidenceEngine.create_evidence(
                    document_id=doc.id,
                    exact_supporting_text=f"Document '{doc.title}' in effect from {doc.effective_date}" + (f" until {doc.valid_until}" if doc.valid_until else ""),
                    page_or_section="Document Metadata",
                    is_inferred=False,
                    confidence=0.95
                )
            )

        # Check supersession among active documents
        # A newer active document with explicit SUPERSEDES relationship supersedes older docs
        final_applicable_docs: List[Document] = []
        superseded_clause_info: List[Dict[str, Any]] = []

        for doc in applicable_docs:
            # Check if any other doc in applicable_docs supersedes this doc
            is_superseded = False
            for other_doc in applicable_docs:
                for ref in other_doc.references:
                    if (
                        ref.get("target_document_id") == doc.id and
                        ref.get("relationship") in ("SUPERSEDES", "REPLACES")
                    ):
                        is_superseded = True
                        superseded_clause_info.append({
                            "document_id": doc.id,
                            "superseded_by": other_doc.id,
                            "relationship": ref.get("relationship"),
                            "effective_date": other_doc.effective_date
                        })
                        break
                if is_superseded:
                    break

            if not is_superseded:
                final_applicable_docs.append(doc)
            else:
                superseded_docs.append(doc)

        # Collect applicable clauses
        applicable_clauses: List[Clause] = []
        for doc in final_applicable_docs:
            applicable_clauses.extend(doc.clauses)

        # Determine overall status
        status = "RESOLVED"
        if unresolved_reasons and not final_applicable_docs:
            status = "UNRESOLVED"
        elif unresolved_reasons and final_applicable_docs:
            status = "PARTIALLY_RESOLVED"

        return TemporalApplicabilityResult(
            query_date=query_date_str,
            scheme_name=scheme_name,
            status=status,
            applicable_document_ids=[d.id for d in final_applicable_docs],
            applicable_clauses=applicable_clauses,
            superseded_clauses=superseded_clause_info,
            active_amendments=pending_amendments,
            unresolved_reasons=unresolved_reasons,
            evidence=evidence_trail
        )

    def trace_condition_origin(
        self,
        scheme_name: str,
        condition_keyword: str
    ) -> List[Dict[str, Any]]:
        """
        Traces the historical introduction and amendments of a specific condition
        (e.g., 'income_ceiling', 'maintenance_allowance', 'attendance').
        Answers: 'Which notification introduced this particular condition?'
        """
        history: List[Dict[str, Any]] = []
        
        # Sort documents by effective date or publication date
        scheme_docs = [
            doc for doc in self.documents_by_id.values()
            if doc.scheme_name.strip().lower() == scheme_name.strip().lower()
        ]
        
        scheme_docs.sort(
            key=lambda d: self.parse_iso_or_fuzzy_date(d.effective_date or d.publication_date) or date.min
        )

        for doc in scheme_docs:
            for clause in doc.clauses:
                # Check text or structured attributes
                text_match = condition_keyword.lower() in clause.text.lower()
                attr_match = any(condition_keyword.lower() in str(k).lower() or condition_keyword.lower() in str(v).lower() for k, v in clause.structured_attributes.items())
                
                if text_match or attr_match:
                    history.append({
                        "document_id": doc.id,
                        "document_title": doc.title,
                        "order_number": doc.order_number,
                        "clause_id": clause.id,
                        "clause_number": clause.clause_number,
                        "effective_date": doc.effective_date,
                        "publication_date": doc.publication_date,
                        "clause_text": clause.text,
                        "structured_attributes": clause.structured_attributes
                    })

        return history
