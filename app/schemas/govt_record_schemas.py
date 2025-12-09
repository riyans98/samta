from pydantic import BaseModel
from typing import Literal, Optional
from datetime import date, time, datetime

# Aadhaar Model
# table name = aadhaar_records
class AadhaarRecord(BaseModel):

    def __init__(self, **data):
        super().__init__(**data)

    aadhaar_id: int
    full_name: str
    father_name: str
    dob: date
    gender: str
    address_line1: str
    address_line2: Optional[str] = None
    district: str
    state: str
    pincode: str
    mobile: str
    email: Optional[str] = None
    enrollment_date: date
    last_update: Optional[datetime] = None
    mobile_verified: bool
    email_verified: bool
    status: str

# FIR Model
# table name = fir_records
class FIRRecord(BaseModel):

    def __init__(self, **data):
        super().__init__(**data)

    fir_no: str
    police_station_code: str
    police_station_name: str
    district: str
    state: str
    filing_datetime: datetime

    complainant_name: str
    complainant_age: int
    complainant_gender: str
    complainant_address: str
    complainant_contact: str
    complainant_relation: Optional[str] = None

    victim_name: Optional[str] = None
    victim_age: Optional[int] = None
    victim_gender: Optional[str] = None
    victim_address: Optional[str] = None
    victim_contact: Optional[str] = None

    accused_name: Optional[str] = None
    accused_description: Optional[str] = None

    incident_date: date
    incident_time: time
    incident_location: str
    incident_summary: str
    sections_invoked: Optional[str] = None
    case_action: Optional[str] = None

    investigating_officer: str
    case_status: str
    last_update: Optional[datetime] = None

# Caste Certificate Model
# table name = caste_certificates
# constraints :
    # CONSTRAINT fk_caste_cert_aadhaar FOREIGN KEY (aadhaar_number)
    #     REFERENCES aadhaar_records(aadhaar_id) ON DELETE RESTRICT ON UPDATE CASCADE
class CasteCertificate(BaseModel):
    certificate_id: str                 # VARCHAR(32)
    aadhaar_number: int                 # BIGINT -> use int in Python
    person_name: str                    # person_name (VARCHAR)
    caste_category: str                 # e.g., 'SC','ST','OBC','General'
    caste_name: Optional[str] = None    # sub-caste / tribe name
    issue_date: Optional[date] = None
    issuing_authority: Optional[str] = None
    verification_date: Optional[date] = None
    certificate_status: Optional[str] = None   # active, pending, expired, etc.
    remarks: Optional[str] = None

# NPCI Bank KYC
# table name = npci_bank_kyc
# constraints :
    # CONSTRAINT fk_npci_primary_aadhaar FOREIGN KEY (primary_aadhaar)
    #     REFERENCES aadhaar_records(aadhaar_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    # CONSTRAINT fk_npci_secondary_aadhaar FOREIGN KEY (secondary_aadhaar)
    #     REFERENCES aadhaar_records(aadhaar_id) ON DELETE RESTRICT ON UPDATE CASCADE
class NPCIBankKYC(BaseModel):
    kyc_id: str                         # VARCHAR(32)
    account_number: str                 # VARCHAR(32)
    account_type: Optional[str] = None  # 'JOINT', 'SAVINGS', etc.
    
    primary_holder_name: str
    primary_aadhaar: int
    primary_caste_category: Optional[str] = None

    secondary_holder_name: Optional[str] = None
    secondary_aadhaar: Optional[int] = None
    secondary_caste_category: Optional[str] = None

    bank_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    kyc_status: Optional[str] = None        # verified, pending, rejected
    kyc_completed_on: Optional[date] = None
    remarks: Optional[str] = None

# table name = treasury
class TreasuryRecord(BaseModel):
    id: int
    transaction_id: Optional[str] = None

    case_id: Optional[str] = None
    case_type: Optional[str] = None  # 'ATROCITY' or 'ICM'

    amount: float
    transaction_type: str            # 'CREDIT' or 'DEBIT'

    balance_after: float

    initiated_by: Optional[str] = None
    state: str
    district: str
    remark: Optional[str] = None

    transaction_time: datetime

class TreasuryTransaction(BaseModel):
    amount: float
    transaction_id: Optional[str] = None
    transaction_type: Optional[Literal['CREDIT', 'DEBIT']]
    state: str
    district: str
    remark: Optional[str]

# table name = AtrocitySections 
class AtrocitySection(BaseModel):
    id: int
    Section: str
    OffenseDescription: str
    MinimumCompensation: float
    PaymentStages: Optional[str] = None

    class Config:
        orm_mode = True
