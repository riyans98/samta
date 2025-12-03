# app/routers/dbt.py
import shutil
import os
import re
from fastapi import APIRouter, HTTPException, Query, status, Depends, UploadFile, File, Form
from typing import Dict, Any, Optional
from pydantic import ValidationError, conint

from app.core.config import settings
from app.core.security import verify_jwt_token # Protection
from app.db.session import (
    get_dbt_db_connection, 
    get_all_fir_data, 
    get_fir_data_by_fir_no, 
    get_fir_data_by_case_no,
    get_timeline,
    insert_case_event,
    update_atrocity_case
)
from app.schemas.dbt_schemas import (
    AtrocityBase, 
    AtrocityDBModel, 
    AtrocityFullRecord, 
    DocumentInfo, 
    DocumentsByType,
    ApprovalPayload,
    CorrectionPayload,
    ChargeSheetPayload,
    CaseCompletionPayload,
    FundReleasePayload,
    CaseEvent,
    STAGE_ALLOWED_ROLE,
    STAGE_NEXT_PENDING_AT,
    STAGE_APPROVAL_EVENT
)
from app.db.govt_session import get_fir_by_number, get_aadhaar_by_number

router = APIRouter(
    prefix="/dbt/case",
    tags=["DBT Case Management"],
    # Yahan JWT security lagao
    # dependencies=[Depends(verify_jwt_token)] 
)


# File names ko DB mein store karne ke liye ek helper function
# app/routers/dbt.py (save_uploaded_file function ko replace karein)

import os
import shutil
import base64
from fastapi import UploadFile, HTTPException, status

def get_mime_type(filename: str) -> str:
    """Get MIME type based on file extension"""
    ext = os.path.splitext(filename)[1].lower()
    mime_types = {
        '.pdf': 'application/pdf',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
    }
    return mime_types.get(ext, 'application/octet-stream')

def get_documents_by_fir_no(fir_no: str) -> DocumentsByType:
    """
    Retrieves all documents for a given FIR number from the upload directory.
    
    Returns base64-encoded file content so it can be sent across different servers.
    
    Filename pattern: FIR{firNumber}_{userId}_{FILE_TYPE}.{extension}
    Example: FIRFIR-2025-004_user_PHOTO.png
    
    Parses the filename to extract document type,
    then organizes documents by type with their content.
    """
    documents = DocumentsByType()
    
    if not os.path.exists(settings.UPLOAD_DIR):
        return documents
    
    try:
        # Pattern to match files with document type before extension
        # Handles both old format (FIR{fir_no}_{user}_{TYPE}_FIR.{ext}) and new format (FIR{fir_no}_{user}_{TYPE}.{ext})
        # FIR numbers may contain hyphens and special characters
        # Capturing group: document type (between second-to-last or third-to-last _ and .ext)
        escaped_fir = re.escape(fir_no)
        # Pattern matches: FIR{fir_no}_{user}_{TYPE}(_FIR)?.{ext}
        # (_FIR)? is optional to handle both old and new filename formats
        pattern = rf"FIR{escaped_fir}_[^_]+_([A-Z]+)(?:_FIR)?\.[a-zA-Z0-9]+"
        
        for filename in os.listdir(settings.UPLOAD_DIR):
            match = re.match(pattern, filename)
            if match:
                file_type = match.group(1)
                file_path = os.path.join(settings.UPLOAD_DIR, filename)
                
                try:
                    # Read file and encode as base64
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                    
                    # Get file size
                    file_size = len(file_content)
                    
                    # Encode to base64
                    base64_content = base64.b64encode(file_content).decode('utf-8')
                    
                    # Get MIME type
                    mime_type = get_mime_type(filename)
                    
                    doc_info = DocumentInfo(
                        filename=filename,
                        file_type=file_type,
                        content=base64_content,
                        file_size=file_size,
                        mime_type=mime_type
                    )
                    
                    # Organize by document type
                    if file_type == "FIR":
                        documents.FIR.append(doc_info)
                    elif file_type == "PHOTO":
                        documents.PHOTO.append(doc_info)
                    elif file_type == "CASTE":
                        documents.CASTE.append(doc_info)
                    elif file_type == "MEDICAL":
                        documents.MEDICAL.append(doc_info)
                    elif file_type == "POSTMORTEM":
                        documents.POSTMORTEM.append(doc_info)
                    else:
                        documents.OTHER.append(doc_info)
                
                except Exception as e:
                    print(f"Error reading file {filename}: {e}")
                    continue
    
    except Exception as e:
        print(f"Error retrieving documents for FIR {fir_no}: {e}")
    
    return documents

