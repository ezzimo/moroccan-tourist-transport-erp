"""
Notification utilities for HR service
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
                    "service": "hr_service"
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
                    "service": "hr_service"
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


# Convenience functions for common HR notifications

async def send_recruitment_notification(
    application_data: Dict[str, Any],
    notification_type: str = "new_application"
) -> bool:
    """Send recruitment notification
    
    Args:
        application_data: Application details
        notification_type: Type of notification
        
    Returns:
        True if sent successfully
    """
    notification_service = NotificationService()
    
    # Get HR managers (mock - would come from user service)
    hr_managers = ["hr_manager_1", "hr_manager_2"]
    
    template_name = f"hr_{notification_type}"
    variables = {
        "applicant_name": application_data.get("applicant_name", ""),
        "position": application_data.get("position", ""),
        "source": application_data.get("source", ""),
        "email": application_data.get("email", ""),
        "stage": application_data.get("stage", ""),
        "rejection_reason": application_data.get("rejection_reason", "")
    }
    
    # Determine priority based on notification type
    priority = "high" if notification_type in ["new_application", "stage_change"] else "medium"
    
    return await notification_service.send_bulk_notification(
        recipient_ids=hr_managers,
        template_name=template_name,
        variables=variables,
        channels=["email", "push"],
        priority=priority
    )


async def send_training_notification(
    employee_id: str,
    training_data: Dict[str, Any],
    notification_type: str = "training_assigned"
) -> bool:
    """Send training notification to employee
    
    Args:
        employee_id: Employee UUID
        training_data: Training details
        notification_type: Type of notification
        
    Returns:
        True if sent successfully
    """
    notification_service = NotificationService()
    
    template_name = f"hr_{notification_type}"
    variables = {
        "employee_name": training_data.get("employee_name", ""),
        "training_title": training_data.get("training_title", ""),
        "start_date": training_data.get("start_date", ""),
        "location": training_data.get("location", ""),
        "trainer": training_data.get("trainer", "")
    }
    
    return await notification_service.send_notification(
        recipient_id=employee_id,
        template_name=template_name,
        variables=variables,
        channels=["email", "sms"],
        priority="medium"
    )


async def send_document_notification(
    employee_id: str,
    document_data: Dict[str, Any],
    notification_type: str = "document_uploaded"
) -> bool:
    """Send document notification
    
    Args:
        employee_id: Employee UUID
        document_data: Document details
        notification_type: Type of notification
        
    Returns:
        True if sent successfully
    """
    notification_service = NotificationService()
    
    template_name = f"hr_{notification_type}"
    variables = {
        "employee_name": document_data.get("employee_name", ""),
        "document_title": document_data.get("document_title", ""),
        "document_type": document_data.get("document_type", ""),
        "status": document_data.get("status", ""),
        "rejection_reason": document_data.get("rejection_reason", "")
    }
    
    return await notification_service.send_notification(
        recipient_id=employee_id,
        template_name=template_name,
        variables=variables,
        channels=["email"],
        priority="medium"
    )


async def send_expiry_alert(
    employee_id: str,
    employee_name: str,
    item_type: str,
    expiry_date: date,
    days_remaining: int
) -> bool:
    """Send expiry alert notification
    
    Args:
        employee_id: Employee UUID
        employee_name: Employee full name
        item_type: Type of expiring item
        expiry_date: Expiry date
        days_remaining: Days until expiry
        
    Returns:
        True if sent successfully
    """
    notification_service = NotificationService()
    
    template_name = f"hr_expiry_alert"
    variables = {
        "employee_name": employee_name,
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
        recipient_id=employee_id,
        template_name=template_name,
        variables=variables,
        channels=["email", "sms"],
        priority=priority
    )


async def send_compliance_alert(
    compliance_data: Dict[str, Any],
    recipients: List[str]
) -> Dict[str, bool]:
    """Send compliance alert to HR management
    
    Args:
        compliance_data: Compliance alert details
        recipients: List of recipient user IDs
        
    Returns:
        Dict mapping recipient to success status
    """
    notification_service = NotificationService()
    
    template_name = "hr_compliance_alert"
    variables = {
        "alert_type": compliance_data.get("alert_type", ""),
        "employee_count": compliance_data.get("employee_count", 0),
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


async def send_onboarding_notification(
    employee_id: str,
    employee_data: Dict[str, Any]
) -> bool:
    """Send onboarding notification to new employee
    
    Args:
        employee_id: Employee UUID
        employee_data: Employee details
        
    Returns:
        True if sent successfully
    """
    notification_service = NotificationService()
    
    template_name = "hr_employee_onboarding"
    variables = {
        "employee_name": employee_data.get("employee_name", ""),
        "start_date": employee_data.get("start_date", ""),
        "department": employee_data.get("department", ""),
        "position": employee_data.get("position", ""),
        "manager_name": employee_data.get("manager_name", "")
    }
    
    return await notification_service.send_notification(
        recipient_id=employee_id,
        template_name=template_name,
        variables=variables,
        channels=["email"],
        priority="high"
    )