"""
Tests for tour instance functionality
"""
import pytest
from services.tour_instance_service import TourInstanceService
from schemas.tour_instance import TourInstanceCreate, TourAssignment, TourStatusUpdate
from models.tour_instance import TourStatus
from datetime import date, timedelta
import uuid


class TestTourInstances:
    """Test class for tour instance operations"""
    
    @pytest.mark.asyncio
    async def test_create_tour_instance(self, session, redis_client, create_test_tour_template, sample_tour_instance_data):
        """Test creating a new tour instance"""
        instance_service = TourInstanceService(session, redis_client)
        
        # Mock external service calls
        instance_service._verify_booking_exists = lambda x: True
        instance_service._verify_customer_exists = lambda x: True
        
        # Create template
        test_template = create_test_tour_template(
            min_participants=2,
            max_participants=10
        )
        
        # Create instance
        instance_data = TourInstanceCreate(
            template_id=test_template.id,
            booking_id=uuid.uuid4(),
            customer_id=uuid.uuid4(),
            **sample_tour_instance_data
        )
        
        instance = await instance_service.create_instance(instance_data)
        
        assert instance.template_id == test_template.id
        assert instance.title == sample_tour_instance_data["title"]
        assert instance.participant_count == 4
        assert instance.status == TourStatus.PLANNED
        assert instance.language == "French"
    
    @pytest.mark.asyncio
    async def test_create_instance_invalid_participant_count(self, session, redis_client, create_test_tour_template):
        """Test creating instance with invalid participant count"""
        instance_service = TourInstanceService(session, redis_client)
        
        # Mock external service calls
        instance_service._verify_booking_exists = lambda x: True
        instance_service._verify_customer_exists = lambda x: True
        
        # Create template with strict limits
        test_template = create_test_tour_template(
            min_participants=5,
            max_participants=10
        )
        
        # Try to create instance with too few participants
        instance_data = TourInstanceCreate(
            template_id=test_template.id,
            booking_id=uuid.uuid4(),
            customer_id=uuid.uuid4(),
            title="Test Tour",
            start_date=date.today() + timedelta(days=7),
            end_date=date.today() + timedelta(days=9),
            participant_count=3,  # Below minimum
            lead_passenger_name="Test Customer"
        )
        
        with pytest.raises(Exception) as exc_info:
            await instance_service.create_instance(instance_data)
        
        assert "between 5 and 10" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_assign_resources(self, session, redis_client, create_test_tour_template, create_test_tour_instance):
        """Test assigning resources to tour instance"""
        instance_service = TourInstanceService(session, redis_client)
        
        # Create template and instance
        test_template = create_test_tour_template()
        test_instance = create_test_tour_instance(test_template.id)
        
        # Assign resources
        assignment = TourAssignment(
            guide_id=uuid.uuid4(),
            vehicle_id=uuid.uuid4(),
            driver_id=uuid.uuid4(),
            notes="Resources assigned for March tour"
        )
        
        updated_instance = await instance_service.assign_resources(
            test_instance.id, assignment
        )
        
        assert updated_instance.assigned_guide_id == assignment.guide_id
        assert updated_instance.assigned_vehicle_id == assignment.vehicle_id
        assert updated_instance.assigned_driver_id == assignment.driver_id
        assert "Resources assigned" in updated_instance.internal_notes
    
    @pytest.mark.asyncio
    async def test_update_status(self, session, redis_client, create_test_tour_template, create_test_tour_instance):
        """Test updating tour instance status"""
        instance_service = TourInstanceService(session, redis_client)
        
        # Create template and instance
        test_template = create_test_tour_template()
        test_instance = create_test_tour_instance(
            test_template.id,
            status=TourStatus.PLANNED
        )
        
        # Update status to confirmed
        status_update = TourStatusUpdate(
            status=TourStatus.CONFIRMED,
            notes="Tour confirmed by customer"
        )
        
        updated_instance = await instance_service.update_status(
            test_instance.id, status_update
        )
        
        assert updated_instance.status == TourStatus.CONFIRMED
        assert updated_instance.confirmed_at is not None
        assert "Tour confirmed" in updated_instance.internal_notes
    
    @pytest.mark.asyncio
    async def test_invalid_status_transition(self, session, redis_client, create_test_tour_template, create_test_tour_instance):
        """Test invalid status transition"""
        instance_service = TourInstanceService(session, redis_client)
        
        # Create completed tour instance
        test_template = create_test_tour_template()
        test_instance = create_test_tour_instance(
            test_template.id,
            status=TourStatus.COMPLETED
        )
        
        # Try to change status from completed to in progress (invalid)
        status_update = TourStatusUpdate(
            status=TourStatus.IN_PROGRESS,
            notes="Invalid transition"
        )
        
        with pytest.raises(Exception) as exc_info:
            await instance_service.update_status(test_instance.id, status_update)
        
        assert "Invalid status transition" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_update_progress(self, session, redis_client, create_test_tour_template, create_test_tour_instance):
        """Test updating tour progress"""
        from schemas.tour_instance import TourProgressUpdate
        
        instance_service = TourInstanceService(session, redis_client)
        
        # Create template and instance
        test_template = create_test_tour_template(duration_days=5)
        test_instance = create_test_tour_instance(
            test_template.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=4)  # 5 days total
        )
        
        # Update progress
        progress_update = TourProgressUpdate(
            current_day=3,
            completion_percentage=60.0,
            notes="Halfway through the tour"
        )
        
        updated_instance = await instance_service.update_progress(
            test_instance.id, progress_update
        )
        
        assert updated_instance.current_day == 3
        assert updated_instance.completion_percentage == 60.0
        assert "Halfway through" in updated_instance.internal_notes
    
    @pytest.mark.asyncio
    async def test_get_instance_summary(self, session, redis_client, create_test_tour_template, create_test_tour_instance, create_test_itinerary_item, create_test_incident):
        """Test getting comprehensive tour instance summary"""
        instance_service = TourInstanceService(session, redis_client)
        
        # Mock customer info retrieval
        instance_service._get_customer_info = lambda x: {
            "full_name": "Test Customer",
            "email": "test@example.com"
        }
        
        # Create template and instance
        test_template = create_test_tour_template()
        test_instance = create_test_tour_instance(test_template.id)
        
        # Create itinerary items
        create_test_itinerary_item(test_instance.id, title="Activity 1", is_completed=True)
        create_test_itinerary_item(test_instance.id, title="Activity 2", is_completed=False)
        
        # Create incidents
        create_test_incident(test_instance.id, title="Minor delay", is_resolved=True)
        create_test_incident(test_instance.id, title="Weather issue", is_resolved=False)
        
        # Get summary
        summary = await instance_service.get_instance_summary(test_instance.id)
        
        assert summary.id == test_instance.id
        assert summary.itinerary_items_count == 2
        assert summary.completed_items_count == 1
        assert summary.incidents_count == 2
        assert summary.unresolved_incidents_count == 1
        assert summary.customer_name == "Test Customer"
        assert summary.template_title == test_template.title
    
    @pytest.mark.asyncio
    async def test_get_active_tours(self, session, redis_client, create_test_tour_template, create_test_tour_instance):
        """Test getting active tours"""
        instance_service = TourInstanceService(session, redis_client)
        
        # Create template
        test_template = create_test_tour_template()
        
        # Create tours with different statuses
        confirmed_tour = create_test_tour_instance(
            test_template.id,
            title="Confirmed Tour",
            status=TourStatus.CONFIRMED
        )
        in_progress_tour = create_test_tour_instance(
            test_template.id,
            title="In Progress Tour",
            status=TourStatus.IN_PROGRESS
        )
        completed_tour = create_test_tour_instance(
            test_template.id,
            title="Completed Tour",
            status=TourStatus.COMPLETED
        )
        
        # Get active tours
        active_tours = await instance_service.get_active_tours()
        
        assert len(active_tours) == 2
        active_titles = [tour.title for tour in active_tours]
        assert "Confirmed Tour" in active_titles
        assert "In Progress Tour" in active_titles
        assert "Completed Tour" not in active_titles
    
    @pytest.mark.asyncio
    async def test_cannot_modify_completed_tour(self, session, redis_client, create_test_tour_template, create_test_tour_instance):
        """Test that completed tours cannot be modified"""
        from schemas.tour_instance import TourInstanceUpdate
        
        instance_service = TourInstanceService(session, redis_client)
        
        # Create completed tour
        test_template = create_test_tour_template()
        test_instance = create_test_tour_instance(
            test_template.id,
            status=TourStatus.COMPLETED
        )
        
        # Try to update completed tour
        update_data = TourInstanceUpdate(
            title="Updated Title",
            participant_count=6
        )
        
        with pytest.raises(Exception) as exc_info:
            await instance_service.update_instance(test_instance.id, update_data)
        
        assert "Cannot modify" in str(exc_info.value)