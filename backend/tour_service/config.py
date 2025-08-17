"""
Configuration settings for the tour operations microservice
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
    
    # Tour Configuration
    max_tour_duration_days: int = 30
    default_language: str = "French"
    
    # Real-time Updates
    websocket_enabled: bool = True
    notification_timeout: int = 30
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()