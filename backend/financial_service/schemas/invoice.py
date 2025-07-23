"""
Invoice-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from models.invoice import InvoiceStatus, PaymentStatus
import uuid


class InvoiceItemCreate(BaseModel):
    description: str
    quantity: Decimal = Decimal("1.0")
    unit_price: Decimal
    tax_rate: float = 20.0
    item_code: Optional[str] = None
    category: Optional[str] = None


class InvoiceItemResponse(BaseModel):
    id: uuid.UUID
    description: str
    quantity: Decimal
    unit_price: Decimal
    total_amount: Decimal
    tax_rate: float
    tax_amount: Decimal
    item_code: Optional[str]
    category: Optional[str]


class InvoiceBase(BaseModel):
    booking_id: Optional[uuid.UUID] = None
    customer_id: uuid.UUID
    customer_name: str
    customer_email: str
    customer_address: Optional[str] = None
    customer_tax_id: Optional[str] = None
    currency: str = "MAD"
    tax_rate: float = 20.0
    tax_inclusive: bool = True
    payment_terms: str = "Net 30"
    description: Optional[str] = None
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate]
    due_date: Optional[date] = None
    discount_amount: Decimal = Decimal("0.0")
    
    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('Invoice must have at least one item')
        return v
    
    @validator('currency')
    def validate_currency(cls, v):
        allowed_currencies = ["MAD", "EUR", "USD"]
        if v not in allowed_currencies:
            raise ValueError(f'Currency must be one of {allowed_currencies}')
        return v


class InvoiceUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_address: Optional[str] = None
    customer_tax_id: Optional[str] = None
    status: Optional[InvoiceStatus] = None
    payment_status: Optional[PaymentStatus] = None
    due_date: Optional[date] = None
    payment_terms: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    discount_amount: Optional[Decimal] = None


class InvoiceResponse(InvoiceBase):
    id: uuid.UUID
    invoice_number: str
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    status: InvoiceStatus
    payment_status: PaymentStatus
    issue_date: date
    due_date: date
    sent_date: Optional[date]
    paid_date: Optional[date]
    payment_method: Optional[str]
    created_by: Optional[uuid.UUID]
    approved_by: Optional[uuid.UUID]
    created_at: datetime
    updated_at: Optional[datetime]
    items: List[InvoiceItemResponse] = []
    paid_amount: Decimal
    outstanding_amount: Decimal
    is_overdue: bool
    days_overdue: int


class InvoiceSummary(BaseModel):
    """Invoice summary for dashboard"""
    total_invoices: int
    total_amount: Decimal
    paid_amount: Decimal
    outstanding_amount: Decimal
    overdue_amount: Decimal
    by_status: Dict[str, int]
    by_currency: Dict[str, Decimal]
    average_payment_days: Optional[float]


class InvoiceSearch(BaseModel):
    """Invoice search criteria"""
    query: Optional[str] = None
    customer_id: Optional[uuid.UUID] = None
    booking_id: Optional[uuid.UUID] = None
    status: Optional[InvoiceStatus] = None
    payment_status: Optional[PaymentStatus] = None
    currency: Optional[str] = None
    issue_date_from: Optional[date] = None
    issue_date_to: Optional[date] = None
    due_date_from: Optional[date] = None
    due_date_to: Optional[date] = None
    amount_min: Optional[Decimal] = None
    amount_max: Optional[Decimal] = None
    is_overdue: Optional[bool] = None


class InvoiceGeneration(BaseModel):
    """Schema for generating invoice from booking"""
    booking_id: uuid.UUID
    due_date: Optional[date] = None
    payment_terms: Optional[str] = "Net 30"
    notes: Optional[str] = None
    send_immediately: bool = False