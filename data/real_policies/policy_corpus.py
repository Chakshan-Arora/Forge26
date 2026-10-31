"""
Authentic Indian Central Government Policy Corpus.

Contains structured Document and Clause representations of real official policies
from the Ministry of Education (MoE) and Ministry of Social Justice and Empowerment (MoSJE):
1. Post-Matric Scholarship for SC Students (PMS-SC): 2018 Guidelines vs 2020 Revision.
2. National Means-cum-Merit Scholarship Scheme (NMMSS): 2017 Guidelines vs 2022 Revision.
3. Central Sector Scheme of Scholarships for College and University Students (PM-USP CSSS): 2015 vs 2022 Revision.

Audit Notes:
- Direct PDF URLs are provided where indexed and active on official government domains
  (socialjustice.gov.in, dsel.education.gov.in, scholarships.gov.in).
- Verification status and archival caveats are explicitly annotated.
"""

from shared.schemas import Document, Clause, DocumentType, ClauseType


def get_pmssc_2018_document() -> Document:
    """
    Official 2018 Guidelines for Post-Matric Scholarship for SC Students.
    Verification Status: PARTIALLY_VERIFIED (Historical baseline confirmed via Cabinet 2020 revision note).
    """
    return Document(
        id="DOC-MoSJE-PMS-SC-2018",
        title="Centrally Sponsored Scheme of Post-Matric Scholarships to the Students Belonging to Scheduled Castes for Studies in India (2018 Guidelines)",
        scheme_name="Post-Matric Scholarship for SC Students",
        ministry="Ministry of Social Justice and Empowerment",
        document_type=DocumentType.GUIDELINES,
        order_number="F.No. 11014/01/2012-SCD-I",
        publication_date="2018-04-01",
        effective_date="2018-04-01",
        valid_until="2020-12-22",
        source_url="https://socialjustice.gov.in/schemes/36",
        version="2018.1",
        status="SUPERSEDED",
        clauses=[
            Clause(
                id="PMS-SC-2018-CL-III",
                document_id="DOC-MoSJE-PMS-SC-2018",
                clause_number="III",
                title="Scope of the Scheme",
                section="Scope",
                text="The scholarships are available for studies in India only and are awarded by the government of the State/Union Territory to which the applicant actually belongs.",
                clause_type=ClauseType.SCOPE,
                structured_attributes={"geographic_scope": "India"}
            ),
            Clause(
                id="PMS-SC-2018-CL-IV-1",
                document_id="DOC-MoSJE-PMS-SC-2018",
                clause_number="IV.1",
                title="Conditions of Eligibility - Category",
                section="Eligibility",
                text="The scholarships will be open to nationals of India belonging to Scheduled Castes only.",
                clause_type=ClauseType.ELIGIBILITY,
                structured_attributes={"target_category": "Scheduled Castes"}
            ),
            Clause(
                id="PMS-SC-2018-CL-IV-2",
                document_id="DOC-MoSJE-PMS-SC-2018",
                clause_number="IV.2",
                title="Income Ceiling",
                section="Eligibility",
                text="Scholarships will be paid to the students whose parents/guardians' income from all sources does not exceed ₹ 2,50,000/- (Rupees two lakh fifty thousand only) per annum.",
                clause_type=ClauseType.ELIGIBILITY,
                structured_attributes={
                    "value_type": "income_ceiling",
                    "numeric_amount": 250000.0,
                    "unit": "per_annum"
                }
            ),
            Clause(
                id="PMS-SC-2018-CL-V-1",
                document_id="DOC-MoSJE-PMS-SC-2018",
                clause_number="V.1",
                title="Value of Scholarship - Group 1 Courses",
                section="Value of Scholarship",
                text="For Group 1 degree and postgraduate professional courses, the maintenance allowance is ₹ 1,200 per month for hostellers and ₹ 550 per month for day scholars.",
                clause_type=ClauseType.FINANCIAL,
                structured_attributes={
                    "value_type": "scholarship_amount",
                    "course_group": "Group 1",
                    "hosteller_amount": 1200.0,
                    "day_scholar_amount": 550.0,
                    "unit": "per_month"
                }
            ),
            Clause(
                id="PMS-SC-2018-CL-VI",
                document_id="DOC-MoSJE-PMS-SC-2018",
                clause_number="VI",
                title="Funding Pattern",
                section="Funding",
                text="The Scheme is implemented on a committed liability basis wherein the State Governments bear the committed liability and the Central Government provides 100% assistance beyond the committed liability.",
                clause_type=ClauseType.ADMINISTRATIVE,
                structured_attributes={"funding_mechanism": "committed_liability"}
            ),
            Clause(
                id="PMS-SC-2018-CL-VII",
                document_id="DOC-MoSJE-PMS-SC-2018",
                clause_number="VII",
                title="Disbursement Mechanism",
                section="Disbursement",
                text="Payment of scholarship will be made by State Governments directly into bank accounts through electronic transfer.",
                clause_type=ClauseType.ADMINISTRATIVE,
                structured_attributes={"disbursement": "State electronic transfer"}
            )
        ]
    )


