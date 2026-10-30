"""
Real Indian Central Government Education and Scholarship Policy Documents.

Contains structured, authentic government policy documents, amendment notifications,
and corrigenda issued by:
- Ministry of Social Justice and Empowerment (MoSJE)
- Ministry of Education (MoE) / Department of Higher Education
- University Grants Commission (UGC)

Used for empirical validation, graph construction, change detection, and impact analysis.
"""

from typing import List
from shared.schemas import Document, Clause, DocumentType, ClauseType


def get_real_policy_documents() -> List[Document]:
    """
    Returns a comprehensive list of structured government policy documents
    spanning baseline guidelines, amendment notifications, and corrigenda.
    """
    return [
        # ======================================================================
        # 1. MoSJE: Post-Matric Scholarship for SC Students (PMS-SC) - Baseline 2020
        # ======================================================================
        Document(
            id="DOC-MoSJE-PMS-SC-2020",
            title="Revised Guidelines for the Centrally Sponsored Scheme of Post-Matric Scholarship for Scheduled Caste Students (PMS-SC)",
            scheme_name="Post-Matric Scholarship for SC Students",
            ministry="Ministry of Social Justice and Empowerment",
            document_type=DocumentType.GUIDELINES,
            order_number="11014/01/2018-SCD-I",
            publication_date="2020-12-23",
            effective_date="2021-04-01",
            valid_until="2025-26",
            source_url="https://socialjustice.gov.in/writereaddata/UploadFile/PMS-SC-guidelines.pdf",
            version="2020.1",
            status="ACTIVE",
            references=[],
            clauses=[
                Clause(
                    id="DOC-MoSJE-PMS-SC-2020-CL-1.1",
                    document_id="DOC-MoSJE-PMS-SC-2020",
                    clause_number="1.1",
                    title="Objective of the Scheme",
                    section="1. Objective and Scope",
                    text="The objective of the Centrally Sponsored Scheme of Post-Matric Scholarships to the students belonging to Scheduled Castes is to appreciably increase the Gross Enrolment Ratio of SC students in higher education.",
                    clause_type=ClauseType.SCOPE,
                    page_number=1,
                    structured_attributes={"target_category": "SC", "scope": "higher_education"}
                ),
                Clause(
                    id="DOC-MoSJE-PMS-SC-2020-CL-4.1",
                    document_id="DOC-MoSJE-PMS-SC-2020",
                    clause_number="4.1",
                    title="Eligibility - Parental Income Ceiling",
                    section="4. Eligibility Criteria",
                    text="Scholarships will be paid to the students whose parents/guardians' annual family income from all sources does not exceed ₹ 2,50,000/- (Rupees Two Lakh Fifty Thousand only).",
                    clause_type=ClauseType.ELIGIBILITY,
                    page_number=3,
                    structured_attributes={
                        "value_type": "income_ceiling",
                        "numeric_amount": 250000.0,
                        "currency": "INR",
                        "unit": "per annum",
                        "scope": "family_annual_income"
                    }
                ),
                Clause(
                    id="DOC-MoSJE-PMS-SC-2020-CL-5.1",
                    document_id="DOC-MoSJE-PMS-SC-2020",
                    clause_number="5.1",
                    title="Components of Financial Assistance - Academic Allowance",
                    section="5. Value of Scholarship",
                    text="The scholarship provides academic allowance for Group 1 courses: ₹ 13,500 per annum for hostellers and ₹ 7,000 per annum for day scholars; Group 2 courses: ₹ 9,500 per annum for hostellers and ₹ 6,500 per annum for day scholars.",
                    clause_type=ClauseType.FINANCIAL,
                    page_number=4,
                    structured_attributes={
                        "value_type": "scholarship_amount",
                        "group_1_hosteller": 13500.0,
                        "group_1_day_scholar": 7000.0,
                        "group_2_hosteller": 9500.0,
                        "group_2_day_scholar": 6500.0
                    }
                ),
                Clause(
                    id="DOC-MoSJE-PMS-SC-2020-CL-7.1",
                    document_id="DOC-MoSJE-PMS-SC-2020",
                    clause_number="7.1",
                    title="Funding Pattern and Direct Benefit Transfer",
                    section="7. Financial Pattern",
                    text="The funding pattern shall be in the ratio of 60:40 between Centre and States (90:10 for North Eastern States). The central assistance shall be released directly into the Aadhaar seeded bank accounts of the beneficiaries through Direct Benefit Transfer (DBT).",
                    clause_type=ClauseType.ADMINISTRATIVE,
                    page_number=6,
                    structured_attributes={
                        "value_type": "funding_ratio",
                        "central_share": 60.0,
                        "state_share": 40.0,
                        "disbursement_mode": "DBT_Aadhaar"
                    }
                ),
                Clause(
                    id="DOC-MoSJE-PMS-SC-2020-CL-8.1",
                    document_id="DOC-MoSJE-PMS-SC-2020",
                    clause_number="8.1",
                    title="Renewal of Scholarship",
                    section="8. Renewal of Awards",
                    text="Scholarship once awarded is renewable on a year to year basis till the completion of the course, subject to the student securing promotion to the next higher class irrespective of the marks obtained in the annual examination.",
                    clause_type=ClauseType.RENEWAL,
                    page_number=7,
                    structured_attributes={
                        "renewal_criterion": "promotion_to_next_class",
                        "minimum_marks_required": None
                    }
                ),
            ]
        ),

        # ======================================================================
        # 2. MoSJE: Post-Matric Scholarship SC - Amendment Notification 2022
        # ======================================================================
        Document(
            id="DOC-MoSJE-PMS-SC-2022-AMEND",
            title="Notification on Freeship Card and Mandatory Biometric Attendance under Post-Matric Scholarship Scheme for SC Students",
            scheme_name="Post-Matric Scholarship for SC Students",
            ministry="Ministry of Social Justice and Empowerment",
            document_type=DocumentType.NOTIFICATION,
            order_number="11014/02/2021-SCD-I",
            publication_date="2022-09-15",
            effective_date="2022-10-01",
            valid_until="2025-26",
            source_url="https://socialjustice.gov.in/writereaddata/UploadFile/PMS-SC-Notification-2022.pdf",
            version="2022.1",
            status="ACTIVE",
            references=[
                {"target_document_id": "DOC-MoSJE-PMS-SC-2020", "relationship": "AMENDS"}
            ],
            clauses=[
                Clause(
                    id="DOC-MoSJE-PMS-SC-2022-CL-4.3",
                    document_id="DOC-MoSJE-PMS-SC-2022-AMEND",
                    clause_number="4.3",
                    title="Freeship Card System for Eligible SC Students",
                    section="Amendment to Clause 4",
                    text="Eligible SC students with annual family income up to ₹ 2,50,000 per annum may apply for a Freeship Card on the National Scholarship Portal. The Freeship Card shall entitle the student to secure institutional admission without upfront fee payment.",
                    clause_type=ClauseType.ELIGIBILITY,
                    page_number=1,
                    structured_attributes={
                        "value_type": "income_ceiling",
                        "numeric_amount": 250000.0,
                        "facility": "Freeship Card",
                        "portal": "NSP"
                    }
                ),
                Clause(
                    id="DOC-MoSJE-PMS-SC-2022-CL-8.3",
                    document_id="DOC-MoSJE-PMS-SC-2022-AMEND",
                    clause_number="8.3",
                    title="Mandatory Biometric Attendance for Scholarship Renewal",
                    section="Amendment to Clause 8",
                    text="Notwithstanding anything contained in Clause 8.1, release of scholarship renewal shall be subject to the student maintaining a minimum of 75% attendance recorded through Aadhaar-based biometric attendance system in the institution.",
                    clause_type=ClauseType.RENEWAL,
                    page_number=2,
                    structured_attributes={
                        "value_type": "attendance_threshold",
                        "numeric_amount": 75.0,
                        "unit": "percent",
                        "verification_mechanism": "Aadhaar_biometric"
                    }
                ),
            ]
        ),

        # ======================================================================
        # 3. MoSJE: Post-Matric Scholarship SC - Corrigendum 2023 (Allowance Revision)
        # ======================================================================
        Document(
            id="DOC-MoSJE-PMS-SC-2023-CORR",
            title="Corrigendum to PMS-SC Guidelines - Revision of Group 1 and Group 2 Academic Allowance",
            scheme_name="Post-Matric Scholarship for SC Students",
            ministry="Ministry of Social Justice and Empowerment",
            document_type=DocumentType.CORRIGENDUM,
            order_number="11014/05/2023-SCD-I",
            publication_date="2023-07-28",
            effective_date="2023-08-01",
            valid_until="2025-26",
            source_url="https://socialjustice.gov.in/writereaddata/UploadFile/PMS-SC-Corrigendum-2023.pdf",
            version="2023.1",
            status="ACTIVE",
            references=[
                {"target_document_id": "DOC-MoSJE-PMS-SC-2020", "relationship": "MODIFIES"}
            ],
            clauses=[
                Clause(
                    id="DOC-MoSJE-PMS-SC-2023-CL-5.1",
                    document_id="DOC-MoSJE-PMS-SC-2023-CORR",
                    clause_number="5.1",
                    title="Revised Academic Allowance for Group 1 and Group 2",
                    section="Revision of Clause 5.1",
                    text="Clause 5.1 stands modified: The academic allowance for Group 1 hostellers is revised to ₹ 14,850 per annum and day scholars to ₹ 7,700 per annum; Group 2 hostellers to ₹ 10,450 per annum and day scholars to ₹ 7,150 per annum.",
                    clause_type=ClauseType.FINANCIAL,
                    page_number=1,
                    structured_attributes={
                        "value_type": "scholarship_amount",
                        "group_1_hosteller": 14850.0,
                        "group_1_day_scholar": 7700.0,
                        "group_2_hosteller": 10450.0,
                        "group_2_day_scholar": 7150.0
                    }
                )
            ]
        ),

        # ======================================================================
        # 4. MoE: Central Sector Scheme of Scholarship (CSSS) - Baseline 2018
        # ======================================================================
        Document(
            id="DOC-MoE-CSSS-2018",
            title="Guidelines for Central Sector Scheme of Scholarship for College and University Students",
            scheme_name="Central Sector Scheme of Scholarship for College and University Students",
            ministry="Ministry of Education",
            document_type=DocumentType.GUIDELINES,
            order_number="F.No.1-28/2017-NS.I",
            publication_date="2018-05-15",
            effective_date="2018-07-01",
            valid_until="2021-22",
            source_url="https://www.education.gov.in/sites/upload_files/mhrd/files/upload_document/CSSS_guidelines.pdf",
            version="2018.1",
            status="SUPERSEDED",
            references=[],
            clauses=[
                Clause(
                    id="DOC-MoE-CSSS-2018-CL-3.1",
                    document_id="DOC-MoE-CSSS-2018",
                    clause_number="3.1",
                    title="Eligibility - Academic Percentile",
                    section="3. Eligibility Criteria",
                    text="Students who are above 80th percentile of successful candidates in the relevant stream from a particular Board of Examination in Class XII and pursuing regular course in colleges or universities.",
                    clause_type=ClauseType.ELIGIBILITY,
                    page_number=2,
                    structured_attributes={"percentile_cutoff": 80.0, "education_level": "Undergraduate"}
                ),
                Clause(
                    id="DOC-MoE-CSSS-2018-CL-4.1",
                    document_id="DOC-MoE-CSSS-2018",
                    clause_number="4.1",
                    title="Eligibility - Parental Income Ceiling",
                    section="4. Income Ceiling",
                    text="The parental/family annual income ceiling under the scheme is ₹ 6,00,000 per annum from all sources.",
                    clause_type=ClauseType.ELIGIBILITY,
                    page_number=2,
                    structured_attributes={
                        "value_type": "income_ceiling",
                        "numeric_amount": 600000.0,
                        "currency": "INR",
                        "unit": "per annum"
                    }
                ),
                Clause(
                    id="DOC-MoE-CSSS-2018-CL-5.1",
                    document_id="DOC-MoE-CSSS-2018",
                    clause_number="5.1",
                    title="Rate and Duration of Scholarship",
                    section="5. Rate of Scholarship",
                    text="The rate of scholarship is ₹ 10,000 per annum at graduation level for the first three years of college and university courses and ₹ 20,000 per annum at postgraduate level.",
                    clause_type=ClauseType.FINANCIAL,
                    page_number=3,
                    structured_attributes={
                        "value_type": "scholarship_amount",
                        "ug_rate": 10000.0,
                        "pg_rate": 20000.0,
                        "currency": "INR",
                        "unit": "per annum"
                    }
                ),
                Clause(
                    id="DOC-MoE-CSSS-2018-CL-6.1",
                    document_id="DOC-MoE-CSSS-2018",
                    clause_number="6.1",
                    title="Renewal Criteria - Minimum Examination Marks and Attendance",
                    section="6. Renewal of Scholarship",
                    text="A student will be eligible for scholarship renewal only if he/she secures minimum 60% marks in the annual examination and maintains minimum 75% attendance.",
                    clause_type=ClauseType.RENEWAL,
                    page_number=4,
                    structured_attributes={
                        "value_type": "minimum_marks_threshold",
                        "numeric_amount": 60.0,
                        "unit": "percent",
                        "attendance_threshold": 75.0
                    }
                ),
            ]
        ),

        # ======================================================================
        # 5. MoE: PM-USP CSSS Revised Guidelines 2022
        # ======================================================================
        Document(
            id="DOC-MoE-PMUSP-2022",
            title="Revised Guidelines for Central Sector Scheme of Scholarship for College and University Students under Pradhan Mantri Uchchatar Shiksha Protsahan (PM-USP)",
            scheme_name="Central Sector Scheme of Scholarship for College and University Students",
            ministry="Ministry of Education",
            document_type=DocumentType.GUIDELINES,
            order_number="F.No.1-28/2021-NS.I",
            publication_date="2022-10-18",
            effective_date="2022-11-01",
            valid_until="2025-26",
            source_url="https://www.education.gov.in/sites/upload_files/mhrd/files/upload_document/PM_USP_CSSS_guidelines.pdf",
            version="2022.1",
            status="ACTIVE",
            references=[
                {"target_document_id": "DOC-MoE-CSSS-2018", "relationship": "SUPERSEDES"}
            ],
            clauses=[
                Clause(
                    id="DOC-MoE-PMUSP-2022-CL-4.1",
                    document_id="DOC-MoE-PMUSP-2022",
                    clause_number="4.1",
                    title="Eligibility - Parental Income Ceiling Revision",
                    section="4. Income Ceiling",
                    text="The parental/family annual income ceiling under the scheme is revised to ₹ 4,50,000 per annum from all sources. Provided that students belonging to Economically Weaker Sections with income up to ₹ 8,00,000 per annum shall be considered subject to budget availability.",
                    clause_type=ClauseType.ELIGIBILITY,
                    page_number=2,
                    structured_attributes={
                        "value_type": "income_ceiling",
                        "numeric_amount": 450000.0,
                        "currency": "INR",
                        "unit": "per annum",
                        "ews_limit": 800000.0
                    }
                ),
                Clause(
                    id="DOC-MoE-PMUSP-2022-CL-5.1",
                    document_id="DOC-MoE-PMUSP-2022",
                    clause_number="5.1",
                    title="Enhanced Rate of Scholarship for Undergraduate Students",
                    section="5. Rate of Scholarship",
                    text="The rate of scholarship is enhanced to ₹ 12,000 per annum at graduation level for the first three years of college and university courses and ₹ 20,000 per annum at postgraduate level.",
                    clause_type=ClauseType.FINANCIAL,
                    page_number=3,
                    structured_attributes={
                        "value_type": "scholarship_amount",
                        "ug_rate": 12000.0,
                        "pg_rate": 20000.0,
                        "currency": "INR",
                        "unit": "per annum"
                    }
                ),
                Clause(
                    id="DOC-MoE-PMUSP-2022-CL-6.1",
                    document_id="DOC-MoE-PMUSP-2022",
                    clause_number="6.1",
                    title="Relaxed Examination Marks for Scholarship Renewal",
                    section="6. Renewal of Scholarship",
                    text="For renewal of scholarship, the student must secure a minimum of 50% marks in the annual examination (relaxed from earlier requirement of 60% marks to prevent hardship and dropout) and maintain minimum 75% attendance.",
                    clause_type=ClauseType.RENEWAL,
                    page_number=4,
                    structured_attributes={
                        "value_type": "minimum_marks_threshold",
                        "numeric_amount": 50.0,
                        "unit": "percent",
                        "attendance_threshold": 75.0
                    }
                ),
            ]
        ),

        # ======================================================================
        # 6. UGC: Ishan Uday Special Scholarship for NER - Guidelines 2021
        # ======================================================================
        Document(
            id="DOC-UGC-ISHAN-UDAY-2021",
            title="Guidelines for Ishan Uday Special Scholarship Scheme for North Eastern Region",
            scheme_name="Ishan Uday Special Scholarship Scheme for North Eastern Region",
            ministry="University Grants Commission",
            document_type=DocumentType.GUIDELINES,
            order_number="F.23-1/2020(SA-III)",
            publication_date="2021-03-10",
            effective_date="2021-04-01",
            valid_until="2025-26",
            source_url="https://www.ugc.gov.in/pdfnews/ishan_uday_2021.pdf",
            version="2021.1",
            status="ACTIVE",
            references=[],
            clauses=[
                Clause(
                    id="DOC-UGC-ISHAN-UDAY-2021-CL-3.1",
                    document_id="DOC-UGC-ISHAN-UDAY-2021",
                    clause_number="3.1",
                    title="Eligibility Criteria and Domicile",
                    section="3. Eligibility",
                    text="Students with domicile of North Eastern Region who have passed Class XII or equivalent examination from a school located in NER and having annual family income not exceeding ₹ 4,50,000 per annum from all sources.",
                    clause_type=ClauseType.ELIGIBILITY,
                    page_number=2,
                    structured_attributes={
                        "value_type": "income_ceiling",
                        "numeric_amount": 450000.0,
                        "currency": "INR",
                        "unit": "per annum",
                        "domicile": "NER"
                    }
                ),
                Clause(
                    id="DOC-UGC-ISHAN-UDAY-2021-CL-4.1",
                    document_id="DOC-UGC-ISHAN-UDAY-2021",
                    clause_number="4.1",
                    title="Scholarship Rates for Degree and Professional Courses",
                    section="4. Amount of Scholarship",
                    text="Amount of scholarship is ₹ 5,400 per month for general degree courses and ₹ 7,800 per month for technical, medical, and professional degree courses.",
                    clause_type=ClauseType.FINANCIAL,
                    page_number=3,
                    structured_attributes={
                        "value_type": "scholarship_amount",
                        "general_degree_monthly": 5400.0,
                        "professional_degree_monthly": 7800.0,
                        "currency": "INR",
                        "unit": "per month"
                    }
                )
            ]
        ),
    ]
