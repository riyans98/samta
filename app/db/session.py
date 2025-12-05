# app/db/session.py
import mysql.connector
from mysql.connector import Error
from fastapi import HTTPException, status
from typing import Dict, Any, List, Optional
# CONFIGS ko .env se load karna
from app.core.config import settings
# app/db/session.py (Extended)
# ... (Previous imports)

# CONFIGS ko .env se load karna
from app.core.config import settings
from app.schemas.dbt_schemas import AtrocityDBModel, CaseEvent

# Login DB config (for reference)
LOGIN_DB_CONFIG = {
    'host': settings.DB_HOST,
    # ... (other login db details)
}

# DBT DB config (new)
DBT_DB_CONFIG = {
    'host': settings.DBT_DB_HOST,
    'port': settings.DBT_DB_PORT,
    'user': settings.DBT_DB_USER,
    'password': settings.DBT_DB_PASSWORD,
    'database': settings.DBT_DB_DATABASE
}

def get_dbt_db_connection():
    """Establishes and returns a database connection for 'defaultdb'."""
    try:
        connection = mysql.connector.connect(**DBT_DB_CONFIG)
        return connection
    except Error as e:
        print(f"DBT Database Connection Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"DBT Database connection failed: {e}"
        )
# ... (previous execute_insert and get_db_connection functions remain for login db)

# DB_CONFIG ko centralized kar diya gaya hai
DB_CONFIG = {
    'host': settings.DB_HOST,
    'port': settings.DB_PORT,
    'user': settings.DB_USER,
    'password': settings.DB_PASSWORD,
    'database': settings.DB_DATABASE
}

def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Database Connection Error: {e}")
        # Connection failure is a critical 500 error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Database connection failed: {e}"
        )

# Execute functions ko yahan move kar rahe hain taaki DB logic separate rahe

def execute_insert(table_name: str, data: Dict[str, Any], hashed_password: str):
    """
    Handles data insertion. Expects the password to be already hashed.
    """
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Replace plain text password with the hashed version
        data['password'] = hashed_password
        clean_data = {k: v for k, v in data.items() if v is not None}
        
        columns = ", ".join(clean_data.keys())
        placeholders = ", ".join(["%s"] * len(clean_data))
        values = tuple(clean_data.values())
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        cursor.execute(query, values)
        connection.commit()
        return {"message": f"Data inserted successfully into {table_name}"}
    except Error as e:
        print(f"Database Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Database insertion failed: {e}"
        )
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# execute_login_query ko auth_service.py/security.py mein move karna behtar hai 
# kyunki usme bcrypt aur password logic hai, jo ki DB se zyada security/business logic hai.


def execute_update_users(id: int, hash: str): 
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        table_name = 'citizen_users'

        query = f"UPDATE {table_name} SET password_hash = '{hash}' WHERE citizen_id = {id}"
        cursor.execute(query)
        connection.commit()

        return {"message": f"Data updated successfully into {table_name}"}
    except Error as e:
        print(f"Database Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Database insertion failed: {e}"
        )
    finally:
        if connection and connection.is_connected() and cursor:
            cursor.close()
            connection.close()


def get_citizen_by_login_id(login_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetches citizen user data by login_id from citizen_users table.
    Returns all user data including password_hash for verification.
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM citizen_users WHERE login_id = %s"
        cursor.execute(query, (login_id,))
        result = cursor.fetchone()
        
        if result:
            # Normalize keys to lowercase for consistency
            return {k.lower(): v for k, v in result.items()}
        return None
    except Error as e:
        print(f"Database Error fetching citizen: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failed: {e}"
        )
    finally:
        if connection and connection.is_connected() and cursor:
            cursor.close()
            connection.close()


def get_all_fir_data() -> list[AtrocityDBModel]:
    connection = get_dbt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ATROCITY")
        data = cursor.fetchall()
        return [AtrocityDBModel(**row) for row in data]
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()

def get_fir_data_by_case_no(case_no: int) -> AtrocityDBModel:
    connection = get_dbt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM ATROCITY WHERE Case_No = %s"
        cursor.execute(query, (case_no,))
        row = cursor.fetchone()
        if not row:
            return None
        return AtrocityDBModel(**row)
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()

def get_fir_data_by_fir_no(fir_no: str) -> AtrocityDBModel:
    connection = get_dbt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM ATROCITY WHERE FIR_NO = %s"
        cursor.execute(query, (fir_no,))
        row = cursor.fetchone()
        if not row:
            return None
        return AtrocityDBModel(**row)
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


def get_atrocity_cases_by_aadhaar(aadhaar_number: int) -> list[AtrocityDBModel]:
    """
    Fetch all atrocity cases for a given Aadhaar number.
    Returns list of cases with all details (same as /get-fir-form-data).
    """
    connection = get_dbt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM ATROCITY WHERE Aadhar_No = %s"
        cursor.execute(query, (aadhaar_number,))
        data = cursor.fetchall()
        if data:
            return [AtrocityDBModel(**row) for row in data]
        return []
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()

def get_timeline(case_no: int) -> List[CaseEvent]:
    conn = get_dbt_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM CASE_EVENTS WHERE case_no = %s ORDER BY created_at ASC",
            (case_no,)
        )
        rows = cursor.fetchall()
        return [CaseEvent(**row) for row in rows]
    finally:
        cursor.close()
        conn.close()


def insert_case_event(
    case_no: int,
    performed_by: str,
    performed_by_role: str,
    event_type: str,
    event_data: Dict[str, Any] | None = None
) -> int:
    """
    Inserts a new event into the CASE_EVENTS table.
    Returns the event_id of the inserted row.
    """
    import json
    conn = get_dbt_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO CASE_EVENTS (case_no, performed_by, performed_by_role, event_type, event_data)
            VALUES (%s, %s, %s, %s, %s)
        """
        event_data_json = json.dumps(event_data) if event_data else None
        cursor.execute(query, (case_no, performed_by, performed_by_role, event_type, event_data_json))
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to insert case event: {e}"
        )
    finally:
        cursor.close()
        conn.close()


def update_atrocity_case(case_no: int, updates: Dict[str, Any]) -> bool:
    """
    Updates specified fields in the ATROCITY table for a given case.
    Only updates Stage, Pending_At, Approved_By, Fund_Ammount fields (workflow-related).
    Returns True if update was successful.
    """
    if not updates:
        return False
    
    # Only allow workflow-related field updates
    allowed_fields = {'Stage', 'Pending_At', 'Approved_By', 'Fund_Ammount'}
    filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
    
    if not filtered_updates:
        return False
    
    conn = get_dbt_db_connection()
    try:
        cursor = conn.cursor()
        set_clause = ", ".join([f"{k} = %s" for k in filtered_updates.keys()])
        values = list(filtered_updates.values()) + [case_no]
        query = f"UPDATE ATROCITY SET {set_clause} WHERE Case_No = %s"
        cursor.execute(query, values)
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update atrocity case: {e}"
        )
    finally:
        cursor.close()
        conn.close()
