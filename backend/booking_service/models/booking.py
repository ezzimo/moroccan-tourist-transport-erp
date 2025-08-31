"""
Booking model for reservation management (parent in 1:N with ReservationItem).
"""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
import uuid

from sqlalchemy import Column, Numeric
from sqlalchemy.orm import relationship  # << explicit SA relationship
from sqlmodel import SQLModel, Field, Relationship

from .enums import BookingStatus, ServiceType, PaymentStatus

# Only for type-checkers; avoids runtime circular import at import time
if TYPE_CHECKING:
    from .reservation_item import ReservationItem


class Booking(SQLModel, table=True):
    """Booking model for managing customer reservations."""

    __tablename__ = "bookings"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Customer Information
    customer_id: Optional[uuid.UUID] = Field(index=True, default=None)

    # Booking Details
    service_type: Optional[ServiceType] = Field(index=True, default=None)
    status: BookingStatus = Field(default=BookingStatus.PENDING, index=True)

    # Passenger Information
    pax_count: Optional[int] = Field(ge=1, le=50, default=None)
    lead_passenger_name: Optional[str] = Field(max_length=255, default=None)
    lead_passenger_email: Optional[str] = Field(max_length=255, default=None)
    lead_passenger_phone: Optional[str] = Field(max_length=20, default=None)

    # Dates and Duration
    start_date: Optional[date] = Field(index=True, default=None)
    end_date: Optional[date] = Field(default=None, index=True)

    # Pricing
    base_price: Optional[Decimal] = Field(
        sa_column=Column(Numeric(10, 2)), default=None
    )
    discount_amount: Optional[Decimal] = Field(
        default=Decimal(0), sa_column=Column(Numeric(10, 2))
    )
    total_price: Optional[Decimal] = Field(
        sa_column=Column(Numeric(10, 2)), default=None
    )
    currency: str = Field(default="MAD", max_length=3)

    # Payment
    payment_status: Optional[PaymentStatus] = Field(
        default=PaymentStatus.PENDING, index=True
    )
    payment_method: Optional[str] = Field(default=None, max_length=50)
    payment_reference: Optional[str] = Field(default=None, max_length=100)

    # Additional Information
    special_requests: Optional[str] = Field(default=None, max_length=2000)
    internal_notes: Optional[str] = Field(default=None, max_length=2000)

    # Cancellation
    cancellation_reason: Optional[str] = Field(default=None, max_length=500)
    cancelled_by: Optional[uuid.UUID] = Field(default=None)
    cancelled_at: Optional[datetime] = Field(default=None)

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    confirmed_at: Optional[datetime] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)

    # ONE -> MANY: give SQLAlchemy a concrete target via sa_relationship
    reservation_items: list["ReservationItem"] = Relationship(
        sa_relationship=relationship(
            "ReservationItem",
            back_populates="booking",
            cascade="all, delete-orphan",
            single_parent=True,
            passive_deletes=True,
            lazy="selectin",
            order_by="ReservationItem.created_at",
        )
    )

    # ---------- Business logic ----------
    def calculate_total_price(self) -> Decimal:
        if not self.base_price:
            return Decimal(0)
        return self.base_price - (self.discount_amount or Decimal(0))

    def is_expired(self) -> bool:
        return bool(self.expires_at and datetime.utcnow() > self.expires_at)

    def can_be_cancelled(self) -> bool:
        return self.status in (BookingStatus.PENDING, BookingStatus.CONFIRMED)

    def get_duration_days(self) -> int:
        if not self.start_date or not self.end_date:
            return 1
        return (self.end_date - self.start_date).days + 1
