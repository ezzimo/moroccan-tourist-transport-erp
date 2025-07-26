"""
 Utility functions and dependencies for inventory service
 """
from .auth import *
from .notifications import *
from .validation import *


__all__ = [
    "get_current_user", "require_permission", "CurrentUser",
    "NotificationService", "send_low_stock_alert", 
    "send_purchase_order_notification", "validate_item_data",
    "validate_stock_movement", "validate_supplier_data",
    "validate_purchase_order", "validate_movement_data",
    "validate_analytics_query",
]