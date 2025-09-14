"""
Utility functions for booking service
"""

# Do not import pdf_generator here; it depends on an optional lib (reportlab).
# Eager import would crash the app during startup if the lib is missing.

__all__ = []