"""
Reservation service for managing booking items and components
"""

from sqlmodel import Session, select
from fastapi import HTTPException, status
from models import Booking, BookingStatus, ReservationItem
from schemas.booking import (
    ReservationItemCreate,
    ReservationItemUpdate,
    ReservationItemResponse,
)
from typing import List
from datetime import datetime
from decimal import Decimal
import uuid


class ReservationService:
    """Service for handling reservation items and booking components"""

    def __init__(self, session: Session):
        self.session = session

    async def add_reservation_item(
        self, item_data: ReservationItemCreate
    ) -> ReservationItemResponse:
        """Add a reservation item to a booking"""
        # Verify booking exists and can be modified
        booking = await self._get_modifiable_booking(item_data.booking_id)

        # Calculate total price
        total_price = item_data.unit_price * item_data.quantity

        # Create reservation item
        item = ReservationItem(
            booking_id=item_data.booking_id,
            type=item_data.type,
            reference_id=item_data.reference_id,
            name=item_data.name,
            description=item_data.description,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            total_price=total_price,
            notes=item_data.notes,
        )

        # Set specifications if provided
        if item_data.specifications:
            item.set_specifications_dict(item_data.specifications)

        self.session.add(item)

        # Update booking total price
        booking.total_price += total_price
        booking.updated_at = datetime.utcnow()
        self.session.add(booking)

        self.session.commit()
        self.session.refresh(item)

        return ReservationItemResponse.from_model(item)

    async def get_reservation_item(self, item_id: uuid.UUID) -> ReservationItemResponse:
        """Get reservation item by ID"""
        statement = select(ReservationItem).where(ReservationItem.id == item_id)
        item = self.session.exec(statement).first()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation item not found",
            )

        return ReservationItemResponse.from_model(item)

    async def get_booking_items(
        self, booking_id: uuid.UUID
    ) -> List[ReservationItemResponse]:
        """Get all reservation items for a booking"""
        # Verify booking exists
        await self._verify_booking_exists(booking_id)

        statement = (
            select(ReservationItem)
            .where(ReservationItem.booking_id == booking_id)
            .order_by(ReservationItem.created_at)
        )

        items = self.session.exec(statement).all()

        return [ReservationItemResponse.from_model(item) for item in items]

    async def update_reservation_item(
        self, item_id: uuid.UUID, item_data: ReservationItemUpdate
    ) -> ReservationItemResponse:
        """Update a reservation item"""
        statement = select(ReservationItem).where(ReservationItem.id == item_id)
        item = self.session.exec(statement).first()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation item not found",
            )

        # Verify booking can be modified
        booking = await self._get_modifiable_booking(item.booking_id)

        # Store old total price for booking update
        old_total_price = item.total_price

        # Update fields
        update_data = item_data.model_dump(
            exclude_unset=True, exclude={"specifications"}
        )

        for field, value in update_data.items():
            setattr(item, field, value)

        # Handle specifications separately
        if item_data.specifications is not None:
            item.set_specifications_dict(item_data.specifications)

        # Recalculate total price if quantity or unit price changed
        if item_data.quantity is not None or item_data.unit_price is not None:
            item.total_price = item.unit_price * item.quantity

        item.updated_at = datetime.utcnow()

        # Update booking total price
        price_difference = item.total_price - old_total_price
        booking.total_price += price_difference
        booking.updated_at = datetime.utcnow()

        self.session.add(item)
        self.session.add(booking)
        self.session.commit()
        self.session.refresh(item)

        return ReservationItemResponse.from_model(item)

    async def remove_reservation_item(self, item_id: uuid.UUID) -> dict:
        """Remove a reservation item from a booking"""
        statement = select(ReservationItem).where(ReservationItem.id == item_id)
        item = self.session.exec(statement).first()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation item not found",
            )

        # Verify booking can be modified
        booking = await self._get_modifiable_booking(item.booking_id)

        # Update booking total price
        booking.total_price -= item.total_price
        booking.updated_at = datetime.utcnow()

        self.session.add(booking)
        self.session.delete(item)
        self.session.commit()

        return {"message": "Reservation item removed successfully"}

    async def confirm_reservation_item(
        self, item_id: uuid.UUID
    ) -> ReservationItemResponse:
        """Confirm a reservation item"""
        statement = select(ReservationItem).where(ReservationItem.id == item_id)
        item = self.session.exec(statement).first()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation item not found",
            )

        item.is_confirmed = True
        item.updated_at = datetime.utcnow()

        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)

        return ReservationItemResponse.from_model(item)

    async def cancel_reservation_item(
        self, item_id: uuid.UUID
    ) -> ReservationItemResponse:
        """Cancel a reservation item"""
        statement = select(ReservationItem).where(ReservationItem.id == item_id)
        item = self.session.exec(statement).first()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation item not found",
            )

        # Verify booking can be modified
        booking = await self._get_modifiable_booking(item.booking_id)

        item.is_cancelled = True
        item.updated_at = datetime.utcnow()

        # Update booking total price (subtract cancelled item)
        booking.total_price -= item.total_price
        booking.updated_at = datetime.utcnow()

        self.session.add(item)
        self.session.add(booking)
        self.session.commit()
        self.session.refresh(item)

        return ReservationItemResponse.from_model(item)

    async def get_booking_summary(self, booking_id: uuid.UUID) -> dict:
        """Get summary of all reservation items for a booking"""
        # Verify booking exists
        await self._verify_booking_exists(booking_id)

        statement = select(ReservationItem).where(
            ReservationItem.booking_id == booking_id
        )

        items = self.session.exec(statement).all()

        summary = {
            "total_items": len(items),
            "confirmed_items": len([item for item in items if item.is_confirmed]),
            "cancelled_items": len([item for item in items if item.is_cancelled]),
            "pending_items": len(
                [
                    item
                    for item in items
                    if not item.is_confirmed and not item.is_cancelled
                ]
            ),
            "total_value": sum(
                item.total_price for item in items if not item.is_cancelled
            ),
            "by_type": {},
        }

        # Group by item type
        for item in items:
            item_type = item.type.value
            if item_type not in summary["by_type"]:
                summary["by_type"][item_type] = {
                    "count": 0,
                    "total_value": Decimal(0),
                    "confirmed": 0,
                    "cancelled": 0,
                }

            summary["by_type"][item_type]["count"] += 1
            if not item.is_cancelled:
                summary["by_type"][item_type]["total_value"] += item.total_price

            if item.is_confirmed:
                summary["by_type"][item_type]["confirmed"] += 1
            elif item.is_cancelled:
                summary["by_type"][item_type]["cancelled"] += 1

        # Convert Decimal to float for JSON serialization
        summary["total_value"] = float(summary["total_value"])
        for item_type in summary["by_type"]:
            summary["by_type"][item_type]["total_value"] = float(
                summary["by_type"][item_type]["total_value"]
            )

        return summary

    async def _verify_booking_exists(self, booking_id: uuid.UUID) -> Booking:
        """Verify that a booking exists"""
        statement = select(Booking).where(Booking.id == booking_id)
        booking = self.session.exec(statement).first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        return booking

    async def _get_modifiable_booking(self, booking_id: uuid.UUID) -> Booking:
        """Get a booking that can be modified"""
        booking = await self._verify_booking_exists(booking_id)

        if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify cancelled or refunded booking",
            )

        return booking
