"""
Notification utilities for fleet management
"""
import redis
import json
from typing import Dict, Any, Optional
from datetime import datetime, date
from config import settings
import uuid


class NotificationService:
    """Service for sending fleet-related notifications"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def send_compliance_alert(self, vehicle_id: uuid.UUID, alert_type: str, data: Dict[str, Any]):
        """Send compliance alert notification"""
        notification = {
            "type": "compliance_alert",
            "vehicle_id": str(vehicle_id),
            "alert_type": alert_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Publish to Redis channel for real-time alerts
        self.redis.publish("fleet_compliance_alerts", json.dumps(notification))
        
        # Store alert for offline access
        alert_key = f"alerts:compliance:{vehicle_id}"
        self.redis.lpush(alert_key, json.dumps(notification))
        self.redis.ltrim(alert_key, 0, 99)  # Keep last 100 alerts
        self.redis.expire(alert_key, 86400 * 30)  # Expire after 30 days
    
    async def send_maintenance_reminder(self, vehicle_id: uuid.UUID, maintenance_type: str, data: Dict[str, Any]):
        """Send maintenance reminder notification"""
        notification = {
            "type": "maintenance_reminder",
            "vehicle_id": str(vehicle_id),
            "maintenance_type": maintenance_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Publish to Redis channel
        self.redis.publish("fleet_maintenance_reminders", json.dumps(notification))
        
        # Store reminder
        reminder_key = f"reminders:maintenance:{vehicle_id}"
        self.redis.setex(reminder_key, 86400 * 7, json.dumps(notification))  # Keep for 7 days
    
    async def send_assignment_update(self, vehicle_id: uuid.UUID, assignment_id: uuid.UUID, update_type: str):
        """Send assignment update notification"""
        notification = {
            "type": "assignment_update",
            "vehicle_id": str(vehicle_id),
            "assignment_id": str(assignment_id),
            "update_type": update_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Publish to vehicle-specific channel
        vehicle_channel = f"fleet_updates:{vehicle_id}"
        self.redis.publish(vehicle_channel, json.dumps(notification))
        
        # Publish to general fleet channel
        self.redis.publish("fleet_assignment_updates", json.dumps(notification))


async def send_compliance_alert(redis_client: redis.Redis, vehicle_id: uuid.UUID, alert_type: str, data: Dict[str, Any]):
    """Helper function to send compliance alert"""
    notification_service = NotificationService(redis_client)
    await notification_service.send_compliance_alert(vehicle_id, alert_type, data)


async def send_maintenance_reminder(redis_client: redis.Redis, vehicle_id: uuid.UUID, maintenance_type: str, data: Dict[str, Any]):
    """Helper function to send maintenance reminder"""
    notification_service = NotificationService(redis_client)
    await notification_service.send_maintenance_reminder(vehicle_id, maintenance_type, data)