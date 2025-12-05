from datetime import time, timedelta
from app.core.config import settings
import mysql.connector
from mysql.connector import Error
from fastapi import HTTPException, status
from app.schemas.govt_record_schemas import AadhaarRecord, FIRRecord, CasteCertificate, NPCIBankKYC
from typing import Optional, List, Dict, Any


# DB_CONFIG ko centralized kar diya gaya hai
GOVT_DB_CONFIG = {
    'host': settings.DB_HOST,
    'port': settings.DB_PORT,
    'user': settings.DB_USER,
    'password': settings.DB_PASSWORD,
    'database': settings.GOVT_DB_DATABASE
}

def get_govt_db_connection():
    """Establishes and returns a dummy database connection for govt database connection."""
    try:
        connection = mysql.connector.connect(**GOVT_DB_CONFIG)
        return connection
    except Error as e:
        print(f"Govt Database Connection Error: {e}")
        # Connection failure is a critical 500 error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Govt Database connection failed: {e}"
        )

# Database Access Functions with Pydantic Return Types

def get_aadhaar_by_number(aadhaar_number: str) -> Optional[AadhaarRecord]:
    connection = get_govt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM aadhaar_records WHERE aadhaar_id = %s"
        cursor.execute(query, (aadhaar_number,))
        result = cursor.fetchone()
        if result:
            return AadhaarRecord(**result)
        return None
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Aadhaar fetch failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()

