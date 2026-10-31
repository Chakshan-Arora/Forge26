"""
Agentic Regulatory Workflow Orchestrator for Policy Intel.

Implements a stateful, multi-step regulatory investigation graph using LangGraph:
STEP 1: Understand user's regulatory query
STEP 2: Identify relevant scheme, target date, and applicant group
STEP 3: Retrieve relevant documents and version lineages
STEP 4: Identify applicable clauses
STEP 5: Invoke regulatory comparison engine when historical revisions are detected
STEP 6: Invoke impact analysis engine to determine affected student groups
STEP 7: Retrieve and bind verbatim supporting evidence
STEP 8: Validate evidence sufficiency and compute verification confidence
STEP 9: Identify unresolved questions, temporal ambiguities, or statutory conflicts
STEP 10: Synthesize structured, authoritative response with explicit reasoning distinctions
"""

from __future__ import annotations
import logging
import re
import uuid
from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, END

from shared.schemas import (
    Document,
    Clause,
    ChangeRecord,
    ImpactAnalysisReport,
    ConflictReport,
    TemporalApplicabilityResult,
    EvidenceRecord,
    AffectedGroup,
    AgentInvestigationStep,
    AgentQueryRequest,
    AgentQueryResponse,
)
from shared.constants import (
    SCHEME_PMS_SC,
    SCHEME_NMMSS,
    SCHEME_PM_USP_CSSS,
    REASONING_FACTUAL,
    REASONING_DETERMINISTIC,
    REASONING_INFERRED,
    REASONING_UNRESOLVED,
)
from backend.services.intelligence_service import IntelligenceService
from backend.services.evidence_service import EvidenceService

logger = logging.getLogger(__name__)


class RegulatoryAgentState(TypedDict, total=False):
    """Complete workflow state across all investigation nodes."""
    session_id: str
    query: str
    scheme_name: Optional[str]
    target_date: Optional[str]
    beneficiary_group: Optional[str]
    query_intent: str
    identified_documents: List[Document]
    identified_clauses: List[Clause]
    comparison_changes: List[ChangeRecord]
    impact_report: Optional[ImpactAnalysisReport]
    temporal_result: Optional[TemporalApplicabilityResult]
    conflict_reports: List[ConflictReport]
    evidence_citations: List[EvidenceRecord]
    verification_confidence: float
    uncertainties: List[str]
    actionable_recommendations: List[str]
    direct_answer: str
    reasoning_type: str
    steps_taken: List[AgentInvestigationStep]
    error: Optional[str]