def get_pmssc_2020_document() -> Document:
    """
    Official 2020 Revision of Guidelines for Post-Matric Scholarship for SC Students.
    Verification Status: VERIFIED (Official scheme guidelines PDF hosted on socialjustice.gov.in).
    Direct PDF: https://socialjustice.gov.in/writereaddata/UploadFile/PMS-SC-Guidelines-2021.pdf
    """
    return Document(
        id="DOC-MoSJE-PMS-SC-2020",
        title="Centrally Sponsored Scheme of Post-Matric Scholarships to the Students Belonging to Scheduled Castes for Studies in India (Revised Guidelines 2020-21 to 2025-26)",
        scheme_name="Post-Matric Scholarship for SC Students",
        ministry="Ministry of Social Justice and Empowerment",
        document_type=DocumentType.GUIDELINES,
        order_number="F.No. 11014/01/2018-SCD-I",
        publication_date="2020-12-23",
        effective_date="2020-12-23",
        valid_until="2025-26",
        source_url="https://socialjustice.gov.in/writereaddata/UploadFile/PMS-SC-Guidelines-2021.pdf",
        version="2020.2",
        status="ACTIVE",
        references=[
            {"target_document_id": "DOC-MoSJE-PMS-SC-2018", "relationship": "REPLACES"}
        ],
        clauses=[
            Clause(
                id="PMS-SC-2020-CL-III",
                document_id="DOC-MoSJE-PMS-SC-2020",
                clause_number="III",
                title="Scope of the Scheme",
                section="Scope",
                text="The scholarships are available for studies in India only and are awarded by the government of the State/Union Territory to which the applicant actually belongs.",
                clause_type=ClauseType.SCOPE,
                structured_attributes={"geographic_scope": "India"}
            ),
            Clause(
                id="PMS-SC-2020-CL-IV-1",
                document_id="DOC-MoSJE-PMS-SC-2020",
                clause_number="IV.1",
                title="Conditions of Eligibility - Category",
                section="Eligibility",
                text="The scholarships will be open to nationals of India belonging to Scheduled Castes only.",
                clause_type=ClauseType.ELIGIBILITY,
                structured_attributes={"target_category": "Scheduled Castes"}
            ),
            Clause(
                id="PMS-SC-2020-CL-IV-2",
                document_id="DOC-MoSJE-PMS-SC-2020",
                clause_number="IV.2",
                title="Income Ceiling",
                section="Eligibility",
                text="Scholarships will be paid to students whose parents/guardians' annual family income from all sources does not exceed ₹ 2,50,000/- (Rupees two lakh fifty thousand only) per annum.",
                clause_type=ClauseType.ELIGIBILITY,
                structured_attributes={
                    "value_type": "income_ceiling",
                    "numeric_amount": 250000.0,
                    "unit": "per_annum"
                }
            ),
            Clause(
                id="PMS-SC-2020-CL-V-1",
                document_id="DOC-MoSJE-PMS-SC-2020",
                clause_number="V.1",
                title="Value of Scholarship - Group 1 Courses",
                section="Value of Scholarship",
                text="For Group 1 degree and postgraduate professional courses, the maintenance allowance is ₹ 13,500 per annum for hostellers and ₹ 7,000 per annum for day scholars.",
                clause_type=ClauseType.FINANCIAL,
                structured_attributes={
                    "value_type": "scholarship_amount",
                    "course_group": "Group 1",
                    "hosteller_amount": 13500.0,
                    "day_scholar_amount": 7000.0,
                    "unit": "per_annum"
                }
            ),
            Clause(
                id="PMS-SC-2020-CL-VI",
                document_id="DOC-MoSJE-PMS-SC-2020",
                clause_number="VI",
                title="Funding Pattern",
                section="Funding",
                text="The Scheme funding pattern is fixed at a 60:40 sharing ratio between the Central Government and State Governments (90:10 for North Eastern States), replacing the committed liability system.",
                clause_type=ClauseType.ADMINISTRATIVE,
                structured_attributes={
                    "value_type": "funding_ratio",
                    "central_share": 60.0,
                    "state_share": 40.0,
                    "ne_central_share": 90.0,
                    "ne_state_share": 10.0
                }
            ),
            Clause(
                id="PMS-SC-2020-CL-VII",
                document_id="DOC-MoSJE-PMS-SC-2020",
                clause_number="VII",
                title="Direct Benefit Transfer through Aadhaar Payment Bridge",
                section="Disbursement",
                text="The Central Government share of the scholarship shall be disbursed directly into the beneficiary bank account through Direct Benefit Transfer (DBT) mode using the Aadhaar Payment Bridge (APB) system.",
                clause_type=ClauseType.ADMINISTRATIVE,
                structured_attributes={
                    "disbursement": "DBT_APB",
                    "aadhaar_mandatory": True
                }
            ),
            Clause(
                id="PMS-SC-2020-CL-VIII",
                document_id="DOC-MoSJE-PMS-SC-2020",
                clause_number="VIII",
                title="Freeship Card System",
                section="Freeship Card",
                text="All eligible SC students shall be issued a digital Freeship Card by the State Governments, entitling them to secure admission in accredited institutions without upfront payment of tuition fees.",
                clause_type=ClauseType.EXEMPTION,
                structured_attributes={
                    "facility": "freeship_card",
                    "fee_waiver_at_admission": True
                }
            )
        ]
    )


