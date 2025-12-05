# app/routers/admin.py
from fastapi import APIRouter, Depends, status, HTTPException

from app.core.security import api_key_auth, hash_password
from app.db.session import execute_insert, execute_update_users
from app.schemas.auth_schemas import StateNodalOfficer, DistrictLvlOfficer, VisheshThanaOfficer, PFMSOfficer, RolesType

# Admin router, secured by the api_key_auth dependency at the router level
router = APIRouter(
    prefix="", # No prefix required, endpoints will be prefixed in main.py if needed
    tags=["Admin"],
    # Yahan Admin API Key Dependency lagana behtar hai, agar saare endpoints protected hon
    # dependencies=[Depends(api_key_auth)] 
)

# Admin Endpoints (Secured by API Key per endpoint)
@router.post("/state_nodal_officers", status_code=status.HTTP_201_CREATED)
async def create_state_nodal_officer(
    officer: StateNodalOfficer, 
    key: str = Depends(api_key_auth)
):
    # Password Hash karna
    hashed_pass = hash_password(officer.password)
    # DB me insert karna
    return execute_insert("State_Nodal_Officers", officer.model_dump(), hashed_pass)

@router.post("/district_lvl_officers", status_code=status.HTTP_201_CREATED)
async def create_district_lvl_officer(
    officer_data: dict, 
    key: str = Depends(api_key_auth)
):
    """
    Register district-level officers: Tribal Officer, District Collector/DM/SJO, or PFMS Officer.
    
    For Tribal Officer / District Collector / PFMS Officer:
    - role: "Tribal Officer", "District Collector/DM/SJO", or "PFMS Officer"
    - district: Required (district name for all three roles)
    """
    role = officer_data.get("role")
    
    # Validate role
    if role not in [
    "State Nodal Officer",
    "Tribal Officer",
    "District Collector/DM/SJO",
    "Investigation Officer",
    "PFMS Officer",
    "ADM"
]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role for district_lvl_officers. Allowed: Tribal Officer, District Collector/DM/SJO, PFMS Officer"
        )
    
    # District is required for all three roles
    if not officer_data.get("district"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"District is required for {role}"
        )
    
    # Create schema based on role
    if role == "PFMS Officer":
        officer = PFMSOfficer(**officer_data)
    else:
        officer = DistrictLvlOfficer(**officer_data)
    
    hashed_pass = hash_password(officer.password)
    return execute_insert("District_lvl_Officers", officer.model_dump(), hashed_pass)

# @router.patch("/citizen_users", status_code=status.HTTP_201_CREATED)
async def create_citizen_user():
    # Pydantic ke .dict(by_alias=True) ki jagah, hum officer.model_dump() use kar rahe hain, jo pydantic v2 ka standard hai. 
    # Agar model me koi alias hota toh use karna padta, but yahan direct field names hain.
    try:
        for i in range(1, 11):
            hashed_pass = hash_password('123')
            execute_update_users(i, hashed_pass)
        return "success"
    except Exception as e:
        return "failed"

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_vishesh_thana_officer(
    officer: VisheshThanaOfficer, 
    key: str = Depends(api_key_auth)
):
    # Pydantic ke .dict(by_alias=True) ki jagah, hum officer.model_dump() use kar rahe hain, jo pydantic v2 ka standard hai. 
    # Agar model me koi alias hota toh use karna padta, but yahan direct field names hain.
    hashed_pass = hash_password(officer.password)
    officer.role = "Investigation Officer"
    return execute_insert("Vishesh_Thana_Officers", officer.model_dump(exclude_none=True), hashed_pass)