"""
Pricing-related Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
import uuid


class PricingRequest(BaseModel):
    """Request schema for pricing calculation"""
    service_type: str = Field(..., description="Type of service being priced")
    base_price: float = Field(..., ge=0, description="Base price before discounts")
    pax_count: int = Field(..., ge=1, description="Number of passengers")
    start_date: date = Field(..., description="Service start date")
    end_date: Optional[date] = Field(default=None, description="Service end date")
    customer_id: Optional[uuid.UUID] = Field(default=None, description="Customer ID for personalized pricing")
    promo_code: Optional[str] = Field(default=None, description="Promotional code")
    currency: Optional[str] = Field(default="MAD", description="Currency code")


class AppliedRule(BaseModel):
    """Applied pricing rule information"""
    rule_id: uuid.UUID
    rule_name: str
    discount_type: str
    discount_amount: float
    description: Optional[str] = None


class PricingCalculation(BaseModel):
    """Pricing calculation result"""
    base_price: float
    discount_amount: float
    total_price: float
    applied_rules: List[AppliedRule]
    currency: str
    breakdown: List[dict] = Field(default_factory=list)


class PricingRuleCreate(BaseModel):
    """Schema for creating pricing rules"""
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    code: Optional[str] = Field(default=None, max_length=50)
    discount_type: str
    discount_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    discount_amount: Optional[float] = Field(default=None, ge=0)
    service_type: Optional[str] = Field(default=None, max_length=100)
    min_pax: Optional[int] = Field(default=None, ge=1)
    max_pax: Optional[int] = Field(default=None, ge=1)
    min_amount: Optional[float] = Field(default=None, ge=0)
    max_amount: Optional[float] = Field(default=None, ge=0)
    valid_from: date
    valid_until: date
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    max_uses: Optional[int] = Field(default=None, ge=0)
    max_uses_per_customer: int = Field(default=1, ge=1)
    priority: int = Field(default=0)
    is_active: bool = Field(default=True)
    is_combinable: bool = Field(default=False)
    conditions: Optional[dict] = None


class PricingRuleResponse(BaseModel):
    """Schema for pricing rule response"""
    id: uuid.UUID
    name: str
    description: Optional[str]
    code: Optional[str]
    discount_type: str
    discount_percentage: Optional[float]
    discount_amount: Optional[float]
    service_type: Optional[str]
    min_pax: Optional[int]
    max_pax: Optional[int]
    valid_from: date
    valid_until: date
    is_active: bool
    current_uses: int
    max_uses: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True