@@ .. @@
 @router.post("/", response_model=BookingResponse)
 async def create_booking(
     booking_data: BookingCreate,
     db: Session = Depends(get_session),
     current_user: CurrentUser = Depends(get_current_user),
     _: None = Depends(require_permission("booking", "create", "bookings")),
 ):
     """Create a new booking"""
+    
+    logger.info(
+        "Booking creation requested by %s for customer_id=%s",
+        current_user.email, booking_data.customer_id
+    )
+    
+    try:
+        booking_service = BookingService(db)
+        result = await booking_service.create_booking(booking_data, current_user.user_id)
+        
+        logger.info(
+            "Booking created successfully: %s for customer %s",
+            result.id, result.customer_id
+        )
+        
+        return result
+        
+    except HTTPException as e:
+        logger.error(
+            "Booking creation failed for customer %s: %s",
+            booking_data.customer_id, e.detail
+        )
+        raise
+    except Exception as e:
+        logger.exception("Unexpected error creating booking: %s", e)
+        raise HTTPException(
+            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
+            detail=f"Failed to create booking: {str(e)}"
+        )