"""
Tests for RegulatoryNormalizer and Indian currency/number parsing.
"""

import pytest
from intelligence.normalizer import RegulatoryNormalizer


def test_normalize_text():
    raw = "  Clause 4.1.\xa0\xa0Scholarships   shall be paid @ Rs. 2,50,000/- p.a.  "
    norm = RegulatoryNormalizer.normalize_text(raw)
    assert "₹ 2,50,000/- per annum" in norm
    assert "  " not in norm


def test_normalize_clause_number():
    assert RegulatoryNormalizer.normalize_clause_number("Clause 4.1.") == "4.1"
    assert RegulatoryNormalizer.normalize_clause_number("Para 4(a):") == "4(a)"
    assert RegulatoryNormalizer.normalize_clause_number("(4.1.2)") == "4.1.2"
    assert RegulatoryNormalizer.normalize_clause_number("Section 3") == "3"


def test_parse_indian_amount_lakhs():
    assert RegulatoryNormalizer.parse_indian_amount("₹ 2.50 Lakh") == 250000.0
    assert RegulatoryNormalizer.parse_indian_amount("2.5 lakh") == 250000.0
    assert RegulatoryNormalizer.parse_indian_amount("Rs. 8.0 Lakhs") == 800000.0
    assert RegulatoryNormalizer.parse_indian_amount("1.5 lakh") == 150000.0
    assert RegulatoryNormalizer.parse_indian_amount("3.5 Lakhs") == 350000.0


def test_parse_indian_amount_comma_notation():
    assert RegulatoryNormalizer.parse_indian_amount("₹ 2,50,000/-") == 250000.0
    assert RegulatoryNormalizer.parse_indian_amount("Rs 12,000") == 12000.0
    assert RegulatoryNormalizer.parse_indian_amount("6,00,000") == 600000.0


def test_parse_indian_amount_words():
    assert RegulatoryNormalizer.parse_indian_amount("two lakh fifty thousand") == 250000.0
    assert RegulatoryNormalizer.parse_indian_amount("one lakh fifty thousand") == 150000.0


def test_extract_structured_values_income():
    text = "Students whose annual family income from all sources does not exceed ₹ 2,50,000/- per annum are eligible."
    vals = RegulatoryNormalizer.extract_structured_values(text)
    assert len(vals) >= 1
    income_val = next(v for v in vals if v.value_type == "income_ceiling")
    assert income_val.numeric_amount == 250000.0
    assert income_val.unit == "per_annum"
    assert income_val.interval_max == 250000.0


def test_extract_structured_values_scholarship():
    text = "The scholarship rate is ₹ 12,000 per annum for hostellers."
    vals = RegulatoryNormalizer.extract_structured_values(text)
    sch_val = next(v for v in vals if v.value_type == "scholarship_amount")
    assert sch_val.numeric_amount == 12000.0
    assert sch_val.extra_attributes.get("beneficiary_mode") == "hosteller"


def test_extract_structured_values_percentage_and_ratio():
    text = "Minimum 55% marks required for renewal with 75% attendance. Central-State share is 60:40."
    vals = RegulatoryNormalizer.extract_structured_values(text)
    types = [v.value_type for v in vals]
    assert "minimum_marks_threshold" in types
    assert "attendance_threshold" in types
    assert "funding_ratio" in types

    ratio_val = next(v for v in vals if v.value_type == "funding_ratio")
    assert ratio_val.extra_attributes.get("central_share") == 60.0
    assert ratio_val.extra_attributes.get("state_share") == 40.0
