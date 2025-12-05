# app/routers/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
from typing import Dict, Any, Optional, List

from app.core.config import settings
from app.core.security import create_access_token, execute_login_query, verify_jwt_token, verify_password
from app.schemas.auth_schemas import LoginCredentials, Token, Officer, OfficerResponse, RolesType, CitizenLoginCredentials, CitizenLoginResponse, CitizenDataWithAadhaar
from app.db.session import get_citizen_by_login_id
from app.db.govt_session import get_aadhaar_by_number, get_fir_by_number

# Router object banane se hum is file ko main app se alag kar sakte hain
router = APIRouter(
    prefix="", # No prefix for global endpoints like /login
    tags=["Authentication"],
)

@router.post("/login", response_model=OfficerResponse)
async def login_user(credentials: LoginCredentials):
    """Authenticates a user and issues a JWT access token."""
    
    # Is mapping ko security.py se yahan move kiya gaya hai taaki business logic (roles) router mein rahe
    role_to_table: Dict[RolesType, str] = {
        "State Nodal Officer": "State_Nodal_Officers",
        "Tribal Officer": "District_lvl_Officers",
        "District Collector/DM/SJO": "District_lvl_Officers",
        "Investigation Officer": "Vishesh_Thana_Officers",
        "PFMS Officer": "District_lvl_Officers"
    }
    
    table_name = role_to_table.get(credentials.role)
    
    if not table_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role selected.")

    # Execute login query in security module
    # For District_lvl_Officers, also pass the role to prevent role confusion
    # (Tribal Officer, District Collector/DM/SJO, and PFMS Officer all use this table)
    user_info: Optional[Dict[str, Any]] = execute_login_query(
        table_name, 
        credentials.login_id, 
        credentials.password,
        role=credentials.role if table_name == "District_lvl_Officers" else None
    )

    if user_info:
        # Create data payload for the token (sub = subject/login_id)
        # Keys are guaranteed to be lowercase from execute_login_query's normalization
        # Include jurisdiction fields for access control
        
        # IMPORTANT: Override the role from database with the role selected during login
        # This ensures that if both DM and TO are in the same table, the user gets the role they logged in with
        user_info['role'] = credentials.role
        
        # Extract jurisdiction fields - they should be lowercase from normalized_data
        state_ut = user_info.get('state_ut')
        district = user_info.get('district')
        vishesh_p_s_name = user_info.get('vishesh_p_s_name')
        
        token_payload = {
            "sub": user_info['login_id'], 
            "role": credentials.role,  # Use the role selected during login, not DB role
            "state_ut": state_ut,
        }
        
        # Add district for district-level officers (TO, DM, IO)
        if district:
            token_payload['district'] = district
        
        # Add vishesh_p_s_name for Investigation Officers
        if vishesh_p_s_name:
            token_payload['vishesh_p_s_name'] = vishesh_p_s_name
        
        # Debug log (remove in production)
        print(f"JWT Token Payload: {token_payload}")
        
        access_token = create_access_token(
            token_payload,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        user_info['access_token'] = access_token
        
        # Return the access token and the token type
        return user_info
    else:
        # Return 401 Unauthorized for failed authentication
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Login ID or Password for the selected role.")

# Example of a protected endpoint (will be moved to a different router later)
@router.get("/user/me")
async def get_current_user(token_payload: dict = Depends(verify_jwt_token)):
    """Fetches current user info. Requires valid JWT token."""
    return {
        "message": "Authenticated user data.",
        "user_id": token_payload.get("sub"),
        "role": token_payload.get("role"),
        "state_ut": token_payload.get("state_ut"),
        "district": token_payload.get("district"),
        "vishesh_p_s_name": token_payload.get("vishesh_p_s_name"),
        "full_payload": token_payload
    }


# ======================== CITIZEN LOGIN ========================

@router.post("/citizen/login", response_model=CitizenLoginResponse)
async def citizen_login(credentials: CitizenLoginCredentials):
    """
    Authenticates a citizen user using login_id and password.
    Returns user data with JWT token on successful authentication.
    """
    # Fetch citizen user from database
    citizen_data = get_citizen_by_login_id(credentials.login_id)
    
    if not citizen_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Login ID or Password."
        )
    
    # Verify password against stored hash
    stored_hash = citizen_data.get('password_hash')
    
    if not stored_hash or not verify_password(credentials.password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Login ID or Password."
        )
    
    # Create JWT token payload for citizen
    token_payload = {
        "sub": citizen_data['login_id'],
        "role": "citizen",
        "citizen_id": citizen_data['citizen_id'],
        "aadhaar_number": citizen_data['aadhaar_number'],
    }
    
    # Generate JWT token
    access_token = create_access_token(
        token_payload,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Build response with user data (excluding password_hash)
    response_data = {
        "citizen_id": citizen_data['citizen_id'],
        "login_id": citizen_data['login_id'],
        "aadhaar_number": citizen_data['aadhaar_number'],
        "caste_certificate_id": citizen_data.get('caste_certificate_id'),
        "full_name": citizen_data['full_name'],
        "mobile_number": citizen_data['mobile_number'],
        "email": citizen_data.get('email'),
        "created_at": citizen_data.get('created_at'),
        "updated_at": citizen_data.get('updated_at'),
        "access_token": access_token
    }
    
    return response_data


# ======================== CITIZEN DATA WITH AADHAAR ========================

@router.get("/citizen/profile", response_model=CitizenDataWithAadhaar)
async def get_citizen_profile(token_payload: dict = Depends(verify_jwt_token)):
    """
    Fetches citizen profile with Aadhaar data enriched from govt database.
    Requires valid JWT token.
    """
    citizen_id = token_payload.get("citizen_id")
    aadhaar_number = token_payload.get("aadhaar_number")
    
    if not citizen_id or not aadhaar_number:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing citizen_id or aadhaar_number"
        )
    
    # Fetch citizen data from citizen_users table
    citizen_data = get_citizen_by_login_id(token_payload.get("sub"))
    
    if not citizen_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Citizen user not found"
        )
    
    # Fetch Aadhaar data from govt database
    aadhaar_data = get_aadhaar_by_number(str(aadhaar_number))
    
    # Build response
    response_data = {
        "citizen_id": citizen_data['citizen_id'],
        "login_id": citizen_data['login_id'],
        "aadhaar_number": citizen_data['aadhaar_number'],
        "caste_certificate_id": citizen_data.get('caste_certificate_id'),
        "full_name": citizen_data['full_name'],
        "mobile_number": citizen_data['mobile_number'],
        "email": citizen_data.get('email'),
        "created_at": citizen_data.get('created_at'),
        "updated_at": citizen_data.get('updated_at'),
        "aadhaar_data": aadhaar_data.model_dump() if aadhaar_data else None
    }
    
    return response_data