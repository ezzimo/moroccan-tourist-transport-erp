"""
Booking service for booking management operations
"""

from sqlmodel import Session, select, and_, or_, func
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
from schemas.booking_filters import BookingFilters
from utils.pagination import PaginationParams, paginate_query
from utils.locking import acquire_booking_lock, release_booking_lock
from services.pricing_service import PricingService
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from math import ceil
import redis
import uuid
import httpx
import json
import logging

logger = logging.getLogger(__name__)


class BookingService:
    """Service for handling booking operations"""

    def __init__(self, session: Session, redis_client=None):
        self.session = session
        self.redis = redis_client  # Optional for backward compatibility
        self.pricing_service = PricingService(session)

    async def create_booking(
        self,
        booking_data: BookingCreate,
        current_user_id: uuid.UUID,
        customer_verified: bool = False,
        customer_snapshot: Optional[Dict[str, Any]] = None,
    ) -> BookingResponse:
        """Create a new booking with locking mechanism"""
        logger.info("Creating booking with verification status: %s", customer_verified)
        logger.debug("DIAGNOSTIC: Starting create_booking - customer_id=%s, service_type=%s, base_price=%s", 
                    booking_data.customer_id, booking_data.service_type, booking_data.base_price)
        
        # Acquire lock for booking creation
        lock_key = (
            f"booking_create:{booking_data.customer_id}:{booking_data.start_date}"
        )
        logger.debug("DIAGNOSTIC: Acquiring lock with key: %s", lock_key)
        lock_id = acquire_booking_lock(
            self.redis,
            "booking",
            str(booking_data.customer_id),
            str(booking_data.start_date),
        )

        if not lock_id:
            logger.debug("DIAGNOSTIC: Failed to acquire lock")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Another booking is being processed. Please try again.",
            )
        
        logger.debug("DIAGNOSTIC: Lock acquired successfully: %s", lock_id)

        try:
            # Verify customer exists (call CRM service)
            logger.debug("DIAGNOSTIC: About to verify customer exists")
            await self._verify_customer_exists(booking_data.customer_id)
            logger.debug("DIAGNOSTIC: Customer verification completed successfully")

            # Calculate pricing
            logger.debug("DIAGNOSTIC: Starting pricing calculation")
            pricing_request = {
                "service_type": booking_data.service_type.value,
                "base_price": booking_data.base_price,
                "pax_count": booking_data.pax_count,
                "start_date": booking_data.start_date,
                "end_date": booking_data.end_date,
                "customer_id": booking_data.customer_id,
                "promo_code": booking_data.promo_code,
            }
            logger.debug("DIAGNOSTIC: Pricing request data: %s", pricing_request)

            pricing_result = await self.pricing_service.calculate_pricing(
                pricing_request
            )
            logger.debug("DIAGNOSTIC: Pricing calculation completed: %s", pricing_result)

            # Prepare booking data
            logger.debug("DIAGNOSTIC: Preparing booking data")
            booking_dict = booking_data.model_dump()
            
            # Add verification metadata to internal notes
            notes = booking_dict.get("internal_notes", "") or ""
            verification_info = []
            
            if not customer_verified:
                verification_info.append("[customer_unverified]")
            else:
                verification_info.append("[customer_verified]")
                if customer_snapshot:
                    customer_name = customer_snapshot.get("full_name") or customer_snapshot.get("company_name")
                    if customer_name:
                        verification_info.append(f"customer_name:{customer_name}")
            
            if verification_info:
                notes = f"{' '.join(verification_info)} {notes}".strip()
                booking_dict["internal_notes"] = notes
            
            logger.debug("DIAGNOSTIC: Booking dict prepared with notes: %s", notes[:100])

            # Create booking
            logger.debug("DIAGNOSTIC: Creating Booking model instance")
            try:
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
                    internal_notes=booking_dict.get("internal_notes"),
                    expires_at=datetime.utcnow() + timedelta(minutes=30),  # 30 min expiry
                )
                logger.debug("DIAGNOSTIC: Booking model instance created successfully")
            except Exception as e:
                logger.error("DIAGNOSTIC: Failed to create Booking model instance: %s", str(e))
                logger.error("DIAGNOSTIC: Exception type: %s", type(e).__name__)
                raise

            logger.debug("DIAGNOSTIC: Adding booking to session")
            self.session.add(booking)
            logger.debug("DIAGNOSTIC: About to commit booking to database")
            self.session.commit()
            logger.debug("DIAGNOSTIC: Booking committed successfully")
            self.session.refresh(booking)
            logger.debug("DIAGNOSTIC: Booking refreshed, ID: %s", booking.id)

            # Schedule expiry check
            logger.debug("DIAGNOSTIC: Scheduling booking expiry")
            await self._schedule_booking_expiry(booking.id)
            logger.debug("DIAGNOSTIC: Booking expiry scheduled")

            logger.info("Booking created: %s (verified: %s)", booking.id, customer_verified)
            logger.debug("DIAGNOSTIC: About to create BookingResponse")
            try:
                response = BookingResponse(**booking.model_dump())
                logger.debug("DIAGNOSTIC: BookingResponse created successfully")
                return response
            except Exception as e:
                logger.error("DIAGNOSTIC: Failed to create BookingResponse: %s", str(e))
                logger.error("DIAGNOSTIC: Exception type: %s", type(e).__name__)
                logger.error("DIAGNOSTIC: Booking model dump: %s", booking.model_dump())
                raise

        finally:
            # Always release the lock
            logger.debug("DIAGNOSTIC: Releasing lock: %s", lock_id)
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

    async def get_bookings(self, filters: BookingFilters):
        """Get paginated list of bookings with filters"""
        # Build base query
        query = select(Booking)
        count_query = select(func.count(Booking.id))
        
        # Apply filters based on actual Booking model fields
        conditions = []
        
        if filters.customer_id is not None:
            conditions.append(Booking.customer_id == filters.customer_id)
        
        if filters.service_type is not None:
            conditions.append(Booking.service_type == filters.service_type)
        
        if filters.status is not None:
            conditions.append(Booking.status == filters.status)
        
        if filters.payment_status is not None:
            conditions.append(Booking.payment_status == filters.payment_status)
        
        if filters.start_date_from is not None:
            from datetime import datetime
            start_date = datetime.strptime(filters.start_date_from, "%Y-%m-%d").date()
            conditions.append(Booking.start_date >= start_date)
        
        if filters.start_date_to is not None:
            from datetime import datetime
            end_date = datetime.strptime(filters.start_date_to, "%Y-%m-%d").date()
            conditions.append(Booking.start_date <= end_date)
        
        if filters.created_from is not None:
            conditions.append(Booking.created_at >= filters.created_from)
        
        if filters.created_to is not None:
            conditions.append(Booking.created_at <= filters.created_to)
        
        if filters.pax_count_min is not None:
            conditions.append(Booking.pax_count >= filters.pax_count_min)
        
        if filters.pax_count_max is not None:
            conditions.append(Booking.pax_count <= filters.pax_count_max)
        
        if filters.currency is not None:
            conditions.append(Booking.currency == filters.currency)
        
        if filters.search:
            # Search in lead passenger name and email (actual model fields)
            search_term = f"%{filters.search}%"
            conditions.append(
                or_(
                    func.lower(Booking.lead_passenger_name).like(search_term.lower()),
                    func.lower(Booking.lead_passenger_email).like(search_term.lower())
                )
            )
        
        # Apply all conditions
        if conditions:
            from sqlmodel import and_
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Apply sorting
        if filters.sort_by:
            # Safe list of sortable columns
            sortable_columns = {
                'created_at': Booking.created_at,
                'start_date': Booking.start_date,
                'total_price': Booking.total_price,
                'lead_passenger_name': Booking.lead_passenger_name,
                'status': Booking.status,
                'pax_count': Booking.pax_count
            }
            
            if filters.sort_by in sortable_columns:
                col = sortable_columns[filters.sort_by]
                if filters.sort_order == "desc":
                    query = query.order_by(col.desc())
                else:
                    query = query.order_by(col.asc())
            else:
                # Default sort if invalid sort_by
                query = query.order_by(Booking.created_at.desc())
        else:
            # Default sort by creation date
            query = query.order_by(Booking.created_at.desc())
        
        # Get total count
        total = self.session.exec(count_query).one()
        
        # Apply pagination
        items = self.session.exec(query.offset(filters.offset).limit(filters.size)).all()
        
        return {
            "items": items,
            "page": filters.page,
            "size": filters.size,
            "total": total,
            "pages": ceil(total / filters.size) if filters.size else 1
        }

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

    async def generate_voucher_pdf(self, booking_id: uuid.UUID) -> bytes:
        """Generate booking voucher PDF"""
        from config import settings
        from utils import pdf_generator
        
        if not settings.pdf_enabled or not pdf_generator.have_reportlab():
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="PDF generation is not available"
            )
        
        booking = await self.get_booking(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        # Convert booking to dict for PDF generation
        booking_dict = booking.model_dump() if hasattr(booking, 'model_dump') else booking.__dict__
        
        return pdf_generator.generate_booking_confirmation(booking_dict)
    
    async def _verify_customer_exists(self, customer_id: uuid.UUID) -> bool:
        """Verify customer exists in CRM service"""
        logger.debug("DIAGNOSTIC: _verify_customer_exists called for customer_id: %s", customer_id)
        try:
            from config import settings

            logger.debug("DIAGNOSTIC: Making HTTP request to CRM service: %s", settings.crm_service_url)
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.crm_service_url}/api/v1/customers/{customer_id}"
                )
                logger.debug("DIAGNOSTIC: CRM response status: %s", response.status_code)
                if response.status_code != 200:
                    logger.debug("DIAGNOSTIC: CRM response body: %s", response.text[:200])
                return response.status_code == 200
        except Exception as e:
            logger.error("DIAGNOSTIC: Exception in _verify_customer_exists: %s", str(e))
            logger.error("DIAGNOSTIC: Exception type: %s", type(e).__name__)
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
        logger.debug("DIAGNOSTIC: _schedule_booking_expiry called for booking_id: %s", booking_id)
        # In a production environment, you would use Celery or similar
        # For now, we'll store the expiry in Redis
        try:
            expiry_key = f"booking_expiry:{booking_id}"
            logger.debug("DIAGNOSTIC: Setting Redis expiry key: %s", expiry_key)
            
            # Check if redis client is async or sync
            if hasattr(self.redis, 'setex'):
                # Sync Redis client
                self.redis.setex(expiry_key, 1800, str(booking_id))  # 30 minutes
                logger.debug("DIAGNOSTIC: Redis expiry set using sync client")
            else:
                # Async Redis client - this would need await
                logger.warning("DIAGNOSTIC: Async Redis client detected but method not awaited")
                # For now, skip to avoid blocking
                pass
        except Exception as e:
            logger.error("DIAGNOSTIC: Exception in _schedule_booking_expiry: %s", str(e))
            logger.error("DIAGNOSTIC: Exception type: %s", type(e).__name__)
            # Don't fail booking creation for expiry scheduling issues
            pass