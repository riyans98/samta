# app/schemas/auth_schemas.py
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional

# Base Model


RolesType = Literal[
    "State Nodal Officer",
    "Tribal Officer",
    "District Collector/DM/SJO",
    "Investigation Officer",
    "PFMS Officer"
]

class BaseOfficer(BaseModel):
    """Base model for data insertion."""
    login_id: str = Field(..., max_length=255)
    password: str = Field(..., max_length=255)
    role: RolesType = Field(..., max_length=50)
    state_ut: str = Field(..., max_length=100)

class StateNodalOfficer(BaseOfficer):
    pass

class DistrictLvlOfficer(BaseOfficer):
    district: str = Field(..., max_length=100)

class PFMSOfficer(DistrictLvlOfficer):
    """
    PFMS Officer - operates at district level for fund release operations.
    Inherits district field from DistrictLvlOfficer.
    """
    pass

class VisheshThanaOfficer(DistrictLvlOfficer):
    # By default, FastAPI Pydantic field names ko use karta hai. 
    # 'visbesh_p_s_name' ko 'visbesh_p_s_name' hi rehne dete hain, 'alias' ki zarurat nahi hai agar input aur model field same ho.
    vishesh_p_s_name: Optional[str] = Field(None, max_length=100) 
    # example_name field ko hata diya gaya hai, kyunki yeh production data ke liye relevant nahi lag raha.

# Model for the Login Endpoint
class LoginCredentials(BaseModel):
    login_id: str
    password: str
    role: RolesType

# Model for JWT Response
class Token(BaseModel):
    access_token: str

class Officer(BaseModel):
    login_id: str
    role: RolesType
    state_ut: str
    district: Optional[str] = None
    vishesh_p_s_name: Optional[str] = None

class OfficerResponse(Officer, Token):
    pass

# table name = citizen_users
class CitizenUser(BaseModel):
    citizen_id: Optional[int] = None          # AUTO_INCREMENT, returned from DB

    login_id: str
    password_hash: str

    aadhaar_number: int
    caste_certificate_id: Optional[str] = None

    full_name: str
    mobile_number: str
    email: Optional[EmailStr] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Citizen Login Schemas
class CitizenLoginCredentials(BaseModel):
    """Model for citizen login request."""
    login_id: str
    password: str


class CitizenUserResponse(BaseModel):
    """Response model for citizen user data (without password_hash)."""
    citizen_id: int
    login_id: str
    aadhaar_number: int
    caste_certificate_id: Optional[str] = None
    full_name: str
    mobile_number: str
    email: Optional[EmailStr] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CitizenLoginResponse(CitizenUserResponse):
    """Response model for citizen login with JWT token."""
    access_token: str


# Citizen Data with Aadhaar Info
class AadhaarDataResponse(BaseModel):
    """Aadhaar data fetched from govt database."""
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
    email: Optional[EmailStr] = None
    enrollment_date: date
    last_update: Optional[datetime] = None
    mobile_verified: bool
    email_verified: bool
    status: str


class CitizenDataWithAadhaar(CitizenUserResponse):
    """Citizen user data enriched with Aadhaar information."""
    aadhaar_data: Optional[AadhaarDataResponse] = None