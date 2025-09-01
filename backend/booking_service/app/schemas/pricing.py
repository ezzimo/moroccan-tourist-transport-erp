"""
Pricing request/response schemas
"""
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID


class PricingRequest(BaseModel):
    """Request schema for pricing calculation"""
    service_type: str = Field(..., description="Type of service being priced")
    base_price: Decimal = Field(..., ge=0, description="Base price before rules")
    pax_count: int = Field(..., ge=1, description="Number of passengers")
    start_date: date = Field(..., description="Service start date")
    end_date: Optional[date] = Field(default=None, description="Service end date")
    customer_id: Optional[UUID] = Field(default=None, description="Customer ID for personalized pricing")
    currency: Optional[str] = Field(default="MAD", description="Currency code")
    promo_code: Optional[str] = Field(default=None, description="Promotional code")


class AppliedRule(BaseModel):
    """Applied pricing rule details"""
    rule_id: UUID
    rule_name: str
    rule_type: str
    effect_amount: Decimal
    description: Optional[str] = None


class PricingResponse(BaseModel):
    """Response schema for pricing calculation"""
    base_price: Decimal = Field(..., description="Original base price")
    pax_count: int = Field(..., description="Number of passengers")
    subtotal: Decimal = Field(..., description="Base price × passenger count")
    discount_amount: Decimal = Field(..., description="Total discount applied")
    surcharge_amount: Decimal = Field(..., description="Total surcharge applied")
    total_price: Decimal = Field(..., description="Final price after all rules")
    currency: str = Field(..., description="Currency code")
    applied_rules: List[AppliedRule] = Field(default_factory=list, description="Rules that were applied")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class PricingRuleCreate(BaseModel):
    """Schema for creating pricing rules"""
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    service_type: Optional[str] = Field(default=None, max_length=100)
    rule_type: str = Field(..., description="Type of pricing rule")
    discount_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    discount_amount: Optional[float] = Field(default=None, ge=0)
    surcharge_percentage: Optional[float] = Field(default=None, ge=0)
    surcharge_amount: Optional[float] = Field(default=None, ge=0)
    min_pax: Optional[int] = Field(default=None, ge=1)
    max_pax: Optional[int] = Field(default=None, ge=1)
    start_date_from: Optional[date] = Field(default=None)
    start_date_to: Optional[date] = Field(default=None)
    valid_from: Optional[date] = Field(default=None)
    valid_until: Optional[date] = Field(default=None)
    priority: int = Field(default=100)
    is_combinable: bool = Field(default=True)
    max_uses: Optional[int] = Field(default=None, ge=0)
    conditions: Optional[dict] = Field(default=None)


class PricingRuleResponse(BaseModel):
    """Response schema for pricing rules"""
    id: UUID
    name: str
    description: Optional[str]
    service_type: Optional[str]
    rule_type: str
    discount_percentage: Optional[float]
    discount_amount: Optional[float]
    surcharge_percentage: Optional[float]
    surcharge_amount: Optional[float]
    min_pax: Optional[int]
    max_pax: Optional[int]
    start_date_from: Optional[date]
    start_date_to: Optional[date]
    valid_from: Optional[date]
    valid_until: Optional[date]
    priority: int
    is_active: bool
    is_combinable: bool
    max_uses: Optional[int]
    current_uses: int
    conditions: Optional[dict]
    
    class Config:
        from_attributes = True