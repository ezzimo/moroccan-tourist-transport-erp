"""
Client for interacting with the Payment Service.
"""
from decimal import Decimal
from typing import Dict, Any, Optional

from .base import ServiceClientBase, ExternalServiceError


class PaymentServiceClient(ServiceClientBase):
    """
    Provides methods for interacting with the Payment Service API.
    """
    def __init__(self, *, base_url: str, api_key: Optional[str] = None):
        super().__init__(base_url)
        self._api_key = api_key

    async def confirm_payment(
        self,
        *,
        reference: str,
        expected_amount: Decimal,
        currency: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Confirms a payment with the Payment Service.

        Args:
            reference: The payment reference from the provider.
            expected_amount: The amount that is expected to have been paid.
            currency: The currency of the payment.
            idempotency_key: An optional key to ensure the request is processed only once.

        Returns:
            A dictionary containing the confirmation details from the payment service.

        Raises:
            ExternalServiceError: If the payment confirmation fails or the status
                                  in the response is not a success status.
        """
        if not self._api_key:
            raise ExternalServiceError("Payment API key is not configured.", 500)

        headers = {"Authorization": f"Bearer {self._api_key}"}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        payload = {
            "reference": reference,
            "expected_amount": str(expected_amount),
            "currency": currency,
        }

        response_data = await self.request_json(
            "POST",
            "/payments/confirm",
            json=payload,
            headers=headers,
        )

        status = response_data.get("status", "").lower()
        if status not in {"captured", "succeeded"}:
            raise ExternalServiceError(
                f"Payment confirmation failed with status: '{status}'.",
                status_code=400
            )

        return response_data
