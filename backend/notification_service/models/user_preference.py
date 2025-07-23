"""
User preference model for notification settings
"""
from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from models.notification import NotificationChannel, NotificationType
import uuid
import json


class UserPreference(SQLModel, table=True):
    """User preference model for notification settings"""
    __tablename__ = "user_preferences"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # User Identification
    user_id: uuid.UUID = Field(unique=True, index=True)
    user_type: str = Field(default="user", max_length=20)  # user, customer, employee
    
    # Contact Information
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    push_token: Optional[str] = Field(default=None, max_length=500)
    
    # Channel Preferences (JSON)
    email_enabled: bool = Field(default=True)
    sms_enabled: bool = Field(default=True)
    push_enabled: bool = Field(default=True)
    whatsapp_enabled: bool = Field(default=False)
    
    # Notification Type Preferences (JSON)
    notification_preferences: Optional[str] = Field(default=None)  # JSON mapping
    
    # Quiet Hours
    quiet_hours_enabled: bool = Field(default=False)
    quiet_hours_start: Optional[str] = Field(default=None, max_length=5)  # HH:MM
    quiet_hours_end: Optional[str] = Field(default=None, max_length=5)    # HH:MM
    quiet_hours_timezone: str = Field(default="Africa/Casablanca", max_length=50)
    
    # Frequency Limits
    max_emails_per_day: Optional[int] = Field(default=None, ge=0)
    max_sms_per_day: Optional[int] = Field(default=None, ge=0)
    
    # Language and Formatting
    preferred_language: str = Field(default="en", max_length=5)
    preferred_timezone: str = Field(default="Africa/Casablanca", max_length=50)
    
    # Status
    is_active: bool = Field(default=True, index=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    def get_notification_preferences_dict(self) -> Dict[str, Dict[str, bool]]:
        """Parse notification preferences from JSON string"""
        if not self.notification_preferences:
            return {}
        try:
            return json.loads(self.notification_preferences)
        except:
            return {}
    
    def set_notification_preferences_dict(self, preferences: Dict[str, Dict[str, bool]]):
        """Set notification preferences as JSON string"""
        self.notification_preferences = json.dumps(preferences) if preferences else None
    
    def is_channel_enabled(self, channel: NotificationChannel) -> bool:
        """Check if a specific channel is enabled"""
        if channel == NotificationChannel.EMAIL:
            return self.email_enabled and bool(self.email)
        elif channel == NotificationChannel.SMS:
            return self.sms_enabled and bool(self.phone)
        elif channel == NotificationChannel.PUSH:
            return self.push_enabled and bool(self.push_token)
        elif channel == NotificationChannel.WHATSAPP:
            return self.whatsapp_enabled and bool(self.phone)
        return False
    
    def is_notification_type_enabled(
        self, 
        notification_type: NotificationType, 
        channel: NotificationChannel
    ) -> bool:
        """Check if a specific notification type is enabled for a channel"""
        if not self.is_channel_enabled(channel):
            return False
        
        preferences = self.get_notification_preferences_dict()
        type_prefs = preferences.get(notification_type.value, {})
        
        # Default to enabled if not specified
        return type_prefs.get(channel.value, True)
    
    def is_in_quiet_hours(self) -> bool:
        """Check if current time is within quiet hours"""
        if not self.quiet_hours_enabled or not self.quiet_hours_start or not self.quiet_hours_end:
            return False
        
        from datetime import datetime
        import pytz
        
        try:
            tz = pytz.timezone(self.quiet_hours_timezone)
            now = datetime.now(tz)
            current_time = now.time()
            
            start_time = datetime.strptime(self.quiet_hours_start, "%H:%M").time()
            end_time = datetime.strptime(self.quiet_hours_end, "%H:%M").time()
            
            if start_time <= end_time:
                return start_time <= current_time <= end_time
            else:
                # Quiet hours span midnight
                return current_time >= start_time or current_time <= end_time
        except:
            return False
    
    def get_enabled_channels(self) -> List[NotificationChannel]:
        """Get list of enabled channels"""
        channels = []
        
        if self.is_channel_enabled(NotificationChannel.EMAIL):
            channels.append(NotificationChannel.EMAIL)
        if self.is_channel_enabled(NotificationChannel.SMS):
            channels.append(NotificationChannel.SMS)
        if self.is_channel_enabled(NotificationChannel.PUSH):
            channels.append(NotificationChannel.PUSH)
        if self.is_channel_enabled(NotificationChannel.WHATSAPP):
            channels.append(NotificationChannel.WHATSAPP)
        
        return channels