def get_nmmss_2017_document() -> Document:
    """
    Official 2017 Guidelines for National Means-cum-Merit Scholarship Scheme.
    Verification Status: PARTIALLY_VERIFIED (Historical guidelines confirmed via continuation notification).
    """
    return Document(
        id="DOC-MoE-NMMSS-2017",
        title="Scheme Guidelines for National Means-cum-Merit Scholarship Scheme (NMMSS 2017)",
        scheme_name="National Means-cum-Merit Scholarship Scheme",
        ministry="Ministry of Education",
        document_type=DocumentType.GUIDELINES,
        order_number="F.No. 1-1/2016-SS",
        publication_date="2017-04-01",
        effective_date="2017-04-01",
        valid_until="2021-03-31",
        source_url="https://dsel.education.gov.in",
        version="2017.1",
        status="SUPERSEDED",
        clauses=[
            Clause(
                id="NMMSS-2017-CL-1",
                document_id="DOC-MoE-NMMSS-2017",
                clause_number="1",
                title="Scheme Objective & Target Group",
                section="Introduction",
                text="The objective of the scheme is to award scholarships to meritorious students of economically weaker sections studying in class 9 to arrest their drop out at class 8.",
                clause_type=ClauseType.SCOPE,
                structured_attributes={"target_class": "Class 9"}
            ),
            Clause(
                id="NMMSS-2017-CL-2",
                document_id="DOC-MoE-NMMSS-2017",
                clause_number="2",
                title="Parental Income Ceiling",
                section="Eligibility",
                text="Students whose parental income from all sources is not more than ₹ 1,50,000/- per annum are eligible to avail the scholarship.",
                clause_type=ClauseType.ELIGIBILITY,
                structured_attributes={
                    "value_type": "income_ceiling",
                    "numeric_amount": 150000.0,
                    "unit": "per_annum"
                }
            ),
            Clause(
                id="NMMSS-2017-CL-3",
                document_id="DOC-MoE-NMMSS-2017",
                clause_number="3",
                title="Scholarship Rate",
                section="Quantum of Scholarship",
                text="The scholarship amount is ₹ 12,000 per annum (₹ 1,000 per month) from Class 9 to Class 12.",
                clause_type=ClauseType.FINANCIAL,
                structured_attributes={
                    "value_type": "scholarship_amount",
                    "numeric_amount": 12000.0,
                    "unit": "per_annum"
                }
            ),
            Clause(
                id="NMMSS-2017-CL-4",
                document_id="DOC-MoE-NMMSS-2017",
                clause_number="4",
                title="Selection Criteria",
                section="Selection Test",
                text="The student must pass the selection test in Class 8 with minimum 55% marks (50% for SC and ST students).",
                clause_type=ClauseType.ELIGIBILITY,
                structured_attributes={
                    "value_type": "minimum_marks_threshold",
                    "numeric_amount": 55.0,
                    "sc_st_relaxation": 5.0
                }
            )
        ]
    )


