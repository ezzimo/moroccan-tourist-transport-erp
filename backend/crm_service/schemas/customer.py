"""
Customer-related Pydantic schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from models.customer import ContactType, LoyaltyStatus
import uuid


class CustomerBase(BaseModel):
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    contact_type: ContactType
    email: EmailStr
    phone: str
    nationality: Optional[str] = None
    region: Optional[str] = None
    preferred_language: str = "French"


class CustomerCreate(CustomerBase):
    tags: Optional[List[str]] = []
    notes: Optional[str] = None


class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    nationality: Optional[str] = None
    region: Optional[str] = None
    preferred_language: Optional[str] = None
    tags: Optional[List[str]] = None
    loyalty_status: Optional[LoyaltyStatus] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: uuid.UUID
    loyalty_status: LoyaltyStatus
    is_active: bool
    tags: List[str] = []
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]
    last_interaction: Optional[datetime]
    
    @classmethod
    def from_model(cls, customer):
        """Create response from database model"""
        return cls(
            id=customer.id,
            full_name=customer.full_name,
            company_name=customer.company_name,
            contact_type=customer.contact_type,
            email=customer.email,
            phone=customer.phone,
            nationality=customer.nationality,
            region=customer.region,
            preferred_language=customer.preferred_language,
            loyalty_status=customer.loyalty_status,
            is_active=customer.is_active,
            tags=customer.get_tags_list(),
            notes=customer.notes,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
            last_interaction=customer.last_interaction
        )


class CustomerSummary(CustomerResponse):
    """Extended customer response with summary statistics"""
    total_interactions: int = 0
    total_feedback: int = 0
    average_rating: Optional[float] = None
    last_feedback_date: Optional[datetime] = None
    segments: List[str] = []
    interaction_channels: Dict[str, int] = {}
    feedback_by_service: Dict[str, int] = {}


class CustomerSearch(BaseModel):
    """Customer search criteria"""
    query: Optional[str] = None
    contact_type: Optional[ContactType] = None
    region: Optional[str] = None
    loyalty_status: Optional[LoyaltyStatus] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = True