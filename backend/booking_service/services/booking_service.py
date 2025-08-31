"""
Booking service for booking management operations
"""

from sqlmodel import Session, select, and_, or_
from fastapi import HTTPException, status
from models import (
    Booking,
    BookingStatus,
    PaymentStatus,
    ReservationItem,
)
from schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    BookingSummary,
    BookingConfirm,
    BookingCancel,
    BookingSearch,
)
from utils.pagination import PaginationParams, paginate_query
from utils.locking import acquire_booking_lock, release_booking_lock
from services.pricing_service import PricingService
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import redis
import uuid
import httpx


class BookingService:
    """Service for handling booking operations"""

    def __init__(self, session: Session, redis_client: redis.Redis):
        self.session = session
        self.redis = redis_client
        self.pricing_service = PricingService(session)

    async def create_booking(
        self, booking_data: BookingCreate, current_user_id: uuid.UUID
    ) -> BookingResponse:
        """Create a new booking with locking mechanism"""
        # Acquire lock for booking creation
        lock_key = (
            f"booking_create:{booking_data.customer_id}:{booking_data.start_date}"
        )
        lock_id = acquire_booking_lock(
            self.redis,
            "booking",
            str(booking_data.customer_id),
            str(booking_data.start_date),
        )

        if not lock_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Another booking is being processed. Please try again.",
            )

        try:
            # Verify customer exists (call CRM service)
            await self._verify_customer_exists(booking_data.customer_id)

            # Calculate pricing
            pricing_request = {
                "service_type": booking_data.service_type.value,
                "base_price": booking_data.base_price,
                "pax_count": booking_data.pax_count,
                "start_date": booking_data.start_date,
                "end_date": booking_data.end_date,
                "customer_id": booking_data.customer_id,
                "promo_code": booking_data.promo_code,
            }

            pricing_result = await self.pricing_service.calculate_pricing(
                pricing_request
            )

            # Create booking
            booking = Booking(
                customer_id=booking_data.customer_id,
                service_type=booking_data.service_type,
                pax_count=booking_data.pax_count,
                lead_passenger_name=booking_data.lead_passenger_name,
                lead_passenger_email=booking_data.lead_passenger_email,
                lead_passenger_phone=booking_data.lead_passenger_phone,
                start_date=booking_data.start_date,
                end_date=booking_data.end_date,
                base_price=pricing_result["base_price"],
                discount_amount=pricing_result["discount_amount"],
                total_price=pricing_result["total_price"],
                payment_method=booking_data.payment_method,
                special_requests=booking_data.special_requests,
                expires_at=datetime.utcnow() + timedelta(minutes=30),  # 30 min expiry
            )

            self.session.add(booking)
            self.session.commit()
            self.session.refresh(booking)

            # Schedule expiry check
            await self._schedule_booking_expiry(booking.id)

            return BookingResponse(**booking.model_dump())

        finally:
            # Always release the lock
            release_booking_lock(
                self.redis,
                "booking",
                str(booking_data.customer_id),
                str(booking_data.start_date),
                lock_id,
            )

    async def get_booking(self, booking_id: uuid.UUID) -> BookingResponse:
        """Get booking by ID"""
        statement = select(Booking).where(Booking.id == booking_id)
        booking = self.session.exec(statement).first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        return BookingResponse(**booking.model_dump())

    async def get_bookings(
        self, pagination: PaginationParams, search: Optional[BookingSearch] = None
    ) -> Tuple[List[BookingResponse], int]:
        """Get list of bookings with optional search"""
        query = select(Booking)

        # Apply search filters
        if search:
            conditions = []

            if search.customer_id:
                conditions.append(Booking.customer_id == search.customer_id)

            if search.status:
                conditions.append(Booking.status == search.status)

            if search.service_type:
                conditions.append(Booking.service_type == search.service_type)

            if search.payment_status:
                conditions.append(Booking.payment_status == search.payment_status)

            if search.start_date_from:
                conditions.append(Booking.start_date >= search.start_date_from)

            if search.start_date_to:
                conditions.append(Booking.start_date <= search.start_date_to)

            if search.lead_passenger_name:
                conditions.append(
                    Booking.lead_passenger_name.ilike(f"%{search.lead_passenger_name}%")
                )

            if search.lead_passenger_email:
                conditions.append(
                    Booking.lead_passenger_email.ilike(
                        f"%{search.lead_passenger_email}%"
                    )
                )

            if conditions:
                query = query.where(and_(*conditions))

        # Order by creation date (newest first)
        query = query.order_by(Booking.created_at.desc())

        bookings, total = paginate_query(self.session, query, pagination)

        return [BookingResponse(**booking.model_dump()) for booking in bookings], total

    async def update_booking(
        self, booking_id: uuid.UUID, booking_data: BookingUpdate
    ) -> BookingResponse:
        """Update booking information"""
        statement = select(Booking).where(Booking.id == booking_id)
        booking = self.session.exec(statement).first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update cancelled or refunded booking",
            )

        # Update fields
        update_data = booking_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(booking, field, value)

        booking.updated_at = datetime.utcnow()

        self.session.add(booking)
        self.session.commit()
        self.session.refresh(booking)

        return BookingResponse(**booking.model_dump())

    async def confirm_booking(
        self, booking_id: uuid.UUID, confirm_data: BookingConfirm
    ) -> BookingResponse:
        """Confirm a pending booking"""
        statement = select(Booking).where(Booking.id == booking_id)
        booking = self.session.exec(statement).first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        if booking.status != BookingStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending bookings can be confirmed",
            )

        if booking.is_expired():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Booking has expired"
            )

        # Update booking status
        booking.status = BookingStatus.CONFIRMED
        booking.confirmed_at = datetime.utcnow()
        booking.updated_at = datetime.utcnow()
        booking.expires_at = None  # Remove expiry

        if confirm_data.payment_reference:
            booking.payment_reference = confirm_data.payment_reference
            booking.payment_status = PaymentStatus.PAID

        if confirm_data.internal_notes:
            booking.internal_notes = confirm_data.internal_notes

        self.session.add(booking)
        self.session.commit()
        self.session.refresh(booking)

        return BookingResponse(**booking.model_dump())

    async def cancel_booking(
        self, booking_id: uuid.UUID, cancel_data: BookingCancel, cancelled_by: uuid.UUID
    ) -> BookingResponse:
        """Cancel a booking"""
        statement = select(Booking).where(Booking.id == booking_id)
        booking = self.session.exec(statement).first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        if not booking.can_be_cancelled():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking cannot be cancelled",
            )

        # Update booking status
        booking.status = BookingStatus.CANCELLED
        booking.cancellation_reason = cancel_data.reason
        booking.cancelled_by = cancelled_by
        booking.cancelled_at = datetime.utcnow()
        booking.updated_at = datetime.utcnow()

        if cancel_data.internal_notes:
            booking.internal_notes = cancel_data.internal_notes

        # Handle refund if specified
        if cancel_data.refund_amount:
            booking.payment_status = PaymentStatus.REFUNDED

        self.session.add(booking)
        self.session.commit()
        self.session.refresh(booking)

        return BookingResponse(**booking.model_dump())

    async def get_booking_summary(self, booking_id: uuid.UUID) -> BookingSummary:
        """Get comprehensive booking summary"""
        statement = select(Booking).where(Booking.id == booking_id)
        booking = self.session.exec(statement).first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        # Get reservation items count
        items_count_stmt = select(ReservationItem).where(
            ReservationItem.booking_id == booking_id
        )
        reservation_items = self.session.exec(items_count_stmt).all()

        # Get customer information from CRM service
        customer_info = await self._get_customer_info(booking.customer_id)

        # Create summary response
        base_response = BookingResponse(**booking.model_dump())

        return BookingSummary(
            **base_response.model_dump(),
            reservation_items_count=len(reservation_items),
            duration_days=booking.get_duration_days(),
            is_expired=booking.is_expired(),
            can_be_cancelled=booking.can_be_cancelled(),
            customer_name=customer_info.get("full_name") if customer_info else None,
            customer_email=customer_info.get("email") if customer_info else None,
        )

    async def expire_booking(self, booking_id: uuid.UUID) -> bool:
        """Expire a booking that hasn't been confirmed"""
        statement = select(Booking).where(Booking.id == booking_id)
        booking = self.session.exec(statement).first()

        if not booking:
            return False

        if booking.status == BookingStatus.PENDING and booking.is_expired():
            booking.status = BookingStatus.EXPIRED
            booking.updated_at = datetime.utcnow()

            self.session.add(booking)
            self.session.commit()

            return True

        return False

    async def _verify_customer_exists(self, customer_id: uuid.UUID) -> bool:
        """Verify customer exists in CRM service"""
        try:
            from config import settings

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.crm_service_url}/api/v1/customers/{customer_id}"
                )
                return response.status_code == 200
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to verify customer information",
            )

    async def _get_customer_info(self, customer_id: uuid.UUID) -> Optional[dict]:
        """Get customer information from CRM service"""
        try:
            from config import settings

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.crm_service_url}/api/v1/customers/{customer_id}"
                )
                if response.status_code == 200:
                    return response.json()
        except:
            pass
        return None

    async def _schedule_booking_expiry(self, booking_id: uuid.UUID):
        """Schedule booking expiry check"""
        # In a production environment, you would use Celery or similar
        # For now, we'll store the expiry in Redis
        expiry_key = f"booking_expiry:{booking_id}"
        self.redis.setex(expiry_key, 1800, str(booking_id))  # 30 minutes
