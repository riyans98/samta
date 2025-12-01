# app/db/session.py
import mysql.connector
from mysql.connector import Error
from fastapi import HTTPException, status
from typing import Dict, Any

# CONFIGS ko .env se load karna
from app.core.config import settings
# app/db/session.py (Extended)
# ... (Previous imports)

# CONFIGS ko .env se load karna
from app.core.config import settings
from app.schemas.dbt_schemas import AtrocityBase

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

def get_all_fir_data() -> list[AtrocityBase]:
    connection = get_dbt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ATROCITY")
        data = cursor.fetchall()
        result: list[AtrocityBase] = [AtrocityBase(**row) for row in data]
        return result
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()

def get_fir_data_by_case_no(case_no: int):
    connection = get_dbt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM ATROCITY WHERE Case_No = %s"
        cursor.execute(query, (case_no,))
        result = cursor.fetchone()
        return result
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()

def get_fir_data_by_fir_no(fir_no: str):
    connection = get_dbt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM ATROCITY WHERE FIR_NO = %s"
        cursor.execute(query, (fir_no,))
        result = cursor.fetchone()
        return result
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()