"""
End-to-End Pipeline Integration Test.

Validates the full lifecycle specified in the project requirements:
Official document -> Structured policy -> Change detection -> Regulatory graph
-> Impact analysis -> Evidence verification -> User-facing report.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.schemas import Document, Clause, DocumentType, ClauseType, ChangeType
from backend.database import Base
from backend.services.persistence_service import (
    save_document,
    get_document_by_id,
    list_documents,
)
from backend.services.intelligence_service import IntelligenceService
from backend.agent import RegulatoryInvestigationAgent
from shared.schemas import AgentQueryRequest


def test_complete_e2e_regulatory_lifecycle():
    """Validates the end-to-end workflow from document to evidence-backed report."""
    # 1. In-memory database setup
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # 2. Ingest Revision 1 (2024 Baseline)
    doc_v1 = Document(
        id="DOC-E2E-TEST-2024",
        title="National Merit Scheme 2024 Guidelines",
        scheme_name="National Merit Support Scheme",
        ministry="Ministry of Education",
        document_type=DocumentType.GUIDELINES,
        order_number="EDU/2024/001",
        publication_date="2024-04-01",
        version="1.0",
        status="SUPERSEDED",
        clauses=[
            Clause(
                id="E2E-CL-1",
                document_id="DOC-E2E-TEST-2024",
                clause_number="1.0",
                title="Income Eligibility",
                text="The annual income of parents must not exceed ₹ 2,00,000 per annum.",
                clause_type=ClauseType.ELIGIBILITY,
                structured_attributes={"income_ceiling": 200000.0, "unit": "per_annum"}
            ),
            Clause(
                id="E2E-CL-2",
                document_id="DOC-E2E-TEST-2024",
                clause_number="2.0",
                title="Scholarship Amount",
                text="The scholarship shall be ₹ 10,000 per annum.",
                clause_type=ClauseType.FINANCIAL,
                structured_attributes={"numeric_amount": 10000.0, "unit": "per_annum"}
            )
        ]
    )
    save_document(db, doc_v1)
    assert get_document_by_id(db, "DOC-E2E-TEST-2024") is not None

    # 3. Ingest Revision 2 (2026 Amendment)
    doc_v2 = Document(
        id="DOC-E2E-TEST-2026",
        title="National Merit Scheme 2026 Amendment",
        scheme_name="National Merit Support Scheme",
        ministry="Ministry of Education",
        document_type=DocumentType.AMENDMENT,
        order_number="EDU/2026/009",
        publication_date="2026-04-01",
        version="2.0",
        status="ACTIVE",
        clauses=[
            Clause(
                id="E2E-CL-1-REV",
                document_id="DOC-E2E-TEST-2026",
                clause_number="1.0",
                title="Income Eligibility Revision",
                text="The annual income ceiling has been enhanced to ₹ 3,00,000 per annum.",
                clause_type=ClauseType.ELIGIBILITY,
                structured_attributes={"income_ceiling": 300000.0, "unit": "per_annum"}
            ),
            Clause(
                id="E2E-CL-2-REV",
                document_id="DOC-E2E-TEST-2026",
                clause_number="2.0",
                title="Enhanced Scholarship",
                text="The scholarship is enhanced to ₹ 15,000 per annum paid via DBT.",
                clause_type=ClauseType.FINANCIAL,
                structured_attributes={"numeric_amount": 15000.0, "unit": "per_annum"}
            )
        ]
    )
    save_document(db, doc_v2)

    # 4. Intelligence Engine comparison
    intel = IntelligenceService()
    intel.register_document(doc_v1)
    intel.register_document(doc_v2)

    changes, summary = intel.compare_documents(
        base_document_id=doc_v1.id,
        target_document_id=doc_v2.id,
        db=db
    )
    assert len(changes) >= 2
    assert summary["total_changes"] >= 2

    # 5. Regulatory Knowledge Graph verification
    kg = intel.get_knowledge_graph_data(db)
    assert len(kg["nodes"]) > 0
    assert any(n["id"] == "DOC-E2E-TEST-2026" for n in kg["nodes"])

    # 6. Impact Analysis Report
    impact = intel.analyze_impact(
        base_document_id=doc_v1.id,
        target_document_id=doc_v2.id,
        db=db
    )
    assert impact.summary is not None
    assert len(impact.evidence_trail) > 0

    # 7. Agentic Investigation Query
    agent = RegulatoryInvestigationAgent(intel_service=intel)
    query_resp = agent.investigate(
        AgentQueryRequest(
            query="What changed in the National Merit Support Scheme between 2024 and 2026?",
            scheme_name="National Merit Support Scheme"
        )
    )
    assert len(query_resp.direct_answer) > 50
    assert len(query_resp.steps_taken) >= 4
    assert query_resp.verification_confidence > 0.7
    assert len(query_resp.evidence_citations) > 0

    db.close()
