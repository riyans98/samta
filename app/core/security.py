# app/core/security.py
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Header, Depends, status
from typing import Optional, Dict, Any
from mysql.connector import Error

from app.core.config import settings
from app.db.session import get_db_connection

# JWT Configuration ko settings se import kiya gaya hai
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# --- 1. Password Hashing and Verification ---

def hash_password(password: str) -> str:
    """Hashes a plain text password using bcrypt."""
    plain_password = password.encode('utf-8')
    # Use bcrypt's gensalt() to generate a unique salt and hash the password
    hashed_password = bcrypt.hashpw(plain_password, bcrypt.gensalt())
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against a bcrypt hash."""
    # Validate hash format before checking
    if not hashed_password or not hashed_password.startswith(('$2b$', '$2a$')):
        return False
    
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# --- 2. JWT Generation and Verification ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Generates a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency Function for JWT Verification
def verify_jwt_token(authorization: str = Header(..., alias='Authorization')) -> Dict[str, Any]:
    """Verifies JWT token from Authorization header and returns payload."""
    try:
        # Extract token from "Bearer <token>" format
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header format.")
        
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login_id: str = payload.get("sub")
        
        if login_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload.")
        
        return payload
        
    except JWTError:
        # JWTError handles expired, invalid signature, or wrong algorithm
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    except IndexError:
        # Handle split index error if header is just "Bearer"
        raise HTTPException(status_code=401, detail="Token missing after 'Bearer'.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {e}")

# Dependency Function for Admin API Key Auth
def api_key_auth(x_api_key: str = Header(..., alias='X-API-Key')):
    """Validates the Admin API Key."""
    if x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key.")
    return x_api_key
    
# --- 3. Login Query (Moved from main.py) ---
def execute_login_query(table_name: str, login_id: str, plain_password: str) -> Optional[Dict[str, Any]]:
    """
    Queries the database for the user's stored hash and verifies the plain password against it.
    Returns the user data (minus the password hash) if successful, otherwise None.
    """
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True) # Retrieve results as dictionaries
        
        query = f"SELECT * FROM {table_name} WHERE login_id = %s"
        cursor.execute(query, (login_id,))
        user_data = cursor.fetchone()

        if not user_data:
            return None
        
        # MySQL columns can be uppercase, so we standardize the keys to lowercase
        # before accessing or using them.
        normalized_data = {k.lower(): v for k, v in user_data.items()}

        stored_hashed_password_str = normalized_data.get('password')
        
        if not stored_hashed_password_str:
             # This should not happen if table is correct, but safe check is good
            return None 

        # Verify the submitted plain password against the stored hash
        if verify_password(plain_password, stored_hashed_password_str):
            # Remove the sensitive password hash before returning user data
            normalized_data.pop('password', None)
            return normalized_data
        
        return None
            
    except Error as e:
        print(f"Database Error during login: {e}")
        # Only raise 500 if it's a connection/query error, not an authentication failure
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database login check failed: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()