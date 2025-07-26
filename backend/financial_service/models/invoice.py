"""
Invoice model for billing management
"""
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Numeric
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
import uuid


class InvoiceStatus(str, Enum):
    """Invoice status enumeration"""
    DRAFT = "Draft"
    SENT = "Sent"
    PAID = "Paid"
    OVERDUE = "Overdue"
    CANCELLED = "Cancelled"
    REFUNDED = "Refunded"


class PaymentStatus(str, Enum):
    """Payment status enumeration"""
    PENDING = "Pending"
    PARTIAL = "Partial"
    PAID = "Paid"
    FAILED = "Failed"
    REFUNDED = "Refunded"


class Invoice(SQLModel, table=True):
    """Invoice model for customer billing"""
    __tablename__ = "invoices"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Invoice Identification
    invoice_number: str = Field(unique=True, max_length=50, index=True)
    
    # References
    booking_id: Optional[uuid.UUID] = Field(default=None, index=True)  # Reference to booking service
    customer_id: uuid.UUID = Field(index=True)  # Reference to CRM service
    
    # Customer Information (cached for performance)
    customer_name: str = Field(max_length=255)
    customer_email: str = Field(max_length=255)
    customer_address: Optional[str] = Field(default=None, max_length=500)
    customer_tax_id: Optional[str] = Field(default=None, max_length=50)
    
    # Financial Details
    subtotal: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    tax_amount: Decimal = Field(default=0, sa_column=Column(Numeric(10, 2)))
    discount_amount: Decimal = Field(default=0, sa_column=Column(Numeric(10, 2)))
    total_amount: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    currency: str = Field(default="MAD", max_length=3)
    
    # Tax Information
    tax_rate: float = Field(default=20.0)  # VAT rate percentage
    tax_inclusive: bool = Field(default=True)
    
    # Status and Dates
    status: InvoiceStatus = Field(default=InvoiceStatus.DRAFT, index=True)
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING, index=True)
    
    # Important Dates
    issue_date: date = Field(default_factory=date.today, index=True)
    due_date: date = Field(index=True)
    sent_date: Optional[date] = Field(default=None)
    paid_date: Optional[date] = Field(default=None)
    
    # Payment Terms
    payment_terms: str = Field(default="Net 30", max_length=100)
    payment_method: Optional[str] = Field(default=None, max_length=50)
    
    # Additional Information
    description: Optional[str] = Field(default=None, max_length=1000)
    notes: Optional[str] = Field(default=None, max_length=2000)
    
    # Audit Fields
    created_by: Optional[uuid.UUID] = Field(default=None)
    approved_by: Optional[uuid.UUID] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    payments: List["Payment"] = Relationship(back_populates="invoice")
    invoice_items: List["InvoiceItem"] = Relationship(back_populates="invoice")
    
    def calculate_totals(self):
        """Calculate invoice totals from items"""
        if not self.invoice_items:
            return
        
        self.subtotal = sum(item.total_amount for item in self.invoice_items)
        
        if self.tax_inclusive:
            # Tax is included in the subtotal
            self.tax_amount = self.subtotal * (self.tax_rate / (100 + self.tax_rate))
            self.total_amount = self.subtotal - self.discount_amount
        else:
            # Tax is added to subtotal
            self.tax_amount = self.subtotal * (self.tax_rate / 100)
            self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
    
    def get_paid_amount(self) -> Decimal:
        """Get total amount paid for this invoice"""
        return sum(payment.amount for payment in self.payments if payment.status == "Confirmed")
    
    def get_outstanding_amount(self) -> Decimal:
        """Get outstanding amount to be paid"""
        return self.total_amount - self.get_paid_amount()
    
    def is_overdue(self) -> bool:
        """Check if invoice is overdue"""
        return (
            self.payment_status != PaymentStatus.PAID and
            date.today() > self.due_date
        )
    
    def get_days_overdue(self) -> int:
        """Get number of days overdue"""
        if not self.is_overdue():
            return 0
        return (date.today() - self.due_date).days