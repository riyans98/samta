from http.client import HTTPException
from typing import Literal, Optional
from app.db.session import get_dbt_db_connection
from app.schemas.govt_record_schemas import TreasuryRecord, TreasuryTransaction

table_name = 'treasury'
def get_last_treasury_data_for_state_and_district(state: str, district: str) -> TreasuryRecord | None:
    connection = None
    cursor = None
    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor()
        
        # Replace plain text password with the hashed version
        query = f"SELECT * FROM {table_name} WHERE LOWER(state) = '{state.lower()}' AND LOWER(district) = '{district.lower()}' ORDER BY transaction_time DESC LIMIT 1"
        
        cursor.execute(query)
        record = cursor.fetchone()
        if not record:
            return None

        return TreasuryRecord(**record)
    except Exception as e:
        raise HTTPException("last value not found: {e}")
    finally:
        if connection and connection.is_connected() and cursor:
            cursor.close()
            connection.close()

def get_last_treasury_data_if_amount_is_sufficient(amount: float, state: str, district: str) -> TreasuryRecord | None:
    last_record = get_last_treasury_data_for_state_and_district(state, district)

    if (not last_record):
        return None

    if (last_record.balance_after >= amount):
        return last_record

    return None

def insert_transaction(state: str, district: str, amount: float, transaction_type: Literal['CREDIT','DEBIT'],  balance_after: float, remark: Optional[str]):
    connection = None
    cursor = None
    try:
        connection = get_dbt_db_connection()
        cursor = connection.cursor()
        
        # Replace plain text password with the hashed version
        query = f"INSERT INTO {table_name} (state, district, amount, transaction_type, balance_after, remark) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (state, district, amount, transaction_type, balance_after, remark))
        connection.commit()
    except Exception as e:
        raise HTTPException("last value not found: {e}")
    finally:
        if connection and connection.is_connected() and cursor:
            cursor.close()
            connection.close()

def perform_debit(record: TreasuryTransaction, last_record: TreasuryRecord):
    if (last_record.balance_after < record.amount):
        raise Exception("Not enough funds")

    new_balance = last_record.balance_after - record.amount
    insert_transaction(record.state, record.district, record.amount, 'DEBIT', new_balance, record.remark)

def perform_credit(record: TreasuryTransaction):
    last_record = get_last_treasury_data_for_state_and_district(record.state, record.district)
    if (not last_record):
        new_balance = record.amount
    else:
        new_balance = last_record.balance_after + record.amount
    insert_transaction(record.state, record.district, record.amount, 'CREDIT', new_balance, record.remark)