def normalize_time(value):
    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())
        hours = (total_seconds // 3600) % 24
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return time(hour=hours, minute=minutes, second=seconds)
    return value

def get_fir_by_number(fir_number: str) -> Optional[FIRRecord]:
    connection = get_govt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM fir_records WHERE fir_no = %s"
        cursor.execute(query, (fir_number,))
        result = cursor.fetchone()
        if result:
            # Fix incident_time if needed
            if "incident_time" in result:
                result["incident_time"] = normalize_time(result["incident_time"])
            
            return FIRRecord(**result)
        return None
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"FIR fetch failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


# ======================== CASTE CERTIFICATE FUNCTIONS ========================

def get_caste_certificate_by_id(certificate_id: str) -> Optional[CasteCertificate]:
    """Fetch caste certificate by certificate ID."""
    connection = get_govt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM caste_certificates WHERE certificate_id = %s"
        cursor.execute(query, (certificate_id,))
        result = cursor.fetchone()
        if result:
            return CasteCertificate(**result)
        return None
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Caste Certificate fetch by ID failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


def get_caste_certificates_by_aadhaar(aadhaar_number: int) -> List[CasteCertificate]:
    """Fetch all caste certificates for a given Aadhaar number."""
    connection = get_govt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM caste_certificates WHERE aadhaar_number = %s"
        cursor.execute(query, (aadhaar_number,))
        results = cursor.fetchall()
        if results:
            return [CasteCertificate(**row) for row in results]
        return []
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Caste Certificate fetch by Aadhaar failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


def get_caste_certificates_by_person_name(person_name: str) -> List[CasteCertificate]:
    """Fetch caste certificates by person name (supports partial matches)."""
    connection = get_govt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM caste_certificates WHERE person_name LIKE %s"
        cursor.execute(query, (f"%{person_name}%",))
        results = cursor.fetchall()
        if results:
            return [CasteCertificate(**row) for row in results]
        return []
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Caste Certificate fetch by name failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


def get_caste_certificates_by_category(caste_category: str) -> List[CasteCertificate]:
    """Fetch caste certificates by caste category (SC, ST, OBC, General)."""
    connection = get_govt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM caste_certificates WHERE caste_category = %s"
        cursor.execute(query, (caste_category,))
        results = cursor.fetchall()
        if results:
            return [CasteCertificate(**row) for row in results]
        return []
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Caste Certificate fetch by category failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


def get_caste_certificates_by_status(status_filter: str) -> List[CasteCertificate]:
    """Fetch caste certificates by status (active, pending, expired, etc.)."""
    connection = get_govt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM caste_certificates WHERE certificate_status = %s"
        cursor.execute(query, (status_filter,))
        results = cursor.fetchall()
        if results:
            return [CasteCertificate(**row) for row in results]
        return []
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Caste Certificate fetch by status failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


def get_all_caste_certificates(filters: Optional[Dict[str, Any]] = None, limit: int = 100, offset: int = 0) -> List[CasteCertificate]:
    """Fetch all caste certificates with optional filters and pagination."""
    connection = get_govt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM caste_certificates WHERE 1=1"
        params = []
        
        if filters:
            if "caste_category" in filters:
                query += " AND caste_category = %s"
                params.append(filters["caste_category"])
            if "certificate_status" in filters:
                query += " AND certificate_status = %s"
                params.append(filters["certificate_status"])
            if "aadhaar_number" in filters:
                query += " AND aadhaar_number = %s"
                params.append(filters["aadhaar_number"])
            if "issuing_authority" in filters:
                query += " AND issuing_authority = %s"
                params.append(filters["issuing_authority"])
        
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        if results:
            return [CasteCertificate(**row) for row in results]
        return []
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Caste Certificate fetch all failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


# ======================== NPCI BANK KYC FUNCTIONS ========================

def get_npci_kyc_by_id(kyc_id: str) -> Optional[NPCIBankKYC]:
    """Fetch NPCI Bank KYC by KYC ID."""
    connection = get_govt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM npci_bank_kyc WHERE kyc_id = %s"
        cursor.execute(query, (kyc_id,))
        result = cursor.fetchone()
        if result:
            return NPCIBankKYC(**result)
        return None
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"NPCI KYC fetch by ID failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


def get_npci_kyc_by_account_number(account_number: str) -> List[NPCIBankKYC]:
    """Fetch NPCI Bank KYC by account number."""
    connection = get_govt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM npci_bank_kyc WHERE account_number = %s"
        cursor.execute(query, (account_number,))
        results = cursor.fetchall()
        if results:
            return [NPCIBankKYC(**row) for row in results]
        return []
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"NPCI KYC fetch by account number failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


def get_npci_kyc_by_primary_aadhaar(primary_aadhaar: int) -> List[NPCIBankKYC]:
    """Fetch NPCI Bank KYC by primary account holder's Aadhaar."""
    connection = get_govt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM npci_bank_kyc WHERE primary_aadhaar = %s"
        cursor.execute(query, (primary_aadhaar,))
        results = cursor.fetchall()
        if results:
            return [NPCIBankKYC(**row) for row in results]
        return []
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"NPCI KYC fetch by primary Aadhaar failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


def get_npci_kyc_by_secondary_aadhaar(secondary_aadhaar: int) -> List[NPCIBankKYC]:
    """Fetch NPCI Bank KYC by secondary account holder's Aadhaar."""
    connection = get_govt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM npci_bank_kyc WHERE secondary_aadhaar = %s"
        cursor.execute(query, (secondary_aadhaar,))
        results = cursor.fetchall()
        if results:
            return [NPCIBankKYC(**row) for row in results]
        return []
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"NPCI KYC fetch by secondary Aadhaar failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


def get_npci_kyc_by_bank_name(bank_name: str) -> List[NPCIBankKYC]:
    """Fetch NPCI Bank KYC records by bank name."""
    connection = get_govt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM npci_bank_kyc WHERE bank_name = %s"
        cursor.execute(query, (bank_name,))
        results = cursor.fetchall()
        if results:
            return [NPCIBankKYC(**row) for row in results]
        return []
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"NPCI KYC fetch by bank name failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


def get_npci_kyc_by_status(kyc_status: str) -> List[NPCIBankKYC]:
    """Fetch NPCI Bank KYC records by KYC status (verified, pending, rejected)."""
    connection = get_govt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM npci_bank_kyc WHERE kyc_status = %s"
        cursor.execute(query, (kyc_status,))
        results = cursor.fetchall()
        if results:
            return [NPCIBankKYC(**row) for row in results]
        return []
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"NPCI KYC fetch by status failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


def get_npci_kyc_by_ifsc_code(ifsc_code: str) -> List[NPCIBankKYC]:
    """Fetch NPCI Bank KYC records by IFSC code."""
    connection = get_govt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM npci_bank_kyc WHERE ifsc_code = %s"
        cursor.execute(query, (ifsc_code,))
        results = cursor.fetchall()
        if results:
            return [NPCIBankKYC(**row) for row in results]
        return []
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"NPCI KYC fetch by IFSC code failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


def get_npci_kyc_by_primary_holder_name(holder_name: str) -> List[NPCIBankKYC]:
    """Fetch NPCI Bank KYC records by primary holder name (supports partial matches)."""
    connection = get_govt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM npci_bank_kyc WHERE primary_holder_name LIKE %s"
        cursor.execute(query, (f"%{holder_name}%",))
        results = cursor.fetchall()
        if results:
            return [NPCIBankKYC(**row) for row in results]
        return []
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"NPCI KYC fetch by primary holder name failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


def get_all_npci_kyc(filters: Optional[Dict[str, Any]] = None, limit: int = 100, offset: int = 0) -> List[NPCIBankKYC]:
    """Fetch all NPCI Bank KYC records with optional filters and pagination."""
    connection = get_govt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM npci_bank_kyc WHERE 1=1"
        params = []
        
        if filters:
            if "bank_name" in filters:
                query += " AND bank_name = %s"
                params.append(filters["bank_name"])
            if "kyc_status" in filters:
                query += " AND kyc_status = %s"
                params.append(filters["kyc_status"])
            if "primary_aadhaar" in filters:
                query += " AND primary_aadhaar = %s"
                params.append(filters["primary_aadhaar"])
            if "account_type" in filters:
                query += " AND account_type = %s"
                params.append(filters["account_type"])
            if "primary_caste_category" in filters:
                query += " AND primary_caste_category = %s"
                params.append(filters["primary_caste_category"])
        
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        if results:
            return [NPCIBankKYC(**row) for row in results]
        return []
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"NPCI KYC fetch all failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()

