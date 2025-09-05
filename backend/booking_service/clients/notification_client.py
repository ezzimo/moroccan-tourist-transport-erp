"""
Client for interacting with the Notification Service.
"""
from typing import Dict, Any

from .base import ServiceClientBase


class NotificationServiceClient(ServiceClientBase):
    """
    Provides methods for sending notifications via the Notification Service.
    """

    async def send_booking_confirmation_email(
        self,
        *,
        recipient_email: str,
        booking_payload: Dict[str, Any],
    ) -> bool:
        """
        Sends a booking confirmation email.

        Args:
            recipient_email: The email address of the recipient.
            booking_payload: The booking data to be included in the email template.

        Returns:
            True if the email was sent successfully, False otherwise.
        """
        payload = {
            "recipient_email": recipient_email,
            "booking_payload": booking_payload,
        }
        await self.request_json(
            "POST",
            "/notifications/email/send",
            json=payload,
        )
        return True

    async def send_booking_confirmation_sms(
        self,
        *,
        phone_number: str,
        message: str,
    ) -> bool:
        """
        Sends a booking confirmation SMS.

        Args:
            phone_number: The phone number of the recipient.
            message: The text message to send.

        Returns:
            True if the SMS was sent successfully, False otherwise.
        """
        payload = {"phone_number": phone_number, "message": message}
        await self.request_json(
            "POST",
            "/notifications/sms/send",
            json=payload,
        )
        return True
