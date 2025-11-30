# app/routers/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
from typing import Dict, Any

from app.core.config import settings
from app.core.security import create_access_token, execute_login_query, verify_jwt_token
from app.schemas.auth_schemas import LoginCredentials, Token

# Router object banane se hum is file ko main app se alag kar sakte hain
router = APIRouter(
    prefix="", # No prefix for global endpoints like /login
    tags=["Authentication"],
)

@router.post("/login", response_model=Token)
async def login_user(credentials: LoginCredentials):
    """Authenticates a user and issues a JWT access token."""
    
    # Is mapping ko security.py se yahan move kiya gaya hai taaki business logic (roles) router mein rahe
    role_to_table = {
        "State Nodal Officer": "State_Nodal_Officers",
        "Tribal Officer": "District_lvl_Officers",
        "District Collector/DM/SJO": "District_lvl_Officers",
        "Vishesh Thana Officer": "Vishesh_Thana_Officers"
    }
    
    table_name = role_to_table.get(credentials.role)
    
    if not table_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role selected.")

    # Execute login query in security module
    user_info: Optional[Dict[str, Any]] = execute_login_query(
        table_name, 
        credentials.login_id, 
        credentials.password
    )

    if user_info:
        # Create data payload for the token (sub = subject/login_id)
        # Keys are guaranteed to be lowercase from execute_login_query's normalization
        token_payload = {"sub": user_info['login_id'], "role": user_info['role']}
        
        access_token = create_access_token(
            token_payload,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Return the access token and the token type
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "role": user_info['role']
        }
    else:
        # Return 401 Unauthorized for failed authentication
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Login ID or Password for the selected role.")

# Example of a protected endpoint (will be moved to a different router later)
@router.get("/user/me")
async def get_current_user(token_payload: dict = Depends(verify_jwt_token)):
    """Fetches current user info. Requires valid JWT token."""
    return {"message": "Authenticated user data.", "user_id": token_payload.get("sub"), "role": token_payload.get("role")}