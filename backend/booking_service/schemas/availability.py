"""
Availability-related Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from models.availability import ResourceType
import uuid


class AvailabilityRequest(BaseModel):
    """Schema for availability check request"""
    resource_type: Optional[ResourceType] = None
    resource_ids: Optional[List[uuid.UUID]] = None
    start_date: date
    end_date: Optional[date] = None
    required_capacity: int = 1
    service_type: Optional[str] = None


class ResourceAvailability(BaseModel):
    """Schema for individual resource availability"""
    resource_id: uuid.UUID
    resource_name: str
    resource_type: ResourceType
    date: date
    total_capacity: int
    available_capacity: int
    is_available: bool
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class AvailabilityResponse(BaseModel):
    """Schema for availability check response"""
    request_date: date
    end_date: Optional[date]
    required_capacity: int
    available_resources: List[ResourceAvailability] = []
    total_available: int = 0
    has_availability: bool = False


class AvailabilitySlotCreate(BaseModel):
    """Schema for creating availability slots"""
    resource_type: ResourceType
    resource_id: uuid.UUID
    resource_name: str
    date: date
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_capacity: int = 1
    is_blocked: bool = False
    block_reason: Optional[str] = None


class AvailabilitySlotUpdate(BaseModel):
    """Schema for updating availability slots"""
    total_capacity: Optional[int] = None
    available_capacity: Optional[int] = None
    is_blocked: Optional[bool] = None
    block_reason: Optional[str] = None


class AvailabilitySlotResponse(BaseModel):
    """Schema for availability slot response"""
    id: uuid.UUID
    resource_type: ResourceType
    resource_id: uuid.UUID
    resource_name: str
    date: date
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    total_capacity: int
    available_capacity: int
    reserved_capacity: int
    booking_id: Optional[uuid.UUID]
    is_blocked: bool
    block_reason: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]