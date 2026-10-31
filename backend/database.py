"""
Database configuration and session management for Policy Intel.

Supports PostgreSQL in production environments and SQLite for seamless
local development and zero-dependency automated testing.
"""

import logging
from typing import Generator
from sqlalchemy import create_engine, text as sa_text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from backend.config import settings

logger = logging.getLogger(__name__)

# Configure engine arguments based on dialect
engine_kwargs = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency to provide a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(seed_corpus: bool = True) -> None:
    """
    Initializes database tables and optionally seeds the authentic
    Indian Central Government policy corpus.
    """
    import backend.models  # Ensure models are registered with Base
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    # Ensure verification_status column exists in SQLite if created earlier
    with engine.connect() as conn:
        try:
            conn.execute(sa_text("ALTER TABLE documents ADD COLUMN verification_status VARCHAR(64) DEFAULT 'UNVERIFIED'"))
            conn.commit()
        except Exception:
            pass

    if seed_corpus:
        from backend.services.persistence_service import seed_initial_corpus_if_empty
        with SessionLocal() as db:
            seed_initial_corpus_if_empty(db)
