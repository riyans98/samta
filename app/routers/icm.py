# app/routers/icm.py
"""
ICM (Inter-Caste Marriage) Routes

API endpoints for Inter-Caste Marriage applications.
Supports multipart form data for file uploads.

Roles: Citizen, ADM, Tribal Officer, District Collector/DM/SJO, State Nodal Officer, PFMS Officer
Stage Flow: 0 → 1 → 2 → 3 → 4 → 5 → 6 (Completed)
Documents: MARRIAGE, GROOM_SIGN, BRIDE_SIGN, WITNESS_SIGN
"""

import logging
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.core.security import verify_jwt_token
from app.schemas.icm_schemas import ICMApplication, ICMEvent
from app.services.icm_service import (
    get_user_icm_applications,
    create_icm_application_with_files,
    approve_icm_application,
    reject_icm_application,
    get_icm_applications_by_jurisdiction,
    request_icm_correction,
    pfms_release,
    get_application_documents
)
from app.services.icm_utils import (
    ROLE_CITIZEN, ROLE_ADM, ROLE_TO, ROLE_DM, ROLE_SNO, ROLE_PFMS,
    OFFICER_ROLES,
    assert_jurisdiction
)
from app.db.icm_session import get_icm_events_by_application, get_icm_application_by_id

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/icm",
    tags=["ICM Application Management"],
)


# ======================== REQUEST/RESPONSE MODELS ========================

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


class PFMSReleaseRequest(BaseModel):
    """Request model for PFMS fund release"""
    amount: int
    txn_id: str
    bank_ref: Optional[str] = None


# ======================== CITIZEN ENDPOINTS ========================

