# app/routers/dbt.py
import shutil
import os
import re
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import Dict, Any, Optional, List
from datetime import date
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.core.security import verify_jwt_token # Protection
from app.db.session import get_dbt_db_connection, get_all_fir_data, get_fir_data_by_fir_no
from app.schemas.dbt_schemas import AtrocityBase
from app.db.govt_session import get_fir_by_number, get_aadhaar_by_number
from app.schemas.govt_record_schemas import FIRRecord, AadhaarRecord

router = APIRouter(
    prefix="/dbt/case",
    tags=["DBT Case Management"],
    # Yahan JWT security lagao
    dependencies=[Depends(verify_jwt_token)] 
)

# --- Response Models for Documents ---
class DocumentInfo(BaseModel):
    """Information about a single document with base64 encoded content"""
    filename: str
    file_type: str
    content: str  # Base64 encoded file content
    file_size: int  # File size in bytes
    mime_type: str  # MIME type for proper rendering

class DocumentsByType(BaseModel):
    """Documents organized by type"""
    FIR: List[DocumentInfo] = []
    PHOTO: List[DocumentInfo] = []
    CASTE: List[DocumentInfo] = []
    MEDICAL: List[DocumentInfo] = []
    POSTMORTEM: List[DocumentInfo] = []
    OTHER: List[DocumentInfo] = []

class AtrocityWithDocuments(AtrocityBase):
    """Atrocity case with associated documents"""
    documents: DocumentsByType = DocumentsByType()

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

@router.get("/get-fir-form-data", response_model=list[AtrocityBase])
async def get_fir_form_data():
    return get_all_fir_data()

@router.get("/get-fir-form-data/fir/{fir_no}", response_model=AtrocityWithDocuments)
async def get_fir_form_data_by_case_no(fir_no: str):
    """
    Retrieves FIR data along with all associated documents organized by type.
    
    Documents are identified by FIR number and organized by document type:
    - FIR: FIR documents
    - PHOTO: Victim photos
    - CASTE: Caste certificates
    - MEDICAL: Medical reports
    - POSTMORTEM: Postmortem reports
    - OTHER: Other documents
    """
    # Get FIR data from database
    fir_data = get_fir_data_by_fir_no(fir_no)
    
    # Get associated documents organized by type
    documents = get_documents_by_fir_no(fir_no)
    
    # Convert FIR data to dict and add documents
    fir_dict = fir_data if isinstance(fir_data, dict) else fir_data.__dict__
    
    # Create response with documents
    response = AtrocityWithDocuments(
        documents=documents,
        **fir_dict
    )
    
    return response