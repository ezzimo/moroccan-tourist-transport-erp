"""
Pricing-related Pydantic schemas
"""
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date
from typing import Optional
from uuid import UUID


class PricingRequest(BaseModel):
    """Request schema for pricing calculation"""
    service_type: str = Field(..., description="Type of service (Tour, Transfer, etc.)")
    base_price: Decimal = Field(..., ge=0, description="Base price per person")
    pax_count: int = Field(..., ge=1, description="Number of passengers")
    start_date: date = Field(..., description="Service start date")
    end_date: Optional[date] = Field(default=None, description="Service end date")
    customer_id: Optional[UUID] = Field(default=None, description="Customer ID for personalized pricing")
    currency: Optional[str] = Field(default="MAD", description="Currency code")
    promo_code: Optional[str] = Field(default=None, description="Promotional code")


class PricingResponse(BaseModel):
    """Response schema for pricing calculation"""
    base_price: Decimal = Field(..., description="Base price per person")
    pax_count: int = Field(..., description="Number of passengers")
    service_type: str = Field(..., description="Type of service")
    subtotal: Decimal = Field(..., description="Subtotal before discounts/surcharges")
    discount_amount: Decimal = Field(..., description="Total discount applied")
    surcharge_amount: Decimal = Field(..., description="Total surcharge applied")
    total_price: Decimal = Field(..., description="Final total price")
    currency: str = Field(..., description="Currency code")
    applied_rules: list[str] = Field(default_factory=list, description="Names of applied pricing rules")


class AppliedRule(BaseModel):
    """Information about an applied pricing rule"""
    rule_name: str
    rule_type: str
    discount_amount: Optional[Decimal] = None
    surcharge_amount: Optional[Decimal] = None