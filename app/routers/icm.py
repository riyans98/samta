# app/routers/icm.py
"""
ICM (Inter-Caste Marriage) Routes

Handles all API endpoints for Inter-Caste Marriage applications.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional, List
from pydantic import BaseModel

from app.core.security import verify_jwt_token
from app.schemas.icm_schemas import ICMApplication, ICMEvent
from app.services.icm_service import (
    get_user_icm_applications,
    create_icm_application,
    approve_icm_application,
    reject_icm_application,
    get_icm_applications_by_jurisdiction,
    request_icm_correction
)
from app.db.icm_session import get_icm_events_by_application


router = APIRouter(
    prefix="/icm",
    tags=["ICM Application Management"],
)


# ======================== REQUEST/RESPONSE MODELS ========================

class CreateICMApplicationRequest(BaseModel):
    """Request model for creating ICM application"""
    groom_name: str
    groom_age: int
    groom_father_name: str
    groom_dob: str  # YYYY-MM-DD
    groom_aadhaar: int
    groom_caste_cert_id: Optional[str] = None
    
    bride_name: str
    bride_age: int
    bride_father_name: str
    bride_dob: str  # YYYY-MM-DD
    bride_aadhaar: int
    bride_caste_cert_id: Optional[str] = None
    
    marriage_date: str  # YYYY-MM-DD
    joint_account_number: str
    joint_ifsc: Optional[str] = None


class ApproveICMRequest(BaseModel):
    """Request model for approving ICM application"""
    comment: Optional[str] = None


class RejectICMRequest(BaseModel):
    """Request model for rejecting ICM application"""
    reason: str


class CorrectionRequest(BaseModel):
    """Request model for requesting corrections"""
    corrections_required: List[str]
    comment: Optional[str] = None


# ======================== CITIZEN ENDPOINTS ========================

@router.post("/applications", status_code=status.HTTP_201_CREATED)
async def submit_icm_application(
    application: CreateICMApplicationRequest,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Submit a new ICM application.
    
    Requires JWT token (citizen must be authenticated).
    """
    citizen_id = token_payload.get("citizen_id")
    if not citizen_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Citizen ID missing from token"
        )
    
    # Prepare application data
    app_data = application.model_dump()
    app_data['citizen_id'] = citizen_id
    app_data['applicant_aadhaar'] = token_payload.get("aadhaar_number")
    app_data['state_ut'] = token_payload.get("state_ut", "")
    app_data['district'] = token_payload.get("district", "")
    app_data['current_stage'] = 0
    app_data['pending_at'] = 'ADM'
    app_data['application_status'] = 'Pending'
    
    # Create application
    result = create_icm_application(app_data)
    
    return {
        "icm_id": result["icm_id"],
        "status": "created",
        "current_stage": result["current_stage"],
        "pending_at": result["pending_at"],
        "message": result["message"]
    }


@router.get("/applications", response_model=List[dict])
async def get_citizen_applications(
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get all ICM applications for the authenticated citizen.
    
    Requires JWT token (citizen must be authenticated).
    """
    citizen_id = token_payload.get("citizen_id")
    if not citizen_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Citizen ID missing from token"
        )
    
    applications = get_user_icm_applications(citizen_id)
    return applications


@router.get("/applications/{icm_id}")
async def get_icm_application_details(
    icm_id: int,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get details of a specific ICM application with timeline.
    """
    from app.db.icm_session import get_icm_application_by_id
    
    application = get_icm_application_by_id(icm_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ICM Application #{icm_id} not found"
        )
    
    # Get events/timeline
    events = get_icm_events_by_application(icm_id)
    
    return {
        "application": application.model_dump(),
        "timeline": [event.model_dump() for event in events]
    }


# ======================== ADMIN/OFFICER ENDPOINTS ========================

@router.post("/applications/{icm_id}/approve", status_code=status.HTTP_200_OK)
async def approve_application(
    icm_id: int,
    payload: ApproveICMRequest,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Approve an ICM application and move to next stage.
    
    Only officers (ADM, TO, DM, SNO, PFMS) can approve.
    """
    role = token_payload.get("role")
    if role not in ("ADM", "TO", "DM", "SNO", "PFMS", "Tribal Officer", "District Collector/DM/SJO", "State Nodal Officer", "PFMS Officer"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only officers can approve applications"
        )
    
    result = approve_icm_application(
        icm_id=icm_id,
        actor=token_payload.get("sub"),
        role=role,
        comment=payload.comment
    )
    
    return result


@router.post("/applications/{icm_id}/reject", status_code=status.HTTP_200_OK)
async def reject_application(
    icm_id: int,
    payload: RejectICMRequest,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Reject an ICM application.
    
    Only officers can reject applications.
    """
    role = token_payload.get("role")
    if role not in ("ADM", "TO", "DM", "SNO", "PFMS", "Tribal Officer", "District Collector/DM/SJO", "State Nodal Officer", "PFMS Officer"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only officers can reject applications"
        )
    
    result = reject_icm_application(
        icm_id=icm_id,
        actor=token_payload.get("sub"),
        role=role,
        reason=payload.reason
    )
    
    return result


@router.post("/applications/{icm_id}/request-correction", status_code=status.HTTP_200_OK)
async def request_correction(
    icm_id: int,
    payload: CorrectionRequest,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Request corrections for an ICM application.
    
    Officers can request corrections which sends application back to citizen.
    """
    role = token_payload.get("role")
    if role not in ("ADM", "TO", "DM", "SNO", "PFMS", "Tribal Officer", "District Collector/DM/SJO", "State Nodal Officer", "PFMS Officer"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only officers can request corrections"
        )
    
    result = request_icm_correction(
        icm_id=icm_id,
        actor=token_payload.get("sub"),
        role=role,
        corrections_required=payload.corrections_required,
        comment=payload.comment
    )
    
    return result


@router.get("/applications", tags=["Admin"])
async def get_all_applications_filtered(
    state_ut: str,
    district: Optional[str] = None,
    pending_at: Optional[str] = None,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get ICM applications filtered by jurisdiction and status.
    
    Admin/Officers only endpoint.
    """
    role = token_payload.get("role")
    if role not in ("ADM", "TO", "DM", "SNO", "PFMS", "Tribal Officer", "District Collector/DM/SJO", "State Nodal Officer", "PFMS Officer"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only officers can view all applications"
        )
    
    applications = get_icm_applications_by_jurisdiction(
        state_ut=state_ut,
        district=district,
        pending_at=pending_at
    )
    
    return applications


@router.get("/applications/{icm_id}/timeline")
async def get_application_timeline(
    icm_id: int,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get complete timeline/events for an ICM application.
    """
    from app.db.icm_session import get_icm_application_by_id
    
    application = get_icm_application_by_id(icm_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ICM Application #{icm_id} not found"
        )
    
    events = get_icm_events_by_application(icm_id)
    
    return {
        "icm_id": icm_id,
        "current_stage": application.current_stage,
        "status": application.application_status,
        "timeline": [event.model_dump() for event in events]
    }
