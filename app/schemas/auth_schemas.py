# app/schemas/auth_schemas.py
from pydantic import BaseModel, Field
from typing import Optional

# Base Model
class BaseOfficer(BaseModel):
    """Base model for data insertion."""
    login_id: str = Field(..., max_length=255)
    password: str = Field(..., max_length=255)
    role: str = Field(..., max_length=50)
    state_ut: str = Field(..., max_length=100)

class StateNodalOfficer(BaseOfficer):
    pass

class DistrictLvlOfficer(BaseOfficer):
    district: str = Field(..., max_length=100)

class VisheshThanaOfficer(DistrictLvlOfficer):
    # By default, FastAPI Pydantic field names ko use karta hai. 
    # 'visbesh_p_s_name' ko 'visbesh_p_s_name' hi rehne dete hain, 'alias' ki zarurat nahi hai agar input aur model field same ho.
    vishesh_p_s_name: Optional[str] = Field(None, max_length=100) 
    # example_name field ko hata diya gaya hai, kyunki yeh production data ke liye relevant nahi lag raha.

# Model for the Login Endpoint
class LoginCredentials(BaseModel):
    login_id: str
    password: str
    role: str

# Model for JWT Response
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str