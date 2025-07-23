"""
Feedback-related Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.feedback import ServiceType
import uuid


class FeedbackBase(BaseModel):
    service_type: ServiceType
    rating: int
    comments: Optional[str] = None
    is_anonymous: bool = False
    source: str = "web"


class FeedbackCreate(FeedbackBase):
    customer_id: uuid.UUID
    booking_id: Optional[uuid.UUID] = None


class FeedbackUpdate(BaseModel):
    resolved: Optional[bool] = None
    resolution_notes: Optional[str] = None
    resolved_by: Optional[uuid.UUID] = None


class FeedbackResponse(FeedbackBase):
    id: uuid.UUID
    customer_id: uuid.UUID
    booking_id: Optional[uuid.UUID]
    resolved: bool
    resolution_notes: Optional[str]
    resolved_by: Optional[uuid.UUID]
    resolved_at: Optional[datetime]
    submitted_at: datetime
    created_at: datetime
    sentiment: str


class FeedbackStats(BaseModel):
    """Feedback statistics"""
    total_feedback: int
    average_rating: float
    rating_distribution: dict
    by_service_type: dict
    sentiment_analysis: dict
    resolution_rate: float
    pending_resolution: int