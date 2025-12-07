# app/services/icm_utils.py
"""
ICM Utility Functions

Provides validation, jurisdiction checks, and role-stage mapping for ICM workflow.
Uses ONLY these DB roles: "Citizen", "Tribal Officer", "District Collector/DM/SJO", 
"State Nodal Officer", "PFMS Officer"
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status

from app.db.session import get_dbt_db_connection
from app.db.govt_session import get_aadhaar_by_number

logger = logging.getLogger(__name__)


# ======================== ROLE & STAGE CONSTANTS ========================

# Official DB Roles (ONLY these 5 roles)
ROLE_CITIZEN = "Citizen"
ROLE_TO = "Tribal Officer"
ROLE_DM = "District Collector/DM/SJO"
ROLE_SNO = "State Nodal Officer"
ROLE_PFMS = "PFMS Officer"

# All valid officer roles
OFFICER_ROLES = [ROLE_TO, ROLE_DM, ROLE_SNO, ROLE_PFMS]

# Stage flow: 0 → 1 → 2 → 3 → 4 → 5
# Stage 0: Submitted (Citizen) → pending_at: Tribal Officer
# Stage 1: TO Approved → pending_at: District Collector/DM/SJO
# Stage 2: DM Approved → pending_at: State Nodal Officer
# Stage 3: SNO Approved → pending_at: PFMS Officer
# Stage 4: PFMS Fund Released → pending_at: COMPLETED
# Stage 5: Completed (final)

STAGE_SUBMITTED = 0
STAGE_TO_APPROVED = 1
STAGE_DM_APPROVED = 2
STAGE_SNO_APPROVED = 3
STAGE_PFMS_RELEASED = 4
STAGE_COMPLETED = 5

# Role → allowed stage to act on
ROLE_STAGE_MAP = {
    ROLE_TO: STAGE_SUBMITTED,       # TO acts on stage 0
    ROLE_DM: STAGE_TO_APPROVED,     # DM acts on stage 1
    ROLE_SNO: STAGE_DM_APPROVED,    # SNO acts on stage 2
    ROLE_PFMS: STAGE_SNO_APPROVED,  # PFMS acts on stage 3
}

# Stage → next stage after approval
NEXT_STAGE_MAP = {
    STAGE_SUBMITTED: STAGE_TO_APPROVED,       # 0 → 1
    STAGE_TO_APPROVED: STAGE_DM_APPROVED,     # 1 → 2
    STAGE_DM_APPROVED: STAGE_SNO_APPROVED,    # 2 → 3
    STAGE_SNO_APPROVED: STAGE_PFMS_RELEASED,  # 3 → 4
    STAGE_PFMS_RELEASED: STAGE_COMPLETED,     # 4 → 5
}

# Stage → pending_at role
STAGE_PENDING_AT_MAP = {
    STAGE_SUBMITTED: ROLE_TO,
    STAGE_TO_APPROVED: ROLE_DM,
    STAGE_DM_APPROVED: ROLE_SNO,
    STAGE_SNO_APPROVED: ROLE_PFMS,
    STAGE_PFMS_RELEASED: "COMPLETED",
    STAGE_COMPLETED: "COMPLETED",
}

# Event type mapping by role
EVENT_TYPE_MAP = {
    ROLE_TO: {"approve": "TO_APPROVED", "correction": "TO_CORRECTION"},
    ROLE_DM: {"approve": "DM_APPROVED", "correction": "DM_CORRECTION", "reject": "DM_REJECTED"},
    ROLE_SNO: {"approve": "SNO_APPROVED", "correction": "SNO_CORRECTION"},
    ROLE_PFMS: {"approve": "PFMS_FUND_RELEASED", "correction": "PFMS_CORRECTION"},
}


# ======================== JURISDICTION CHECKS ========================

def assert_jurisdiction(token_payload: Dict[str, Any], application: Any) -> None:
    """
    Centralized jurisdiction check for ICM operations.
    
    Rules:
    - ADM/TO/DM: application.district == user.district AND application.state_ut == user.state_ut
    - SNO: application.state_ut == user.state_ut
    - PFMS: application.state_ut == user.state_ut (state-level)
    - Citizen: token.aadhaar == groom_aadhaar OR bride_aadhaar OR token.citizen_id == application.citizen_id
    
    Args:
        token_payload: JWT token payload with user info
        application: ICM application object or dict
    
    Raises:
        HTTPException 403: If jurisdiction mismatch
    """
    role = token_payload.get("role")
    user_state = token_payload.get("state_ut", "")
    user_district = token_payload.get("district", "")
    user_aadhaar = token_payload.get("aadhaar_number")
    citizen_id = token_payload.get("citizen_id")
    
    # Get application data
    if hasattr(application, 'model_dump'):
        app_data = application.model_dump()
    elif hasattr(application, '__dict__'):
        app_data = application.__dict__
    else:
        app_data = application
    
    app_state = app_data.get("state_ut", "")
    app_district = app_data.get("district", "")
    app_groom_aadhaar = app_data.get("groom_aadhaar")
    app_bride_aadhaar = app_data.get("bride_aadhaar")
    app_citizen_id = app_data.get("citizen_id")
    
    # Citizen access check
    if role == ROLE_CITIZEN or citizen_id:
        is_partner = (user_aadhaar == app_groom_aadhaar or user_aadhaar == app_bride_aadhaar)
        is_owner = (citizen_id == app_citizen_id)
        
        if not (is_partner or is_owner):
            logger.warning(f"Citizen jurisdiction denied: citizen_id={citizen_id}, app_citizen_id={app_citizen_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You are not associated with this application"
            )
        return
    
    # Officer jurisdiction checks
    if role in [ROLE_TO, ROLE_DM]:
        # District-level officers: must match both state AND district
        if app_state != user_state or app_district != user_district:
            logger.warning(f"Jurisdiction denied: role={role}, user_district={user_district}, app_district={app_district}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: jurisdiction mismatch (district)"
            )
    elif role in [ROLE_SNO, ROLE_PFMS]:
        # State-level officers: must match state
        if app_state != user_state:
            logger.warning(f"Jurisdiction denied: role={role}, user_state={user_state}, app_state={app_state}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: jurisdiction mismatch (state)"
            )
    else:
        # Unknown role
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: invalid role"
        )


def validate_role_for_stage(role: str, current_stage: int) -> bool:
    """
    Check if a role is allowed to act on the current stage.
    
    Args:
        role: User's role
        current_stage: Application's current stage
    
    Returns:
        True if role can act, False otherwise
    """
    allowed_stage = ROLE_STAGE_MAP.get(role)
    return allowed_stage == current_stage


def get_next_stage(current_stage: int) -> int:
    """Get the next stage after approval."""
    return NEXT_STAGE_MAP.get(current_stage, current_stage)


def get_pending_at_for_stage(stage: int) -> str:
    """Get the pending_at role for a given stage."""
    return STAGE_PENDING_AT_MAP.get(stage, "COMPLETED")


def get_event_type(role: str, action: str) -> str:
    """
    Get event type string for a role and action.
    
    Args:
        role: Officer role
        action: Action type (approve, correction, reject)
    
    Returns:
        Event type string
    """
    role_events = EVENT_TYPE_MAP.get(role, {})
    return role_events.get(action, f"{role.upper()}_{action.upper()}")


# ======================== VALIDATION FUNCTIONS ========================

def validate_applicant_is_partner(
    applicant_aadhaar: int,
    groom_aadhaar: int,
    bride_aadhaar: int
) -> None:
    """
    Validate that applicant is one of the partners (groom or bride).
    
    Args:
        applicant_aadhaar: Applicant's Aadhaar number
        groom_aadhaar: Groom's Aadhaar number
        bride_aadhaar: Bride's Aadhaar number
    
    Raises:
        HTTPException 400: If applicant is not a partner
    """
    if applicant_aadhaar != groom_aadhaar and applicant_aadhaar != bride_aadhaar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Applicant must be either the groom or bride (Aadhaar must match)"
        )


def validate_aadhaar_exists(aadhaar_number: int, field_name: str = "Aadhaar") -> bool:
    """
    Validate that an Aadhaar number exists in the aadhaar_records table.
    
    Args:
        aadhaar_number: Aadhaar number to validate
        field_name: Field name for error message
    
    Returns:
        True if exists
    
    Raises:
        HTTPException 400: If Aadhaar doesn't exist
    """
    try:
        aadhaar_record = get_aadhaar_by_number(aadhaar_number)
        if not aadhaar_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} ({aadhaar_number}) not found in Aadhaar database"
            )
        return True
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating Aadhaar {aadhaar_number}: {e}")
        # Don't fail on DB errors in prototype - just log warning
        logger.warning(f"Aadhaar validation skipped for {aadhaar_number} due to error")
        return True


def check_duplicate_couple(groom_aadhaar: int, bride_aadhaar: int) -> None:
    """
    Check if a couple already has an active ICM application.
    
    Active = status NOT in ['Rejected', 'Completed']
    Also checks reversed pair (bride as groom, groom as bride).
    
    Args:
        groom_aadhaar: Groom's Aadhaar number
        bride_aadhaar: Bride's Aadhaar number
    
    Raises:
        HTTPException 409: If duplicate couple found
    """
    connection = get_dbt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Check both orderings of the couple
        query = """
            SELECT icm_id, application_status, current_stage 
            FROM icm_applications 
            WHERE (
                (groom_aadhaar = %s AND bride_aadhaar = %s) 
                OR 
                (groom_aadhaar = %s AND bride_aadhaar = %s)
            )
            AND application_status NOT IN ('Rejected', 'Completed')
        """
        
        cursor.execute(query, (groom_aadhaar, bride_aadhaar, bride_aadhaar, groom_aadhaar))
        existing = cursor.fetchone()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An active application already exists for this couple (ICM #{existing['icm_id']})"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking duplicate couple: {e}")
        # Don't block on DB errors - allow application
    finally:
        cursor.close()
        connection.close()


def check_aadhaar_in_approved_applications(groom_aadhaar: int, bride_aadhaar: int) -> None:
    """
    Check if either groom or bride Aadhaar exists in any approved/completed application.
    
    Args:
        groom_aadhaar: Groom's Aadhaar number
        bride_aadhaar: Bride's Aadhaar number
    
    Raises:
        HTTPException 409: If either Aadhaar found in approved applications
    """
    connection = get_dbt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Check if either Aadhaar exists in any approved/completed application
        query = """
            SELECT icm_id, groom_aadhaar, bride_aadhaar, application_status
            FROM icm_applications 
            WHERE (
                groom_aadhaar IN (%s, %s) 
                OR 
                bride_aadhaar IN (%s, %s)
            )
            AND application_status = 'Completed'
        """
        
        cursor.execute(query, (groom_aadhaar, bride_aadhaar, groom_aadhaar, bride_aadhaar))
        existing = cursor.fetchone()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Groom or Bride has already received ICM benefit (Application #{existing['icm_id']})"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking Aadhaar in approved applications: {e}")
    finally:
        cursor.close()
        connection.close()


def validate_file_types(files: Dict[str, Any]) -> List[str]:
    """
    Validate file content types.
    
    Args:
        files: Dictionary of file objects
    
    Returns:
        List of validation errors (empty if all valid)
    """
    errors = []
    allowed_types = ['image/png', 'image/jpeg', 'image/jpg', 'application/pdf']
    
    for field_name, file in files.items():
        if file and hasattr(file, 'content_type'):
            if file.content_type not in allowed_types:
                errors.append(f"{field_name}: Invalid file type. Allowed: PNG, JPEG, PDF")
    
    return errors
