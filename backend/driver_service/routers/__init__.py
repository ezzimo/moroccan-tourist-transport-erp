"""
API routers for the driver management microservice
"""
from .drivers import router as drivers_router
from .assignments import router as assignments_router
from .training import router as training_router
from .incidents import router as incidents_router
from .mobile import router as mobile_router

__all__ = ["drivers_router", "assignments_router", "training_router", "incidents_router", "mobile_router"]