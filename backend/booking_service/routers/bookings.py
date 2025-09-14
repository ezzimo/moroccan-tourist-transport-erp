"""
Booking management routes
"""
import io
import os
import uuid
import logging
from typing import Optional
import redis.asyncio as redis

from fastapi import APIRouter, Depends, Body, Query, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from database import get_session, get_redis
from services.booking_service import BookingService
from clients.customer_client import get_customer_by_id, CustomerVerificationError

from schemas.booking_filters import BookingFilters
from schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from utils.auth import get_current_user, require_permission, CurrentUser
from utils.pagination import PaginatedResponse
from config import settings
from utils import pdf_generator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bookings", tags=["Booking Management"])


@router.post("/", response_model=BookingResponse)
async def create_booking(
    booking_data: BookingCreate,
    request: Request,
    db: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "create", "bookings")),
):
    """
    Create a new booking.

    Notes:
    - Do NOT gate booking creation on PDF/reportlab.
    - Optional: attempt customer verification; map known failures to typed errors.
    """
    logger.info("Creating booking for customer %s", booking_data.customer_id)

    # Optional: resilient customer verification (non-strict by default)
    auth_header = request.headers.get("Authorization")
    try:
        customer_data = await get_customer_by_id(booking_data.customer_id, auth_header=auth_header)
        customer_verified = customer_data is not None
        logger.debug("Customer verification result for %s: %s", booking_data.customer_id, customer_verified)
        # We do not hard-fail if None; the service layer can decide how to tag unverified customers.
    except CustomerVerificationError as e:
        logger.warning("Customer verification failure: %s (%s)", e, e.type)
        raise HTTPException(status_code=e.status, detail={"type": e.type, "detail": str(e)})

    service = BookingService(db, redis_client)
    return await service.create_booking(
        booking_data, 
        current_user.user_id,
        customer_verified=customer_verified,
        customer_snapshot=customer_data
    )


@router.get("/", response_model=PaginatedResponse[BookingResponse])
async def get_bookings(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    sort_by: Optional[str] = Query(None),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    customer_id: Optional[uuid.UUID] = Query(None),
    service_type: Optional[str] = Query(None),
    status_: Optional[str] = Query(None, alias="status"),
    payment_status: Optional[str] = Query(None),
    start_date_from: Optional[str] = Query(None, description="YYYY-MM-DD"),
    start_date_to: Optional[str] = Query(None, description="YYYY-MM-DD"),
    created_from: Optional[str] = Query(None),
    created_to: Optional[str] = Query(None),
    pax_count_min: Optional[int] = Query(None, ge=0),
    pax_count_max: Optional[int] = Query(None, ge=0),
    currency: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "read", "bookings")),
):
    """
    List bookings with pagination and filters.
    """
    filters = BookingFilters(
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order,
        customer_id=customer_id,
        service_type=service_type,
        status=status_,
        payment_status=payment_status,
        start_date_from=start_date_from,
        start_date_to=start_date_to,
        created_from=created_from,
        created_to=created_to,
        pax_count_min=pax_count_min,
        pax_count_max=pax_count_max,
        currency=currency,
        search=search,
    )

    service = BookingService(db, redis_client)
    return await service.get_bookings(filters)


@router.get("/{booking_id}/voucher")
async def download_booking_voucher(
    booking_id: uuid.UUID,
    db: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    _: None = Depends(require_permission("booking", "read", "bookings")),
):
    """
    Download a booking voucher as PDF.

    - Guarded by settings.pdf_enabled and lazy reportlab import.
    - Returns 404 if booking not found.
    - Returns 501 when PDF feature disabled or reportlab not installed.
    """
    if not settings.pdf_enabled or not pdf_generator.have_reportlab():
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={"type": "pdf_not_enabled", "detail": "PDF generation is disabled or reportlab is not installed."},
        )

    service = BookingService(db, redis_client)
    booking = await service.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    booking_dict = booking.model_dump() if hasattr(booking, "model_dump") else booking.__dict__

    buf = io.BytesIO()
    pdf_generator.generate_booking_voucher(booking_dict, buf)
    buf.seek(0)

    return StreamingResponse(
        io.BytesIO(buf.getvalue()),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=booking_voucher_{booking_id}.pdf"},
    )


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: uuid.UUID,
    db: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "read", "bookings")),
):
    service = BookingService(db, redis_client)
    return await service.get_booking(booking_id)


@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: uuid.UUID,
    booking_data: BookingUpdate,
    db: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "update", "bookings")),
):
    service = BookingService(db, redis_client)
    return await service.update_booking(booking_id, booking_data, current_user.user_id)


@router.post("/{booking_id}/confirm")
async def confirm_booking(
    booking_id: uuid.UUID,
    db: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "update", "bookings")),
):
    service = BookingService(db, redis_client)
    return await service.confirm_booking(booking_id, current_user.user_id)


@router.post("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: uuid.UUID,
    reason: str = Body(..., embed=True),
    db: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "update", "bookings")),
):
    service = BookingService(db, redis_client)
    return await service.cancel_booking(booking_id, reason, current_user.user_id)


@router.delete("/{booking_id}")
async def delete_booking(
    booking_id: uuid.UUID,
    db: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "delete", "bookings")),
):
    service = BookingService(db, redis_client)
    return await service.delete_booking(booking_id)