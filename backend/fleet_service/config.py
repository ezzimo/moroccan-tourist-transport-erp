"""
Configuration settings for the fleet management microservice
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/fleet_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/4"
    
    # Service Integration
    auth_service_url: str = "http://localhost:8000"
    crm_service_url: str = "http://localhost:8001"
    booking_service_url: str = "http://localhost:8002"
    tour_service_url: str = "http://localhost:8003"
    
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
    
    # Fleet Configuration
    maintenance_alert_days: int = 7  # Days before maintenance due
    compliance_alert_days: int = 30  # Days before compliance expiry
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = ["pdf", "jpg", "jpeg", "png", "doc", "docx"]
    
    class Config:
        env_file = ".env"


settings = Settings()