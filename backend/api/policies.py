"""
Policies API Endpoints.

Provides scheme-level aggregations, version timelines, and lineage tracing.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from shared.schemas import Document
from backend.services.persistence_service import list_documents, get_document_by_id
from backend.services.intelligence_service import IntelligenceService

router = APIRouter(prefix="/policies", tags=["Policies"])


@router.get("", response_model=List[Dict[str, Any]])
def get_schemes(db: Session = Depends(get_db)):
    """
    Returns unique government education schemes registered in the platform,
    along with their current active guidelines, issuing ministry, and version count.
    """
    all_docs = list_documents(db)
    schemes_map: Dict[str, Dict[str, Any]] = {}

    for doc in all_docs:
        s_name = doc.scheme_name
        if s_name not in schemes_map:
            schemes_map[s_name] = {
                "scheme_name": s_name,
                "ministry": doc.ministry,
                "total_documents": 0,
                "versions": [],
                "active_version": None,
                "latest_publication_date": None,
                "portal_url": doc.source_url,
            }
        
        info = schemes_map[s_name]
        info["total_documents"] += 1
        info["versions"].append({
            "document_id": doc.id,
            "version": doc.version,
            "document_type": doc.document_type.value if hasattr(doc.document_type, "value") else str(doc.document_type),
            "status": doc.status,
            "publication_date": doc.publication_date,
            "effective_date": doc.effective_date,
            "clause_count": len(doc.clauses),
        })

        if doc.status == "ACTIVE" or info["active_version"] is None:
            info["active_version"] = doc.version
            info["latest_publication_date"] = doc.publication_date

    return list(schemes_map.values())


@router.get("/{policy_id}")
def get_policy_or_scheme(policy_id: str, db: Session = Depends(get_db)):
    """Retrieves document details if policy_id matches a Document, or scheme history if scheme name."""
    doc = get_document_by_id(db, policy_id)
    if doc:
        return doc

    # Check if policy_id matches a scheme name
    scheme_docs = list_documents(db, scheme_name=policy_id)
    if not scheme_docs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No policy or scheme found matching '{policy_id}'."
        )
    return {
        "scheme_name": policy_id,
        "documents": scheme_docs,
        "count": len(scheme_docs)
    }


@router.get("/{policy_id}/history")
def get_policy_history(policy_id: str, db: Session = Depends(get_db)):
    """
    Returns the chronological regulatory lineage, revisions, and amendments
    for a given scholarship scheme or document.
    """
    doc = get_document_by_id(db, policy_id)
    scheme_name = doc.scheme_name if doc else policy_id

    docs = list_documents(db, scheme_name=scheme_name)
    if not docs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No history records found for scheme '{scheme_name}'."
        )

    # Sort chronologically
    docs.sort(key=lambda d: d.publication_date or d.effective_date or "")

    timeline = []
    for d in docs:
        timeline.append({
            "document_id": d.id,
            "title": d.title,
            "version": d.version,
            "document_type": d.document_type.value if hasattr(d.document_type, "value") else str(d.document_type),
            "order_number": d.order_number,
            "publication_date": d.publication_date,
            "effective_date": d.effective_date,
            "valid_until": d.valid_until,
            "status": d.status,
            "source_url": d.source_url,
            "clause_count": len(d.clauses),
        })

    return {
        "scheme_name": scheme_name,
        "timeline_events": timeline,
        "total_versions": len(timeline),
    }
