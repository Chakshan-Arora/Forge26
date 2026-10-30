"""
Integration Tests for the LangGraph Agentic Investigation Workflow.

Validates multi-step policy query analysis, document retrieval,
clause identification, change detection, impact analysis, evidence
verification, and structured answer synthesis.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from shared.schemas import AgentQueryRequest
from backend.agent import RegulatoryInvestigationAgent


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_agent_change_investigation(client: TestClient):
    """Verifies complete multi-step agent flow for a policy change query."""
    payload = {
        "query": "What changed in the Post-Matric Scholarship for SC students guidelines?"
    }
    resp = client.post("/api/agent/query", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["session_id"].startswith("SES-")
    assert "Post-Matric Scholarship for SC Students" in data["scheme_name"]
    assert len(data["steps_taken"]) >= 4
    assert len(data["detected_changes"]) >= 4
    assert len(data["evidence_citations"]) > 0
    assert data["verification_confidence"] > 0.7
    assert len(data["direct_answer"]) > 100
    assert len(data["actionable_recommendations"]) > 0


def test_agent_temporal_query(client: TestClient):
    """Verifies agent flow when querying point-in-time regulatory applicability."""
    payload = {
        "query": "What was the applicable eligibility rule on 2019-06-01 for Post-Matric SC students?"
    }
    resp = client.post("/api/agent/query", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["session_id"]
    assert "2019" in data["direct_answer"] or "DOC-MoSJE-PMS-SC-2018" in data["direct_answer"]
    assert len(data["steps_taken"]) >= 3


def test_agent_audit_history(client: TestClient):
    """Verifies that executed agent queries are logged to the database audit table."""
    resp = client.get("/api/agent/history")
    assert resp.status_code == 200
    history = resp.json()
    assert len(history) >= 1
    assert "session_id" in history[0]
    assert "query" in history[0]
