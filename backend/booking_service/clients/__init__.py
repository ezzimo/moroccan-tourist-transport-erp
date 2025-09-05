"""
Clients for interacting with external services.
"""
from .base import (
    ServiceClientBase,
    ExternalServiceError,
    IntegrationAuthError,
    IntegrationBadRequest,
    IntegrationNotFound,
    IntegrationTimeoutError,
)
from .customer_client import get_customer_by_id, verify_customer_exists, CustomerVerificationError
from .fleet_client import FleetServiceClient
from .payment_client import PaymentServiceClient
from .notification_client import NotificationServiceClient

__all__ = [
    "ServiceClientBase",
    "ExternalServiceError",
    "IntegrationAuthError",
    "IntegrationBadRequest",
    "IntegrationNotFound",
    "IntegrationTimeoutError",
    "get_customer_by_id",
    "verify_customer_exists",
    "CustomerVerificationError",
    "FleetServiceClient",
    "PaymentServiceClient",
    "NotificationServiceClient",
]