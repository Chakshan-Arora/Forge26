"""
Backend Configuration for Policy Intel.

Loads environment variables, defines database connections,
API prefixes, and deployment environment settings.
"""

import os
from typing import List


class Settings:
    """Application configuration parameters."""

    PROJECT_NAME: str = "Policy Intel"
    PROJECT_DESCRIPTION: str = "AI-Powered Regulatory Intelligence Platform for Indian Central Government Education & Scholarship Policies"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # Database configuration
    # Default is SQLite for out-of-the-box zero-setup execution.
    # In production or docker, set DATABASE_URL=postgresql://user:pass@localhost:5432/policy_intel
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./policy_intel.db")

    # Security & CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*",
    ]

    # LLM Settings (optional API key for semantic expansion)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
