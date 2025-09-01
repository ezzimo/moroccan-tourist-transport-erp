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
    crm_service_url: str = "http://crm_service:8001"
    
    # JWT Configuration (for token validation)
    jwt_secret_key: str = "super-secret-key-change-this"
    jwt_algorithm: str = "HS256"
    jwt_audience: str = "mtterp"
    jwt_issuer: str = "auth-service"
    jwt_allowed_audiences: List[str] = ["mtterp", "booking_service"]
    jwt_disable_audience_check: bool = False
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Booking Configuration
    default_currency: str = "MAD"
    booking_expiry_hours: int = 24
    max_passengers_per_booking: int = 50
    
    # PDF Generation
    pdf_enabled: bool = True
    pdf_company_name: str = "Atlas Tours Morocco"
    pdf_company_address: str = "Casablanca, Morocco"
    pdf_company_phone: str = "+212 522 123 456"
    pdf_company_email: str = "info@atlastours.ma"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()