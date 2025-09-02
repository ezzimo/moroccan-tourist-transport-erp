"""
Booking management routes
"""
import uuid
import logging
import redis.asyncio as redis
import os

from fastapi import APIRouter, Depends, Body, Query
from sqlmodel import Session
from database import get_session, get_redis
from services.booking_service import BookingService
from clients.customer_client import get_customer_by_id, CustomerVerificationError
from uuid import UUID
import logging

logger = logging.getLogger(__name__)
from schemas.booking_filters import BookingFilters
from schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from utils.auth import get_current_user, require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from utils import pdf_generator
from typing import Optional

logger = logging.getLogger(__name__)
# PDF feature flag
PDF_ENABLED = os.getenv("BOOKING_PDF_ENABLED", "false").lower() in {"1", "true", "yes"}

router = APIRouter(prefix="/bookings", tags=["Booking Management"])


from typing import Optional

@router.post("/", response_model=BookingResponse)
async def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "create", "bookings"))
):
    if not PDF_ENABLED or not pdf_generator.have_reportlab():
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={
                "type": "pdf_not_enabled", 
                "detail": "PDF generation is disabled or reportlab is not installed."
            }
        )
    
    """Create a new booking"""
    logger.info(f"Creating booking for customer {booking_data.customer_id}")
    
    # Resilient customer verification
    try:
        token = request.headers.get("Authorization")
        result = await booking_service.create_booking(
            payload,
            customer_verified=customer is not None,
            customer_snapshot=customer
        )
        logger.info("Booking created successfully: %s", result.id)
    except CustomerVerificationError as e:
        logger.warning("Customer verification strict failure: %s (%s)", e, e.type)
        logger.warning("Booking validation error: %s", e)
        raise HTTPException(
            status_code=e.status, 
            detail={"type": "validation_error", "detail": str(e)}
        )
    except Exception as e:
        logger.error("Unexpected customer verification error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"type": "booking_create_failed", "detail": "Unexpected error during booking creation"}
        )

    if customer is None:
        # Customer not found or verification skipped due to non-strict mode
        logger.warning("Customer %s not found or unverifiable", payload.customer_id)
        # In non-strict mode, we proceed but tag the booking
        pass

    booking_service = BookingService(db, redis_client)
    return await booking_service.create_booking(booking_data, current_user.user_id)


@router.get("/", response_model=PaginatedResponse[BookingResponse])
async def get_bookings(
    # pagination
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    sort_by: Optional[str] = Query(None),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    # common filters (align with BookingFilters / service code)
    customer_id: Optional[uuid.UUID] = Query(None),
    service_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    payment_status: Optional[str] = Query(None),
    start_date_from: Optional[str] = Query(None, description="YYYY-MM-DD"),
    start_date_to: Optional[str] = Query(None, description="YYYY-MM-DD"),
    created_from: Optional[str] = Query(None),
    created_to: Optional[str] = Query(None),
    pax_count_min: Optional[int] = Query(None, ge=0),
    pax_count_max: Optional[int] = Query(None, ge=0),
    currency: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    # DI
    db: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "read", "bookings")),
):
    """
    Get list of bookings with optional filters.
    Router builds a BookingFilters DTO and passes it to the service.
    """
    filters = BookingFilters(
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order,          # "asc" | "desc"
        customer_id=customer_id,
        service_type=service_type,
        status=status,
        payment_status=payment_status,
    pdf_generator.generate_voucher_pdf(booking.model_dump(), pdf_stream)
        created_from=created_from,
        created_to=created_to,
        pax_count_min=pax_count_min,
        pax_count_max=pax_count_max,
        currency=currency,
        search=search,
    )

    service = BookingService(db, redis_client)
    return await service.get_bookings(filters)


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: uuid.UUID,
    db: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "read", "bookings"))
):
    """Get booking by ID"""
    booking_service = BookingService(db, redis_client)
    return await booking_service.get_booking(booking_id)


@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: uuid.UUID,
    booking_data: BookingUpdate,
    db: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "update", "bookings"))
):
    """Update booking information"""
    booking_service = BookingService(db, redis_client)
    return await booking_service.update_booking(booking_id, booking_data, current_user.user_id)


@router.post("/{booking_id}/confirm")
async def confirm_booking(
    booking_id: uuid.UUID,
    db: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "update", "bookings")),
):
    """Confirm a pending booking"""
    service = BookingService(db, redis_client)
    return await service.confirm_booking(booking_id, current_user.user_id)


@router.post("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: uuid.UUID,
    # If you already have a CancelRequest schema, swap the next line for: payload: CancelRequest
    reason: str = Body(..., embed=True),
    db: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "update", "bookings")),
):
    """Cancel a booking"""
    service = BookingService(db, redis_client)
    # If you used a payload model, pass payload.reason instead of reason
    return await service.cancel_booking(booking_id, reason, current_user.user_id)


@router.delete("/{booking_id}")
async def delete_booking(
    booking_id: uuid.UUID,
    db: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "delete", "bookings")),
):
    """Delete a booking"""
    service = BookingService(db, redis_client)
    return await service.delete_booking(booking_id)