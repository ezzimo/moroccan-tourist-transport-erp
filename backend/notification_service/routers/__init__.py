"""
API routers for the notification microservice
"""
from .notifications import router as notifications_router
from .templates import router as templates_router
from .preferences import router as preferences_router
from .logs import router as logs_router

__all__ = ["notifications_router", "templates_router", "preferences_router", "logs_router"]