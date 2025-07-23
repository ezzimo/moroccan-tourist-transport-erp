"""
Booking-related Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from models.booking import BookingStatus, ServiceType, PaymentStatus
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
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v
    
    @validator('pax_count')
    def validate_pax_count(cls, v):
        if v < 1 or v > 50:
            raise ValueError('Passenger count must be between 1 and 50')
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