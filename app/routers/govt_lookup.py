# app/routers/govt_lookup.py
"""
Government Records Lookup APIs

Provides endpoints to fetch government records:
- Aadhaar Records
- Caste Certificates
- NPCI Bank KYC

Access: Citizens & Officers (used for validation and verification)
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Depends

from app.core.security import verify_jwt_token
from app.schemas.govt_record_schemas import AadhaarRecord, CasteCertificate, NPCIBankKYC
from app.db.govt_session import (
    get_aadhaar_by_number,
    get_caste_certificate_by_id,
    get_caste_certificates_by_aadhaar,
    get_caste_certificates_by_person_name,
    get_caste_certificates_by_category,
    get_npci_kyc_by_id,
    get_npci_kyc_by_account_number,
    get_npci_kyc_by_primary_aadhaar,
    get_npci_kyc_by_secondary_aadhaar,
    get_npci_kyc_by_bank_name,
    get_npci_kyc_by_status
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/govt",
    tags=["Government Records Lookup"],
)


# ======================== AADHAAR ENDPOINTS ========================

@router.get("/aadhaar/{aadhaar_number}", response_model=AadhaarRecord)
async def get_aadhaar_details(
    aadhaar_number: str,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get Aadhaar record details by Aadhaar number.
    
    Used for:
    - Validating Aadhaar existence during ICM application
    - Verifying groom/bride Aadhaar before approval
    - Cross-referencing with other documents
    
    Access: Citizens & Officers
    """
    aadhaar_data = get_aadhaar_by_number(aadhaar_number)
    
    if not aadhaar_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aadhaar record not found for ID: {aadhaar_number}"
        )
    
    logger.info(f"Aadhaar lookup: {aadhaar_number}, accessed by user: {token_payload.get('sub')}")
    
    return aadhaar_data


# ======================== CASTE CERTIFICATE ENDPOINTS ========================

