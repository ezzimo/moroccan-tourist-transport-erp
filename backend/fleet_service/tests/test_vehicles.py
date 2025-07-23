"""
Tests for vehicle functionality
"""
import pytest
from services.vehicle_service import VehicleService
from schemas.vehicle import VehicleCreate
from models.vehicle import VehicleType, VehicleStatus, FuelType


class TestVehicles:
    """Test class for vehicle operations"""
    
    @pytest.mark.asyncio
    async def test_create_vehicle(self, session, redis_client, sample_vehicle_data):
        """Test creating a new vehicle"""
        vehicle_service = VehicleService(session, redis_client)
        
        vehicle_create = VehicleCreate(**sample_vehicle_data)
        vehicle = await vehicle_service.create_vehicle(vehicle_create)
        
        assert vehicle.license_plate == sample_vehicle_data["license_plate"]
        assert vehicle.vehicle_type == VehicleType.BUS
        assert vehicle.brand == "Mercedes"
        assert vehicle.model == "Sprinter"
        assert vehicle.seating_capacity == 16
        assert vehicle.status == VehicleStatus.AVAILABLE
        assert vehicle.is_active is True
    
    @pytest.mark.asyncio
    async def test_create_vehicle_duplicate_license_plate(self, session, redis_client, sample_vehicle_data):
        """Test creating vehicle with duplicate license plate"""
        vehicle_service = VehicleService(session, redis_client)
        
        vehicle_create = VehicleCreate(**sample_vehicle_data)
        
        # Create first vehicle
        await vehicle_service.create_vehicle(vehicle_create)
        
        # Try to create second vehicle with same license plate
        with pytest.raises(Exception) as exc_info:
            await vehicle_service.create_vehicle(vehicle_create)
        
        assert "already exists" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_vehicle(self, session, redis_client, create_test_vehicle):
        """Test getting vehicle by ID"""
        vehicle_service = VehicleService(session, redis_client)
        
        # Create test vehicle
        test_vehicle = create_test_vehicle(
            license_plate="TEST-001",
            brand="Toyota",
            model="Hiace"
        )
        
        # Get vehicle
        retrieved_vehicle = await vehicle_service.get_vehicle(test_vehicle.id)
        
        assert retrieved_vehicle.id == test_vehicle.id
        assert retrieved_vehicle.license_plate == "TEST-001"
        assert retrieved_vehicle.brand == "Toyota"
        assert retrieved_vehicle.model == "Hiace"
    
    @pytest.mark.asyncio
    async def test_update_vehicle(self, session, redis_client, create_test_vehicle):
        """Test updating vehicle information"""
        from schemas.vehicle import VehicleUpdate
        
        vehicle_service = VehicleService(session, redis_client)
        
        # Create test vehicle
        test_vehicle = create_test_vehicle()
        
        # Update vehicle
        update_data = VehicleUpdate(
            brand="Updated Brand",
            model="Updated Model",
            status=VehicleStatus.MAINTENANCE,
            current_odometer=15000
        )
        
        updated_vehicle = await vehicle_service.update_vehicle(test_vehicle.id, update_data)
        
        assert updated_vehicle.brand == "Updated Brand"
        assert updated_vehicle.model == "Updated Model"
        assert updated_vehicle.status == VehicleStatus.MAINTENANCE
        assert updated_vehicle.current_odometer == 15000
        assert updated_vehicle.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_check_availability(self, session, redis_client, create_test_vehicle, create_test_assignment):
        """Test checking vehicle availability"""
        from datetime import date, timedelta
        
        vehicle_service = VehicleService(session, redis_client)
        
        # Create test vehicle
        test_vehicle = create_test_vehicle(status=VehicleStatus.AVAILABLE)
        
        # Test availability without conflicts
        start_date = date.today() + timedelta(days=10)
        end_date = date.today() + timedelta(days=12)
        
        availability = await vehicle_service.check_availability(
            test_vehicle.id, start_date, end_date
        )
        
        assert availability.is_available is True
        assert len(availability.conflicting_assignments) == 0
        
        # Create conflicting assignment
        create_test_assignment(
            test_vehicle.id,
            start_date=date.today() + timedelta(days=11),
            end_date=date.today() + timedelta(days=13)
        )
        
        # Test availability with conflicts
        availability = await vehicle_service.check_availability(
            test_vehicle.id, start_date, end_date
        )
        
        assert availability.is_available is False
        assert len(availability.conflicting_assignments) == 1
    
    @pytest.mark.asyncio
    async def test_get_vehicle_summary(self, session, redis_client, create_test_vehicle, create_test_maintenance_record, create_test_assignment, create_test_fuel_log):
        """Test getting comprehensive vehicle summary"""
        vehicle_service = VehicleService(session, redis_client)
        
        # Create test vehicle
        test_vehicle = create_test_vehicle()
        
        # Create related records
        create_test_maintenance_record(test_vehicle.id, cost=500.0)
        create_test_maintenance_record(test_vehicle.id, cost=300.0)
        create_test_assignment(test_vehicle.id)
        create_test_fuel_log(test_vehicle.id, fuel_efficiency=12.5)
        create_test_fuel_log(test_vehicle.id, fuel_efficiency=11.8)
        
        # Get summary
        summary = await vehicle_service.get_vehicle_summary(test_vehicle.id)
        
        assert summary.id == test_vehicle.id
        assert summary.total_assignments == 1
        assert summary.total_maintenance_records == 2
        assert summary.total_maintenance_cost == 800.0
        assert summary.average_fuel_efficiency == 12.15  # (12.5 + 11.8) / 2
    
    @pytest.mark.asyncio
    async def test_get_available_vehicles(self, session, redis_client, create_test_vehicle):
        """Test getting available vehicles for a period"""
        from datetime import date, timedelta
        
        vehicle_service = VehicleService(session, redis_client)
        
        # Create available vehicle
        available_vehicle = create_test_vehicle(
            license_plate="AVAILABLE-001",
            status=VehicleStatus.AVAILABLE,
            vehicle_type=VehicleType.BUS,
            seating_capacity=20
        )
        
        # Create unavailable vehicle
        unavailable_vehicle = create_test_vehicle(
            license_plate="UNAVAILABLE-001",
            status=VehicleStatus.MAINTENANCE
        )
        
        # Get available vehicles
        start_date = date.today() + timedelta(days=1)
        end_date = date.today() + timedelta(days=3)
        
        available_vehicles = await vehicle_service.get_available_vehicles(
            start_date, end_date, VehicleType.BUS.value, 15
        )
        
        assert len(available_vehicles) == 1
        assert available_vehicles[0].id == available_vehicle.id
        assert available_vehicles[0].license_plate == "AVAILABLE-001"
    
    @pytest.mark.asyncio
    async def test_compliance_status(self, session, redis_client, create_test_vehicle):
        """Test vehicle compliance status checking"""
        from datetime import date, timedelta
        
        vehicle_service = VehicleService(session, redis_client)
        
        # Create vehicle with expiring documents
        test_vehicle = create_test_vehicle(
            insurance_expiry=date.today() + timedelta(days=15),  # Expires soon
            registration_expiry=date.today() + timedelta(days=60),  # OK
            inspection_expiry=date.today() - timedelta(days=5)  # Expired
        )
        
        # Get vehicle with compliance status
        vehicle_response = await vehicle_service.get_vehicle(test_vehicle.id)
        
        compliance_status = vehicle_response.compliance_status
        
        # Insurance should need attention (expires in 15 days)
        assert compliance_status["insurance"]["needs_attention"] is True
        assert compliance_status["insurance"]["days_until_expiry"] == 15
        
        # Registration should be OK (expires in 60 days)
        assert compliance_status["registration"]["needs_attention"] is False
        
        # Inspection should be expired
        assert compliance_status["inspection"]["is_expired"] is True
        assert compliance_status["inspection"]["days_until_expiry"] == -5
    
    @pytest.mark.asyncio
    async def test_delete_vehicle_with_active_assignments(self, session, redis_client, create_test_vehicle, create_test_assignment):
        """Test that vehicles with active assignments cannot be deleted"""
        vehicle_service = VehicleService(session, redis_client)
        
        # Create vehicle with active assignment
        test_vehicle = create_test_vehicle()
        create_test_assignment(
            test_vehicle.id,
            status=AssignmentStatus.ACTIVE
        )
        
        # Try to delete vehicle
        with pytest.raises(Exception) as exc_info:
            await vehicle_service.delete_vehicle(test_vehicle.id)
        
        assert "active assignments" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_delete_vehicle_without_active_assignments(self, session, redis_client, create_test_vehicle):
        """Test deleting vehicle without active assignments"""
        vehicle_service = VehicleService(session, redis_client)
        
        # Create vehicle without active assignments
        test_vehicle = create_test_vehicle()
        
        # Delete vehicle
        result = await vehicle_service.delete_vehicle(test_vehicle.id)
        
        assert "deactivated successfully" in result["message"]
        
        # Verify vehicle is deactivated
        updated_vehicle = await vehicle_service.get_vehicle(test_vehicle.id)
        assert updated_vehicle.is_active is False
        assert updated_vehicle.status == VehicleStatus.RETIRED