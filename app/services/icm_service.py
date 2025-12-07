# app/services/icm_service.py
"""
ICM (Inter-Caste Marriage) Service Layer

Business logic for ICM application management with proper workflow:
- Stage flow: 0 → 1 → 2 → 3 → 4 → 5 (Completed)
- Roles: Citizen, Tribal Officer, District Collector/DM/SJO, State Nodal Officer, PFMS Officer
- Every action creates an event
- Centralized jurisdiction checks
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status, UploadFile

from app.core.config import settings
from app.db.icm_session import (
    get_icm_application_by_id,
    get_all_icm_applications,
    get_icm_applications_by_citizen,
    insert_icm_application,
    update_icm_application,
    insert_icm_event
)
from app.schemas.icm_schemas import ICMApplication
from app.services.icm_utils import (
    ROLE_CITIZEN, ROLE_TO, ROLE_DM, ROLE_SNO, ROLE_PFMS,
    OFFICER_ROLES,
    STAGE_SUBMITTED, STAGE_COMPLETED,
    ROLE_STAGE_MAP, NEXT_STAGE_MAP, STAGE_PENDING_AT_MAP, EVENT_TYPE_MAP,
    assert_jurisdiction,
    validate_role_for_stage,
    get_next_stage,
    get_pending_at_for_stage,
    get_event_type,
    validate_applicant_is_partner,
    validate_aadhaar_exists,
    check_duplicate_couple,
    check_aadhaar_in_approved_applications
)
from app.services.icm_storage import save_icm_file, get_icm_documents

logger = logging.getLogger(__name__)


# ======================== EVENT HELPER ========================

def append_icm_event(
    icm_id: int,
    event_type: str,
    event_role: str,
    event_stage: int,
    comment: Optional[str] = None,
    event_data: Optional[Dict[str, Any]] = None
) -> int:
    """
    Standalone function to append an ICM event.
    Every workflow action MUST create an event.
    
    Args:
        icm_id: Application ID
        event_type: Type of event (APPLICATION_SUBMITTED, ADM_APPROVED, etc.)
        event_role: Role that triggered event
        event_stage: Current stage when event occurred
        comment: Optional comment
        event_data: Optional additional data as JSON
    
    Returns:
        event_id of created event
    """
    logger.info(f"ICM event: {event_type}, icm_id={icm_id}, role={event_role}, stage={event_stage}")
    return insert_icm_event(
        icm_id=icm_id,
        event_type=event_type,
        event_role=event_role,
        event_stage=event_stage,
        comment=comment,
        event_data=event_data
    )


# ======================== APPLICATION RETRIEVAL ========================

def get_user_icm_applications(citizen_id: int) -> List[Dict[str, Any]]:
    """
    Get all ICM applications for a specific citizen.
    
    Args:
        citizen_id: Citizen ID to fetch applications for
    
    Returns:
        List of ICM applications as dictionaries
    """
    applications = get_icm_applications_by_citizen(citizen_id)
    return [app.model_dump() for app in applications]


def get_icm_applications_by_jurisdiction(
    state_ut: str,
    district: Optional[str] = None,
    pending_at: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get ICM applications filtered by jurisdiction and status.
    
    Args:
        state_ut: State/UT filter (required)
        district: District filter (optional)
        pending_at: Pending at role filter (optional)
    
    Returns:
        List of filtered applications
    """
    all_applications = get_all_icm_applications()

    filtered = []
    for app in all_applications:
        # Filter by state
        if app.state_ut.lower() != state_ut.lower():
            continue
        
        # Filter by district if provided
        if district and app.district.lower() != district.lower():
            continue
        
        # Filter by pending_at if provided
        if pending_at and app.pending_at.lower() != pending_at.lower():
            continue
        
        filtered.append(app.model_dump())
    
    return filtered


# ======================== APPLICATION CREATION ========================

