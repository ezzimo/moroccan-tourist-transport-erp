"""
Customer model for CRM system
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class ContactType(str, Enum):
    """Customer contact type enumeration"""
    INDIVIDUAL = "Individual"
    CORPORATE = "Corporate"


class LoyaltyStatus(str, Enum):
    """Customer loyalty status enumeration"""
    NEW = "New"
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"
    VIP = "VIP"


class Customer(SQLModel, table=True):
    """Customer model with profile and preference information"""
    __tablename__ = "customers"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Basic Information
    full_name: Optional[str] = Field(default=None, max_length=255, index=True)
    company_name: Optional[str] = Field(default=None, max_length=255, index=True)
    contact_type: ContactType = Field(index=True)
    
    # Contact Information
    email: str = Field(unique=True, index=True, max_length=255)
    phone: str = Field(max_length=20, index=True)
    
    # Location & Demographics
    nationality: Optional[str] = Field(default=None, max_length=100)
    region: Optional[str] = Field(default=None, max_length=100, index=True)
    preferred_language: str = Field(default="French", max_length=50)
    
    # Customer Attributes
    tags: Optional[str] = Field(default=None)  # JSON string of tags
    loyalty_status: LoyaltyStatus = Field(default=LoyaltyStatus.NEW, index=True)
    
    # Status & Metadata
    is_active: bool = Field(default=True, index=True)
    notes: Optional[str] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    last_interaction: Optional[datetime] = Field(default=None)
    
    # Relationships
    interactions: List["Interaction"] = Relationship(back_populates="customer")
    feedback: List["Feedback"] = Relationship(back_populates="customer")
    
    def get_display_name(self) -> str:
        """Get display name based on contact type"""
        if self.contact_type == ContactType.CORPORATE:
            return self.company_name or "Unknown Company"
        return self.full_name or "Unknown Customer"
    
    def get_tags_list(self) -> List[str]:
        """Parse tags from JSON string"""
        if not self.tags:
            return []
        try:
            import json
            return json.loads(self.tags)
        except:
            return []
    
    def set_tags_list(self, tags: List[str]):
        """Set tags as JSON string"""
        import json
        self.tags = json.dumps(tags) if tags else None