"""
Invoice item model for line items
"""
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Numeric
from typing import Optional
from decimal import Decimal
import uuid


class InvoiceItem(SQLModel, table=True):
    """Invoice item model for invoice line items"""
    __tablename__ = "invoice_items"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Foreign Keys
    invoice_id: uuid.UUID = Field(foreign_key="invoices.id", index=True)
    
    # Item Details
    description: str = Field(max_length=500)
    quantity: Decimal = Field(default=1, sa_column=Column(Numeric(10, 2)))
    unit_price: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    total_amount: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    
    # Tax Information
    tax_rate: float = Field(default=20.0)
    tax_amount: Decimal = Field(default=0, sa_column=Column(Numeric(10, 2)))
    
    # Additional Information
    item_code: Optional[str] = Field(default=None, max_length=50)
    category: Optional[str] = Field(default=None, max_length=100)
    
    # Relationships
    invoice: Optional["Invoice"] = Relationship(back_populates="invoice_items")
    
    def calculate_total(self):
        """Calculate total amount for this item"""
        self.total_amount = self.quantity * self.unit_price
        self.tax_amount = self.total_amount * (self.tax_rate / 100)