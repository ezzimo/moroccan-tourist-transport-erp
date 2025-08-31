"""
Tests for reservation item functionality
"""
import pytest
from services.reservation_service import ReservationService
from schemas.booking import ReservationItemCreate, ReservationItemUpdate
from models.enums import ItemType, BookingStatus
from decimal import Decimal


class TestReservationItems:
    """Test class for reservation item operations"""
    
    @pytest.mark.asyncio
    async def test_add_reservation_item(self, session, create_test_booking):
        """Test adding a reservation item to a booking"""
        reservation_service = ReservationService(session)
        
        # Create test booking
        test_booking = create_test_booking(status=BookingStatus.PENDING)
        original_total = test_booking.total_price
        
        # Add reservation item
        item_data = ReservationItemCreate(
            booking_id=test_booking.id,
            type=ItemType.TRANSPORT,
            name="Airport Transfer",
            description="Round trip airport transfer",
            quantity=1,
            unit_price=Decimal("150.00"),
            specifications={"vehicle_type": "SUV", "pickup_time": "08:00"}
        )
        
        item = await reservation_service.add_reservation_item(item_data)
        
        assert item.booking_id == test_booking.id
        assert item.type == ItemType.TRANSPORT
        assert item.name == "Airport Transfer"
        assert item.quantity == 1
        assert item.unit_price == Decimal("150.00")
        assert item.total_price == Decimal("150.00")
        assert item.specifications["vehicle_type"] == "SUV"
        
        # Verify booking total was updated
        from sqlmodel import select
        from models import Booking
        
        updated_booking = session.exec(
            select(Booking).where(Booking.id == test_booking.id)
        ).first()
        
        assert updated_booking.total_price == original_total + Decimal("150.00")
    
    @pytest.mark.asyncio
    async def test_get_reservation_item(self, session, create_test_booking, create_test_reservation_item):
        """Test getting reservation item by ID"""
        reservation_service = ReservationService(session)
        
        # Create test booking and item
        test_booking = create_test_booking()
        test_item = create_test_reservation_item(
            test_booking.id,
            name="Test Service",
            type=ItemType.ACCOMMODATION
        )
        
        # Get item
        retrieved_item = await reservation_service.get_reservation_item(test_item.id)
        
        assert retrieved_item.id == test_item.id
        assert retrieved_item.booking_id == test_booking.id
        assert retrieved_item.name == "Test Service"
        assert retrieved_item.type == ItemType.ACCOMMODATION
    
    @pytest.mark.asyncio
    async def test_get_booking_items(self, session, create_test_booking, create_test_reservation_item):
        """Test getting all reservation items for a booking"""
        reservation_service = ReservationService(session)
        
        # Create test booking
        test_booking = create_test_booking()
        
        # Create multiple items
        item1 = create_test_reservation_item(
            test_booking.id,
            name="Transport",
            type=ItemType.TRANSPORT
        )
        item2 = create_test_reservation_item(
            test_booking.id,
            name="Accommodation",
            type=ItemType.ACCOMMODATION
        )
        item3 = create_test_reservation_item(
            test_booking.id,
            name="Activity",
            type=ItemType.ACTIVITY
        )
        
        # Get all items
        items = await reservation_service.get_booking_items(test_booking.id)
        
        assert len(items) == 3
        assert all(item.booking_id == test_booking.id for item in items)
        
        # Check items are ordered by creation time
        item_names = [item.name for item in items]
        assert "Transport" in item_names
        assert "Accommodation" in item_names
        assert "Activity" in item_names
    
    @pytest.mark.asyncio
    async def test_update_reservation_item(self, session, create_test_booking, create_test_reservation_item):
        """Test updating a reservation item"""
        reservation_service = ReservationService(session)
        
        # Create test booking and item
        test_booking = create_test_booking()
        test_item = create_test_reservation_item(
            test_booking.id,
            name="Original Service",
            quantity=1,
            unit_price=Decimal("100.00")
        )
        
        # Update item
        update_data = ReservationItemUpdate(
            name="Updated Service",
            quantity=2,
            unit_price=Decimal("120.00"),
            specifications={"updated": True}
        )
        
        updated_item = await reservation_service.update_reservation_item(
            test_item.id, update_data
        )
        
        assert updated_item.name == "Updated Service"
        assert updated_item.quantity == 2
        assert updated_item.unit_price == Decimal("120.00")
        assert updated_item.total_price == Decimal("240.00")  # 2 * 120
        assert updated_item.specifications["updated"] is True
        assert updated_item.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_remove_reservation_item(self, session, create_test_booking, create_test_reservation_item):
        """Test removing a reservation item"""
        reservation_service = ReservationService(session)
        
        # Create test booking and item
        test_booking = create_test_booking(total_price=Decimal("1000.00"))
        test_item = create_test_reservation_item(
            test_booking.id,
            unit_price=Decimal("150.00"),
            total_price=Decimal("150.00")
        )
        
        # Remove item
        result = await reservation_service.remove_reservation_item(test_item.id)
        
        assert "removed successfully" in result["message"]
        
        # Verify item was deleted
        with pytest.raises(Exception) as exc_info:
            await reservation_service.get_reservation_item(test_item.id)
        
        assert "not found" in str(exc_info.value)
        
        # Verify booking total was updated
        from sqlmodel import select
        from models import Booking
        
        updated_booking = session.exec(
            select(Booking).where(Booking.id == test_booking.id)
        ).first()
        
        assert updated_booking.total_price == Decimal("850.00")  # 1000 - 150
    
    @pytest.mark.asyncio
    async def test_confirm_reservation_item(self, session, create_test_booking, create_test_reservation_item):
        """Test confirming a reservation item"""
        reservation_service = ReservationService(session)
        
        # Create test booking and item
        test_booking = create_test_booking()
        test_item = create_test_reservation_item(
            test_booking.id,
            is_confirmed=False
        )
        
        # Confirm item
        confirmed_item = await reservation_service.confirm_reservation_item(test_item.id)
        
        assert confirmed_item.is_confirmed is True
        assert confirmed_item.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_cancel_reservation_item(self, session, create_test_booking, create_test_reservation_item):
        """Test cancelling a reservation item"""
        reservation_service = ReservationService(session)
        
        # Create test booking and item
        test_booking = create_test_booking(total_price=Decimal("1000.00"))
        test_item = create_test_reservation_item(
            test_booking.id,
            unit_price=Decimal("200.00"),
            total_price=Decimal("200.00")
        )
        
        # Cancel item
        cancelled_item = await reservation_service.cancel_reservation_item(test_item.id)
        
        assert cancelled_item.is_cancelled is True
        assert cancelled_item.updated_at is not None
        
        # Verify booking total was updated (cancelled item cost removed)
        from sqlmodel import select
        from models import Booking
        
        updated_booking = session.exec(
            select(Booking).where(Booking.id == test_booking.id)
        ).first()
        
        assert updated_booking.total_price == Decimal("800.00")  # 1000 - 200
    
    @pytest.mark.asyncio
    async def test_get_booking_summary(self, session, create_test_booking, create_test_reservation_item):
        """Test getting booking items summary"""
        reservation_service = ReservationService(session)
        
        # Create test booking
        test_booking = create_test_booking()
        
        # Create various items
        create_test_reservation_item(
            test_booking.id,
            type=ItemType.TRANSPORT,
            unit_price=Decimal("150.00"),
            total_price=Decimal("150.00"),
            is_confirmed=True
        )
        create_test_reservation_item(
            test_booking.id,
            type=ItemType.ACCOMMODATION,
            unit_price=Decimal("300.00"),
            total_price=Decimal("300.00"),
            is_confirmed=False
        )
        create_test_reservation_item(
            test_booking.id,
            type=ItemType.ACTIVITY,
            unit_price=Decimal("100.00"),
            total_price=Decimal("100.00"),
            is_cancelled=True
        )
        
        # Get summary
        summary = await reservation_service.get_booking_summary(test_booking.id)
        
        assert summary["total_items"] == 3
        assert summary["confirmed_items"] == 1
        assert summary["cancelled_items"] == 1
        assert summary["pending_items"] == 1
        assert summary["total_value"] == 450.0  # 150 + 300 (cancelled not counted)
        
        # Check by type
        assert "Transport" in summary["by_type"]
        assert "Accommodation" in summary["by_type"]
        assert "Activity" in summary["by_type"]
        
        assert summary["by_type"]["Transport"]["count"] == 1
        assert summary["by_type"]["Transport"]["confirmed"] == 1
        assert summary["by_type"]["Transport"]["total_value"] == 150.0
        
        assert summary["by_type"]["Activity"]["cancelled"] == 1
        assert summary["by_type"]["Activity"]["total_value"] == 0.0  # Cancelled
    
    @pytest.mark.asyncio
    async def test_cannot_modify_cancelled_booking(self, session, create_test_booking):
        """Test that reservation items cannot be added to cancelled bookings"""
        reservation_service = ReservationService(session)
        
        # Create cancelled booking
        test_booking = create_test_booking(status=BookingStatus.CANCELLED)
        
        # Try to add item
        item_data = ReservationItemCreate(
            booking_id=test_booking.id,
            type=ItemType.TRANSPORT,
            name="Test Service",
            quantity=1,
            unit_price=Decimal("100.00")
        )
        
        with pytest.raises(Exception) as exc_info:
            await reservation_service.add_reservation_item(item_data)
        
        assert "Cannot modify cancelled" in str(exc_info.value)