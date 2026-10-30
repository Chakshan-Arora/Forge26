"""
Changes API Endpoints.

Handles clause-level change detection, historical diffing, and change inspections.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.database import get_db
from shared.schemas import ChangeRecord, CompareRequest
from backend.services.persistence_service import list_changes
from backend.services.intelligence_service import IntelligenceService

router = APIRouter(prefix="/changes", tags=["Changes"])


@router.get("", response_model=List[ChangeRecord])
def get_changes(
    document_id: Optional[str] = Query(None, description="Filter changes by document ID"),
    change_type: Optional[str] = Query(None, description="Filter by ChangeType (ADDED, MODIFIED, etc.)"),
    db: Session = Depends(get_db)
):
    """Retrieves detected clause-level changes from the persistent repository."""
    return list_changes(db, document_id=document_id, change_type=change_type)


@router.get("/{change_id}", response_model=ChangeRecord)
def get_change(
    change_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves a single detected change record with complete supporting evidence."""
    changes = list_changes(db)
    for c in changes:
        if c.change_id == change_id:
            return c
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"ChangeRecord with ID '{change_id}' not found."
    )


@router.post("/compare")
def compare_policies(
    payload: CompareRequest,
    db: Session = Depends(get_db)
):
    """
    Executes an on-demand, clause-level comparison between two policy revisions.
    Returns detected changes, statistical summary, and persists findings.
    """
    intel = IntelligenceService.get_instance()
    try:
        changes, summary = intel.compare_documents(
            target_document_id=payload.target_document_id,
            base_document_id=payload.base_document_id,
            db=db
        )
        return {
            "target_document_id": payload.target_document_id,
            "base_document_id": payload.base_document_id,
            "summary": summary,
            "changes": changes,
            "change_count": len(changes),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Comparison failed: {str(e)}"
        )
