"""
Configuration settings for the driver management microservice
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/driver_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/10"
    
    # Service Integration
    auth_service_url: str = "http://localhost:8000"
    tour_service_url: str = "http://localhost:8003"
    fleet_service_url: str = "http://localhost:8004"
    hr_service_url: str = "http://localhost:8005"
    notification_service_url: str = "http://localhost:8007"
    
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
    
    # Driver Configuration
    license_alert_days: int = 30  # Alert 30 days before license expiry
    health_cert_alert_days: int = 60  # Alert 60 days before health cert expiry
    training_validity_months: int = 24  # Default training validity period
    
    # Assignment Configuration
    max_daily_hours: int = 10  # Maximum driving hours per day
    rest_period_hours: int = 11  # Minimum rest period between assignments
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = ["pdf", "jpg", "jpeg", "png", "doc", "docx"]
    
    # Mobile API Configuration
    mobile_session_timeout: int = 86400  # 24 hours
    offline_sync_enabled: bool = True
    
    # Performance Tracking
    performance_review_period_months: int = 6
    incident_severity_weights: dict = {
        "minor": 1,
        "moderate": 3,
        "major": 5,
        "critical": 10
    }
    
    class Config:
        env_file = ".env"


settings = Settings()