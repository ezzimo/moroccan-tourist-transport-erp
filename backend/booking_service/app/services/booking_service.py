"""
Booking service with improved error handling and customer validation
"""
import logging
from typing import List, Optional
from sqlmodel import Session, select, and_, or_
from fastapi import HTTPException, status
from datetime import datetime, date
import uuid
from decimal import Decimal

from models.booking import Booking, BookingStatus
from schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from schemas.booking_filters import BookingFilters
from clients.customer_client import CustomerClient
from services.pricing_service import PricingService
from schemas.pricing import PricingRequest
from utils.pagination import paginate_query

logger = logging.getLogger(__name__)


class BookingService:
    """Service for handling booking operations"""
    
    def __init__(self, session: Session, redis_client=None):
        self.session = session
        self.redis = redis_client
        self.pricing_service = PricingService(session)
        self.customer_client = CustomerClient()

    async def create_booking(self, booking_data: BookingCreate, created_by: uuid.UUID) -> BookingResponse:
        """Create a new booking with comprehensive validation"""
        logger.info("Creating booking for customer %s, service_type=%s, pax_count=%s", 
                   booking_data.customer_id, booking_data.service_type, booking_data.pax_count)
        
        # === BOOKING: VALIDATION START ===
        # Verify customer exists
        if booking_data.customer_id:
            try:
                await self.customer_client.verify_customer_exists(str(booking_data.customer_id))
            except HTTPException as e:
                logger.error("Customer verification failed for %s: %s", booking_data.customer_id, e.detail)
                raise
        
        # Validate booking data
        if booking_data.pax_count < 1:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Passenger count must be at least 1"
            )
        
        if booking_data.pax_count > 50:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Passenger count cannot exceed 50"
            )
        
        if booking_data.start_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Start date cannot be in the past"
            )
        
        if booking_data.end_date and booking_data.end_date < booking_data.start_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="End date cannot be before start date"
            )
        
        # Calculate pricing if not provided
        if booking_data.total_price is None:
            try:
                pricing_req = PricingRequest(
                    service_type=booking_data.service_type,
                    base_price=Decimal(str(booking_data.base_price or 0)),
                    pax_count=booking_data.pax_count,
                    start_date=booking_data.start_date,
                    end_date=booking_data.end_date,
                    customer_id=booking_data.customer_id,
                    currency=booking_data.currency or "MAD"
                )
                pricing_result = await self.pricing_service.calculate_pricing(pricing_req)
                booking_data.total_price = pricing_result.total_price
                booking_data.discount_amount = pricing_result.discount_amount
                logger.info("Server-side pricing calculated: total=%s, discount=%s", 
                           pricing_result.total_price, pricing_result.discount_amount)
            except Exception as e:
                logger.error("Pricing calculation failed during booking creation: %s", e)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to calculate pricing for this booking"
                )
        # === BOOKING: VALIDATION END ===
        
        # Check for duplicate bookings
        existing_stmt = select(Booking).where(
            and_(
                Booking.customer_id == booking_data.customer_id,
                Booking.start_date == booking_data.start_date,
                Booking.status != BookingStatus.CANCELLED
            )
        )
        existing_booking = self.session.exec(existing_stmt).first()
        
        if existing_booking:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A booking already exists for customer {booking_data.customer_id} on {booking_data.start_date}"
            )
        
        # Create booking
        try:
            booking = Booking(**booking_data.model_dump(), created_by=created_by)
            self.session.add(booking)
            self.session.commit()
            self.session.refresh(booking)
            
            logger.info("Booking created successfully: id=%s, total_price=%s", 
                       booking.id, booking.total_price)
            return BookingResponse.model_validate(booking)
            
        except Exception as e:
            self.session.rollback()
            logger.exception("Failed to create booking: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create booking - please try again"
            )