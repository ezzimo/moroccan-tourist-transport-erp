"""
Configuration settings for the CRM microservice
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/crm_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/1"
    
    # Auth Service Integration
    auth_service_url: str = "http://localhost:8000"
    
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
    
    # GDPR Compliance
    data_retention_days: int = 2555  # 7 years for Morocco business records
    
    class Config:
        env_file = ".env"


settings = Settings()