# app/db/session.py
import mysql.connector
from mysql.connector import Error
from fastapi import HTTPException, status
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from app.core.config import settings
from app.schemas.dbt_schemas import AtrocityDBModel, CaseEvent 
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
ALERT_TABLE_NAME = "pending_alerts"
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

# ======================================================================
# ALERT MANAGEMENT FUNCTIONS (FIXED)
# ======================================================================

def insert_new_pending_alert(case_no: int, junior_role: str, senior_role: str, pending_duration: int) -> Optional[int]:
    """Inserts a new alert record if no active alert exists for this case."""
    connection = None
    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor()

        check_query = f"SELECT alert_id FROM {ALERT_TABLE_NAME} WHERE case_no = %s AND is_active = TRUE"
        cursor.execute(check_query, (case_no,))
        if cursor.fetchone(): return None 

        insert_query = f"""
            INSERT INTO {ALERT_TABLE_NAME} 
            (case_no, junior_role, senior_role, alerted_at, pending_duration) 
            VALUES (%s, %s, %s, NOW(), %s)
        """
        values = (case_no, junior_role, senior_role, pending_duration)
        cursor.execute(insert_query, values)
        connection.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"DB Error inserting alert: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            connection.close()


def get_active_alerts_for_senior_dashboard(senior_role: str, user_id: str) -> List[Dict]:
    """Fetches active alerts (is_active=TRUE) for the senior's role, including case details for jurisdiction check."""
    connection = None
    results = []
    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = f"""
            SELECT A.*, T.FIR_NO, T.Victim_Name, T.Pending_At, T.District, T.State_UT
            FROM {ALERT_TABLE_NAME} A
            JOIN ATROCITY T ON A.case_no = T.Case_No
            WHERE A.senior_role = %s AND A.is_active = TRUE
            ORDER BY A.alerted_at DESC
        """
        cursor.execute(query, (senior_role,))
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"DB Error fetching senior alerts: {e}")
        return []
    finally:
        if connection and connection.is_connected():
            connection.close()


def get_alerts_for_junior_feedback(junior_role: str) -> List[Dict]:
    """Fetches alerts that are NOT active but have senior_input (for junior feedback)."""
    connection = None
    results = []
    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = f"""
            SELECT A.*, T.FIR_NO, T.Victim_Name, T.Pending_At
            FROM {ALERT_TABLE_NAME} A
            JOIN ATROCITY T ON A.case_no = T.Case_No
            WHERE A.junior_role = %s AND A.is_active = FALSE AND A.senior_input IS NOT NULL
            ORDER BY A.alerted_at DESC
        """
        cursor.execute(query, (junior_role,))
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"DB Error fetching junior feedback: {e}")
        return []
    finally:
        if connection and connection.is_connected():
            connection.close()


# app/db/session.py (Update senior_resolve_alert function)

