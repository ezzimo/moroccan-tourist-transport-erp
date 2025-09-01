"""
Configuration settings for the booking microservice
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:booking_pass@db_booking:5432/booking_db"

    # Redis
    REDIS_URL: str = "redis://redis_auth:6379/2"

    # Service URLs
    CUSTOMER_SERVICE_URL: str = "http://crm_service:8001/api/v1"
    AUTH_SERVICE_URL: str = "http://auth_service:8000/api/v1"

    # JWT
    JWT_SECRET_KEY: str = "super-secret-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    JWT_AUDIENCE: str = "mtterp"
    JWT_ISSUER: str = "auth-service"
    JWT_ALLOWED_AUDIENCES: List[str] = ["mtterp", "booking_service"]
    JWT_DISABLE_AUDIENCE_CHECK: bool = False

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Dev convenience: allow booking creation to proceed if CRM check fails
    ALLOW_DEV_CUSTOMER_BYPASS: bool = True

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()