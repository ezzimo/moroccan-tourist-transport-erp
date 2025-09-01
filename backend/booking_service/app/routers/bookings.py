import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session
import redis

from database import get_session
from utils.redis import get_redis
from utils.auth import get_current_user, require_permission, CurrentUser
from utils.pagination import PaginationParams, paginate_query
from services.booking_service import BookingService
from services.pricing_service import PricingService
from schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from schemas.booking_filters import BookingFilters
from schemas.pricing import PricingRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/bookings", tags=["Bookings"])

# === ROUTER: CREATE BOOKING ===
import logging
from fastapi import HTTPException, status
from services.booking_service import BookingService
from services.pricing_service import PricingService
from schemas.pricing import PricingRequest

logger = logging.getLogger(__name__)

@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    body: BookingCreate,
    request: Request,
    db: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(get_current_user),
    request: Request = None,
    _: None = Depends(require_permission("booking", "create", "bookings")),
):
    logger.info("Creating booking for customer %s by user %s", 

    # Try to forward Authorization header if present
    bearer = None
    try:
        auth_header = request.headers.get("Authorization") if request else None
        if auth_header and auth_header.lower().startswith("bearer "):
            bearer = auth_header.split(" ", 1)[1]
    except Exception:
        bearer = None

    # Verify customer exists with proper auth forwarding
    await booking_service._verify_customer_exists(str(payload.customer_id), bearer)

    # Create the booking
    return await booking_service.create_booking(payload)

    try:
        # Create service with access token for customer verification
        service = BookingService(db, redis_client, access_token=getattr(current_user, 'access_token', None))

        # Try to forward Authorization header if present
        bearer = None
        try:
            auth_header = request.headers.get("Authorization") if request else None
            if auth_header and auth_header.lower().startswith("bearer "):
                bearer = auth_header.split(" ", 1)[1]
        except Exception:
            bearer = None

        await service._verify_customer_exists(str(body.customer_id), bearer)

        result = await service.create_booking(body, created_by=current_user.user_id)
        
        logger.info("Booking created successfully: %s", result.get("id", "unknown"))
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error creating booking: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create booking"
        )
    """
    Create a new booking with comprehensive validation and pricing
    
    If total_price is not provided, it will be calculated server-side
    using the pricing service and applicable rules.
    """
    logger.info("Creating booking for customer %s by user %s", 
               body.customer_id, current_user.email)
    
    # Input validation
    if not body.customer_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Customer ID is required"
        )
    
    if not body.service_type:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Service type is required"
        )
    
    # If total_price not provided, calculate server-side pricing
    if body.total_price is None:
        if body.base_price is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Either total_price or base_price must be provided"
            )
        
        try:
            logger.debug("Calculating server-side pricing for booking")
            pricing_req = PricingRequest(
                service_type=body.service_type,
                base_price=body.base_price,
                pax_count=body.pax_count,
                start_date=body.start_date,
                end_date=body.end_date,
                customer_id=body.customer_id,
                currency=body.currency or "MAD",
                promo_code=body.promo_code
            )
            pricing_service = PricingService(db)
            pricing_result = await pricing_service.calculate_pricing(pricing_req)
            
            # Update booking data with calculated pricing
            body.total_price = pricing_result.total_price
            body.discount_amount = pricing_result.discount_amount
            
            logger.info("Server-side pricing calculated: total=%s, discount=%s", 
                       pricing_result.total_price, pricing_result.discount_amount)
        except HTTPException:
            # Re-raise pricing validation errors
            raise
        except Exception as ex:
            logger.error("Server-side pricing calculation failed: %s", ex)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to calculate pricing for this booking"
            )
    
    try:
        service = BookingService(db, redis_client)
        booking = await service.create_booking(body, created_by=current_user.user_id)
        
        logger.info("Booking created successfully: id=%s", booking.id)
        return booking
        
    except HTTPException:
        # Re-raise service-level HTTP exceptions
        raise
    except Exception as ex:
        logger.exception("Unexpected error creating booking: %s", ex)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
            detail="Failed to create booking - please try again"