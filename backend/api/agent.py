"""
AI Agentic Investigation API Endpoints.

Coordinates multi-step regulatory investigations across schemes,
historical comparisons, point-in-time applicability, and evidence trails.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from shared.schemas import AgentQueryRequest, AgentQueryResponse
from backend.agent import RegulatoryInvestigationAgent
from backend.services.persistence_service import save_agent_audit_log
from backend.models import AgentAuditLogModel

router = APIRouter(prefix="/agent", tags=["AI Agent Investigation"])


@router.post("/query", response_model=AgentQueryResponse)
def query_agent(
    payload: AgentQueryRequest,
    db: Session = Depends(get_db)
):
    """
    Submits a policy question to the LangGraph-powered regulatory investigation agent.
    Returns structured, evidence-backed answers with explicit reasoning indicators.
    """
    try:
        agent = RegulatoryInvestigationAgent()
        response = agent.investigate(payload)

        # Audit log to DB
        steps_dicts = [s.model_dump() for s in response.steps_taken]
        save_agent_audit_log(
            db=db,
            session_id=response.session_id,
            query=payload.query,
            direct_answer=response.direct_answer,
            reasoning_type=response.reasoning_type,
            steps_taken=steps_dicts,
            scheme_name=response.scheme_name
        )

        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent investigation failed: {str(e)}"
        )


@router.get("/history")
def get_agent_history(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Retrieves previous agent investigation sessions and execution audits."""
    logs = db.query(AgentAuditLogModel).order_by(AgentAuditLogModel.created_at.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "session_id": l.session_id,
            "query": l.query,
            "scheme_name": l.scheme_name,
            "direct_answer": l.direct_answer,
            "reasoning_type": l.reasoning_type,
            "step_count": len(l.steps_taken or []),
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]
