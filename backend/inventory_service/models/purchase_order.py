"""
Purchase order model for procurement management
"""
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Numeric
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
import uuid


class PurchaseOrderStatus(str, Enum):
    """Purchase order status enumeration"""
    DRAFT = "Draft"
    PENDING = "Pending"
    APPROVED = "Approved"
    SENT = "Sent"
    CONFIRMED = "Confirmed"
    PARTIALLY_RECEIVED = "Partially Received"
    RECEIVED = "Received"
    CANCELLED = "Cancelled"
    CLOSED = "Closed"


class PurchaseOrderPriority(str, Enum):
    """Purchase order priority enumeration"""
    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"
    URGENT = "Urgent"


class PurchaseOrder(SQLModel, table=True):
    """Purchase order model for procurement management"""
    __tablename__ = "purchase_orders"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Order Identification
    po_number: str = Field(unique=True, max_length=50, index=True)
    
    # Supplier Information
    supplier_id: uuid.UUID = Field(foreign_key="suppliers.id", index=True)
    
    # Order Details
    status: PurchaseOrderStatus = Field(default=PurchaseOrderStatus.DRAFT, index=True)
    priority: PurchaseOrderPriority = Field(default=PurchaseOrderPriority.NORMAL)
    
    # Financial Information
    subtotal: Decimal = Field(default=0, sa_column=Column(Numeric(12, 2)))
    tax_amount: Decimal = Field(default=0, sa_column=Column(Numeric(10, 2)))
    shipping_cost: Decimal = Field(default=0, sa_column=Column(Numeric(10, 2)))
    discount_amount: Decimal = Field(default=0, sa_column=Column(Numeric(10, 2)))
    total_amount: Decimal = Field(sa_column=Column(Numeric(12, 2)))
    currency: str = Field(default="MAD", max_length=3)
    
    # Dates
    order_date: date = Field(default_factory=date.today, index=True)
    required_date: Optional[date] = Field(default=None)
    expected_delivery_date: Optional[date] = Field(default=None)
    actual_delivery_date: Optional[date] = Field(default=None)
    
    # Delivery Information
    delivery_address: Optional[str] = Field(default=None, max_length=500)
    delivery_contact: Optional[str] = Field(default=None, max_length=255)
    delivery_phone: Optional[str] = Field(default=None, max_length=20)
    
    # Terms and Conditions
    payment_terms: Optional[str] = Field(default=None, max_length=100)
    delivery_terms: Optional[str] = Field(default=None, max_length=100)
    
    # Additional Information
    notes: Optional[str] = Field(default=None, max_length=2000)
    internal_notes: Optional[str] = Field(default=None, max_length=1000)
    
    # Approval Workflow
    requested_by: uuid.UUID = Field(index=True)
    approved_by: Optional[uuid.UUID] = Field(default=None)
    approved_at: Optional[datetime] = Field(default=None)
    
    # Receiving Information
    received_by: Optional[uuid.UUID] = Field(default=None)
    received_at: Optional[datetime] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    supplier: Optional["Supplier"] = Relationship(back_populates="purchase_orders")
    items: List["PurchaseOrderItem"] = Relationship(back_populates="purchase_order")
    
    def calculate_totals(self):
        """Calculate order totals from items"""
        if not self.items:
            return
        
        self.subtotal = sum(item.total_cost for item in self.items)
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost - self.discount_amount
    
    def is_overdue(self) -> bool:
        """Check if order is overdue"""
        if not self.expected_delivery_date or self.status in [
            PurchaseOrderStatus.RECEIVED, 
            PurchaseOrderStatus.CANCELLED, 
            PurchaseOrderStatus.CLOSED
        ]:
            return False
        
        return date.today() > self.expected_delivery_date
    
    def get_days_overdue(self) -> int:
        """Get number of days overdue"""
        if not self.is_overdue():
            return 0
        
        return (date.today() - self.expected_delivery_date).days
    
    def can_be_cancelled(self) -> bool:
        """Check if order can be cancelled"""
        return self.status in [
            PurchaseOrderStatus.DRAFT,
            PurchaseOrderStatus.PENDING,
            PurchaseOrderStatus.APPROVED,
            PurchaseOrderStatus.SENT
        ]
    
    def get_completion_percentage(self) -> float:
        """Get order completion percentage based on received items"""
        if not self.items:
            return 0.0
        
        total_ordered = sum(item.quantity for item in self.items)
        total_received = sum(item.received_quantity for item in self.items)
        
        if total_ordered == 0:
            return 0.0
        
        return (total_received / total_ordered) * 100


class PurchaseOrderItem(SQLModel, table=True):
    """Purchase order item model for order line items"""
    __tablename__ = "purchase_order_items"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Foreign Keys
    purchase_order_id: uuid.UUID = Field(foreign_key="purchase_orders.id", index=True)
    item_id: uuid.UUID = Field(foreign_key="items.id", index=True)
    
    # Order Details
    quantity: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    unit_cost: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    total_cost: Decimal = Field(sa_column=Column(Numeric(12, 2)))
    
    # Receiving Information
    received_quantity: Decimal = Field(default=0, sa_column=Column(Numeric(10, 2)))
    remaining_quantity: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    
    # Additional Information
    description: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = Field(default=None, max_length=500)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    purchase_order: Optional["PurchaseOrder"] = Relationship(back_populates="items")
    item: Optional["Item"] = Relationship(back_populates="purchase_order_items")
    
    def calculate_total_cost(self):
        """Calculate total cost from quantity and unit cost"""
        self.total_cost = self.quantity * self.unit_cost
        self.remaining_quantity = self.quantity - self.received_quantity
    
    def is_fully_received(self) -> bool:
        """Check if item is fully received"""
        return self.received_quantity >= self.quantity
    
    def get_received_percentage(self) -> float:
        """Get percentage of item received"""
        if self.quantity == 0:
            return 0.0
        
        return (self.received_quantity / self.quantity) * 100