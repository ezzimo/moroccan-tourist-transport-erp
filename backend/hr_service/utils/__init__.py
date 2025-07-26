"""
Utility functions and dependencies
"""

from .auth import *
from .pagination import *
from .upload import *
from .validation import *
from .notifications import *

__all__ = [
    "get_current_user",
    "require_permission",
    "CurrentUser",
    "paginate_query",
    "PaginationParams",
    "FileUploadHandler",
    "validate_document",
    "process_upload",
    "validate_employee_data",
    "validate_job_application_data",
    "validate_training_data",
    "NotificationService",
    "send_recruitment_notification",
    "send_training_notification",
]
