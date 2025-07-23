"""
Payment-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from models.payment import PaymentMethod, PaymentStatus
import uuid


class PaymentBase(BaseModel):
    invoice_id: uuid.UUID
    amount: Decimal
    currency: str = "MAD"
    payment_method: PaymentMethod
    payment_date: date
    reference_number: Optional[str] = None
    transaction_id: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    card_last_four: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class PaymentCreate(PaymentBase):
    exchange_rate: Optional[Decimal] = None
    processing_fee: Optional[Decimal] = Decimal("0.0")
    gateway_fee: Optional[Decimal] = Decimal("0.0")
    receipt_url: Optional[str] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Payment amount must be greater than 0')
        return v
    
    @validator('currency')
    def validate_currency(cls, v):
        allowed_currencies = ["MAD", "EUR", "USD"]
        if v not in allowed_currencies:
            raise ValueError(f'Currency must be one of {allowed_currencies}')
        return v


class PaymentUpdate(BaseModel):
    amount: Optional[Decimal] = None
    payment_date: Optional[date] = None
    reference_number: Optional[str] = None
    transaction_id: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    status: Optional[PaymentStatus] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    is_reconciled: Optional[bool] = None
    receipt_url: Optional[str] = None


class PaymentResponse(PaymentBase):
    id: uuid.UUID
    customer_id: uuid.UUID
    exchange_rate: Optional[Decimal]
    amount_in_base_currency: Optional[Decimal]
    status: PaymentStatus
    processed_at: Optional[datetime]
    is_reconciled: bool
    reconciled_at: Optional[datetime]
    reconciled_by: Optional[uuid.UUID]
    processing_fee: Optional[Decimal]
    gateway_fee: Optional[Decimal]
    receipt_url: Optional[str]
    created_by: Optional[uuid.UUID]
    created_at: datetime
    updated_at: Optional[datetime]
    net_amount: Decimal
    is_partial_payment: bool


class PaymentSummary(BaseModel):
    """Payment summary for dashboard"""
    total_payments: int
    total_amount: Decimal
    by_method: Dict[str, Decimal]
    by_status: Dict[str, int]
    by_currency: Dict[str, Decimal]
    reconciled_amount: Decimal
    unreconciled_amount: Decimal
    average_processing_time_hours: Optional[float]


class PaymentSearch(BaseModel):
    """Payment search criteria"""
    query: Optional[str] = None
    invoice_id: Optional[uuid.UUID] = None
    customer_id: Optional[uuid.UUID] = None
    payment_method: Optional[PaymentMethod] = None
    status: Optional[PaymentStatus] = None
    currency: Optional[str] = None
    payment_date_from: Optional[date] = None
    payment_date_to: Optional[date] = None
    amount_min: Optional[Decimal] = None
    amount_max: Optional[Decimal] = None
    is_reconciled: Optional[bool] = None


class PaymentReconciliation(BaseModel):
    """Schema for payment reconciliation"""
    payment_ids: List[uuid.UUID]
    reconciled_by: uuid.UUID
    notes: Optional[str] = None
    bank_statement_reference: Optional[str] = None