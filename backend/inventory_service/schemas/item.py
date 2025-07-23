"""
Item-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from models.item import ItemCategory, ItemUnit, ItemStatus
import uuid


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    sku: str
    barcode: Optional[str] = None
    category: ItemCategory
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    unit: ItemUnit
    unit_cost: Decimal
    currency: str = "MAD"
    reorder_level: Decimal
    max_stock_level: Optional[Decimal] = None
    warehouse_location: str = "Main Warehouse"
    bin_location: Optional[str] = None
    primary_supplier_id: Optional[uuid.UUID] = None
    has_expiry: bool = False
    shelf_life_days: Optional[int] = None
    is_critical: bool = False
    notes: Optional[str] = None


class ItemCreate(ItemBase):
    current_quantity: Decimal = Decimal("0")
    
    @validator('unit_cost', 'reorder_level')
    def validate_positive_values(cls, v):
        if v < 0:
            raise ValueError('Value must be non-negative')
        return v
    
    @validator('sku')
    def validate_sku(cls, v):
        if not v.strip():
            raise ValueError('SKU cannot be empty')
        return v.strip().upper()
    
    @validator('shelf_life_days')
    def validate_shelf_life(cls, v, values):
        if v is not None and v <= 0:
            raise ValueError('Shelf life must be positive')
        if values.get('has_expiry') and v is None:
            raise ValueError('Shelf life is required for items with expiry')
        return v


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    barcode: Optional[str] = None
    category: Optional[ItemCategory] = None
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    unit: Optional[ItemUnit] = None
    unit_cost: Optional[Decimal] = None
    reorder_level: Optional[Decimal] = None
    max_stock_level: Optional[Decimal] = None
    warehouse_location: Optional[str] = None
    bin_location: Optional[str] = None
    primary_supplier_id: Optional[uuid.UUID] = None
    has_expiry: Optional[bool] = None
    shelf_life_days: Optional[int] = None
    status: Optional[ItemStatus] = None
    is_critical: Optional[bool] = None
    notes: Optional[str] = None


class ItemResponse(ItemBase):
    id: uuid.UUID
    current_quantity: Decimal
    reserved_quantity: Decimal
    last_purchase_date: Optional[date]
    last_purchase_cost: Optional[Decimal]
    average_cost: Optional[Decimal]
    expiry_date: Optional[date]
    status: ItemStatus
    created_at: datetime
    updated_at: Optional[datetime]
    available_quantity: Decimal
    is_low_stock: bool
    is_out_of_stock: bool
    stock_value: Decimal
    is_expired: bool
    days_until_expiry: Optional[int]


class ItemSummary(BaseModel):
    """Item summary for dashboard"""
    total_items: int
    active_items: int
    low_stock_items: int
    out_of_stock_items: int
    expired_items: int
    total_stock_value: Decimal
    by_category: Dict[str, int]
    by_warehouse: Dict[str, int]
    critical_items_low_stock: int


class ItemSearch(BaseModel):
    """Item search criteria"""
    query: Optional[str] = None
    category: Optional[ItemCategory] = None
    status: Optional[ItemStatus] = None
    warehouse_location: Optional[str] = None
    supplier_id: Optional[uuid.UUID] = None
    is_low_stock: Optional[bool] = None
    is_critical: Optional[bool] = None
    has_expiry: Optional[bool] = None


class ItemStockAdjustment(BaseModel):
    """Schema for stock adjustment"""
    quantity: Decimal
    reason: str
    notes: Optional[str] = None
    reference_number: Optional[str] = None
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v == 0:
            raise ValueError('Adjustment quantity cannot be zero')
        return v


class ItemReorderSuggestion(BaseModel):
    """Schema for reorder suggestions"""
    item_id: uuid.UUID
    item_name: str
    current_quantity: Decimal
    reorder_level: Decimal
    suggested_quantity: Decimal
    primary_supplier_name: Optional[str]
    estimated_cost: Optional[Decimal]
    priority: str  # Low, Normal, High, Critical