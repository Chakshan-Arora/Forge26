# Person 3 Integration Contract: Regulatory Intelligence Engine

**Author**: Lead Regulatory Intelligence & Impact Analysis Engineer (Person 2)  
**Consumer**: Platform, FastAPI Backend & Agent Engineer (Person 3)  
**Package / Namespace**: `intelligence`  
**Shared Schema Module**: `shared.schemas`  
**Contract Version**: `2.0.0` (Hardened & Independently Verified)

---

## 1. Quick Start & Exact Imports

```python
from shared.schemas import (
    Document,
    Clause,
    DocumentType,
    ClauseType,
    ChangeType,
    ChangeRecord,
    ConflictReport,
    ImpactAnalysisReport,
    TemporalApplicabilityResult,
    EvidenceRecord,
    AffectedGroup,
    StructuredValue,
)

from intelligence import (
    PolicyIntelEngine,
    ChangeDetector,
    ClauseMatcher,
    TemporalResolver,
    ImpactAnalyzer,
    ConflictDetector,
    EvidenceEngine,
    EvidenceMissingError,
    EvidenceValidationError,
    NetworkXRegulatoryGraph,
)
```

---

## 2. Primary Public Facade: `PolicyIntelEngine`

The authoritative entry point is `PolicyIntelEngine`. It exposes high-level, production-hardened methods designed directly for FastAPI endpoints and agent tools.

### A. Lifecycle & Ingestion

```python
engine = PolicyIntelEngine()

# Register single document (aliased to ingest_document)
engine.register_document(document: Document) -> None
engine.ingest_document(document: Document) -> None

# Register batch of documents (aliased to ingest_documents)
engine.register_documents(documents: List[Document]) -> None
engine.ingest_documents(documents: List[Document]) -> None

# Document repository access
doc = engine.get_document(document_id: str) -> Optional[Document]
all_docs = engine.list_documents() -> List[Document]
```

### B. Clause-Level Comparison (`compare_documents`)

```python
changes, summary = engine.compare_documents(
    base_document: Optional[Union[str, Document]] = None,
    target_document: Optional[Union[str, Document]] = None,
    update_graph: bool = True,
    base_document_id: Optional[str] = None,
    target_document_id: Optional[str] = None,
) -> Tuple[List[ChangeRecord], ChangeDetectionSummary]
```
- **Inputs**:
  - `base_document` / `base_document_id`: Either the baseline `Document` instance, its string ID (retrieved from engine registry), or `None` (for initial policy baselines where all clauses are treated as `ADDED`).
  - `target_document` / `target_document_id`: The amending or revised `Document` instance or its string ID.
  - `update_graph`: If `True` (default), newly detected `ChangeRecord` objects are automatically ingested as typed nodes and edges in the regulatory knowledge graph.
- **Outputs**:
  - `changes`: `List[ChangeRecord]` — List of validated clause shifts.
  - `summary`: `ChangeDetectionSummary` — Aggregated counts of additions, removals, modifications, replacements, extensions, exemptions, clarifications, and renumbering.

### C. Evidence-Backed Impact Analysis (`analyze_impact`)

```python
report: ImpactAnalysisReport = engine.analyze_impact(
    target_document: Optional[Union[str, Document]] = None,
    base_document: Optional[Union[str, Document]] = None,
    changes: Optional[List[ChangeRecord]] = None,
    target_document_id: Optional[str] = None,
    base_document_id: Optional[str] = None,
) -> ImpactAnalysisReport
```
- **Inputs**:
  - `target_document` (or `target_document_id`): Required.
  - `base_document` (or `base_document_id`): Optional baseline.
  - `changes`: Optional pre-computed `List[ChangeRecord]`. If omitted, comparison is executed automatically.
- **Outputs**:
  - `ImpactAnalysisReport` containing:
    - `affected_groups`: `List[AffectedGroup]` with concrete student cohorts (`Day Scholars`, `Hostellers`, `Fresh Applicants`, `Renewal Candidates`).
    - `deterministic_deltas`: Mathematical relaxation and restriction intervals (e.g. `{"type": "INCOME_CEILING_RELAXATION", "newly_eligible_interval": {"min_exclusive": 150000.0, "max_inclusive": 350000.0}}`).
    - `actionable_recommendations`: Clear, step-by-step guidance for students, institutions, and administrative portals.
    - `traceable_evidence`: Every single claim is backed by verbatim policy citations.

### D. Point-in-Time Regulatory Applicability (`resolve_applicability`)

```python
result: TemporalApplicabilityResult = engine.resolve_applicability(
    scheme_name: str,
    query_date: str  # Format: "YYYY-MM-DD" or Indian FY "2022-23"
) -> TemporalApplicabilityResult

# Backward-compatible alias:
result = engine.query_eligibility_at_date(scheme_name, query_date)
```
- **Outputs**:
  - `TemporalApplicabilityResult` with `status` (`"RESOLVED"`, `"PARTIALLY_RESOLVED"`, or `"UNRESOLVED"`).
  - `applicable_document_ids`: List of document IDs valid on `query_date`.
  - `applicable_clauses`: Exact `Clause` instances legally enforceable at that point in time.
  - `active_amendments`: List of notifications published prior to `query_date` but pending enforcement (e.g., `status = "NOTIFIED_PENDING_ENFORCEMENT"`).
  - `unresolved_reasons`: Detailed legal rationale if dates are missing or ambiguous.

### E. Provenance Tracing (`trace_condition_origin`)

