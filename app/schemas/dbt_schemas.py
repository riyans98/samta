# app/schemas/dbt_schemas.py
from pydantic import BaseModel, Field, conint, EmailStr, validator
from typing import Optional, Literal
from datetime import date, datetime

# Note: File uploads ke liye hum FastAPI ke UploadFile use karenge, models mein nahi.

class AtrocityBase(BaseModel):
    # --- FIR Details (Partial) ---
    FIR_NO: str # FIR_NO is NOT NULL
    Case_Description: str = Field(..., max_length=500, description="Incident Description from form")

    # --- Victim Details ---
    Victim_Name: str = Field(..., max_length=150)
    Father_Name: str = Field(..., max_length=150, description="Assuming 'relation' maps to Father_Name/Husband_Name in DB")
    Victim_DOB: date # Yahan date object aayega
    Gender: Literal["male", "female", "other"]
    Victim_Mobile_No: str = Field(..., max_length=15, min_length=10)
    Aadhar_No: Optional[int] # Optional as per DB, but required by form. Keeping optional here for DB model match.
    Caste: str = Field(..., max_length=50)

    # --- Bank Details ---
    Bank_Account_No: str = Field(..., max_length=20)
    IFSC_Code: Optional[str] = Field(None, max_length=20)
    Holder_Name: Optional[str] = Field(None, max_length=100)
    Bank_Name: str = Field(..., max_length=100)
    
    # --- Other DB required fields (Initial State) ---
    Stage: conint(ge=0, le=10) = 0
    Pending_At: str = Field("Vishesh Thana Officer", max_length=100)
    Applicant_Name: str = Field(..., max_length=150) # Assuming Victim_Name is the Applicant for now
    Applicant_Relation: Optional[str] = Field(None, max_length=100)
    Applicant_Mobile_No: str = Field(..., max_length=15)
    Applicant_Email: Optional[EmailStr] = Field(None, max_length=100)
    
    # Note: Applied_Acts, Location, Date_of_Incident are missing in the form data, 
    # but required by the ATROCITY table. We'll set them as optional or use placeholders.
    Applied_Acts: Optional[str] = Field(None, max_length=500)
    Location: Optional[str] = Field(None, max_length=200)
    Date_of_Incident: Optional[date] = None


    class Config:
        # Allows accessing fields by their alias (e.g., 'relation' in input maps to 'Father_Name' in model)
        populate_by_name = True 
        # For date objects (DOB)
        json_encoders = {date: lambda v: v.isoformat()}