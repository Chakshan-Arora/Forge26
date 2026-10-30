"""
SQLAlchemy ORM Models for Policy Intel.

Persists Documents, Clauses, Changes, Evidence, Impact Analysis Reports,
and Agent Audit Logs, preserving full traceability to original government records.
"""

from __future__ import annotations
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    Text,
    JSON,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from backend.database import Base


class DocumentModel(Base):
    """Stores official government policy documents and guidelines."""

    __tablename__ = "documents"

    id = Column(String(128), primary_key=True, index=True)
    title = Column(String(512), nullable=False)
    scheme_name = Column(String(256), nullable=False, index=True)
    ministry = Column(String(256), nullable=False, index=True)
    document_type = Column(String(64), nullable=False, index=True)
    order_number = Column(String(128), nullable=True)
    publication_date = Column(String(32), nullable=True, index=True)
    effective_date = Column(String(32), nullable=True, index=True)
    valid_until = Column(String(32), nullable=True)
    source_url = Column(String(512), nullable=True)
    version = Column(String(32), default="1.0")
    status = Column(String(32), default="ACTIVE", index=True)
    verification_status = Column(String(64), default="UNVERIFIED", index=True)
    references_json = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    clauses = relationship("ClauseModel", back_populates="document", cascade="all, delete-orphan", lazy="joined")

    __table_args__ = (
        Index("idx_doc_scheme_version", "scheme_name", "version"),
    )


class ClauseModel(Base):
    """Stores individual structured clauses from a document."""

    __tablename__ = "clauses"

    id = Column(String(128), primary_key=True, index=True)
    document_id = Column(String(128), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    clause_number = Column(String(64), nullable=False)
    title = Column(String(256), nullable=True)
    section = Column(String(256), nullable=True)
    text = Column(Text, nullable=False)
    normalized_text = Column(Text, nullable=True)
    clause_type = Column(String(64), default="GENERAL", index=True)
    structured_attributes = Column(JSON, default=dict)
    page_number = Column(Integer, nullable=True)
    subclauses = Column(JSON, default=list)

    # Relationships
    document = relationship("DocumentModel", back_populates="clauses")


class ChangeModel(Base):
    """Stores detected regulatory changes between policy versions."""

    __tablename__ = "changes"

    change_id = Column(String(128), primary_key=True, index=True)
    document_id = Column(String(128), nullable=False, index=True)
    previous_document_id = Column(String(128), nullable=True, index=True)
    clause_id = Column(String(128), nullable=False, index=True)
    change_type = Column(String(64), nullable=False, index=True)
    previous_text = Column(Text, nullable=True)
    current_text = Column(Text, nullable=True)
    previous_value = Column(JSON, nullable=True)
    current_value = Column(JSON, nullable=True)
    effective_from = Column(String(32), nullable=True)
    affected_groups = Column(JSON, default=list)
    confidence = Column(Float, default=1.0)
    uncertainties = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Evidence linkage
    evidence_items = relationship("EvidenceModel", back_populates="change", cascade="all, delete-orphan", lazy="joined")


class EvidenceModel(Base):
    """Stores verifiable evidence citations for legal findings and changes."""

    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    change_id = Column(String(128), ForeignKey("changes.change_id", ondelete="CASCADE"), nullable=True, index=True)
    document_id = Column(String(128), nullable=False, index=True)
    clause_id = Column(String(128), nullable=True, index=True)
    source_url = Column(String(512), nullable=True)
    exact_supporting_text = Column(Text, nullable=False)
    page_or_section = Column(String(128), nullable=True)
    is_inferred = Column(Boolean, default=False)
    confidence = Column(Float, default=1.0)
    notes = Column(Text, nullable=True)

    # Relationships
    change = relationship("ChangeModel", back_populates="evidence_items")


class ImpactReportModel(Base):
    """Stores generated student impact analysis reports."""

    __tablename__ = "impact_reports"

    report_id = Column(String(128), primary_key=True, index=True)
    scheme_name = Column(String(256), nullable=False, index=True)
    base_document_id = Column(String(128), nullable=True)
    target_document_id = Column(String(128), nullable=False, index=True)
    summary = Column(Text, nullable=False)
    explicitly_affected_groups = Column(JSON, default=list)
    potentially_affected_groups = Column(JSON, default=list)
    unresolved_groups = Column(JSON, default=list)
    deterministic_deltas = Column(JSON, default=list)
    practical_consequences = Column(JSON, default=list)
    evidence_trail = Column(JSON, default=list)
    generated_at = Column(String(64), nullable=False)


class AgentAuditLogModel(Base):
    """Stores full audit logs for AI regulatory investigation queries."""

    __tablename__ = "agent_audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(128), nullable=False, index=True)
    query = Column(Text, nullable=False)
    scheme_name = Column(String(256), nullable=True)
    direct_answer = Column(Text, nullable=False)
    reasoning_type = Column(String(64), nullable=False)
    steps_taken = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