class RegulatoryInvestigationAgent:
    """
    Stateful multi-node LangGraph orchestrator for regulatory policy investigations.
    """

    def __init__(self, intel_service: Optional[IntelligenceService] = None):
        self.intel_service = intel_service or IntelligenceService.get_instance()
        self.workflow = self._build_graph()

    def _build_graph(self):
        """Constructs the LangGraph state machine with conditional routing."""
        workflow = StateGraph(RegulatoryAgentState)

        # Register nodes
        workflow.add_node("understand_query", self._node_understand_query)
        workflow.add_node("retrieve_documents_and_clauses", self._node_retrieve_documents_and_clauses)
        workflow.add_node("execute_comparison_and_impact", self._node_execute_comparison_and_impact)
        workflow.add_node("resolve_temporal_validity", self._node_resolve_temporal_validity)
        workflow.add_node("detect_regulatory_conflicts", self._node_detect_regulatory_conflicts)
        workflow.add_node("validate_evidence", self._node_validate_evidence)
        workflow.add_node("synthesize_response", self._node_synthesize_response)

        # Set entry point
        workflow.set_entry_point("understand_query")

        # Step 1-2 -> Step 3-4
        workflow.add_edge("understand_query", "retrieve_documents_and_clauses")

        # Conditional routing after retrieval based on query intent
        workflow.add_conditional_edges(
            "retrieve_documents_and_clauses",
            self._route_investigation_path,
            {
                "compare_impact": "execute_comparison_and_impact",
                "temporal": "resolve_temporal_validity",
                "conflict": "detect_regulatory_conflicts",
                "direct_validate": "validate_evidence",
            }
        )

        # Branch targets rejoin at evidence validation
        workflow.add_edge("execute_comparison_and_impact", "validate_evidence")
        workflow.add_edge("resolve_temporal_validity", "validate_evidence")
        workflow.add_edge("detect_regulatory_conflicts", "validate_evidence")

        # Step 8-9 -> Step 10 (Final synthesis) -> END
        workflow.add_edge("validate_evidence", "synthesize_response")
        workflow.add_edge("synthesize_response", END)

        return workflow.compile()

    # -------------------------------------------------------------
    # ROUTING LOGIC
    # -------------------------------------------------------------
    def _route_investigation_path(self, state: RegulatoryAgentState) -> str:
        intent = state.get("query_intent", "CHANGE_INVESTIGATION")
        if intent == "TEMPORAL_VALIDITY":
            return "temporal"
        elif intent == "CONFLICT_CHECK":
            return "conflict"
        elif intent in ("CHANGE_INVESTIGATION", "IMPACT_ANALYSIS"):
            return "compare_impact"
        return "direct_validate"

    # -------------------------------------------------------------
    # WORKFLOW NODES
    # -------------------------------------------------------------
    def _node_understand_query(self, state: RegulatoryAgentState) -> Dict[str, Any]:
        """STEP 1 & 2: Understand query intent, scheme, date, and group."""
        query = state.get("query", "")
        steps: List[AgentInvestigationStep] = list(state.get("steps_taken", []))

        # Detect scheme if not specified
        detected_scheme = state.get("scheme_name")
        q_lower = query.lower()
        if not detected_scheme:
            if any(k in q_lower for k in ["pms-sc", "post-matric", "post matric", "sc student", "scheduled caste"]):
                detected_scheme = SCHEME_PMS_SC
            elif any(k in q_lower for k in ["nmmss", "means-cum-merit", "means cum merit", "class 8", "class 9"]):
                detected_scheme = SCHEME_NMMSS
            elif any(k in q_lower for k in ["pm-usp", "csss", "college and university", "central sector"]):
                detected_scheme = SCHEME_PM_USP_CSSS
            else:
                detected_scheme = SCHEME_PMS_SC  # Default to flagship SC scheme

        # Detect date
        detected_date = state.get("target_date")
        if not detected_date:
            date_match = re.search(r"\b(20\d\d(?:-\d\d-\d\d)?)\b", query)
            if date_match:
                val = date_match.group(1)
                detected_date = val if "-" in val else f"{val}-04-01"

        # Detect intent
        if detected_date and any(w in q_lower for w in ["applicable", "valid", "rule", "was", "eligibility on", "in 20", "on 20"]):
            intent = "TEMPORAL_VALIDITY"
        elif any(w in q_lower for w in ["what changed", "difference", "modify", "modified", "revision", "new rules", "change", "amendment"]):
            intent = "CHANGE_INVESTIGATION"
        elif any(w in q_lower for w in ["conflict", "contradiction", "supersede", "dispute", "clash"]):
            intent = "CONFLICT_CHECK"
        elif any(w in q_lower for w in ["who is affected", "impact", "ineligible", "newly eligible", "excluded"]):
            intent = "IMPACT_ANALYSIS"
        elif detected_date:
            intent = "TEMPORAL_VALIDITY"
        else:
            intent = "CHANGE_INVESTIGATION"

        # Detect demographic / economic group
        group = state.get("beneficiary_group")
        if not group:
            if "hosteller" in q_lower:
                group = "Hosteller Students"
            elif "day scholar" in q_lower:
                group = "Day Scholar Students"
            elif "income" in q_lower or "2.5" in q_lower or "3.5" in q_lower:
                group = "Marginal Income Cohort (INR 2.5L - 3.5L)"
            elif "female" in q_lower or "girl" in q_lower:
                group = "Female Applicants"

        steps.append(
            AgentInvestigationStep(
                step_number=1,
                step_name="Query Analysis & Classification",
                description=f"Identified query intent as '{intent}' and targeted scheme '{detected_scheme}'.",
                tool_invoked="IntentClassifier",
                details={"intent": intent, "scheme": detected_scheme, "date": detected_date, "group": group}
            )
        )

        return {
            "scheme_name": detected_scheme,
            "target_date": detected_date,
            "beneficiary_group": group,
            "query_intent": intent,
            "steps_taken": steps,
        }

    def _node_retrieve_documents_and_clauses(self, state: RegulatoryAgentState) -> Dict[str, Any]:
        """STEP 3 & 4: Retrieve relevant documents and applicable clauses."""
        self.intel_service.initialize()
        scheme_name = state.get("scheme_name", SCHEME_PMS_SC)
        steps: List[AgentInvestigationStep] = list(state.get("steps_taken", []))

        # Retrieve documents matching scheme
        all_docs = self.intel_service.engine.list_documents()
        matched_docs = [
            d for d in all_docs
            if scheme_name.lower() in d.scheme_name.lower() or d.scheme_name.lower() in scheme_name.lower()
        ]
        # Sort chronologically by publication/effective date
        matched_docs.sort(key=lambda d: d.publication_date or d.effective_date or "")

        # Extract clauses across these documents
        clauses: List[Clause] = []
        for d in matched_docs:
            clauses.extend(d.clauses)

        steps.append(
            AgentInvestigationStep(
                step_number=2,
                step_name="Regulatory Document & Clause Retrieval",
                description=f"Retrieved {len(matched_docs)} official policy documents and {len(clauses)} structured clauses for {scheme_name}.",
                tool_invoked="CorpusRetriever",
                details={
                    "document_ids": [d.id for d in matched_docs],
                    "clause_count": len(clauses),
                }
            )
        )

        return {
            "identified_documents": matched_docs,
            "identified_clauses": clauses,
            "steps_taken": steps,
        }

    def _node_execute_comparison_and_impact(self, state: RegulatoryAgentState) -> Dict[str, Any]:
        """STEP 5 & 6: Regulatory comparison and impact analysis."""
        steps: List[AgentInvestigationStep] = list(state.get("steps_taken", []))
        docs = state.get("identified_documents", [])
        scheme_name = state.get("scheme_name", SCHEME_PMS_SC)

        if len(docs) < 2:
            return {"comparison_changes": [], "uncertainties": ["Only one policy revision found in repository for this scheme."]}

        # Compare oldest baseline to newest target
        base_doc = docs[0]
        target_doc = docs[-1]

        changes, summary = self.intel_service.compare_documents(
            base_document_id=base_doc.id,
            target_document_id=target_doc.id
        )

        impact_report = self.intel_service.analyze_impact(
            base_document_id=base_doc.id,
            target_document_id=target_doc.id
        )

        steps.append(
            AgentInvestigationStep(
                step_number=3,
                step_name="Regulatory Comparison & Impact Analysis",
                description=f"Detected {len(changes)} clause-level modifications between {base_doc.version} and {target_doc.version}. Evaluated affected student groups.",
                tool_invoked="PolicyIntelEngine.compare_documents & analyze_impact",
                details={
                    "base_doc": base_doc.id,
                    "target_doc": target_doc.id,
                    "changes_detected": len(changes),
                    "affected_groups": len(impact_report.explicitly_affected_groups) + len(impact_report.potentially_affected_groups),
                }
            )
        )

        return {
            "comparison_changes": changes,
            "impact_report": impact_report,
            "steps_taken": steps,
        }

    def _node_resolve_temporal_validity(self, state: RegulatoryAgentState) -> Dict[str, Any]:
        """STEP 5 (Alternative): Point-in-time regulatory applicability query."""
        steps: List[AgentInvestigationStep] = list(state.get("steps_taken", []))
        scheme_name = state.get("scheme_name", SCHEME_PMS_SC)
        target_date = state.get("target_date", "2020-01-01")

        result = self.intel_service.query_temporal_applicability(scheme_name, target_date)

        steps.append(
            AgentInvestigationStep(
                step_number=3,
                step_name="Point-in-Time Temporal Resolution",
                description=f"Resolved active regulatory provisions for {scheme_name} on date {target_date}.",
                tool_invoked="TemporalResolver.resolve_applicability_at_date",
                details={
                    "query_date": target_date,
                    "applicable_docs": result.applicable_document_ids,
                    "applicable_clauses": len(result.applicable_clauses),
                }
            )
        )

        return {
            "temporal_result": result,
            "steps_taken": steps,
        }

    def _node_detect_regulatory_conflicts(self, state: RegulatoryAgentState) -> Dict[str, Any]:
        """STEP 5 (Alternative): Conflict and ambiguity detection."""
        steps: List[AgentInvestigationStep] = list(state.get("steps_taken", []))
        scheme_name = state.get("scheme_name", SCHEME_PMS_SC)

        conflicts = self.intel_service.detect_conflicts(scheme_name)

        steps.append(
            AgentInvestigationStep(
                step_number=3,
                step_name="Regulatory Conflict & Gap Detection",
                description=f"Audited scheme regulations for contradictions or scope overlaps. Found {len(conflicts)} potential issues.",
                tool_invoked="ConflictDetector.detect_conflicts_for_scheme",
                details={"conflict_count": len(conflicts)}
            )
        )

        return {
            "conflict_reports": conflicts,
            "steps_taken": steps,
        }

    def _node_validate_evidence(self, state: RegulatoryAgentState) -> Dict[str, Any]:
        """STEP 7, 8, & 9: Aggregate and validate supporting evidence, assess uncertainties."""
        steps: List[AgentInvestigationStep] = list(state.get("steps_taken", []))
        citations: List[EvidenceRecord] = []
        uncertainties: List[str] = list(state.get("uncertainties", []))

        # Collect evidence from comparison changes
        changes = state.get("comparison_changes", [])
        for chg in changes:
            citations.extend(chg.evidence)
            uncertainties.extend(chg.uncertainties)

        # Collect evidence from impact report
        impact_report = state.get("impact_report")
        if impact_report:
            citations.extend(impact_report.evidence_trail)
            for g in impact_report.unresolved_groups:
                uncertainties.append(f"Unresolved interpretation for {g.group_name}: {g.details}")

        # Collect evidence from temporal result
        temporal_res = state.get("temporal_result")
        if temporal_res:
            citations.extend(temporal_res.evidence)
            uncertainties.extend(temporal_res.unresolved_reasons)

        # Collect evidence from conflicts
        for conf in state.get("conflict_reports", []):
            citations.extend(conf.evidence)
            uncertainties.extend(conf.uncertainties)

        # Deduplicate citations
        unique_citations: List[EvidenceRecord] = []
        seen_keys = set()
        for ev in citations:
            key = (ev.document_id, ev.clause_id, ev.exact_supporting_text)
            if key not in seen_keys:
                seen_keys.add(key)
                unique_citations.append(ev)

        # Deduplicate uncertainties
        unique_uncertainties = list(dict.fromkeys(uncertainties))

        # Compute aggregate confidence
        confidence = EvidenceService.calculate_aggregate_confidence(unique_citations)

        steps.append(
            AgentInvestigationStep(
                step_number=4,
                step_name="Evidence Sufficiency & Caveat Verification",
                description=f"Compiled {len(unique_citations)} verbatim citations. Calculated verification confidence: {confidence * 100:.1f}%.",
                tool_invoked="EvidenceEngine.verify_sufficiency",
                details={
                    "evidence_count": len(unique_citations),
                    "confidence": confidence,
                    "uncertainty_count": len(unique_uncertainties),
                }
            )
        )

        return {
            "evidence_citations": unique_citations,
            "verification_confidence": confidence,
            "uncertainties": unique_uncertainties,
            "steps_taken": steps,
        }

    def _node_synthesize_response(self, state: RegulatoryAgentState) -> Dict[str, Any]:
        """STEP 10: Formulate structured authoritative response with explicit reasoning."""
        steps: List[AgentInvestigationStep] = list(state.get("steps_taken", []))
        query = state.get("query", "")
        scheme_name = state.get("scheme_name", SCHEME_PMS_SC)
        intent = state.get("query_intent", "CHANGE_INVESTIGATION")
        changes = state.get("comparison_changes", [])
        impact_report = state.get("impact_report")
        temporal_res = state.get("temporal_result")
        conflicts = state.get("conflict_reports", [])
        evidence_list = state.get("evidence_citations", [])
        uncertainties = state.get("uncertainties", [])

        # Formulate answer based on investigation results
        paragraphs: List[str] = []
        recommendations: List[str] = []
        reasoning_type = REASONING_FACTUAL

        if temporal_res:
            paragraphs.append(
                f"**Temporal Applicability on {temporal_res.query_date}:**\n"
                f"For {scheme_name}, the regulatory regime active on {temporal_res.query_date} was governed by document(s): "
                f"{', '.join(temporal_res.applicable_document_ids) or 'No active policy found'}."
            )
            if temporal_res.applicable_clauses:
                paragraphs.append(
                    f"A total of {len(temporal_res.applicable_clauses)} clauses were enforceable at this point in time."
                )
            recommendations.append(f"Verify applicant eligibility against the active provisions in {', '.join(temporal_res.applicable_document_ids)}.")

        elif changes:
            reasoning_type = REASONING_DETERMINISTIC
            paragraphs.append(
                f"**Regulatory Change Intelligence for {scheme_name}:**\n"
                f"A systematic clause-level comparison revealed {len(changes)} substantive modification(s) across official revisions."
            )
            for chg in changes[:4]:
                if chg.previous_text and chg.current_text:
                    paragraphs.append(
                        f"- **Clause {chg.clause_id} ({chg.change_type.value}):** Modified from '{chg.previous_text[:90]}...' to '{chg.current_text[:90]}...'."
                    )
                elif chg.current_text:
                    paragraphs.append(
                        f"- **Clause {chg.clause_id} ({chg.change_type.value}):** Added provision: '{chg.current_text[:120]}...'."
                    )

            if impact_report:
                paragraphs.append(f"\n**Impact Summary:** {impact_report.summary}")
                recommendations.extend(impact_report.practical_consequences[:3])
            else:
                recommendations.append("Ensure student renewal applications adhere to the updated clause thresholds on the National Scholarship Portal.")

        elif conflicts:
            reasoning_type = REASONING_UNRESOLVED
            paragraphs.append(
                f"**Regulatory Conflict Audit for {scheme_name}:**\n"
                f"The system detected {len(conflicts)} potential conflict(s) or ambiguities across published notifications."
            )
            for c in conflicts:
                paragraphs.append(f"- **{c.conflict_type}:** {c.description}")
            recommendations.append("Seek official clarification from the Department/Nodal Agency regarding overlapping dates.")

        else:
            paragraphs.append(
                f"**Policy Query Response for {scheme_name}:**\n"
                f"Retrieved official documents and clauses governing {scheme_name}. All clauses are actively registered in the regulatory graph."
            )
            recommendations.append("Consult the official portal guidelines for the active academic cycle.")

        if uncertainties:
            reasoning_type = REASONING_UNRESOLVED

        direct_answer = "\n\n".join(paragraphs)

        steps.append(
            AgentInvestigationStep(
                step_number=5,
                step_name="Structured Synthesis & Recommendation Formulation",
                description="Synthesized evidence-backed answer with explicit distinction of deterministic calculations and caveats.",
                tool_invoked="ResponseSynthesizer",
                details={"reasoning_type": reasoning_type, "recommendations_count": len(recommendations)}
            )
        )

        return {
            "direct_answer": direct_answer,
            "reasoning_type": reasoning_type,
            "actionable_recommendations": recommendations,
            "steps_taken": steps,
        }

    # -------------------------------------------------------------
    # PUBLIC EXECUTION INTERFACE
    # -------------------------------------------------------------
    def investigate(self, req: AgentQueryRequest) -> AgentQueryResponse:
        """Executes the full LangGraph investigation workflow."""
        session_id = req.session_id or f"SES-{uuid.uuid4().hex[:8].upper()}"
        initial_state: RegulatoryAgentState = {
            "session_id": session_id,
            "query": req.query,
            "scheme_name": req.scheme_name,
            "target_date": req.target_date,
            "beneficiary_group": req.beneficiary_group,
            "steps_taken": [],
            "uncertainties": [],
            "comparison_changes": [],
            "evidence_citations": [],
            "conflict_reports": [],
        }

        final_state = self.workflow.invoke(initial_state)

        # Format source documents
        identified_docs = final_state.get("identified_documents", [])
        src_docs = [
            {
                "id": d.id,
                "title": d.title,
                "scheme_name": d.scheme_name,
                "version": d.version,
                "source_url": d.source_url,
                "publication_date": d.publication_date,
            }
            for d in identified_docs
        ]

        impact_rep = final_state.get("impact_report")
        affected_groups: List[AffectedGroup] = []
        impact_summary = None
        if impact_rep:
            impact_summary = impact_rep.summary
            affected_groups = impact_rep.explicitly_affected_groups + impact_rep.potentially_affected_groups

        return AgentQueryResponse(
            session_id=session_id,
            query=req.query,
            scheme_name=final_state.get("scheme_name"),
            direct_answer=final_state.get("direct_answer", "Investigation complete."),
            reasoning_type=final_state.get("reasoning_type", REASONING_FACTUAL),
            steps_taken=final_state.get("steps_taken", []),
            detected_changes=final_state.get("comparison_changes", []),
            impact_summary=impact_summary,
            affected_groups=affected_groups,
            evidence_citations=final_state.get("evidence_citations", []),
            verification_confidence=final_state.get("verification_confidence", 1.0),
            uncertainties=final_state.get("uncertainties", []),
            actionable_recommendations=final_state.get("actionable_recommendations", []),
            source_documents=src_docs,
        )
