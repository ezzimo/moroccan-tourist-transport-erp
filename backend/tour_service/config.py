"""
Configuration settings for the tour operations microservice
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:tour_pass@db_tour:5432/tour_db"
    
    # Redis
    redis_url: str = "redis://localhost:6382/3"
    
    # Service Integration
    auth_service_url: str = "http://auth_service:8000"
    crm_service_url: str = "http://crm_service:8001"
    booking_service_url: str = "http://booking_service:8002"
    
    # JWT (for token validation)
    secret_key: str = "super-secret-key-change-this"
    algorithm: str = "HS256"
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Tour Configuration
    max_tour_duration_days: int = 30
    default_language: str = "French"
    
    # Real-time Updates
    websocket_enabled: bool = True
    notification_timeout: int = 30
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()