"""
Notification model for tracking sent messages
"""
from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid
import json


class NotificationType(str, Enum):
    """Notification type enumeration"""
    BOOKING_CONFIRMED = "booking_confirmed"
    BOOKING_CANCELLED = "booking_cancelled"
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_FAILED = "payment_failed"
    TOUR_ASSIGNED = "tour_assigned"
    TOUR_REMINDER = "tour_reminder"
    TOUR_CANCELLED = "tour_cancelled"
    INCIDENT_REPORTED = "incident_reported"
    VEHICLE_MAINTENANCE = "vehicle_maintenance"
    DOCUMENT_EXPIRY = "document_expiry"
    TRAINING_ASSIGNED = "training_assigned"
    TRAINING_REMINDER = "training_reminder"
    CONTRACT_EXPIRY = "contract_expiry"
    SYSTEM_ALERT = "system_alert"
    CUSTOM = "custom"


class NotificationChannel(str, Enum):
    """Notification channel enumeration"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WHATSAPP = "whatsapp"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class NotificationStatus(str, Enum):
    """Notification status enumeration"""
    PENDING = "pending"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RecipientType(str, Enum):
    """Recipient type enumeration"""
    USER = "user"
    CUSTOMER = "customer"
    EMPLOYEE = "employee"
    ROLE = "role"
    DEPARTMENT = "department"
    ALL = "all"


class Notification(SQLModel, table=True):
    """Notification model for tracking sent messages"""
    __tablename__ = "notifications"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Notification Details
    type: NotificationType = Field(index=True)
    channel: NotificationChannel = Field(index=True)
    
    # Recipient Information
    recipient_type: RecipientType = Field(index=True)
    recipient_id: Optional[str] = Field(default=None, index=True)
    recipient_email: Optional[str] = Field(default=None, max_length=255)
    recipient_phone: Optional[str] = Field(default=None, max_length=20)
    recipient_name: Optional[str] = Field(default=None, max_length=255)
    
    # Message Content
    subject: Optional[str] = Field(default=None, max_length=500)
    message: str = Field(max_length=5000)
    payload: Optional[str] = Field(default=None)  # JSON string for additional data
    
    # Template Information
    template_id: Optional[uuid.UUID] = Field(default=None, index=True)
    template_variables: Optional[str] = Field(default=None)  # JSON string
    
    # Status and Tracking
    status: NotificationStatus = Field(default=NotificationStatus.PENDING, index=True)
    retry_count: int = Field(default=0, ge=0)
    max_retries: int = Field(default=3, ge=0)
    
    # Delivery Information
    sent_at: Optional[datetime] = Field(default=None)
    delivered_at: Optional[datetime] = Field(default=None)
    failed_at: Optional[datetime] = Field(default=None)
    
    # External References
    external_id: Optional[str] = Field(default=None, max_length=255)  # Provider message ID
    provider_response: Optional[str] = Field(default=None, max_length=1000)
    
    # Error Information
    error_message: Optional[str] = Field(default=None, max_length=1000)
    error_code: Optional[str] = Field(default=None, max_length=50)
    
    # Scheduling
    scheduled_at: Optional[datetime] = Field(default=None, index=True)
    expires_at: Optional[datetime] = Field(default=None)
    
    # Priority and Grouping
    priority: int = Field(default=5, ge=1, le=10)  # 1 = highest, 10 = lowest
    group_id: Optional[str] = Field(default=None, max_length=100, index=True)
    
    # Metadata
    source_service: Optional[str] = Field(default=None, max_length=50)
    source_event: Optional[str] = Field(default=None, max_length=100)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: Optional[datetime] = Field(default=None)
    
    def get_payload_dict(self) -> Dict[str, Any]:
        """Parse payload from JSON string"""
        if not self.payload:
            return {}
        try:
            return json.loads(self.payload)
        except:
            return {}
    
    def set_payload_dict(self, payload: Dict[str, Any]):
        """Set payload as JSON string"""
        self.payload = json.dumps(payload) if payload else None
    
    def get_template_variables_dict(self) -> Dict[str, Any]:
        """Parse template variables from JSON string"""
        if not self.template_variables:
            return {}
        try:
            return json.loads(self.template_variables)
        except:
            return {}
    
    def set_template_variables_dict(self, variables: Dict[str, Any]):
        """Set template variables as JSON string"""
        self.template_variables = json.dumps(variables) if variables else None
    
    def can_retry(self) -> bool:
        """Check if notification can be retried"""
        return (
            self.status == NotificationStatus.FAILED and
            self.retry_count < self.max_retries
        )
    
    def is_expired(self) -> bool:
        """Check if notification has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def should_send_now(self) -> bool:
        """Check if notification should be sent now"""
        if self.scheduled_at:
            return datetime.utcnow() >= self.scheduled_at
        return True