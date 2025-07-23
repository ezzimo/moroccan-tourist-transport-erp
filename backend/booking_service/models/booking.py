"""
Booking model for reservation management
"""

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric
from typing import Optional
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
import uuid


class BookingStatus(str, Enum):
    """Booking status enumeration"""

    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    REFUNDED = "Refunded"
    EXPIRED = "Expired"


class ServiceType(str, Enum):
    """Service type enumeration"""

    TOUR = "Tour"
    TRANSFER = "Transfer"
    CUSTOM_PACKAGE = "Custom Package"
    ACCOMMODATION = "Accommodation"
    ACTIVITY = "Activity"


class PaymentStatus(str, Enum):
    """Payment status enumeration"""

    PENDING = "Pending"
    PARTIAL = "Partial"
    PAID = "Paid"
    REFUNDED = "Refunded"
    FAILED = "Failed"


class Booking(SQLModel, table=True):
    """Booking model for managing customer reservations"""

    __tablename__ = "bookings"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )

    # Customer Information
    customer_id: Optional[uuid.UUID] = Field(
        index=True, default=None
    )  # Reference to CRM service

    # Booking Details
    service_type: Optional[ServiceType] = Field(index=True, default=None)
    status: BookingStatus = Field(default=BookingStatus.PENDING, index=True)

    # Passenger Information
    # Number of passengers
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
        default=0,
        sa_column=Column(Numeric(10, 2)),
    )
    total_price: Optional[Decimal] = Field(
        sa_column=Column(Numeric(10, 2)), default=None
    )
    currency: str = Field(default="MAD", max_length=3)

    # Payment
    payment_status: Optional[PaymentStatus] = Field(
        default=PaymentStatus.PENDING,
        index=True,
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
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
    )
    updated_at: Optional[datetime] = Field(default=None)
    confirmed_at: Optional[datetime] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)

    def calculate_total_price(self) -> Decimal:
        """Calculate total price including discounts"""
        return self.base_price - self.discount_amount

    def is_expired(self) -> bool:
        """Check if booking has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def can_be_cancelled(self) -> bool:
        """Check if booking can be cancelled"""
        return self.status in [BookingStatus.PENDING, BookingStatus.CONFIRMED]

    def get_duration_days(self) -> int:
        """Get booking duration in days"""
        if not self.end_date:
            return 1
        return (self.end_date - self.start_date).days + 1