@router.get("/caste-certificate/{certificate_id}", response_model=CasteCertificate)
async def get_caste_certificate_details(
    certificate_id: str,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get Caste Certificate by certificate ID.
    
    Used for:
    - Validating caste certificate during ICM application
    - Verifying SC/ST eligibility
    - Ensuring at least one spouse has valid caste certificate
    
    Access: Citizens & Officers
    """
    cert_data = get_caste_certificate_by_id(certificate_id)
    
    if not cert_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Caste certificate not found for ID: {certificate_id}"
        )
    
    logger.info(f"Caste certificate lookup: {certificate_id}, accessed by user: {token_payload.get('sub')}")
    
    return cert_data


@router.get("/caste-certificates/aadhaar/{aadhaar_number}", response_model=List[CasteCertificate])
async def get_caste_certificates_by_person_aadhaar(
    aadhaar_number: int,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get all Caste Certificates for a person by their Aadhaar number.
    
    Returns all certificates issued to or linked with this Aadhaar number.
    Useful for verifying multiple certificates or finding the valid one.
    
    Access: Citizens & Officers
    """
    cert_data = get_caste_certificates_by_aadhaar(aadhaar_number)
    
    if not cert_data:
        logger.info(f"No caste certificates found for Aadhaar: {aadhaar_number}")
        return []
    
    logger.info(f"Caste certificate lookup by Aadhaar: {aadhaar_number}, accessed by user: {token_payload.get('sub')}")
    
    return cert_data


@router.get("/caste-certificates/name/{person_name}", response_model=List[CasteCertificate])
async def get_caste_certificates_by_name(
    person_name: str,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get Caste Certificates by person name (supports partial matches).
    
    Useful for:
    - Searching certificates when Aadhaar is not available
    - Finding all certificates for a name variation
    
    Access: Citizens & Officers
    """
    cert_data = get_caste_certificates_by_person_name(person_name)
    
    if not cert_data:
        logger.info(f"No caste certificates found for name: {person_name}")
        return []
    
    logger.info(f"Caste certificate lookup by name: {person_name}, accessed by user: {token_payload.get('sub')}")
    
    return cert_data


@router.get("/caste-certificates/category/{category}", response_model=List[CasteCertificate])
async def get_caste_certificates_by_caste_category(
    category: str,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get Caste Certificates by caste category (SC, ST, OBC, General).
    
    Useful for:
    - Verifying SC/ST eligibility for the scheme
    - Finding all SC/ST certificates in a database
    
    Category values: "SC", "ST", "OBC", "General"
    
    Access: Citizens & Officers
    """
    if category.upper() not in ["SC", "ST", "OBC", "GENERAL"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category. Use: SC, ST, OBC, or General"
        )
    
    cert_data = get_caste_certificates_by_category(category.upper())
    
    if not cert_data:
        logger.info(f"No caste certificates found for category: {category}")
        return []
    
    logger.info(f"Caste certificate lookup by category: {category}, accessed by user: {token_payload.get('sub')}")
    
    return cert_data


# ======================== NPCI BANK KYC ENDPOINTS ========================

@router.get("/bank-kyc/{kyc_id}", response_model=NPCIBankKYC)
async def get_bank_kyc_details(
    kyc_id: str,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get NPCI Bank KYC details by KYC ID.
    
    Used for:
    - Validating joint bank account information
    - Verifying account holder names and Aadhaar numbers
    
    Access: Citizens & Officers
    """
    kyc_data = get_npci_kyc_by_id(kyc_id)
    
    if not kyc_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NPCI Bank KYC not found for ID: {kyc_id}"
        )
    
    logger.info(f"Bank KYC lookup: {kyc_id}, accessed by user: {token_payload.get('sub')}")
    
    return kyc_data


@router.get("/bank-kyc/account/{account_number}", response_model=List[NPCIBankKYC])
async def get_bank_kyc_by_account(
    account_number: str,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get NPCI Bank KYC records by account number.
    
    Validates:
    - Account exists and is JOINT type
    - Account holder names and Aadhaar numbers
    - Matching groom/bride Aadhaar with account holders
    
    Access: Citizens & Officers
    """
    kyc_data = get_npci_kyc_by_account_number(account_number)
    
    if not kyc_data:
        logger.info(f"No KYC records found for account: {account_number}")
        return []
    
    logger.info(f"Bank KYC lookup by account: {account_number}, accessed by user: {token_payload.get('sub')}")
    
    return kyc_data


@router.get("/bank-kyc/primary-aadhaar/{primary_aadhaar}", response_model=List[NPCIBankKYC])
async def get_bank_kyc_by_primary(
    primary_aadhaar: int,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get NPCI Bank KYC records where given Aadhaar is primary account holder.
    
    Used for:
    - Finding all joint accounts where someone is primary holder
    - Verifying primary holder identity
    
    Access: Citizens & Officers
    """
    kyc_data = get_npci_kyc_by_primary_aadhaar(primary_aadhaar)
    
    if not kyc_data:
        logger.info(f"No KYC records found for primary Aadhaar: {primary_aadhaar}")
        return []
    
    logger.info(f"Bank KYC lookup by primary Aadhaar: {primary_aadhaar}, accessed by user: {token_payload.get('sub')}")
    
    return kyc_data


@router.get("/bank-kyc/secondary-aadhaar/{secondary_aadhaar}", response_model=List[NPCIBankKYC])
async def get_bank_kyc_by_secondary(
    secondary_aadhaar: int,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get NPCI Bank KYC records where given Aadhaar is secondary account holder.
    
    Used for:
    - Finding all joint accounts where someone is secondary holder
    - Verifying secondary holder identity
    
    Access: Citizens & Officers
    """
    kyc_data = get_npci_kyc_by_secondary_aadhaar(secondary_aadhaar)
    
    if not kyc_data:
        logger.info(f"No KYC records found for secondary Aadhaar: {secondary_aadhaar}")
        return []
    
    logger.info(f"Bank KYC lookup by secondary Aadhaar: {secondary_aadhaar}, accessed by user: {token_payload.get('sub')}")
    
    return kyc_data


@router.get("/bank-kyc/bank/{bank_name}", response_model=List[NPCIBankKYC])
async def get_bank_kyc_by_bank(
    bank_name: str,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get NPCI Bank KYC records by bank name.
    
    Useful for:
    - Finding all accounts in a specific bank
    - Administrative/audit purposes
    
    Access: Citizens & Officers
    """
    kyc_data = get_npci_kyc_by_bank_name(bank_name)
    
    if not kyc_data:
        logger.info(f"No KYC records found for bank: {bank_name}")
        return []
    
    logger.info(f"Bank KYC lookup by bank: {bank_name}, accessed by user: {token_payload.get('sub')}")
    
    return kyc_data


@router.get("/bank-kyc/status/{kyc_status}", response_model=List[NPCIBankKYC])
async def get_bank_kyc_by_kyc_status(
    kyc_status: str,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get NPCI Bank KYC records by KYC status.
    
    Status values: "verified", "pending", "rejected"
    
    Useful for:
    - Finding only verified accounts for fund transfer
    - Audit trail of pending/rejected KYC
    
    Access: Citizens & Officers
    """
    if kyc_status.lower() not in ["verified", "pending", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Use: verified, pending, or rejected"
        )
    
    kyc_data = get_npci_kyc_by_status(kyc_status.lower())
    
    if not kyc_data:
        logger.info(f"No KYC records found with status: {kyc_status}")
        return []
    
    logger.info(f"Bank KYC lookup by status: {kyc_status}, accessed by user: {token_payload.get('sub')}")
    
    return kyc_data
