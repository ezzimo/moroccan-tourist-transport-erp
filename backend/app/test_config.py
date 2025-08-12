"""
Test configuration settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class TestSettings(BaseSettings):
    __test__ = False
    # Database - Use SQLite for testing
    database_url: str = "sqlite:///./test_auth.db"

    # Redis - Use fake Redis for testing
    redis_url: str = "redis://localhost:6379/1"

    # JWT
    secret_key: str = "test-secret-key-for-testing-only"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # OTP
    otp_expire_minutes: int = 5
    otp_max_attempts: int = 3

    # Rate Limiting
    login_rate_limit: int = 5  # attempts per minute

    # CORS
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Environment
    environment: str = "testing"
    debug: bool = True

    model_config = SettingsConfigDict(env_file=".env.test", extra="ignore")


test_settings = TestSettings()
