"""
API routers for the fleet management microservice
"""
from .vehicles import router as vehicles_router
from .maintenance import router as maintenance_router
from .assignments import router as assignments_router
from .fuel import router as fuel_router
from .documents import router as documents_router

__all__ = ["vehicles_router", "maintenance_router", "assignments_router", "fuel_router", "documents_router"]