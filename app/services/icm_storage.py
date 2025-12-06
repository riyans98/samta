# app/services/icm_storage.py
"""
ICM File Storage Module

Handles file saving and retrieval for ICM documents.
Uses same naming pattern as atrocity: ICM{icm_id}_{uploader}_{TYPE}.{ext}
Document retrieval returns base64-encoded content matching get_documents_by_fir_no() format.
"""

import os
import re
import base64
import logging
from typing import Optional, List, Dict, Any
from fastapi import UploadFile, HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)

# Allowed file types for ICM documents
ALLOWED_CONTENT_TYPES = [
    'image/png',
    'image/jpeg',
    'image/jpg',
    'application/pdf'
]

# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# ICM Document types (only 4 documents)
ICM_DOC_TYPES = {
    'MARRIAGE': 'marriage_certificate_file',
    'GROOM_SIGN': 'groom_signature_file',
    'BRIDE_SIGN': 'bride_signature_file',
    'WITNESS_SIGN': 'witness_signature_file'
}


def get_mime_type(filename: str) -> str:
    """Get MIME type from filename extension."""
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    mime_types = {
        'pdf': 'application/pdf',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
    }
    return mime_types.get(ext, 'application/octet-stream')


def validate_file(file: UploadFile, doc_type: str) -> None:
    """
    Validate uploaded file.
    
    Args:
        file: UploadFile object
        doc_type: Document type (MARRIAGE, GROOM_SIGN, etc.)
    
    Raises:
        HTTPException: If validation fails
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File required for {doc_type}"
        )
    
    # Check content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type for {doc_type}. Allowed: PNG, JPEG, PDF"
        )


async def save_icm_file(
    icm_id: int,
    file: UploadFile,
    doc_type: str,
    uploader: str = "citizen"
) -> str:
    """
    Save an ICM document file.
    
    Naming pattern: ICM{icm_id}_{uploader}_{TYPE}.{ext}
    Example: ICM123_citizen_MARRIAGE.pdf
    
    Args:
        icm_id: ICM application ID
        file: UploadFile object
        doc_type: Document type (MARRIAGE, GROOM_SIGN, BRIDE_SIGN, WITNESS_SIGN)
        uploader: Uploader identifier (default: citizen)
    
    Returns:
        Relative file path for storage in DB
    
    Raises:
        HTTPException: If file saving fails
    """
    if not file or not file.filename:
        return ""
    
    # Validate file
    validate_file(file, doc_type)
    
    # Get file extension
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'bin'
    
    # Create filename: ICM{icm_id}_{uploader}_{TYPE}.{ext}
    filename = f"ICM{icm_id}_{uploader}_{doc_type}.{ext}"
    
    # Ensure upload directory exists
    upload_dir = settings.UPLOAD_DIR
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_path = os.path.join(upload_dir, filename)
    
    try:
        # Read and validate file size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large for {doc_type}. Maximum size: 10MB"
            )
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"ICM file saved: {filename}, icm_id={icm_id}, type={doc_type}")
        
        # Return filename (not full path) for DB storage
        return filename
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save ICM file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file for {doc_type}"
        )
    finally:
        await file.seek(0)  # Reset file pointer


def get_icm_documents(icm_id: int) -> Dict[str, List[Dict[str, Any]]]:
    """
    Retrieve all documents for an ICM application with base64 encoding.
    
    Matches format of get_documents_by_fir_no() for consistency.
    
    Filename pattern: ICM{icm_id}_{uploader}_{TYPE}.{ext}
    
    Args:
        icm_id: ICM application ID
    
    Returns:
        Dictionary with document types as keys, each containing list of:
        - filename: str
        - file_type: str
        - content: str (base64 encoded)
        - file_size: int
        - mime_type: str
    """
    documents = {
        'MARRIAGE': [],
        'GROOM_SIGN': [],
        'BRIDE_SIGN': [],
        'WITNESS_SIGN': [],
        'OTHER': []
    }
    
    upload_dir = settings.UPLOAD_DIR
    if not os.path.exists(upload_dir):
        return documents
    
    try:
        # Pattern: ICM{icm_id}_{uploader}_{TYPE}.{ext}
        # Example: ICM2_citizen_12_GROOM_SIGN.png (uploader can have underscores like citizen_12)
        # Matches: ICM2_<anything>_<DOCUMENT_TYPE>.ext
        # Using non-greedy .+? to handle multiple underscores correctly
        pattern = rf"ICM{icm_id}_.+?_([A-Z_]+)\.[a-zA-Z0-9]+"
        
        for filename in os.listdir(upload_dir):
            match = re.match(pattern, filename)
            if match:
                file_type = match.group(1)
                file_path = os.path.join(upload_dir, filename)
                
                # Debug log
                logger.debug(f"Found ICM file: {filename}, type: {file_type}")
                
                try:
                    # Read file and encode as base64
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                    
                    file_size = len(file_content)
                    base64_content = base64.b64encode(file_content).decode('utf-8')
                    mime_type = get_mime_type(filename)
                    
                    doc_info = {
                        'filename': filename,
                        'file_type': file_type,
                        'content': base64_content,
                        'file_size': file_size,
                        'mime_type': mime_type
                    }
                    
                    # Organize by document type
                    if file_type in documents:
                        documents[file_type].append(doc_info)
                    else:
                        documents['OTHER'].append(doc_info)
                        
                except Exception as e:
                    logger.error(f"Error reading ICM file {filename}: {e}")
                    continue
                    
    except Exception as e:
        logger.error(f"Error retrieving ICM documents for icm_id={icm_id}: {e}")
    
    return documents


def delete_icm_files(icm_id: int) -> int:
    """
    Delete all files associated with an ICM application.
    
    Args:
        icm_id: ICM application ID
    
    Returns:
        Number of files deleted
    """
    deleted_count = 0
    upload_dir = settings.UPLOAD_DIR
    
    if not os.path.exists(upload_dir):
        return 0
    
    try:
        pattern = rf"ICM{icm_id}_.*"
        
        for filename in os.listdir(upload_dir):
            if re.match(pattern, filename):
                file_path = os.path.join(upload_dir, filename)
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    logger.info(f"Deleted ICM file: {filename}")
                except Exception as e:
                    logger.error(f"Failed to delete ICM file {filename}: {e}")
                    
    except Exception as e:
        logger.error(f"Error deleting ICM files for icm_id={icm_id}: {e}")
    
    return deleted_count
