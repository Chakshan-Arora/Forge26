"""
Documents API Endpoints.

Handles document discovery, detailed clause inspection, and ingestion.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.database import get_db
from shared.schemas import Document, DocumentIngestRequest
from backend.services.persistence_service import (
    list_documents,
    get_document_by_id,
    save_document,
)
from backend.services.intelligence_service import IntelligenceService
from ingestion.service import IngestionService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=List[Document])
def get_documents(
    scheme_name: Optional[str] = Query(None, description="Filter by scheme name"),
    ministry: Optional[str] = Query(None, description="Filter by issuing ministry"),
    document_type: Optional[str] = Query(None, description="Filter by document type (e.g. GUIDELINES, NOTIFICATION)"),
    db: Session = Depends(get_db)
):
    """Retrieves all registered policy documents matching optional criteria."""
    return list_documents(db, scheme_name=scheme_name, ministry=ministry, document_type=document_type)


@router.get("/{document_id}", response_model=Document)
def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves full details and clauses of a single document by its ID."""
    doc = get_document_by_id(db, document_id)
    if not doc:
        # Fallback to intelligence engine in-memory registry
        intel = IntelligenceService.get_instance()
        doc = intel.engine.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found."
        )
    return doc


@router.post("/ingest", response_model=Document, status_code=status.HTTP_201_CREATED)
def ingest_document(
    payload: DocumentIngestRequest,
    db: Session = Depends(get_db)
):
    """
    Ingests a new policy document or notification.
    Accepts either pre-structured Document or raw notification text for parsing.
    """
    ingestion_service = IngestionService()
    try:
        doc = ingestion_service.process_ingest_request(payload)
        # Persist to database
        save_document(db, doc)
        # Register in intelligence engine
        intel = IntelligenceService.get_instance()
        intel.register_document(doc)
        return doc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to ingest document: {str(e)}"
        )
