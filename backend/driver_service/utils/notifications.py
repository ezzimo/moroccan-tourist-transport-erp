"""
Notification utilities for driver service
"""
import httpx
from typing import Dict, Any, List, Optional
from datetime import date, datetime
from config import settings
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications via notification microservice"""
    
    def __init__(self):
        self.notification_service_url = settings.notification_service_url
        self.timeout = 30.0
    
    async def send_notification(
        self,
        recipient_id: str,
        template_name: str,
        variables: Dict[str, Any],
        channels: List[str] = None,
        priority: str = "medium"
    ) -> bool:
        """Send notification via notification service
        
        Args:
            recipient_id: User ID to send notification to
            template_name: Notification template name
            variables: Template variables
            channels: Notification channels (email, sms, push)
            priority: Notification priority (low, medium, high, urgent)
            
        Returns:
            True if sent successfully
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "recipient_id": recipient_id,
                    "template_name": template_name,
                    "variables": variables,
                    "channels": channels or ["email"],
                    "priority": priority,
                    "service": "driver_service"
                }
                
                response = await client.post(
                    f"{self.notification_service_url}/api/v1/notifications/send",
                    json=payload
                )
                
                if response.status_code == 200:
                    logger.info(f"Notification sent successfully to {recipient_id}")
                    return True
                else:
                    logger.error(f"Failed to send notification: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return False
    
    async def send_bulk_notification(
        self,
        recipient_ids: List[str],
        template_name: str,
        variables: Dict[str, Any],
        channels: List[str] = None,
        priority: str = "medium"
    ) -> Dict[str, bool]:
        """Send bulk notifications
        
        Args:
            recipient_ids: List of user IDs
            template_name: Notification template name
            variables: Template variables
            channels: Notification channels
            priority: Notification priority
            
        Returns:
            Dict mapping recipient_id to success status
        """
        results = {}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "recipient_ids": recipient_ids,
                    "template_name": template_name,
                    "variables": variables,
                    "channels": channels or ["email"],
                    "priority": priority,
                    "service": "driver_service"
                }
                
                response = await client.post(
                    f"{self.notification_service_url}/api/v1/notifications/send-bulk",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", {})
                    logger.info(f"Bulk notification sent to {len(recipient_ids)} recipients")
                else:
                    logger.error(f"Failed to send bulk notification: {response.status_code}")
                    # Mark all as failed
                    results = {recipient_id: False for recipient_id in recipient_ids}
                    
        except Exception as e:
            logger.error(f"Error sending bulk notification: {str(e)}")
            results = {recipient_id: False for recipient_id in recipient_ids}
        
        return results


# Convenience functions for common notifications

async def send_expiry_alert(
    driver_id: str,
    driver_name: str,
    item_type: str,
    expiry_date: date,
    days_remaining: int
) -> bool:
    """Send expiry alert notification
    
    Args:
        driver_id: Driver UUID
        driver_name: Driver full name
        item_type: Type of expiring item (license, health_cert, etc.)
        expiry_date: Expiry date
        days_remaining: Days until expiry
        
    Returns:
        True if sent successfully
    """
    notification_service = NotificationService()
    
    template_name = f"driver_{item_type}_expiry_alert"
    variables = {
        "driver_name": driver_name,
        "item_type": item_type.replace("_", " ").title(),
        "expiry_date": expiry_date.strftime("%Y-%m-%d"),
        "days_remaining": days_remaining
    }
    
    # Determine priority based on days remaining
    if days_remaining <= 7:
        priority = "urgent"
    elif days_remaining <= 14:
        priority = "high"
    else:
        priority = "medium"
    
    return await notification_service.send_notification(
        recipient_id=driver_id,
        template_name=template_name,
        variables=variables,
        channels=["email", "sms"],
        priority=priority
    )


async def send_assignment_notification(
    driver_id: str,
    assignment_data: Dict[str, Any],
    notification_type: str = "new_assignment"
) -> bool:
    """Send assignment notification to driver
    
    Args:
        driver_id: Driver UUID
        assignment_data: Assignment details
        notification_type: Type of notification (new_assignment, assignment_updated, etc.)
        
    Returns:
        True if sent successfully
    """
    notification_service = NotificationService()
    
    template_name = f"driver_{notification_type}"
    variables = {
        "driver_name": assignment_data.get("driver_name", ""),
        "tour_title": assignment_data.get("tour_title", ""),
        "start_date": assignment_data.get("start_date", ""),
        "end_date": assignment_data.get("end_date", ""),
        "pickup_location": assignment_data.get("pickup_location", ""),
        "special_instructions": assignment_data.get("special_instructions", "")
    }
    
    return await notification_service.send_notification(
        recipient_id=driver_id,
        template_name=template_name,
        variables=variables,
        channels=["email", "push"],
        priority="high"
    )


async def send_training_notification(
    driver_id: str,
    training_data: Dict[str, Any],
    notification_type: str = "training_scheduled"
) -> bool:
    """Send training notification to driver
    
    Args:
        driver_id: Driver UUID
        training_data: Training details
        notification_type: Type of notification
        
    Returns:
        True if sent successfully
    """
    notification_service = NotificationService()
    
    template_name = f"driver_{notification_type}"
    variables = {
        "driver_name": training_data.get("driver_name", ""),
        "training_title": training_data.get("training_title", ""),
        "training_type": training_data.get("training_type", ""),
        "scheduled_date": training_data.get("scheduled_date", ""),
        "location": training_data.get("location", ""),
        "trainer_name": training_data.get("trainer_name", "")
    }
    
    return await notification_service.send_notification(
        recipient_id=driver_id,
        template_name=template_name,
        variables=variables,
        channels=["email", "sms"],
        priority="medium"
    )


async def send_incident_notification(
    incident_data: Dict[str, Any],
    recipients: List[str],
    notification_type: str = "incident_reported"
) -> Dict[str, bool]:
    """Send incident notification to multiple recipients
    
    Args:
        incident_data: Incident details
        recipients: List of recipient user IDs
        notification_type: Type of notification
        
    Returns:
        Dict mapping recipient to success status
    """
    notification_service = NotificationService()
    
    template_name = f"driver_{notification_type}"
    variables = {
        "driver_name": incident_data.get("driver_name", ""),
        "incident_type": incident_data.get("incident_type", ""),
        "severity": incident_data.get("severity", ""),
        "incident_date": incident_data.get("incident_date", ""),
        "location": incident_data.get("location", ""),
        "description": incident_data.get("description", "")[:200] + "..." if len(incident_data.get("description", "")) > 200 else incident_data.get("description", "")
    }
    
    # Determine priority based on severity
    severity = incident_data.get("severity", "").lower()
    if severity in ["critical", "major"]:
        priority = "urgent"
    elif severity == "moderate":
        priority = "high"
    else:
        priority = "medium"
    
    return await notification_service.send_bulk_notification(
        recipient_ids=recipients,
        template_name=template_name,
        variables=variables,
        channels=["email", "push"],
        priority=priority
    )


async def send_compliance_alert(
    compliance_data: Dict[str, Any],
    recipients: List[str]
) -> Dict[str, bool]:
    """Send compliance alert to management
    
    Args:
        compliance_data: Compliance alert details
        recipients: List of recipient user IDs
        
    Returns:
        Dict mapping recipient to success status
    """
    notification_service = NotificationService()
    
    template_name = "driver_compliance_alert"
    variables = {
        "alert_type": compliance_data.get("alert_type", ""),
        "driver_count": compliance_data.get("driver_count", 0),
        "critical_count": compliance_data.get("critical_count", 0),
        "warning_count": compliance_data.get("warning_count", 0),
        "report_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    return await notification_service.send_bulk_notification(
        recipient_ids=recipients,
        template_name=template_name,
        variables=variables,
        channels=["email"],
        priority="high"
    )