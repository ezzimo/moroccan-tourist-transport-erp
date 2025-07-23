"""
API routers for the financial management microservice
"""
from .invoices import router as invoices_router
from .payments import router as payments_router
from .expenses import router as expenses_router
from .tax_reports import router as tax_reports_router
from .analytics import router as analytics_router

__all__ = ["invoices_router", "payments_router", "expenses_router", "tax_reports_router", "analytics_router"]