"""
Booking-related Pydantic schemas
"""

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from models.enums import (
    BookingStatus,
    ServiceType,
    PaymentStatus,
    ItemType,
    ResourceType,
    DiscountType,
)
import uuid


class BookingBase(BaseModel):
    customer_id: uuid.UUID
    service_type: ServiceType
    pax_count: int
    lead_passenger_name: str
    lead_passenger_email: EmailStr
    lead_passenger_phone: str
    start_date: date
    end_date: Optional[date] = None
    special_requests: Optional[str] = None


class BookingCreate(BookingBase):
    base_price: Decimal
    promo_code: Optional[str] = None
    payment_method: Optional[str] = None

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v, values):
        start_date = (
            values.data.get("start_date")
            if hasattr(values, "data")
            else values.get("start_date")
        )
        if v and start_date and v < start_date:
            raise ValueError("End date must be after start date")
        return v

    @field_validator("pax_count")
    @classmethod
    def validate_pax_count(cls, v):
        if v < 1 or v > 50:
            raise ValueError("Passenger count must be between 1 and 50")
        return v


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


class BookingResponse(BookingBase):
    id: uuid.UUID
    status: BookingStatus
    base_price: Decimal
    discount_amount: Decimal
    total_price: Decimal
    currency: str
    payment_status: PaymentStatus
    payment_method: Optional[str]
    payment_reference: Optional[str]
    internal_notes: Optional[str]
    cancellation_reason: Optional[str]
    cancelled_by: Optional[uuid.UUID]
    cancelled_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    confirmed_at: Optional[datetime]
    expires_at: Optional[datetime]


class BookingSummary(BookingResponse):
    """Extended booking response with summary information"""

    reservation_items_count: int = 0
    duration_days: int = 1
    is_expired: bool = False
    can_be_cancelled: bool = True
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None


class BookingConfirm(BaseModel):
    """Schema for booking confirmation"""

    payment_reference: Optional[str] = None
    internal_notes: Optional[str] = None


class BookingCancel(BaseModel):
    """Schema for booking cancellation"""

    reason: str
    refund_amount: Optional[Decimal] = None
    internal_notes: Optional[str] = None


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
