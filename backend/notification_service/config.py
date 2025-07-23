"""
Configuration settings for the notification microservice
"""
from pydantic_settings import BaseSettings
from typing import List, Dict, Any


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/notification_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/7"
    
    # Service Integration
    auth_service_url: str = "http://localhost:8000"
    crm_service_url: str = "http://localhost:8001"
    booking_service_url: str = "http://localhost:8002"
    tour_service_url: str = "http://localhost:8003"
    fleet_service_url: str = "http://localhost:8004"
    hr_service_url: str = "http://localhost:8005"
    financial_service_url: str = "http://localhost:8006"
    
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
    
    # Notification Configuration
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 60
    notification_timeout_seconds: int = 30
    
    # Email Configuration (SMTP)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    default_from_email: str = "noreply@atlastours.ma"
    default_from_name: str = "Atlas Tours Morocco"
    
    # SMS Configuration (Twilio)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    
    # Push Notification Configuration (Firebase)
    firebase_server_key: str = ""
    firebase_project_id: str = ""
    
    # WhatsApp Configuration (optional)
    whatsapp_api_url: str = ""
    whatsapp_api_token: str = ""
    
    # Rate Limiting
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 1000
    
    # Template Configuration
    template_cache_ttl: int = 3600  # 1 hour
    max_template_size: int = 1024 * 1024  # 1MB
    
    # Fallback Configuration
    enable_fallback_channels: bool = True
    fallback_mapping: Dict[str, List[str]] = {
        "email": ["sms"],
        "sms": ["email"],
        "push": ["email", "sms"]
    }
    
    # Webhook Configuration
    webhook_timeout_seconds: int = 10
    webhook_retry_attempts: int = 2
    
    class Config:
        env_file = ".env"


settings = Settings()