# ... (other imports)
def save_uploaded_file(file: UploadFile, base_name: str) -> str:
    """
    Saves the file to the local directory and returns the generated filename.

    :param file: The UploadFile object.
    :param base_name: The base name including document type (e.g., FIRFIR-2025-001_user_PHOTO).
    """
    if not file or not file.filename:
        return "" # Handle optional files

    # 1. Extension Extract Karna
    _, file_extension = os.path.splitext(file.filename)
    # Security: Only allow specific extensions
    if file_extension.lower() not in ['.pdf', '.jpg', '.jpeg', '.png']:
         raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST, 
             detail=f"Invalid file type: {file.filename}. Only PDF/JPG/PNG allowed."
         )

    # 2. Filename Format: base_name already contains FIR{firNumber}_{userId}_{FILE_TYPE}
    # So just append extension
    generated_filename = f"{base_name}{file_extension.lower()}"
    file_path = os.path.join(settings.UPLOAD_DIR, generated_filename)

    # 3. File Save Karna
    try:
        # File pointer ko starting position par set karna
        file.file.seek(0) 
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return generated_filename
    except Exception as e:
        print(f"File upload error for {generated_filename}: {e}")
        # Agar file save na ho paye, toh 500 error raise karein
        raise HTTPException(status_code=500, detail=f"File upload failed for {generated_filename}")
# def save_uploaded_file(file: UploadFile, prefix: str) -> str:
#     """Saves the file to the local directory and returns the filename."""
#     if not file:
#         return "" # Empty string for optional files
    
#     # Secure filename: Use case_no/fir_no for organization/uniqueness
#     # For now, we'll use a simple name (need FIR_NO for proper naming)
#     filename = f"{prefix}_{file.filename.replace(' ', '_')}"
#     file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
#     try:
#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
#         return filename
#     except Exception as e:
#         print(f"File upload error: {e}")
#         raise HTTPException(status_code=500, detail=f"File upload failed for {file.filename}")


