from datetime import time, timedelta
from app.core.config import settings
import mysql.connector
from mysql.connector import Error
from fastapi import HTTPException, status
from app.schemas.govt_record_schemas import AadhaarRecord, FIRRecord
from typing import Optional


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
