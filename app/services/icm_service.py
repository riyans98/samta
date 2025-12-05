# app/services/icm_service.py
"""
ICM (Inter-Caste Marriage) Service Layer

This module contains business logic for ICM application management.
Functions handle application creation, retrieval, and workflow operations.
"""

from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status

from app.db.icm_session import (
    get_icm_application_by_id,
    get_all_icm_applications,
    get_icm_applications_by_citizen,
    insert_icm_application,
    update_icm_application,
    insert_icm_event
)
from app.schemas.icm_schemas import ICMApplication, ICMEvent


def get_user_icm_applications(citizen_id: int) -> List[Dict[str, Any]]:
    """
    Get all ICM applications for a specific citizen.
    
    Args:
        citizen_id: Citizen ID to fetch applications for
    
    Returns:
        List of ICM applications
    """
    applications = get_icm_applications_by_citizen(citizen_id)
    return [app.model_dump() for app in applications]


def create_icm_application(
    application_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Creates a new ICM application.
    
    Args:
        application_data: Application data dictionary
    
    Returns:
        Created application with ID and status
    
    Raises:
        HTTPException: If creation fails
    """
    try:
        icm_id = insert_icm_application(application_data)
        
        # Insert initial event
        insert_icm_event(
            icm_id=icm_id,
            event_type="APPLICATION_CREATED",
            event_role="CITIZEN",
            event_stage=0,
            comment="Application created",
            event_data={"action": "created"}
        )
        
        return {
            "icm_id": icm_id,
            "status": "created",
            "message": "ICM application created successfully",
            "current_stage": 0,
            "pending_at": "ADM"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ICM application: {e}"
        )


def approve_icm_application(
    icm_id: int,
    actor: str,
    role: str,
    comment: Optional[str] = None
) -> Dict[str, Any]:
    """
    Approves an ICM application and moves to next stage.
    
    Args:
        icm_id: Application ID
        actor: User approving (login_id)
        role: Role of approver (ADM, TO, DM, SNO, PFMS)
        comment: Optional comment
    
    Returns:
        Updated application status
    
    Raises:
        HTTPException: If application not found or validation fails
    """
    application = get_icm_application_by_id(icm_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ICM Application #{icm_id} not found"
        )
    
    # Get next stage
    next_stage = application.current_stage + 1
    
    # Define stage flow for ICM
    stage_next_role = {
        0: "TO",
        1: "DM",
        2: "SNO",
        3: "PFMS",
        4: "CLOSED"
    }
    
    next_pending_at = stage_next_role.get(next_stage, "CLOSED")
    
    # Update application
    update_payload = {
        "current_stage": next_stage,
        "pending_at": next_pending_at,
        "application_status": "Under Review"
    }
    
    success = update_icm_application(icm_id, update_payload)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve application"
        )
    
    # Insert approval event
    event_data = {
        "actor": actor,
        "comment": comment,
        "approved": True
    }
    insert_icm_event(
        icm_id=icm_id,
        event_type=f"{role}_APPROVED",
        event_role=role,
        event_stage=application.current_stage,
        comment=comment,
        event_data=event_data
    )
    
    return {
        "icm_id": icm_id,
        "previous_stage": application.current_stage,
        "new_stage": next_stage,
        "pending_at": next_pending_at,
        "approved_by": role,
        "message": f"Application approved and moved to stage {next_stage}"
    }


def reject_icm_application(
    icm_id: int,
    actor: str,
    role: str,
    reason: str
) -> Dict[str, Any]:
    """
    Rejects an ICM application.
    
    Args:
        icm_id: Application ID
        actor: User rejecting
        role: Role of user
        reason: Reason for rejection
    
    Returns:
        Updated application status
    
    Raises:
        HTTPException: If application not found
    """
    application = get_icm_application_by_id(icm_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ICM Application #{icm_id} not found"
        )
    
    # Update application
    update_payload = {
        "application_status": "Rejected"
    }
    
    success = update_icm_application(icm_id, update_payload)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject application"
        )
    
    # Insert rejection event
    event_data = {
        "actor": actor,
        "reason": reason,
        "rejected": True
    }
    insert_icm_event(
        icm_id=icm_id,
        event_type="APPLICATION_REJECTED",
        event_role=role,
        event_stage=application.current_stage,
        comment=reason,
        event_data=event_data
    )
    
    return {
        "icm_id": icm_id,
        "status": "Rejected",
        "reason": reason,
        "rejected_by": role
    }


def get_icm_applications_by_jurisdiction(
    state_ut: str,
    district: Optional[str] = None,
    pending_at: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get ICM applications filtered by jurisdiction and status.
    
    Args:
        state_ut: State/UT filter
        district: District filter (optional)
        pending_at: Pending at filter (optional)
    
    Returns:
        List of filtered applications
    """
    all_applications = get_all_icm_applications()
    
    filtered = []
    for app in all_applications:
        # Filter by state
        if app.state_ut != state_ut:
            continue
        
        # Filter by district if provided
        if district and app.district != district:
            continue
        
        # Filter by pending_at if provided
        if pending_at and app.pending_at != pending_at:
            continue
        
        filtered.append(app.model_dump())
    
    return filtered


def request_icm_correction(
    icm_id: int,
    actor: str,
    role: str,
    corrections_required: List[str],
    comment: Optional[str] = None
) -> Dict[str, Any]:
    """
    Requests corrections for an ICM application.
    
    Args:
        icm_id: Application ID
        actor: User requesting correction
        role: Role of user
        corrections_required: List of fields needing correction
        comment: Optional comment
    
    Returns:
        Correction request details
    
    Raises:
        HTTPException: If application not found
    """
    application = get_icm_application_by_id(icm_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ICM Application #{icm_id} not found"
        )
    
    # Update application
    update_payload = {
        "application_status": "Correction Required",
        "pending_at": "CITIZEN"
    }
    
    success = update_icm_application(icm_id, update_payload)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request correction"
        )
    
    # Insert correction event
    event_data = {
        "actor": actor,
        "corrections_required": corrections_required,
        "comment": comment
    }
    insert_icm_event(
        icm_id=icm_id,
        event_type="CORRECTION_REQUESTED",
        event_role=role,
        event_stage=application.current_stage,
        comment=comment,
        event_data=event_data
    )
    
    return {
        "icm_id": icm_id,
        "status": "Correction Required",
        "corrections_required": corrections_required,
        "pending_at": "CITIZEN",
        "requested_by": role
    }
