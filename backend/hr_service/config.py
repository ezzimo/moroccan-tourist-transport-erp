"""
Configuration settings for the HR microservice
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # Service Integration
    auth_service_url: str
    crm_service_url: str
    booking_service_url: str
    tour_service_url: str
    fleet_service_url: str
    
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
    
    # HR Configuration
    probation_period_months: int = 6
    annual_leave_days: int = 22  # Morocco standard
    sick_leave_days: int = 90    # Morocco labor law
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str]
    
    # Training
    training_pass_score: float = 70.0
    mandatory_training_reminder_days: int = 30
    
    # Payroll Integration
    payroll_export_schedule: str = "monthly"  # monthly, bi-weekly
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()