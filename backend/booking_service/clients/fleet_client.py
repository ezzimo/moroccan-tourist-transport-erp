"""
Client for interacting with the Fleet Service.
"""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from uuid import UUID

from .base import ServiceClientBase


class FleetServiceClient(ServiceClientBase):
    """
    Provides methods for interacting with the Fleet Service API.
    """

    async def get_available(
        self,
        *,
        start_time: datetime,
        end_time: datetime,
        capacity: Optional[int] = None,
        vehicle_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetches available vehicles from the Fleet Service.

        Args:
            start_time: The start of the time window.
            end_time: The end of the time window.
            capacity: The minimum required passenger capacity.
            vehicle_type: The specific type of vehicle requested.

        Returns:
            A list of dictionaries, where each dictionary represents an available vehicle.
        """
        params = {
            "start_time": start_time.astimezone(timezone.utc).isoformat(),
            "end_time": end_time.astimezone(timezone.utc).isoformat(),
        }
        if capacity is not None:
            params["capacity"] = capacity
        if vehicle_type is not None:
            params["type"] = vehicle_type

        return await self.request_json("GET", "/vehicles/available", params=params)

    async def reserve_vehicle(
        self,
        *,
        vehicle_id: UUID,
        booking_id: UUID,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Reserves a specific vehicle for a booking.

        Args:
            vehicle_id: The ID of the vehicle to reserve.
            booking_id: The ID of the booking this reservation is for.
            idempotency_key: An optional key to ensure the request is processed only once.

        Returns:
            A dictionary representing the successful reservation.
        """
        headers = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        payload = {"booking_id": str(booking_id)}

        return await self.request_json(
            "POST",
            f"/vehicles/{vehicle_id}/reserve",
            json=payload,
            headers=headers,
        )

    async def release_vehicle(
        self,
        *,
        vehicle_id: UUID,
        booking_id: UUID,
    ) -> bool:
        """
        Releases a previously reserved vehicle.

        Args:
            vehicle_id: The ID of the vehicle to release.
            booking_id: The ID of the booking that held the reservation.

        Returns:
            True if the vehicle was released successfully, False otherwise.
        """
        payload = {"booking_id": str(booking_id)}
        await self.request_json(
            "POST",
            f"/vehicles/{vehicle_id}/release",
            json=payload,
        )
        return True
