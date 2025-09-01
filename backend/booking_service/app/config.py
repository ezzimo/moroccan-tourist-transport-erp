@@ .. @@
 class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:booking_pass@db_booking:5432/booking_db"
    
    # Redis
    REDIS_URL: str = "redis://redis_auth:6379/2"
    
    # Service URLs for inter-service communication
    CUSTOMER_SERVICE_URL: str = "http://crm_service:8001/api/v1"
    AUTH_SERVICE_URL: str = "http://auth_service:8000/api/v1"
    
    # JWT Configuration (should match auth service)
    JWT_SECRET_KEY: str = "super-secret-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    JWT_AUDIENCE: str = "mtterp"
    JWT_ISSUER: str = "auth-service"
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
     # Database
     database_url: str = "postgresql://postgres:booking_pass@db_booking:5432/booking_db"
     
     # Redis
     redis_url: str = "redis://redis_auth:6379/2"
     
     # Service Integration
     auth_service_url: str = "http://auth_service:8000"
    customer_service_url: str = "http://crm_service:8001"
+    customer_service_url: str = "http://crm_service:8001"
     
     # JWT (for token validation)
     secret_key: str = "super-secret-key-change-this"
     algorithm: str = "HS256"
     jwt_audience: str = "mtterp"
     jwt_issuer: str = "auth-service"
     jwt_allowed_audiences: List[str] = ["mtterp", "booking_service"]
     jwt_disable_audience_check: bool = False
     
     # CORS
     allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
     
     # Environment
     environment: str = "development"
     debug: bool = True
    allow_dev_customer_bypass: bool = False
     
+    # Development settings
+    allow_dev_customer_bypass: bool = False
+    
     # Pagination
     default_page_size: int = 20
     max_page_size: int = 100