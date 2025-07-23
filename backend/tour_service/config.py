"""
Configuration settings for the tour operations microservice
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/tour_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/3"
    
    # Service Integration
    auth_service_url: str = "http://localhost:8000"
    crm_service_url: str = "http://localhost:8001"
    booking_service_url: str = "http://localhost:8002"
    
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
    
    # Tour Configuration
    max_tour_duration_days: int = 30
    default_language: str = "French"
    
    # Real-time Updates
    websocket_enabled: bool = True
    notification_timeout: int = 30
    
    class Config:
        env_file = ".env"


settings = Settings()