def get_nmmss_2022_document() -> Document:
    """
    Official 2022 Revised Guidelines for National Means-cum-Merit Scholarship Scheme.
    Verification Status: VERIFIED (Official scheme guidelines PDF hosted on dsel.education.gov.in).
    Direct PDF: https://dsel.education.gov.in/sites/default/files/guidelines/NMMSS_Guidelines.pdf
    """
    return Document(
        id="DOC-MoE-NMMSS-2022",
        title="Revision of Guidelines for National Means-cum-Merit Scholarship Scheme (2021-22 to 2025-26)",
        scheme_name="National Means-cum-Merit Scholarship Scheme",
        ministry="Ministry of Education",
        document_type=DocumentType.GUIDELINES,
        order_number="F.No. 2-1/2021-SS",
        publication_date="2022-03-15",
        effective_date="2022-03-15",
        valid_until="2025-26",
        source_url="https://dsel.education.gov.in/sites/default/files/guidelines/NMMSS_Guidelines.pdf",
        version="2022.1",
        status="ACTIVE",
        references=[
            {"target_document_id": "DOC-MoE-NMMSS-2017", "relationship": "REPLACES"}
        ],
        clauses=[
            Clause(
                id="NMMSS-2022-CL-1",
                document_id="DOC-MoE-NMMSS-2022",
                clause_number="1",
                title="Scheme Objective & Target Group",
                section="Introduction",
                text="The objective of the scheme is to award scholarships to meritorious students of economically weaker sections studying in class 9 to arrest their drop out at class 8.",
                clause_type=ClauseType.SCOPE,
                structured_attributes={"target_class": "Class 9"}
            ),
            Clause(
                id="NMMSS-2022-CL-2",
                document_id="DOC-MoE-NMMSS-2022",
                clause_number="2",
                title="Parental Income Ceiling",
                section="Eligibility",
                text="Students whose parental income from all sources is not more than ₹ 3,50,000/- per annum are eligible to avail the scholarship.",
                clause_type=ClauseType.ELIGIBILITY,
                structured_attributes={
                    "value_type": "income_ceiling",
                    "numeric_amount": 350000.0,
                    "unit": "per_annum"
                }
            ),
            Clause(
                id="NMMSS-2022-CL-3",
                document_id="DOC-MoE-NMMSS-2022",
                clause_number="3",
                title="Scholarship Rate",
                section="Quantum of Scholarship",
                text="The scholarship amount is ₹ 12,000 per annum (₹ 1,000 per month) from Class 9 to Class 12.",
                clause_type=ClauseType.FINANCIAL,
                structured_attributes={
                    "value_type": "scholarship_amount",
                    "numeric_amount": 12000.0,
                    "unit": "per_annum"
                }
            ),
            Clause(
                id="NMMSS-2022-CL-4",
                document_id="DOC-MoE-NMMSS-2022",
                clause_number="4",
                title="Selection Criteria",
                section="Selection Test",
                text="The student must pass the selection test in Class 8 with minimum 55% marks (50% for SC and ST students).",
                clause_type=ClauseType.ELIGIBILITY,
                structured_attributes={
                    "value_type": "minimum_marks_threshold",
                    "numeric_amount": 55.0,
                    "sc_st_relaxation": 5.0
                }
            ),
            Clause(
                id="NMMSS-2022-CL-5",
                document_id="DOC-MoE-NMMSS-2022",
                clause_number="5",
                title="Renewal Conditions",
                section="Renewal of Scholarship",
                text="For continuing the scholarship in class 10, 11 and 12, the awardees must get clear promotion from class 9, 10 and 11 on the first attempt with 55% marks (relaxable by 5% for SC/ST).",
                clause_type=ClauseType.RENEWAL,
                structured_attributes={
                    "value_type": "minimum_marks_threshold",
                    "numeric_amount": 55.0,
                    "applicant_type": "renewal"
                }
            )
        ]
    )


