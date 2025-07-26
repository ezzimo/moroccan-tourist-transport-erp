"""
Pydantic schemas for request/response models
"""

from .item import ItemBase, ItemCreate, ItemUpdate, ItemResponse, ItemSummary
from .supplier import (
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
    SupplierWithStats,
    SupplierPerformance,
)
from .stock_movement import (
    StockMovementBase,
    StockMovementCreate,
    StockMovementUpdate,
    StockMovementResponse,
)
from .purchase_order import (
    PurchaseOrderBase,
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    PurchaseOrderResponse,
    PurchaseOrderSummary,
)


__all__ = [
    # Item schemas
    "ItemBase",
    "ItemCreate",
    "ItemUpdate",
    "ItemResponse",
    "ItemSummary",
    # Supplier schemas
    "SupplierCreate",
    "SupplierUpdate",
    "SupplierResponse",
    "SupplierWithStats",
    "SupplierPerformance",
    # Purchase order schemas
    "PurchaseOrderBase",
    "PurchaseOrderCreate",
    "PurchaseOrderUpdate",
    "PurchaseOrderResponse",
    "PurchaseOrderSummary",
    # Stock movement schemas
    "StockMovementBase",
    "StockMovementCreate",
    "StockMovementUpdate",
    "StockMovementResponse",
]
