"""
Database models for the notification microservice
"""
from .notification import (
    Notification, NotificationType, NotificationChannel, 
    NotificationStatus, RecipientType
)
from .template import Template, TemplateType
from .user_preference import UserPreference

__all__ = [
    "Notification", "NotificationType", "NotificationChannel", 
    "NotificationStatus", "RecipientType",
    "Template", "TemplateType",
    "UserPreference"
]