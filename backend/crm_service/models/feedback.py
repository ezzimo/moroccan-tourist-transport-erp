"""
Feedback model for customer service evaluation
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class ServiceType(str, Enum):
    """Service type enumeration for feedback"""
    TOUR = "Tour"
    BOOKING = "Booking"
    SUPPORT = "Support"
    TRANSPORT = "Transport"
    ACCOMMODATION = "Accommodation"
    GENERAL = "General"


class Feedback(SQLModel, table=True):
    """Feedback model for customer service evaluation"""
    __tablename__ = "feedback"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Foreign Keys
    customer_id: uuid.UUID = Field(foreign_key="customers.id", index=True)
    booking_id: Optional[uuid.UUID] = Field(default=None, index=True)  # Reference to booking service
    
    # Feedback Details
    service_type: ServiceType = Field(index=True)
    rating: int = Field(ge=1, le=5, index=True)
    comments: Optional[str] = Field(default=None, max_length=2000)
    
    # Resolution Tracking
    resolved: bool = Field(default=False, index=True)
    resolution_notes: Optional[str] = Field(default=None, max_length=1000)
    resolved_by: Optional[uuid.UUID] = Field(default=None)
    resolved_at: Optional[datetime] = Field(default=None)
    
    # Metadata
    is_anonymous: bool = Field(default=False)
    source: str = Field(default="web", max_length=50)  # web, mobile, email, etc.
    
    # Timestamps
    submitted_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    customer: Optional["Customer"] = Relationship(back_populates="feedback")
    
    def get_sentiment(self) -> str:
        """Get sentiment based on rating"""
        if self.rating >= 4:
            return "positive"
        elif self.rating == 3:
            return "neutral"
        else:
            return "negative"