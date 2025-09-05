"""
Pricing-related Pydantic schemas with robust input validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from decimal import Decimal, InvalidOperation
from datetime import date
import uuid


class PricingRequest(BaseModel):
    """Schema for pricing calculation request with safe numeric conversion"""
    service_type: str = Field(..., min_length=1, max_length=100)
    base_price: Decimal = Field(..., ge=0, description="Base price in local currency")
    pax_count: int = Field(..., ge=1, le=50, description="Number of passengers")
    start_date: date = Field(..., description="Service start date")
    end_date: Optional[date] = Field(None, description="Service end date")
    customer_id: Optional[uuid.UUID] = Field(None, description="Customer ID for loyalty discounts")
    promo_code: Optional[str] = Field(None, max_length=50, description="Promotional code")
    
    @field_validator('base_price', mode='before')
    @classmethod
    def validate_base_price(cls, v):
        """Convert and validate base price"""
        if v is None or v == '':
            raise ValueError("Base price is required")
        
        try:
            # Handle string inputs from frontend
            if isinstance(v, str):
                v = v.strip()
                if not v:
                    raise ValueError("Base price cannot be empty")
            
            decimal_value = Decimal(str(v))
            
            if decimal_value < 0:
                raise ValueError("Base price must be non-negative")
            
            if decimal_value > Decimal('999999.99'):
                raise ValueError("Base price is too large")
                
            return decimal_value.quantize(Decimal('0.01'))
            
        except (InvalidOperation, ValueError, TypeError) as e:
            raise ValueError(f"Invalid base price format: {str(e)}")
    
    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        """Ensure end date is after start date"""
        if v and 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError("End date must be after start date")
        return v
    
    @field_validator('promo_code', mode='before')
    @classmethod
    def validate_promo_code(cls, v):
        """Clean and validate promo code"""
        if v:
            v = str(v).strip().upper()
            if not v:
                return None
            if len(v) > 50:
                raise ValueError("Promo code is too long")
        return v or None


class PricingCalculation(BaseModel):
    """Schema for pricing calculation response"""
    base_price: Decimal = Field(..., description="Original base price")
    discount_amount: Decimal = Field(default=Decimal('0'), description="Total discount applied")
    total_price: Decimal = Field(..., description="Final price after discounts")
    applied_rules: List['PricingRule'] = Field(default_factory=list, description="Applied pricing rules")
    currency: str = Field(default="MAD", description="Currency code")
    
    class Config:
        from_attributes = True


class PricingRule(BaseModel):
    """Schema for applied pricing rule"""
    rule_id: uuid.UUID
    rule_name: str
    discount_type: str
    discount_amount: Decimal
    
    class Config:
        from_attributes = True


class PricingContext(BaseModel):
    """Internal pricing context for service layer"""
    service_type: str
    base_price: Decimal
    pax_count: int
    start_date: date
    end_date: Optional[date] = None
    customer_id: Optional[uuid.UUID] = None
    promo_code: Optional[str] = None
    
    @classmethod
    def from_request(cls, request: PricingRequest) -> 'PricingContext':
        """Create pricing context from request"""
        return cls(
            service_type=request.service_type,
            base_price=request.base_price,
            pax_count=request.pax_count,
            start_date=request.start_date,
            end_date=request.end_date,
            customer_id=request.customer_id,
            promo_code=request.promo_code
        )


class PricingError(BaseModel):
    """Schema for pricing calculation errors"""
    error_code: str = Field(..., description="Error code for client handling")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")