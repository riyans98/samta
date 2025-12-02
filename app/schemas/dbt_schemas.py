from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import date


"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
NOTE FOR COPILOT AND DEVELOPERS:

This file contains TWO DIFFERENT types of schemas:

1) AtrocityBase → A FORM TEMPLATE ONLY.
   - This is the structure filled by Investigation Officer during FIR submission.
   - It is NOT the structure stored in the database.
   - It should NOT be used for generating DB models, queries, or response models.

2) AtrocityDBModel → The ACTUAL database structure.
   - This matches the MySQL ATROCITY table exactly.
   - This MUST be used for any API response involving case records.
   - This MUST be used by Copilot to generate frontend TypeScript interfaces.

DO NOT mix the two schemas.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

# ======================================================================
# 1. USER ROLE DEFINITIONS
# ======================================================================

RolesType = Literal[
    "State Nodal Officer",
    "Tribal Officer",
    "District Magistrate",
    "Investigation Officer",
    "PFMS Officer"
]


# ======================================================================
# 1.1 DOCUMENT SCHEMAS
# ======================================================================


class DocumentInfo(BaseModel):
    """Information about a single document with base64 encoded content"""
    filename: str
    file_type: str
    content: str  # Base64 encoded file content
    file_size: int  # File size in bytes
    mime_type: str  # MIME type for proper rendering

class DocumentsByType(BaseModel):
    """Documents organized by type"""
    FIR: List[DocumentInfo] = []
    PHOTO: List[DocumentInfo] = []
    CASTE: List[DocumentInfo] = []
    MEDICAL: List[DocumentInfo] = []
    POSTMORTEM: List[DocumentInfo] = []
    OTHER: List[DocumentInfo] = []

# ======================================================================
# 2. FORM TEMPLATE FOR IO SUBMISSION (NOT THE DB MODEL)
# ======================================================================

class AtrocityBase(BaseModel):
    """
    FORM TEMPLATE — NOT the DB schema.

    Filled during initial FIR submission.

    Used only for:
    - IO input
    - merging Aadhaar data
    - merging FIR data
    - validating request payloads

    NOT USED for:
    - DB storage
    - workflow responses
    - case detail API responses
    """
    FIR_NO: Optional[str] = None
    Victim_Name: Optional[str] = None
    Father_Name: Optional[str] = None
    Victim_DOB: Optional[date] = None
    Gender: Optional[str] = None
    Victim_Mobile_No: Optional[str] = None
    Aadhar_No: Optional[int] = None
    Caste: Optional[str] = None
    Case_Description: Optional[str] = None
    Date_of_Incident: Optional[date] = None
    Bank_Account_No: Optional[str] = None
    IFSC_Code: Optional[str] = None
    Holder_Name: Optional[str] = None
    Applicant_Name: Optional[str] = None
    Applicant_Mobile_No: Optional[str] = None
    Caste_Certificate_No: Optional[str] = None
    Victim_Image_No: Optional[str] = None
    Medical_Report_Image: Optional[str] = None
    Passbook_Image: Optional[str] = None
    Location: Optional[str] = None
    Applied_Acts: Optional[str] = None

class AtrocityWithDocuments(AtrocityBase):
    """Atrocity case with associated documents"""
    documents: DocumentsByType = DocumentsByType()


# ======================================================================
# 3. FULL DATABASE MODEL (ATROCITY TABLE MIRROR)

# ======================================================================
class AtrocityDBModel(BaseModel):
    """
    ACTUAL DATABASE MODEL — Source of Truth.

    This matches the MySQL ATROCITY table exactly.
    This must be used for:
    - Case listing
    - Case detail screen
    - Workflow actions (approve, correction, fund release)
    - Frontend integration
    - Timeline rendering
    """

    Case_No: int
    FIR_NO: Optional[str]
    Victim_Name: Optional[str]
    Father_Name: Optional[str]
    Victim_DOB: Optional[str]
    Gender: Optional[str]
    Victim_Mobile_No: Optional[str]
    Aadhar_No: Optional[int]
    Caste: Optional[str]
    Caste_Certificate_No: Optional[str]
    Applied_Acts: Optional[str]
    Case_Description: Optional[str]
    Victim_Image_No: Optional[str]
    Location: Optional[str]
    Date_of_Incident: Optional[str]

    Medical_Report_Image: Optional[str]
    Passbook_Image: Optional[str]

    Bank_Account_No: Optional[str]
    IFSC_Code: Optional[str]
    Holder_Name: Optional[str]

    Stage: Optional[int]
    Fund_Type: Optional[str]
    Fund_Ammount: Optional[str]
    Pending_At: Optional[str]
    Approved_By: Optional[str]

    Limit_Delayed: Optional[int]
    Reason_for_Delay: Optional[str]

    Applicant_Name: Optional[str]
    Applicant_Relation: Optional[str]
    Applicant_Mobile_No: Optional[str]
    Applicant_Email: Optional[str]

    Bank_Name: Optional[str]
    created_at: Optional[str]


# ======================================================================
# 4. WORKFLOW REQUEST PAYLOADS (FOR APPROVE / CORRECTION / FUNDS)
# ======================================================================

class ApprovalPayload(BaseModel):
    actor: str
    role: RolesType
    next_stage: int
    comment: Optional[str] = None
    payload: Optional[dict] = None


class CorrectionPayload(BaseModel):
    actor: str
    role: RolesType
    comment: Optional[str] = None
    corrections_required: Optional[List[str]] = None


class ChargeSheetPayload(BaseModel):
    actor: str
    role: RolesType
    chargesheet_no: str
    chargesheet_date: str
    court_name: str
    severity: Optional[str] = None


class CaseCompletionPayload(BaseModel):
    actor: str
    role: RolesType
    judgment_ref: str
    judgment_date: str
    verdict: str
    notes: Optional[str] = None


class FundReleasePayload(BaseModel):
    actor: str
    role: RolesType
    amount: float
    percent_of_total: float
    fund_type: Optional[str] = None
    txn_id: Optional[str] = None
    bank_acknowledgement: Optional[str] = None


# ======================================================================
# 5. EVENT MODEL (TIMELINE API)
# ======================================================================

class CaseEvent(BaseModel):
    event_id: int
    case_no: int
    performed_by: str
    performed_by_role: str
    event_type: str
    event_data: Optional[dict]
    created_at: str

class AtrocityFullRecord(BaseModel):
    data: AtrocityDBModel
    documents: DocumentsByType = DocumentsByType()
    events: Optional[List[CaseEvent]] = None