"""
Configuration settings for the booking microservice
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:booking_pass@db_booking:5432/booking_db"
    
    # Redis
    redis_url: str = "redis://redis_auth:6379/2"
    
    # Service Integration
    auth_service_url: str = "http://auth_service:8000"
    customer_service_base: str = "http://crm_service:8001/api/v1"
    
    # Customer Verification
    customer_verify_strict: bool = False
    customer_http_timeout: float = 2.0
    
    # JWT (for token validation)
    jwt_secret_key: str = "super-secret-key-change-this"
    jwt_algorithm: str = "HS256"
    jwt_audience: str = "mtterp"
    jwt_issuer: str = "auth-service"
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()