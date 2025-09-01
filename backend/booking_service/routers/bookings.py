"""
Booking management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from database import get_session, get_redis
from services.booking_service import BookingService
from schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from utils.auth import get_current_user, require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import Optional, List
import uuid
import logging
import redis.asyncio as redis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bookings", tags=["Booking Management"])


@router.post("/", response_model=BookingResponse)
async def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "create", "bookings"))
):
    """Create a new booking"""
    logger.info(f"Creating booking for customer {booking_data.customer_id}")
    
    booking_service = BookingService(db, redis_client)
    return await booking_service.create_booking(booking_data, current_user.user_id)


@router.get("/", response_model=PaginatedResponse[BookingResponse])
async def get_bookings(
    pagination: PaginationParams = Depends(),
    customer_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    service_type: Optional[str] = None,
    db: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "read", "bookings"))
):
    """Get list of bookings with optional filters"""
    booking_service = BookingService(db, redis_client)
    return await booking_service.get_bookings(
        pagination=pagination,
        customer_id=customer_id,
        status=status,
        service_type=service_type
    )


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
    _: None = Depends(require_permission("booking", "update", "bookings"))
):
    """Confirm a pending booking"""
    booking_service = BookingService(db, redis_client)
    return await booking_service.confirm_booking(booking_id, current_user.user_id)


@router.post("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: uuid.UUID,
    reason: str,
    db: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "update", "bookings"))
):
    """Cancel a booking"""
    booking_service = BookingService(db, redis_client)
    return await booking_service.cancel_booking(booking_id, reason, current_user.user_id)


@router.delete("/{booking_id}")
async def delete_booking(
    booking_id: uuid.UUID,
    db: Session = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(require_permission("booking", "delete", "bookings"))
):
    """Delete a booking"""
    booking_service = BookingService(db)
    return await booking_service.delete_booking(booking_id)