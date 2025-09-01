"""
Pricing-related Pydantic schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date
from decimal import Decimal
import uuid


class PricingRequest(BaseModel):
    """Request schema for pricing calculation"""
    service_type: str = Field(..., description="Type of service (Tour, Transfer, etc.)")
    base_price: Decimal = Field(..., ge=0, description="Base price before discounts")
    pax_count: int = Field(..., ge=1, le=50, description="Number of passengers")
    start_date: date = Field(..., description="Service start date")
    end_date: Optional[date] = Field(None, description="Service end date")
    customer_id: Optional[uuid.UUID] = Field(None, description="Customer ID for loyalty discounts")
    promo_code: Optional[str] = Field(None, max_length=50, description="Promotional code")
    route_id: Optional[uuid.UUID] = Field(None, description="Route ID for route-specific discounts")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v
    
    def to_pricing_context(self) -> 'PricingContext':
        """Convert to PricingContext for service layer"""
        return PricingContext(
            service_type=self.service_type,
            base_price=self.base_price,
            pax_count=self.pax_count,
            start_date=self.start_date,
            end_date=self.end_date,
            customer_id=self.customer_id,
            promo_code=self.promo_code,
            route_id=self.route_id
        )


class PricingContext(BaseModel):
    """Internal context for pricing calculations"""
    service_type: str
    base_price: Decimal
    pax_count: int
    start_date: date
    end_date: Optional[date] = None
    customer_id: Optional[uuid.UUID] = None
    promo_code: Optional[str] = None
    route_id: Optional[uuid.UUID] = None
    
    @property
    def party_size(self) -> int:
        """Alias for pax_count for backward compatibility"""
        return self.pax_count


class AppliedRule(BaseModel):
    """Schema for applied pricing rule"""
    rule_id: uuid.UUID
    rule_name: str
    discount_type: str
    discount_amount: Decimal
    discount_percentage: Optional[Decimal] = None


class PricingCalculation(BaseModel):
    """Response schema for pricing calculation"""
    base_price: Decimal
    discount_amount: Decimal = Field(default=Decimal('0'))
    total_price: Decimal
    applied_rules: List[AppliedRule] = Field(default_factory=list)
    currency: str = Field(default="MAD")
    
    @validator('total_price')
    def validate_total_price(cls, v, values):
        if v < 0:
            raise ValueError('Total price cannot be negative')
        return v


class PromoCodeValidation(BaseModel):
    """Schema for promo code validation"""
    promo_code: str = Field(..., max_length=50)
    service_type: str
    base_price: Decimal = Field(..., ge=0)
    pax_count: int = Field(..., ge=1)
    start_date: date
    customer_id: Optional[uuid.UUID] = None


class PromoCodeResponse(BaseModel):
    """Response schema for promo code validation"""
    valid: bool
    discount_amount: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    message: Optional[str] = None
    rule_name: Optional[str] = None