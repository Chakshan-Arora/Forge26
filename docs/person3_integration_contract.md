# Policy Intel: Person 3 (Backend API) Integration Contract

This document is the authoritative integration contract between **Person 2 (Regulatory Intelligence & Impact Analysis Engine)** and **Person 3 (Backend API, Persistence, and FastAPI Service)**.

---

## 1. System Responsibilities and Boundaries

- **Person 1 (Document Ingestion)**: Ingests PDF/Gazettes and provides structured `Document` objects containing metadata and `Clause` items.
- **Person 2 (Intelligence Engine - This Module)**: Consumes `Document` objects, maintains the temporal knowledge graph, executes clause-level change detection, evaluates temporal applicability, computes deterministic student impacts, audits regulatory conflicts, and validates evidence.
- **Person 3 (Backend API & Platform)**: Instantiates `PolicyIntelEngine`, wraps its methods with FastAPI endpoints, manages persistence, and delivers JSON payloads to the React dashboard.

---

## 2. Exact Import Statements

```python
from intelligence import (
    PolicyIntelEngine,
    IntelligenceSettings,
    DEFAULT_SETTINGS,
    EvidenceMissingError,
    ChangeType,
    ClauseType,
    DocumentType,
    NodeType,
    RelationshipType,
)
from shared.schemas import (
    Document,
    Clause,
    ChangeRecord,
    ImpactAnalysisReport,
    ConflictReport,
    TemporalApplicabilityResult,
    EvidenceRecord,
    StructuredValue,
    AffectedGroup,
)
```

---

## 3. Authoritative Class and Method Signatures

