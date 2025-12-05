# app/services/dbt_service.py
"""
DBT (Direct Benefit Transfer) Service Layer

This module contains business logic for DBT case management operations.
Functions in this module handle case filtering, validation, and workflow operations.
"""

from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status

from app.db.session import (
    get_fir_data_by_case_no,
    get_all_fir_data,
    update_atrocity_case,
    insert_case_event
)
from app.schemas.dbt_schemas import AtrocityDBModel


def filter_cases_by_jurisdiction(
    cases: list[AtrocityDBModel],
    token_payload: dict
) -> list[AtrocityDBModel]:
    """
    Filters a list of cases based on user's jurisdiction.
    
    Rules:
    - IO: Only cases from their police station
    - TO/DM: Only cases from their district + state
    - SNO: All cases from their state
    - PFMS: Cases from their state at fund release stages (4, 6, 7)
    
    Args:
        cases: List of AtrocityDBModel cases
        token_payload: JWT token payload containing role and jurisdiction
    
    Returns:
        Filtered list of cases based on user's jurisdiction
    """
    role = token_payload.get("role")
    user_state = token_payload.get("state_ut")
    user_district = token_payload.get("district")
    user_ps = token_payload.get("vishesh_p_s_name")
    
    filtered = []
    
    for case in cases:
        # Investigation Officer: match police station
        if role == "Investigation Officer":
            if case.Vishesh_P_S_Name == user_ps:
                filtered.append(case)
        
        # Tribal Officer or District Collector/DM/SJO: match district AND state
        elif role in ("Tribal Officer", "District Collector/DM/SJO"):
            if case.District == user_district and case.State_UT == user_state:
                filtered.append(case)
        
        # State Nodal Officer: match state only
        elif role == "State Nodal Officer":
            if case.State_UT == user_state:
                filtered.append(case)
        
        # PFMS Officer: match state AND fund release stages
        elif role == "PFMS Officer":
            if case.State_UT == user_state and case.Stage in (4, 6, 7):
                filtered.append(case)
    
    return filtered


def validate_jurisdiction(
    token_payload: dict,
    case: AtrocityDBModel
):
    """
    Validates that the user has jurisdiction access to the case.
    
    Rules:
    - IO: case.Vishesh_P_S_Name == user.vishesh_p_s_name
    - TO/DM: case.District == user.district AND case.State_UT == user.state_ut
    - SNO: case.State_UT == user.state_ut (full state access)
    - PFMS: case.State_UT == user.state_ut AND case.Stage in {4, 6, 7}
    
    Raises 403 if user lacks jurisdiction access.
    
    Args:
        token_payload: JWT token payload
        case: AtrocityDBModel case to validate
    
    Raises:
        HTTPException: 403 Forbidden if no jurisdiction
    """
    role = token_payload.get("role")
    user_state = token_payload.get("state_ut")
    user_district = token_payload.get("district")
    user_ps = token_payload.get("vishesh_p_s_name")
    
    case_state = case.State_UT
    case_district = case.District
    case_ps = case.Vishesh_P_S_Name
    
    # Investigation Officer: must match police station
    if role == "Investigation Officer":
        if case_ps != user_ps:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You only have access to cases from {user_ps}"
            )
        return
    
    # Tribal Officer or District Collector/DM/SJO: must match district AND state
    if role in ("Tribal Officer", "District Collector/DM/SJO"):
        if case_state != user_state or case_district != user_district:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You only have access to cases from {user_district}, {user_state}"
            )
        return
    
    # State Nodal Officer: must match state only
    if role == "State Nodal Officer":
        if case_state != user_state:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You only have access to cases from {user_state}"
            )
        return
    
    # PFMS Officer: must match state AND case must be at fund release stage
    if role == "PFMS Officer":
        if case_state != user_state:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You only have access to cases from {user_state}"
            )
        if case.Stage not in (4, 6, 7, 8):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"PFMS Officers can only access cases at fund release stages (4, 6, 7)"
            )
        return


def validate_role_for_action(
    token_payload: dict, 
    payload_role: str, 
    case: AtrocityDBModel, 
    expected_stage: int | list[int],
    stage_allowed_role: Dict[int, str]
):
    """
    Validates that:
    1. JWT user role matches the role claimed in payload (403 if mismatch)
    2. Case is at the expected stage for this action (400 if wrong stage)
    3. The claimed role is allowed to act at this stage (403 if not allowed)
    
    Args:
        token_payload: JWT token payload
        payload_role: Role claimed in request payload
        case: AtrocityDBModel case
        expected_stage: Expected stage(s) for the action
        stage_allowed_role: Mapping of stages to allowed roles
    
    Raises:
        HTTPException: 403 or 400 if validation fails
    """
    # 1. JWT role must match payload role
    jwt_role = token_payload.get("role")
    if jwt_role != payload_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role mismatch: JWT role '{jwt_role}' does not match payload role '{payload_role}'"
        )
    
    # 2. Check if case is at expected stage
    expected_stages = expected_stage if isinstance(expected_stage, list) else [expected_stage]
    if case.Stage not in expected_stages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Case is at stage {case.Stage}, but this action requires stage {expected_stages}"
        )
    
    # 3. Check if role is allowed at this stage
    allowed_role = stage_allowed_role.get(case.Stage)
    if allowed_role and payload_role != allowed_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{payload_role}' cannot act at stage {case.Stage}. Expected: '{allowed_role}'"
        )