async def create_icm_application_with_files(
    application_data: Dict[str, Any],
    files: Dict[str, Optional[UploadFile]],
    token_payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a new ICM application with file uploads.
    
    Validates:
    1. Applicant must be groom or bride
    2. Both Aadhaar numbers must exist
    3. No duplicate couple with active application
    4. Neither person has already received benefit
    
    Args:
        application_data: Form field data
        files: Dictionary of uploaded files
        token_payload: JWT token payload
    
    Returns:
        Created application details
    
    Raises:
        HTTPException: On validation or creation failure
    """
    citizen_id = token_payload.get("citizen_id")
    applicant_aadhaar = token_payload.get("aadhaar_number")
    groom_aadhaar = application_data.get("groom_aadhaar")
    bride_aadhaar = application_data.get("bride_aadhaar")
    
    # Validation 1: Applicant must be one of the partners
    validate_applicant_is_partner(applicant_aadhaar, groom_aadhaar, bride_aadhaar)
    
    # Validation 2: Verify Aadhaar numbers exist (soft validation - logs warning on error)
    validate_aadhaar_exists(groom_aadhaar, "Groom Aadhaar")
    validate_aadhaar_exists(bride_aadhaar, "Bride Aadhaar")
    
    # Validation 3: Check for duplicate couple with active application
    check_duplicate_couple(groom_aadhaar, bride_aadhaar)
    
    # Validation 4: Check if either person already received benefit
    check_aadhaar_in_approved_applications(groom_aadhaar, bride_aadhaar)
    
    # Prepare application data
    application_data['citizen_id'] = citizen_id
    application_data['applicant_aadhaar'] = applicant_aadhaar
    application_data['state_ut'] = token_payload.get("state_ut", "")
    application_data['district'] = token_payload.get("district", "")
    application_data['current_stage'] = STAGE_SUBMITTED  # 0
    application_data['pending_at'] = ROLE_TO  # Tribal Officer (TO)
    application_data['application_status'] = 'Pending'
    
    try:
        # Insert application (without file paths initially)
        icm_id = insert_icm_application(application_data)
        
        logger.info(f"ICM application created: icm_id={icm_id}, citizen_id={citizen_id}")
        
        # Save files and update application with file paths
        file_paths = {}
        uploader = f"citizen_{citizen_id}"
        
        # MARRIAGE certificate
        if files.get('marriage_certificate'):
            filename = await save_icm_file(icm_id, files['marriage_certificate'], 'MARRIAGE', uploader)
            if filename:
                file_paths['marriage_certificate_file'] = filename
        
        # GROOM_SIGN
        if files.get('groom_signature'):
            filename = await save_icm_file(icm_id, files['groom_signature'], 'GROOM_SIGN', uploader)
            if filename:
                file_paths['groom_signature_file'] = filename
        
        # BRIDE_SIGN
        if files.get('bride_signature'):
            filename = await save_icm_file(icm_id, files['bride_signature'], 'BRIDE_SIGN', uploader)
            if filename:
                file_paths['bride_signature_file'] = filename
        
        # WITNESS_SIGN (optional)
        if files.get('witness_signature'):
            filename = await save_icm_file(icm_id, files['witness_signature'], 'WITNESS_SIGN', uploader)
            if filename:
                file_paths['witness_signature_file'] = filename
        
        # Update application with file paths
        if file_paths:
            update_icm_application(icm_id, file_paths)
        
        # Create APPLICATION_SUBMITTED event
        event_data = {
            "action": "submitted",
            "applicant_aadhaar": applicant_aadhaar,
            "groom_aadhaar": groom_aadhaar,
            "bride_aadhaar": bride_aadhaar,
            "files": list(file_paths.keys())
        }
        
        append_icm_event(
            icm_id=icm_id,
            event_type="APPLICATION_SUBMITTED",
            event_role=ROLE_CITIZEN,
            event_stage=STAGE_SUBMITTED,
            comment="Application submitted by citizen",
            event_data=event_data
        )
        
        return {
            "icm_id": icm_id,
            "status": "created",
            "message": "ICM application created successfully",
            "current_stage": STAGE_SUBMITTED,
            "pending_at": ROLE_TO
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create ICM application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ICM application: {str(e)}"
        )


def create_icm_application(application_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Legacy function - Creates ICM application without files.
    Kept for backward compatibility.
    
    Args:
        application_data: Application data dictionary
    
    Returns:
        Created application with ID and status
    """
    try:
        icm_id = insert_icm_application(application_data)
        
        # Insert initial event
        append_icm_event(
            icm_id=icm_id,
            event_type="APPLICATION_SUBMITTED",
            event_role=ROLE_CITIZEN,
            event_stage=STAGE_SUBMITTED,
            comment="Application created",
            event_data={"action": "created"}
        )
        
        return {
            "icm_id": icm_id,
            "status": "created",
            "message": "ICM application created successfully",
            "current_stage": STAGE_SUBMITTED,
            "pending_at": ROLE_TO
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ICM application: {e}"
        )


# ======================== APPROVAL WORKFLOW ========================

def approve_icm_application(
    icm_id: int,
    actor: str,
    role: str,
    comment: Optional[str] = None,
    token_payload: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Approves an ICM application and moves to next stage.
    
    Stage Flow:
    - Stage 0 (ADM): approves → Stage 1 (Tribal Officer)
    - Stage 1 (TO): approves → Stage 2 (DM)
    - Stage 2 (DM): approves → Stage 3 (SNO)
    - Stage 3 (SNO): approves → Stage 4 (PFMS)
    - Stage 4 (PFMS): approves via pfms_release → Stage 5 → Stage 6 (Completed)
    
    Args:
        icm_id: Application ID
        actor: User approving (login_id)
        role: Role of approver
        comment: Optional comment
        token_payload: JWT token for jurisdiction check
    
    Returns:
        Updated application status
    
    Raises:
        HTTPException: If validation fails
    """
    application = get_icm_application_by_id(icm_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ICM Application #{icm_id} not found"
        )
    
    # Jurisdiction check
    if token_payload:
        assert_jurisdiction(token_payload, application)
    
    # Validate role can act on current stage
    if not validate_role_for_stage(role, application.current_stage):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role {role} cannot approve at stage {application.current_stage}"
        )
    
    # Get next stage and pending_at
    current_stage = application.current_stage
    next_stage = get_next_stage(current_stage)
    next_pending_at = get_pending_at_for_stage(next_stage)
    
    # Determine application status
    if next_stage == STAGE_COMPLETED:
        app_status = "Completed"
    else:
        app_status = "Under Review"
    
    # Update application
    update_payload = {
        "current_stage": next_stage,
        "pending_at": next_pending_at,
        "application_status": app_status
    }
    
    success = update_icm_application(icm_id, update_payload)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve application"
        )
    
    # Get event type for this role
    event_type = get_event_type(role, "approve")
    
    # Insert approval event
    event_data = {
        "actor": actor,
        "role": role,
        "previous_stage": current_stage,
        "new_stage": next_stage,
        "comment": comment
    }
    
    append_icm_event(
        icm_id=icm_id,
        event_type=event_type,
        event_role=role,
        event_stage=current_stage,
        comment=comment,
        event_data=event_data
    )
    
    logger.info(f"ICM action: approve, icm_id={icm_id}, user={actor}, role={role}")
    
    return {
        "icm_id": icm_id,
        "previous_stage": current_stage,
        "new_stage": next_stage,
        "pending_at": next_pending_at,
        "approved_by": role,
        "message": f"Application approved and moved to stage {next_stage}"
    }


def reject_icm_application(
    icm_id: int,
    actor: str,
    role: str,
    reason: str,
    token_payload: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Rejects an ICM application.
    
    Any officer can reject, but typically DM rejects.
    Sets application_status='Rejected' and pending_at=NULL.
    
    Args:
        icm_id: Application ID
        actor: User rejecting
        role: Role of user
        reason: Reason for rejection
        token_payload: JWT token for jurisdiction check
    
    Returns:
        Updated application status
    """
    application = get_icm_application_by_id(icm_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ICM Application #{icm_id} not found"
        )
    
    # Jurisdiction check
    if token_payload:
        assert_jurisdiction(token_payload, application)
    
    current_stage = application.current_stage
    
    # Update application
    update_payload = {
        "application_status": "Rejected",
        "pending_at": None
    }
    
    success = update_icm_application(icm_id, update_payload)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject application"
        )
    
    # Get event type (DM_REJECTED for DM, else generic)
    if role == ROLE_DM:
        event_type = "DM_REJECTED"
    else:
        event_type = f"{role.split()[0].upper()}_REJECTED"
    
    # Insert rejection event
    event_data = {
        "actor": actor,
        "role": role,
        "reason": reason,
        "stage_at_rejection": current_stage
    }
    
    append_icm_event(
        icm_id=icm_id,
        event_type=event_type,
        event_role=role,
        event_stage=current_stage,
        comment=reason,
        event_data=event_data
    )
    
    logger.info(f"ICM action: reject, icm_id={icm_id}, user={actor}, role={role}")
    
    return {
        "icm_id": icm_id,
        "status": "Rejected",
        "reason": reason,
        "rejected_by": role
    }


def request_icm_correction(
    icm_id: int,
    actor: str,
    role: str,
    corrections_required: List[str],
    comment: Optional[str] = None,
    token_payload: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Requests corrections for an ICM application.
    
    Any officer can request corrections.
    Resets: stage=0, pending_at='Citizen'
    
    Args:
        icm_id: Application ID
        actor: User requesting correction
        role: Role of user
        corrections_required: List of fields needing correction
        comment: Optional comment
        token_payload: JWT token for jurisdiction check
    
    Returns:
        Correction request details
    """
    application = get_icm_application_by_id(icm_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ICM Application #{icm_id} not found"
        )
    
    # Jurisdiction check
    if token_payload:
        assert_jurisdiction(token_payload, application)
    
    current_stage = application.current_stage
    
    # Reset to stage 0, pending_at Citizen
    update_payload = {
        "current_stage": STAGE_SUBMITTED,  # 0
        "application_status": "Correction Required",
        "pending_at": ROLE_CITIZEN  # "Citizen"
    }
    
    success = update_icm_application(icm_id, update_payload)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request correction"
        )
    
    # Get role-specific event type
    event_type = get_event_type(role, "correction")
    
    # Insert correction event
    event_data = {
        "actor": actor,
        "role": role,
        "corrections_required": corrections_required,
        "comment": comment,
        "stage_before_correction": current_stage
    }
    
    append_icm_event(
        icm_id=icm_id,
        event_type=event_type,
        event_role=role,
        event_stage=current_stage,
        comment=comment,
        event_data=event_data
    )
    
    logger.info(f"ICM action: correction, icm_id={icm_id}, user={actor}, role={role}")
    
    return {
        "icm_id": icm_id,
        "status": "Correction Required",
        "corrections_required": corrections_required,
        "pending_at": ROLE_CITIZEN,
        "requested_by": role
    }


# ======================== PFMS FUND RELEASE ========================

def pfms_release(
    icm_id: int,
    actor: str,
    role: str,
    amount: int,
    txn_id: str,
    bank_ref: Optional[str] = None,
    token_payload: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    PFMS fund release action - completes the ICM application.
    
    Validates:
    - Current stage must be 3 (SNO approved, pending PFMS)
    - Amount should match configured grant (default 250000)
    - Role must be PFMS Officer
    
    Actions:
    - Sets stage to 4 then 5 (Completed)
    - Sets application_status='Completed'
    - Sets pending_at='COMPLETED'
    - Creates PFMS_FUND_RELEASED event
    
    Args:
        icm_id: Application ID
        actor: PFMS officer performing release
        role: Must be "PFMS Officer"
        amount: Amount released (should be 250000)
        txn_id: Transaction ID
        bank_ref: Bank reference (optional)
        token_payload: JWT token for jurisdiction check
    
    Returns:
        Fund release confirmation
    """
    application = get_icm_application_by_id(icm_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ICM Application #{icm_id} not found"
        )
    
    # Jurisdiction check
    if token_payload:
        assert_jurisdiction(token_payload, application)
    
    # Validate role
    if role != ROLE_PFMS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only PFMS Officer can release funds"
        )
    
    # Validate current stage (must be 3 - pending PFMS)
    if application.current_stage != 3:  # STAGE_SNO_APPROVED
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Application must be at stage 3 for fund release. Current stage: {application.current_stage}"
        )
    
    # Validate amount (warning only, don't block)
    configured_amount = settings.ICM_GRANT_AMOUNT
    if amount != configured_amount:
        logger.warning(f"PFMS release amount {amount} differs from configured {configured_amount}")
    
    current_stage = application.current_stage
    
    # Update application to Completed
    update_payload = {
        "current_stage": STAGE_COMPLETED,  # 6
        "application_status": "Completed",
        "pending_at": "COMPLETED"
    }
    
    success = update_icm_application(icm_id, update_payload)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete fund release"
        )
    
    # Insert PFMS_FUND_RELEASED event
    event_data = {
        "actor": actor,
        "role": role,
        "amount": amount,
        "txn_id": txn_id,
        "bank_ref": bank_ref,
        "grant_amount": configured_amount
    }
    
    append_icm_event(
        icm_id=icm_id,
        event_type="PFMS_FUND_RELEASED",
        event_role=role,
        event_stage=current_stage,
        comment=f"Fund released: Rs. {amount}, TxnID: {txn_id}",
        event_data=event_data
    )
    
    logger.info(f"ICM action: pfms_release, icm_id={icm_id}, user={actor}, amount={amount}, txn_id={txn_id}")
    
    return {
        "icm_id": icm_id,
        "status": "Completed",
        "amount_released": amount,
        "txn_id": txn_id,
        "bank_ref": bank_ref,
        "message": "Fund released successfully. Application completed."
    }


# ======================== DOCUMENT RETRIEVAL ========================

def get_application_documents(icm_id: int) -> Dict[str, Any]:
    """
    Get all documents for an ICM application with base64 encoding.
    
    Args:
        icm_id: Application ID
    
    Returns:
        Documents organized by type with base64 content
    """
    application = get_icm_application_by_id(icm_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ICM Application #{icm_id} not found"
        )
    
    documents = get_icm_documents(icm_id)
    
    return {
        "icm_id": icm_id,
        "documents": documents
    }
