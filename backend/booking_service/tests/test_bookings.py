"""
Tests for booking functionality
"""
import pytest
from services.booking_service import BookingService
from schemas.booking import BookingCreate
from models.booking import BookingStatus, ServiceType
from decimal import Decimal
import uuid


class TestBookings:
    """Test class for booking operations"""
    
    @pytest.mark.asyncio
    async def test_create_booking(self, session, redis_client, sample_booking_data):
        """Test creating a new booking"""
        booking_service = BookingService(session, redis_client)
        
        # Mock customer verification
        booking_service._verify_customer_exists = lambda x: True
        
        booking_create = BookingCreate(**sample_booking_data)
        current_user_id = uuid.uuid4()
        
        booking = await booking_service.create_booking(booking_create, current_user_id)
        
        assert booking.customer_id == uuid.UUID(sample_booking_data["customer_id"])
        assert booking.service_type == ServiceType.TOUR
        assert booking.pax_count == 4
        assert booking.lead_passenger_name == "Ahmed Hassan"
        assert booking.status == BookingStatus.PENDING
        assert booking.expires_at is not None
    
    @pytest.mark.asyncio
    async def test_get_booking(self, session, redis_client, create_test_booking):
        """Test getting booking by ID"""
        booking_service = BookingService(session, redis_client)
        
        # Create test booking
        test_booking = create_test_booking()
        
        # Get booking
        retrieved_booking = await booking_service.get_booking(test_booking.id)
        
        assert retrieved_booking.id == test_booking.id
        assert retrieved_booking.customer_id == test_booking.customer_id
        assert retrieved_booking.service_type == test_booking.service_type
    
    @pytest.mark.asyncio
    async def test_get_booking_not_found(self, session, redis_client):
        """Test getting non-existent booking"""
        booking_service = BookingService(session, redis_client)
        
        fake_id = uuid.uuid4()
        
        with pytest.raises(Exception) as exc_info:
            await booking_service.get_booking(fake_id)
        
        assert "Booking not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_confirm_booking(self, session, redis_client, create_test_booking):
        """Test confirming a pending booking"""
        from schemas.booking import BookingConfirm
        
        booking_service = BookingService(session, redis_client)
        
        # Create pending booking
        test_booking = create_test_booking(status=BookingStatus.PENDING)
        
        # Confirm booking
        confirm_data = BookingConfirm(
            payment_reference="PAY123456",
            internal_notes="Payment confirmed"
        )
        
        confirmed_booking = await booking_service.confirm_booking(test_booking.id, confirm_data)
        
        assert confirmed_booking.status == BookingStatus.CONFIRMED
        assert confirmed_booking.payment_reference == "PAY123456"
        assert confirmed_booking.confirmed_at is not None
        assert confirmed_booking.expires_at is None
    
    @pytest.mark.asyncio
    async def test_cancel_booking(self, session, redis_client, create_test_booking):
        """Test cancelling a booking"""
        from schemas.booking import BookingCancel
        
        booking_service = BookingService(session, redis_client)
        
        # Create confirmed booking
        test_booking = create_test_booking(status=BookingStatus.CONFIRMED)
        
        # Cancel booking
        cancel_data = BookingCancel(
            reason="Customer requested cancellation",
            refund_amount=Decimal("500.00")
        )
        cancelled_by = uuid.uuid4()
        
        cancelled_booking = await booking_service.cancel_booking(
            test_booking.id, cancel_data, cancelled_by
        )
        
        assert cancelled_booking.status == BookingStatus.CANCELLED
        assert cancelled_booking.cancellation_reason == "Customer requested cancellation"
        assert cancelled_booking.cancelled_by == cancelled_by
        assert cancelled_booking.cancelled_at is not None
    
    @pytest.mark.asyncio
    async def test_update_booking(self, session, redis_client, create_test_booking):
        """Test updating booking information"""
        from schemas.booking import BookingUpdate
        
        booking_service = BookingService(session, redis_client)
        
        # Create test booking
        test_booking = create_test_booking()
        
        # Update booking
        update_data = BookingUpdate(
            pax_count=6,
            special_requests="Updated special requests"
        )
        
        updated_booking = await booking_service.update_booking(test_booking.id, update_data)
        
        assert updated_booking.pax_count == 6
        assert updated_booking.special_requests == "Updated special requests"
        assert updated_booking.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_expire_booking(self, session, redis_client, create_test_booking):
        """Test expiring a booking"""
        from datetime import datetime, timedelta
        
        booking_service = BookingService(session, redis_client)
        
        # Create expired booking
        expired_time = datetime.utcnow() - timedelta(minutes=1)
        test_booking = create_test_booking(
            status=BookingStatus.PENDING,
            expires_at=expired_time
        )
        
        # Expire booking
        success = await booking_service.expire_booking(test_booking.id)
        
        assert success is True
        
        # Verify booking is expired
        expired_booking = await booking_service.get_booking(test_booking.id)
        assert expired_booking.status == BookingStatus.EXPIRED
    
    @pytest.mark.asyncio
    async def test_get_booking_summary(self, session, redis_client, create_test_booking, create_test_reservation_item):
        """Test getting comprehensive booking summary"""
        booking_service = BookingService(session, redis_client)
        
        # Mock customer info retrieval
        booking_service._get_customer_info = lambda x: {
            "full_name": "Test Customer",
            "email": "test@example.com"
        }
        
        # Create test booking
        test_booking = create_test_booking()
        
        # Create reservation items
        create_test_reservation_item(test_booking.id, name="Transport")
        create_test_reservation_item(test_booking.id, name="Accommodation")
        
        # Get booking summary
        summary = await booking_service.get_booking_summary(test_booking.id)
        
        assert summary.id == test_booking.id
        assert summary.reservation_items_count == 2
        assert summary.customer_name == "Test Customer"
        assert summary.customer_email == "test@example.com"
        assert summary.can_be_cancelled is True
    
    @pytest.mark.asyncio
    async def test_booking_search(self, session, redis_client, create_test_booking):
        """Test booking search functionality"""
        from schemas.booking import BookingSearch
        from utils.pagination import PaginationParams
        
        booking_service = BookingService(session, redis_client)
        
        # Create test bookings
        customer_id = uuid.uuid4()
        create_test_booking(
            customer_id=customer_id,
            service_type=ServiceType.TOUR,
            status=BookingStatus.CONFIRMED
        )
        create_test_booking(
            customer_id=customer_id,
            service_type=ServiceType.TRANSFER,
            status=BookingStatus.PENDING
        )
        
        # Search by customer ID
        search = BookingSearch(customer_id=customer_id)
        pagination = PaginationParams(page=1, size=10)
        
        bookings, total = await booking_service.get_bookings(pagination, search)
        
        assert total == 2
        assert len(bookings) == 2
        assert all(booking.customer_id == customer_id for booking in bookings)
        
        # Search by service type
        search = BookingSearch(service_type=ServiceType.TOUR)
        bookings, total = await booking_service.get_bookings(pagination, search)
        
        assert total >= 1
        assert all(booking.service_type == ServiceType.TOUR for booking in bookings)