def approve_case_workflow(
    case_no: int,
    actor: str,
    role: str,
    comment: Optional[str] = None,
    fund_amount: Optional[float] = None,
    stage_allowed_role: Optional[Dict[int, str]] = None,
    stage_next_pending_at: Optional[Dict[int, str]] = None,
    stage_approval_event: Optional[Dict[int, str]] = None
) -> Dict[str, Any]:
    """
    Approves a case and moves it to the next stage.
    
    Args:
        case_no: Case number to approve
        actor: User who is approving (login_id)
        role: Role of the approver
        comment: Optional comment
        fund_amount: Optional fund amount (for Tribal Officer at stage 1)
        stage_allowed_role: Mapping of stages to allowed roles
        stage_next_pending_at: Mapping of current stage to next pending role
        stage_approval_event: Mapping of stage to approval event type
    
    Returns:
        Dictionary with case details and new stage information
    
    Raises:
        HTTPException: If case not found or validation fails
    """
    # Get current case
    case = get_fir_data_by_case_no(case_no)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case #{case_no} not found"
        )
    
    # Get next stage
    next_stage = case.Stage + 1
    next_pending_at = stage_next_pending_at.get(case.Stage, "Unknown") if stage_next_pending_at else "Unknown"
    event_type = stage_approval_event.get(case.Stage, "APPROVED") if stage_approval_event else "APPROVED"
    
    # Prepare update payload
    update_payload = {
        "Stage": next_stage,
        "Pending_At": next_pending_at,
        "Approved_By": role
    }
    
    # Add fund amount if provided (Tribal Officer at stage 1)
    if fund_amount is not None:
        update_payload["Fund_Ammount"] = str(fund_amount)
    
    # Update case in database
    success = update_atrocity_case(case_no, update_payload)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update case"
        )
    
    # Insert approval event
    event_data = {
        "actor": actor,
        "comment": comment,
        "fund_amount": fund_amount
    }
    insert_case_event(
        case_no=case_no,
        performed_by=actor,
        performed_by_role=role,
        event_type=event_type,
        event_data=event_data
    )
    
    return {
        "case_no": case_no,
        "previous_stage": case.Stage,
        "new_stage": next_stage,
        "pending_at": next_pending_at,
        "approved_by": role,
        "message": f"Case approved and moved to stage {next_stage}"
    }


def request_correction_workflow(
    case_no: int,
    actor: str,
    role: str,
    comment: Optional[str] = None,
    corrections_required: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Requests corrections for a case (sends back to previous stage).
    
    Args:
        case_no: Case number
        actor: User requesting correction
        role: Role of the user
        comment: Reason for requesting correction
        corrections_required: List of fields/items needing correction
    
    Returns:
        Dictionary with correction request details
    
    Raises:
        HTTPException: If case not found
    """
    case = get_fir_data_by_case_no(case_no)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case #{case_no} not found"
        )
    
    # Update case status to correction pending
    update_payload = {
        "Pending_At": "Correction",
        "application_status": "Correction Requested"
    }
    
    success = update_atrocity_case(case_no, update_payload)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request correction"
        )
    
    # Insert correction event
    event_data = {
        "actor": actor,
        "comment": comment,
        "corrections_required": corrections_required
    }
    insert_case_event(
        case_no=case_no,
        performed_by=actor,
        performed_by_role=role,
        event_type="CORRECTION_REQUESTED",
        event_data=event_data
    )
    
    return {
        "case_no": case_no,
        "stage": case.Stage,
        "status": "Correction Requested",
        "comment": comment,
        "corrections_required": corrections_required
    }


def get_all_cases_for_user(token_payload: dict) -> List[Dict[str, Any]]:
    """
    Get all cases accessible to the current user based on their jurisdiction.
    
    Args:
        token_payload: JWT token payload with role and jurisdiction
    
    Returns:
        List of cases filtered by user's jurisdiction
    """
    all_cases = get_all_fir_data()
    filtered_cases = filter_cases_by_jurisdiction(all_cases, token_payload)
    return [case.model_dump() for case in filtered_cases]
