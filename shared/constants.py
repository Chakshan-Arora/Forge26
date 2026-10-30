"""
Shared constants for Policy Intel.

Defines standard regulatory authorities, ministries, document types,
default confidence thresholds, and system constants across all modules.
"""

from typing import List, Dict

# Standard Government Ministries
MINISTRY_MOSJE = "Ministry of Social Justice and Empowerment"
MINISTRY_MOE = "Ministry of Education"
MINISTRY_MOTA = "Ministry of Tribal Affairs"
MINISTRY_MOMA = "Ministry of Minority Affairs"

OFFICIAL_MINISTRIES: List[str] = [
    MINISTRY_MOSJE,
    MINISTRY_MOE,
    MINISTRY_MOTA,
    MINISTRY_MOMA,
]

# Standard Flagship Schemes
SCHEME_PMS_SC = "Post-Matric Scholarship for SC Students"
SCHEME_NMMSS = "National Means-cum-Merit Scholarship Scheme"
SCHEME_PM_USP_CSSS = "Central Sector Scheme of Scholarships for College and University Students"

SUPPORTED_SCHEMES: List[str] = [
    SCHEME_PMS_SC,
    SCHEME_NMMSS,
    SCHEME_PM_USP_CSSS,
]

# Scheme Portal URLs
OFFICIAL_PORTALS: Dict[str, str] = {
    SCHEME_PMS_SC: "https://socialjustice.gov.in/schemes/post-matric-scholarship-sc",
    SCHEME_NMMSS: "https://scholarships.gov.in",
    SCHEME_PM_USP_CSSS: "https://www.education.gov.in/scholarships-education-loan-0",
}

# Ingestion & Processing Status
STATUS_PENDING = "PENDING"
STATUS_PROCESSING = "PROCESSING"
STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED = "FAILED"

# Verification & Confidence Levels
HIGH_CONFIDENCE_THRESHOLD = 0.85
MEDIUM_CONFIDENCE_THRESHOLD = 0.60
LOW_CONFIDENCE_THRESHOLD = 0.40

# Regulatory Decision Distinctions
REASONING_FACTUAL = "RETRIEVED_FACT"
REASONING_DETERMINISTIC = "DETERMINISTIC_CALCULATION"
REASONING_INFERRED = "AI_INFERRED_INTERPRETATION"
REASONING_UNRESOLVED = "UNRESOLVED_AMBIGUITY"
