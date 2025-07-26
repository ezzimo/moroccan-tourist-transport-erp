"""
Notification utilities for QA service
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
                    "service": "qa_service"
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
                    "service": "qa_service"
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


# Convenience functions for common QA notifications

async def send_audit_notification(
    audit_id: str,
    audit_data: Dict[str, Any],
    notification_type: str = "audit_scheduled"
) -> bool:
    """Send audit notification
    
    Args:
        audit_id: Audit UUID
        audit_data: Audit details
        notification_type: Type of notification
        
    Returns:
        True if sent successfully
    """
    notification_service = NotificationService()
    
    template_name = f"qa_{notification_type}"
    variables = {
        "audit_number": audit_data.get("audit_number", ""),
        "entity_type": audit_data.get("entity_type", ""),
        "scheduled_date": audit_data.get("scheduled_date", ""),
        "auditor_id": audit_data.get("auditor_id", "")
    }
    
    # Determine priority based on notification type
    priority_map = {
        "audit_scheduled": "medium",
        "audit_overdue": "high",
        "audit_completed": "low"
    }
    priority = priority_map.get(notification_type, "medium")
    
    return await notification_service.send_notification(
        recipient_id=audit_data.get("auditor_id", ""),
        template_name=template_name,
        variables=variables,
        channels=["email", "push"],
        priority=priority
    )


async def send_nonconformity_alert(
    nonconformity_id: str,
    nonconformity_data: Dict[str, Any],
    notification_type: str = "nonconformity_created"
) -> bool:
    """Send non-conformity alert
    
    Args:
        nonconformity_id: Non-conformity UUID
        nonconformity_data: Non-conformity details
        notification_type: Type of notification
        
    Returns:
        True if sent successfully
    """
    notification_service = NotificationService()
    
    template_name = f"qa_{notification_type}"
    variables = {
        "nc_number": nonconformity_data.get("nc_number", ""),
        "severity": nonconformity_data.get("severity", ""),
        "description": nonconformity_data.get("description", "")[:200] + "..." if len(nonconformity_data.get("description", "")) > 200 else nonconformity_data.get("description", ""),
        "audit_number": nonconformity_data.get("audit_number", "")
    }
    
    # Determine priority based on severity
    severity = nonconformity_data.get("severity", "").lower()
    if severity == "critical":
        priority = "urgent"
        channels = ["email", "sms", "push"]
    elif severity == "major":
        priority = "high"
        channels = ["email", "push"]
    else:
        priority = "medium"
        channels = ["email"]
    
    # Send to QA managers (mock - would come from user service)
    qa_managers = ["qa_manager_1", "qa_manager_2"]
    
    return await notification_service.send_bulk_notification(
        recipient_ids=qa_managers,
        template_name=template_name,
        variables=variables,
        channels=channels,
        priority=priority
    )


async def send_compliance_alert(
    requirement_id: str,
    compliance_data: Dict[str, Any],
    notification_type: str = "compliance_due"
) -> bool:
    """Send compliance alert
    
    Args:
        requirement_id: Requirement UUID
        compliance_data: Compliance details
        notification_type: Type of notification
        
    Returns:
        True if sent successfully
    """
    notification_service = NotificationService()
    
    template_name = f"qa_{notification_type}"
    variables = {
        "title": compliance_data.get("title", ""),
        "domain": compliance_data.get("domain", ""),
        "required_by": compliance_data.get("required_by", ""),
        "status": compliance_data.get("status", "")
    }
    
    # Determine priority based on notification type
    priority_map = {
        "compliance_due": "high",
        "compliance_expired": "urgent",
        "compliance_met": "low"
    }
    priority = priority_map.get(notification_type, "medium")
    
    # Send to compliance officers (mock - would come from user service)
    compliance_officers = ["compliance_officer_1", "compliance_officer_2"]
    
    return await notification_service.send_bulk_notification(
        recipient_ids=compliance_officers,
        template_name=template_name,
        variables=variables,
        channels=["email", "push"],
        priority=priority
    )


async def send_certification_alert(
    certification_id: str,
    certification_data: Dict[str, Any],
    notification_type: str = "certification_expiring"
) -> bool:
    """Send certification alert
    
    Args:
        certification_id: Certification UUID
        certification_data: Certification details
        notification_type: Type of notification
        
    Returns:
        True if sent successfully
    """
    notification_service = NotificationService()
    
    template_name = f"qa_{notification_type}"
    variables = {
        "certificate_number": certification_data.get("certificate_number", ""),
        "name": certification_data.get("name", ""),
        "entity_type": certification_data.get("entity_type", ""),
        "expiry_date": certification_data.get("expiry_date", ""),
        "suspension_reason": certification_data.get("suspension_reason", "")
    }
    
    # Determine priority based on notification type
    priority_map = {
        "certification_expiring": "high",
        "certification_expired": "urgent",
        "certification_suspended": "urgent",
        "certification_renewed": "low"
    }
    priority = priority_map.get(notification_type, "medium")
    
    # Send to relevant managers (mock - would come from user service)
    managers = ["qa_manager", "operations_manager", "compliance_officer"]
    
    return await notification_service.send_bulk_notification(
        recipient_ids=managers,
        template_name=template_name,
        variables=variables,
        channels=["email", "push"],
        priority=priority
    )


async def send_qa_dashboard_alert(
    dashboard_data: Dict[str, Any],
    recipients: List[str]
) -> Dict[str, bool]:
    """Send QA dashboard alert to management
    
    Args:
        dashboard_data: Dashboard alert details
        recipients: List of recipient user IDs
        
    Returns:
        Dict mapping recipient to success status
    """
    notification_service = NotificationService()
    
    template_name = "qa_dashboard_alert"
    variables = {
        "alert_type": dashboard_data.get("alert_type", ""),
        "overdue_audits": dashboard_data.get("overdue_audits", 0),
        "critical_nonconformities": dashboard_data.get("critical_nonconformities", 0),
        "expiring_certifications": dashboard_data.get("expiring_certifications", 0),
        "compliance_issues": dashboard_data.get("compliance_issues", 0),
        "report_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    return await notification_service.send_bulk_notification(
        recipient_ids=recipients,
        template_name=template_name,
        variables=variables,
        channels=["email"],
        priority="high"
    )