"""
Persistence Service for Policy Intel.

Handles conversion between Pydantic domain models and SQLAlchemy ORM models,
CRUD queries, transactions, and seeding the authentic policy corpus.
"""

from __future__ import annotations
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from shared.schemas import (
    Document,
    Clause,
    ChangeRecord,
    EvidenceRecord,
    ImpactAnalysisReport,
    DocumentType,
    ClauseType,
    ChangeType,
)
from backend.models import (
    DocumentModel,
    ClauseModel,
    ChangeModel,
    EvidenceModel,
    ImpactReportModel,
    AgentAuditLogModel,
)
from ingestion.corpus_loader import AuthenticCorpusLoader

logger = logging.getLogger(__name__)


def document_to_schema(model: DocumentModel) -> Document:
    """Converts a DocumentModel ORM instance to a Pydantic Document."""
    clauses = [
        Clause(
            id=c.id,
            document_id=c.document_id,
            clause_number=c.clause_number,
            title=c.title,
            section=c.section,
            text=c.text,
            normalized_text=c.normalized_text,
            clause_type=ClauseType(c.clause_type) if c.clause_type in ClauseType._value2member_map_ else ClauseType.GENERAL,
            structured_attributes=c.structured_attributes or {},
            page_number=c.page_number,
            subclauses=c.subclauses or [],
        )
        for c in (model.clauses or [])
    ]
    return Document(
        id=model.id,
        title=model.title,
        scheme_name=model.scheme_name,
        ministry=model.ministry,
        document_type=DocumentType(model.document_type) if model.document_type in DocumentType._value2member_map_ else DocumentType.NOTIFICATION,
        order_number=model.order_number,
        publication_date=model.publication_date,
        effective_date=model.effective_date,
        valid_until=model.valid_until,
        source_url=model.source_url,
        version=model.version or "1.0",
        status=model.status or "ACTIVE",
        verification_status=getattr(model, "verification_status", "UNVERIFIED") or "UNVERIFIED",
        clauses=clauses,
        references=model.references_json or [],
    )


def save_document(db: Session, doc: Document) -> DocumentModel:
    """Saves or updates a Document and its constituent clauses."""
    existing = db.query(DocumentModel).filter(DocumentModel.id == doc.id).first()
    if existing:
        db.delete(existing)
        db.flush()

    doc_model = DocumentModel(
        id=doc.id,
        title=doc.title,
        scheme_name=doc.scheme_name,
        ministry=doc.ministry,
        document_type=doc.document_type.value if hasattr(doc.document_type, "value") else str(doc.document_type),
        order_number=doc.order_number,
        publication_date=doc.publication_date,
        effective_date=doc.effective_date,
        valid_until=doc.valid_until,
        source_url=doc.source_url,
        version=doc.version,
        status=doc.status,
        references_json=doc.references,
    )
    db.add(doc_model)

    for cl in doc.clauses:
        clause_model = ClauseModel(
            id=cl.id,
            document_id=doc.id,
            clause_number=cl.clause_number,
            title=cl.title,
            section=cl.section,
            text=cl.text,
            normalized_text=cl.normalized_text,
            clause_type=cl.clause_type.value if hasattr(cl.clause_type, "value") else str(cl.clause_type),
            structured_attributes=cl.structured_attributes,
            page_number=cl.page_number,
            subclauses=cl.subclauses,
        )
        db.add(clause_model)

    db.commit()
    db.refresh(doc_model)
    return doc_model


def get_document_by_id(db: Session, document_id: str) -> Optional[Document]:
    """Retrieves a document by ID and returns Pydantic Document."""
    model = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    return document_to_schema(model) if model else None


def list_documents(
    db: Session,
    scheme_name: Optional[str] = None,
    ministry: Optional[str] = None,
    document_type: Optional[str] = None
) -> List[Document]:
    """Queries all registered documents with optional filtering."""
    query = db.query(DocumentModel)
    if scheme_name:
        query = query.filter(DocumentModel.scheme_name.ilike(f"%{scheme_name}%"))
    if ministry:
        query = query.filter(DocumentModel.ministry.ilike(f"%{ministry}%"))
    if document_type:
        query = query.filter(DocumentModel.document_type == document_type)
    
    models = query.order_by(DocumentModel.publication_date.desc()).all()
    return [document_to_schema(m) for m in models]


def save_change_records(db: Session, changes: List[ChangeRecord]) -> None:
    """Stores detected ChangeRecords with supporting EvidenceRecords."""
    for chg in changes:
        existing = db.query(ChangeModel).filter(ChangeModel.change_id == chg.change_id).first()
        if existing:
            db.delete(existing)
            db.flush()

        chg_model = ChangeModel(
            change_id=chg.change_id,
            document_id=chg.document_id,
            previous_document_id=chg.previous_document_id,
            clause_id=chg.clause_id,
            change_type=chg.change_type.value if hasattr(chg.change_type, "value") else str(chg.change_type),
            previous_text=chg.previous_text,
            current_text=chg.current_text,
            previous_value=chg.previous_value if isinstance(chg.previous_value, (dict, list, str, int, float, bool, type(None))) else str(chg.previous_value),
            current_value=chg.current_value if isinstance(chg.current_value, (dict, list, str, int, float, bool, type(None))) else str(chg.current_value),
            effective_from=chg.effective_from,
            affected_groups=[g.model_dump() if hasattr(g, "model_dump") else g for g in chg.affected_groups],
            confidence=chg.confidence or 1.0,
            uncertainties=chg.uncertainties,
        )
        db.add(chg_model)

        for ev in chg.evidence:
            ev_model = EvidenceModel(
                change_id=chg.change_id,
                document_id=ev.document_id,
                clause_id=ev.clause_id,
                source_url=ev.source_url,
                exact_supporting_text=ev.exact_supporting_text,
                page_or_section=ev.page_or_section,
                is_inferred=ev.is_inferred,
                confidence=ev.confidence,
                notes=ev.notes,
            )
            db.add(ev_model)

    db.commit()


