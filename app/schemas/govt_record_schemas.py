from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime

# Aadhaar Model
class AadhaarRecord(BaseModel):
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
class FIRRecord(BaseModel):
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

    investigating_officer: str
    case_status: str
    last_update: Optional[datetime] = None