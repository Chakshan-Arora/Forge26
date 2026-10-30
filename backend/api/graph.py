"""
Regulatory Knowledge Graph API Endpoints.

Provides network graph exports and subgraph queries for Schemes,
Documents, Clauses, Beneficiary Groups, and Amendments.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.intelligence_service import IntelligenceService

router = APIRouter(prefix="/graph", tags=["Knowledge Graph"])


@router.get("")
def get_graph(
    format: str = Query("json", description="Export format: 'json' or 'mermaid'"),
    db: Session = Depends(get_db)
):
    """
    Returns the temporal regulatory knowledge graph.
    Supports JSON for interactive graph visualizers (React Flow) and Mermaid for diagrams.
    """
    intel = IntelligenceService.get_instance()
    intel.initialize(db)

    if format.lower() == "mermaid":
        mermaid_code = intel.engine.export_graph_mermaid()
        return {"format": "mermaid", "data": mermaid_code}

    graph_dict = intel.get_knowledge_graph_data(db)
    return {
        "format": "json",
        "nodes": graph_dict.get("nodes", []),
        "edges": graph_dict.get("edges", []),
        "node_count": len(graph_dict.get("nodes", [])),
        "edge_count": len(graph_dict.get("edges", [])),
    }


@router.get("/{entity_id}")
def get_entity_subgraph(
    entity_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns the immediate local subgraph (connected neighbors)
    for a specific Scheme, Policy Document, or Clause.
    """
    intel = IntelligenceService.get_instance()
    subgraph = intel.get_subgraph_data(entity_id=entity_id, db=db)
    if not subgraph.get("nodes"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity '{entity_id}' not found in the regulatory knowledge graph."
        )
    return subgraph
