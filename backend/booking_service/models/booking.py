"""
Booking model for reservation management
"""
from __future__ import annotations
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Numeric
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timezone
from enum import Enum
from decimal import Decimal
import uuid
import json


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


class ItemType(str, Enum):
    """Reservation item type enumeration"""

    ACCOMMODATION = "Accommodation"
    TRANSPORT = "Transport"
    ACTIVITY = "Activity"
    GUIDE = "Guide"
    MEAL = "Meal"
    INSURANCE = "Insurance"


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

    # Relationships
    reservation_items: List["ReservationItem"] = Relationship(
        back_populates="booking",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "lazy": "select",
        },
    )

    def calculate_total_price(self) -> Decimal:
        """Calculate total price including discounts"""
        if not self.base_price:
            return Decimal(0)
        return self.base_price - (self.discount_amount or Decimal(0))

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
        if not self.start_date or not self.end_date:
            return 1
        return (self.end_date - self.start_date).days + 1


class ReservationItem(SQLModel, table=True):
    """Reservation item model for booking components"""

    __tablename__ = "reservation_items"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True,
    )

    # Foreign Keys
    booking_id: Optional[uuid.UUID] = Field(
        foreign_key="bookings.id", index=True, default=None
    )

    # Item Details
    type: Optional[ItemType] = Field(index=True, default=None)
    reference_id: Optional[uuid.UUID] = Field(
        default=None,
        index=True,
    )  # FK to external service
    name: Optional[str] = Field(max_length=255, default=None)
    description: Optional[str] = Field(default=None, max_length=1000)

    # Quantity and Pricing
    quantity: int = Field(default=1, ge=1)
    unit_price: Optional[Decimal] = Field(
        sa_column=Column(Numeric(10, 2)), default=None
    )
    total_price: Optional[Decimal] = Field(
        sa_column=Column(Numeric(10, 2)), default=None
    )

    # Additional Information
    specifications: Optional[str] = Field(
        default=None,
    )  # JSON string for item-specific data
    notes: Optional[str] = Field(default=None, max_length=500)

    # Status
    is_confirmed: bool = Field(default=False)
    is_cancelled: bool = Field(default=False)

    # Timestamps
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
    )
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    booking: Optional["Booking"] = Relationship(
        back_populates="reservation_items",
        sa_relationship_kwargs={"lazy": "select"},
    )

    def get_specifications_dict(self) -> dict:
        """Parse specifications from JSON string"""
        if not self.specifications:
            return {}
        try:
            import json
            return json.loads(self.specifications)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_specifications_dict(self, specs: dict):
        """Set specifications as JSON string"""
        import json
        self.specifications = json.dumps(specs) if specs else None


"""
Pricing rule model for dynamic pricing and discounts
"""


class DiscountType(str, Enum):
    """Discount type enumeration"""
    PERCENTAGE = "Percentage"
    FIXED_AMOUNT = "Fixed Amount"
    BUY_X_GET_Y = "Buy X Get Y"
    EARLY_BIRD = "Early Bird"
    GROUP_DISCOUNT = "Group Discount"


class PricingRule(SQLModel, table=True):
    """Pricing rule model for dynamic pricing and discounts"""
    __tablename__ = "pricing_rules"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )

    # Rule Information
    name: str = Field(unique=True, max_length=255, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    code: Optional[str] = Field(default=None, unique=True, max_length=50)  # Promo code

    # Rule Type and Value
    discount_type: DiscountType = Field(index=True)
    discount_percentage: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    discount_amount: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))

    # Conditions (stored as JSON)
    conditions: str = Field()  # JSON string containing rule conditions

    # Validity
    valid_from: date = Field(index=True)
    valid_until: date = Field(index=True)

    # Usage Limits
    max_uses: Optional[int] = Field(default=None)
    max_uses_per_customer: Optional[int] = Field(default=1)
    current_uses: int = Field(default=0)

    # Priority and Status
    priority: int = Field(default=0, index=True)  # Higher number = higher priority
    is_active: bool = Field(default=True, index=True)
    is_combinable: bool = Field(default=False)  # Can be combined with other rules

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    def get_conditions_dict(self) -> Dict[str, Any]:
        """Parse conditions from JSON string"""
        try:
            return json.loads(self.conditions)
        except:
            return {}

    def set_conditions_dict(self, conditions_dict: Dict[str, Any]):
        """Set conditions as JSON string"""
        self.conditions = json.dumps(conditions_dict)

    def is_valid_now(self) -> bool:
        """Check if rule is currently valid"""
        today = date.today()
        return (
            self.is_active and
            self.valid_from <= today <= self.valid_until and
            (self.max_uses is None or self.current_uses < self.max_uses)
        )

    def can_apply_to_booking(self, booking_data: dict) -> bool:
        """Check if rule can be applied to a booking"""
        if not self.is_valid_now():
            return False

        conditions = self.get_conditions_dict()

        # Check minimum passenger count
        if "min_pax" in conditions:
            if booking_data.get("pax_count", 0) < conditions["min_pax"]:
                return False

        # Check service type
        if "service_types" in conditions:
            if booking_data.get("service_type") not in conditions["service_types"]:
                return False

        # Check booking value
        if "min_booking_value" in conditions:
            if booking_data.get("base_price", 0) < conditions["min_booking_value"]:
                return False

        # Check advance booking days
        if "min_advance_days" in conditions:
            booking_date = booking_data.get("start_date")
            if booking_date:
                from datetime import datetime
                if isinstance(booking_date, str):
                    booking_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
                days_advance = (booking_date - date.today()).days
                if days_advance < conditions["min_advance_days"]:
                    return False

        return True

    def calculate_discount(self, base_price: Decimal, pax_count: int = 1) -> Decimal:
        """Calculate discount amount for given base price"""
        if self.discount_type == DiscountType.PERCENTAGE:
            if self.discount_percentage:
                return base_price * (self.discount_percentage / 100)

        elif self.discount_type == DiscountType.FIXED_AMOUNT:
            if self.discount_amount:
                return self.discount_amount

        elif self.discount_type == DiscountType.GROUP_DISCOUNT:
            conditions = self.get_conditions_dict()
            group_threshold = conditions.get("group_threshold", 10)
            if pax_count >= group_threshold and self.discount_percentage:
                return base_price * (self.discount_percentage / 100)

        return Decimal(0)


"""
Availability model for resource scheduling
"""


class ResourceType(str, Enum):
    """Resource type enumeration"""
    VEHICLE = "Vehicle"
    GUIDE = "Guide"
    ACCOMMODATION = "Accommodation"
    ACTIVITY = "Activity"


class AvailabilitySlot(SQLModel, table=True):
    """Availability slot model for resource scheduling"""
    __tablename__ = "availability_slots"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    # Resource Information
    resource_type: ResourceType = Field(index=True)
    # Reference to external service
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

    # Booking Reference
    booking_id: Optional[uuid.UUID] = Field(default=None, foreign_key="bookings.id")

    # Status
    is_blocked: bool = Field(default=False)  # Manually blocked
    block_reason: Optional[str] = Field(default=None, max_length=255)

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
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
        self.updated_at = datetime.now(timezone.utc)

        return True

    def release_capacity(self, capacity: int) -> bool:
        """Release reserved capacity"""
        if self.reserved_capacity < capacity:
            return False

        self.available_capacity += capacity
        self.reserved_capacity -= capacity
        self.updated_at = datetime.now(timezone.utc)

        return True
