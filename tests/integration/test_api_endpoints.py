"""
Integration Tests for Policy Intel REST API Endpoints.

Validates Documents, Policies, Changes, Impact, Graph, and Health endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db
from backend.services.intelligence_service import IntelligenceService


@pytest.fixture(scope="module")
def client():
    """Provides a TestClient within the application lifespan context."""
    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client: TestClient):
    """GET /api/health returns 200 with connected DB and registered documents."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["registered_documents"] >= 6


def test_system_stats(client: TestClient):
    """GET /api/stats returns accurate metrics across documents and KG."""
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_documents"] >= 6
    assert data["total_schemes"] >= 3
    assert data["knowledge_graph_nodes"] > 0
    assert data["knowledge_graph_edges"] > 0


def test_get_documents_and_filtering(client: TestClient):
    """GET /api/documents returns all documents and supports scheme filtering."""
    resp = client.get("/api/documents")
    assert resp.status_code == 200
    docs = resp.json()
    assert len(docs) >= 6

    # Test filtering by scheme
    resp_filtered = client.get("/api/documents?scheme_name=Post-Matric")
    assert resp_filtered.status_code == 200
    filtered_docs = resp_filtered.json()
    assert len(filtered_docs) >= 2
    for d in filtered_docs:
        assert "post-matric" in d["scheme_name"].lower()


def test_get_document_by_id(client: TestClient):
    """GET /api/documents/{document_id} returns single document with full clauses."""
    doc_id = "DOC-MoSJE-PMS-SC-2020"
    resp = client.get(f"/api/documents/{doc_id}")
    assert resp.status_code == 200
    doc = resp.json()
    assert doc["id"] == doc_id
    assert len(doc["clauses"]) >= 7
    assert doc["scheme_name"] == "Post-Matric Scholarship for SC Students"


def test_get_policies_and_history(client: TestClient):
    """GET /api/policies returns schemes, and /api/policies/{scheme}/history returns version timeline."""
    resp = client.get("/api/policies")
    assert resp.status_code == 200
    schemes = resp.json()
    assert len(schemes) >= 3

    # Test history endpoint
    resp_hist = client.get("/api/policies/Post-Matric Scholarship for SC Students/history")
    assert resp_hist.status_code == 200
    hist = resp_hist.json()
    assert hist["total_versions"] >= 2
    assert len(hist["timeline_events"]) >= 2


def test_changes_compare_endpoint(client: TestClient):
    """POST /api/changes/compare detects clause differences between revisions."""
    payload = {
        "base_document_id": "DOC-MoSJE-PMS-SC-2018",
        "target_document_id": "DOC-MoSJE-PMS-SC-2020"
    }
    resp = client.post("/api/changes/compare", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["change_count"] >= 4
    assert "summary" in data


def test_impact_analysis_endpoint(client: TestClient):
    """POST /api/impact/analyze computes student cohort impacts and eligibility deltas."""
    payload = {
        "base_document_id": "DOC-MoSJE-PMS-SC-2018",
        "target_document_id": "DOC-MoSJE-PMS-SC-2020"
    }
    resp = client.post("/api/impact/analyze", json=payload)
    assert resp.status_code == 200
    report = resp.json()
    assert report["report_id"]
    assert report["summary"]
    assert len(report["explicitly_affected_groups"]) > 0 or len(report["potentially_affected_groups"]) > 0


def test_knowledge_graph_endpoints(client: TestClient):
    """GET /api/graph returns nodes/edges and supports mermaid format."""
    resp_json = client.get("/api/graph")
    assert resp_json.status_code == 200
    graph_data = resp_json.json()
    assert graph_data["node_count"] > 0
    assert graph_data["edge_count"] > 0

    resp_mermaid = client.get("/api/graph?format=mermaid")
    assert resp_mermaid.status_code == 200
    assert "flowchart" in resp_mermaid.json()["data"]


def test_document_ingestion_api(client: TestClient):
    """POST /api/documents/ingest parses raw notification text into clauses."""
    raw_notification = """
    Clause 1. Scope: This notification covers higher education grants across India.
    Clause 2. Eligibility: Annual family income must not exceed ₹ 3,00,000/- per annum.
    Clause 3. Value: Maintenance allowance is ₹ 1,500 per month for hostellers.
    """
    payload = {
        "raw_text": raw_notification,
        "scheme_name": "Test Special Educational Grant",
        "ministry": "Ministry of Education",
        "document_type": "NOTIFICATION",
        "order_number": "TEST-NOTIF-2026/01",
        "publication_date": "2026-05-15",
        "version": "1.0",
    }
    resp = client.post("/api/documents/ingest", json=payload)
    assert resp.status_code == 201
    doc = resp.json()
    assert doc["scheme_name"] == "Test Special Educational Grant"
    assert len(doc["clauses"]) == 3
