"""
Tests for maintenance functionality
"""
import pytest
from services.maintenance_service import MaintenanceService
from schemas.maintenance_record import MaintenanceRecordCreate
from models.maintenance_record import MaintenanceType
from datetime import date, timedelta


class TestMaintenance:
    """Test class for maintenance operations"""
    
    @pytest.mark.asyncio
    async def test_create_maintenance_record(self, session, redis_client, create_test_vehicle, sample_maintenance_data):
        """Test creating a new maintenance record"""
        maintenance_service = MaintenanceService(session, redis_client)
        
        # Create test vehicle
        test_vehicle = create_test_vehicle(current_odometer=14000)
        
        # Create maintenance record
        maintenance_data = MaintenanceRecordCreate(
            vehicle_id=test_vehicle.id,
            **sample_maintenance_data
        )
        
        record = await maintenance_service.create_maintenance_record(maintenance_data)
        
        assert record.vehicle_id == test_vehicle.id
        assert record.maintenance_type == MaintenanceType.PREVENTIVE
        assert record.description == sample_maintenance_data["description"]
        assert record.cost == 350.0
        assert record.labor_hours == 2.0
        assert record.is_completed is True
    
    @pytest.mark.asyncio
    async def test_create_maintenance_updates_vehicle_odometer(self, session, redis_client, create_test_vehicle):
        """Test that maintenance record updates vehicle odometer"""
        from sqlmodel import select
        from models.vehicle import Vehicle
        
        maintenance_service = MaintenanceService(session, redis_client)
        
        # Create test vehicle with lower odometer
        test_vehicle = create_test_vehicle(current_odometer=14000)
        
        # Create maintenance record with higher odometer
        maintenance_data = MaintenanceRecordCreate(
            vehicle_id=test_vehicle.id,
            maintenance_type=MaintenanceType.PREVENTIVE,
            description="Test maintenance",
            date_performed=date.today(),
            odometer_reading=15500  # Higher than vehicle's current odometer
        )
        
        await maintenance_service.create_maintenance_record(maintenance_data)
        
        # Check that vehicle odometer was updated
        updated_vehicle = session.exec(select(Vehicle).where(Vehicle.id == test_vehicle.id)).first()
        assert updated_vehicle.current_odometer == 15500
    
    @pytest.mark.asyncio
    async def test_get_vehicle_maintenance_history(self, session, redis_client, create_test_vehicle, create_test_maintenance_record):
        """Test getting maintenance history for a vehicle"""
        from utils.pagination import PaginationParams
        
        maintenance_service = MaintenanceService(session, redis_client)
        
        # Create test vehicle
        test_vehicle = create_test_vehicle()
        
        # Create multiple maintenance records
        create_test_maintenance_record(
            test_vehicle.id,
            maintenance_type=MaintenanceType.PREVENTIVE,
            description="Oil change"
        )
        create_test_maintenance_record(
            test_vehicle.id,
            maintenance_type=MaintenanceType.CORRECTIVE,
            description="Brake repair"
        )
        
        # Get maintenance history
        pagination = PaginationParams(page=1, size=10)
        records, total = await maintenance_service.get_vehicle_maintenance_history(
            test_vehicle.id, pagination
        )
        
        assert total == 2
        assert len(records) == 2
        assert all(record.vehicle_id == test_vehicle.id for record in records)
    
    @pytest.mark.asyncio
    async def test_get_upcoming_maintenance(self, session, redis_client, create_test_vehicle, create_test_maintenance_record):
        """Test getting vehicles with upcoming maintenance"""
        maintenance_service = MaintenanceService(session, redis_client)
        
        # Create test vehicle
        test_vehicle = create_test_vehicle(license_plate="UPCOMING-001")
        
        # Create maintenance record with upcoming service
        create_test_maintenance_record(
            test_vehicle.id,
            next_service_date=date.today() + timedelta(days=15),
            is_completed=True
        )
        
        # Get upcoming maintenance
        upcoming = await maintenance_service.get_upcoming_maintenance(days_ahead=30)
        
        assert len(upcoming) == 1
        assert upcoming[0]["vehicle_id"] == str(test_vehicle.id)
        assert upcoming[0]["license_plate"] == "UPCOMING-001"
        assert upcoming[0]["days_until_service"] == 15
    
    @pytest.mark.asyncio
    async def test_get_maintenance_stats(self, session, redis_client, create_test_vehicle, create_test_maintenance_record):
        """Test getting maintenance statistics"""
        maintenance_service = MaintenanceService(session, redis_client)
        
        # Create test vehicle
        test_vehicle = create_test_vehicle()
        
        # Create maintenance records with different types and costs
        create_test_maintenance_record(
            test_vehicle.id,
            maintenance_type=MaintenanceType.PREVENTIVE,
            cost=300.0,
            date_performed=date.today() - timedelta(days=30)
        )
        create_test_maintenance_record(
            test_vehicle.id,
            maintenance_type=MaintenanceType.CORRECTIVE,
            cost=500.0,
            date_performed=date.today() - timedelta(days=15)
        )
        create_test_maintenance_record(
            test_vehicle.id,
            maintenance_type=MaintenanceType.PREVENTIVE,
            cost=200.0,
            date_performed=date.today() - timedelta(days=5)
        )
        
        # Get statistics
        stats = await maintenance_service.get_maintenance_stats(days=365)
        
        assert stats.total_records == 3
        assert stats.total_cost == 1000.0
        assert stats.average_cost == 1000.0 / 3
        assert stats.by_type["Preventive"]["count"] == 2
        assert stats.by_type["Corrective"]["count"] == 1
        assert stats.preventive_percentage == (2 / 3) * 100
    
    @pytest.mark.asyncio
    async def test_update_maintenance_record(self, session, redis_client, create_test_vehicle, create_test_maintenance_record):
        """Test updating maintenance record"""
        from schemas.maintenance_record import MaintenanceRecordUpdate
        
        maintenance_service = MaintenanceService(session, redis_client)
        
        # Create test vehicle and maintenance record
        test_vehicle = create_test_vehicle()
        test_record = create_test_maintenance_record(
            test_vehicle.id,
            description="Original description",
            cost=100.0
        )
        
        # Update maintenance record
        update_data = MaintenanceRecordUpdate(
            description="Updated description",
            cost=150.0,
            is_completed=True
        )
        
        updated_record = await maintenance_service.update_maintenance_record(
            test_record.id, update_data
        )
        
        assert updated_record.description == "Updated description"
        assert updated_record.cost == 150.0
        assert updated_record.is_completed is True
        assert updated_record.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_delete_maintenance_record(self, session, redis_client, create_test_vehicle, create_test_maintenance_record):
        """Test deleting maintenance record"""
        maintenance_service = MaintenanceService(session, redis_client)
        
        # Create test vehicle and maintenance record
        test_vehicle = create_test_vehicle()
        test_record = create_test_maintenance_record(test_vehicle.id)
        
        # Delete maintenance record
        result = await maintenance_service.delete_maintenance_record(test_record.id)
        
        assert "deleted successfully" in result["message"]
        
        # Verify record is deleted
        with pytest.raises(Exception) as exc_info:
            await maintenance_service.get_maintenance_record(test_record.id)
        
        assert "not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_warranty_calculation(self, session, redis_client, create_test_vehicle):
        """Test warranty calculation for maintenance records"""
        maintenance_service = MaintenanceService(session, redis_client)
        
        # Create test vehicle
        test_vehicle = create_test_vehicle()
        
        # Create maintenance record with future warranty
        maintenance_data = MaintenanceRecordCreate(
            vehicle_id=test_vehicle.id,
            maintenance_type=MaintenanceType.CORRECTIVE,
            description="Brake replacement",
            date_performed=date.today(),
            cost=800.0,
            warranty_until=date.today() + timedelta(days=365)  # 1 year warranty
        )
        
        record = await maintenance_service.create_maintenance_record(maintenance_data)
        
        assert record.is_under_warranty is True
        
        # Create maintenance record with expired warranty
        expired_warranty_data = MaintenanceRecordCreate(
            vehicle_id=test_vehicle.id,
            maintenance_type=MaintenanceType.CORRECTIVE,
            description="Old repair",
            date_performed=date.today() - timedelta(days=400),
            cost=500.0,
            warranty_until=date.today() - timedelta(days=30)  # Expired warranty
        )
        
        expired_record = await maintenance_service.create_maintenance_record(expired_warranty_data)
        
        assert expired_record.is_under_warranty is False