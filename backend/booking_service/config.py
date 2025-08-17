"""
Configuration settings for the booking microservice
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # Auth Service Integration
    auth_service_url: str
    crm_service_url: str
    
    # JWT (for token validation)
    secret_key: str
    algorithm: str = "HS256"
    
    # CORS
    allowed_origins: List[str]
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Booking Configuration
    booking_expiry_minutes: int = 30  # Auto-expire unconfirmed bookings
    max_concurrent_bookings: int = 1000
    
    # Pricing
    default_currency: str = "MAD"  # Moroccan Dirham
    
    # PDF Generation
    company_name: str = "Atlas Tours Morocco"
    company_address: str = "Casablanca, Morocco"
    company_phone: str = "+212 522 123 456"
    company_email: str = "info@atlastours.ma"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()