def senior_resolve_alert(alert_id: int, senior_input: str) -> bool:
    """Senior officer inputs comment, closing the ticket."""
    connection = None
    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor()
        
        # 🔥 DEBUG LOG: Check values receiving in function
        print(f"DEBUG DB: Resolving Alert ID: {alert_id} (Type: {type(alert_id)}) with Input: {senior_input}")

        # Query update kar rahe hain
        update_query = f"""
            UPDATE {ALERT_TABLE_NAME} 
            SET is_active = FALSE, senior_input = %s, ticket_close_date = NOW()
            WHERE alert_id = %s
        """
        
        # NOTE: Maine 'AND is_active = TRUE' hata diya hai testing ke liye.
        # Agar row exist karti hai toh update honi chahiye, chahe status kuch bhi ho.

        # Ensure alert_id is an integer
        cursor.execute(update_query, (senior_input, int(alert_id)))
        connection.commit()
        
        rows_affected = cursor.rowcount
        print(f"DEBUG DB: Rows Updated: {rows_affected}")

        return rows_affected > 0

    except Exception as e:
        print(f"DB Error resolving alert: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            
def junior_respond_to_alert(alert_id: int, junior_reason: str) -> bool:
    """Junior officer adds their reason/reply to the closed ticket."""
    connection = None
    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor()
        
        update_query = f"""
            UPDATE {ALERT_TABLE_NAME} 
            SET junior_reason = %s
            WHERE alert_id = %s
        """
        cursor.execute(update_query, (junior_reason, alert_id))
        connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"DB Error junior responding: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            connection.close()


# def get_alert_details_by_id(alert_id: int) -> Optional[Dict]:
#     """Fetches the full alert record along with critical case details by joining pending_alerts and ATROCITY tables."""
#     connection = None
#     try:
#         connection = get_dbt_db_connection()
#         cursor = connection.cursor(dictionary=True)
        
#         query = f"""
#             SELECT 
#                 A.*, 
#                 T.FIR_NO, T.Victim_Name, T.Pending_At AS Case_Pending_At, T.District, T.State_UT
#             FROM {ALERT_TABLE_NAME} A
#             JOIN ATROCITY T ON A.case_no = T.Case_No
#             WHERE A.alert_id = %s
#         """
#         cursor.execute(query, (alert_id,))
#         results = cursor.fetchone()
        
#         if results and 'pending_duration' in results:
#             results['pending_duration'] = int(results['pending_duration'])
            
#         return results
        
#     except Exception as e:
#         print(f"DB Error fetching alert detail {alert_id}: {e}")
#         return None
#     finally:
#         if connection and connection.is_connected():
#             connection.close()


def deactivate_pending_alert(case_no: int) -> bool:
    """Deactivates all active alerts for a case when action is taken."""
    connection = None
    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor()
        
        update_query = f"UPDATE {ALERT_TABLE_NAME} SET is_active = FALSE WHERE case_no = %s AND is_active = TRUE"
        cursor.execute(update_query, (case_no,))
        connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"DB Error deactivating alert: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            connection.close()

# ======================================================================
# Alert Related Functions for Dashboard 
# ======================================================================

# app/db/session.py (Final Implementation of get_alert_details_by_id)

# ... (Previous functions) ...

def get_alert_details_by_id(alert_id: int) -> Optional[Dict]:
    """
    Fetches the full alert record along with critical case details 
    by joining pending_alerts (A) and ATROCITY (T) tables.
    """
    connection = None
    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # NOTE: A.is_active is used to determine the ticket status in the frontend
        query = f"""
            SELECT 
                A.alert_id, A.case_no, A.junior_role, A.senior_role, A.pending_duration, A.senior_input, 
                A.junior_reason, A.is_active, A.ticket_close_date,
                T.FIR_NO, T.Victim_Name, T.Pending_At AS Case_Pending_At, T.District, T.State_UT, T.Stage
            FROM {ALERT_TABLE_NAME} A
            JOIN ATROCITY T ON A.case_no = T.Case_No
            WHERE A.alert_id = %s
        """
        cursor.execute(query, (alert_id,))
        results = cursor.fetchone()
        
        if results and 'pending_duration' in results:
            # Convert pending_duration to integer for consistency
            results['pending_duration'] = int(results['pending_duration'])
        
        return results
        
    except Exception as e:
        print(f"DB Error fetching alert detail {alert_id}: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            connection.close()

# ... (Rest of the session.py file) ...
# app/db/session.py (Corrected get_active_alerts_for_senior_dashboard)

def get_active_alerts_for_senior_dashboard(senior_role: str, user_id: str) -> List[Dict]:
    """
    Fetches active alerts (is_active=TRUE) for the senior's role, including case details 
    required for jurisdiction check in the router.
    """
    connection = None
    results = []
    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # 🔥 CRITICAL FIX: T.State_UT aur T.District ko query mein shamil karna
        query = f"""
            SELECT 
                A.*, 
                T.FIR_NO, T.Victim_Name, T.Pending_At, T.District, T.State_UT 
            FROM {ALERT_TABLE_NAME} A
            JOIN ATROCITY T ON A.case_no = T.Case_No
            WHERE A.senior_role = %s AND A.is_active = TRUE
            ORDER BY A.alerted_at DESC
        """
        # We pass senior_role to filter alerts meant for this role
        cursor.execute(query, (senior_role,))
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"DB Error fetching senior alerts: {e}")
        return []
    finally:
        if connection and connection.is_connected():
            connection.close()


# app/db/session.py (Final Fix for Role Matching)

# app/db/session.py (Final Fix for Role Matching - Should be applied)

def get_active_alerts_for_senior_dashboard(senior_role: str, user_id: str) -> List[Dict]:
    connection = None
    results = []
    
    # 🔥 FIX: Normalize the input role for query comparison
    normalized_role = senior_role.strip().lower()

    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = f"""
            SELECT 
                A.*, 
                T.FIR_NO, T.Victim_Name, T.Pending_At, T.District, T.State_UT 
            FROM {ALERT_TABLE_NAME} A
            JOIN ATROCITY T ON A.case_no = T.Case_No
            -- CRITICAL: Compare normalized input role with normalized DB role
            WHERE LOWER(A.senior_role) = %s AND A.is_active = TRUE
            ORDER BY A.alerted_at DESC
        """
        cursor.execute(query, (normalized_role,))
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"DB Error fetching senior alerts: {e}")
        return []
    finally:
        if connection and connection.is_connected():
            connection.close()