def insert_atrocity_case(data: Dict[str, Any]):
    """Handles data insertion into the ATROCITY table in defaultdb."""
    connection = None
    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor()
        
        # Debug: Log what's being inserted
        print(f"DEBUG insert_atrocity_case: State_UT={data.get('State_UT')}, District={data.get('District')}, Vishesh_P_S_Name={data.get('Vishesh_P_S_Name')}")
        
        # Prepare data for insertion (Pydantic model ke field names)
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        values = tuple(data.values())
        
        query = f"INSERT INTO ATROCITY ({columns}) VALUES ({placeholders})"
        
        cursor.execute(query, values)
        connection.commit()
        last_id = cursor.lastrowid
        return {"Case_No": last_id, "message": "Atrocity case filed successfully."}
    except Exception as e:
        print(f"DBT Database Insertion Error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database insertion failed: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@router.post("/submit_fir", status_code=status.HTTP_201_CREATED)
async def submit_fir_form(
    isDrafted: bool = Query(False),
    # --- FIR Details (Form Data)
    firNumber: str = Form(..., description="FIR_NO"),
    # incidentDescription: str = Form(..., description="Case_Description"),
    firDocument: UploadFile = File(..., description="FIR Document File"),

    # --- Victim Details (Form Data)
    # name: str = Form(..., description="Victim_Name"),
    # dob: str = Form(..., description="Victim_DOB (YYYY-MM-DD)"),
    # relation: str = Form(..., description="Father_Name/Husband_Name"),
    # gender: str = Form(..., description="Gender"),
    caste: str = Form(..., description="Caste"),
    aadhaar: str = Form(..., description="Aadhar_No"),
    # mobile: str = Form(..., description="Victim_Mobile_No"),
    email: Optional[str] = Form(None, description="Applicant_Email"),
    photo: UploadFile = File(..., description="Victim_Image_No"),

    # --- Proof Documents (File Uploads)
    casteCertificate: UploadFile = File(..., description="Caste_Certificate_No"),
    medicalCertificate: Optional[UploadFile] = File(None, description="Medical_Report_Image"),
    postmortem: Optional[UploadFile] = File(None, description="Postmortem Report Image (Not in DB schema, but relevant)"),
    # otherDocument: Optional[UploadFile] = File(None, description="Other Document"),
    
    # --- Bank Details (Form Data)
    accountNumber: str = Form(..., description="Bank_Account_No"),
    ifscCode: Optional[str] = Form(None, description="IFSC_Code"),
    holderName: Optional[str] = Form(None, description="Holder_Name"),
    bankName: str = Form(..., description="Bank Name"), 
    # branchName: str = Form(..., description="Branch Name (Not in DB)"),
    
    # Authenticated user info
    token_payload: dict = Depends(verify_jwt_token)
):
    aadhaar_data = None
    fir_data = None
    
    try:
        aadhaar_data = get_aadhaar_by_number(aadhaar)
        fir_data = get_fir_by_number(firNumber)

        if aadhaar_data is None or fir_data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aadhaar/FIR data not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Cannot fetch Aadhaar/FIR data: {e}")
    
    # --- 1. Data Validation (Pydantic) ---
    try:

        # Convert date string to date object for validation

        
        # Prepare data structure for Pydantic validation (DB schema mapping)
        input_data = {

            # FIR Details
            "FIR_NO": firNumber, # FIR_NO is INT in DB
            "Case_Description": fir_data.incident_summary,
            
            # Victim Details
            "Victim_Name": fir_data.victim_name,
            "Father_Name": aadhaar_data.father_name,
            "Victim_DOB": aadhaar_data.dob,
            "Gender": aadhaar_data.gender.lower(),
            "Victim_Mobile_No": aadhaar_data.mobile,
            "Aadhar_No": int(aadhaar) if aadhaar else None, # Aadhar is BIGINT in DB
            "Caste": caste,

            # Bank Details
            "Bank_Account_No": accountNumber,
            "IFSC_Code": ifscCode,
            "Holder_Name": holderName,
            "Bank_Name": bankName,

            # Applicant Details (assuming victim is applicant for simplicity based on form data)
            "Applicant_Name": fir_data.complainant_name, 
            "Applicant_Relation": fir_data.complainant_relation,
            "Applicant_Mobile_No": fir_data.complainant_contact,
            "Applicant_Email": email,
            "Applied_Acts": fir_data.sections_invoked,
            "Location": fir_data.incident_location,
            "Date_of_Incident": fir_data.incident_date,

            # Stage and Pending_At logic based on isDrafted
            # If isDrafted=True: stays at Stage 0 (IO draft)
            # If isDrafted=False: moves to Stage 1 (Tribal Officer pending)
            "Stage": 0 if isDrafted else 1,
            "Pending_At": 'Investigation Officer' if isDrafted else 'Tribal Officer',
            
            # Jurisdiction fields (captured from IO's JWT token - the filing officer)
            "State_UT": token_payload.get('state_ut'),
            "District": token_payload.get('district'),
            "Vishesh_P_S_Name": token_payload.get('vishesh_p_s_name'),
        }
        
        # Debug logging
        print(f"DEBUG: JWT Token Payload: {token_payload}")
        print(f"DEBUG: isDrafted={isDrafted}, Stage will be set to {'0 (Draft)' if isDrafted else '1 (Submit)'}")
        print(f"DEBUG: Extracted Jurisdiction - State_UT: {token_payload.get('state_ut')}, District: {token_payload.get('district')}, PS: {token_payload.get('vishesh_p_s_name')}")
        
        # Validate data against the schema
        case_data = AtrocityBase(**input_data)

    except (ValidationError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Validation Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid data format: {e}")

    # --- 2. File Upload and Mapping ---
    
    # Unique prefix for file storage
    file_prefix = f"FIR{firNumber}_{token_payload.get('sub')}" 
    
    # Save files and get the names to store in the DB
    try:
        # DB Field: FIR_Document (Assuming we need a new column for this, 
        # as it's not in the provided schema but is required by the form)
        fir_doc_name = save_uploaded_file(firDocument, f"{file_prefix}_FIR")
        
        # DB Field: Victim_Image_No
        photo_name = save_uploaded_file(photo, f"{file_prefix}_PHOTO")
        
        # DB Field: Caste_Certificate_No
        caste_cert_name = save_uploaded_file(casteCertificate, f"{file_prefix}_CASTE")
        
        # DB Field: Medical_Report_Image
        medical_report_name = ""
        if medicalCertificate:
            medical_report_name = save_uploaded_file(medicalCertificate, f"{file_prefix}_MEDICAL")
        
    except HTTPException:
        # Re-raise file upload errors
        raise

    # --- 3. Final DB Data Preparation ---
    db_payload = case_data.model_dump()
    
    # Add file paths to the payload. These correspond to the DB columns.
    db_payload['Caste_Certificate_No'] = caste_cert_name
    db_payload['Medical_Report_Image'] = medical_report_name
    db_payload['Victim_Image_No'] = photo_name
    
    # Add jurisdiction fields from JWT token
    db_payload['State_UT'] = token_payload.get('state_ut')
    db_payload['District'] = token_payload.get('district')
    db_payload['Vishesh_P_S_Name'] = token_payload.get('vishesh_p_s_name')
    
    print(f"DEBUG: Final DB Payload - State_UT: {db_payload.get('State_UT')}, District: {db_payload.get('District')}, PS: {db_payload.get('Vishesh_P_S_Name')}")
    
    # Note: Passbook_Image is missing from the form, we'll assume it's blank for now.
    db_payload['Passbook_Image'] = "" 
    
    # NOTE: Bank Name and Branch Name are not in the ATROCITY table, 
    # they should be stored in a separate BANK_DETAILS table or a JSON/text field.
    # For simplicity, they are skipped for ATROCITY table insertion.

    # --- 4. Check if FIR already exists (prevent duplicates) ---
    existing_case = get_fir_data_by_fir_no(firNumber)
    
    if existing_case:
        # FIR already exists - UPDATE instead of INSERT (UPSERT pattern)
        case_no = existing_case.Case_No
        print(f"DEBUG: FIR {firNumber} already exists as Case #{case_no}. Updating instead of inserting.")
        
        # Only update allowed fields to prevent overwriting sensitive data
        update_payload = {
            "Stage": 0 if isDrafted else 1,
            "Pending_At": 'Investigation Officer' if isDrafted else 'Tribal Officer',
            "Approved_By": token_payload.get('sub')
        }
        
        try:
            update_atrocity_case(case_no, update_payload)
            print(f"DEBUG: Case #{case_no} updated successfully")
        except Exception as e:
            print(f"ERROR: Failed to update case {case_no}: {e}")
            raise
        
        response = {"Case_No": case_no, "message": "Atrocity case updated successfully (already exists)."}
    else:
        # FIR doesn't exist - INSERT new record
        response = insert_atrocity_case(db_payload)
        case_no = response.get("Case_No")
        print(f"DEBUG: New case #{case_no} created for FIR {firNumber}")
    
    # --- 5. Insert FIR_SUBMITTED event only if final submit (not draft) ---
    # Check if FIR_SUBMITTED event already exists for this case to prevent duplicate events
    timeline = get_timeline(case_no)
    fir_submitted_exists = any(event.event_type == "FIR_SUBMITTED" for event in timeline)
    
    if not isDrafted and not fir_submitted_exists:
        event_data = {
            "comment": "FIR submitted by Investigation Officer",
            "is_draft": False
        }
        insert_case_event(
            case_no=case_no,
            performed_by=token_payload.get('sub'),
            performed_by_role=token_payload.get('role'),
            event_type="FIR_SUBMITTED",
            event_data=event_data
        )
        print(f"DEBUG: FIR_SUBMITTED event inserted for case {case_no}")
    else:
        reason = "isDrafted=True" if isDrafted else "FIR_SUBMITTED event already exists"
        print(f"DEBUG: Case {case_no} - No new FIR_SUBMITTED event inserted ({reason}).")
    
    # --- 6. Return success response with stage and pending_at info ---
    return {
        "case_no": case_no,
        "fir_no": firNumber,
        "stage": 0 if isDrafted else 1,
        "pending_at": "Investigation Officer" if isDrafted else "Tribal Officer",
        "is_drafted": isDrafted,
        "is_update": existing_case is not None,
        "message": f"FIR saved as {'draft' if isDrafted else 'submitted successfully'}. Case #{case_no} {'created' if not existing_case else 'updated'}."
    }


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
        
        # Tribal Officer or District Magistrate: match district + state
        elif role in ("Tribal Officer", "District Collector/DM/SJO"):
            if case.State_UT == user_state and case.District == user_district:
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


@router.get("/get-fir-form-data")
async def get_fir_form_data(
    pending_at: str = Query("", max_length=100),
    approved_by: str = Query("", max_length=100),
    stage: conint(ge=0, le=10) = 0,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get all cases filtered by user's jurisdiction.
    
    Each officer role only sees cases within their assigned geographic area:
    - IO: cases from their Vishesh P.S.
    - TO/DM: cases from their district
    - SNO: cases from their state
    - PFMS: cases from their state at fund stages (4, 6, 7)
    """
    data: list[AtrocityDBModel] = get_all_fir_data()
    
    # Apply jurisdiction filter first
    data = filter_cases_by_jurisdiction(data, token_payload)
    
    # Then apply query filters
    if pending_at:
        data = [d for d in data if d.Pending_At == pending_at]
    if approved_by:
        data = [d for d in data if d.Approved_By == approved_by]
    if stage:
        data = [d for d in data if d.Stage == stage]
    
    # Return as list of dicts for proper JSON serialization
    return [d.model_dump() for d in data]

@router.get("/get-fir-form-data/fir/{fir_no}", response_model=AtrocityFullRecord)
async def get_fir_form_data_by_case_no(
    fir_no: str,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get full case details by FIR number.
    
    Returns 403 if user lacks jurisdiction access to the case.
    """
    # Get FIR data from database
    data = get_fir_data_by_fir_no(fir_no)
    
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    # Validate jurisdiction access
    validate_jurisdiction(token_payload, data)
    
    docs = get_documents_by_fir_no(fir_no)

    return AtrocityFullRecord(
        data=data,
        documents=docs,
        events=get_timeline(data.Case_No)
    )


# ======================================================================
# WORKFLOW ENDPOINTS (Per BACKEND_DATA_CONTRACT.md)
# ======================================================================

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
                detail=f"Access denied: Case belongs to PS '{case_ps}', but you are assigned to '{user_ps}'"
            )
        return
    
    # Tribal Officer or District Magistrate: must match district AND state
    if role in ("Tribal Officer", "District Collector/DM/SJO"):
        if case_state != user_state or case_district != user_district:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Case is in {case_district}, {case_state}, but you are assigned to {user_district}, {user_state}"
            )
        return
    
    # State Nodal Officer: must match state only
    if role == "State Nodal Officer":
        if case_state != user_state:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Case is in state '{case_state}', but you are assigned to '{user_state}'"
            )
        return
    
    # PFMS Officer: must match state AND case must be at fund release stage
    if role == "PFMS Officer":
        if case_state != user_state:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Case is in state '{case_state}', but you are assigned to '{user_state}'"
            )
        if case.Stage not in (4, 6, 7):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"PFMS can only access cases at fund release stages (4, 6, 7). Case is at stage {case.Stage}"
            )
        return


