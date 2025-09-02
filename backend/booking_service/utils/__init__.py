"""
Utility functions and dependencies
"""
from .auth import *
# Do not import pdf_generator here; it depends on an optional lib (reportlab).
# Eager import would crash the app during startup if the lib is missing.
from .auth import *
from .pagination import *

__all__ = [
__all__ = [
    "get_current_user", "require_permission", "verify_auth_token",
    "PaginationParams", "paginate_query"
]