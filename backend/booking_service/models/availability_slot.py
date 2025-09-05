"""
Availability model for resource scheduling.
"""

from __future__ import annotations

from datetime import datetime, date, timezone
from typing import Optional
import uuid

from sqlmodel import SQLModel, Field

from .enums import ResourceType


class AvailabilitySlot(SQLModel, table=True):
    """Availability slot model for resource scheduling"""

    __tablename__ = "availability_slots"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )

    # Resource Information
    resource_type: ResourceType = Field(index=True)
    resource_id: uuid.UUID = Field(index=True)
    resource_name: str = Field(max_length=255)

    # Availability Details
    slot_date: date = Field(index=True)
    start_time: Optional[datetime] = Field(default=None)
    end_time: Optional[datetime] = Field(default=None)

    # Capacity
    total_capacity: int = Field(default=1, ge=1)
    available_capacity: int = Field(default=1, ge=0)
    reserved_capacity: int = Field(default=0, ge=0)

    # Booking Reference (kept as explicit FK via string in your routers/
    # migrations)
    # The foreign key is referenced as a string for compatibility with routers
    # and migrations.
    booking_id: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="bookings.id",
    )

    # Status
    is_blocked: bool = Field(default=False)
    block_reason: Optional[str] = Field(default=None, max_length=255)

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: Optional[datetime] = Field(default=None)

    def is_available(self, required_capacity: int = 1) -> bool:
        return (
            not self.is_blocked
            and self.available_capacity >= required_capacity
        )

    def reserve_capacity(self, capacity: int, booking_id: uuid.UUID) -> bool:
        if not self.is_available(capacity):
            return False
        self.available_capacity -= capacity
        self.reserved_capacity += capacity
        self.booking_id = booking_id
        self.updated_at = datetime.now(timezone.utc)
        return True

    def release_capacity(self, capacity: int) -> bool:
        if self.reserved_capacity < capacity:
            return False
        self.available_capacity += capacity
        self.reserved_capacity -= capacity
        self.updated_at = datetime.now(timezone.utc)
        return True
