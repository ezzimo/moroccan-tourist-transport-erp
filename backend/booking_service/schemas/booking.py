"""
Booking-related Pydantic schemas for the Booking Service.

Defines the data transfer objects (DTOs) for creating, reading,
and confirming bookings, ensuring type safety and validation.
"""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator, model_validator
from sqlmodel import SQLModel, Field

from backend.booking_service.models.enums import (
    BookingStatus,
    ServiceType,
    PaymentStatus,
    ItemType,
    ResourceType,
    DiscountType,
)


# Phase 1 Schemas (BK-006)

class BookingCreate(SQLModel):
    """
    Create request for a booking.

    `customer_id` is validated against the Customer Relationship Management (CRM)
    service in the service layer. This linkage is handled by `clients/customer_client.py`.
    """
    # Core booking details
    customer_id: UUID
    service_type: ServiceType
    booking_source: str = "web"

    # Trip details
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    pax_count: Optional[int] = Field(default=None, ge=1, le=50)
    vehicle_type_requested: Optional[str] = Field(default=None, max_length=100)

    # Location details
    pickup_location_text: Optional[str] = Field(default=None, max_length=500)
    pickup_location_coords: Optional[Dict[str, Any]] = None
    dropoff_location_text: Optional[str] = Field(default=None, max_length=500)
    dropoff_location_coords: Optional[Dict[str, Any]] = None

    # Passenger details
    lead_passenger_name: Optional[str] = None
    lead_passenger_email: Optional[EmailStr] = None
    lead_passenger_phone: Optional[str] = None

    # Operational details
    agent_id: Optional[UUID] = None
    price_snapshot: Optional[Dict[str, Any]] = None
    payment_provider: Optional[str] = Field(default=None, max_length=50)

    @field_validator("pickup_location_coords", "dropoff_location_coords")
    @classmethod
    def _check_coords(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate that coordinate dictionaries contain valid lat/lng values."""
        if v is None:
            return v
        lat = v.get("lat")
        lng = v.get("lng")
        if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
            raise ValueError("Coordinates require numeric 'lat' and 'lng' values.")
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            raise ValueError("Coordinate values are out of valid geographical range.")
        return v

    @model_validator(mode="after")
    def _check_times(self) -> "BookingCreate":
        """Ensure that if both start and end times are provided, start_time precedes end_time."""
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValueError("start_time must be earlier than end_time.")
        return self


class BookingResponse(SQLModel):
    """
    Standard response model for a booking, returning all core fields.
    """
    id: UUID
    status: BookingStatus
    customer_id: UUID
    service_type: ServiceType

    # Trip details
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    pax_count: Optional[int] = None
    vehicle_type_requested: Optional[str] = None
    vehicle_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None

    # Location details
    pickup_location_text: Optional[str] = None
    pickup_location_coords: Optional[Dict[str, Any]] = None
    dropoff_location_text: Optional[str] = None
    dropoff_location_coords: Optional[Dict[str, Any]] = None

    # Estimates
    estimated_duration_minutes: Optional[int] = None
    estimated_distance_km: Optional[float] = None

    # Passenger details
    lead_passenger_name: Optional[str] = None
    lead_passenger_email: Optional[EmailStr] = None
    lead_passenger_phone: Optional[str] = None

    # Pricing and Payment
    base_price: Optional[Decimal] = None
    discount_amount: Decimal
    total_price: Optional[Decimal] = None
    currency: str
    price_snapshot: Optional[Dict[str, Any]] = None
    payment_status: PaymentStatus
    payment_provider: Optional[str] = None
    payment_reference: Optional[str] = None

    # Operational details
    booking_source: str
    agent_id: Optional[UUID] = None
    internal_notes: Optional[str] = None

    # Timestamps & Status
    created_at: datetime
    updated_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    cancelled_by: Optional[UUID] = None


class BookingConfirmPayload(SQLModel):
    """
    Payload required to confirm a pending booking.
    Typically used after a successful payment or manual verification.
    """
    payment_reference: str
    vehicle_id: UUID
    driver_id: UUID
    internal_notes: Optional[str] = None
    payment_amount: Optional[Decimal] = None  # Optional, for cross-checking payment


class BookingConfirmationResponse(SQLModel):
    """
    Response sent after a booking is successfully confirmed.
    """
    booking_id: UUID
    status: BookingStatus
    confirmed_at: datetime
    vehicle_id: UUID
    driver_id: UUID
    payment_status: PaymentStatus
    notification_status: str  # e.g., "SENT", "FAILED", "PENDING"


# --- Legacy / Other Schemas ---
# Note: These may need updates in subsequent tickets.

class BookingUpdate(BaseModel):
    pax_count: Optional[int] = None
    lead_passenger_name: Optional[str] = None
    lead_passenger_email: Optional[EmailStr] = None
    lead_passenger_phone: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    special_requests: Optional[str] = None
    internal_notes: Optional[str] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None


class BookingSearch(BaseModel):
    """Schema for booking search criteria"""
    customer_id: Optional[uuid.UUID] = None
    status: Optional[BookingStatus] = None
    service_type: Optional[ServiceType] = None
    payment_status: Optional[PaymentStatus] = None
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    lead_passenger_name: Optional[str] = None
    lead_passenger_email: Optional[str] = None


"""
Reservation item-related Pydantic schemas
"""


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


"""
Availability-related Pydantic schemas
"""


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


"""
Pricing rule-related Pydantic schemas
"""


class PricingRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    code: Optional[str] = None
    discount_type: DiscountType
    discount_percentage: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    conditions: Dict[str, Any]
    valid_from: date
    valid_until: date
    max_uses: Optional[int] = None
    max_uses_per_customer: int = 1
    priority: int = 0
    is_combinable: bool = False

    @field_validator('discount_percentage')
    @classmethod
    def validate_percentage(cls, v, values):
        discount_type = (
            values.data.get('discount_type')
            if hasattr(values, "data")
            else values.get('discount_type')
        )
        if (
            discount_type == DiscountType.PERCENTAGE
            and (not v or v <= 0 or v > 100)
        ):
            raise ValueError('Discount percentage must be between 0 and 100')
        return v

    @field_validator('discount_amount')
    @classmethod
    def validate_amount(cls, v, values):
        discount_type = (
            values.data.get('discount_type')
            if hasattr(values, "data")
            else values.get('discount_type')
        )
        if discount_type == DiscountType.FIXED_AMOUNT and (not v or v <= 0):
            raise ValueError('Discount amount must be greater than 0')
        return v

    @field_validator('valid_until')
    @classmethod
    def validate_dates(cls, v, values):
        valid_from = (
            values.data.get('valid_from')
            if hasattr(values, "data")
            else values.get('valid_from')
        )
        if valid_from and v <= valid_from:
            raise ValueError('Valid until date must be after valid from date')
        return v


class PricingRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    discount_percentage: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    conditions: Optional[Dict[str, Any]] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    max_uses: Optional[int] = None
    max_uses_per_customer: Optional[int] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    is_combinable: Optional[bool] = None


class PricingRuleResponse(PricingRuleBase):
    id: uuid.UUID
    current_uses: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]


class PricingRequest(BaseModel):
    """Schema for pricing calculation request"""
    service_type: str
    base_price: Decimal
    pax_count: int
    start_date: date
    end_date: Optional[date] = None
    customer_id: Optional[uuid.UUID] = None
    promo_code: Optional[str] = None


class PricingResponse(BaseModel):
    """Schema for pricing calculation response"""
    base_price: Decimal
    discount_amount: Decimal
    total_price: Decimal
    applied_rules: List[Dict[str, Any]] = []
    currency: str = "MAD"