#####show alert data on senior's page 1st time.
# app/db/session.py (Core function for AlertView.tsx)

def get_alert_details_by_id(alert_id: int) -> Optional[Dict]:
    """
    Fetches the full alert record along with critical case details 
    by joining pending_alerts (A) and ATROCITY (T) tables.
    """
    connection = None
    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Select all communication and status fields from A (pending_alerts)
        # And necessary case fields from T (ATROCITY)
        query = f"""
            SELECT 
                A.*, 
                T.FIR_NO, T.Victim_Name, T.Pending_At AS Case_Pending_At, 
                T.District, T.State_UT, T.Stage, T.Case_Description
            FROM {ALERT_TABLE_NAME} A
            JOIN ATROCITY T ON A.case_no = T.Case_No
            WHERE A.alert_id = %s
        """
        cursor.execute(query, (alert_id,))
        results = cursor.fetchone()
        
        if results and 'pending_duration' in results:
            results['pending_duration'] = int(results['pending_duration'])
        print(f"Pending Duration: {results['pending_duration']}")  # Debugging line
            
        return results
        
    except Exception as e:
        print(f"DB Error fetching alert detail {alert_id}: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            connection.close()

# app/db/session.py (Part 1: Dashboard Summary Fetch)

# ... (Previous imports and utility functions) ...

def get_active_alerts_for_senior_dashboard(senior_role: str, user_id: str) -> List[Dict]:
    """
    Fetches active alerts (is_active=TRUE) for the senior's role, ensuring case details 
    (District, State_UT) are included for the router's jurisdiction check.
    """
    connection = None
    results = []
    
    # 1. Normalize the input role for case-insensitive comparison
    normalized_role = senior_role.strip().lower()

    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = f"""
            SELECT 
                A.*, 
                T.FIR_NO, T.Victim_Name, T.Pending_At, T.District, T.State_UT 
            FROM {ALERT_TABLE_NAME} A
            JOIN ATROCITY T ON A.case_no = T.Case_No
            -- CRITICAL: Compare normalized input role with normalized DB role
            WHERE LOWER(A.senior_role) = %s AND A.is_active = TRUE
            ORDER BY A.alerted_at DESC
        """
        # 2. Execute query with normalized role
        cursor.execute(query, (normalized_role,))
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"DB Error fetching senior alerts: {e}")
        return []
    finally:
        if connection and connection.is_connected():
            connection.close()


# app/db/session.py (Part 2: Alert Detail Page Fetch)

# ... (Previous functions) ...

def get_alert_details_by_id(alert_id: int) -> Optional[Dict]:
    """
    Fetches the full alert record along with critical case details 
    by joining pending_alerts (A) and ATROCITY (T) tables for the detail page.
    """
    connection = None
    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Select all communication/status fields from A and case fields from T
        query = f"""
            SELECT 
                A.alert_id, A.case_no, A.junior_role, A.senior_role, A.pending_duration, A.senior_input, 
                A.junior_reason, A.is_active, A.ticket_close_date,
                T.FIR_NO, T.Victim_Name, T.Pending_At AS Case_Pending_At, 
                T.District, T.State_UT, T.Stage, T.Case_Description
            FROM {ALERT_TABLE_NAME} A
            JOIN ATROCITY T ON A.case_no = T.Case_No
            WHERE A.alert_id = %s
        """
        cursor.execute(query, (alert_id,))
        results = cursor.fetchone()
        
        if results and 'pending_duration' in results:
            # Ensure pending_duration is an integer for frontend compatibility
            results['pending_duration'] = int(results['pending_duration'])
            
        return results
        
    except Exception as e:
        print(f"DB Error fetching alert detail {alert_id}: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            connection.close()
# ... (Other functions) ...
