from typing import Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

SortOrder = Literal["asc", "desc"]

class BookingFilters(BaseModel):
    """Filters for booking queries with pagination and sorting"""
    
    # Pagination
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=200, description="Items per page")
    
    # Sorting
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: SortOrder = Field(default="desc", description="Sort order")
    
    # Booking filters (matching actual Booking model fields)
    customer_id: Optional[uuid.UUID] = Field(default=None, description="Filter by customer ID")
    service_type: Optional[str] = Field(default=None, description="Filter by service type")
    status: Optional[str] = Field(default=None, description="Filter by booking status")
    payment_status: Optional[str] = Field(default=None, description="Filter by payment status")
    
    # Date filters (using actual model field names)
    start_date_from: Optional[str] = Field(default=None, description="Filter by start date from (YYYY-MM-DD)")
    start_date_to: Optional[str] = Field(default=None, description="Filter by start date to (YYYY-MM-DD)")
    created_from: Optional[datetime] = Field(default=None, description="Filter by creation date from")
    created_to: Optional[datetime] = Field(default=None, description="Filter by creation date to")
    
    # Search
    search: Optional[str] = Field(default=None, description="Search in lead passenger name, email")
    
    # Additional filters
    pax_count_min: Optional[int] = Field(default=None, ge=1, description="Minimum passenger count")
    pax_count_max: Optional[int] = Field(default=None, ge=1, description="Maximum passenger count")
    currency: Optional[str] = Field(default=None, description="Filter by currency")
    
    @property
    def offset(self) -> int:
        """Calculate offset for pagination"""
        return (self.page - 1) * self.size