def validate_role_for_action(
    token_payload: dict, 
    payload_role: str, 
    case: AtrocityDBModel, 
    expected_stage: int | list[int]
):
    """
    Validates that:
    1. JWT user role matches the role claimed in payload (403 if mismatch)
    2. Case is at the expected stage for this action (400 if wrong stage)
    3. The claimed role is allowed to act at this stage (403 if not allowed)
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
    allowed_role = STAGE_ALLOWED_ROLE.get(case.Stage)
    if allowed_role and payload_role != allowed_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{payload_role}' cannot act at stage {case.Stage}. Expected: '{allowed_role}'"
        )


@router.post("/{case_no}/approve", status_code=status.HTTP_200_OK)
async def approve_case(
    case_no: int,
    payload: ApprovalPayload,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Approve a case and move it to the next stage.
    
    Allowed transitions:
    - Stage 1 (TO verifies) → Stage 2 (DM pending)
    - Stage 2 (DM approves) → Stage 3 (SNO pending)
    - Stage 3 (SNO sanctions) → Stage 4 (PFMS pending)
    """
    # Get current case
    case = get_fir_data_by_case_no(case_no)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    # Validate jurisdiction access
    validate_jurisdiction(token_payload, case)
    
    # Ensure stage is set
    if case.Stage is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Case stage is not set")
    
    # Validate role and stage (stages 1, 2, 3 allow approve action)
    validate_role_for_action(token_payload, payload.role, case, [0, 1, 2, 3])
    
    # Determine event type based on current stage
    event_type = STAGE_APPROVAL_EVENT.get(case.Stage, "APPROVED")
    
    # Insert event
    event_data = {
        "comment": payload.comment,
        "next_stage": payload.next_stage,
        **(payload.payload or {})
    }
    insert_case_event(
        case_no=case_no,
        performed_by=payload.actor,
        performed_by_role=payload.role,
        event_type=event_type,
        event_data=event_data
    )
    
    # Update case stage and pending_at
    next_pending_at = STAGE_NEXT_PENDING_AT.get(case.Stage, "")
    update_atrocity_case(case_no, {
        "Stage": payload.next_stage,
        "Pending_At": next_pending_at,
        "Approved_By": payload.actor
    })
    
    return {
        "message": f"Case {case_no} approved successfully",
        "new_stage": payload.next_stage,
        "pending_at": next_pending_at,
        "event_type": event_type
    }


