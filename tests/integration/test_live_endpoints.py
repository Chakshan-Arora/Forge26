import pytest
from fastapi.testclient import TestClient
from backend.main import app

def test_all_endpoints():
    with TestClient(app) as client:
        results = []

        def check(name, resp, expected_status, validator=None):
            passed = resp.status_code == expected_status
            detail = ""
            if passed and validator:
                try:
                    validator_res = validator(resp.json())
                    if validator_res is not True:
                        passed = False
                        detail = f"Validator failed: {validator_res}. Keys: {list(resp.json().keys())}"
                except Exception as e:
                    passed = False
                    detail = f"Exception in validator: {e}"
            if not passed and not detail:
                detail = f"Status got {resp.status_code}, expected {expected_status}. Body: {resp.text[:200]}"
            results.append({"name": name, "passed": passed, "status": resp.status_code, "detail": detail})
            status_sym = "[PASS]" if passed else "[FAIL]"
            print(f"{status_sym} {name} (HTTP {resp.status_code}) {detail}")

        print("=== 1. HEALTH & STATS ===")
        r = client.get("/api/health")
        check("GET /api/health", r, 200, lambda d: d.get("status") == "healthy")

        r = client.get("/api/stats")
        check("GET /api/stats", r, 200, lambda d: d.get("total_documents", 0) >= 6)

        print("\n=== 2. DOCUMENTS ===")
        r = client.get("/api/documents")
        check("GET /api/documents (list)", r, 200, lambda d: isinstance(d, list) and len(d) >= 6)

        r = client.get("/api/documents/DOC-MoSJE-PMS-SC-2020")
        check("GET /api/documents/{id} (valid)", r, 200, lambda d: d["id"] == "DOC-MoSJE-PMS-SC-2020" and d.get("verification_status") == "VERIFIED")

        r = client.get("/api/documents/DOC-MoSJE-PMS-SC-2018")
        check("GET /api/documents/{id} (partially verified baseline)", r, 200, lambda d: d.get("verification_status") == "PARTIALLY_VERIFIED")

        r = client.get("/api/documents/NON_EXISTENT_DOC")
        check("GET /api/documents/{id} (missing)", r, 404)

        ingest_payload = {
            "scheme_name": "Test Gazette Scheme",
            "ministry": "Ministry of Education",
            "document_type": "NOTIFICATION",
            "raw_text": "Clause 1.0 Income Ceiling: Parental annual income must not exceed Rs 3,00,000 per annum.\nClause 2.0 Academic: Minimum 60% marks in previous examination."
        }
        r = client.post("/api/documents/ingest", json=ingest_payload)
        check("POST /api/documents/ingest (valid raw_text)", r, 201, lambda d: len(d.get("clauses", [])) >= 1)

        r = client.post("/api/documents/ingest", json={"scheme_name": "Missing Ministry"})
        check("POST /api/documents/ingest (invalid payload)", r, 422)

        print("\n=== 3. POLICIES & HISTORY ===")
        r = client.get("/api/policies")
        check("GET /api/policies (list schemes)", r, 200, lambda d: len(d) >= 3)

        r = client.get("/api/policies/Post-Matric Scholarship for SC Students")
        check("GET /api/policies/{scheme} (valid)", r, 200, lambda d: d["scheme_name"] == "Post-Matric Scholarship for SC Students" and len(d["documents"]) >= 2)

        r = client.get("/api/policies/NonExistentSchemeXYZ")
        check("GET /api/policies/{scheme} (missing)", r, 404)

        r = client.get("/api/policies/Post-Matric Scholarship for SC Students/history")
        check("GET /api/policies/{scheme}/history (valid)", r, 200, lambda d: len(d.get("timeline_events", [])) >= 2)

        print("\n=== 4. CHANGES & COMPARISON ===")
        compare_payload = {
            "base_document_id": "DOC-MoSJE-PMS-SC-2018",
            "target_document_id": "DOC-MoSJE-PMS-SC-2020"
        }
        r = client.post("/api/changes/compare", json=compare_payload)
        check("POST /api/changes/compare (valid pair)", r, 200, lambda d: len(d.get("changes", [])) >= 4)

        r = client.post("/api/changes/compare", json={"target_document_id": "NON_EXISTENT_TARGET"})
        check("POST /api/changes/compare (missing target)", r, 400)

        r = client.get("/api/changes")
        check("GET /api/changes (list changes)", r, 200, lambda d: len(d) >= 1)

        r = client.get("/api/changes/CHG-NON-EXISTENT")
        check("GET /api/changes/{id} (missing)", r, 404)

        print("\n=== 5. IMPACT ANALYSIS ===")
        impact_payload = {
            "base_document_id": "DOC-MoSJE-PMS-SC-2018",
            "target_document_id": "DOC-MoSJE-PMS-SC-2020"
        }
        r = client.post("/api/impact/analyze", json=impact_payload)
        report_id = None
        if r.status_code == 200:
            report_id = r.json().get("report_id")
        check("POST /api/impact/analyze (valid)", r, 200, lambda d: "report_id" in d and len(d.get("explicitly_affected_groups", [])) >= 1)

        r = client.post("/api/impact/analyze", json={"target_document_id": "NON_EXISTENT_ID"})
        check("POST /api/impact/analyze (invalid target)", r, 400)

        if report_id:
            r = client.get(f"/api/impact/{report_id}")
            check("GET /api/impact/{id} (valid)", r, 200, lambda d: d["report_id"] == report_id)

        r = client.get("/api/impact/NON_EXISTENT_REPORT")
        check("GET /api/impact/{id} (missing)", r, 404)

        print("\n=== 6. REGULATORY KNOWLEDGE GRAPH ===")
        r = client.get("/api/graph")
        check("GET /api/graph (full)", r, 200, lambda d: d.get("node_count", 0) > 10 and d.get("edge_count", 0) > 10)

        r = client.get("/api/graph/DOC-MoSJE-PMS-SC-2020")
        check("GET /api/graph/{entity_id} (subgraph)", r, 200, lambda d: d.get("node_count", 0) > 0)

        print("\n=== 7. AGENT INVESTIGATION & HISTORY ===")
        # Investigation 1: Change Query
        q1 = {"query": "What changed in the Post-Matric Scholarship for SC students guidelines?"}
        r = client.post("/api/agent/query", json=q1)
        check("POST /api/agent/query (change investigation)", r, 200, lambda d: len(d.get("steps_taken", [])) >= 4 and len(d.get("detected_changes", [])) >= 4)

        # Investigation 2: Temporal Query
        q2 = {"query": "What was the applicable eligibility rule on 2019-06-01 for Post-Matric SC students?"}
        r = client.post("/api/agent/query", json=q2)
        check("POST /api/agent/query (temporal applicability)", r, 200, lambda d: "2019" in d.get("direct_answer", "") or "DOC-MoSJE-PMS-SC-2018" in d.get("direct_answer", ""))

        # Investigation 3: Impact Query
        q3 = {"query": "How are students with family income between 2.0 lakh and 2.5 lakh affected by the PMS-SC revision?"}
        r = client.post("/api/agent/query", json=q3)
        check("POST /api/agent/query (cohort impact)", r, 200, lambda d: len(d.get("affected_groups", [])) >= 1 or "income" in d.get("direct_answer", "").lower())

        # Invalid Query
        r = client.post("/api/agent/query", json={})
        check("POST /api/agent/query (invalid/empty body)", r, 422)

        r = client.get("/api/agent/history")
        check("GET /api/agent/history (audit trail)", r, 200, lambda d: len(d) >= 3)

        failed = [res for res in results if not res["passed"]]
        assert len(failed) == 0, f"Failed endpoint tests: {failed}"

if __name__ == "__main__":
    test_all_endpoints()
