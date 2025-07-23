"""
API routers for the QA & Compliance microservice
"""
from .audits import router as audits_router
from .nonconformities import router as nonconformities_router
from .compliance import router as compliance_router
from .certifications import router as certifications_router
from .reports import router as reports_router

__all__ = ["audits_router", "nonconformities_router", "compliance_router", "certifications_router", "reports_router"]