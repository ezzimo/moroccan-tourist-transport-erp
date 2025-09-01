"""
Configuration settings for the booking & reservation microservice
"""
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    # Database
    database_url: str = "postgresql://postgres:booking_pass@db_booking:5432/booking_db"
    
    # Redis
    redis_url: str = "redis://redis_auth:6379/2"
    
    # Service Integration
    auth_service_url: str = "http://auth_service:8000"
    crm_service_url: str = "http://crm_service:8001"
    fleet_service_url: str = "http://fleet_service:8004"
    
    # JWT Configuration
    jwt_secret_key: str = "super-secret-key-change-this"
    jwt_algorithm: str = "HS256"
    jwt_audience: str = Field(default="mtterp", alias="JWT_AUDIENCE")
    jwt_issuer: str = Field(default="auth-service", alias="JWT_ISSUER")
    jwt_allowed_audiences: List[str] = Field(default_factory=list, alias="JWT_ALLOWED_AUDIENCES")
    jwt_disable_audience_check: bool = Field(default=False, alias="JWT_DISABLE_AUDIENCE_CHECK")
    
    @field_validator("jwt_allowed_audiences", mode="before")
    @classmethod
    def parse_allowed_audiences(cls, v):
        """Parse JWT allowed audiences from various formats"""
        if v is None:
            return []
        if isinstance(v, list):
            return [str(x) for x in v]
        if isinstance(v, str):
            raw = v.strip()
            if not raw:
                return []
            # Try JSON array first
            if raw.startswith("[") and raw.endswith("]"):
                try:
                    arr = json.loads(raw)
                    if isinstance(arr, list):
                        return [str(x) for x in arr]
                except Exception:
                    pass
            # Fallback: comma-separated
            return [p.strip() for p in raw.split(",") if p.strip()]
        return []
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Booking Configuration
    booking_expiry_hours: int = 24
    max_advance_booking_days: int = 365
    
    # Pricing
    default_currency: str = "MAD"
    tax_rate: float = 20.0


settings = Settings()