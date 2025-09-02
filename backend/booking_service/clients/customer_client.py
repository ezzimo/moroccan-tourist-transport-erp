"""
Resilient customer client for booking service
"""
from __future__ import annotations
from typing import Any, Optional
import os
import httpx
import logging
from uuid import UUID

logger = logging.getLogger(__name__)

CUSTOMER_SVC_BASE = os.getenv("CUSTOMER_SERVICE_BASE", "http://crm_service:8001/api/v1")
CUSTOMER_VERIFY_STRICT = os.getenv("CUSTOMER_VERIFY_STRICT", "false").lower() in {"1", "true", "yes"}
HTTP_TIMEOUT = float(os.getenv("CUSTOMER_HTTP_TIMEOUT", "2.0"))


class CustomerVerificationError(Exception):
    """Custom exception for customer verification failures"""
    def __init__(self, message: str, type_: str = "customer_verification_failed", status: int = 400):
        super().__init__(message)
        self.type = type_
        self.status = status


def extract_bearer_token(auth_header: Optional[str]) -> Optional[str]:
    """Extract bearer token from Authorization header"""
    if not auth_header:
        return None
    
    if auth_header.startswith("Bearer "):
        return auth_header[7:]  # Remove "Bearer " prefix
    
    return None


async def get_customer_by_id(customer_id: UUID, token: Optional[str] = None, auth_header: Optional[str] = None) -> Optional[dict[str, Any]]:
    """
    Try to fetch a single customer; return dict if found, None if 404.
    Raise CustomerVerificationError for auth problems if STRICT, else None.
    Network errors/timeouts are logged and return None when not STRICT.
    
    Args:
        customer_id: Customer UUID to lookup
        token: Bearer token (without "Bearer " prefix)
        auth_header: Full Authorization header value (e.g., "Bearer xyz123")
    """
    url = f"{CUSTOMER_SVC_BASE}/customers/{customer_id}"
    headers = {"Accept": "application/json"}
    
    # Use auth_header if provided, otherwise construct from token
    if auth_header:
        headers["Authorization"] = auth_header
    elif token:
        headers["Authorization"] = f"Bearer {token}"

    logger.info("Verifying customer %s at %s", customer_id, url)

    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            resp = await client.get(url, headers=headers)
    except Exception as e:
        logger.warning("Customer lookup network error: %s %s -> %s", "GET", url, e)
        if CUSTOMER_VERIFY_STRICT:
            raise CustomerVerificationError("Customer lookup failed", "customer_service_unreachable", 503)
        return None

    logger.info("Customer lookup response: %s", resp.status_code)

    if resp.status_code == 200:
        try:
            customer_data = resp.json()
            logger.info("Customer verified: %s (%s)", customer_data.get("email", "unknown"), customer_data.get("full_name", "unknown"))
            return customer_data
        except Exception:
            logger.warning("Customer lookup invalid JSON body: %s", resp.text[:512])
            if CUSTOMER_VERIFY_STRICT:
                raise CustomerVerificationError("Invalid customer response", "customer_service_invalid", 502)
            return None

    if resp.status_code == 404:
        logger.warning("Customer not found: %s", customer_id)
        if CUSTOMER_VERIFY_STRICT:
            raise CustomerVerificationError("Customer not found", "customer_not_found", 422)
        return None

    if resp.status_code in (401, 403):
        logger.warning("Customer lookup auth error (%s): %s", resp.status_code, resp.text[:512])
        if CUSTOMER_VERIFY_STRICT:
            raise CustomerVerificationError("Not authorized to verify customer", "customer_forbidden", 403)
        return None

    logger.warning("Customer lookup unexpected status %s: %s", resp.status_code, resp.text[:512])
    if CUSTOMER_VERIFY_STRICT:
        raise CustomerVerificationError("Customer service error", "customer_service_error", 502)
    return None


async def verify_customer_exists(customer_id: UUID, token: Optional[str] = None, auth_header: Optional[str] = None) -> bool:
    """
    Simple boolean check if customer exists.
    Returns True if customer found, False otherwise.
    Only raises in strict mode for auth/service errors.
    """
    try:
        customer = await get_customer_by_id(customer_id, token, auth_header)
        return customer is not None
    except CustomerVerificationError:
        # Re-raise in strict mode
        raise
    except Exception as e:
        logger.warning("Customer verification failed: %s", e)
        return not CUSTOMER_VERIFY_STRICT  # Fail open in non-strict mode