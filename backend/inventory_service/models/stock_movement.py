"""
Stock movement model for tracking inventory changes
"""
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Numeric
from typing import Optional
from datetime import datetime
from enum import Enum
from decimal import Decimal
import uuid


class MovementType(str, Enum):
    """Stock movement type enumeration"""
    IN = "IN"           # Stock received
    OUT = "OUT"         # Stock issued/used
    ADJUST = "ADJUST"   # Stock adjustment
    TRANSFER = "TRANSFER"  # Transfer between locations
    RETURN = "RETURN"   # Return to stock
    DAMAGE = "DAMAGE"   # Damaged/lost stock
    EXPIRED = "EXPIRED" # Expired stock removal


class MovementReason(str, Enum):
    """Movement reason enumeration"""
    PURCHASE = "Purchase"
    MAINTENANCE = "Maintenance"
    REPAIR = "Repair"
    OFFICE_USE = "Office Use"
    ADJUSTMENT = "Adjustment"
    TRANSFER = "Transfer"
    RETURN = "Return"
    DAMAGE = "Damage"
    EXPIRY = "Expiry"
    THEFT = "Theft"
    INITIAL_STOCK = "Initial Stock"
    OTHER = "Other"


class StockMovement(SQLModel, table=True):
    """Stock movement model for tracking inventory changes"""
    __tablename__ = "stock_movements"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Foreign Keys
    item_id: uuid.UUID = Field(foreign_key="items.id", index=True)
    
    # Movement Details
    movement_type: MovementType = Field(index=True)
    reason: MovementReason = Field(index=True)
    quantity: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    unit_cost: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    total_cost: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    
    # Reference Information
    reference_type: Optional[str] = Field(default=None, max_length=50)  # PO, Maintenance, etc.
    reference_id: Optional[str] = Field(default=None, max_length=100)
    reference_number: Optional[str] = Field(default=None, max_length=100)
    
    # Location Information
    from_location: Optional[str] = Field(default=None, max_length=100)
    to_location: Optional[str] = Field(default=None, max_length=100)
    
    # Stock Levels (after movement)
    quantity_before: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    quantity_after: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    
    # Additional Information
    notes: Optional[str] = Field(default=None, max_length=1000)
    batch_number: Optional[str] = Field(default=None, max_length=50)
    expiry_date: Optional[datetime] = Field(default=None)
    
    # Audit Information
    performed_by: uuid.UUID = Field(index=True)  # User who performed the movement
    approved_by: Optional[uuid.UUID] = Field(default=None)  # User who approved (if required)
    
    # Timestamps
    movement_date: datetime = Field(default_factory=datetime.utcnow, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    item: Optional["Item"] = Relationship(back_populates="stock_movements")
    
    def calculate_total_cost(self):
        """Calculate total cost from quantity and unit cost"""
        if self.unit_cost:
            self.total_cost = self.quantity * self.unit_cost
    
    def is_inbound(self) -> bool:
        """Check if movement increases stock"""
        return self.movement_type in [MovementType.IN, MovementType.RETURN, MovementType.ADJUST]
    
    def is_outbound(self) -> bool:
        """Check if movement decreases stock"""
        return self.movement_type in [MovementType.OUT, MovementType.DAMAGE, MovementType.EXPIRED]
    
    def get_quantity_change(self) -> Decimal:
        """Get the quantity change (positive for IN, negative for OUT)"""
        if self.is_inbound():
            return self.quantity
        elif self.is_outbound():
            return -self.quantity
        else:  # TRANSFER or other neutral movements
            return Decimal(0)