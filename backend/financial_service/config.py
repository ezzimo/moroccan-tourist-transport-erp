"""
Configuration settings for the financial management microservice
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # Service Integration
    auth_service_url: str
    crm_service_url: str
    booking_service_url: str
    tour_service_url: str
    fleet_service_url: str
    hr_service_url: str
    
    # JWT (for token validation)
    secret_key: str
    algorithm: str = "HS256"
    
    # CORS
    allowed_origins: List[str]
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Financial Configuration
    default_currency: str = "MAD"  # Moroccan Dirham
    supported_currencies: List[str]
    vat_rate: float = 20.0  # Morocco VAT rate
    invoice_due_days: int = 30
    
    # Payment Configuration
    payment_timeout_minutes: int = 30
    auto_reconcile_threshold: float = 0.01  # Auto-reconcile if difference < 1 cent
    
    # Tax Configuration
    tax_year_start_month: int = 1  # January
    vat_declaration_frequency: str = "monthly"  # monthly, quarterly
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str]
    
    # Company Information
    company_name: str
    company_address: str
    company_tax_id: str
    company_vat_number: str
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()