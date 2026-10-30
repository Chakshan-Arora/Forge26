# Policy Intel: REST API Documentation

The Policy Intel FastAPI backend provides RESTful endpoints organized across seven logical domains:

Base URL: `http://localhost:8000/api`
Interactive Swagger UI: `http://localhost:8000/api/docs`
ReDoc Specification: `http://localhost:8000/api/redoc`

---

## 1. System & Health

### `GET /api/health`
Checks server health, database connectivity, and registered policy count.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "Policy Intel",
  "version": "1.0.0",
  "database": "connected",
  "registered_documents": 6,
  "environment": "development"
}
```

### `GET /api/stats`
Returns system-wide metrics on documents, flagship schemes, detected changes, and Knowledge Graph entities.

---

## 2. Documents

### `GET /api/documents`
Lists all registered policy documents with optional filters:
- `scheme_name` (string, optional)
- `ministry` (string, optional)
- `document_type` (string, optional: `POLICY`, `GUIDELINES`, `NOTIFICATION`, etc.)

### `GET /api/documents/{document_id}`
Returns complete details of a specific policy document, including all structured clauses and parsed attributes.

### `POST /api/documents/ingest`
Ingests a new official notification or guidelines document.
Supports either:
1. Raw unstructured notification text (auto-segmented into numbered clauses by `PolicyDocumentExtractor`).
2. Pre-structured `Document` payload conforming to `shared.schemas.Document`.

---

## 3. Policies & Lineage

### `GET /api/policies`
Returns a list of unique government schemes, their active version, total registered documents, and issuing ministry.

### `GET /api/policies/{scheme_name}/history`
Returns the chronological regulatory timeline of revisions, guidelines, and amendments for a scholarship scheme.

---

## 4. Changes & Comparisons

### `GET /api/changes`
Lists detected regulatory changes from persistent storage.
- `document_id` (optional filter)
- `change_type` (optional filter: `ADDED`, `MODIFIED`, `REPLACED`, etc.)

### `GET /api/changes/{change_id}`
Retrieves a specific change record with its full supporting verbatim evidence citations.

### `POST /api/changes/compare`
Executes on-demand clause comparison between two policy revisions:
```json
{
  "base_document_id": "DOC-MoSJE-PMS-SC-2018",
  "target_document_id": "DOC-MoSJE-PMS-SC-2020"
}
```

---

## 5. Student Impact Analysis

### `POST /api/impact/analyze`
Generates a multi-dimensional impact report evaluating affected student cohorts, deterministic interval shifts, and practical actions:
```json
{
  "base_document_id": "DOC-MoSJE-PMS-SC-2018",
  "target_document_id": "DOC-MoSJE-PMS-SC-2020"
}
```

### `GET /api/impact/{analysis_id}`
Retrieves a previously generated impact analysis report by ID.

---

## 6. Regulatory Knowledge Graph

### `GET /api/graph`
Returns the regulatory knowledge graph.
- `format=json` (default): Returns `{ "nodes": [...], "edges": [...] }` for interactive graph rendering.
- `format=mermaid`: Returns Mermaid markdown diagram syntax.

### `GET /api/graph/{entity_id}`
Returns the local subgraph neighborhood (directly connected nodes and edges) for a given scheme, document, or clause.

---

## 7. AI Agent Investigation

### `POST /api/agent/query`
Submits a natural language policy question to the LangGraph regulatory investigation orchestrator.

**Request:**
```json
{
  "query": "What changed in the Post-Matric Scholarship for SC students guidelines?",
  "scheme_name": "Post-Matric Scholarship for SC Students",
  "session_id": "optional-custom-session-id"
}
```

**Response (200 OK):**
```json
{
  "session_id": "SES-6D442960",
  "query": "What changed in the Post-Matric Scholarship for SC students guidelines?",
  "scheme_name": "Post-Matric Scholarship for SC Students",
  "direct_answer": "**Regulatory Change Intelligence for Post-Matric Scholarship for SC Students:**...",
  "reasoning_type": "DETERMINISTIC_CALCULATION",
  "steps_taken": [
    { "step_number": 1, "step_name": "Query Analysis & Classification", "tool_invoked": "IntentClassifier" },
    { "step_number": 2, "step_name": "Regulatory Document & Clause Retrieval", "tool_invoked": "CorpusRetriever" },
    { "step_number": 3, "step_name": "Regulatory Comparison & Impact Analysis", "tool_invoked": "PolicyIntelEngine" },
    { "step_number": 4, "step_name": "Evidence Sufficiency & Caveat Verification", "tool_invoked": "EvidenceEngine" },
    { "step_number": 5, "step_name": "Structured Synthesis & Recommendation Formulation", "tool_invoked": "ResponseSynthesizer" }
  ],
  "detected_changes": [...],
  "impact_summary": "...",
  "affected_groups": [...],
  "evidence_citations": [...],
  "verification_confidence": 0.95,
  "uncertainties": [...],
  "actionable_recommendations": [...]
}
```

### `GET /api/agent/history`
Returns recent investigation sessions and audit traces from the database.
