"""
Configuration settings for the HR microservice
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/hr_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/5"
    
    # Service Integration
    auth_service_url: str = "http://localhost:8000"
    crm_service_url: str = "http://localhost:8001"
    booking_service_url: str = "http://localhost:8002"
    tour_service_url: str = "http://localhost:8003"
    fleet_service_url: str = "http://localhost:8004"
    
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
    
    # HR Configuration
    probation_period_months: int = 6
    annual_leave_days: int = 22  # Morocco standard
    sick_leave_days: int = 90    # Morocco labor law
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = ["pdf", "jpg", "jpeg", "png", "doc", "docx"]
    
    # Training
    training_pass_score: float = 70.0
    mandatory_training_reminder_days: int = 30
    
    # Payroll Integration
    payroll_export_schedule: str = "monthly"  # monthly, bi-weekly
    
    class Config:
        env_file = ".env"


settings = Settings()