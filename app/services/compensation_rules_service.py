"""
Compensation Rules Service

Handles CRUD operations for compensation rules.
Provides compensation calculation based on atrocity sections and case types.
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status

from app.db.session import get_dbt_db_connection
from app.schemas.dbt_schemas import CompensationRule

logger = logging.getLogger(__name__)


# ======================== HELPER FUNCTIONS ========================

def _row_to_compensation_rule(row: tuple) -> CompensationRule:
    """
    Convert database row tuple to CompensationRule object.
    
    Args:
        row: Database row tuple (id, case_id, section_code, action_name, amount)
    
    Returns:
        CompensationRule object
    """
    return CompensationRule(
        id=row[0],
        case_id=row[1],
        section_code=row[2],
        action_name=row[3],
        amount=row[4]
    )


# ======================== RETRIEVAL FUNCTIONS ========================

def get_compensation_rule_by_id(rule_id: int) -> Optional[CompensationRule]:
    """
    Retrieve a specific compensation rule by ID.
    
    Args:
        rule_id: The ID of the compensation rule
    
    Returns:
        CompensationRule object or None if not found
    
    Raises:
        HTTPException: On database error
    """
    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor()
        
        query = """
            SELECT id, case_id, section_code, action_name, amount
            FROM compensation_rules
            WHERE id = %s
        """
        
        cursor.execute(query, (rule_id,))
        row = cursor.fetchone()
        cursor.close()
        connection.close()
        
        return _row_to_compensation_rule(row) if row else None
        
    except Exception as e:
        logger.error(f"Error retrieving compensation rule {rule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve compensation rule {rule_id}"
        )


def get_all_compensation_rules_by_case_id(case_id: int) -> List[CompensationRule]:
    """
    Retrieve all compensation rules for a specific case.
    
    Args:
        case_id: The case ID to fetch rules for
    
    Returns:
        List of CompensationRule objects for the case
    
    Raises:
        HTTPException: On database error
    """
    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor()
        
        query = """
            SELECT id, case_id, section_code, action_name, amount
            FROM compensation_rules
            WHERE case_id = %s
            ORDER BY id ASC
        """
        
        cursor.execute(query, (case_id,))
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        
        rules = [_row_to_compensation_rule(row) for row in rows] if rows else []
        
        logger.info(f"Retrieved {len(rules)} compensation rules for case {case_id}")
        return rules
        
    except Exception as e:
        logger.error(f"Error retrieving compensation rules for case {case_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve compensation rules for case {case_id}"
        )


def get_all_compensation_rules() -> List[CompensationRule]:
    """
    Retrieve all compensation rules from the database.
    
    Returns:
        List of CompensationRule objects
    
    Raises:
        HTTPException: On database error
    """
    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor()
        
        query = """
            SELECT id, case_id, section_code, action_name, amount
            FROM compensation_rules
            ORDER BY case_id ASC, id ASC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        
        rules = [_row_to_compensation_rule(row) for row in rows] if rows else []
        
        logger.info(f"Retrieved {len(rules)} total compensation rules")
        return rules
        
    except Exception as e:
        logger.error(f"Error retrieving all compensation rules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve compensation rules"
        )


# ======================== CREATE FUNCTIONS ========================

