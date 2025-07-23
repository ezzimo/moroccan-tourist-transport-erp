"""
Availability model for resource scheduling
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, date
from enum import Enum
import uuid


class ResourceType(str, Enum):
    """Resource type enumeration"""
    VEHICLE = "Vehicle"
    GUIDE = "Guide"
    ACCOMMODATION = "Accommodation"
    ACTIVITY = "Activity"


class AvailabilitySlot(SQLModel, table=True):
    """Availability slot model for resource scheduling"""
    __tablename__ = "availability_slots"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Resource Information
    resource_type: ResourceType = Field(index=True)
    resource_id: uuid.UUID = Field(index=True)  # Reference to external service
    resource_name: str = Field(max_length=255)
    
    # Availability Details
    date: date = Field(index=True)
    start_time: Optional[datetime] = Field(default=None)
    end_time: Optional[datetime] = Field(default=None)
    
    # Capacity
    total_capacity: int = Field(default=1, ge=1)
    available_capacity: int = Field(ge=0)
    reserved_capacity: int = Field(default=0, ge=0)
    
    # Booking Reference
    booking_id: Optional[uuid.UUID] = Field(default=None, foreign_key="bookings.id")
    
    # Status
    is_blocked: bool = Field(default=False)  # Manually blocked
    block_reason: Optional[str] = Field(default=None, max_length=255)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    def is_available(self, required_capacity: int = 1) -> bool:
        """Check if slot has available capacity"""
        return (
            not self.is_blocked and
            self.available_capacity >= required_capacity
        )
    
    def reserve_capacity(self, capacity: int, booking_id: uuid.UUID) -> bool:
        """Reserve capacity for a booking"""
        if not self.is_available(capacity):
            return False
        
        self.available_capacity -= capacity
        self.reserved_capacity += capacity
        self.booking_id = booking_id
        self.updated_at = datetime.utcnow()
        
        return True
    
    def release_capacity(self, capacity: int) -> bool:
        """Release reserved capacity"""
        if self.reserved_capacity < capacity:
            return False
        
        self.available_capacity += capacity
        self.reserved_capacity -= capacity
        self.updated_at = datetime.utcnow()
        
        return True