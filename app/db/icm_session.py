# app/db/icm_session.py
"""
ICM Database Session Module

Handles all database operations for ICM (Inter-Caste Marriage) applications.
Uses ICM_DB for persistent data storage.
"""

from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
import mysql.connector
from mysql.connector import Error
import json

from app.core.config import settings
from app.db.session import get_dbt_db_connection
from app.schemas.icm_schemas import ICMApplication, ICMEvent

# ======================== ICM APPLICATION FUNCTIONS ========================

def get_icm_application_by_id(icm_id: int) -> Optional[ICMApplication]:
    """
    Fetch an ICM application by ID.
    
    Args:
        icm_id: Application ID
    
    Returns:
        ICMApplication or None if not found
    """
    connection = get_dbt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM icm_applications WHERE icm_id = %s"
        cursor.execute(query, (icm_id,))
        result = cursor.fetchone()
        
        if result:
            return ICMApplication(**result)
        return None
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ICM application fetch failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


def get_icm_applications_by_citizen(citizen_id: int) -> List[ICMApplication]:
    """
    Fetch all ICM applications for a citizen.
    
    Args:
        citizen_id: Citizen ID
    
    Returns:
        List of ICMApplication records
    """
    connection = get_dbt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM icm_applications WHERE citizen_id = %s"
        cursor.execute(query, (citizen_id,))
        results = cursor.fetchall()
        
        if results:
            return [ICMApplication(**row) for row in results]
        return []
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ICM applications fetch failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


def get_all_icm_applications(limit: int = 100, offset: int = 0) -> List[ICMApplication]:
    """
    Fetch all ICM applications with pagination.
    
    Args:
        limit: Maximum records to return
        offset: Number of records to skip
    
    Returns:
        List of ICMApplication records
    """
    connection = get_dbt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM icm_applications LIMIT %s OFFSET %s"
        cursor.execute(query, (limit, offset))
        results = cursor.fetchall()
        
        if results:
            return [ICMApplication(**row) for row in results]
        return []
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ICM applications fetch failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


def insert_icm_application(data: Dict[str, Any]) -> int:
    """
    Insert a new ICM application.
    
    Args:
        data: Application data dictionary
    
    Returns:
        The icm_id of the inserted record
    
    Raises:
        HTTPException: If insertion fails
    """
    connection = get_dbt_db_connection()
    try:
        cursor = connection.cursor()
        
        # Remove None values for cleaner SQL
        clean_data = {k: v for k, v in data.items() if v is not None}
        
        columns = ", ".join(clean_data.keys())
        placeholders = ", ".join(["%s"] * len(clean_data))
        values = tuple(clean_data.values())
        
        query = f"INSERT INTO icm_applications ({columns}) VALUES ({placeholders})"
        
        cursor.execute(query, values)
        connection.commit()
        
        return cursor.lastrowid
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ICM application insertion failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


def update_icm_application(icm_id: int, updates: Dict[str, Any]) -> bool:
    """
    Update an ICM application.
    
    Args:
        icm_id: Application ID
        updates: Dictionary of fields to update
    
    Returns:
        True if update successful, False otherwise
    
    Raises:
        HTTPException: If update fails
    """
    if not updates:
        return False
    
    connection = get_dbt_db_connection()
    try:
        cursor = connection.cursor()
        
        set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
        values = list(updates.values()) + [icm_id]
        
        query = f"UPDATE icm_applications SET {set_clause}, updated_at = NOW() WHERE icm_id = %s"
        
        cursor.execute(query, values)
        connection.commit()
        
        return cursor.rowcount > 0
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ICM application update failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


# ======================== ICM EVENT FUNCTIONS ========================

def get_icm_events_by_application(icm_id: int) -> List[ICMEvent]:
    """
    Fetch all events for an ICM application.
    
    Args:
        icm_id: Application ID
    
    Returns:
        List of ICMEvent records
    """
    connection = get_dbt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM icm_events WHERE icm_id = %s ORDER BY created_at DESC"
        cursor.execute(query, (icm_id,))
        results = cursor.fetchall()
        
        if results:
            return [ICMEvent(**row) for row in results]
        return []
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ICM events fetch failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


def insert_icm_event(
    icm_id: int,
    event_type: str,
    event_role: str,
    event_stage: int,
    comment: Optional[str] = None,
    event_data: Optional[Dict[str, Any]] = None
) -> int:
    """
    Insert a new ICM event.
    
    Args:
        icm_id: Application ID
        event_type: Type of event
        event_role: Role that triggered the event
        event_stage: Current application stage
        comment: Optional comment
        event_data: Optional JSON event data
    
    Returns:
        The event_id of the inserted record
    
    Raises:
        HTTPException: If insertion fails
    """
    connection = get_dbt_db_connection()
    try:
        cursor = connection.cursor()
        
        # Convert event_data to JSON string if provided
        event_data_json = json.dumps(event_data) if event_data else None
        
        query = """
            INSERT INTO icm_events 
            (icm_id, event_type, event_role, event_stage, comment, event_data)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (icm_id, event_type, event_role, event_stage, comment, event_data_json))
        connection.commit()
        
        return cursor.lastrowid
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ICM event insertion failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


# ======================== ICM QUERY FUNCTIONS ========================

def get_icm_applications_by_status(status: str, limit: int = 100, offset: int = 0) -> List[ICMApplication]:
    """
    Fetch ICM applications by status.
    
    Args:
        status: Application status (Pending, Approved, Rejected, etc.)
        limit: Maximum records to return
        offset: Number of records to skip
    
    Returns:
        List of ICMApplication records
    """
    connection = get_dbt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM icm_applications WHERE application_status = %s LIMIT %s OFFSET %s"
        cursor.execute(query, (status, limit, offset))
        results = cursor.fetchall()
        
        if results:
            return [ICMApplication(**row) for row in results]
        return []
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ICM applications query failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()


def get_icm_applications_by_stage(stage: int, limit: int = 100, offset: int = 0) -> List[ICMApplication]:
    """
    Fetch ICM applications by current stage.
    
    Args:
        stage: Current stage
        limit: Maximum records to return
        offset: Number of records to skip
    
    Returns:
        List of ICMApplication records
    """
    connection = get_dbt_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM icm_applications WHERE current_stage = %s LIMIT %s OFFSET %s"
        cursor.execute(query, (stage, limit, offset))
        results = cursor.fetchall()
        
        if results:
            return [ICMApplication(**row) for row in results]
        return []
    except Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ICM applications query failed: {e}"
        )
    finally:
        cursor.close()
        connection.close()
