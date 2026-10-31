"""
Conflict and Dependency Detector Module.

Identifies conflicting provisions, partial amendments, missing historical references,
and crucially distinguishes genuine contradictions from distinct cohort/scope rules.
"""

from __future__ import annotations
import re
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple

from shared.schemas import (
    ConflictReport,
    Document,
    Clause,
    EvidenceRecord,
)
from intelligence.evidence_engine import EvidenceEngine


class ConflictDetector:
    """Detects regulatory conflicts, competing amendments, and dependency gaps."""

    def __init__(self, documents: Optional[List[Document]] = None):
        self.documents = documents or []
        self.docs_by_id = {d.id: d for d in self.documents}

    def register_documents(self, documents: List[Document]) -> None:
        """Registers a list of documents for conflict analysis."""
        for d in documents:
            if d.id not in self.docs_by_id:
                self.documents.append(d)
                self.docs_by_id[d.id] = d

    @classmethod
    def _is_distinct_scope(cls, clause_a: Clause, clause_b: Clause) -> Tuple[bool, Optional[str]]:
        """
        Determines whether differing criteria apply to distinct beneficiary cohorts,
        modes of study, or institutional categories rather than a true contradiction.
        """
        t_a = clause_a.text.lower()
        t_b = clause_b.text.lower()

        # Check 1: Hosteller vs Day Scholar
        a_hosteller = "hosteller" in t_a
        b_hosteller = "hosteller" in t_b
        a_day = "day scholar" in t_a
        b_day = "day scholar" in t_b
        if (a_hosteller and b_day) or (a_day and b_hosteller):
            return True, "Distinct allowance modes: One clause governs Hostellers, the other Day Scholars."

        # Check 2: Fresh vs Renewal
        a_fresh = "fresh" in t_a
        b_fresh = "fresh" in t_b
        a_renewal = "renewal" in t_a
        b_renewal = "renewal" in t_b
        if (a_fresh and b_renewal) or (a_renewal and b_fresh):
            return True, "Distinct applicant categories: One applies to Fresh applicants, the other to Renewal candidates."

        # Check 3: Course Groups (e.g. Group 1 Degree/PG vs Group 4 Higher Secondary)
        grp_a = re.search(r"group\s+([1-4]|i{1,3}|iv)", t_a)
        grp_b = re.search(r"group\s+([1-4]|i{1,3}|iv)", t_b)
        if grp_a and grp_b and grp_a.group(1) != grp_b.group(1):
            return True, f"Distinct course groups: Group {grp_a.group(1)} vs Group {grp_b.group(1)}."

        return False, None

    def detect_conflicts_for_scheme(self, scheme_name: str) -> List[ConflictReport]:
        """
        Scans all documents associated with scheme_name for contradictions,
        supersession ambiguities, and missing document dependencies.
        """
        reports: List[ConflictReport] = []
        scheme_docs = [
            d for d in self.documents
            if d.scheme_name.strip().lower() == scheme_name.strip().lower()
        ]

        if len(scheme_docs) < 1:
            return reports

        # 1. Detect Missing Historical Version Dependencies
        for doc in scheme_docs:
            for ref in doc.references:
                target_id = ref.get("target_document_id")
                if target_id and target_id not in self.docs_by_id:
                    reports.append(
                        ConflictReport(
                            conflict_id=f"CONF-DEP-{uuid.uuid4().hex[:8].upper()}",
                            conflict_type="MISSING_HISTORICAL_DEPENDENCY",
                            description=(
                                f"Document '{doc.id}' references predecessor/amended order '{target_id}', "
                                "which is missing from the regulatory repository. Full legal provenance cannot be traced."
                            ),
                            conflicting_clause_ids=[],
                            document_ids=[doc.id, target_id],
                            scheme_name=scheme_name,
                            is_genuine_contradiction=False,
                            distinct_scopes_identified=None,
                            resolution_status="REQUIRES_CLARIFICATION",
                            uncertainties=[f"Missing source file for document reference '{target_id}'."],
                            evidence=[
                                EvidenceEngine.create_evidence(
                                    document_id=doc.id,
                                    exact_supporting_text=f"References missing target {target_id}",
                                    page_or_section="References Metadata",
                                    is_inferred=False
                                )
                            ]
                        )
                    )

        # 2. Check for Partial Amendments
        for doc in scheme_docs:
            if doc.document_type.value in ("AMENDMENT", "NOTIFICATION", "CORRIGENDUM"):
                # If document contains few clauses compared to full scheme guidelines
                if len(doc.clauses) < 5:
                    amended_targets = [
                        ref.get("target_document_id") for ref in doc.references
                        if ref.get("relationship") in ("AMENDS", "MODIFIES")
                    ]
                    reports.append(
                        ConflictReport(
                            conflict_id=f"CONF-PART-{uuid.uuid4().hex[:8].upper()}",
                            conflict_type="PARTIAL_AMENDMENT",
                            description=(
                                f"Notification '{doc.id}' is a partial amendment containing {len(doc.clauses)} clause(s). "
                                f"It selectively updates specific provisions while baseline guidelines ({', '.join(amended_targets) or 'preceding policy'}) remain in force."
                            ),
                            conflicting_clause_ids=[c.id for c in doc.clauses],
                            document_ids=[doc.id] + [t for t in amended_targets if t],
                            scheme_name=scheme_name,
                            is_genuine_contradiction=False,
                            distinct_scopes_identified="Partial amendment modifies only targeted subclauses.",
                            resolution_status="RESOLVED_BY_TEMPORAL_PRECEDENCE",
                            uncertainties=[],
                            evidence=[
                                EvidenceEngine.create_evidence(
                                    document_id=doc.id,
                                    exact_supporting_text=f"Partial amendment order {doc.order_number or doc.id}",
                                    page_or_section="Header",
                                    is_inferred=False
                                )
                            ]
                        )
                    )

        # 3. Pairwise Clause Conflict & Distinct Scope Check across active documents
        # Compare clauses between active documents
        for i in range(len(scheme_docs)):
            for j in range(i + 1, len(scheme_docs)):
                doc_a = scheme_docs[i]
                doc_b = scheme_docs[j]
                
                # Check for clause clashes within the same clause type (e.g. ELIGIBILITY)
                for cl_a in doc_a.clauses:
                    for cl_b in doc_b.clauses:
                        if cl_a.clause_type == cl_b.clause_type and cl_a.clause_type.value == "ELIGIBILITY":
                            # Check if both define income limits or thresholds with differing values
                            val_a = cl_a.structured_attributes.get("numeric_amount")
                            val_b = cl_b.structured_attributes.get("numeric_amount")
                            
                            if val_a is not None and val_b is not None and val_a != val_b:
                                is_distinct, scope_reason = self._is_distinct_scope(cl_a, cl_b)
                                
                                if is_distinct:
                                    reports.append(
                                        ConflictReport(
                                            conflict_id=f"CONF-SCOPE-{uuid.uuid4().hex[:8].upper()}",
                                            conflict_type="DISTINCT_COHORTS_DISAMBIGUATION",
                                            description=f"Apparent numeric variation between clause {cl_a.id} ({val_a}) and {cl_b.id} ({val_b}) is disambiguated by distinct scopes: {scope_reason}",
                                            conflicting_clause_ids=[cl_a.id, cl_b.id],
                                            document_ids=[doc_a.id, doc_b.id],
                                            scheme_name=scheme_name,
                                            is_genuine_contradiction=False,
                                            distinct_scopes_identified=scope_reason,
                                            resolution_status="RESOLVED_BY_SPECIALITY",
                                            uncertainties=[],
                                            evidence=[
                                                EvidenceEngine.from_clause(cl_a, doc_a),
                                                EvidenceEngine.from_clause(cl_b, doc_b)
                                            ]
                                        )
                                    )
                                else:
                                    # True legal contradiction or temporal supersession question
                                    # Check if one document chronologically succeeds and supersedes the other
                                    eff_a = doc_a.effective_date or doc_a.publication_date
                                    eff_b = doc_b.effective_date or doc_b.publication_date
                                    
                                    resolution = "UNRESOLVED"
                                    is_genuine = True
                                    uncertainty_msg = "Clauses stipulate incompatible criteria for the same domain."
                                    
                                    if eff_a and eff_b and eff_a != eff_b:
                                        resolution = "RESOLVED_BY_TEMPORAL_PRECEDENCE"
                                        is_genuine = False
                                        uncertainty_msg = f"Later document ({doc_b.id if eff_b > eff_a else doc_a.id}) takes precedence over earlier order."

                                    reports.append(
                                        ConflictReport(
                                            conflict_id=f"CONF-CONTRA-{uuid.uuid4().hex[:8].upper()}",
                                            conflict_type="DIRECT_CONTRADICTION" if is_genuine else "POTENTIAL_SUPERSEDED",
                                            description=f"Differing eligibility limits ({val_a} vs {val_b}) between {cl_a.id} and {cl_b.id}.",
                                            conflicting_clause_ids=[cl_a.id, cl_b.id],
                                            document_ids=[doc_a.id, doc_b.id],
                                            scheme_name=scheme_name,
                                            is_genuine_contradiction=is_genuine,
                                            distinct_scopes_identified=None,
                                            resolution_status=resolution,
                                            uncertainties=[uncertainty_msg],
                                            evidence=[
                                                EvidenceEngine.from_clause(cl_a, doc_a),
                                                EvidenceEngine.from_clause(cl_b, doc_b)
                                            ]
                                        )
                                    )

        return reports
