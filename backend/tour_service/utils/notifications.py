"""
Notification utilities for real-time updates
"""
import redis
import json
from typing import Dict, Any, Optional
from datetime import datetime
from config import settings
import uuid


class NotificationService:
    """Service for sending real-time notifications"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def send_tour_update(self, tour_id: uuid.UUID, update_type: str, data: Dict[str, Any]):
        """Send tour update notification"""
        notification = {
            "type": "tour_update",
            "tour_id": str(tour_id),
            "update_type": update_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Publish to Redis channel for real-time updates
        channel = f"tour_updates:{tour_id}"
        self.redis.publish(channel, json.dumps(notification))
        
        # Store notification for offline access
        notification_key = f"notifications:tour:{tour_id}"
        self.redis.lpush(notification_key, json.dumps(notification))
        self.redis.ltrim(notification_key, 0, 99)  # Keep last 100 notifications
        self.redis.expire(notification_key, 86400 * 7)  # Expire after 7 days
    
    async def send_incident_alert(self, incident_id: uuid.UUID, tour_id: uuid.UUID, severity: str, data: Dict[str, Any]):
        """Send incident alert notification"""
        notification = {
            "type": "incident_alert",
            "incident_id": str(incident_id),
            "tour_id": str(tour_id),
            "severity": severity,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Publish to general incidents channel
        self.redis.publish("incident_alerts", json.dumps(notification))
        
        # Publish to tour-specific channel
        tour_channel = f"tour_updates:{tour_id}"
        self.redis.publish(tour_channel, json.dumps(notification))
        
        # Store alert for offline access
        alert_key = f"alerts:incident:{incident_id}"
        self.redis.setex(alert_key, 86400 * 30, json.dumps(notification))  # Keep for 30 days
    
    async def send_itinerary_update(self, tour_id: uuid.UUID, day_number: int, data: Dict[str, Any]):
        """Send itinerary update notification"""
        notification = {
            "type": "itinerary_update",
            "tour_id": str(tour_id),
            "day_number": day_number,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Publish to tour channel
        channel = f"tour_updates:{tour_id}"
        self.redis.publish(channel, json.dumps(notification))
    
    async def send_assignment_update(self, tour_id: uuid.UUID, assignment_type: str, resource_id: uuid.UUID):
        """Send resource assignment notification"""
        notification = {
            "type": "assignment_update",
            "tour_id": str(tour_id),
            "assignment_type": assignment_type,
            "resource_id": str(resource_id),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Publish to tour channel
        channel = f"tour_updates:{tour_id}"
        self.redis.publish(channel, json.dumps(notification))
        
        # Publish to resource-specific channel
        resource_channel = f"resource_updates:{assignment_type}:{resource_id}"
        self.redis.publish(resource_channel, json.dumps(notification))
    
    async def get_tour_notifications(self, tour_id: uuid.UUID, limit: int = 50) -> list:
        """Get recent notifications for a tour"""
        notification_key = f"notifications:tour:{tour_id}"
        notifications = self.redis.lrange(notification_key, 0, limit - 1)
        
        return [json.loads(notification) for notification in notifications]


async def send_tour_update(redis_client: redis.Redis, tour_id: uuid.UUID, update_type: str, data: Dict[str, Any]):
    """Helper function to send tour update"""
    notification_service = NotificationService(redis_client)
    await notification_service.send_tour_update(tour_id, update_type, data)


async def send_incident_alert(redis_client: redis.Redis, incident_id: uuid.UUID, tour_id: uuid.UUID, severity: str, data: Dict[str, Any]):
    """Helper function to send incident alert"""
    notification_service = NotificationService(redis_client)
    await notification_service.send_incident_alert(incident_id, tour_id, severity, data)