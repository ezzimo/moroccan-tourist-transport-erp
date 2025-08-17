"""
Configuration settings for the inventory management microservice
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
    fleet_service_url: str
    financial_service_url: str
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
    
    # Inventory Configuration
    default_currency: str = "MAD"  # Moroccan Dirham
    low_stock_alert_threshold: float = 0.2  # 20% of reorder level
    auto_reorder_enabled: bool = False
    
    # Warehouse Configuration
    default_warehouse: str = "Main Warehouse"
    max_warehouses: int = 10
    
    # Purchase Order Configuration
    po_approval_required: bool = True
    po_auto_approve_limit: float = 5000.0  # MAD
    
    # Supplier Configuration
    supplier_performance_period_days: int = 365
    min_supplier_rating: float = 3.0
    
    # Alerts Configuration
    enable_low_stock_alerts: bool = True
    enable_expiry_alerts: bool = True
    alert_check_interval_hours: int = 24
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str]
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()