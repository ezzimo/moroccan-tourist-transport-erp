"""
Configuration settings for the financial management microservice
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/financial_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/6"
    
    # Service Integration
    auth_service_url: str = "http://localhost:8000"
    crm_service_url: str = "http://localhost:8001"
    booking_service_url: str = "http://localhost:8002"
    tour_service_url: str = "http://localhost:8003"
    fleet_service_url: str = "http://localhost:8004"
    hr_service_url: str = "http://localhost:8005"
    
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
    
    # Financial Configuration
    default_currency: str = "MAD"  # Moroccan Dirham
    supported_currencies: List[str] = ["MAD", "EUR", "USD"]
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
    allowed_file_types: List[str] = ["pdf", "jpg", "jpeg", "png", "xlsx", "csv"]
    
    # Company Information
    company_name: str = "Atlas Tours Morocco"
    company_address: str = "Casablanca, Morocco"
    company_tax_id: str = "123456789"
    company_vat_number: str = "MA123456789"
    
    class Config:
        env_file = ".env"


settings = Settings()