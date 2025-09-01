"""
FastAPI application entry point for booking service
"""
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from config import settings
from database import create_db_and_tables
from routers import (
    bookings_router, availability_router, pricing_router, reservation_items_router
)
import logging
import traceback


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
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and create tables"""
    try:
        create_db_and_tables()
        logger.info("Booking service database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


# Health check with dependency verification
@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        from database import get_session, get_redis
        from sqlmodel import text
        
        # Test database connection
        try:
            db = next(get_session())
            db.exec(text("SELECT 1"))
            db.close()
            db_status = "healthy"
        except Exception as db_error:
            db_status = f"unhealthy: {str(db_error)}"
        
        # Test Redis connection
        try:
            redis_client = get_redis()
            redis_client.ping()
            redis_status = "healthy"
        except Exception as redis_error:
            redis_status = f"unhealthy: {str(redis_error)}"
        
        # Test PDF generation capability
        try:
            from utils.pdf_generator import PDFGenerator
            pdf_gen = PDFGenerator()
            pdf_status = "healthy"
        except Exception as pdf_error:
            pdf_status = f"unhealthy: {str(pdf_error)}"
            logger.error(f"PDF generator error: {pdf_error}")
        
        # Overall health status
        overall_status = "healthy" if all(
            status == "healthy" for status in [db_status, redis_status, pdf_status]
        ) else "unhealthy"
        
        response = {
            "status": overall_status,
            "service": "booking-microservice",
            "version": "1.0.0",
            "database": db_status,
            "redis": redis_status,
            "pdf_generator": pdf_status,
            "timestamp": "2025-01-15T10:00:00Z"
        }
        
        if overall_status == "unhealthy":
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=response
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "booking-microservice",
                "version": "1.0.0",
                "error": str(e)
            }
        )


# Include routers
app.include_router(bookings_router, prefix="/api/v1")
app.include_router(availability_router, prefix="/api/v1")
app.include_router(pricing_router, prefix="/api/v1")
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
            "Availability checking",
            "Dynamic pricing",
            "Reservation items",
            "PDF voucher generation",
            "Real-time notifications"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=settings.debug
    )