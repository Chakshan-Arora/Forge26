"""
Policy Intel - FastAPI Application Entry Point.

Connects document acquisition, intelligence engine reasoning,
state persistence, and agentic investigation workflows.
"""

from __future__ import annotations
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import init_db, get_db
from backend.services.intelligence_service import IntelligenceService
from backend.api import documents, policies, changes, impact, graph, agent
from backend.services.persistence_service import list_documents, list_changes

# Logging setup
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("policy_intel")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event handler for database and intelligence engine setup."""
    logger.info("Initializing Policy Intel Backend...")
    # Initialize DB schema & seed authentic corpus
    init_db(seed_corpus=True)
    # Prime intelligence engine with authentic corpus and compute KG edges
    intel = IntelligenceService.get_instance()
    intel.initialize()
    logger.info("Policy Intel Backend successfully started.")
    yield
    logger.info("Shutting down Policy Intel Backend...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(documents.router, prefix=settings.API_PREFIX)
app.include_router(policies.router, prefix=settings.API_PREFIX)
app.include_router(changes.router, prefix=settings.API_PREFIX)
app.include_router(impact.router, prefix=settings.API_PREFIX)
app.include_router(graph.router, prefix=settings.API_PREFIX)
app.include_router(agent.router, prefix=settings.API_PREFIX)


@app.get("/api/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """Health check validating database connectivity and intelligence engine readiness."""
    intel = IntelligenceService.get_instance()
    doc_count = len(intel.engine.list_documents())
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "connected",
        "registered_documents": doc_count,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/api/stats", tags=["System"])
def system_stats(db: Session = Depends(get_db)):
    """Summary metrics of documents, detected changes, and active schemes."""
    docs = list_documents(db)
    changes = list_changes(db)
    schemes = list({d.scheme_name for d in docs})
    intel = IntelligenceService.get_instance()
    kg_data = intel.get_knowledge_graph_data(db)

    return {
        "total_documents": len(docs),
        "total_schemes": len(schemes),
        "total_changes_detected": len(changes),
        "knowledge_graph_nodes": len(kg_data.get("nodes", [])),
        "knowledge_graph_edges": len(kg_data.get("edges", [])),
        "active_schemes": schemes,
    }


# Mount frontend production build if available (must be mounted after all API routes)
import os
from fastapi.staticfiles import StaticFiles

frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
