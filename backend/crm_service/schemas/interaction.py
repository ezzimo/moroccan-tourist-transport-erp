"""
Interaction-related Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.interaction import ChannelType
import uuid


class InteractionBase(BaseModel):
    channel: ChannelType
    subject: Optional[str] = None
    summary: str
    duration_minutes: Optional[int] = None
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None


class InteractionCreate(InteractionBase):
    customer_id: uuid.UUID
    staff_member_id: Optional[uuid.UUID] = None


class InteractionUpdate(BaseModel):
    subject: Optional[str] = None
    summary: Optional[str] = None
    duration_minutes: Optional[int] = None
    follow_up_required: Optional[bool] = None
    follow_up_date: Optional[datetime] = None


class InteractionResponse(InteractionBase):
    id: uuid.UUID
    customer_id: uuid.UUID
    staff_member_id: Optional[uuid.UUID]
    timestamp: datetime
    created_at: datetime


class InteractionStats(BaseModel):
    """Interaction statistics"""
    total_interactions: int
    by_channel: dict
    by_month: dict
    average_duration: Optional[float]
    follow_ups_pending: int