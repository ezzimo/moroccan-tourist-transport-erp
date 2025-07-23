"""
Supplier model for vendor management
"""
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Numeric
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
import uuid


class SupplierStatus(str, Enum):
    """Supplier status enumeration"""
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"
    BLACKLISTED = "Blacklisted"


class SupplierType(str, Enum):
    """Supplier type enumeration"""
    PARTS_SUPPLIER = "Parts Supplier"
    SERVICE_PROVIDER = "Service Provider"
    EQUIPMENT_VENDOR = "Equipment Vendor"
    OFFICE_SUPPLIER = "Office Supplier"
    FUEL_SUPPLIER = "Fuel Supplier"
    OTHER = "Other"


class Supplier(SQLModel, table=True):
    """Supplier model for vendor management"""
    __tablename__ = "suppliers"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Basic Information
    name: str = Field(max_length=255, index=True)
    code: str = Field(unique=True, max_length=20, index=True)
    type: SupplierType = Field(index=True)
    
    # Contact Information
    contact_person: Optional[str] = Field(default=None, max_length=255)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=500)
    city: Optional[str] = Field(default=None, max_length=100)
    country: str = Field(default="Morocco", max_length=100)
    
    # Business Information
    tax_id: Optional[str] = Field(default=None, max_length=50)
    registration_number: Optional[str] = Field(default=None, max_length=50)
    website: Optional[str] = Field(default=None, max_length=255)
    
    # Terms and Conditions
    payment_terms: Optional[str] = Field(default=None, max_length=100)  # e.g., "Net 30"
    delivery_time_days: Optional[int] = Field(default=None, ge=0)
    minimum_order_amount: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    currency: str = Field(default="MAD", max_length=3)
    
    # Performance Metrics
    performance_rating: Optional[float] = Field(default=None, ge=0, le=5)
    on_time_delivery_rate: Optional[float] = Field(default=None, ge=0, le=100)
    quality_rating: Optional[float] = Field(default=None, ge=0, le=5)
    total_orders: int = Field(default=0, ge=0)
    total_value: Decimal = Field(default=0, sa_column=Column(Numeric(15, 2)))
    
    # Status and Metadata
    status: SupplierStatus = Field(default=SupplierStatus.ACTIVE, index=True)
    is_preferred: bool = Field(default=False)
    notes: Optional[str] = Field(default=None, max_length=2000)
    
    # Important Dates
    first_order_date: Optional[date] = Field(default=None)
    last_order_date: Optional[date] = Field(default=None)
    contract_start_date: Optional[date] = Field(default=None)
    contract_end_date: Optional[date] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    items: List["Item"] = Relationship(back_populates="supplier")
    purchase_orders: List["PurchaseOrder"] = Relationship(back_populates="supplier")
    
    def calculate_performance_rating(self) -> float:
        """Calculate overall performance rating"""
        if not self.on_time_delivery_rate or not self.quality_rating:
            return 0.0
        
        # Weighted average: 60% delivery, 40% quality
        delivery_score = (self.on_time_delivery_rate / 100) * 5  # Convert to 5-point scale
        quality_score = self.quality_rating
        
        return round((delivery_score * 0.6) + (quality_score * 0.4), 2)
    
    def is_contract_active(self) -> bool:
        """Check if supplier contract is currently active"""
        if not self.contract_start_date or not self.contract_end_date:
            return True  # No contract dates means always active
        
        today = date.today()
        return self.contract_start_date <= today <= self.contract_end_date
    
    def days_until_contract_expiry(self) -> Optional[int]:
        """Get days until contract expires"""
        if not self.contract_end_date:
            return None
        
        return (self.contract_end_date - date.today()).days
    
    def get_average_order_value(self) -> Decimal:
        """Calculate average order value"""
        if self.total_orders == 0:
            return Decimal(0)
        
        return self.total_value / self.total_orders
    
    def update_performance_metrics(self, on_time: bool, quality_score: float, order_value: Decimal):
        """Update performance metrics with new order data"""
        # Update totals
        self.total_orders += 1
        self.total_value += order_value
        
        # Update on-time delivery rate
        if self.on_time_delivery_rate is None:
            self.on_time_delivery_rate = 100.0 if on_time else 0.0
        else:
            # Calculate new rate using weighted average
            total_on_time = (self.on_time_delivery_rate / 100) * (self.total_orders - 1)
            if on_time:
                total_on_time += 1
            self.on_time_delivery_rate = (total_on_time / self.total_orders) * 100
        
        # Update quality rating
        if self.quality_rating is None:
            self.quality_rating = quality_score
        else:
            # Calculate new rating using weighted average
            total_quality = self.quality_rating * (self.total_orders - 1)
            self.quality_rating = (total_quality + quality_score) / self.total_orders
        
        # Update overall performance rating
        self.performance_rating = self.calculate_performance_rating()
        
        # Update last order date
        self.last_order_date = date.today()
        if not self.first_order_date:
            self.first_order_date = date.today()