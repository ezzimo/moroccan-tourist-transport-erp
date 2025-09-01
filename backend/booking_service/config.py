"""
Configuration settings for the booking microservice
"""
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json
from typing import List, Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    # Database
    database_url: str = Field(
        default="postgresql://postgres:booking_pass@db_booking:5432/booking_db",
        alias="DATABASE_URL"
    )
    
    # Redis
    redis_url: str = Field(
        default="redis://redis_auth:6379/2",
        alias="REDIS_URL"
    )
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=2, alias="REDIS_DB")
    
    # JWT Configuration
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_audience: str = Field(default="mtterp", alias="JWT_AUDIENCE")
    jwt_issuer: str = Field(default="auth-service", alias="JWT_ISSUER")
    jwt_allowed_audiences: List[str] = Field(default_factory=list, alias="JWT_ALLOWED_AUDIENCES")
    jwt_disable_audience_check: bool = Field(default=False, alias="JWT_DISABLE_AUDIENCE_CHECK")
    
    # Service Integration
    auth_service_url: str = Field(
        default="http://auth_service:8000",
        alias="AUTH_SERVICE_URL"
    )
    
    # CORS
    allowed_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        alias="ALLOWED_ORIGINS"
    )
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Environment
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    
    @field_validator("jwt_allowed_audiences", mode="before")
    @classmethod
    def parse_allowed_audiences(cls, raw):
        """Parse JWT_ALLOWED_AUDIENCES from various formats"""
        if raw is None or raw == "":
            return []
        if isinstance(raw, list):
            return [str(x) for x in raw]
        if isinstance(raw, str):
            raw = raw.strip()
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

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, raw):
        """Parse ALLOWED_ORIGINS from various formats"""
        if raw is None:
            return ["http://localhost:3000"]
        if isinstance(raw, list):
            return [str(x) for x in raw]
        if isinstance(raw, str):
            raw = raw.strip()
            if not raw:
                return ["http://localhost:3000"]
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
        return [raw]


settings = Settings()