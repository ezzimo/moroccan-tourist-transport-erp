"""
Pricing rule-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from models.pricing_rule import DiscountType
import uuid


class PricingRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    code: Optional[str] = None
    discount_type: DiscountType
    discount_percentage: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    conditions: Dict[str, Any]
    valid_from: date
    valid_until: date
    max_uses: Optional[int] = None
    max_uses_per_customer: int = 1
    priority: int = 0
    is_combinable: bool = False


class PricingRuleCreate(PricingRuleBase):
    @validator('discount_percentage')
    def validate_percentage(cls, v, values):
        if values.get('discount_type') == DiscountType.PERCENTAGE and (not v or v <= 0 or v > 100):
            raise ValueError('Discount percentage must be between 0 and 100')
        return v
    
    @validator('discount_amount')
    def validate_amount(cls, v, values):
        if values.get('discount_type') == DiscountType.FIXED_AMOUNT and (not v or v <= 0):
            raise ValueError('Discount amount must be greater than 0')
        return v
    
    @validator('valid_until')
    def validate_dates(cls, v, values):
        if 'valid_from' in values and v <= values['valid_from']:
            raise ValueError('Valid until date must be after valid from date')
        return v


class PricingRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    discount_percentage: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    conditions: Optional[Dict[str, Any]] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    max_uses: Optional[int] = None
    max_uses_per_customer: Optional[int] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    is_combinable: Optional[bool] = None


class PricingRuleResponse(PricingRuleBase):
    id: uuid.UUID
    current_uses: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]


class PricingRequest(BaseModel):
    """Schema for pricing calculation request"""
    service_type: str
    base_price: Decimal
    pax_count: int
    start_date: date
    end_date: Optional[date] = None
    customer_id: Optional[uuid.UUID] = None
    promo_code: Optional[str] = None


class PricingResponse(BaseModel):
    """Schema for pricing calculation response"""
    base_price: Decimal
    discount_amount: Decimal
    total_price: Decimal
    applied_rules: List[Dict[str, Any]] = []
    currency: str = "MAD"