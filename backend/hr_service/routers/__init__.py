"""
API routers for the HR microservice
"""
from .employees import router as employees_router
from .recruitment import router as recruitment_router
from .training import router as training_router
from .documents import router as documents_router
from .analytics import router as analytics_router

__all__ = ["employees_router", "recruitment_router", "training_router", "documents_router", "analytics_router"]