"""
Tests for assignment functionality
"""
import pytest
from services.assignment_service import AssignmentService
from schemas.assignment import AssignmentCreate
from models.assignment import AssignmentStatus
from models.vehicle import VehicleStatus
from datetime import date, timedelta
import uuid


class TestAssignments:
    """Test class for assignment operations"""
    
    @pytest.mark.asyncio
    async def test_create_assignment(self, session, redis_client, create_test_vehicle, sample_assignment_data):
        """Test creating a new assignment"""
        assignment_service = AssignmentService(session, redis_client)
        
        # Mock tour instance verification
        assignment_service._verify_tour_instance_exists = lambda x: True
        
        # Create test vehicle
        test_vehicle = create_test_vehicle(status=VehicleStatus.AVAILABLE)
        
        # Create assignment
        assignment_data = AssignmentCreate(
            vehicle_id=test_vehicle.id,
            **sample_assignment_data
        )
        
        assignment = await assignment_service.create_assignment(assignment_data)
        
        assert assignment.vehicle_id == test_vehicle.id
        assert assignment.status == AssignmentStatus.SCHEDULED
        assert assignment.pickup_location == "Marrakech Hotel"
        assert assignment.dropoff_location == "Merzouga Desert Camp"
        assert assignment.estimated_distance == 560
    
    @pytest.mark.asyncio
    async def test_create_assignment_with_conflicts(self, session, redis_client, create_test_vehicle, create_test_assignment):
        """Test creating assignment with date conflicts"""
        assignment_service = AssignmentService(session, redis_client)
        
        # Mock tour instance verification
        assignment_service._verify_tour_instance_exists = lambda x: True
        
        # Create test vehicle
        test_vehicle = create_test_vehicle()
        
        # Create existing assignment
        create_test_assignment(
            test_vehicle.id,
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=7)
        )
        
        # Try to create conflicting assignment
        conflicting_assignment = AssignmentCreate(
            vehicle_id=test_vehicle.id,
            tour_instance_id=uuid.uuid4(),
            start_date=date.today() + timedelta(days=6),  # Overlaps with existing
            end_date=date.today() + timedelta(days=8)
        )
        
        with pytest.raises(Exception) as exc_info:
            await assignment_service.create_assignment(conflicting_assignment)
        
        assert "conflicting assignments" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_start_assignment(self, session, redis_client, create_test_vehicle, create_test_assignment):
        """Test starting an assignment"""
        from sqlmodel import select
        from models.vehicle import Vehicle
        
        assignment_service = AssignmentService(session, redis_client)
        
        # Create test vehicle and assignment
        test_vehicle = create_test_vehicle(status=VehicleStatus.AVAILABLE)
        test_assignment = create_test_assignment(
            test_vehicle.id,
            status=AssignmentStatus.SCHEDULED
        )
        
        # Start assignment
        started_assignment = await assignment_service.start_assignment(
            test_assignment.id, start_odometer=15000
        )
        
        assert started_assignment.status == AssignmentStatus.ACTIVE
        assert started_assignment.start_odometer == 15000
        assert started_assignment.actual_start_date is not None
        
        # Check that vehicle status was updated
        updated_vehicle = session.exec(select(Vehicle).where(Vehicle.id == test_vehicle.id)).first()
        assert updated_vehicle.status == VehicleStatus.IN_USE
        assert updated_vehicle.current_odometer == 15000
    
    @pytest.mark.asyncio
    async def test_complete_assignment(self, session, redis_client, create_test_vehicle, create_test_assignment):
        """Test completing an assignment"""
        from sqlmodel import select
        from models.vehicle import Vehicle
        
        assignment_service = AssignmentService(session, redis_client)
        
        # Create test vehicle and active assignment
        test_vehicle = create_test_vehicle(status=VehicleStatus.IN_USE)
        test_assignment = create_test_assignment(
            test_vehicle.id,
            status=AssignmentStatus.ACTIVE,
            start_odometer=15000
        )
        
        # Complete assignment
        completed_assignment = await assignment_service.complete_assignment(
            test_assignment.id, end_odometer=15500
        )
        
        assert completed_assignment.status == AssignmentStatus.COMPLETED
        assert completed_assignment.end_odometer == 15500
        assert completed_assignment.actual_end_date is not None
        assert completed_assignment.distance_traveled == 500  # 15500 - 15000
        
        # Check that vehicle status was updated
        updated_vehicle = session.exec(select(Vehicle).where(Vehicle.id == test_vehicle.id)).first()
        assert updated_vehicle.status == VehicleStatus.AVAILABLE
        assert updated_vehicle.current_odometer == 15500
    
    @pytest.mark.asyncio
    async def test_cancel_assignment(self, session, redis_client, create_test_vehicle, create_test_assignment):
        """Test cancelling an assignment"""
        assignment_service = AssignmentService(session, redis_client)
        
        # Create test vehicle and assignment
        test_vehicle = create_test_vehicle()
        test_assignment = create_test_assignment(
            test_vehicle.id,
            status=AssignmentStatus.SCHEDULED
        )
        
        # Cancel assignment
        cancelled_assignment = await assignment_service.cancel_assignment(
            test_assignment.id, "Customer cancelled tour"
        )
        
        assert cancelled_assignment.status == AssignmentStatus.CANCELLED
        assert "Customer cancelled tour" in cancelled_assignment.notes
        assert cancelled_assignment.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_cannot_complete_assignment_with_invalid_odometer(self, session, redis_client, create_test_vehicle, create_test_assignment):
        """Test that assignment cannot be completed with invalid odometer reading"""
        assignment_service = AssignmentService(session, redis_client)
        
        # Create test vehicle and active assignment
        test_vehicle = create_test_vehicle()
        test_assignment = create_test_assignment(
            test_vehicle.id,
            status=AssignmentStatus.ACTIVE,
            start_odometer=15000
        )
        
        # Try to complete with lower odometer reading
        with pytest.raises(Exception) as exc_info:
            await assignment_service.complete_assignment(
                test_assignment.id, end_odometer=14500  # Lower than start
            )
        
        assert "cannot be less than start reading" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_vehicle_assignments(self, session, redis_client, create_test_vehicle, create_test_assignment):
        """Test getting all assignments for a vehicle"""
        from utils.pagination import PaginationParams
        
        assignment_service = AssignmentService(session, redis_client)
        
        # Create test vehicle
        test_vehicle = create_test_vehicle()
        
        # Create multiple assignments
        create_test_assignment(
            test_vehicle.id,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=3)
        )
        create_test_assignment(
            test_vehicle.id,
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=7)
        )
        
        # Get vehicle assignments
        pagination = PaginationParams(page=1, size=10)
        assignments, total = await assignment_service.get_vehicle_assignments(
            test_vehicle.id, pagination
        )
        
        assert total == 2
        assert len(assignments) == 2
        assert all(assignment.vehicle_id == test_vehicle.id for assignment in assignments)
    
    @pytest.mark.asyncio
    async def test_assignment_conflict_detection(self, session, redis_client, create_test_vehicle):
        """Test assignment conflict detection"""
        assignment_service = AssignmentService(session, redis_client)
        
        # Create test vehicle
        test_vehicle = create_test_vehicle()
        
        # Test various conflict scenarios
        start_date = date.today() + timedelta(days=5)
        end_date = date.today() + timedelta(days=7)
        
        # Check conflicts (should be empty initially)
        conflicts = await assignment_service._check_assignment_conflicts(
            test_vehicle.id, start_date, end_date
        )
        assert len(conflicts) == 0
        
        # Create assignment
        existing_assignment = create_test_assignment(
            test_vehicle.id,
            start_date=start_date,
            end_date=end_date,
            status=AssignmentStatus.SCHEDULED
        )
        
        # Test exact overlap
        conflicts = await assignment_service._check_assignment_conflicts(
            test_vehicle.id, start_date, end_date
        )
        assert len(conflicts) == 1
        assert conflicts[0].conflicting_assignment_id == existing_assignment.id
        
        # Test partial overlap (start before, end during)
        conflicts = await assignment_service._check_assignment_conflicts(
            test_vehicle.id, 
            start_date - timedelta(days=1), 
            start_date + timedelta(days=1)
        )
        assert len(conflicts) == 1
        
        # Test no overlap (completely before)
        conflicts = await assignment_service._check_assignment_conflicts(
            test_vehicle.id, 
            start_date - timedelta(days=5), 
            start_date - timedelta(days=3)
        )
        assert len(conflicts) == 0
        
        # Test no overlap (completely after)
        conflicts = await assignment_service._check_assignment_conflicts(
            test_vehicle.id, 
            end_date + timedelta(days=1), 
            end_date + timedelta(days=3)
        )
        assert len(conflicts) == 0