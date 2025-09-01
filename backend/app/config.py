"""
Configuration settings for the authentication microservice
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    database_url_sync: str
    database_url_async: str
    redis_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    otp_expire_minutes: int
    otp_max_attempts: int
    login_rate_limit: int
    allowed_origins: list[str]
    environment: str
    debug: bool
    
    # JWT Configuration
    jwt_audience: str = "mtterp"
    jwt_issuer: str = "auth-service"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
