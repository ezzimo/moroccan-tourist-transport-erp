"""
Pricing rule model with explicit columns to avoid JSON subscripting
"""
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional
from datetime import date
from uuid import UUID, uuid4
from enum import Enum


class RuleType(str, Enum):
    """Pricing rule types"""
    PERCENTAGE_DISCOUNT = "percentage_discount"
    FLAT_DISCOUNT = "flat_discount"
    SURCHARGE_PERCENTAGE = "surcharge_percentage"
    SURCHARGE_FLAT = "surcharge_flat"
    GROUP_DISCOUNT = "group_discount"
    EARLY_BIRD = "early_bird"


class PricingRule(SQLModel, table=True):
    """Pricing rule model with explicit columns for safe attribute access"""
    __tablename__ = "pricing_rules"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    
    # Rule application
    service_type: Optional[str] = Field(default=None, max_length=100, index=True)
    rule_type: RuleType = Field(index=True)
    
    # Discount/surcharge values
    discount_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    discount_amount: Optional[float] = Field(default=None, ge=0)
    surcharge_percentage: Optional[float] = Field(default=None, ge=0)
    surcharge_amount: Optional[float] = Field(default=None, ge=0)
    
    # Participant constraints
    min_pax: Optional[int] = Field(default=None, ge=1)
    max_pax: Optional[int] = Field(default=None, ge=1)
    
    # Date constraints
    start_date_from: Optional[date] = Field(default=None)
    start_date_to: Optional[date] = Field(default=None)
    valid_from: Optional[date] = Field(default=None)
    valid_until: Optional[date] = Field(default=None)
    
    # Rule behavior
    priority: int = Field(default=100, index=True)
    is_active: bool = Field(default=True, index=True)
    is_combinable: bool = Field(default=True)
    max_uses: Optional[int] = Field(default=None, ge=0)
    current_uses: int = Field(default=0, ge=0)
    
    # Additional metadata (safe to subscript after fetching)
    conditions: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    def is_applicable(self, service_type: str, pax_count: int, booking_date: date) -> bool:
        """Check if rule applies to given parameters using safe attribute access"""
        if not self.is_active:
            return False
            
        # Service type check
        if self.service_type and self.service_type != service_type:
            return False
            
        # Participant count checks
        if self.min_pax is not None and pax_count < self.min_pax:
            return False
        if self.max_pax is not None and pax_count > self.max_pax:
            return False
            
        # Date range checks
        if self.start_date_from and booking_date < self.start_date_from:
            return False
        if self.start_date_to and booking_date > self.start_date_to:
            return False
            
        # Rule validity period
        if self.valid_from and booking_date < self.valid_from:
            return False
        if self.valid_until and booking_date > self.valid_until:
            return False
            
        # Usage limits
        if self.max_uses is not None and self.current_uses >= self.max_uses:
            return False
            
        return True
    
    def get_effect_value(self) -> Optional[float]:
        """Get the primary effect value for this rule"""
        if self.rule_type == RuleType.PERCENTAGE_DISCOUNT:
            return self.discount_percentage
        elif self.rule_type == RuleType.FLAT_DISCOUNT:
            return self.discount_amount
        elif self.rule_type == RuleType.SURCHARGE_PERCENTAGE:
            return self.surcharge_percentage
        elif self.rule_type == RuleType.SURCHARGE_FLAT:
            return self.surcharge_amount
        return None