@@ .. @@
 """
 Booking service with improved error handling and customer validation
 """
 import logging
 from typing import List, Optional
 from sqlmodel import Session, select, and_, or_
 from fastapi import HTTPException, status
 from datetime import datetime, date
 import uuid
 
 from models.booking import Booking, BookingStatus
 from schemas.booking import BookingCreate, BookingUpdate, BookingResponse
 from schemas.booking_filters import BookingFilters
+from clients.customer_client import CustomerClient
 from services.pricing_service import PricingService
 from utils.pagination import paginate_query
 
 logger = logging.getLogger(__name__)
 
 
 class BookingService:
     """Service for handling booking operations"""
     
     def __init__(self, session: Session, redis_client=None):
         self.session = session
         self.redis = redis_client
         self.pricing_service = PricingService(session)
+        self.customer_client = CustomerClient()
 
     async def create_booking(self, booking_data: BookingCreate, created_by: Optional[uuid.UUID] = None) -> BookingResponse:
         """Create a new booking with comprehensive validation"""
         
+        logger.info(
+            "Creating booking for customer_id=%s, service_type=%s, pax_count=%s",
+            booking_data.customer_id, booking_data.service_type, booking_data.pax_count
+        )
+        
+        # Validate customer exists early
+        if booking_data.customer_id:
+            try:
+                await self.customer_client.verify_customer_exists(str(booking_data.customer_id))
+            except HTTPException as e:
+                logger.error(f"Customer validation failed: {e.detail}")
+                raise
+        
+        # Validate booking data
+        if booking_data.pax_count < 1:
+            raise HTTPException(
+                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
+                detail="Passenger count must be at least 1"
+            )
+        
+        if booking_data.pax_count > 50:
+            raise HTTPException(
+                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
+                detail="Passenger count cannot exceed 50"
+            )
+        
+        if booking_data.base_price < 0:
+            raise HTTPException(
+                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
+                detail="Base price must be non-negative"
+            )
+        
+        if booking_data.start_date < date.today():
+            raise HTTPException(
+                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
+                detail="Start date cannot be in the past"
+            )
+        
+        if booking_data.end_date and booking_data.end_date < booking_data.start_date:
+            raise HTTPException(
+                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
+                detail="End date must be after start date"
+            )
+        
+        # Calculate pricing if promo code provided
+        total_price = booking_data.base_price
+        discount_amount = 0.0
+        
+        if booking_data.promo_code:
+            try:
+                from schemas.pricing import PricingRequest
+                pricing_request = PricingRequest(
+                    service_type=booking_data.service_type,
+                    base_price=booking_data.base_price,
+                    pax_count=booking_data.pax_count,
+                    start_date=booking_data.start_date,
+                    end_date=booking_data.end_date,
+                    customer_id=booking_data.customer_id,
+                    promo_code=booking_data.promo_code
+                )
+                
+                pricing_result = await self.pricing_service.calculate_pricing(pricing_request)
+                total_price = pricing_result.total_price
+                discount_amount = pricing_result.discount_amount
+                
+                logger.info(f"Pricing calculated: base={booking_data.base_price}, total={total_price}, discount={discount_amount}")
+                
+            except HTTPException as e:
+                logger.error(f"Pricing calculation failed: {e.detail}")
+                raise HTTPException(
+                    status_code=status.HTTP_400_BAD_REQUEST,
+                    detail=f"Pricing calculation failed: {e.detail}"
+                )
+        
         # Create booking
-        booking = Booking(**booking_data.model_dump())
+        try:
+            booking = Booking(
+                customer_id=booking_data.customer_id,
+                service_type=booking_data.service_type,
+                status=BookingStatus.PENDING,
+                pax_count=booking_data.pax_count,
+                lead_passenger_name=booking_data.lead_passenger_name,
+                lead_passenger_email=booking_data.lead_passenger_email,
+                lead_passenger_phone=booking_data.lead_passenger_phone,
+                start_date=booking_data.start_date,
+                end_date=booking_data.end_date,
+                base_price=booking_data.base_price,
+                discount_amount=discount_amount,
+                total_price=total_price,
+                currency=booking_data.currency or "MAD",
+                payment_method=booking_data.payment_method,
+                special_requests=booking_data.special_requests
+            )
+            
+            self.session.add(booking)
+            self.session.commit()
+            self.session.refresh(booking)
+            
+            logger.info(f"Booking created successfully: {booking.id}")
+            
+            return BookingResponse.model_validate(booking)
+            
+        except Exception as e:
+            self.session.rollback()
+            logger.error(f"Failed to create booking: {e}")
+            raise HTTPException(
+                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
+                detail=f"Failed to create booking: {str(e)}"
+            )