"""
Configuration settings for the CRM microservice
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # Auth Service Integration
    auth_service_url: str
    
    # JWT (for token validation)
    secret_key: str
    algorithm: str = "HS256"
    
    # JWT Audience Configuration
    jwt_audience: str = "mtterp"
    jwt_issuer: str = "auth-service"
    jwt_allowed_audiences: List[str] = ["mtterp"]
    jwt_disable_audience_check: bool = False
    
    # CORS
    allowed_origins: List[str]
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # GDPR Compliance
    data_retention_days: int = 2555  # 7 years for Morocco business records

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()