```python
provenance_trail: List[Dict[str, Any]] = engine.trace_condition_origin(
    scheme_name: str,
    condition_keyword: str  # e.g., "income ceiling", "attendance", "maintenance"
) -> List[Dict[str, Any]]

# Backward-compatible alias:
provenance_trail = engine.trace_condition(scheme_name, condition_keyword)
```
- **Returns**: Chronologically ordered list of clauses introducing or altering the specified condition across all versions.

### F. Conflict & Dependency Gap Scanning (`detect_conflicts`)

```python
conflicts: List[ConflictReport] = engine.detect_conflicts(scheme_name: str) -> List[ConflictReport]
```
- **Returns**: `List[ConflictReport]` identifying:
  - `DIRECT_CONTRADICTION`: Incompatible criteria on the same effective date.
  - `PARTIAL_AMENDMENT`: Sub-clause modifications requiring baseline context.
  - `DISTINCT_COHORTS_DISAMBIGUATION`: Distinguishing cohort-specific rules (Hostellers vs Day Scholars) from false contradictions.
  - `MISSING_HISTORICAL_DEPENDENCY`: Referenced predecessor orders absent from the repository.

### G. Graph & Audit Trail Export

```python
graph_dict: Dict[str, Any] = engine.export_graph_dict()
# Returns: {"total_nodes": N, "total_edges": E, "nodes": [...], "edges": [...]}

mermaid_markup: str = engine.export_graph_mermaid()
# Returns: Mermaid-compatible diagram string for UI rendering

audit_text: str = engine.get_audit_trail(evidence_list: List[EvidenceRecord])
# Returns: Formatted markdown audit table
```

---

## 3. Working Code Example for Person 3

```python
from data.real_policies import get_nmmss_2017_document, get_nmmss_2022_document
from intelligence import PolicyIntelEngine

def run_integration_pipeline():
    # 1. Instantiate engine
    engine = PolicyIntelEngine()

    # 2. Ingest authentic documents
    doc_2017 = get_nmmss_2017_document()
    doc_2022 = get_nmmss_2022_document()
    engine.ingest_documents([doc_2017, doc_2022])

    # 3. Detect changes at clause level
    changes, summary = engine.compare_documents(
        base_document_id=doc_2017.id,
        target_document_id=doc_2022.id
    )
    print(f"Total changes: {summary.total_changes}")

    # 4. Perform impact analysis
    report = engine.analyze_impact(
        target_document_id=doc_2022.id,
        base_document_id=doc_2017.id,
        changes=changes
    )
    for delta in report.deterministic_deltas:
        print(f"Mathematical delta: {delta}")

    # 5. Point-in-time applicability check
    res_2019 = engine.resolve_applicability("National Means-cum-Merit Scholarship Scheme", "2019-06-01")
    assert res_2019.applicable_document_ids == [doc_2017.id]

    res_2023 = engine.resolve_applicability("National Means-cum-Merit Scholarship Scheme", "2023-01-01")
    assert res_2023.applicable_document_ids == [doc_2022.id]

    # 6. Export graph
    graph_dict = engine.export_graph_dict()
    print(f"Graph nodes: {graph_dict['total_nodes']}, edges: {graph_dict['total_edges']}")

if __name__ == "__main__":
    run_integration_pipeline()
```

---

## 4. Error Handling & Exception Types

| Exception Class | Trigger Condition | Recommended FastAPI HTTP Status |
| :--- | :--- | :--- |
| `ValueError` | Non-existent document ID, missing target document, or unrecognized matching method. | `400 Bad Request` or `404 Not Found` |
| `EvidenceMissingError` | Attempt to register or construct a `ChangeRecord` without verbatim supporting text. | `422 Unprocessable Entity` |
| `EvidenceValidationError` | Verbatim quote does not match source document text within tolerance threshold. | `422 Unprocessable Entity` |

---

## 5. Performance & Concurrency Guarantees

- **Execution Time**: Under **50ms** for two 50-clause documents using threshold-safe maximum weight bipartite matching (`networkx.max_weight_matching`).
- **Memory Footprint**: In-memory graph of 100 documents and 1,000 clauses consumes `< 15 MB` RAM.
- **Concurrency**: Pure Python read methods (`resolve_applicability`, `trace_condition_origin`, `detect_conflicts`, `export_graph_dict`) are thread-safe and re-entrant. Mutation methods (`ingest_document`, `compare_documents` with `update_graph=True`) update the in-memory graph. In a multi-worker ASGI setup, documents should be loaded during FastAPI startup lifespan or backed by a persistent graph store.

---

## 6. Person 3 Assumptions & Boundaries

### What Person 3 Can Safely Assume:
1. Every `ChangeRecord.evidence` contains at least one verified `EvidenceRecord` with exact supporting text.
2. Unmatched clauses are categorized cleanly into `ADDED` or `REMOVED` without phantom pairings.
3. Dates in ISO format `YYYY-MM-DD` and Indian Financial Year strings (e.g. `2022-23`) are parsed reliably.
4. An omission of a clause is flagged with an explicit legal uncertainty note rather than an assumed statutory repeal.

### What Person 3 Must NOT Assume:
1. **Never assume publication date equals effective date**: Central Government notifications regularly specify forward enforcement dates. Always inspect `TemporalApplicabilityResult.active_amendments` for pending orders.
2. **Never assume that a higher-numbered document completely supersedes an earlier one**: Partial amendments modify only targeted provisions while previous rules remain in force.
3. **Never resolve genuine contradictions silently**: If `ConflictReport.resolution_status == "UNRESOLVED"`, prompt the user or highlight the conflicting notifications.
