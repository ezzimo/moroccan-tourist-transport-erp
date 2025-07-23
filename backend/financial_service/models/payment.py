"""
Payment model for payment tracking
"""
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Numeric
from typing import Optional
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
import uuid


class PaymentMethod(str, Enum):
    """Payment method enumeration"""
    CASH = "Cash"
    CREDIT_CARD = "Credit Card"
    DEBIT_CARD = "Debit Card"
    BANK_TRANSFER = "Bank Transfer"
    CHECK = "Check"
    MOBILE_PAYMENT = "Mobile Payment"
    CRYPTOCURRENCY = "Cryptocurrency"
    OTHER = "Other"


class PaymentStatus(str, Enum):
    """Payment status enumeration"""
    PENDING = "Pending"
    PROCESSING = "Processing"
    CONFIRMED = "Confirmed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"
    REFUNDED = "Refunded"


class Payment(SQLModel, table=True):
    """Payment model for tracking customer payments"""
    __tablename__ = "payments"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # References
    invoice_id: uuid.UUID = Field(foreign_key="invoices.id", index=True)
    customer_id: uuid.UUID = Field(index=True)  # Reference to CRM service
    
    # Payment Details
    amount: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    currency: str = Field(default="MAD", max_length=3)
    exchange_rate: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 4)))
    amount_in_base_currency: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    
    # Payment Information
    payment_method: PaymentMethod = Field(index=True)
    payment_date: date = Field(index=True)
    reference_number: Optional[str] = Field(default=None, max_length=100)
    transaction_id: Optional[str] = Field(default=None, max_length=100)
    
    # Bank/Card Information
    bank_name: Optional[str] = Field(default=None, max_length=100)
    account_number: Optional[str] = Field(default=None, max_length=50)
    card_last_four: Optional[str] = Field(default=None, max_length=4)
    
    # Status and Processing
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, index=True)
    processed_at: Optional[datetime] = Field(default=None)
    
    # Reconciliation
    is_reconciled: bool = Field(default=False, index=True)
    reconciled_at: Optional[datetime] = Field(default=None)
    reconciled_by: Optional[uuid.UUID] = Field(default=None)
    
    # Additional Information
    description: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = Field(default=None, max_length=1000)
    receipt_url: Optional[str] = Field(default=None, max_length=500)
    
    # Fees and Charges
    processing_fee: Optional[Decimal] = Field(default=0, sa_column=Column(Numeric(10, 2)))
    gateway_fee: Optional[Decimal] = Field(default=0, sa_column=Column(Numeric(10, 2)))
    
    # Audit Fields
    created_by: Optional[uuid.UUID] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    invoice: Optional["Invoice"] = Relationship(back_populates="payments")
    
    def calculate_base_currency_amount(self, base_currency: str = "MAD"):
        """Calculate amount in base currency using exchange rate"""
        if self.currency == base_currency:
            self.amount_in_base_currency = self.amount
        elif self.exchange_rate:
            self.amount_in_base_currency = self.amount * self.exchange_rate
    
    def get_net_amount(self) -> Decimal:
        """Get net amount after fees"""
        return self.amount - (self.processing_fee or 0) - (self.gateway_fee or 0)
    
    def is_partial_payment(self) -> bool:
        """Check if this is a partial payment"""
        if not self.invoice:
            return False
        return self.amount < self.invoice.total_amount