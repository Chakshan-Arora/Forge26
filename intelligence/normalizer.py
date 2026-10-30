"""
Regulatory Text and Financial Threshold Normalization Module.

Handles Indian legal text formatting, Indian numbering conventions
(Lakh, Crore, Rs, ₹), and deterministic financial/academic parameter extraction.
"""

from __future__ import annotations
import re
from typing import Any, Dict, List, Optional, Tuple
from shared.schemas import StructuredValue


# Word to number mapping for Indian English legal texts
NUMBER_WORDS: Dict[str, float] = {
    "one": 1.0,
    "two": 2.0,
    "three": 3.0,
    "four": 4.0,
    "five": 5.0,
    "six": 6.0,
    "seven": 7.0,
    "eight": 8.0,
    "nine": 9.0,
    "ten": 10.0,
    "fifty": 50.0,
    "sixty": 60.0,
    "seventy": 70.0,
    "eighty": 80.0,
    "ninety": 90.0,
    "hundred": 100.0,
    "thousand": 1000.0,
    "lakh": 100000.0,
    "lakhs": 100000.0,
    "lac": 100000.0,
    "lacs": 100000.0,
    "crore": 10000000.0,
    "crores": 10000000.0,
}


class RegulatoryNormalizer:
    """Normalizes regulatory clauses and extracts structured criteria deterministically."""

    @staticmethod
    def normalize_text(text: Optional[str]) -> str:
        """Standardizes whitespaces, quotes, dashes, and casing for comparison."""
        if not text:
            return ""
        
        # Replace non-breaking spaces and irregular whitespace
        t = re.sub(r"[\xa0\u2000-\u200b\s]+", " ", text)
        
        # Replace smart quotes and dashes
        t = t.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        t = t.replace("—", "-").replace("–", "-")
        
        # Standardize Indian currency symbol and variations (with word boundaries!)
        t = re.sub(r"\b(?:Rs\.?|INR)\s*", "₹ ", t, flags=re.IGNORECASE)
        t = re.sub(r"₹\s*", "₹ ", t)
        
        # Standardize 'per annum' / 'p.a.'
        t = re.sub(r"(?:\bp\.a\.|\bper\s+annum\b|\bannually\b)", "per annum", t, flags=re.IGNORECASE)
        t = re.sub(r"(?:\bp\.m\.|\bper\s+month\b|\bmonthly\b)", "per month", t, flags=re.IGNORECASE)
        
        # Collapse multiple spaces
        t = re.sub(r"\s+", " ", t)
        return t.strip()

    @staticmethod
    def normalize_clause_number(clause_num: Optional[str]) -> str:
        """
        Normalizes clause numbers (e.g. 'Clause 4.1.', 'Para 4(a)', '(4.1)')
        into standard dot/bracket hierarchy: '4.1', '4(a)'.
        """
        if not clause_num:
            return ""
        
        s = clause_num.strip()
        # Remove leading "Clause", "Para", "Paragraph", "Section", "Rule", "Article"
        s = re.sub(r"^(?:Clause|Para(?:graph)?|Section|Rule|Article|Sub-clause)\s*", "", s, flags=re.IGNORECASE)
        # Strip trailing dot, colon, hyphen
        s = re.sub(r"[\.:\-]+$", "", s).strip()
        # Strip outer brackets if wrapped completely e.g. "(4.1)" -> "4.1"
        m = re.match(r"^\(([^\)]+)\)$", s)
        if m:
            s = m.group(1).strip()
        return s

    @classmethod
    def parse_indian_amount(cls, text_snippet: str) -> Optional[float]:
        """
        Parses Indian currency numbers:
        - '₹ 2,50,000', '2,50,000/-', '250000' -> 250000.0
        - '₹ 2.50 Lakh', '2.5 lakh', '2.50 lakh' -> 250000.0
        - '₹ 8.0 Lakh', '8 lakh' -> 800000.0
        - '₹ 12,000' -> 12000.0
        - 'two lakh fifty thousand' -> 250000.0
        """
        s = cls.normalize_text(text_snippet).lower()
        
        # Pattern 1: Decimal lakh/crore e.g. "₹ 2.50 lakh", "2.5 lakhs", "8 lakh"
        lakh_pattern = re.search(r"(?:₹\s*)?(\d+(?:\.\d+)?)\s*(?:lakhs?|lacs?)", s)
        if lakh_pattern:
            return float(lakh_pattern.group(1)) * 100000.0
        
        crore_pattern = re.search(r"(?:₹\s*)?(\d+(?:\.\d+)?)\s*crores?", s)
        if crore_pattern:
            return float(crore_pattern.group(1)) * 10000000.0
            
        # Pattern 2: Comma separated Indian currency e.g. "₹ 2,50,000", "12,000/-"
        comma_pattern = re.search(r"(?:₹\s*)?(\d{1,3}(?:,\d{2,3})+)(?:\s*/-)?", s)
        if comma_pattern:
            clean_num = comma_pattern.group(1).replace(",", "")
            return float(clean_num)
            
        # Pattern 3: Plain integer with currency symbol e.g. "₹ 250000"
        currency_int_pattern = re.search(r"₹\s*(\d{4,9})", s)
        if currency_int_pattern:
            return float(currency_int_pattern.group(1))

        # Pattern 4: Words e.g. "two lakh fifty thousand"
        if "lakh" in s or "thousand" in s:
            words = re.findall(r"\b[a-z]+\b", s)
            total = 0.0
            current = 0.0
            matched = False
            for w in words:
                if w in NUMBER_WORDS:
                    val = NUMBER_WORDS[w]
                    if val in (100000.0, 10000000.0):
                        if current == 0:
                            current = 1.0
                        total += current * val
                        current = 0.0
                        matched = True
                    elif val == 1000.0:
                        if current == 0:
                            current = 1.0
                        current = current * 1000.0
                        matched = True
                    elif val == 100.0:
                        if current == 0:
                            current = 1.0
                        current = current * 100.0
                        matched = True
                    else:
                        current += val
                        matched = True
            total += current
            if matched and total > 0:
                return total

        return None

    @classmethod
    def extract_structured_values(cls, text: str) -> List[StructuredValue]:
        """
        Extracts structured financial limits, scholarship amounts, percentages,
        and ratios from legal text.
        """
        values: List[StructuredValue] = []
        clean = cls.normalize_text(text)
        
        # 1. Income Ceiling / Limit
        # Flexible match allowing "from all sources", "is not more than", "does not exceed", "up to", etc.
        income_match = re.search(
            r"(?:annual\s+)?(?:family|parental|parents\'?|guardian\'?s?)?\s*income.*?(?:ceiling|limit|exceed|more\s+than|up\s+to|below|is|@)\s*(?:of\s*)?(₹\s*[\d,\.]+(?:\s*(?:lakhs?|lacs?|crores?))?|[\d,\.]+\s*(?:lakhs?|lacs?|crores?))",
            clean,
            flags=re.IGNORECASE
        )
        if income_match:
            raw_str = income_match.group(1)
            parsed_amount = cls.parse_indian_amount(raw_str)
            if parsed_amount is not None:
                values.append(
                    StructuredValue(
                        value_type="income_ceiling",
                        raw_text=raw_str.strip(),
                        numeric_amount=parsed_amount,
                        currency="INR",
                        unit="per_annum",
                        interval_min=0.0,
                        interval_max=parsed_amount,
                        extra_attributes={"scope": "family_annual_income"}
                    )
                )

        # 2. Scholarship Rate / Maintenance Allowance
        # Example: "scholarship of ₹ 12,000 per annum" or "scholarship is ₹ 10,000 per annum at graduation level"
        scholarship_matches = re.finditer(
            r"(?:scholarship(?:\s+amount|\s+rate)?|maintenance\s+allowance|financial\s+assistance|amount\s+of)\s*(?:of|is|@)?\s*(₹\s*[\d,\.]+(?:\s*(?:lakhs?|lacs?))?|[\d,\.]+\s*(?:lakhs?|lacs?))\s*(?:(?:/|-)?\s*(per\s+annum|per\s+month|p\.a\.|p\.m\.))?",
            clean,
            flags=re.IGNORECASE
        )
        for sm in scholarship_matches:
            raw_amt = sm.group(1)
            periodicity = sm.group(2) or "per annum"
            parsed_amt = cls.parse_indian_amount(raw_amt)
            if parsed_amt is not None and parsed_amt > 0:
                # Disambiguate from income ceiling if this was already captured as income
                if not any(v.value_type == "income_ceiling" and v.numeric_amount == parsed_amt for v in values):
                    # Check if hosteller vs day scholar mentioned
                    is_hosteller = bool(re.search(r"hosteller", clean, re.IGNORECASE))
                    is_day_scholar = bool(re.search(r"day\s+scholar", clean, re.IGNORECASE))
                    beneficiary_mode = "hosteller" if is_hosteller else ("day_scholar" if is_day_scholar else "all")
                    
                    values.append(
                        StructuredValue(
                            value_type="scholarship_amount",
                            raw_text=raw_amt.strip(),
                            numeric_amount=parsed_amt,
                            currency="INR",
                            unit=cls.normalize_text(periodicity),
                            extra_attributes={"beneficiary_mode": beneficiary_mode}
                        )
                    )

        # 3. Percentage thresholds (Minimum marks / attendance)
        percentage_matches = re.finditer(
            r"(\d+(?:\.\d+)?)\s*%\s*(?:marks|attendance|aggregate)?",
            clean,
            flags=re.IGNORECASE
        )
        for pm in percentage_matches:
            pct_val = float(pm.group(1))
            # Determine context
            context_window = clean[max(0, pm.start() - 30):min(len(clean), pm.end() + 30)].lower()
            if "attendance" in context_window:
                vtype = "attendance_threshold"
            elif "marks" in context_window or "qualifying" in context_window or "aggregate" in context_window:
                vtype = "minimum_marks_threshold"
            else:
                vtype = "percentage"
            
            values.append(
                StructuredValue(
                    value_type=vtype,
                    raw_text=pm.group(0).strip(),
                    numeric_amount=pct_val,
                    currency=None,
                    unit="percent",
                    interval_min=pct_val,
                    interval_max=100.0,
                    extra_attributes={"raw_context": context_window}
                )
            )

        # 4. Central/State funding sharing ratio (e.g. "60:40", "90:10")
        ratio_match = re.search(r"\b(\d{2})\s*:\s*(\d{2})\b", clean)
        if ratio_match:
            r1, r2 = float(ratio_match.group(1)), float(ratio_match.group(2))
            if r1 + r2 == 100.0:
                values.append(
                    StructuredValue(
                        value_type="funding_ratio",
                        raw_text=f"{int(r1)}:{int(r2)}",
                        numeric_amount=r1,
                        currency=None,
                        unit="ratio",
                        extra_attributes={"central_share": r1, "state_share": r2}
                    )
                )

        return values