@router.post("/applications", status_code=status.HTTP_201_CREATED)
async def submit_icm_application(
    # Groom details
    groom_name: str = Form(...),
    groom_age: int = Form(...),
    groom_father_name: str = Form(...),
    groom_dob: str = Form(...),  # YYYY-MM-DD
    groom_aadhaar: int = Form(...),
    groom_pre_address: str = Form(default=""),
    groom_current_address: str = Form(...),
    groom_permanent_address: str = Form(default=""),
    groom_caste_cert_id: Optional[str] = Form(default=None),
    groom_education: Optional[str] = Form(default=None),
    groom_training: Optional[str] = Form(default=None),
    groom_income: Optional[str] = Form(default=None),
    groom_livelihood: Optional[str] = Form(default=None),
    groom_future_plan: Optional[str] = Form(default=None),
    groom_first_marriage: bool = Form(default=True),
    
    # Bride details
    bride_name: str = Form(...),
    bride_age: int = Form(...),
    bride_father_name: str = Form(...),
    bride_dob: str = Form(...),  # YYYY-MM-DD
    bride_aadhaar: int = Form(...),
    bride_pre_address: str = Form(default=""),
    bride_current_address: str = Form(...),
    bride_permanent_address: str = Form(default=""),
    bride_caste_cert_id: Optional[str] = Form(default=None),
    bride_education: Optional[str] = Form(default=None),
    bride_training: Optional[str] = Form(default=None),
    bride_income: Optional[str] = Form(default=None),
    bride_livelihood: Optional[str] = Form(default=None),
    bride_future_plan: Optional[str] = Form(default=None),
    bride_first_marriage: bool = Form(default=True),
    
    # Marriage details
    marriage_date: str = Form(...),  # YYYY-MM-DD
    marriage_certificate_number: Optional[str] = Form(default=None),
    previous_benefit_taken: bool = Form(default=False),
    
    # Witness details
    witness_name: Optional[str] = Form(default=None),
    witness_aadhaar: Optional[int] = Form(default=None),
    witness_address: Optional[str] = Form(default=None),
    witness_verified: bool = Form(default=False),
    
    # Bank details
    joint_account_number: str = Form(...),
    joint_ifsc: Optional[str] = Form(default=None),
    joint_account_bank_name: Optional[str] = Form(default=None),
    
    # Files (only 4 documents)
    marriage_certificate: UploadFile = File(...),
    groom_signature: UploadFile = File(...),
    bride_signature: UploadFile = File(...),
    witness_signature: Optional[UploadFile] = File(default=None),
    
    # JWT token
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Submit a new ICM application with documents.
    
    Requires multipart/form-data with form fields + files.
    Applicant must be either groom or bride (Aadhaar must match token).
    
    Documents:
    - marriage_certificate (required): MARRIAGE
    - groom_signature (required): GROOM_SIGN
    - bride_signature (required): BRIDE_SIGN
    - witness_signature (optional): WITNESS_SIGN
    """
    citizen_id = token_payload.get("citizen_id")
    if not citizen_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Citizen ID missing from token"
        )
    
    # Log witness verification (prototype - no OTP)
    if witness_verified:
        logger.info(f"Prototype: witness verified flag set without OTP for citizen_id={citizen_id}")
    
    # Prepare application data
    application_data = {
        # Groom
        "groom_name": groom_name,
        "groom_age": groom_age,
        "groom_father_name": groom_father_name,
        "groom_dob": groom_dob,
        "groom_aadhaar": groom_aadhaar,
        "groom_pre_address": groom_pre_address,
        "groom_current_address": groom_current_address,
        "groom_permanent_address": groom_permanent_address,
        "groom_caste_cert_id": groom_caste_cert_id,
        "groom_education": groom_education,
        "groom_training": groom_training,
        "groom_income": groom_income,
        "groom_livelihood": groom_livelihood,
        "groom_future_plan": groom_future_plan,
        "groom_first_marriage": groom_first_marriage,
        
        # Bride
        "bride_name": bride_name,
        "bride_age": bride_age,
        "bride_father_name": bride_father_name,
        "bride_dob": bride_dob,
        "bride_aadhaar": bride_aadhaar,
        "bride_pre_address": bride_pre_address,
        "bride_current_address": bride_current_address,
        "bride_permanent_address": bride_permanent_address,
        "bride_caste_cert_id": bride_caste_cert_id,
        "bride_education": bride_education,
        "bride_training": bride_training,
        "bride_income": bride_income,
        "bride_livelihood": bride_livelihood,
        "bride_future_plan": bride_future_plan,
        "bride_first_marriage": bride_first_marriage,
        
        # Marriage
        "marriage_date": marriage_date,
        "marriage_certificate_number": marriage_certificate_number,
        "previous_benefit_taken": previous_benefit_taken,
        
        # Witness
        "witness_name": witness_name,
        "witness_aadhaar": witness_aadhaar,
        "witness_address": witness_address,
        "witness_verified": witness_verified,
        
        # Bank
        "joint_account_number": joint_account_number,
        "joint_ifsc": joint_ifsc,
        "joint_account_bank_name": joint_account_bank_name,
    }
    
    # Prepare files dictionary
    files = {
        "marriage_certificate": marriage_certificate,
        "groom_signature": groom_signature,
        "bride_signature": bride_signature,
        "witness_signature": witness_signature
    }
    
    # Create application with files
    result = await create_icm_application_with_files(
        application_data=application_data,
        files=files,
        token_payload=token_payload
    )
    
    logger.info(f"ICM action: submit, icm_id={result.get('icm_id')}, user={token_payload.get('sub')}, role={ROLE_CITIZEN}")
    
    return result


@router.get("/applications", response_model=List[dict])
async def get_citizen_applications(
    # Query params for officer filtering
    state_ut: Optional[str] = None,
    district: Optional[str] = None,
    pending_at: Optional[str] = None,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get ICM applications.
    
    - Citizens: Returns their own applications only
    - Officers: Returns applications filtered by jurisdiction (requires state_ut param)
    """
    role = token_payload.get("role")
    citizen_id = token_payload.get("citizen_id")
    
    # Citizen view - their own applications
    if citizen_id and role == ROLE_CITIZEN:
        applications = get_user_icm_applications(citizen_id)
        return applications
    
    # Officer view - filtered by jurisdiction
    if role in OFFICER_ROLES:
        if not state_ut:
            # Use officer's state from token
            state_ut = token_payload.get("state_ut")
        
        if not state_ut:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="state_ut parameter required for officer queries"
            )
        
        applications = get_icm_applications_by_jurisdiction(
            state_ut=state_ut,
            district=district,
            pending_at=pending_at
        )
        return applications
    
    # Citizen without citizen_id - try to return their applications
    if citizen_id:
        applications = get_user_icm_applications(citizen_id)
        return applications
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unable to determine user context"
    )


