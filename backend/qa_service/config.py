"""
Configuration settings for the QA & Compliance microservice
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
    hr_service_url: str
    financial_service_url: str
    notification_service_url: str
    
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
    
    # QA Configuration
    audit_frequency_days: int = 90  # Default audit frequency
    corrective_action_default_days: int = 30
    certification_alert_days: int = 60  # Alert 60 days before expiry
    
    # Compliance Configuration
    compliance_check_frequency_hours: int = 24
    overdue_escalation_days: int = 7
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str]
    
    # Scoring Configuration
    audit_pass_score: float = 80.0  # Minimum score to pass audit
    critical_nonconformity_threshold: int = 1  # Max critical issues allowed
    
    # Morocco Specific
    morocco_tourism_authority: str
    morocco_transport_authority: str
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()