def list_changes(
    db: Session,
    document_id: Optional[str] = None,
    change_type: Optional[str] = None
) -> List[ChangeRecord]:
    """Retrieves stored change records."""
    query = db.query(ChangeModel)
    if document_id:
        query = query.filter((ChangeModel.document_id == document_id) | (ChangeModel.previous_document_id == document_id))
    if change_type:
        query = query.filter(ChangeModel.change_type == change_type)

    models = query.order_by(ChangeModel.created_at.desc()).all()
    results: List[ChangeRecord] = []
    for m in models:
        ev_records = [
            EvidenceRecord(
                document_id=e.document_id,
                clause_id=e.clause_id,
                source_url=e.source_url,
                exact_supporting_text=e.exact_supporting_text,
                page_or_section=e.page_or_section,
                is_inferred=e.is_inferred,
                confidence=e.confidence,
                notes=e.notes,
            )
            for e in m.evidence_items
        ]
        results.append(
            ChangeRecord(
                change_id=m.change_id,
                document_id=m.document_id,
                previous_document_id=m.previous_document_id,
                clause_id=m.clause_id,
                change_type=ChangeType(m.change_type) if m.change_type in ChangeType._value2member_map_ else ChangeType.UNKNOWN,
                previous_text=m.previous_text,
                current_text=m.current_text,
                previous_value=m.previous_value,
                current_value=m.current_value,
                effective_from=m.effective_from,
                affected_groups=m.affected_groups or [],
                evidence=ev_records,
                confidence=m.confidence,
                uncertainties=m.uncertainties or [],
            )
        )
    return results


def save_impact_report(db: Session, report: ImpactAnalysisReport) -> None:
    """Stores an impact analysis report."""
    existing = db.query(ImpactReportModel).filter(ImpactReportModel.report_id == report.report_id).first()
    if existing:
        db.delete(existing)
        db.flush()

    model = ImpactReportModel(
        report_id=report.report_id,
        scheme_name=report.scheme_name,
        base_document_id=report.base_document_id,
        target_document_id=report.target_document_id,
        summary=report.summary,
        explicitly_affected_groups=[g.model_dump() for g in report.explicitly_affected_groups],
        potentially_affected_groups=[g.model_dump() for g in report.potentially_affected_groups],
        unresolved_groups=[g.model_dump() for g in report.unresolved_groups],
        deterministic_deltas=report.deterministic_deltas,
        practical_consequences=report.practical_consequences,
        evidence_trail=[e.model_dump() for e in report.evidence_trail],
        generated_at=report.generated_at,
    )
    db.add(model)
    db.commit()


def get_impact_report_by_id(db: Session, report_id: str) -> Optional[ImpactAnalysisReport]:
    """Retrieves a stored impact report by ID."""
    m = db.query(ImpactReportModel).filter(ImpactReportModel.report_id == report_id).first()
    if not m:
        return None
    from shared.schemas import AffectedGroup
    return ImpactAnalysisReport(
        report_id=m.report_id,
        scheme_name=m.scheme_name,
        base_document_id=m.base_document_id,
        target_document_id=m.target_document_id,
        summary=m.summary,
        explicitly_affected_groups=[AffectedGroup(**g) for g in (m.explicitly_affected_groups or [])],
        potentially_affected_groups=[AffectedGroup(**g) for g in (m.potentially_affected_groups or [])],
        unresolved_groups=[AffectedGroup(**g) for g in (m.unresolved_groups or [])],
        deterministic_deltas=m.deterministic_deltas or [],
        practical_consequences=m.practical_consequences or [],
        evidence_trail=[EvidenceRecord(**e) for e in (m.evidence_trail or [])],
        generated_at=m.generated_at,
    )


def save_agent_audit_log(
    db: Session,
    session_id: str,
    query: str,
    direct_answer: str,
    reasoning_type: str,
    steps_taken: List[Dict[str, Any]],
    scheme_name: Optional[str] = None
) -> None:
    """Logs an agent investigation query and execution steps."""
    log = AgentAuditLogModel(
        session_id=session_id,
        query=query,
        scheme_name=scheme_name,
        direct_answer=direct_answer,
        reasoning_type=reasoning_type,
        steps_taken=steps_taken,
    )
    db.add(log)
    db.commit()


def seed_initial_corpus_if_empty(db: Session) -> int:
    """Seeds the authentic Indian policy corpus if no documents exist."""
    count = db.query(DocumentModel).count()
    if count == 0:
        logger.info("Database empty. Seeding authentic Indian Central Government Policy Corpus...")
        docs = AuthenticCorpusLoader.load_all()
        for doc in docs:
            save_document(db, doc)
        logger.info(f"Successfully seeded {len(docs)} authentic policy documents.")
        return len(docs)
    return count
