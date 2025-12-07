from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, Optional
from datetime import date, datetime

# table name = icm_applications
class ICMApplication(BaseModel):
    """
    Pydantic model representing an application in the ICM system,
    aligned with the icm_applications SQL table.
    """
    model_config = ConfigDict(populate_by_name=True)

    # --- Primary/Applicant Details ---
    icm_id: int                                   
    citizen_id: int                               
    applicant_aadhaar: int                        

    # --- Groom Details ---
    groom_name: str
    groom_age: int
    groom_father_name: str
    groom_pre_address: str                        
    groom_current_address: str
    groom_permanent_address: str                  
    groom_aadhaar: int
    groom_caste_cert_id: Optional[str] = None     
    groom_dob: date
    groom_education: Optional[str] = None
    groom_training: Optional[str] = None
    groom_income: Optional[str] = None            
    groom_livelihood: Optional[str] = None        
    groom_future_plan: Optional[str] = None
    groom_first_marriage: Optional[bool] = True   

    # --- Bride Details ---
    bride_name: str
    bride_age: int
    bride_father_name: str
    bride_pre_address: str                        
    bride_current_address: str
    bride_permanent_address: str                  
    bride_aadhaar: int
    bride_caste_cert_id: Optional[str] = None     
    bride_dob: date
    bride_education: Optional[str] = None
    bride_training: Optional[str] = None
    bride_income: Optional[str] = None            
    bride_livelihood: Optional[str] = None        
    bride_future_plan: Optional[str] = None
    bride_first_marriage: Optional[bool] = True   

    # --- Marriage Details ---
    marriage_date: date
    marriage_certificate_number: Optional[str] = Field(default=None, alias='marriage_cert_number')
    marriage_certificate_file: Optional[str] = Field(default=None, alias='marriage_cert_file')
    previous_benefit_taken: Optional[bool] = False 

    # --- File Uploads ---
    joint_photo_file: Optional[str] = None
    groom_signature_file: Optional[str] = None
    bride_signature_file: Optional[str] = None

    # --- Witness Details ---
    witness_name: Optional[str] = None
    witness_aadhaar: Optional[int] = None
    witness_address: Optional[str] = None         
    witness_signature_file: Optional[str] = None
    witness_verified: Optional[bool] = False      

    # --- Joint Bank Account Details ---
    joint_account_number: str
    joint_ifsc: Optional[str] = None              
    joint_passbook_file: Optional[str] = None
    joint_account_bank_name: Optional[str] = None

    # --- Jurisdiction ---
    state_ut: str
    district: str

    # --- Workflow ---
    current_stage: int = 0                        
    pending_at: str = 'Tribal Officer'                       
    application_status: str = 'Pending'           

    # --- Timestamps ---
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# table name = icm_events
class ICMEvent(BaseModel):
    """
    Pydantic model for an application event, aligned with the icm_events SQL table.
    """
    # Keys
    event_id: int                                      
    icm_id: int                                        # Foreign key for icm_applications

    # Core Event Details
    event_type: str                                    # e.g., ADM_APPROVED, TO_CORRECTION, PFMS_FUND_RELEASED
    event_role: str                                    # e.g., ADM, TO, DM, SNO, PFMS, CITIZEN
    event_stage: int                                   # The application stage number (INT NOT NULL)

    # Optional Details
    comment: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = None        # Maps to the JSON column

    # Timestamp
    created_at: Optional[datetime] = None              