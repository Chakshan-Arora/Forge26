"""
Impact Analysis API Endpoints.

Computes multi-dimensional student impact, eligibility delta shifts, and practical actions.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from shared.schemas import ImpactAnalysisReport, ImpactRequest
from backend.services.persistence_service import get_impact_report_by_id
from backend.services.intelligence_service import IntelligenceService

router = APIRouter(prefix="/impact", tags=["Impact Analysis"])


@router.post("/analyze", response_model=ImpactAnalysisReport)
def analyze_policy_impact(
    payload: ImpactRequest,
    db: Session = Depends(get_db)
):
    """
    Executes student cohort impact analysis between a baseline policy and an amendment.
    Identifies explicitly affected groups, deterministic eligibility deltas, and practical consequences.
    """
    intel = IntelligenceService.get_instance()
    try:
        report = intel.analyze_impact(
            target_document_id=payload.target_document_id,
            base_document_id=payload.base_document_id,
            db=db
        )
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Impact analysis failed: {str(e)}"
        )


@router.get("/{analysis_id}", response_model=ImpactAnalysisReport)
def get_impact_report(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves a previously computed impact report by its report ID."""
    report = get_impact_report_by_id(db, analysis_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Impact report with ID '{analysis_id}' not found."
        )
    return report
