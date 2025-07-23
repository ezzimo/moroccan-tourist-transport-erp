"""
Notification-related Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from models.notification import (
    NotificationType, NotificationChannel, NotificationStatus, RecipientType
)
import uuid


class NotificationBase(BaseModel):
    type: NotificationType
    channel: NotificationChannel
    recipient_type: RecipientType
    recipient_id: Optional[str] = None
    recipient_email: Optional[EmailStr] = None
    recipient_phone: Optional[str] = None
    recipient_name: Optional[str] = None
    subject: Optional[str] = None
    message: str
    payload: Optional[Dict[str, Any]] = None
    priority: int = 5
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class NotificationCreate(NotificationBase):
    template_id: Optional[uuid.UUID] = None
    template_variables: Optional[Dict[str, Any]] = None
    max_retries: int = 3
    source_service: Optional[str] = None
    source_event: Optional[str] = None
    group_id: Optional[str] = None
    
    @validator('priority')
    def validate_priority(cls, v):
        if v < 1 or v > 10:
            raise ValueError('Priority must be between 1 and 10')
        return v
    
    @validator('recipient_email')
    def validate_recipient_contact(cls, v, values):
        channel = values.get('channel')
        recipient_phone = values.get('recipient_phone')
        
        if channel == NotificationChannel.EMAIL and not v:
            raise ValueError('Email is required for email notifications')
        elif channel == NotificationChannel.SMS and not recipient_phone:
            raise ValueError('Phone is required for SMS notifications')
        
        return v


class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatus] = None
    external_id: Optional[str] = None
    provider_response: Optional[str] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None


class NotificationResponse(NotificationBase):
    id: uuid.UUID
    template_id: Optional[uuid.UUID]
    template_variables: Dict[str, Any] = {}
    status: NotificationStatus
    retry_count: int
    max_retries: int
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    failed_at: Optional[datetime]
    external_id: Optional[str]
    provider_response: Optional[str]
    error_message: Optional[str]
    error_code: Optional[str]
    source_service: Optional[str]
    source_event: Optional[str]
    group_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    can_retry: bool
    is_expired: bool
    should_send_now: bool


class NotificationSend(BaseModel):
    """Schema for sending notifications"""
    type: NotificationType
    recipients: List[Dict[str, Any]]  # List of recipient info
    template_id: Optional[uuid.UUID] = None
    template_variables: Optional[Dict[str, Any]] = None
    channels: Optional[List[NotificationChannel]] = None
    priority: int = 5
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    source_service: Optional[str] = None
    source_event: Optional[str] = None
    group_id: Optional[str] = None
    
    @validator('recipients')
    def validate_recipients(cls, v):
        if not v:
            raise ValueError('At least one recipient is required')
        return v


class NotificationBulkSend(BaseModel):
    """Schema for bulk notification sending"""
    type: NotificationType
    channel: NotificationChannel
    template_id: uuid.UUID
    recipients: List[Dict[str, Any]]
    template_variables: Optional[Dict[str, Any]] = None
    priority: int = 5
    scheduled_at: Optional[datetime] = None
    source_service: Optional[str] = None
    group_id: Optional[str] = None


class NotificationSearch(BaseModel):
    """Notification search criteria"""
    type: Optional[NotificationType] = None
    channel: Optional[NotificationChannel] = None
    status: Optional[NotificationStatus] = None
    recipient_type: Optional[RecipientType] = None
    recipient_id: Optional[str] = None
    recipient_email: Optional[str] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    source_service: Optional[str] = None
    group_id: Optional[str] = None


class NotificationStats(BaseModel):
    """Notification statistics"""
    total_notifications: int
    by_status: Dict[str, int]
    by_channel: Dict[str, int]
    by_type: Dict[str, int]
    delivery_rate: float
    average_delivery_time_minutes: Optional[float]
    failed_notifications: int
    retry_rate: float