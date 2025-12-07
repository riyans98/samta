# app/services/__init__.py
"""Services layer for business logic separation"""

from app.services.dbt_service import (
    filter_cases_by_jurisdiction,
    validate_jurisdiction,
    validate_role_for_action,
    approve_case_workflow,
    request_correction_workflow,
    get_all_cases_for_user
)

from app.services.icm_service import (
    create_icm_application,
    approve_icm_application,
    reject_icm_application,
    request_icm_correction,
    pfms_release,
    append_icm_event
)

from app.services.icm_utils import (
    ROLE_CITIZEN, ROLE_TO, ROLE_DM, ROLE_SNO, ROLE_PFMS,
    OFFICER_ROLES,
    STAGE_SUBMITTED, STAGE_COMPLETED,
    assert_jurisdiction,
    validate_role_for_stage,
    get_next_stage,
    get_pending_at_for_stage,
    get_event_type,
    validate_applicant_is_partner,
    check_duplicate_couple
)

from app.services.icm_storage import (
    save_icm_file,
    get_icm_documents
)

__all__ = [
    # DBT Services
    "filter_cases_by_jurisdiction",
    "validate_jurisdiction",
    "validate_role_for_action",
    "approve_case_workflow",
    "request_correction_workflow",
    "get_all_cases_for_user",
    # ICM Services
    "create_icm_application",
    "approve_icm_application",
    "reject_icm_application",
    "request_icm_correction",
    "pfms_release",
    "append_icm_event",
    # ICM Utils
    "ROLE_CITIZEN", "ROLE_TO", "ROLE_DM", "ROLE_SNO", "ROLE_PFMS",
    "OFFICER_ROLES",
    "STAGE_SUBMITTED", "STAGE_COMPLETED",
    "assert_jurisdiction",
    "validate_role_for_stage",
    "get_next_stage",
    "get_pending_at_for_stage",
    "get_event_type",
    "validate_applicant_is_partner",
    "check_duplicate_couple",
    # ICM Storage
    "save_icm_file",
    "get_icm_documents",
]
