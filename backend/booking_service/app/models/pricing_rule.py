"""
Pricing rule model with explicit columns to avoid JSON subscripting
"""
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional
from datetime import date, datetime
from enum import Enum
import uuid


class DiscountType(str, Enum):
    """Discount type enumeration"""
    PERCENTAGE_DISCOUNT = "percentage_discount"
    FLAT_DISCOUNT = "flat_discount"
    SURCHARGE_PERCENTAGE = "surcharge_percentage"
    SURCHARGE_FLAT = "surcharge_flat"
    GROUP_DISCOUNT = "group_discount"
    EARLY_BIRD = "early_bird"


class PricingRule(SQLModel, table=True):
    """Pricing rule model with explicit columns for calculations"""
    __tablename__ = "pricing_rules"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Basic rule information
    name: str = Field(unique=True, max_length=255, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    code: Optional[str] = Field(default=None, max_length=50, unique=True)
    
    # Rule type and value - explicit columns to avoid JSON subscripting
    discount_type: DiscountType = Field(index=True)
    discount_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    discount_amount: Optional[float] = Field(default=None, ge=0)
    
    # Applicability conditions - explicit columns
    service_type: Optional[str] = Field(default=None, max_length=100)
    min_pax: Optional[int] = Field(default=None, ge=1)
    max_pax: Optional[int] = Field(default=None, ge=1)
    min_amount: Optional[float] = Field(default=None, ge=0)
    max_amount: Optional[float] = Field(default=None, ge=0)
    
    # Date validity
    valid_from: date = Field(index=True)
    valid_until: date = Field(index=True)
    start_date_from: Optional[date] = Field(default=None)
    start_date_to: Optional[date] = Field(default=None)
    
    # Usage limits
    max_uses: Optional[int] = Field(default=None, ge=0)
    max_uses_per_customer: int = Field(default=1, ge=1)
    current_uses: int = Field(default=0, ge=0)
    
    # Rule behavior
    priority: int = Field(default=0)
    is_active: bool = Field(default=True, index=True)
    is_combinable: bool = Field(default=False)
    
    # Additional metadata (only use after materializing instance)
    conditions: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    def get_discount_value(self) -> float:
        """Get the discount value based on type"""
        if self.discount_type in [DiscountType.PERCENTAGE_DISCOUNT, DiscountType.SURCHARGE_PERCENTAGE]:
            return self.discount_percentage or 0.0
        else:
            return self.discount_amount or 0.0
    
    def is_applicable_for_amount(self, amount: float) -> bool:
        """Check if rule applies to given amount"""
        if self.min_amount is not None and amount < self.min_amount:
            return False
        if self.max_amount is not None and amount > self.max_amount:
            return False
        return True
    
    def is_applicable_for_pax(self, pax_count: int) -> bool:
        """Check if rule applies to given passenger count"""
        if self.min_pax is not None and pax_count < self.min_pax:
            return False
        if self.max_pax is not None and pax_count > self.max_pax:
            return False
        return True
    
    def is_applicable_for_dates(self, start_date: date, booking_date: date) -> bool:
        """Check if rule applies to given dates"""
        # Check rule validity period
        if booking_date < self.valid_from or booking_date > self.valid_until:
            return False
        
        # Check service date range if specified
        if self.start_date_from is not None and start_date < self.start_date_from:
            return False
        if self.start_date_to is not None and start_date > self.start_date_to:
            return False
        
        return True
    
    def can_be_used(self) -> bool:
        """Check if rule can still be used (usage limits)"""
        if not self.is_active:
            return False
        if self.max_uses is not None and self.current_uses >= self.max_uses:
            return False
        return True