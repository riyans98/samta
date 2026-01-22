from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal, Dict
from datetime import date, datetime


# ======================================================================
# STAGE-ROLE VALIDATION CONSTANTS (Per BACKEND_DATA_CONTRACT.md)
# ======================================================================

# Which role can act at each stage
STAGE_ALLOWED_ROLE: Dict[int, str] = {
    1: "Special Officer",         # Special Officer Approval (replaces TO, DM, SNO)
    2: "PFMS Officer",            # PFMS Fund Transfer (first 25%)
    3: "Investigation Officer",   # Chargesheet Submission
    4: "PFMS Officer",            # Second Tranche Release (25-50%)
    5: "District Collector/DM/SJO",  # Judgment Recording
    6: "PFMS Officer",            # Final Tranche Release
}

# Where case goes after approval at each stage
STAGE_NEXT_PENDING_AT: Dict[int, str] = {
    1: "PFMS Officer",         # After Special Officer approves → PFMS for 1st tranche
    2: "Investigation Officer", # After 1st tranche → IO for chargesheet
    3: "PFMS Officer",         # After chargesheet → PFMS for 2nd tranche
    4: "District Collector/DM/SJO",  # After 2nd tranche → DM for judgment
    5: "PFMS Officer",         # After judgment → PFMS for final tranche
    6: None,                   # After final tranche → Case closed
}

# Event type generated at each approval stage
STAGE_APPROVAL_EVENT: Dict[int, str] = {
    1: "SPECIAL_OFFICER_APPROVED",
    2: "PFMS_FIRST_TRANCHE",
    3: "CHARGESHEET_SUBMITTED",
    4: "PFMS_SECOND_TRANCHE",
    5: "DM_JUDGMENT_RECORDED",
    6: "PFMS_FINAL_TRANCHE",
}

# Stage descriptions for reference
STAGE_DESCRIPTIONS: Dict[int, str] = {
    0: "FIR Submitted (IO)",
    1: "Special Officer Approval Pending",
    2: "First Tranche (25%) Pending (PFMS)",
    3: "Chargesheet Pending (IO)",
    4: "Second Tranche (25–50%) Pending (PFMS)",
    5: "Judgment Pending (DM)",
    6: "Final Tranche Pending (PFMS)",
    7: "Case Closed",
}


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
    "District Collector/DM/SJO",
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
    FIR_NO: Optional[str] = None
    Victim_Name: Optional[str] = None
    Father_Name: Optional[str] = None
    Victim_DOB: Optional[str] = None
    Gender: Optional[str] = None
    Victim_Mobile_No: Optional[str] = None
    Aadhar_No: Optional[int] = None
    Caste: Optional[str] = None
    Caste_Certificate_No: Optional[str] = None
    Applied_Acts: Optional[str] = None
    Case_Description: Optional[str] = None
    Victim_Image_No: Optional[str] = None
    Location: Optional[str] = None
    Date_of_Incident: Optional[str] = None

    Medical_Report_Image: Optional[str] = None
    Passbook_Image: Optional[str] = None

    Bank_Account_No: Optional[str] = None
    IFSC_Code: Optional[str] = None
    Holder_Name: Optional[str] = None

    Stage: Optional[int] = None
    Fund_Type: Optional[str] = None
    Fund_Ammount: Optional[str] = None
    Pending_At: Optional[str] = None
    Approved_By: Optional[str] = None

    Limit_Delayed: Optional[int] = None
    Reason_for_Delay: Optional[str] = None

    Applicant_Name: Optional[str] = None
    Applicant_Relation: Optional[str] = None
    Applicant_Mobile_No: Optional[str] = None
    Applicant_Email: Optional[str] = None

    Bank_Name: Optional[str] = None
    created_at: Optional[str] = None
    
    # Jurisdiction fields (for access control filtering)
    State_UT: Optional[str] = None
    District: Optional[str] = None
    Vishesh_P_S_Name: Optional[str] = None
    
    @field_validator('Victim_DOB', 'Date_of_Incident', 'created_at', mode='before')
    @classmethod
    def convert_dates_to_string(cls, v):
        """Convert date/datetime objects to ISO format strings"""
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.isoformat()
        if isinstance(v, date):
            return v.isoformat()
        return str(v) if v else None


# ======================================================================
# 4. WORKFLOW REQUEST PAYLOADS (FOR APPROVE / CORRECTION / FUNDS)
# ======================================================================

class ApprovalPayload(BaseModel):
    actor: str
    role: RolesType
    next_stage: int
    comment: Optional[str] = None
    fund_amount: Optional[float] = None  # For Tribal Officer to set allowance fund amount at stage 1
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
    event_data: Optional[dict] = None
    created_at: str
    
    @field_validator('event_data', mode='before')
    @classmethod
    def parse_event_data(cls, v):
        """Parse JSON string to dict if needed"""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return v
    
    @field_validator('created_at', mode='before')
    @classmethod
    def parse_created_at(cls, v):
        """Convert datetime to ISO string if needed"""
        from datetime import datetime
        if isinstance(v, datetime):
            return v.isoformat()
        return v

class AtrocityFullRecord(BaseModel):
    data: AtrocityDBModel
    documents: DocumentsByType = DocumentsByType()
    events: Optional[List[CaseEvent]] = None



# ======================================================================
# app/schemas/dbt_schemas.py (New Models)
class SeniorResolutionPayload(BaseModel):
    alert_id: int
    senior_input: str = Field(..., max_length=500)
    
class JuniorResponsePayload(BaseModel):
    alert_id: int
    junior_reason: str = Field(..., max_length=500)


# app/schemas/dbt_schemas.py

from pydantic import BaseModel, Field
from typing import Optional

# ... (Existing models like AtrocityBase etc.) ...

# 🔥 NEW MODELS FOR ALERT RESOLUTION (Add these)

class SeniorResolutionPayload(BaseModel):
    alert_id: int
    # Senior ka input zaroori hai (min length check optional hai)
    senior_input: str = Field(..., min_length=5, max_length=500, description="Reason or instruction from Senior Officer")

class JuniorResponsePayload(BaseModel):
    alert_id: int
    junior_reason: str = Field(..., min_length=5, max_length=500, description="Reply from Junior Officer")