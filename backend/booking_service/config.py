"""
Configuration settings for the booking microservice
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/booking_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/2"
    
    # Auth Service Integration
    auth_service_url: str = "http://localhost:8000"
    crm_service_url: str = "http://localhost:8001"
    
    # JWT (for token validation)
    secret_key: str = "your-super-secret-jwt-key-change-in-production"
    algorithm: str = "HS256"
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
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
    
    class Config:
        env_file = ".env"


settings = Settings()