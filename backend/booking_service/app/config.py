# backend/booking_service/app/config.py
from __future__ import annotations

import json
from typing import List, Union

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:booking_pass@db_booking:5432/booking_db"

    # Redis
    REDIS_URL: str = "redis://redis_auth:6379/2"

    # Service URLs for inter-service communication (use internal DNS + API prefix)
    CUSTOMER_SERVICE_URL: Union[AnyHttpUrl, str] = "http://crm_service:8001/api/v1"
    AUTH_SERVICE_URL: Union[AnyHttpUrl, str] = "http://auth_service:8000/api/v1"

    # JWT Configuration (must match auth_service)
    JWT_SECRET_KEY: str = "super-secret-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    JWT_AUDIENCE: str = "mtterp"
    JWT_ISSUER: str = "auth-service"
    JWT_ALLOWED_AUDIENCES: List[str] = ["mtterp", "booking_service"]
    JWT_DISABLE_AUDIENCE_CHECK: bool = False

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Dev feature flags
    ALLOW_DEV_CUSTOMER_BYPASS: bool = False

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Pydantic Settings config
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,  # allow envs like jwt_secret_key or JWT_SECRET_KEY
    )

    # --- Validators to accept JSON *or* comma-separated env values ---

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def _parse_allowed_origins(cls, v):
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return []
            # Try JSON array first: '["http://a","http://b"]'
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    return [str(x) for x in parsed]
            except Exception:
                pass
            # Fallback to comma-separated: 'http://a,http://b'
            return [part.strip() for part in s.split(",") if part.strip()]
        return v

    @field_validator("JWT_ALLOWED_AUDIENCES", mode="before")
    @classmethod
    def _parse_jwt_audiences(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return []
            # Try JSON array first
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    return [str(x) for x in parsed]
            except Exception:
                pass
            # Fallback to comma-separated
            return [part.strip() for part in s.split(",") if part.strip()]
        return v


# Singleton settings instance
settings = Settings()
