"""
Authentic Government Policy Corpus Loader.

Provides access to real, authentic Indian Central Government education
and scholarship guidelines from the Ministry of Education (MoE) and
the Ministry of Social Justice and Empowerment (MoSJE).
"""

from typing import List, Dict, Optional
from shared.schemas import Document
from data.real_policies.policy_corpus import (
    get_pmssc_2018_document,
    get_pmssc_2020_document,
    get_nmmss_2017_document,
    get_nmmss_2022_document,
    get_pmusp_csss_2015_document,
    get_pmusp_csss_2022_document,
)


class AuthenticCorpusLoader:
    """Loads and organizes official government scholarship documents."""

    @classmethod
    def load_all(cls) -> List[Document]:
        """Loads all authentic Indian central policy documents."""
        return [
            get_pmssc_2018_document(),
            get_pmssc_2020_document(),
            get_nmmss_2017_document(),
            get_nmmss_2022_document(),
            get_pmusp_csss_2015_document(),
            get_pmusp_csss_2022_document(),
        ]

    @classmethod
    def load_by_scheme(cls, scheme_name: str) -> List[Document]:
        """Returns documents belonging to a particular scholarship scheme."""
        all_docs = cls.load_all()
        s_lower = scheme_name.lower()
        return [
            d for d in all_docs
            if s_lower in d.scheme_name.lower() or any(w in d.scheme_name.lower() for w in s_lower.split())
        ]

    @classmethod
    def load_document_by_id(cls, document_id: str) -> Optional[Document]:
        """Fetches an authentic document by its unique identifier."""
        for d in cls.load_all():
            if d.id == document_id:
                return d
        return None
