"""
Segment-related Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


class SegmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    criteria: Dict[str, Any]


class SegmentCreate(SegmentBase):
    pass


class SegmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    criteria: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class SegmentResponse(SegmentBase):
    id: uuid.UUID
    is_active: bool
    customer_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    last_calculated: Optional[datetime]


class SegmentWithCustomers(SegmentResponse):
    """Segment response with customer list"""
    customers: List["CustomerResponse"] = []


# Import here to avoid circular imports
from .customer import CustomerResponse
SegmentWithCustomers.model_rebuild()