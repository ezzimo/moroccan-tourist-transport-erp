"""
Tests for availability functionality
"""
import pytest
from services.availability_service import AvailabilityService
from schemas.booking import AvailabilityRequest
from models.booking import ResourceType
from datetime import date, timedelta
import uuid


class TestAvailability:
    """Test class for availability operations"""
    
    @pytest.mark.asyncio
    async def test_check_availability_with_available_resources(self, session, create_test_availability_slot):
        """Test checking availability with available resources"""
        availability_service = AvailabilityService(session)
        
        # Create available slot
        resource_id = uuid.uuid4()
        test_date = date.today() + timedelta(days=7)
        
        create_test_availability_slot(
            resource_id=resource_id,
            resource_name="Test Vehicle 1",
            date=test_date,
            total_capacity=8,
            available_capacity=8
        )
        
        # Check availability
        request = AvailabilityRequest(
            resource_type=ResourceType.VEHICLE,
            start_date=test_date,
            required_capacity=4
        )
        
        response = await availability_service.check_availability(request)
        
        assert response.has_availability is True
        assert response.total_available == 1
        assert len(response.available_resources) == 1
        assert response.available_resources[0].resource_id == resource_id
        assert response.available_resources[0].is_available is True
    
    @pytest.mark.asyncio
    async def test_check_availability_insufficient_capacity(self, session, create_test_availability_slot):
        """Test checking availability with insufficient capacity"""
        availability_service = AvailabilityService(session)
        
        # Create slot with limited capacity
        resource_id = uuid.uuid4()
        test_date = date.today() + timedelta(days=7)
        
        create_test_availability_slot(
            resource_id=resource_id,
            date=test_date,
            total_capacity=8,
            available_capacity=2  # Only 2 available
        )
        
        # Request more capacity than available
        request = AvailabilityRequest(
            resource_type=ResourceType.VEHICLE,
            start_date=test_date,
            required_capacity=4  # Need 4, but only 2 available
        )
        
        response = await availability_service.check_availability(request)
        
        assert response.has_availability is False
        assert response.total_available == 0
        assert len(response.available_resources) == 1
        assert response.available_resources[0].is_available is False
    
    @pytest.mark.asyncio
    async def test_check_availability_blocked_resource(self, session, create_test_availability_slot):
        """Test checking availability with blocked resources"""
        availability_service = AvailabilityService(session)
        
        # Create blocked slot
        resource_id = uuid.uuid4()
        test_date = date.today() + timedelta(days=7)
        
        create_test_availability_slot(
            resource_id=resource_id,
            date=test_date,
            total_capacity=8,
            available_capacity=8,
            is_blocked=True,
            block_reason="Maintenance"
        )
        
        # Check availability
        request = AvailabilityRequest(
            resource_type=ResourceType.VEHICLE,
            start_date=test_date,
            required_capacity=4
        )
        
        response = await availability_service.check_availability(request)
        
        assert response.has_availability is False
        assert response.total_available == 0
        assert len(response.available_resources) == 0  # Blocked resources not included
    
    @pytest.mark.asyncio
    async def test_reserve_capacity(self, session, create_test_availability_slot):
        """Test reserving capacity for a booking"""
        availability_service = AvailabilityService(session)
        
        # Create available slot
        resource_id = uuid.uuid4()
        test_date = date.today() + timedelta(days=7)
        
        slot = create_test_availability_slot(
            resource_id=resource_id,
            date=test_date,
            total_capacity=8,
            available_capacity=8
        )
        
        # Reserve capacity
        booking_id = uuid.uuid4()
        success = await availability_service.reserve_capacity(
            resource_id, test_date, 4, booking_id
        )
        
        assert success is True
        
        # Verify capacity was reserved
        from sqlmodel import select
        from models.availability import AvailabilitySlot
        
        updated_slot = session.exec(
            select(AvailabilitySlot).where(AvailabilitySlot.id == slot.id)
        ).first()
        
        assert updated_slot.available_capacity == 4  # 8 - 4 = 4
        assert updated_slot.reserved_capacity == 4
        assert updated_slot.booking_id == booking_id
    
    @pytest.mark.asyncio
    async def test_reserve_capacity_insufficient(self, session, create_test_availability_slot):
        """Test reserving more capacity than available"""
        availability_service = AvailabilityService(session)
        
        # Create slot with limited capacity
        resource_id = uuid.uuid4()
        test_date = date.today() + timedelta(days=7)
        
        create_test_availability_slot(
            resource_id=resource_id,
            date=test_date,
            total_capacity=8,
            available_capacity=2  # Only 2 available
        )
        
        # Try to reserve more than available
        booking_id = uuid.uuid4()
        
        with pytest.raises(Exception) as exc_info:
            await availability_service.reserve_capacity(
                resource_id, test_date, 4, booking_id  # Need 4, but only 2 available
            )
        
        assert "Insufficient capacity" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_release_capacity(self, session, create_test_availability_slot):
        """Test releasing reserved capacity"""
        availability_service = AvailabilityService(session)
        
        # Create slot with reserved capacity
        resource_id = uuid.uuid4()
        test_date = date.today() + timedelta(days=7)
        
        slot = create_test_availability_slot(
            resource_id=resource_id,
            date=test_date,
            total_capacity=8,
            available_capacity=4,  # 4 available
            reserved_capacity=4   # 4 reserved
        )
        
        # Release capacity
        success = await availability_service.release_capacity(
            resource_id, test_date, 2  # Release 2
        )
        
        assert success is True
        
        # Verify capacity was released
        from sqlmodel import select
        from models.availability import AvailabilitySlot
        
        updated_slot = session.exec(
            select(AvailabilitySlot).where(AvailabilitySlot.id == slot.id)
        ).first()
        
        assert updated_slot.available_capacity == 6  # 4 + 2 = 6
        assert updated_slot.reserved_capacity == 2   # 4 - 2 = 2
    
    @pytest.mark.asyncio
    async def test_block_resource(self, session, create_test_availability_slot):
        """Test blocking a resource"""
        availability_service = AvailabilityService(session)
        
        # Create available slots
        resource_id = uuid.uuid4()
        start_date = date.today() + timedelta(days=7)
        end_date = start_date + timedelta(days=2)
        
        create_test_availability_slot(
            resource_id=resource_id,
            date=start_date
        )
        create_test_availability_slot(
            resource_id=resource_id,
            date=start_date + timedelta(days=1)
        )
        create_test_availability_slot(
            resource_id=resource_id,
            date=end_date
        )
        
        # Block resource
        blocked_slots = await availability_service.block_resource(
            resource_id, start_date, end_date, "Maintenance scheduled"
        )
        
        assert len(blocked_slots) == 3
        assert all(slot.is_blocked for slot in blocked_slots)
        assert all(slot.block_reason == "Maintenance scheduled" for slot in blocked_slots)
    
    @pytest.mark.asyncio
    async def test_get_resource_schedule(self, session, create_test_availability_slot):
        """Test getting resource schedule"""
        availability_service = AvailabilityService(session)
        
        # Create slots for different dates
        resource_id = uuid.uuid4()
        start_date = date.today() + timedelta(days=7)
        
        slot1 = create_test_availability_slot(
            resource_id=resource_id,
            date=start_date,
            resource_name="Test Vehicle"
        )
        slot2 = create_test_availability_slot(
            resource_id=resource_id,
            date=start_date + timedelta(days=1),
            resource_name="Test Vehicle"
        )
        
        # Get schedule
        schedule = await availability_service.get_resource_schedule(
            resource_id, start_date, start_date + timedelta(days=1)
        )
        
        assert len(schedule) == 2
        assert schedule[0].date == start_date
        assert schedule[1].date == start_date + timedelta(days=1)
        assert all(slot.resource_id == resource_id for slot in schedule)
    
    @pytest.mark.asyncio
    async def test_get_availability_summary(self, session, create_test_availability_slot):
        """Test getting availability summary"""
        availability_service = AvailabilityService(session)
        
        # Create various slots
        start_date = date.today() + timedelta(days=7)
        end_date = start_date + timedelta(days=2)
        
        # Available slot
        create_test_availability_slot(
            resource_type=ResourceType.VEHICLE,
            date=start_date,
            total_capacity=8,
            available_capacity=8
        )
        
        # Partially booked slot
        create_test_availability_slot(
            resource_type=ResourceType.VEHICLE,
            date=start_date + timedelta(days=1),
            total_capacity=8,
            available_capacity=4,
            reserved_capacity=4
        )
        
        # Blocked slot
        create_test_availability_slot(
            resource_type=ResourceType.GUIDE,
            date=start_date + timedelta(days=2),
            total_capacity=1,
            available_capacity=1,
            is_blocked=True
        )
        
        # Get summary
        summary = await availability_service.get_availability_summary(
            start_date, end_date
        )
        
        assert summary["total_slots"] == 3
        assert summary["available_slots"] == 2  # 2 not blocked with capacity > 0
        assert summary["blocked_slots"] == 1
        assert summary["total_capacity"] == 17  # 8 + 8 + 1
        assert summary["available_capacity"] == 12  # 8 + 4 (blocked slot not counted)
        assert summary["reserved_capacity"] == 4
        
        # Check by resource type
        assert "Vehicle" in summary["by_resource_type"]
        assert "Guide" in summary["by_resource_type"]
        assert summary["by_resource_type"]["Vehicle"]["total_slots"] == 2
        assert summary["by_resource_type"]["Guide"]["total_slots"] == 1