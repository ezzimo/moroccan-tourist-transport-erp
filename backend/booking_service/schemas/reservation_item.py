"""
Reservation item-related Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from models.reservation_item import ItemType
import uuid


class ReservationItemBase(BaseModel):
    type: ItemType
    reference_id: Optional[uuid.UUID] = None
    name: str
    description: Optional[str] = None
    quantity: int = 1
    unit_price: Decimal
    specifications: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class ReservationItemCreate(ReservationItemBase):
    booking_id: uuid.UUID


class ReservationItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None
    specifications: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    is_confirmed: Optional[bool] = None
    is_cancelled: Optional[bool] = None


class ReservationItemResponse(ReservationItemBase):
    id: uuid.UUID
    booking_id: uuid.UUID
    total_price: Decimal
    is_confirmed: bool
    is_cancelled: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    @classmethod
    def from_model(cls, item):
        """Create response from database model"""
        return cls(
            id=item.id,
            booking_id=item.booking_id,
            type=item.type,
            reference_id=item.reference_id,
            name=item.name,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.total_price,
            specifications=item.get_specifications_dict(),
            notes=item.notes,
            is_confirmed=item.is_confirmed,
            is_cancelled=item.is_cancelled,
            created_at=item.created_at,
            updated_at=item.updated_at
        )