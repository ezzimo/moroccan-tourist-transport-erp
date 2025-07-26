"""
Supplier-related Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from models.supplier import SupplierStatus, SupplierType
import uuid


class SupplierBase(BaseModel):
    name: str
    code: str
    type: SupplierType
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "Morocco"
    tax_id: Optional[str] = None
    registration_number: Optional[str] = None
    website: Optional[str] = None
    payment_terms: Optional[str] = None
    delivery_time_days: Optional[int] = None
    minimum_order_amount: Optional[Decimal] = None
    currency: str = "MAD"
    notes: Optional[str] = None


class SupplierCreate(SupplierBase):
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    
    @validator('code')
    def validate_code(cls, v):
        if not v.strip():
            raise ValueError('Supplier code cannot be empty')
        return v.strip().upper()
    
    @validator('delivery_time_days')
    def validate_delivery_time(cls, v):
        if v is not None and v < 0:
            raise ValueError('Delivery time cannot be negative')
        return v
    
    @validator('contract_end_date')
    def validate_contract_dates(cls, v, values):
        if v and 'contract_start_date' in values and values['contract_start_date']:
            if v <= values['contract_start_date']:
                raise ValueError('Contract end date must be after start date')
        return v


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    registration_number: Optional[str] = None
    website: Optional[str] = None
    payment_terms: Optional[str] = None
    delivery_time_days: Optional[int] = None
    minimum_order_amount: Optional[Decimal] = None
    currency: Optional[str] = None
    status: Optional[SupplierStatus] = None
    is_preferred: Optional[bool] = None
    notes: Optional[str] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None


class SupplierResponse(SupplierBase):
    id: uuid.UUID
    performance_rating: Optional[float]
    on_time_delivery_rate: Optional[float]
    quality_rating: Optional[float]
    total_orders: int
    total_value: Decimal
    status: SupplierStatus
    is_preferred: bool
    first_order_date: Optional[date]
    last_order_date: Optional[date]
    contract_start_date: Optional[date]
    contract_end_date: Optional[date]
    created_at: datetime
    updated_at: Optional[datetime]
    is_contract_active: bool
    days_until_contract_expiry: Optional[int]
    average_order_value: Decimal


class SupplierWithStats(SupplierResponse):
    """Supplier response with performance statistics"""
    total_orders: int = 0
    delivered_orders: int = 0
    on_time_deliveries: int = 0
    average_delivery_days: Optional[float] = None
    on_time_rate: float = 0.0
    total_order_value: float = 0.0
    last_order_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SupplierPerformance(BaseModel):
    """Supplier performance metrics"""
    supplier_id: uuid.UUID
    supplier_name: str
    total_orders: int
    delivered_orders: int
    pending_orders: int
    on_time_deliveries: int
    late_deliveries: int
    average_delivery_days: float
    on_time_rate: float
    performance_score: float
    total_order_value: float
    average_order_value: float
    last_order_date: Optional[datetime]
    performance_trend: str  # "improving", "stable", "declining"
    
    class Config:
        from_attributes = True


class SupplierSummary(BaseModel):
    """Supplier summary for dashboard"""
    total_suppliers: int
    active_suppliers: int
    preferred_suppliers: int
    average_performance_rating: float
    total_purchase_value: Decimal
    by_type: Dict[str, int]
    by_country: Dict[str, int]
    top_performers: List[SupplierPerformance]


class SupplierSearch(BaseModel):
    """Supplier search criteria"""
    query: Optional[str] = None
    type: Optional[SupplierType] = None
    status: Optional[SupplierStatus] = None
    city: Optional[str] = None
    country: Optional[str] = None
    is_preferred: Optional[bool] = None
    min_performance_rating: Optional[float] = None


class SupplierEvaluation(BaseModel):
    """Schema for supplier evaluation"""
    quality_rating: float
    delivery_rating: float
    communication_rating: float
    pricing_rating: float
    overall_rating: float
    comments: Optional[str] = None
    
    @validator('quality_rating', 'delivery_rating', 'communication_rating', 'pricing_rating', 'overall_rating')
    def validate_ratings(cls, v):
        if v < 0 or v > 5:
            raise ValueError('Rating must be between 0 and 5')
        return v