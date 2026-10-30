"""
Tests for EvidenceEngine: strict validation, provenance tracking, and error handling.
"""

import pytest
from shared.schemas import Clause, Document, DocumentType, EvidenceRecord
from intelligence.evidence_engine import EvidenceEngine, EvidenceMissingError


def test_create_and_validate_evidence():
    ev = EvidenceEngine.create_evidence(
        document_id="DOC-1",
        exact_supporting_text="Income shall not exceed ₹ 2.50 lakh per annum.",
        clause_id="CL-4.1",
        is_inferred=False,
        confidence=0.95
    )
    assert ev.document_id == "DOC-1"
    assert ev.is_inferred is False
    assert ev.confidence == 0.95

    assert EvidenceEngine.validate_records([ev]) is True


def test_missing_evidence_raises_error():
    with pytest.raises(EvidenceMissingError):
        EvidenceEngine.create_evidence(
            document_id="DOC-1",
            exact_supporting_text="" # Empty evidence must fail!
        )

    with pytest.raises(EvidenceMissingError):
        EvidenceEngine.validate_records([], context_description="Empty claim test")


def test_verbatim_quote_verification():
    full_text = "The Central Government share of the scholarship shall be disbursed directly into beneficiary bank accounts."
    valid_quote = "disbursed directly into beneficiary bank accounts"
    invalid_quote = "disbursed through cash cheques"

    assert EvidenceEngine.verify_verbatim_quote(full_text, valid_quote) is True
    assert EvidenceEngine.verify_verbatim_quote(full_text, invalid_quote) is False