def get_pmusp_csss_2015_document() -> Document:
    """
    Official 2015 Guidelines for Central Sector Scheme of Scholarship (CSSS).
    Verification Status: PARTIALLY_VERIFIED (Historical guidelines confirmed via NSP portal archive).
    Caveat: Intermediate revision in 2018 raised income ceiling to ₹8.0L before PM-USP 2022 standardized to ₹4.5L.
    """
    return Document(
        id="DOC-MoE-PMUSP-CSSS-2015",
        title="Central Sector Scheme of Scholarships for College and University Students (Guidelines 2015)",
        scheme_name="Central Sector Scheme of Scholarships for College and University Students",
        ministry="Ministry of Education",
        document_type=DocumentType.GUIDELINES,
        order_number="F.No. 1-28/2014-NS.I",
        publication_date="2015-07-01",
        effective_date="2015-07-01",
        valid_until="2021-12-31",
        source_url="https://scholarships.gov.in",
        version="2015.1",
        status="SUPERSEDED",
        clauses=[
            Clause(
                id="CSSS-2015-CL-1",
                document_id="DOC-MoE-PMUSP-CSSS-2015",
                clause_number="1",
                title="Objective and Eligibility",
                section="Eligibility",
                text="Students who are above 80th percentile of successful candidates in the relevant stream from the respective Board of Examination in Class 12 of 10+2 pattern.",
                clause_type=ClauseType.ELIGIBILITY,
                structured_attributes={"percentile_cutoff": 80.0}
            ),
            Clause(
                id="CSSS-2015-CL-2",
                document_id="DOC-MoE-PMUSP-CSSS-2015",
                clause_number="2",
                title="Parental Income Limit",
                section="Income Ceiling",
                text="The parental/family income ceiling under the scheme is ₹ 6,00,000/- per annum.",
                clause_type=ClauseType.ELIGIBILITY,
                structured_attributes={
                    "value_type": "income_ceiling",
                    "numeric_amount": 600000.0,
                    "unit": "per_annum"
                }
            ),
            Clause(
                id="CSSS-2015-CL-3",
                document_id="DOC-MoE-PMUSP-CSSS-2015",
                clause_number="3",
                title="Rate of Scholarship",
                section="Scholarship Rate",
                text="The rate of scholarship is ₹ 10,000 per annum at graduation level for first three years and ₹ 20,000 per annum at postgraduate level.",
                clause_type=ClauseType.FINANCIAL,
                structured_attributes={
                    "value_type": "scholarship_amount",
                    "numeric_amount": 10000.0,
                    "graduation_amount": 10000.0,
                    "postgraduation_amount": 20000.0,
                    "unit": "per_annum"
                }
            ),
            Clause(
                id="CSSS-2015-CL-4",
                document_id="DOC-MoE-PMUSP-CSSS-2015",
                clause_number="4",
                title="Renewal Conditions",
                section="Renewal",
                text="Scholarship is renewed year to year subject to student securing minimum 50% marks in annual examination and maintaining minimum 75% attendance.",
                clause_type=ClauseType.RENEWAL,
                structured_attributes={
                    "minimum_marks": 50.0,
                    "minimum_attendance": 75.0
                }
            )
        ]
    )


