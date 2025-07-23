"""
Tests for itinerary functionality
"""
import pytest
from services.itinerary_service import ItineraryService
from schemas.itinerary_item import ItineraryItemCreate, ItineraryItemCompletion
from models.itinerary_item import ActivityType
from datetime import time
import uuid


class TestItinerary:
    """Test class for itinerary operations"""
    
    @pytest.mark.asyncio
    async def test_add_itinerary_item(self, session, redis_client, create_test_tour_template, create_test_tour_instance, sample_itinerary_item_data):
        """Test adding an itinerary item to a tour"""
        itinerary_service = ItineraryService(session, redis_client)
        
        # Create template and instance
        test_template = create_test_tour_template(duration_days=3)
        test_instance = create_test_tour_instance(test_template.id)
        
        # Add itinerary item
        item_data = ItineraryItemCreate(
            tour_instance_id=test_instance.id,
            **sample_itinerary_item_data
        )
        
        item = await itinerary_service.add_item(item_data)
        
        assert item.tour_instance_id == test_instance.id
        assert item.day_number == 1
        assert item.activity_type == ActivityType.VISIT
        assert item.title == "Ait Benhaddou Kasbah"
        assert item.location_name == "Ait Benhaddou"
        assert item.coordinates == (31.047043, -7.129532)
        assert item.is_completed is False
    
    @pytest.mark.asyncio
    async def test_add_item_invalid_day(self, session, redis_client, create_test_tour_template, create_test_tour_instance):
        """Test adding item with invalid day number"""
        itinerary_service = ItineraryService(session, redis_client)
        
        # Create template and instance with 3-day duration
        test_template = create_test_tour_template(duration_days=3)
        test_instance = create_test_tour_instance(test_template.id)
        
        # Try to add item for day 5 (exceeds duration)
        item_data = ItineraryItemCreate(
            tour_instance_id=test_instance.id,
            day_number=5,  # Invalid - exceeds 3-day duration
            activity_type=ActivityType.VISIT,
            title="Invalid Day Activity"
        )
        
        with pytest.raises(Exception) as exc_info:
            await itinerary_service.add_item(item_data)
        
        assert "cannot exceed tour duration" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_tour_itinerary(self, session, redis_client, create_test_tour_template, create_test_tour_instance, create_test_itinerary_item):
        """Test getting all itinerary items for a tour"""
        itinerary_service = ItineraryService(session, redis_client)
        
        # Create template and instance
        test_template = create_test_tour_template()
        test_instance = create_test_tour_instance(test_template.id)
        
        # Create multiple itinerary items
        create_test_itinerary_item(
            test_instance.id,
            day_number=1,
            title="Morning Activity",
            start_time=time(9, 0)
        )
        create_test_itinerary_item(
            test_instance.id,
            day_number=1,
            title="Afternoon Activity",
            start_time=time(14, 0)
        )
        create_test_itinerary_item(
            test_instance.id,
            day_number=2,
            title="Day 2 Activity",
            start_time=time(10, 0)
        )
        
        # Get tour itinerary
        items = await itinerary_service.get_tour_itinerary(test_instance.id)
        
        assert len(items) == 3
        # Should be ordered by day, then by start time
        assert items[0].title == "Morning Activity"
        assert items[1].title == "Afternoon Activity"
        assert items[2].title == "Day 2 Activity"
    
    @pytest.mark.asyncio
    async def test_get_day_itinerary(self, session, redis_client, create_test_tour_template, create_test_tour_instance, create_test_itinerary_item):
        """Test getting itinerary for a specific day"""
        itinerary_service = ItineraryService(session, redis_client)
        
        # Create template and instance
        test_template = create_test_tour_template()
        test_instance = create_test_tour_instance(test_template.id)
        
        # Create items for different days
        create_test_itinerary_item(
            test_instance.id,
            day_number=1,
            title="Day 1 Activity",
            duration_minutes=120,
            is_completed=True
        )
        create_test_itinerary_item(
            test_instance.id,
            day_number=1,
            title="Day 1 Activity 2",
            duration_minutes=90,
            is_completed=False
        )
        create_test_itinerary_item(
            test_instance.id,
            day_number=2,
            title="Day 2 Activity"
        )
        
        # Get day 1 itinerary
        day_itinerary = await itinerary_service.get_day_itinerary(test_instance.id, 1)
        
        assert day_itinerary.day_number == 1
        assert len(day_itinerary.items) == 2
        assert day_itinerary.total_items == 2
        assert day_itinerary.completed_items == 1
        assert day_itinerary.estimated_duration_minutes == 210  # 120 + 90
    
    @pytest.mark.asyncio
    async def test_complete_itinerary_item(self, session, redis_client, create_test_tour_template, create_test_tour_instance, create_test_itinerary_item):
        """Test marking an itinerary item as completed"""
        itinerary_service = ItineraryService(session, redis_client)
        
        # Create template and instance
        test_template = create_test_tour_template()
        test_instance = create_test_tour_instance(test_template.id)
        
        # Create itinerary item
        test_item = create_test_itinerary_item(
            test_instance.id,
            title="Test Activity",
            is_completed=False
        )
        
        # Complete the item
        completion_data = ItineraryItemCompletion(
            notes="Activity completed successfully",
            actual_duration_minutes=150
        )
        completed_by = uuid.uuid4()
        
        completed_item = await itinerary_service.complete_item(
            test_item.id, completion_data, completed_by
        )
        
        assert completed_item.is_completed is True
        assert completed_item.completed_at is not None
        assert completed_item.completed_by == completed_by
        assert completed_item.duration_minutes == 150
        assert "Activity completed successfully" in completed_item.notes
    
    @pytest.mark.asyncio
    async def test_cannot_complete_cancelled_item(self, session, redis_client, create_test_tour_template, create_test_tour_instance, create_test_itinerary_item):
        """Test that cancelled items cannot be completed"""
        itinerary_service = ItineraryService(session, redis_client)
        
        # Create template and instance
        test_template = create_test_tour_template()
        test_instance = create_test_tour_instance(test_template.id)
        
        # Create cancelled itinerary item
        test_item = create_test_itinerary_item(
            test_instance.id,
            is_cancelled=True
        )
        
        # Try to complete cancelled item
        completion_data = ItineraryItemCompletion(notes="Trying to complete")
        completed_by = uuid.uuid4()
        
        with pytest.raises(Exception) as exc_info:
            await itinerary_service.complete_item(test_item.id, completion_data, completed_by)
        
        assert "Cannot complete cancelled" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_reorder_items(self, session, redis_client, create_test_tour_template, create_test_tour_instance, create_test_itinerary_item):
        """Test reordering itinerary items for a day"""
        itinerary_service = ItineraryService(session, redis_client)
        
        # Create template and instance
        test_template = create_test_tour_template()
        test_instance = create_test_tour_instance(test_template.id)
        
        # Create items for day 1
        item1 = create_test_itinerary_item(
            test_instance.id,
            day_number=1,
            title="First Activity",
            start_time=time(9, 0)
        )
        item2 = create_test_itinerary_item(
            test_instance.id,
            day_number=1,
            title="Second Activity",
            start_time=time(11, 0)
        )
        item3 = create_test_itinerary_item(
            test_instance.id,
            day_number=1,
            title="Third Activity",
            start_time=time(14, 0)
        )
        
        # Reorder items (reverse order)
        new_order = [item3.id, item1.id, item2.id]
        
        reordered_items = await itinerary_service.reorder_items(
            test_instance.id, 1, new_order
        )
        
        assert len(reordered_items) == 3
        # Items should be in new order based on updated start times
        assert reordered_items[0].title == "Third Activity"
        assert reordered_items[1].title == "First Activity"
        assert reordered_items[2].title == "Second Activity"
    
    @pytest.mark.asyncio
    async def test_update_item(self, session, redis_client, create_test_tour_template, create_test_tour_instance, create_test_itinerary_item):
        """Test updating an itinerary item"""
        from schemas.itinerary_item import ItineraryItemUpdate
        
        itinerary_service = ItineraryService(session, redis_client)
        
        # Create template and instance
        test_template = create_test_tour_template()
        test_instance = create_test_tour_instance(test_template.id)
        
        # Create itinerary item
        test_item = create_test_itinerary_item(
            test_instance.id,
            title="Original Title",
            location_name="Original Location"
        )
        
        # Update item
        update_data = ItineraryItemUpdate(
            title="Updated Title",
            location_name="Updated Location",
            coordinates=(32.0, -8.0),
            notes="Updated notes"
        )
        
        updated_item = await itinerary_service.update_item(test_item.id, update_data)
        
        assert updated_item.title == "Updated Title"
        assert updated_item.location_name == "Updated Location"
        assert updated_item.coordinates == (32.0, -8.0)
        assert updated_item.notes == "Updated notes"
        assert updated_item.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_delete_item(self, session, redis_client, create_test_tour_template, create_test_tour_instance, create_test_itinerary_item):
        """Test deleting an itinerary item"""
        itinerary_service = ItineraryService(session, redis_client)
        
        # Create template and instance
        test_template = create_test_tour_template()
        test_instance = create_test_tour_instance(test_template.id)
        
        # Create itinerary item
        test_item = create_test_itinerary_item(test_instance.id)
        
        # Delete item
        result = await itinerary_service.delete_item(test_item.id)
        
        assert "deleted successfully" in result["message"]
        
        # Verify item is deleted
        with pytest.raises(Exception) as exc_info:
            await itinerary_service.get_item(test_item.id)
        
        assert "not found" in str(exc_info.value)