"""
Impact Analysis Module.

Analyzes policy changes to determine affected student cohorts across:
- Education levels (UG, PG, Higher Secondary, Professional)
- Income brackets (deterministic interval calculation: newly eligible / newly excluded)
- Social and special eligibility categories (SC, ST, OBC, Divyang, etc.)
- Applicant status (Fresh vs Renewal candidates)
- Educational institution types (Government, Aided, Private Unaided, Premier)

Distinguishes:
1. Explicitly affected groups
2. Deterministic potential eligibility changes
3. Groups where impact is unresolved / ambiguous
"""

from __future__ import annotations
from datetime import datetime
import re
import uuid
from typing import Any, Dict, List, Optional, Tuple

from shared.schemas import (
    AffectedGroup,
    ChangeRecord,
    Document,
    EvidenceRecord,
    ImpactAnalysisReport,
)
from intelligence.evidence_engine import EvidenceEngine


class ImpactAnalyzer:
    """Calculates student impact and practical consequences from regulatory changes."""

    # Keywords for explicit group detection
    EDUCATION_LEVEL_KEYWORDS = {
        "undergraduate": ("Undergraduate (UG) Students", "education_level"),
        "graduation": ("Undergraduate (UG) Students", "education_level"),
        "postgraduate": ("Postgraduate (PG) Students", "education_level"),
        "post-graduate": ("Postgraduate (PG) Students", "education_level"),
        "higher secondary": ("Higher Secondary (Class 11-12) Students", "education_level"),
        "class 11": ("Higher Secondary (Class 11-12) Students", "education_level"),
        "class 9": ("Secondary (Class 9-10) Students", "education_level"),
        "professional": ("Professional & Technical Degree Students", "education_level"),
        "engineering": ("Engineering & Technical Students", "education_level"),
        "medical": ("Medical & Allied Sciences Students", "education_level"),
        "ph.d": ("Doctoral / Research Scholars", "education_level"),
    }

    SOCIAL_CATEGORY_KEYWORDS = {
        "scheduled caste": ("Scheduled Caste (SC) Beneficiaries", "social_category"),
        " sc ": ("Scheduled Caste (SC) Beneficiaries", "social_category"),
        "scheduled tribe": ("Scheduled Tribe (ST) Beneficiaries", "social_category"),
        " st ": ("Scheduled Tribe (ST) Beneficiaries", "social_category"),
        "other backward classes": ("Other Backward Classes (OBC) Beneficiaries", "social_category"),
        " obc ": ("Other Backward Classes (OBC) Beneficiaries", "social_category"),
        "economically backward": ("Economically Backward Classes (EBC)", "social_category"),
        "de-notified": ("De-Notified Nomadic Tribes (DNT)", "social_category"),
        "divyang": ("Persons with Disabilities (Divyangjan)", "social_category"),
        "disabilities": ("Persons with Disabilities (Divyangjan)", "social_category"),
        "girl": ("Female Students / Girl Child", "social_category"),
    }

    APPLICANT_STATUS_KEYWORDS = {
        "fresh": ("Fresh / New Applicants", "applicant_status"),
        "renewal": ("Renewal Applicants", "applicant_status"),
        "existing beneficiary": ("Existing Enrolled Beneficiaries", "applicant_status"),
    }

    INSTITUTION_KEYWORDS = {
        "government college": ("Government College Students", "institution_type"),
        "government aided": ("Government-Aided Institution Students", "institution_type"),
        "private unaided": ("Private Unaided Institution Students", "institution_type"),
        "central university": ("Central University Students", "institution_type"),
        "premier": ("Premier Centrally Funded Institutions (IIT/NIT/IIM/AIIMS)", "institution_type"),
        "naac": ("Students in NAAC Accredited Institutions", "institution_type"),
    }

    @classmethod
    def _detect_explicit_groups(
        cls,
        text: str,
        evidence: List[EvidenceRecord]
    ) -> List[AffectedGroup]:
        """Identifies groups explicitly mentioned in policy text."""
        detected: Dict[str, AffectedGroup] = {}
        t_lower = f" {text.lower()} "

        # Scan all category maps
        all_maps = [
            cls.EDUCATION_LEVEL_KEYWORDS,
            cls.SOCIAL_CATEGORY_KEYWORDS,
            cls.APPLICANT_STATUS_KEYWORDS,
            cls.INSTITUTION_KEYWORDS,
        ]

        for mapping in all_maps:
            for kw, (grp_name, cat_type) in mapping.items():
                if kw in t_lower and grp_name not in detected:
                    detected[grp_name] = AffectedGroup(
                        group_name=grp_name,
                        category_type=cat_type,
                        impact_nature="EXPLICITLY_AFFECTED",
                        details=f"Explicitly designated in regulatory text under keyword '{kw.strip()}'.",
                        criteria_delta=None,
                        evidence=evidence
                    )

        return list(detected.values())

    @classmethod
    def _calculate_income_delta_impact(
        cls,
        change: ChangeRecord
    ) -> Tuple[Optional[AffectedGroup], Optional[Dict[str, Any]]]:
        """
        Calculates deterministic interval changes for income ceilings.
        E.g. Prev = 200,000, Curr = 250,000 -> Newly eligible: (200000, 250000].
        """
        prev_val = change.previous_value or {}
        curr_val = change.current_value or {}

        # Check if both represent income limits
        p_type = prev_val.get("value_type")
        c_type = curr_val.get("value_type")
        
        if p_type == "income_ceiling" and c_type == "income_ceiling":
            p_amt = prev_val.get("numeric_amount")
            c_amt = curr_val.get("numeric_amount")
            if p_amt is not None and c_amt is not None and p_amt != c_amt:
                if c_amt > p_amt:
                    # Income ceiling increased -> Newly eligible interval
                    grp_name = f"Students with Annual Family Income ₹{p_amt:,.0f} to ₹{c_amt:,.0f}"
                    delta_info = {
                        "type": "INCOME_CEILING_RELAXATION",
                        "previous_limit": p_amt,
                        "current_limit": c_amt,
                        "newly_eligible_interval": {"min_exclusive": p_amt, "max_inclusive": c_amt},
                        "expansion_amount": c_amt - p_amt
                    }
                    grp = AffectedGroup(
                        group_name=grp_name,
                        category_type="income_level",
                        impact_nature="POTENTIALLY_ELIGIBLE",
                        details=(
                            f"Annual family income ceiling relaxed from ₹{p_amt:,.0f} to ₹{c_amt:,.0f}. "
                            f"Cohorts earning in the interval (₹{p_amt:,.0f}, ₹{c_amt:,.0f}] become newly eligible."
                        ),
                        criteria_delta=delta_info,
                        evidence=change.evidence
                    )
                    return grp, delta_info
                else:
                    # Income ceiling tightened -> Newly excluded interval
                    grp_name = f"Students with Annual Family Income ₹{c_amt:,.0f} to ₹{p_amt:,.0f}"
                    delta_info = {
                        "type": "INCOME_CEILING_RESTRICTION",
                        "previous_limit": p_amt,
                        "current_limit": c_amt,
                        "newly_excluded_interval": {"min_exclusive": c_amt, "max_inclusive": p_amt},
                        "reduction_amount": p_amt - c_amt
                    }
                    grp = AffectedGroup(
                        group_name=grp_name,
                        category_type="income_level",
                        impact_nature="POTENTIALLY_EXCLUDED",
                        details=(
                            f"Annual family income ceiling lowered from ₹{p_amt:,.0f} to ₹{c_amt:,.0f}. "
                            f"Students with income between ₹{c_amt:,.0f} and ₹{p_amt:,.0f} are no longer eligible."
                        ),
                        criteria_delta=delta_info,
                        evidence=change.evidence
                    )
                    return grp, delta_info

        return None, None

    @classmethod
    def _calculate_percentage_delta_impact(
        cls,
        change: ChangeRecord
    ) -> Tuple[Optional[AffectedGroup], Optional[Dict[str, Any]]]:
        """Calculates deterministic impact on marks or attendance changes."""
        prev_val = change.previous_value or {}
        curr_val = change.current_value or {}
        p_type = prev_val.get("value_type")
        c_type = curr_val.get("value_type")

        if p_type in ("minimum_marks_threshold", "attendance_threshold") and c_type == p_type:
            p_amt = prev_val.get("numeric_amount")
            c_amt = curr_val.get("numeric_amount")
            if p_amt is not None and c_amt is not None and p_amt != c_amt:
                label = "Minimum Marks" if "marks" in p_type else "Attendance"
                if c_amt > p_amt:
                    # More stringent criterion
                    grp_name = f"Students with {label} between {p_amt:.1f}% and {c_amt:.1f}%"
                    delta_info = {
                        "type": f"{p_type.upper()}_INCREASED",
                        "previous_threshold": p_amt,
                        "current_threshold": c_amt,
                        "at_risk_interval": {"min_inclusive": p_amt, "max_exclusive": c_amt}
                    }
                    grp = AffectedGroup(
                        group_name=grp_name,
                        category_type="applicant_status",
                        impact_nature="REQUIREMENTS_CHANGED",
                        details=f"Required {label.lower()} increased from {p_amt:.1f}% to {c_amt:.1f}%. Students in this range risk disqualification.",
                        criteria_delta=delta_info,
                        evidence=change.evidence
                    )
                    return grp, delta_info

        return None, None

    @classmethod
    def _calculate_amount_delta_impact(
        cls,
        change: ChangeRecord
    ) -> Tuple[Optional[AffectedGroup], Optional[Dict[str, Any]]]:
        """Calculates financial grant or scholarship amount changes."""
        prev_val = change.previous_value or {}
        curr_val = change.current_value or {}
        if prev_val.get("value_type") == "scholarship_amount" and curr_val.get("value_type") == "scholarship_amount":
            p_amt = prev_val.get("numeric_amount")
            c_amt = curr_val.get("numeric_amount")
            if p_amt is not None and c_amt is not None and p_amt != c_amt:
                delta = c_amt - p_amt
                nature = "Enhanced Benefit" if delta > 0 else "Reduced Benefit"
                delta_info = {
                    "type": "SCHOLARSHIP_RATE_REVISION",
                    "previous_amount": p_amt,
                    "current_amount": c_amt,
                    "net_change": delta,
                    "unit": curr_val.get("unit", "per annum")
                }
                grp = AffectedGroup(
                    group_name="All Enrolled Scholarship Recipients",
                    category_type="applicant_status",
                    impact_nature="EXPLICITLY_AFFECTED",
                    details=f"Scholarship rate revised from ₹{p_amt:,.0f} to ₹{c_amt:,.0f} {curr_val.get('unit', '')} ({nature}: {delta:+,.0f}).",
                    criteria_delta=delta_info,
                    evidence=change.evidence
                )
                return grp, delta_info

        return None, None

    def analyze_document_changes(
        self,
        target_document: Document,
        changes: List[ChangeRecord],
        base_document: Optional[Document] = None
    ) -> ImpactAnalysisReport:
        """
        Synthesizes all clause-level changes into a cohesive Impact Analysis Report.
        """
        explicit_groups: List[AffectedGroup] = []
        potential_groups: List[AffectedGroup] = []
        unresolved_groups: List[AffectedGroup] = []
        deterministic_deltas: List[Dict[str, Any]] = []
        practical_consequences: List[str] = []
        evidence_trail: List[EvidenceRecord] = []

        seen_group_names = set()

        for chg in changes:
            # Evidence collection
            evidence_trail.extend(chg.evidence)

            # 1. Deterministic numerical delta analysis
            inc_grp, inc_delta = self._calculate_income_delta_impact(chg)
            if inc_grp:
                potential_groups.append(inc_grp)
                deterministic_deltas.append(inc_delta)
                practical_consequences.append(inc_grp.details)

            pct_grp, pct_delta = self._calculate_percentage_delta_impact(chg)
            if pct_grp:
                potential_groups.append(pct_grp)
                deterministic_deltas.append(pct_delta)
                practical_consequences.append(pct_grp.details)

            amt_grp, amt_delta = self._calculate_amount_delta_impact(chg)
            if amt_grp:
                potential_groups.append(amt_grp)
                deterministic_deltas.append(amt_delta)
                practical_consequences.append(amt_grp.details)

            # 2. Explicit groups from current text
            if chg.current_text:
                curr_explicit = self._detect_explicit_groups(chg.current_text, chg.evidence)
                for eg in curr_explicit:
                    if eg.group_name not in seen_group_names:
                        explicit_groups.append(eg)
                        seen_group_names.add(eg.group_name)

            # 3. Check for procedural shifts (DBT, DigiLocker, Aadhaar)
            if chg.current_text:
                c_low = chg.current_text.lower()
                if "aadhaar" in c_low or "dbt" in c_low or "direct benefit transfer" in c_low:
                    practical_consequences.append(
                        "Mandatory Aadhaar Seeding: Beneficiaries must ensure active bank accounts are Aadhaar-linked for DBT disbursement."
                    )
                if "digilocker" in c_low:
                    practical_consequences.append(
                        "Digital Certificate Verification: Income/Caste certificates must be uploaded or verified through DigiLocker."
                    )
                if "free ship card" in c_low or "freeship card" in c_low:
                    practical_consequences.append(
                        "Free Ship Card Facility: Eligible students can obtain a Freeship Card on the national portal to secure institutional admission without upfront fee payment."
                    )

            # 4. Check for state-dependent or unresolved clauses
            if chg.current_text and any(w in chg.current_text.lower() for w in ("as prescribed by state", "subject to state quota", "discretion of state")):
                unresolved_groups.append(
                    AffectedGroup(
                        group_name="State Quota / State Discretion Candidates",
                        category_type="institution_type",
                        impact_nature="UNRESOLVED",
                        details="Provisions explicitly defer criteria or quota caps to respective State Government notifications.",
                        criteria_delta=None,
                        evidence=chg.evidence
                    )
                )

        # De-duplicate consequences
        unique_consequences = list(dict.fromkeys(practical_consequences))
        if not unique_consequences:
            unique_consequences.append("Administrative or procedural updates without direct alterations to candidate eligibility thresholds.")

        # Construct executive summary
        summary = (
            f"Policy analysis for '{target_document.scheme_name}' based on Document {target_document.id}. "
            f"Detected {len(changes)} regulatory changes, identifying {len(explicit_groups)} explicitly affected cohorts "
            f"and {len(deterministic_deltas)} quantitative threshold adjustments."
        )

        return ImpactAnalysisReport(
            report_id=f"IMP-{uuid.uuid4().hex[:10].upper()}",
            scheme_name=target_document.scheme_name,
            base_document_id=base_document.id if base_document else None,
            target_document_id=target_document.id,
            summary=summary,
            explicitly_affected_groups=explicit_groups,
            potentially_affected_groups=potential_groups,
            unresolved_groups=unresolved_groups,
            deterministic_deltas=deterministic_deltas,
            practical_consequences=unique_consequences,
            evidence_trail=evidence_trail,
            generated_at=datetime.utcnow().isoformat()
        )
