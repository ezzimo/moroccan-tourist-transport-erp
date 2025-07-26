"""
 Utility functions and dependencies for QA service
 """
from .auth import *
from .notifications import *
from .upload import *
from .validation import *

__all__ = [
    "get_current_user",
    "require_permission",
    "CurrentUser",
    "NotificationService",
    "send_audit_notification",
    "send_compliance_alert",
    "QAFileUploadHandler",
    "process_certificate_upload",
    "process_audit_document_upload",
    "validate_checklist",
    "validate_audit_data",
    "validate_compliance_data",
]