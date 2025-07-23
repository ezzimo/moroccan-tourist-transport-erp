"""
Configuration settings for the QA & Compliance microservice
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/qa_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/9"
    
    # Service Integration
    auth_service_url: str = "http://localhost:8000"
    crm_service_url: str = "http://localhost:8001"
    booking_service_url: str = "http://localhost:8002"
    tour_service_url: str = "http://localhost:8003"
    fleet_service_url: str = "http://localhost:8004"
    hr_service_url: str = "http://localhost:8005"
    financial_service_url: str = "http://localhost:8006"
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
    
    # QA Configuration
    audit_frequency_days: int = 90  # Default audit frequency
    corrective_action_default_days: int = 30
    certification_alert_days: int = 60  # Alert 60 days before expiry
    
    # Compliance Configuration
    compliance_check_frequency_hours: int = 24
    overdue_escalation_days: int = 7
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = ["pdf", "jpg", "jpeg", "png", "doc", "docx"]
    
    # Scoring Configuration
    audit_pass_score: float = 80.0  # Minimum score to pass audit
    critical_nonconformity_threshold: int = 1  # Max critical issues allowed
    
    # Morocco Specific
    morocco_tourism_authority: str = "Ministry of Tourism, Handicrafts and Social Economy"
    morocco_transport_authority: str = "Ministry of Equipment, Transport, Logistics and Water"
    
    class Config:
        env_file = ".env"


settings = Settings()