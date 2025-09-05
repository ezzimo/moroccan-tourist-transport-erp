"""
Base classes and exceptions for external service clients.
"""
import asyncio
import logging
import random
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# --- Custom Exceptions ---

class ExternalServiceError(Exception):
    """Base exception for all external service integration errors."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code

class IntegrationTimeoutError(ExternalServiceError):
    """Raised when a request to an external service times out."""
    def __init__(self, message: str = "Request timed out"):
        super().__init__(message, status_code=504)

class IntegrationAuthError(ExternalServiceError):
    """Raised for 401/403 authentication or authorization errors."""
    def __init__(self, message: str = "Authentication or authorization failed"):
        super().__init__(message, status_code=403)

class IntegrationNotFound(ExternalServiceError):
    """Raised for 404 Not Found errors."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)

class IntegrationBadRequest(ExternalServiceError):
    """Raised for 4xx client errors (e.g., 400, 422)."""
    def __init__(self, message: str = "Bad request or invalid data"):
        super().__init__(message, status_code=400)


# --- Base Service Client ---

class ServiceClientBase:
    """
    Base class for asynchronous service clients with built-in retry logic.
    """
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def build_headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Constructs request headers, merging defaults with provided extras.
        """
        # In a real application, correlation IDs would be sourced from a
        # request context (e.g., using contextvars).
        default_headers = {
            "Accept": "application/json",
            "User-Agent": "BookingService/1.0",
            # "X-Request-Id": get_request_id(),
            # "X-Correlation-Id": get_correlation_id(),
        }
        if extra:
            default_headers.update(extra)
        return default_headers

    async def request_json(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 5.0,
        retries: int = 2,
    ) -> Any:
        """
        Makes an async JSON request with retries and standardized error handling.
        """
        import httpx

        url = f"{self.base_url}{path}"
        request_headers = self.build_headers(headers)

        last_exception = None

        for attempt in range(retries + 1):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.request(
                        method, url, params=params, json=json, headers=request_headers, timeout=timeout
                    )

                if response.status_code in {502, 503, 504} and attempt < retries:
                    last_exception = ExternalServiceError(
                        f"External service returned a retryable server error: {response.status_code}",
                        status_code=response.status_code
                    )
                    logger.warning(
                        "Attempt %d/%d failed with retryable status %d for %s %s",
                        attempt + 1, retries + 1, response.status_code, method, url
                    )
                    # Go to the backoff sleep
                    raise httpx.RequestError("Retryable server error")

                response.raise_for_status()
                return response.json()

            except httpx.TimeoutException as e:
                last_exception = IntegrationTimeoutError(f"Request to {url} timed out.")
                logger.warning("Timeout on attempt %d/%d for %s %s", attempt + 1, retries + 1, method, url)

            except httpx.RequestError as e:
                if "Retryable server error" not in str(e):
                    last_exception = ExternalServiceError(f"Network error requesting {url}: {e}")
                    logger.warning("Network error on attempt %d/%d for %s %s: %s", attempt + 1, retries + 1, method, url, e)

            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                if status in {401, 403}:
                    raise IntegrationAuthError from e
                if status == 404:
                    raise IntegrationNotFound from e
                if 400 <= status < 500:
                    raise IntegrationBadRequest(f"Bad request: {e.response.text}") from e

                # For non-retryable 5xx errors
                raise ExternalServiceError(f"HTTP error: {status} {e.response.text}", status_code=status) from e

            if attempt < retries:
                backoff_time = 0.2 * (2 ** attempt) + random.uniform(0.0, 0.1)
                await asyncio.sleep(backoff_time)

        if last_exception:
            raise last_exception

        raise ExternalServiceError("Request failed after all retries.")
