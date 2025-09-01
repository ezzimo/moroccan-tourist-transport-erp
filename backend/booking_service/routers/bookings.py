"""
Booking management routes with PDF voucher generation
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import Response
from sqlmodel import Session
from database import get_session, get_redis
from services.booking_service import BookingService
from schemas.booking import (
    BookingCreate, BookingUpdate, BookingResponse, BookingConfirmation,
    BookingCancellation, BookingSearch
)
from models.enums import BookingStatus, PaymentStatus
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from utils.pdf_generator import get_pdf_generator
from typing import List, Optional
import redis
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/bookings", tags=["Booking Management"])


@router.post("/", response_model=BookingResponse)
async def create_booking(
    booking_data: BookingCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("booking", "create", "bookings"))
):
    """Create a new booking"""
    try:
        booking_service = BookingService(session, redis_client)
        booking = await booking_service.create_booking(booking_data)
        logger.info(f"Booking created successfully: {booking.id}")
        return booking
    except Exception as e:
        logger.error(f"Failed to create booking: {e}")
        raise


@router.get("/", response_model=PaginatedResponse[BookingResponse])
async def get_bookings(
    pagination: PaginationParams = Depends(),
    customer_id: Optional[uuid.UUID] = Query(None, description="Filter by customer ID"),
    status: Optional[BookingStatus] = Query(None, description="Filter by booking status"),
    service_type: Optional[str] = Query(None, description="Filter by service type"),
    start_date_from: Optional[str] = Query(None, description="Filter by start date from (YYYY-MM-DD)"),
    start_date_to: Optional[str] = Query(None, description="Filter by start date to (YYYY-MM-DD)"),
    payment_status: Optional[PaymentStatus] = Query(None, description="Filter by payment status"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("booking", "read", "bookings"))
):
    """Get list of bookings with optional filters"""
    try:
        booking_service = BookingService(session, redis_client)
        
        # Build search criteria
        search = None
        if any([customer_id, status, service_type, start_date_from, start_date_to, payment_status]):
            search = BookingSearch(
                customer_id=customer_id,
                status=status,
                service_type=service_type,
                start_date_from=start_date_from,
                start_date_to=start_date_to,
                payment_status=payment_status
            )
        
        bookings, total = await booking_service.get_bookings(pagination, search)
        
        return PaginatedResponse.create(
            items=bookings,
            total=total,
            page=pagination.page,
            size=pagination.size
        )
    except Exception as e:
        logger.error(f"Failed to get bookings: {e}")
        raise


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("booking", "read", "bookings"))
):
    """Get booking by ID"""
    try:
        booking_service = BookingService(session, redis_client)
        booking = await booking_service.get_booking(booking_id)
        return booking
    except Exception as e:
        logger.error(f"Failed to get booking {booking_id}: {e}")
        raise


@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: uuid.UUID,
    booking_data: BookingUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("booking", "update", "bookings"))
):
    """Update booking information"""
    try:
        booking_service = BookingService(session, redis_client)
        booking = await booking_service.update_booking(booking_id, booking_data)
        logger.info(f"Booking updated successfully: {booking_id}")
        return booking
    except Exception as e:
        logger.error(f"Failed to update booking {booking_id}: {e}")
        raise


@router.post("/{booking_id}/confirm", response_model=BookingResponse)
async def confirm_booking(
    booking_id: uuid.UUID,
    confirmation_data: BookingConfirmation,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("booking", "update", "bookings"))
):
    """Confirm a pending booking"""
    try:
        booking_service = BookingService(session, redis_client)
        booking = await booking_service.confirm_booking(booking_id, confirmation_data)
        logger.info(f"Booking confirmed successfully: {booking_id}")
        return booking
    except Exception as e:
        logger.error(f"Failed to confirm booking {booking_id}: {e}")
        raise


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: uuid.UUID,
    cancellation_data: BookingCancellation,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("booking", "update", "bookings"))
):
    """Cancel a booking"""
    try:
        booking_service = BookingService(session, redis_client)
        booking = await booking_service.cancel_booking(booking_id, cancellation_data)
        logger.info(f"Booking cancelled successfully: {booking_id}")
        return booking
    except Exception as e:
        logger.error(f"Failed to cancel booking {booking_id}: {e}")
        raise


@router.get("/{booking_id}/voucher")
async def download_booking_voucher(
    booking_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "read", "bookings"))
):
    """Generate and download booking voucher PDF"""
    try:
        booking_service = BookingService(session, None)
        booking = await booking_service.get_booking(booking_id)
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        # Generate PDF voucher
        try:
            pdf_generator = get_pdf_generator()
            pdf_content = pdf_generator.generate_booking_voucher(booking.model_dump())
            
            return Response(
                content=pdf_content,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=booking_voucher_{booking_id}.pdf"
                }
            )
        except Exception as pdf_error:
            logger.warning(f"PDF generation failed, falling back to text: {pdf_error}")
            
            # Fallback to simple text receipt
            pdf_generator = get_pdf_generator()
            text_content = pdf_generator.generate_simple_receipt(booking.model_dump())
            
            return Response(
                content=text_content,
                media_type="text/plain",
                headers={
                    "Content-Disposition": f"attachment; filename=booking_receipt_{booking_id}.txt"
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate voucher for booking {booking_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate booking voucher"
        )


@router.delete("/{booking_id}")
async def delete_booking(
    booking_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("booking", "delete", "bookings"))
):
    """Delete a booking (soft delete)"""
    try:
        booking_service = BookingService(session, redis_client)
        result = await booking_service.delete_booking(booking_id)
        logger.info(f"Booking deleted successfully: {booking_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to delete booking {booking_id}: {e}")
        raise