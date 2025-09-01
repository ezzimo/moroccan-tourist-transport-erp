"""
Configuration settings for the booking service
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field
from typing import List, Optional
from pydantic import Field, field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import json
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)
    
    # Database
    database_url: str = "postgresql://postgres:booking_pass@db_booking:5432/booking_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/2"
    
    # Service Integration
    auth_service_url: str = "http://auth_service:8000"
    crm_service_url: str = "http://crm_service:8001"
    fleet_service_url: str = "http://fleet_service:8004"
    
    # JWT Configuration (aligned with auth service)
    jwt_secret_key: str = Field(default="super-secret-key-change-this", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_audience: str = Field(default="mtterp", alias="JWT_AUDIENCE")
    jwt_issuer: str = Field(default="auth-service", alias="JWT_ISSUER")
    
    # Raw string for flexible parsing
    jwt_allowed_audiences_raw: Optional[str] = Field(default=None, alias="JWT_ALLOWED_AUDIENCES")
    jwt_disable_audience_check: bool = Field(default=False, alias="JWT_DISABLE_AUDIENCE_CHECK")
    
    @field_validator("jwt_allowed_audiences_raw", mode="before")
    @classmethod
    def validate_audiences_raw(cls, v):
        # Keep as string for computed_field processing
        return v
    
    @computed_field
    @property
    def jwt_allowed_audiences(self) -> List[str]:
        """Parse JWT_ALLOWED_AUDIENCES from JSON array or CSV format"""
        if not self.jwt_allowed_audiences_raw:
            return [self.jwt_audience]
        
        raw = self.jwt_allowed_audiences_raw.strip()
        if not raw:
            return [self.jwt_audience]
        
        # Try JSON array first
        if raw.startswith("[") and raw.endswith("]"):
            try:
                arr = json.loads(raw)
                if isinstance(arr, list):
                    return [str(x) for x in arr if x]
            except json.JSONDecodeError:
                pass
        
        # Fallback: comma-separated
        audiences = [p.strip() for p in raw.split(",") if p.strip()]
        return audiences if audiences else [self.jwt_audience]
    jwt_audience: str = "mtterp"
    jwt_issuer: str = "auth-service"
    jwt_allowed_audiences_raw: Optional[str] = Field(default=None, alias="JWT_ALLOWED_AUDIENCES")
    jwt_disable_audience_check: bool = False
    
    # CORS
    allowed_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:8080"])
    
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
    
    @computed_field
    @property
    def jwt_allowed_audiences(self) -> List[str]:
        """Parse JWT_ALLOWED_AUDIENCES from string to list"""
        if not self.jwt_allowed_audiences_raw:
            return [self.jwt_audience]  # Default to main audience
        
        raw = self.jwt_allowed_audiences_raw.strip()
        if not raw:
            return [self.jwt_audience]
        
        # Try JSON parse first
        if raw.startswith('[') and raw.endswith(']'):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed if item]
            except json.JSONDecodeError:
                pass
        


settings = Settings()