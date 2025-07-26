"""
Notification utilities for inventory service
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
                    "service": "inventory_service"
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
                    "service": "inventory_service"
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

async def send_low_stock_alert(
    item_id: str,
    item_name: str,
    current_quantity: int,
    reorder_level: int,
    supplier_id: Optional[str] = None
) -> bool:
    """Send low stock alert notification
    
    Args:
        item_id: Item UUID
        item_name: Item name
        current_quantity: Current stock quantity
        reorder_level: Reorder level threshold
        supplier_id: Supplier UUID (optional)
        
    Returns:
        True if sent successfully
    """
    notification_service = NotificationService()
    
    # Get inventory managers (mock - would come from HR service)
    inventory_managers = ["inventory_manager_1", "inventory_manager_2"]
    
    template_name = "inventory_low_stock_alert"
    variables = {
        "item_name": item_name,
        "current_quantity": current_quantity,
        "reorder_level": reorder_level,
        "shortage": reorder_level - current_quantity,
        "supplier_id": supplier_id
    }
    
    # Determine priority based on stock level
    if current_quantity == 0:
        priority = "urgent"
    elif current_quantity < reorder_level * 0.5:
        priority = "high"
    else:
        priority = "medium"
    
    results = await notification_service.send_bulk_notification(
        recipient_ids=inventory_managers,
        template_name=template_name,
        variables=variables,
        channels=["email", "push"],
        priority=priority
    )
    
    return any(results.values())


async def send_purchase_order_notification(
    supplier_id: str,
    order_data: Dict[str, Any],
    notification_type: str = "order_created"
) -> bool:
    """Send purchase order notification
    
    Args:
        supplier_id: Supplier UUID
        order_data: Purchase order details
        notification_type: Type of notification
        
    Returns:
        True if sent successfully
    """
    notification_service = NotificationService()
    
    # Get procurement team (mock - would come from HR service)
    procurement_team = ["procurement_manager", "purchasing_officer"]
    
    template_name = f"inventory_{notification_type}"
    variables = {
        "order_number": order_data.get("order_number", ""),
        "supplier_name": order_data.get("supplier_name", ""),
        "total_cost": order_data.get("total_cost", 0),
        "expected_delivery": order_data.get("expected_delivery", ""),
        "items_count": order_data.get("items_count", 0)
    }
    
    return await notification_service.send_bulk_notification(
        recipient_ids=procurement_team,
        template_name=template_name,
        variables=variables,
        channels=["email"],
        priority="medium"
    ) and any(procurement_team)


async def send_stock_movement_alert(
    movement_data: Dict[str, Any],
    recipients: List[str],
    notification_type: str = "stock_movement"
) -> Dict[str, bool]:
    """Send stock movement notification
    
    Args:
        movement_data: Movement details
        recipients: List of recipient user IDs
        notification_type: Type of notification
        
    Returns:
        Dict mapping recipient to success status
    """
    notification_service = NotificationService()
    
    template_name = f"inventory_{notification_type}"
    variables = {
        "item_name": movement_data.get("item_name", ""),
        "movement_type": movement_data.get("movement_type", ""),
        "quantity": movement_data.get("quantity", 0),
        "reference": movement_data.get("reference", ""),
        "performed_by": movement_data.get("performed_by", ""),
        "date": movement_data.get("date", "")
    }
    
    return await notification_service.send_bulk_notification(
        recipient_ids=recipients,
        template_name=template_name,
        variables=variables,
        channels=["email"],
        priority="low"
    )


async def send_supplier_performance_alert(
    supplier_data: Dict[str, Any],
    recipients: List[str]
) -> Dict[str, bool]:
    """Send supplier performance alert
    
    Args:
        supplier_data: Supplier performance details
        recipients: List of recipient user IDs
        
    Returns:
        Dict mapping recipient to success status
    """
    notification_service = NotificationService()
    
    template_name = "inventory_supplier_performance_alert"
    variables = {
        "supplier_name": supplier_data.get("supplier_name", ""),
        "performance_score": supplier_data.get("performance_score", 0),
        "issue_type": supplier_data.get("issue_type", ""),
        "recommendation": supplier_data.get("recommendation", ""),
        "report_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    # Determine priority based on performance score
    score = supplier_data.get("performance_score", 100)
    if score < 50:
        priority = "high"
    elif score < 70:
        priority = "medium"
    else:
        priority = "low"
    
    return await notification_service.send_bulk_notification(
        recipient_ids=recipients,
        template_name=template_name,
        variables=variables,
        channels=["email"],
        priority=priority
    )


async def send_reorder_recommendation(
    reorder_data: Dict[str, Any],
    recipients: List[str]
) -> Dict[str, bool]:
    """Send reorder recommendation notification
    
    Args:
        reorder_data: Reorder recommendation details
        recipients: List of recipient user IDs
        
    Returns:
        Dict mapping recipient to success status
    """
    notification_service = NotificationService()
    
    template_name = "inventory_reorder_recommendation"
    variables = {
        "items_count": reorder_data.get("items_count", 0),
        "total_cost": reorder_data.get("total_cost", 0),
        "urgent_items": reorder_data.get("urgent_items", 0),
        "critical_items": reorder_data.get("critical_items", 0),
        "report_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    # Priority based on urgent items
    urgent_count = reorder_data.get("urgent_items", 0)
    if urgent_count > 0:
        priority = "urgent"
    elif reorder_data.get("critical_items", 0) > 0:
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