def create_compensation_rule(
    case_id: int,
    section_code: str,
    action_name: str,
    amount: float
) -> CompensationRule:
    """
    Create a new compensation rule record.
    
    Args:
        case_id: ID of the case
        section_code: Atrocity section code (e.g., "IPC 302")
        action_name: Name of the action/compensation type
        amount: Compensation amount
    
    Returns:
        Created CompensationRule object
    
    Raises:
        HTTPException: On database error or validation failure
    """
    try:
        # Validation
        if case_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Case ID must be positive"
            )
        
        if not section_code or not section_code.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Section code is required"
            )
        
        if not action_name or not action_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Action name is required"
            )
        
        if amount < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Compensation amount cannot be negative"
            )
        
        connection = get_dbt_db_connection()
        cursor = connection.cursor()
        
        insert_query = """
            INSERT INTO compensation_rules (case_id, section_code, action_name, amount)
            VALUES (%s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (case_id, section_code, action_name, amount))
        connection.commit()
        
        new_id = cursor.lastrowid
        cursor.close()
        connection.close()
        
        logger.info(f"Created compensation rule: id={new_id}, case_id={case_id}, section_code={section_code}")
        
        return CompensationRule(
            id=new_id,
            case_id=case_id,
            section_code=section_code,
            action_name=action_name,
            amount=amount
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating compensation rule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create compensation rule"
        )


def create_compensation_rules_batch(
    case_id: int,
    rules: List[Dict[str, Any]]
) -> List[CompensationRule]:
    """
    Create multiple compensation rules for a case.
    
    Args:
        case_id: ID of the case
        rules: List of dicts with keys: section_code, action_name, amount
    
    Returns:
        List of created CompensationRule objects
    
    Raises:
        HTTPException: On database error or validation failure
    """
    try:
        if not rules:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rules list cannot be empty"
            )
        
        if case_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Case ID must be positive"
            )
        
        # Validate all rules before inserting
        for rule in rules:
            if not rule.get("section_code") or not str(rule.get("section_code")).strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="All rules must have section_code"
                )
            
            if not rule.get("action_name") or not str(rule.get("action_name")).strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="All rules must have action_name"
                )
            
            amount = rule.get("amount", 0)
            if amount < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Compensation amount cannot be negative"
                )
        
        connection = get_dbt_db_connection()
        cursor = connection.cursor()
        
        insert_query = """
            INSERT INTO compensation_rules (case_id, section_code, action_name, amount)
            VALUES (%s, %s, %s, %s)
        """
        
        created_rules = []
        
        for rule in rules:
            cursor.execute(
                insert_query,
                (case_id, rule["section_code"], rule["action_name"], rule["amount"])
            )
            connection.commit()
            
            new_id = cursor.lastrowid
            
            created_rules.append(CompensationRule(
                id=new_id,
                case_id=case_id,
                section_code=rule["section_code"],
                action_name=rule["action_name"],
                amount=rule["amount"]
            ))
        
        cursor.close()
        connection.close()
        
        logger.info(f"Created {len(created_rules)} compensation rules for case {case_id}")
        return created_rules
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating batch compensation rules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create compensation rules"
        )


# ======================== UPDATE FUNCTIONS ========================

def update_compensation_rule(
    rule_id: int,
    section_code: Optional[str] = None,
    action_name: Optional[str] = None,
    amount: Optional[float] = None
) -> CompensationRule:
    """
    Update an existing compensation rule (partial update supported).
    
    Args:
        rule_id: The ID of the rule to update
        section_code: Optional new section code
        action_name: Optional new action name
        amount: Optional new amount
    
    Returns:
        Updated CompensationRule object
    
    Raises:
        HTTPException: On database error, validation failure, or not found
    """
    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor()
        
        # Check if rule exists
        cursor.execute("SELECT * FROM compensation_rules WHERE id = %s", (rule_id,))
        row = cursor.fetchone()
        
        if not row:
            cursor.close()
            connection.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Compensation rule with ID {rule_id} not found"
            )
        
        # Validate new values if provided
        if section_code is not None and not section_code.strip():
            cursor.close()
            connection.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Section code cannot be empty"
            )
        
        if action_name is not None and not action_name.strip():
            cursor.close()
            connection.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Action name cannot be empty"
            )
        
        if amount is not None and amount < 0:
            cursor.close()
            connection.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Compensation amount cannot be negative"
            )
        
        # Build dynamic update query
        update_fields = []
        update_values = []
        
        if section_code is not None:
            update_fields.append("section_code = %s")
            update_values.append(section_code)
        
        if action_name is not None:
            update_fields.append("action_name = %s")
            update_values.append(action_name)
        
        if amount is not None:
            update_fields.append("amount = %s")
            update_values.append(amount)
        
        # If no fields to update, return existing record
        if not update_fields:
            cursor.execute("SELECT * FROM compensation_rules WHERE id = %s", (rule_id,))
            existing_row = cursor.fetchone()
            cursor.close()
            connection.close()
            return _row_to_compensation_rule(existing_row)
        
        # Execute update
        update_values.append(rule_id)
        update_query = f"UPDATE compensation_rules SET {', '.join(update_fields)} WHERE id = %s"
        
        cursor.execute(update_query, update_values)
        connection.commit()
        
        # Fetch and return updated record
        cursor.execute("SELECT * FROM compensation_rules WHERE id = %s", (rule_id,))
        updated_row = cursor.fetchone()
        cursor.close()
        connection.close()
        
        logger.info(f"Updated compensation rule: id={rule_id}")
        return _row_to_compensation_rule(updated_row)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating compensation rule {rule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update compensation rule"
        )


# ======================== DELETE FUNCTIONS ========================

def delete_compensation_rule(rule_id: int) -> dict:
    """
    Delete a compensation rule record.
    
    Args:
        rule_id: The ID of the rule to delete
    
    Returns:
        Success message with deleted rule ID
    
    Raises:
        HTTPException: On database error or not found
    """
    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor()
        
        # Check if rule exists
        cursor.execute("SELECT * FROM compensation_rules WHERE id = %s", (rule_id,))
        row = cursor.fetchone()
        
        if not row:
            cursor.close()
            connection.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Compensation rule with ID {rule_id} not found"
            )
        
        # Delete the record
        delete_query = "DELETE FROM compensation_rules WHERE id = %s"
        cursor.execute(delete_query, (rule_id,))
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info(f"Deleted compensation rule: id={rule_id}")
        
        return {
            "message": f"Compensation rule {rule_id} deleted successfully",
            "deleted_id": rule_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting compensation rule {rule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete compensation rule"
        )


def delete_all_compensation_rules_by_case_id(case_id: int) -> dict:
    """
    Delete all compensation rules for a specific case.
    
    Args:
        case_id: The case ID
    
    Returns:
        Success message with count of deleted rules
    
    Raises:
        HTTPException: On database error
    """
    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor()
        
        # Get count of rules to delete
        cursor.execute("SELECT COUNT(*) FROM compensation_rules WHERE case_id = %s", (case_id,))
        count_row = cursor.fetchone()
        count = count_row[0] if count_row else 0
        
        # Delete all rules for the case
        delete_query = "DELETE FROM compensation_rules WHERE case_id = %s"
        cursor.execute(delete_query, (case_id,))
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info(f"Deleted {count} compensation rules for case {case_id}")
        
        return {
            "message": f"Deleted {count} compensation rules for case {case_id}",
            "case_id": case_id,
            "deleted_count": count
        }
        
    except Exception as e:
        logger.error(f"Error deleting compensation rules for case {case_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete compensation rules"
        )


# ======================== UTILITY FUNCTIONS ========================

def get_total_compensation_by_case_id(case_id: int) -> Dict[str, Any]:
    """
    Calculate total compensation amount for a case.
    
    Args:
        case_id: The case ID
    
    Returns:
        Dictionary with case_id, total_amount, and rule_count
    
    Raises:
        HTTPException: On database error
    """
    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor()
        
        query = """
            SELECT COALESCE(SUM(amount), 0), COUNT(*)
            FROM compensation_rules
            WHERE case_id = %s
        """
        
        cursor.execute(query, (case_id,))
        row = cursor.fetchone()
        cursor.close()
        connection.close()
        
        total_amount = float(row[0]) if row else 0.0
        rule_count = int(row[1]) if row else 0
        
        logger.info(f"Total compensation for case {case_id}: {total_amount} ({rule_count} rules)")
        
        return {
            "case_id": case_id,
            "total_amount": total_amount,
            "rule_count": rule_count
        }
        
    except Exception as e:
        logger.error(f"Error calculating total compensation for case {case_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate total compensation"
        )
