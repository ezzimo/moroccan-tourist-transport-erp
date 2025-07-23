"""
User preference-related Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from models.notification import NotificationChannel, NotificationType
import uuid


class UserPreferenceBase(BaseModel):
    user_id: uuid.UUID
    user_type: str = "user"
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    push_token: Optional[str] = None
    email_enabled: bool = True
    sms_enabled: bool = True
    push_enabled: bool = True
    whatsapp_enabled: bool = False
    preferred_language: str = "en"
    preferred_timezone: str = "Africa/Casablanca"


class UserPreferenceCreate(UserPreferenceBase):
    notification_preferences: Optional[Dict[str, Dict[str, bool]]] = None
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    quiet_hours_timezone: str = "Africa/Casablanca"
    max_emails_per_day: Optional[int] = None
    max_sms_per_day: Optional[int] = None
    
    @validator('quiet_hours_start', 'quiet_hours_end')
    def validate_time_format(cls, v):
        if v is not None:
            try:
                from datetime import datetime
                datetime.strptime(v, "%H:%M")
            except ValueError:
                raise ValueError('Time must be in HH:MM format')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.startswith('+'):
            raise ValueError('Phone number must include country code (e.g., +212...)')
        return v


class UserPreferenceUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    push_token: Optional[str] = None
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    whatsapp_enabled: Optional[bool] = None
    notification_preferences: Optional[Dict[str, Dict[str, bool]]] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    quiet_hours_timezone: Optional[str] = None
    max_emails_per_day: Optional[int] = None
    max_sms_per_day: Optional[int] = None
    preferred_language: Optional[str] = None
    preferred_timezone: Optional[str] = None
    is_active: Optional[bool] = None


class UserPreferenceResponse(UserPreferenceBase):
    id: uuid.UUID
    notification_preferences: Dict[str, Dict[str, bool]] = {}
    quiet_hours_enabled: bool
    quiet_hours_start: Optional[str]
    quiet_hours_end: Optional[str]
    quiet_hours_timezone: str
    max_emails_per_day: Optional[int]
    max_sms_per_day: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    enabled_channels: List[NotificationChannel] = []
    is_in_quiet_hours: bool


class ChannelPreference(BaseModel):
    """Individual channel preference"""
    channel: NotificationChannel
    enabled: bool
    contact_info: Optional[str] = None  # email or phone


class NotificationTypePreference(BaseModel):
    """Notification type preference for all channels"""
    notification_type: NotificationType
    channels: Dict[NotificationChannel, bool]


class BulkPreferenceUpdate(BaseModel):
    """Bulk preference update"""
    user_ids: List[uuid.UUID]
    preferences: UserPreferenceUpdate