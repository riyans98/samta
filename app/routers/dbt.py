# app/routers/dbt.py
import shutil
import os
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import Dict, Any, Optional
from datetime import date
from pydantic import ValidationError

from app.core.config import settings
from app.core.security import verify_jwt_token # Protection
from app.db.session import get_dbt_db_connection
from app.schemas.dbt_schemas import AtrocityBase, AtrocityData
from app.db.govt_session import get_fir_by_number, get_aadhaar_by_number
from app.schemas.govt_record_schemas import FIRRecord, AadhaarRecord

router = APIRouter(
    prefix="/dbt/case",
    tags=["DBT Case Management"],
    # Yahan JWT security lagao
    dependencies=[Depends(verify_jwt_token)] 
)

# File names ko DB mein store karne ke liye ek helper function
# app/routers/dbt.py (save_uploaded_file function ko replace karein)

import os
import shutil
from fastapi import UploadFile, HTTPException, status
# ... (other imports)
#removeed file_type: str to fix an error
def save_uploaded_file(file: UploadFile, base_name: str) -> str:
    """
    Saves the file to the local directory and returns the generated filename.

    :param file: The UploadFile object.
    :param base_name: The base name for the file (e.g., FIR_NO).
    :param file_type: Descriptive type (e.g., 'FIR', 'PHOTO', 'CASTE').
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

    # 2. Filename Format (e.g., 1234_FIR_DOC.pdf)
    # Isse unique file name banega: <BaseName>_<FILE_TYPE><extension>
    #generated_filename = f"{base_name}_{file_type.upper()}{file_extension.lower()}"
    file_type="FIR"  # removed to fix an error
    generated_filename = f"{base_name}_{file_type.upper()}{file_extension.lower()}"
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
    # --- FIR Details (Form Data)
    firNumber: str = Form(..., description="FIR_NO"),
    incidentDescription: str = Form(..., description="Case_Description"),
    firDocument: UploadFile = File(..., description="FIR Document File"),

    # --- Victim Details (Form Data)
    name: str = Form(..., description="Victim_Name"),
    dob: str = Form(..., description="Victim_DOB (YYYY-MM-DD)"),
    relation: str = Form(..., description="Father_Name/Husband_Name"),
    gender: str = Form(..., description="Gender"),
    caste: str = Form(..., description="Caste"),
    aadhaar: str = Form(..., description="Aadhar_No"),
    mobile: str = Form(..., description="Victim_Mobile_No"),
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
    branchName: str = Form(..., description="Branch Name (Not in DB)"),
    
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
        }
        
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
    
    # Note: Passbook_Image is missing from the form, we'll assume it's blank for now.
    db_payload['Passbook_Image'] = "" 
    
    # NOTE: Bank Name and Branch Name are not in the ATROCITY table, 
    # they should be stored in a separate BANK_DETAILS table or a JSON/text field.
    # For simplicity, they are skipped for ATROCITY table insertion.

    # --- 4. Database Insertion ---
    return insert_atrocity_case(db_payload)