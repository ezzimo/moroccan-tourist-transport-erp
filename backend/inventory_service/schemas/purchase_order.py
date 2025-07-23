"""
Purchase order-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from models.purchase_order import PurchaseOrderStatus, PurchaseOrderPriority
import uuid


class PurchaseOrderItemCreate(BaseModel):
    item_id: uuid.UUID
    quantity: Decimal
    unit_cost: Decimal
    description: Optional[str] = None
    notes: Optional[str] = None


class PurchaseOrderItemResponse(BaseModel):
    id: uuid.UUID
    item_id: uuid.UUID
    item_name: str
    item_sku: str
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    received_quantity: Decimal
    remaining_quantity: Decimal
    description: Optional[str]
    notes: Optional[str]
    is_fully_received: bool
    received_percentage: float


class PurchaseOrderBase(BaseModel):
    supplier_id: uuid.UUID
    priority: PurchaseOrderPriority = PurchaseOrderPriority.NORMAL
    required_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    delivery_address: Optional[str] = None
    delivery_contact: Optional[str] = None
    delivery_phone: Optional[str] = None
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    items: List[PurchaseOrderItemCreate]
    tax_amount: Decimal = Decimal("0")
    shipping_cost: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    
    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('Purchase order must have at least one item')
        return v
    
    @validator('required_date')
    def validate_required_date(cls, v):
        if v and v < date.today():
            raise ValueError('Required date cannot be in the past')
        return v


class PurchaseOrderUpdate(BaseModel):
    priority: Optional[PurchaseOrderPriority] = None
    status: Optional[PurchaseOrderStatus] = None
    required_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    delivery_address: Optional[str] = None
    delivery_contact: Optional[str] = None
    delivery_phone: Optional[str] = None
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    tax_amount: Optional[Decimal] = None
    shipping_cost: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None


class PurchaseOrderResponse(PurchaseOrderBase):
    id: uuid.UUID
    po_number: str
    status: PurchaseOrderStatus
    subtotal: Decimal
    tax_amount: Decimal
    shipping_cost: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    currency: str
    order_date: date
    actual_delivery_date: Optional[date]
    requested_by: uuid.UUID
    approved_by: Optional[uuid.UUID]
    approved_at: Optional[datetime]
    received_by: Optional[uuid.UUID]
    received_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    supplier_name: str
    items: List[PurchaseOrderItemResponse] = []
    is_overdue: bool
    days_overdue: int
    completion_percentage: float


class PurchaseOrderSummary(BaseModel):
    """Purchase order summary for dashboard"""
    total_orders: int
    by_status: Dict[str, int]
    total_value: Decimal
    pending_approval_value: Decimal
    overdue_orders: int
    average_delivery_time_days: Optional[float]
    by_supplier: Dict[str, int]
    by_priority: Dict[str, int]


class PurchaseOrderSearch(BaseModel):
    """Purchase order search criteria"""
    query: Optional[str] = None
    supplier_id: Optional[uuid.UUID] = None
    status: Optional[PurchaseOrderStatus] = None
    priority: Optional[PurchaseOrderPriority] = None
    requested_by: Optional[uuid.UUID] = None
    order_date_from: Optional[date] = None
    order_date_to: Optional[date] = None
    is_overdue: Optional[bool] = None


class PurchaseOrderApproval(BaseModel):
    """Schema for purchase order approval"""
    approved: bool
    notes: Optional[str] = None


class PurchaseOrderReceiving(BaseModel):
    """Schema for receiving purchase order items"""
    items: List[Dict[str, Any]]  # item_id, received_quantity, notes
    received_date: Optional[date] = None
    notes: Optional[str] = None
    
    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('At least one item must be specified for receiving')
        
        for item in v:
            if 'item_id' not in item or 'received_quantity' not in item:
                raise ValueError('Each item must have item_id and received_quantity')
            
            if item['received_quantity'] <= 0:
                raise ValueError('Received quantity must be positive')
        
        return v


class PurchaseOrderGeneration(BaseModel):
    """Schema for generating purchase orders from reorder suggestions"""
    supplier_id: uuid.UUID
    items: List[Dict[str, Any]]  # item_id, quantity
    priority: PurchaseOrderPriority = PurchaseOrderPriority.NORMAL
    required_date: Optional[date] = None
    notes: Optional[str] = None