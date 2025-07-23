"""
API routers for the inventory management microservice
"""
from .items import router as items_router
from .movements import router as movements_router
from .suppliers import router as suppliers_router
from .purchase_orders import router as purchase_orders_router
from .analytics import router as analytics_router

__all__ = ["items_router", "movements_router", "suppliers_router", "purchase_orders_router", "analytics_router"]