@router.get("/applications/{icm_id}")
async def get_icm_application_details(
    icm_id: int,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get details of a specific ICM application with timeline.
    
    Access: Owner citizen or officer in jurisdiction
    """
    application = get_icm_application_by_id(icm_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ICM Application #{icm_id} not found"
        )
    
    # Jurisdiction check
    assert_jurisdiction(token_payload, application)
    
    # Get events/timeline (now sorted ASC)
    events = get_icm_events_by_application(icm_id)
    
    return {
        "application": application.model_dump(),
        "timeline": [event.model_dump() for event in events]
    }


@router.get("/applications/{icm_id}/timeline")
async def get_application_timeline(
    icm_id: int,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get complete timeline/events for an ICM application.
    Events are sorted ascending by created_at (chronological order).
    """
    application = get_icm_application_by_id(icm_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ICM Application #{icm_id} not found"
        )
    
    # Jurisdiction check
    assert_jurisdiction(token_payload, application)
    
    events = get_icm_events_by_application(icm_id)
    
    return {
        "icm_id": icm_id,
        "current_stage": application.current_stage,
        "status": application.application_status,
        "timeline": [event.model_dump() for event in events]
    }


@router.get("/applications/{icm_id}/documents")
async def get_icm_documents_endpoint(
    icm_id: int,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get all documents for an ICM application with base64 encoding.
    
    Returns documents organized by type:
    - MARRIAGE
    - GROOM_SIGN
    - BRIDE_SIGN
    - WITNESS_SIGN
    
    Each document includes: filename, file_type, content (base64), file_size, mime_type
    """
    application = get_icm_application_by_id(icm_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ICM Application #{icm_id} not found"
        )
    
    # Jurisdiction check
    assert_jurisdiction(token_payload, application)
    
    return get_application_documents(icm_id)


# ======================== DECLARATION HTML ROUTE ========================

@router.get("/{icm_id}/declaration", response_class=HTMLResponse)
async def get_declaration_html(
    icm_id: int,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get printable declaration HTML for an ICM application.
    
    Renders server-side HTML template (no PDF saved).
    Browser can print via Ctrl+P.
    
    Access: Owner citizen or officer in jurisdiction
    """
    application = get_icm_application_by_id(icm_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ICM Application #{icm_id} not found"
        )
    
    # Jurisdiction check
    assert_jurisdiction(token_payload, application)
    
    # Render HTML template
    app_data = application.model_dump()
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Declaration Form - ICM Application #{icm_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Times New Roman', Times, serif;
            font-size: 14px;
            line-height: 1.6;
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #000;
            padding-bottom: 20px;
        }}
        .header h1 {{
            font-size: 18px;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        .header h2 {{
            font-size: 16px;
            font-weight: normal;
        }}
        .section {{
            margin-bottom: 25px;
        }}
        .section-title {{
            font-weight: bold;
            text-decoration: underline;
            margin-bottom: 10px;
        }}
        .field {{
            margin-bottom: 8px;
        }}
        .field-label {{
            font-weight: bold;
            display: inline-block;
            width: 200px;
        }}
        .declaration-text {{
            margin: 30px 0;
            text-align: justify;
            padding: 15px;
            border: 1px solid #ccc;
            background: #f9f9f9;
        }}
        .signature-section {{
            margin-top: 50px;
            display: flex;
            justify-content: space-between;
        }}
        .signature-block {{
            text-align: center;
            width: 30%;
        }}
        .signature-line {{
            border-top: 1px solid #000;
            margin-top: 50px;
            padding-top: 5px;
        }}
        .footer {{
            margin-top: 50px;
            text-align: center;
            font-size: 12px;
            color: #666;
            border-top: 1px solid #ccc;
            padding-top: 10px;
        }}
        @media print {{
            body {{
                padding: 0;
            }}
            .no-print {{
                display: none !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="no-print" style="text-align: center; margin-bottom: 20px;">
        <button onclick="window.print()" style="padding: 10px 20px; font-size: 14px; cursor: pointer;">
            Print Declaration
        </button>
    </div>
    
    <div class="header">
        <h1>Declaration Form</h1>
        <h2>Inter-Caste Marriage Incentive Scheme</h2>
        <p>Application No: ICM-{icm_id}</p>
    </div>
    
    <div class="section">
        <div class="section-title">Groom Details</div>
        <div class="field"><span class="field-label">Name:</span> {app_data.get('groom_name', '')}</div>
        <div class="field"><span class="field-label">Father's Name:</span> {app_data.get('groom_father_name', '')}</div>
        <div class="field"><span class="field-label">Date of Birth:</span> {app_data.get('groom_dob', '')}</div>
        <div class="field"><span class="field-label">Aadhaar Number:</span> XXXX-XXXX-{str(app_data.get('groom_aadhaar', ''))[-4:]}</div>
        <div class="field"><span class="field-label">Current Address:</span> {app_data.get('groom_current_address', '')}</div>
    </div>
    
    <div class="section">
        <div class="section-title">Bride Details</div>
        <div class="field"><span class="field-label">Name:</span> {app_data.get('bride_name', '')}</div>
        <div class="field"><span class="field-label">Father's Name:</span> {app_data.get('bride_father_name', '')}</div>
        <div class="field"><span class="field-label">Date of Birth:</span> {app_data.get('bride_dob', '')}</div>
        <div class="field"><span class="field-label">Aadhaar Number:</span> XXXX-XXXX-{str(app_data.get('bride_aadhaar', ''))[-4:]}</div>
        <div class="field"><span class="field-label">Current Address:</span> {app_data.get('bride_current_address', '')}</div>
    </div>
    
    <div class="section">
        <div class="section-title">Marriage Details</div>
        <div class="field"><span class="field-label">Date of Marriage:</span> {app_data.get('marriage_date', '')}</div>
        <div class="field"><span class="field-label">Certificate Number:</span> {app_data.get('marriage_certificate_number', 'N/A')}</div>
    </div>
    
    <div class="declaration-text">
        <strong>DECLARATION</strong><br><br>
        We, <strong>{app_data.get('groom_name', '_____')}</strong> (Groom) and <strong>{app_data.get('bride_name', '_____')}</strong> (Bride), 
        hereby solemnly declare that:
        <br><br>
        1. The information provided in this application is true and correct to the best of our knowledge and belief.
        <br><br>
        2. We have entered into this inter-caste marriage of our own free will and consent without any coercion or pressure.
        <br><br>
        3. One of us belongs to Scheduled Caste (SC) or Scheduled Tribe (ST) category as per the caste certificate provided.
        <br><br>
        4. We have not previously availed any financial assistance/incentive under Inter-Caste Marriage Scheme from any Government agency.
        <br><br>
        5. We understand that if any information provided is found to be false or incorrect, we shall be liable for prosecution 
        and recovery of the amount with interest.
        <br><br>
        6. The joint bank account details provided are correct and belong to both of us jointly.
    </div>
    
    <div class="signature-section">
        <div class="signature-block">
            <div class="signature-line">
                Signature of Groom<br>
                ({app_data.get('groom_name', '')})
            </div>
        </div>
        <div class="signature-block">
            <div class="signature-line">
                Signature of Bride<br>
                ({app_data.get('bride_name', '')})
            </div>
        </div>
        <div class="signature-block">
            <div class="signature-line">
                Signature of Witness<br>
                ({app_data.get('witness_name', '_______________')})
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>Application ID: ICM-{icm_id} | Generated: {generated_at}</p>
        <p>This is a computer-generated document.</p>
    </div>
</body>
</html>
    """
    
    return HTMLResponse(
        content=html_content,
        headers={
            "Content-Disposition": f'inline; filename="declaration_icm_{icm_id}.html"'
        }
    )


# ======================== OFFICER WORKFLOW ENDPOINTS ========================

@router.post("/applications/{icm_id}/approve", status_code=status.HTTP_200_OK)
async def approve_application(
    icm_id: int,
    payload: ApproveICMRequest,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Approve an ICM application and move to next stage.
    
    Stage Flow:
    - Stage 0: ADM approves → Stage 1 (Tribal Officer)
    - Stage 1: Tribal Officer approves → Stage 2 (DM)
    - Stage 2: DM approves → Stage 3 (SNO)
    - Stage 3: SNO approves → Stage 4 (PFMS)
    - Stage 4: Use /pfms/release endpoint instead
    
    Allowed Roles: ADM, Tribal Officer, District Collector/DM/SJO, State Nodal Officer
    """
    role = token_payload.get("role")
    
    if role not in OFFICER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only officers can approve applications"
        )
    
    # PFMS should use pfms/release endpoint
    if role == ROLE_PFMS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PFMS Officer should use /pfms/release endpoint for fund release"
        )
    
    result = approve_icm_application(
        icm_id=icm_id,
        actor=token_payload.get("sub"),
        role=role,
        comment=payload.comment,
        token_payload=token_payload
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
    
    Any officer can reject, but typically District Collector/DM/SJO.
    Sets application_status='Rejected'.
    
    Allowed Roles: All officers
    """
    role = token_payload.get("role")
    
    if role not in OFFICER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only officers can reject applications"
        )
    
    result = reject_icm_application(
        icm_id=icm_id,
        actor=token_payload.get("sub"),
        role=role,
        reason=payload.reason,
        token_payload=token_payload
    )
    
    return result


@router.post("/applications/{icm_id}/request-correction", status_code=status.HTTP_200_OK)
async def request_correction_endpoint(
    icm_id: int,
    payload: CorrectionRequest,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Request corrections for an ICM application.
    
    Resets application to stage 0, pending_at='Citizen'.
    Citizen can then resubmit without creating a new application.
    
    Allowed Roles: All officers
    """
    role = token_payload.get("role")
    
    if role not in OFFICER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only officers can request corrections"
        )
    
    result = request_icm_correction(
        icm_id=icm_id,
        actor=token_payload.get("sub"),
        role=role,
        corrections_required=payload.corrections_required,
        comment=payload.comment,
        token_payload=token_payload
    )
    
    return result


@router.post("/applications/{icm_id}/pfms/release", status_code=status.HTTP_200_OK)
async def pfms_fund_release(
    icm_id: int,
    payload: PFMSReleaseRequest,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    PFMS fund release - completes the ICM application.
    
    Validates:
    - Application must be at stage 4 (pending PFMS)
    - Only PFMS Officer can release funds
    - Amount should be Rs. 2,50,000 (configurable)
    
    Sets application to stage 6 (Completed).
    Creates PFMS_FUND_RELEASED event with transaction details.
    
    Allowed Roles: PFMS Officer only
    """
    role = token_payload.get("role")
    
    if role != ROLE_PFMS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only PFMS Officer can release funds"
        )
    
    result = pfms_release(
        icm_id=icm_id,
        actor=token_payload.get("sub"),
        role=role,
        amount=payload.amount,
        txn_id=payload.txn_id,
        bank_ref=payload.bank_ref,
        token_payload=token_payload
    )
    
    return result
