"""
Configuration settings for the booking microservice
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:booking_pass@db_booking:5432/booking_db"
    
    # Redis
    redis_url: str = "redis://localhost:6381/2"
    
    # Service Integration
    auth_service_url: str = "http://auth_service:8000"
    crm_service_url: str = "http://crm_service:8001"
    fleet_service_url: str = "http://fleet_service:8004"
    
    # JWT Configuration (aligned with auth service)
    jwt_secret_key: str = "super-secret-key-change-this"
    jwt_algorithm: str = "HS256"
    jwt_audience: str = "mtterp"
    jwt_issuer: str = "auth-service"
    jwt_allowed_audiences: List[str] = ["mtterp", "tourist-erp"]
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
    max_participants_per_booking: int = 50
    
    # Pricing Configuration
    default_tax_rate: float = 20.0
    enable_dynamic_pricing: bool = True
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()