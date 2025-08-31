"""
Booking management routes
"""

from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from database import get_session, get_redis
from services.booking_service import BookingService
from schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    BookingSummary,
    BookingConfirm,
    BookingCancel,
    BookingSearch,
)
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from utils.pdf_generator import generate_booking_voucher
from models.enums import BookingStatus, ServiceType, PaymentStatus
from typing import List, Optional
import redis
import uuid


router = APIRouter(prefix="/bookings", tags=["Booking Management"])


@router.post("/", response_model=BookingResponse)
async def create_booking(
    booking_data: BookingCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("booking", "create", "bookings")
    ),
):
    """Create a new booking"""
    booking_service = BookingService(session, redis_client)
    return await booking_service.create_booking(booking_data, current_user.user_id)


@router.get("/", response_model=PaginatedResponse[BookingResponse])
async def get_bookings(
    pagination: PaginationParams = Depends(),
    customer_id: Optional[uuid.UUID] = Query(None, description="Filter by customer ID"),
    status: Optional[BookingStatus] = Query(
        None, description="Filter by booking status"
    ),
    service_type: Optional[ServiceType] = Query(
        None, description="Filter by service type"
    ),
    payment_status: Optional[PaymentStatus] = Query(
        None, description="Filter by payment status"
    ),
    start_date_from: Optional[str] = Query(
        None, description="Filter by start date from (YYYY-MM-DD)"
    ),
    start_date_to: Optional[str] = Query(
        None, description="Filter by start date to (YYYY-MM-DD)"
    ),
    lead_passenger_name: Optional[str] = Query(
        None, description="Filter by passenger name"
    ),
    lead_passenger_email: Optional[str] = Query(
        None, description="Filter by passenger email"
    ),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("booking", "read", "bookings")
    ),
):
    """Get list of bookings with optional search and filters"""
    booking_service = BookingService(session, redis_client)

    # Build search criteria
    search = None
    if any(
        [
            customer_id,
            status,
            service_type,
            payment_status,
            start_date_from,
            start_date_to,
            lead_passenger_name,
            lead_passenger_email,
        ]
    ):
        from datetime import datetime

        start_date_from_parsed = None
        start_date_to_parsed = None

        if start_date_from:
            start_date_from_parsed = datetime.strptime(
                start_date_from, "%Y-%m-%d"
            ).date()
        if start_date_to:
            start_date_to_parsed = datetime.strptime(start_date_to, "%Y-%m-%d").date()

        search = BookingSearch(
            customer_id=customer_id,
            status=status,
            service_type=service_type,
            payment_status=payment_status,
            start_date_from=start_date_from_parsed,
            start_date_to=start_date_to_parsed,
            lead_passenger_name=lead_passenger_name,
            lead_passenger_email=lead_passenger_email,
        )

    bookings, total = await booking_service.get_bookings(pagination, search)

    return PaginatedResponse.create(
        items=bookings, total=total, page=pagination.page, size=pagination.size
    )


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("booking", "read", "bookings")
    ),
):
    """Get booking by ID"""
    booking_service = BookingService(session, redis_client)
    return await booking_service.get_booking(booking_id)


@router.get("/{booking_id}/summary", response_model=BookingSummary)
async def get_booking_summary(
    booking_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("booking", "read", "bookings")
    ),
):
    """Get comprehensive booking summary"""
    booking_service = BookingService(session, redis_client)
    return await booking_service.get_booking_summary(booking_id)


@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: uuid.UUID,
    booking_data: BookingUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("booking", "update", "bookings")
    ),
):
    """Update booking information"""
    booking_service = BookingService(session, redis_client)
    return await booking_service.update_booking(booking_id, booking_data)


@router.post("/{booking_id}/confirm", response_model=BookingResponse)
async def confirm_booking(
    booking_id: uuid.UUID,
    confirm_data: BookingConfirm,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("booking", "update", "bookings")
    ),
):
    """Confirm a pending booking"""
    booking_service = BookingService(session, redis_client)
    return await booking_service.confirm_booking(booking_id, confirm_data)


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: uuid.UUID,
    cancel_data: BookingCancel,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("booking", "update", "bookings")
    ),
):
    """Cancel a booking"""
    booking_service = BookingService(session, redis_client)
    return await booking_service.cancel_booking(
        booking_id, cancel_data, current_user.user_id
    )


@router.get("/{booking_id}/voucher")
async def get_booking_voucher(
    booking_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("booking", "read", "bookings")
    ),
):
    """Generate and download booking voucher PDF"""
    booking_service = BookingService(session, redis_client)

    # Get booking details
    booking_response = await booking_service.get_booking(booking_id)

    # Get booking model for PDF generation
    from sqlmodel import select
    from models import Booking, ReservationItem

    statement = select(Booking).where(Booking.id == booking_id)
    booking = session.exec(statement).first()

    # Get reservation items
    items_statement = select(ReservationItem).where(
        ReservationItem.booking_id == booking_id
    )
    reservation_items = session.exec(items_statement).all()

    # Generate PDF
    pdf_buffer = generate_booking_voucher(booking, reservation_items)

    # Return PDF as streaming response
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=booking_voucher_{booking_id}.pdf"
        },
    )


@router.post("/{booking_id}/expire")
async def expire_booking(
    booking_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("booking", "update", "bookings")
    ),
):
    """Manually expire a booking (admin only)"""
    booking_service = BookingService(session, redis_client)
    success = await booking_service.expire_booking(booking_id)

    if success:
        return {"message": "Booking expired successfully"}
    else:
        return {"message": "Booking could not be expired"}