All operations are exposed through the unified facade **`PolicyIntelEngine`** located in [`intelligence/engine.py`](file:///intelligence/engine.py):

### 3.1 Initialization
```python
engine = PolicyIntelEngine(
    settings: Optional[IntelligenceSettings] = None,
    graph_backend: Optional[BaseRegulatoryGraph] = None
)
```
- Default `settings` uses `DEFAULT_SETTINGS` (optimal matching, INR currency, strict evidence enforcement).
- Default `graph_backend` uses `NetworkXRegulatoryGraph` (in-memory multi-directed graph).

### 3.2 Ingestion & Document Registration
```python
engine.ingest_document(document: Document) -> None
engine.ingest_documents(documents: List[Document]) -> None
```
- **Aliases**: `register_document`, `register_documents`
- **Behavior**: Registers the document in the repository, populates Document, Scheme, Authority, Clause, and Condition nodes in the knowledge graph, and indexes the document in the temporal resolver.

```python
engine.get_document(document_id: str) -> Optional[Document]
engine.list_documents() -> List[Document]
```

### 3.3 Clause-Level Document Comparison
```python
engine.compare_documents(
    base_document: Optional[Union[str, Document]] = None,
    target_document: Optional[Union[str, Document]] = None,
    update_graph: bool = True,
    method: str = "optimal",
    base_document_id: Optional[str] = None,
    target_document_id: Optional[str] = None,
) -> Tuple[List[ChangeRecord], ChangeDetectionSummary]
```
- Accepts either `Document` instances or registered document ID strings (`str`).
- Also accepts keyword arguments `base_document_id` and `target_document_id`.
- `method`: `"optimal"` (default, uses Kuhn-Munkres/Hungarian assignment via scipy) or `"greedy"` (heuristic candidate sort).
- **Return Type**: `Tuple[List[ChangeRecord], ChangeDetectionSummary]`
- If caller only needs the change records list:
```python
engine.detect_changes(
    base_document: Optional[Union[str, Document]] = None,
    target_document: Optional[Union[str, Document]] = None,
    update_graph: bool = True,
    method: str = "optimal",
) -> List[ChangeRecord]
```

### 3.4 Multi-Dimensional Impact Analysis
```python
engine.analyze_impact(
    target_document: Optional[Union[str, Document]] = None,
    base_document: Optional[Union[str, Document]] = None,
    changes: Optional[List[ChangeRecord]] = None,
    target_document_id: Optional[str] = None,
    base_document_id: Optional[str] = None,
) -> ImpactAnalysisReport
```
- **Return Type**: `ImpactAnalysisReport` containing:
  - `explicitly_affected_groups`: List of demographic/academic groups directly named.
  - `potentially_affected_groups`: Groups identified via deterministic interval shifts.
  - `deterministic_deltas`: Exact numerical deltas (income expansion intervals, scholarship increases, fee waivers).
  - `practical_consequences`: Actionable student guidance (DBT Aadhaar linking, Freeship Card, DigiLocker).
  - `evidence_trail`: Complete list of supporting `EvidenceRecord` items.

### 3.5 Temporal Point-in-Time Applicability
```python
engine.resolve_applicability(
    scheme_name: str,
    query_date: str
) -> TemporalApplicabilityResult
```
- **Alias**: `query_eligibility_at_date`
- `query_date`: ISO format (`"YYYY-MM-DD"`) or fuzzy date (`"01/08/2023"`).
- **Return Type**: `TemporalApplicabilityResult`
  - `status`: `"RESOLVED"`, `"PARTIALLY_RESOLVED"`, or `"UNRESOLVED"`
  - `applicable_document_ids`: List of document IDs legally in effect on `query_date`.
  - `applicable_clauses`: Extracted list of all active `Clause` objects.
  - `active_amendments`: Pending notifications published before `query_date` but taking legal effect after `query_date` (`NOTIFIED_PENDING_ENFORCEMENT`).
  - `superseded_clauses`: Prior provisions that have been superseded.
  - `unresolved_reasons`: Detailed statutory caveats if effective dates cannot be confirmed.

### 3.6 Regulatory Provenance / Condition Origin Query
```python
engine.trace_condition_origin(
    scheme_name: str,
    condition_keyword: str
) -> List[Dict[str, Any]]
```
- **Alias**: `trace_condition`
- Answers: *"Which notification or amendment introduced this condition?"*
- **Return Type**: Chronologically sorted list of document references and clause texts establishing that condition.

### 3.7 Conflict and Dependency Detection
```python
engine.detect_conflicts(scheme_name: str) -> List[ConflictReport]
```
- Detects contradictions, missing predecessor documents, partial amendments, and distinct scope rules (e.g. hosteller vs day scholar).
- **Return Type**: `List[ConflictReport]`

### 3.8 Knowledge Graph and Audit Exports
```python
engine.export_graph_dict() -> Dict[str, Any]      # (Alias: get_graph_dict)
engine.export_graph_mermaid() -> str             # (Alias: get_graph_mermaid)
engine.get_audit_trail(evidence_list: List[EvidenceRecord]) -> str
```

---

## 4. End-to-End Working Integration Example

The following code is verified and executable:

```python
from intelligence import PolicyIntelEngine
from shared.schemas import Document, Clause, DocumentType, ClauseType

# 1. Instantiate engine
engine = PolicyIntelEngine()

# 2. Ingest documents provided by Person 1
doc_2017 = Document(
    id="DOC-MoE-NMMSS-2017",
    title="NMMSS Guidelines 2017",
    scheme_name="National Means-cum-Merit Scholarship Scheme",
    ministry="Ministry of Education",
    document_type=DocumentType.GUIDELINES,
    effective_date="2017-04-01",
    clauses=[
        Clause(
            id="NMMSS-17-CL-2",
            document_id="DOC-MoE-NMMSS-2017",
            clause_number="2",
            text="Students whose parental annual income does not exceed ₹ 1,50,000 per annum are eligible.",
            clause_type=ClauseType.ELIGIBILITY,
            structured_attributes={"value_type": "income_ceiling", "numeric_amount": 150000.0}
        )
    ]
)

doc_2022 = Document(
    id="DOC-MoE-NMMSS-2022",
    title="NMMSS Revised Guidelines 2022",
    scheme_name="National Means-cum-Merit Scholarship Scheme",
    ministry="Ministry of Education",
    document_type=DocumentType.GUIDELINES,
    effective_date="2022-03-15",
    references=[{"target_document_id": "DOC-MoE-NMMSS-2017", "relationship": "REPLACES"}],
    clauses=[
        Clause(
            id="NMMSS-22-CL-2",
            document_id="DOC-MoE-NMMSS-2022",
            clause_number="2",
            text="Students whose parental annual income does not exceed ₹ 3,50,000 per annum are eligible.",
            clause_type=ClauseType.ELIGIBILITY,
            structured_attributes={"value_type": "income_ceiling", "numeric_amount": 350000.0}
        )
    ]
)

engine.ingest_documents([doc_2017, doc_2022])

# 3. Detect clause-level changes (Globally optimal assignment)
changes, summary = engine.compare_documents(
    base_document=doc_2017,
    target_document=doc_2022,
    update_graph=True,
    method="optimal"
)

# Inspect change record
for chg in changes:
    print(f"Change ID: {chg.change_id}")
    print(f"Type: {chg.change_type.value}")
    print(f"Previous Value: {chg.previous_value}")
    print(f"Current Value: {chg.current_value}")
    print(f"Evidence text: {chg.evidence[0].exact_supporting_text}")

# 4. Point-in-time applicability resolution
res_2019 = engine.resolve_applicability("National Means-cum-Merit Scholarship Scheme", "2019-01-01")
print(f"Applicable in 2019: {res_2019.applicable_document_ids}") # ['DOC-MoE-NMMSS-2017']

res_2024 = engine.resolve_applicability("National Means-cum-Merit Scholarship Scheme", "2024-01-01")
print(f"Applicable in 2024: {res_2024.applicable_document_ids}") # ['DOC-MoE-NMMSS-2022']

# 5. Student Impact Analysis
impact = engine.analyze_impact(target_document=doc_2022, base_document=doc_2017, changes=changes)
for delta in impact.deterministic_deltas:
    print("Delta Type:", delta["type"])
    print("Newly Eligible Interval:", delta.get("newly_eligible_interval"))

# 6. Export Knowledge Graph payload for React UI
graph_dict = engine.export_graph_dict()
# { "total_nodes": 12, "total_edges": 14, "nodes": [...], "edges": [...] }
```

---

## 5. Error Handling and Exception Contracts

| Exception Type | Triggering Condition | Recommended Backend / HTTP Handling |
|---|---|---|
| `ValueError` | `target_document` is `None` or document ID cannot be found in engine. | Return HTTP 404 (Not Found) or HTTP 400 (Bad Request). |
| `EvidenceMissingError` | Attempted to emit a change record, impact finding, or conclusion with empty/whitespace evidence text. | Return HTTP 422 (Unprocessable Entity). The intelligence engine refuses to emit unverified assertions. |
| `KeyError` | Missing required fields in unstructured external dictionary payloads. | Validate against Pydantic `shared.schemas` models first. |

---

## 6. Dependencies and Runtime Requirements

- **Python Version**: `>= 3.10` (Python 3.11 recommended).
- **Core Dependencies**: `pydantic>=2.0`, `networkx>=3.0`, `scipy>=1.10`, `numpy>=1.24`, `python-dateutil`.
- **Zero External API Requirement**: The engine operates 100% deterministically offline without requiring external network access or paid LLM API keys.
- **Pluggable Architecture**:
  - Graph backend: Implement `BaseRegulatoryGraph` to connect Neo4j.
  - Semantic similarity: Optional LLM interpretation hook available in `SemanticComparator.interpret_complex_change`.