@router.post("/{case_no}/correction", status_code=status.HTTP_200_OK)
async def request_correction(
    case_no: int,
    payload: CorrectionPayload,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Request correction on a case. Only DM can do this at stage 2.
    Case goes back to Tribal Officer (stage 1).
    
    Transition: Stage 2 → Stage 1 (DM → Tribal Officer)
    """
    # Get current case
    case = get_fir_data_by_case_no(case_no)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    # Validate jurisdiction access
    validate_jurisdiction(token_payload, case)
    
    # Only DM at stage 2 can request correction
    validate_role_for_action(token_payload, payload.role, case, 2)
    
    if payload.role != "District Magistrate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only District Magistrate can request corrections"
        )
    
    # Insert correction event
    event_data = {
        "comment": payload.comment,
        "corrections_required": payload.corrections_required
    }
    insert_case_event(
        case_no=case_no,
        performed_by=payload.actor,
        performed_by_role=payload.role,
        event_type="DM_CORRECTION",
        event_data=event_data
    )
    
    # Send case back to Tribal Officer (stage 1)
    update_atrocity_case(case_no, {
        "Stage": 1,
        "Pending_At": "Tribal Officer"
    })
    
    return {
        "message": f"Correction requested for case {case_no}",
        "new_stage": 1,
        "pending_at": "Tribal Officer",
        "corrections_required": payload.corrections_required
    }


@router.post("/{case_no}/fund-release", status_code=status.HTTP_200_OK)
async def release_funds(
    case_no: int,
    payload: FundReleasePayload,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Release funds (tranche) to the victim. PFMS Officer only.
    
    Tranche stages:
    - Stage 4: First 25% → Stage 5 (chargesheet pending)
    - Stage 6: Second 25-50% → Stage 7 (judgment pending)
    - Stage 7: Final tranche → Stage 8 (case closed)
    
    Fund amounts are tracked ONLY in CASE_EVENTS (not in ATROCITY table).
    """
    # Get current case
    case = get_fir_data_by_case_no(case_no)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    # Validate jurisdiction access
    validate_jurisdiction(token_payload, case)
    
    # PFMS Officer can release funds at stages 4, 6, 7
    validate_role_for_action(token_payload, payload.role, case, [4, 6, 7])
    
    if payload.role != "PFMS Officer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only PFMS Officer can release funds"
        )
    
    # Determine tranche type and next stage
    current_stage = case.Stage
    if current_stage == 4:
        event_type = "PFMS_FIRST_TRANCHE"
        next_stage = 5
        next_pending_at = "Investigation Officer"
        tranche_label = "First Tranche (25%)"
    elif current_stage == 6:
        event_type = "PFMS_SECOND_TRANCHE"
        next_stage = 7
        next_pending_at = "District Magistrate"
        tranche_label = "Second Tranche (25-50%)"
    elif current_stage == 7:
        event_type = "PFMS_FINAL_TRANCHE"
        next_stage = 8
        next_pending_at = ""  # Case closed
        tranche_label = "Final Tranche"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fund release not allowed at stage {current_stage}"
        )
    
    # Insert fund release event with all tranche details
    event_data = {
        "amount": payload.amount,
        "percent_of_total": payload.percent_of_total,
        "fund_type": payload.fund_type,
        "txn_id": payload.txn_id,
        "bank_acknowledgement": payload.bank_acknowledgement,
        "tranche_label": tranche_label
    }
    insert_case_event(
        case_no=case_no,
        performed_by=payload.actor,
        performed_by_role=payload.role,
        event_type=event_type,
        event_data=event_data
    )
    
    # Update case stage (Fund_Ammount stays unchanged - it's total approved amount)
    update_atrocity_case(case_no, {
        "Stage": next_stage,
        "Pending_At": next_pending_at
    })
    
    return {
        "message": f"{tranche_label} released for case {case_no}",
        "amount": payload.amount,
        "percent_of_total": payload.percent_of_total,
        "txn_id": payload.txn_id,
        "new_stage": next_stage,
        "pending_at": next_pending_at
    }


