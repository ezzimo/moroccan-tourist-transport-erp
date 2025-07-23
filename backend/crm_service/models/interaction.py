"""
Interaction model for customer communication tracking
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class ChannelType(str, Enum):
    """Communication channel enumeration"""
    EMAIL = "email"
    PHONE = "phone"
    CHAT = "chat"
    IN_PERSON = "in-person"
    WHATSAPP = "whatsapp"
    SMS = "sms"


class Interaction(SQLModel, table=True):
    """Interaction model for tracking customer communications"""
    __tablename__ = "interactions"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Foreign Keys
    customer_id: uuid.UUID = Field(foreign_key="customers.id", index=True)
    staff_member_id: Optional[uuid.UUID] = Field(default=None, index=True)
    
    # Interaction Details
    channel: ChannelType = Field(index=True)
    subject: Optional[str] = Field(default=None, max_length=255)
    summary: str = Field(max_length=2000)
    
    # Metadata
    duration_minutes: Optional[int] = Field(default=None)
    follow_up_required: bool = Field(default=False)
    follow_up_date: Optional[datetime] = Field(default=None)
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    customer: Optional["Customer"] = Relationship(back_populates="interactions")