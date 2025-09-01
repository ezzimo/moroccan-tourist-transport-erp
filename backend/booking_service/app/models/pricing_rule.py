"""
Pricing rule model with explicit typed columns
"""
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional
from datetime import date
from uuid import UUID, uuid4
from decimal import Decimal


class PricingRule(SQLModel, table=True):
    """Pricing rule model with explicit columns to avoid JSON subscripting"""
    __tablename__ = "pricing_rules"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    
    # Service targeting
    service_type: str = Field(max_length=100, index=True)  # "Tour", "Transfer", etc.
    
    # Rule type and values
    rule_type: str = Field(max_length=50)  # "percentage_discount", "flat_discount", "surcharge_percentage", "surcharge_flat"
    discount_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    discount_amount: Optional[float] = Field(default=None, ge=0)
    surcharge_percentage: Optional[float] = Field(default=None, ge=0)
    surcharge_amount: Optional[float] = Field(default=None, ge=0)
    
    # Applicability conditions
    min_pax: Optional[int] = Field(default=None, ge=1)
    max_pax: Optional[int] = Field(default=None, ge=1)
    start_date_from: Optional[date] = Field(default=None)
    start_date_to: Optional[date] = Field(default=None)
    
    # Rule metadata
    priority: int = Field(default=100, ge=0)
    is_active: bool = Field(default=True, index=True)
    is_combinable: bool = Field(default=False)
    
    # Additional metadata (use sparingly, prefer explicit columns)
    meta: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    # Timestamps
    created_at: date = Field(default_factory=date.today)
    updated_at: Optional[date] = Field(default=None)

    def is_applicable(self, pax_count: int, start_date: date) -> bool:
        """Check if rule applies to given parameters using attribute access only"""
        if not self.is_active:
            return False
        
        if self.min_pax is not None and pax_count < self.min_pax:
            return False
        
        if self.max_pax is not None and pax_count > self.max_pax:
            return False
        
        if self.start_date_from is not None and start_date < self.start_date_from:
            return False
        
        if self.start_date_to is not None and start_date > self.start_date_to:
            return False
        
        return True

    def get_discount_value(self) -> Decimal:
        """Get discount value as Decimal, preferring percentage over flat amount"""
        if self.discount_percentage is not None:
            return Decimal(str(self.discount_percentage))
        elif self.discount_amount is not None:
            return Decimal(str(self.discount_amount))
        return Decimal("0.00")

    def get_surcharge_value(self) -> Decimal:
        """Get surcharge value as Decimal, preferring percentage over flat amount"""
        if self.surcharge_percentage is not None:
            return Decimal(str(self.surcharge_percentage))
        elif self.surcharge_amount is not None:
            return Decimal(str(self.surcharge_amount))
        return Decimal("0.00")