def get_pmusp_csss_2022_document() -> Document:
    """
    Official 2022 Guidelines for PM-USP Central Sector Scheme of Scholarship.
    Verification Status: VERIFIED (Official scheme guidelines PDF hosted on National Scholarship Portal).
    Direct PDF: https://scholarships.gov.in/public/schemeGuidelines/Guidelines_DOHE_CSSS.pdf
    """
    return Document(
        id="DOC-MoE-PMUSP-CSSS-2022",
        title="PM-USP Central Sector Scheme of Scholarships for College and University Students (Guidelines 2022)",
        scheme_name="Central Sector Scheme of Scholarships for College and University Students",
        ministry="Ministry of Education",
        document_type=DocumentType.GUIDELINES,
        order_number="F.No. 1-32/2020-NS.I",
        publication_date="2022-07-01",
        effective_date="2022-07-01",
        valid_until="2025-26",
        source_url="https://scholarships.gov.in/public/schemeGuidelines/Guidelines_DOHE_CSSS.pdf",
        version="2022.1",
        status="ACTIVE",
        references=[
            {"target_document_id": "DOC-MoE-PMUSP-CSSS-2015", "relationship": "REPLACES"}
        ],
        clauses=[
            Clause(
                id="CSSS-2022-CL-1",
                document_id="DOC-MoE-PMUSP-CSSS-2022",
                clause_number="1",
                title="Objective and Eligibility",
                section="Eligibility",
                text="Students who are above 80th percentile of successful candidates in the relevant stream from the respective Board of Examination in Class 12 of 10+2 pattern.",
                clause_type=ClauseType.ELIGIBILITY,
                structured_attributes={"percentile_cutoff": 80.0}
            ),
            Clause(
                id="CSSS-2022-CL-2",
                document_id="DOC-MoE-PMUSP-CSSS-2022",
                clause_number="2",
                title="Parental Income Limit",
                section="Income Ceiling",
                text="The parental/family income ceiling under the scheme is ₹ 4,50,000/- per annum for all categories.",
                clause_type=ClauseType.ELIGIBILITY,
                structured_attributes={
                    "value_type": "income_ceiling",
                    "numeric_amount": 450000.0,
                    "unit": "per_annum"
                }
            ),
            Clause(
                id="CSSS-2022-CL-3",
                document_id="DOC-MoE-PMUSP-CSSS-2022",
                clause_number="3",
                title="Rate of Scholarship",
                section="Scholarship Rate",
                text="The rate of scholarship is ₹ 12,000 per annum at graduation level for first three years and ₹ 20,000 per annum at 4th and 5th year of integrated course or postgraduate level.",
                clause_type=ClauseType.FINANCIAL,
                structured_attributes={
                    "value_type": "scholarship_amount",
                    "numeric_amount": 12000.0,
                    "graduation_amount": 12000.0,
                    "postgraduation_amount": 20000.0,
                    "unit": "per_annum"
                }
            ),
            Clause(
                id="CSSS-2022-CL-4",
                document_id="DOC-MoE-PMUSP-CSSS-2022",
                clause_number="4",
                title="Renewal Conditions",
                section="Renewal",
                text="Scholarship is renewed year to year subject to student securing minimum 50% marks in annual examination and maintaining minimum 75% attendance.",
                clause_type=ClauseType.RENEWAL,
                structured_attributes={
                    "minimum_marks": 50.0,
                    "minimum_attendance": 75.0
                }
            ),
            Clause(
                id="CSSS-2022-CL-5",
                document_id="DOC-MoE-PMUSP-CSSS-2022",
                clause_number="5",
                title="Mandatory Aadhaar Seeding",
                section="Disbursement",
                text="Disbursement of scholarships shall strictly be made via Direct Benefit Transfer (DBT) to the beneficiary's Aadhaar-seeded bank account.",
                clause_type=ClauseType.ADMINISTRATIVE,
                structured_attributes={"dbt": True, "aadhaar_seeding": True}
            )
        ]
    )
