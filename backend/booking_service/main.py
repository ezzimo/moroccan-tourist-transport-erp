"""
FastAPI application entry point for booking service
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from dependencies import get_redis
from config import settings
from dependencies import get_redis
from database import create_db_and_tables
from routers import bookings_router, pricing_router, availability_router, reservation_items_router
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Booking & Reservation Microservice",
    description="Booking and reservation service for Moroccan tourist transport ERP system",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    # Log first (lazy formatting; no big string building unless needed)
    logger.warning(
        "Validation error on %s %s: %s",
        request.method, request.url, exc.errors()
    )

    # Then return a JSON payload (frontend-friendly and consistent)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),     # standard Pydantic error list
            "type": "validation_error",
        },
    )


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    """Handle internal server errors"""
    logger.exception(f"Internal server error on {request.method} {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "type": "system_error",
            "error_code": "INTERNAL_ERROR"
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and create tables"""
    create_db_and_tables()
    logger.info("Booking service database initialized successfully")


@app.get("/health")
async def health_check():
    """Health check endpoint with JWT configuration info"""
    try:
        from database import get_session, get_redis
        from sqlmodel import text
        
        # Test database connection
        db = next(get_session())
        db.exec(text("SELECT 1"))
        db.close()
        
        # Test Redis connection
        try:
            redis_client = await get_redis()
            await redis_client.ping()
            redis_status = "connected"
        except Exception as redis_error:
            redis_status = f"error: {str(redis_error)}"
        
        return {
            "status": "healthy",
            "service": "booking-microservice",
            "version": "1.0.0",
            "database": "connected",
            "redis": redis_status,
            "jwt_config": {
                "audience": settings.jwt_audience,
                "allowed_audiences": settings.jwt_allowed_audiences,
                "issuer": settings.jwt_issuer,
                "disable_audience_check": settings.jwt_disable_audience_check
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "booking-microservice",
                "version": "1.0.0",
                "database": "error",
                "redis": "error",
                "error": str(e)
            }
        )


# Include routers
app.include_router(bookings_router, prefix="/api/v1")
app.include_router(pricing_router, prefix="/api/v1")
app.include_router(availability_router, prefix="/api/v1")
app.include_router(reservation_items_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Booking & Reservation Microservice",
        "version": "1.0.0",
        "description": "Booking and reservation service for Moroccan tourist transport ERP system",
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
        "features": [
            "Booking management",
            "Pricing calculations",
            "Availability checking",
            "Reservation items",
            "Real-time notifications",
            "Multi-currency support"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "booking_service.main:app",
        host="0.0.0.0",
        port=8002,
        reload=settings.debug
    )