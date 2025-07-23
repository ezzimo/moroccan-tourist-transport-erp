"""
API routers for the CRM microservice
"""
from .customers import router as customers_router
from .interactions import router as interactions_router
from .feedback import router as feedback_router
from .segments import router as segments_router

__all__ = ["customers_router", "interactions_router", "feedback_router", "segments_router"]