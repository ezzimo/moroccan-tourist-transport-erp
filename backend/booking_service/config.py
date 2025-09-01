"""
Configuration settings for the booking service
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List
import json


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:booking_pass@db_booking:5432/booking_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/2"
    
    # Service Integration
    auth_service_url: str = "http://auth_service:8000"
    crm_service_url: str = "http://crm_service:8001"
    fleet_service_url: str = "http://fleet_service:8004"
    
    # JWT Configuration (aligned with auth service)
    secret_key: str = "super-secret-key-change-this"
    algorithm: str = "HS256"
    jwt_audience: str = "mtterp"
    jwt_issuer: str = "auth-service"
    jwt_allowed_audiences: List[str] = ["mtterp"]
    jwt_disable_audience_check: bool = False
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Booking Configuration
    default_booking_expiry_hours: int = 24
    max_booking_duration_days: int = 365
    
    @field_validator("jwt_allowed_audiences", mode="before")
    @classmethod
    def parse_jwt_audiences(cls, v):
        """Parse JWT audiences from JSON string or comma-separated values"""
        if not v:
            return ["mtterp"]  # Default audience
        
        if isinstance(v, list):
            return v
        
        if isinstance(v, str):
            # Try JSON array first
            if v.strip().startswith('[') and v.strip().endswith(']'):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return parsed
                except json.JSONDecodeError:
                    pass
            
            # Fall back to comma-separated
            return [aud.strip() for aud in v.split(',') if aud.strip()]
        
        return ["mtterp"]
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()