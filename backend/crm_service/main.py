"""
FastAPI application entry point for CRM microservice
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from config import settings
from database import create_db_and_tables
from routers import customers_router, interactions_router, feedback_router, segments_router
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Customer Relationship Management (CRM) Microservice",
    description="CRM service for Moroccan tourist transport ERP system",
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
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and create tables"""
    create_db_and_tables()
    logger.info("CRM database initialized successfully")


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "crm-microservice",
        "version": "1.0.0"
    }


# Include routers
app.include_router(customers_router, prefix="/api/v1")
app.include_router(interactions_router, prefix="/api/v1")
app.include_router(feedback_router, prefix="/api/v1")
app.include_router(segments_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Customer Relationship Management (CRM) Microservice",
        "version": "1.0.0",
        "description": "CRM service for Moroccan tourist transport ERP system",
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
        "features": [
            "Customer profile management",
            "Interaction tracking",
            "Feedback collection and analysis",
            "Customer segmentation",
            "360° customer view",
            "GDPR compliance"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "crm_service.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug
    )