@router.post("/{case_no}/chargesheet", status_code=status.HTTP_200_OK)
async def submit_chargesheet(
    case_no: int,
    payload: ChargeSheetPayload,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Submit chargesheet for a case. Investigation Officer only at stage 5.
    
    Transition: Stage 5 → Stage 6 (Chargesheet submitted, second tranche pending)
    """
    # Get current case
    case = get_fir_data_by_case_no(case_no)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    # Validate jurisdiction access
    validate_jurisdiction(token_payload, case)
    
    # IO at stage 5 can submit chargesheet
    validate_role_for_action(token_payload, payload.role, case, 5)
    
    if payload.role != "Investigation Officer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Investigation Officer can submit chargesheet"
        )
    
    # Insert chargesheet event
    event_data = {
        "chargesheet_no": payload.chargesheet_no,
        "chargesheet_date": payload.chargesheet_date,
        "court_name": payload.court_name,
        "severity": payload.severity
    }
    insert_case_event(
        case_no=case_no,
        performed_by=payload.actor,
        performed_by_role=payload.role,
        event_type="CHARGESHEET_SUBMITTED",
        event_data=event_data
    )
    
    # Move to stage 6 (second tranche pending)
    update_atrocity_case(case_no, {
        "Stage": 6,
        "Pending_At": "PFMS Officer"
    })
    
    return {
        "message": f"Chargesheet submitted for case {case_no}",
        "chargesheet_no": payload.chargesheet_no,
        "new_stage": 6,
        "pending_at": "PFMS Officer"
    }


@router.post("/{case_no}/complete", status_code=status.HTTP_200_OK)
async def complete_case(
    case_no: int,
    payload: CaseCompletionPayload,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Complete a case with judgment details. District Magistrate only at stage 7.
    
    After judgment, case moves to awaiting final tranche (stays at stage 7,
    pending at PFMS Officer for final release).
    
    Note: This records the judgment. Final fund release is a separate call.
    """
    # Get current case
    case = get_fir_data_by_case_no(case_no)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    # Validate jurisdiction access
    validate_jurisdiction(token_payload, case)
    
    # DM at stage 7 can complete case
    # Note: At stage 7, DM records judgment (allowed role should be DM here)
    jwt_role = token_payload.get("role")
    if jwt_role != payload.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role mismatch: JWT role '{jwt_role}' does not match payload role '{payload.role}'"
        )
    
    if case.Stage != 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Case is at stage {case.Stage}, but completion requires stage 7"
        )
    
    if payload.role != "District Magistrate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only District Magistrate can complete a case"
        )
    
    # Insert judgment event
    event_data = {
        "judgment_ref": payload.judgment_ref,
        "judgment_date": payload.judgment_date,
        "verdict": payload.verdict,
        "notes": payload.notes
    }
    insert_case_event(
        case_no=case_no,
        performed_by=payload.actor,
        performed_by_role=payload.role,
        event_type="DM_JUDGMENT_RECORDED",
        event_data=event_data
    )
    
    # Case stays at stage 7 but now awaits final tranche from PFMS
    update_atrocity_case(case_no, {
        "Pending_At": "PFMS Officer",
        "Approved_By": payload.actor
    })
    
    return {
        "message": f"Judgment recorded for case {case_no}",
        "judgment_ref": payload.judgment_ref,
        "verdict": payload.verdict,
        "stage": 7,
        "pending_at": "PFMS Officer",
        "note": "Awaiting final tranche release"
    }


@router.get("/{case_no}/events", response_model=list[CaseEvent])
async def get_case_events(
    case_no: int,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get all timeline events for a case.
    Requires JWT authentication (any authenticated user can view).
    """
    # Verify case exists
    case = get_fir_data_by_case_no(case_no)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    # Validate jurisdiction access
    validate_jurisdiction(token_payload, case)
    
    events = get_timeline(case_no)
    return events