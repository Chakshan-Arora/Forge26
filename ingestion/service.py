"""
Document Ingestion Service.

Coordinates document acquisition from Person 1's pipelines,
validates against Pydantic schemas, and handles ingestion into
both persistent storage and the regulatory intelligence engine.
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any
from shared.schemas import Document, DocumentIngestRequest, DocumentType
from ingestion.extractor import PolicyDocumentExtractor
from ingestion.corpus_loader import AuthenticCorpusLoader


class IngestionService:
    """Service handling document intake, schema enforcement, and parsing."""

    def __init__(self, extractor: Optional[PolicyDocumentExtractor] = None):
        self.extractor = extractor or PolicyDocumentExtractor()

    def process_ingest_request(self, req: DocumentIngestRequest) -> Document:
        """
        Processes an ingestion request.
        If a pre-structured Document was provided by Person 1, it is validated and used.
        Otherwise, raw text is parsed into structured clauses using PolicyDocumentExtractor.
        """
        if req.structured_document:
            return req.structured_document

        if not req.raw_text:
            raise ValueError("Either 'structured_document' or 'raw_text' must be provided.")

        return self.extractor.extract_from_text(
            raw_text=req.raw_text,
            title=f"Notification: {req.scheme_name}",
            scheme_name=req.scheme_name,
            ministry=req.ministry,
            document_type=req.document_type,
            order_number=req.order_number,
            publication_date=req.publication_date,
            effective_date=req.effective_date,
            source_url=req.source_url,
            version=req.version or "1.0",
            status="ACTIVE"
        )

    def load_initial_corpus(self) -> List[Document]:
        """Loads the official authentic central government policy corpus."""
        return AuthenticCorpusLoader.load_all()
