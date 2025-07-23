"""
Booking model for reservation management
"""

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Numeric
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .reservation_item import ReservationItem


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
    customer_id: uuid.UUID = Field(index=True)  # Reference to CRM service

    # Booking Details
    service_type: ServiceType = Field(index=True)
    status: BookingStatus = Field(default=BookingStatus.PENDING, index=True)

    # Passenger Information
    pax_count: int = Field(ge=1, le=50)  # Number of passengers
    lead_passenger_name: str = Field(max_length=255)
    lead_passenger_email: str = Field(max_length=255)
    lead_passenger_phone: str = Field(max_length=20)

    # Dates and Duration
    start_date: date = Field(index=True)
    end_date: Optional[date] = Field(default=None, index=True)

    # Pricing
    base_price: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    discount_amount: Decimal = Field(
        default=0,
        sa_column=Column(Numeric(10, 2)),
    )
    total_price: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    currency: str = Field(default="MAD", max_length=3)

    # Payment
    payment_status: PaymentStatus = Field(
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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    confirmed_at: Optional[datetime] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)

    # Relationships
    reservation_items: List["ReservationItem"] = Relationship(
        back_populates="booking",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
        repr=False,
    )

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
