# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import timedelta



class Settings(BaseSettings):
    # ... (Previous fields for Login_Credentials/JWT)
    # Database
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_DATABASE: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720 # 12 hours

    # Global
    ADMIN_API_KEY: str
    # New DBT Database
    DBT_DB_HOST: str
    DBT_DB_PORT: int
    DBT_DB_USER: str
    DBT_DB_PASSWORD: str
    DBT_DB_DATABASE: str
    
    # File Upload Directory
    UPLOAD_DIR: str = "uploaded_files"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings() 

# Directory ko check aur create karna
import os
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR)