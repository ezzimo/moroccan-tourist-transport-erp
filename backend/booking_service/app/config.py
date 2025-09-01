@@ .. @@
 class Settings(BaseSettings):
     # Database
     database_url: str = "postgresql://postgres:booking_pass@db_booking:5432/booking_db"
     
     # Redis
     redis_url: str = "redis://redis_auth:6379/2"
     
     # Service Integration
     auth_service_url: str = "http://auth_service:8000"
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
     
+    # Development settings
+    allow_dev_customer_bypass: bool = False
+    
     # Pagination
     default_page_size: int = 20
     max_page_size: int = 100