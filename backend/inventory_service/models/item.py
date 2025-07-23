"""
Item model for inventory management
"""
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Numeric
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
import uuid


class ItemCategory(str, Enum):
    """Item category enumeration"""
    ENGINE_PARTS = "Engine Parts"
    TIRES = "Tires"
    FLUIDS = "Fluids"
    ELECTRICAL = "Electrical"
    BODY_PARTS = "Body Parts"
    TOOLS = "Tools"
    OFFICE_SUPPLIES = "Office Supplies"
    CLEANING_SUPPLIES = "Cleaning Supplies"
    SAFETY_EQUIPMENT = "Safety Equipment"
    CONSUMABLES = "Consumables"
    OTHER = "Other"


class ItemUnit(str, Enum):
    """Item unit enumeration"""
    PIECE = "Piece"
    LITER = "Liter"
    KILOGRAM = "Kilogram"
    METER = "Meter"
    BOX = "Box"
    PACK = "Pack"
    SET = "Set"
    GALLON = "Gallon"
    BOTTLE = "Bottle"
    ROLL = "Roll"


class ItemStatus(str, Enum):
    """Item status enumeration"""
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    DISCONTINUED = "Discontinued"


class Item(SQLModel, table=True):
    """Item model for inventory management"""
    __tablename__ = "items"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Basic Information
    name: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    sku: str = Field(unique=True, max_length=50, index=True)  # Stock Keeping Unit
    barcode: Optional[str] = Field(default=None, max_length=50, index=True)
    
    # Classification
    category: ItemCategory = Field(index=True)
    subcategory: Optional[str] = Field(default=None, max_length=100)
    brand: Optional[str] = Field(default=None, max_length=100)
    model: Optional[str] = Field(default=None, max_length=100)
    
    # Unit and Pricing
    unit: ItemUnit = Field(index=True)
    unit_cost: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    currency: str = Field(default="MAD", max_length=3)
    
    # Stock Information
    current_quantity: Decimal = Field(default=0, sa_column=Column(Numeric(10, 2)))
    reserved_quantity: Decimal = Field(default=0, sa_column=Column(Numeric(10, 2)))
    reorder_level: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    max_stock_level: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    
    # Location
    warehouse_location: str = Field(default="Main Warehouse", max_length=100)
    bin_location: Optional[str] = Field(default=None, max_length=50)
    
    # Supplier Information
    primary_supplier_id: Optional[uuid.UUID] = Field(default=None, foreign_key="suppliers.id")
    
    # Tracking
    last_purchase_date: Optional[date] = Field(default=None)
    last_purchase_cost: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    average_cost: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    
    # Expiry and Maintenance
    has_expiry: bool = Field(default=False)
    expiry_date: Optional[date] = Field(default=None)
    shelf_life_days: Optional[int] = Field(default=None)
    
    # Status and Metadata
    status: ItemStatus = Field(default=ItemStatus.ACTIVE, index=True)
    is_critical: bool = Field(default=False)  # Critical for operations
    notes: Optional[str] = Field(default=None, max_length=1000)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    supplier: Optional["Supplier"] = Relationship(back_populates="items")
    stock_movements: List["StockMovement"] = Relationship(back_populates="item")
    purchase_order_items: List["PurchaseOrderItem"] = Relationship(back_populates="item")
    
    def get_available_quantity(self) -> Decimal:
        """Get available quantity (current - reserved)"""
        return self.current_quantity - self.reserved_quantity
    
    def is_low_stock(self) -> bool:
        """Check if item is below reorder level"""
        return self.current_quantity <= self.reorder_level
    
    def is_out_of_stock(self) -> bool:
        """Check if item is out of stock"""
        return self.current_quantity <= 0
    
    def get_stock_value(self) -> Decimal:
        """Calculate total stock value"""
        return self.current_quantity * self.unit_cost
    
    def is_expired(self) -> bool:
        """Check if item has expired"""
        if not self.has_expiry or not self.expiry_date:
            return False
        return date.today() > self.expiry_date
    
    def days_until_expiry(self) -> Optional[int]:
        """Get days until expiry"""
        if not self.has_expiry or not self.expiry_date:
            return None
        return (self.expiry_date - date.today()).days
    
    def update_average_cost(self, new_cost: Decimal, quantity: Decimal):
        """Update average cost using weighted average"""
        if self.current_quantity > 0:
            total_value = (self.current_quantity * self.average_cost) + (quantity * new_cost)
            total_quantity = self.current_quantity + quantity
            self.average_cost = total_value / total_quantity
        else:
            self.average_cost = new_cost