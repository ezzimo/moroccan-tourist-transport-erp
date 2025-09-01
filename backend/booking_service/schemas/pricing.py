"""
Pricing-related Pydantic schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date
from decimal import Decimal
import uuid


class PricingContext(BaseModel):
    """Comprehensive pricing context for rule evaluation"""
    service_type: str = Field(..., description="Type of service being priced")
    base_price: Decimal = Field(..., ge=0, description="Base price before discounts")
    pax_count: int = Field(..., ge=1, le=50, description="Number of passengers")
    start_date: date = Field(..., description="Service start date")
    end_date: Optional[date] = Field(None, description="Service end date")
    customer_id: Optional[uuid.UUID] = Field(None, description="Customer identifier")
    route_id: Optional[uuid.UUID] = Field(None, description="Route identifier")
    promo_code: Optional[str] = Field(None, max_length=50, description="Promotional code")
    booking_advance_days: Optional[int] = Field(None, ge=0, description="Days in advance of booking")
    customer_loyalty_tier: Optional[str] = Field(None, description="Customer loyalty status")
    season: Optional[str] = Field(None, description="Seasonal pricing period")
    day_of_week: Optional[str] = Field(None, description="Day of the week")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v
    
    @validator('service_type')
    def validate_service_type(cls, v):
        allowed_types = ['Tour', 'Transfer', 'Custom Package', 'Accommodation', 'Activity']
        if v not in allowed_types:
            raise ValueError(f'Service type must be one of: {", ".join(allowed_types)}')
        return v


class PricingRequest(BaseModel):
    """Request schema for pricing calculation"""
    service_type: str = Field(..., description="Type of service")
    base_price: Decimal = Field(..., ge=0, description="Base price")
    pax_count: int = Field(..., ge=1, le=50, description="Number of passengers")
    start_date: date = Field(..., description="Start date")
    end_date: Optional[date] = None
    customer_id: Optional[uuid.UUID] = None
    promo_code: Optional[str] = Field(None, max_length=50)
    
    def to_pricing_context(self) -> PricingContext:
        """Convert to PricingContext for service layer"""
        return PricingContext(
            service_type=self.service_type,
            base_price=self.base_price,
            pax_count=self.pax_count,
            start_date=self.start_date,
            end_date=self.end_date,
            customer_id=self.customer_id,
            promo_code=self.promo_code
        )


class AppliedRule(BaseModel):
    """Applied pricing rule information"""
    rule_id: uuid.UUID
    rule_name: str
    discount_type: str
    discount_amount: Decimal
    discount_percentage: Optional[Decimal] = None


class PricingCalculation(BaseModel):
    """Pricing calculation result"""
    base_price: Decimal
    discount_amount: Decimal = Field(default=Decimal('0.00'))
    total_price: Decimal
    applied_rules: List[AppliedRule] = Field(default_factory=list)
    currency: str = Field(default="MAD")
    calculation_details: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('total_price')
    def validate_total_price(cls, v, values):
        if 'base_price' in values and 'discount_amount' in values:
            expected_total = values['base_price'] - values['discount_amount']
            if abs(v - expected_total) > Decimal('0.01'):  # Allow for rounding
                raise ValueError('Total price must equal base price minus discount amount')
        return v


class PricingRuleConditions(BaseModel):
    """Conditions for pricing rule application"""
    min_pax_count: Optional[int] = None
    max_pax_count: Optional[int] = None
    min_advance_days: Optional[int] = None
    max_advance_days: Optional[int] = None
    valid_service_types: Optional[List[str]] = None
    valid_routes: Optional[List[uuid.UUID]] = None
    valid_customers: Optional[List[uuid.UUID]] = None
    valid_loyalty_tiers: Optional[List[str]] = None
    valid_seasons: Optional[List[str]] = None
    valid_days_of_week: Optional[List[str]] = None
    min_booking_value: Optional[Decimal] = None
    max_booking_value: Optional[Decimal] = None


class PricingRuleCreate(BaseModel):
    """Schema for creating pricing rules"""
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    code: Optional[str] = Field(None, max_length=50)
    discount_type: str = Field(..., description="Type of discount")
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    conditions: PricingRuleConditions = Field(default_factory=PricingRuleConditions)
    valid_from: date
    valid_until: date
    max_uses: Optional[int] = Field(None, ge=0)
    max_uses_per_customer: int = Field(default=1, ge=0)
    priority: int = Field(default=0)
    is_active: bool = Field(default=True)
    is_combinable: bool = Field(default=False)