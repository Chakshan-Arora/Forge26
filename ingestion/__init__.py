"""
Policy Intel Document Ingestion Package.

Provides document extraction adapters, clause-level parsing,
authentic policy corpus loaders, and ingestion interfaces connecting
official government documents into structured Policy Intel schemas.
"""

from ingestion.extractor import PolicyDocumentExtractor
from ingestion.corpus_loader import AuthenticCorpusLoader
from ingestion.service import IngestionService

__all__ = [
    "PolicyDocumentExtractor",
    "AuthenticCorpusLoader",
    "IngestionService",
]
