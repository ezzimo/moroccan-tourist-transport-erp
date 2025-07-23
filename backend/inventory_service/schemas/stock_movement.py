"""
Stock movement-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Any, Dict, List, Optional
from datetime import datetime
from decimal import Decimal
from models.stock_movement import MovementType, MovementReason
import uuid


class StockMovementBase(BaseModel):
    item_id: uuid.UUID
    movement_type: MovementType
    reason: MovementReason
    quantity: Decimal
    unit_cost: Optional[Decimal] = None
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    reference_number: Optional[str] = None
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    notes: Optional[str] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[datetime] = None


class StockMovementCreate(StockMovementBase):
    performed_by: uuid.UUID
    movement_date: Optional[datetime] = None
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v
    
    @validator('unit_cost')
    def validate_unit_cost(cls, v):
        if v is not None and v < 0:
            raise ValueError('Unit cost cannot be negative')
        return v


class StockMovementUpdate(BaseModel):
    notes: Optional[str] = None
    approved_by: Optional[uuid.UUID] = None


class StockMovementResponse(StockMovementBase):
    id: uuid.UUID
    total_cost: Optional[Decimal]
    quantity_before: Decimal
    quantity_after: Decimal
    performed_by: uuid.UUID
    approved_by: Optional[uuid.UUID]
    movement_date: datetime
    created_at: datetime
    item_name: str
    item_sku: str


class StockMovementSummary(BaseModel):
    """Stock movement summary"""
    total_movements: int
    by_type: Dict[str, int]
    by_reason: Dict[str, int]
    total_value_in: Decimal
    total_value_out: Decimal
    net_value_change: Decimal
    most_active_items: List[Dict[str, Any]]


class StockMovementSearch(BaseModel):
    """Stock movement search criteria"""
    item_id: Optional[uuid.UUID] = None
    movement_type: Optional[MovementType] = None
    reason: Optional[MovementReason] = None
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    performed_by: Optional[uuid.UUID] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class BulkStockMovement(BaseModel):
    """Schema for bulk stock movements"""
    movements: List[StockMovementCreate]
    
    @validator('movements')
    def validate_movements(cls, v):
        if not v:
            raise ValueError('At least one movement is required')
        return v