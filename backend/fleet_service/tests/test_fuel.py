"""
Tests for fuel functionality
"""
import pytest
from services.fuel_service import FuelService
from schemas.fuel_log import FuelLogCreate
from datetime import date, timedelta


class TestFuel:
    """Test class for fuel operations"""
    
    @pytest.mark.asyncio
    async def test_create_fuel_log(self, session, create_test_vehicle, sample_fuel_log_data):
        """Test creating a new fuel log"""
        fuel_service = FuelService(session)
        
        # Create test vehicle
        test_vehicle = create_test_vehicle(current_odometer=15000)
        
        # Create fuel log
        fuel_log_data = FuelLogCreate(
            vehicle_id=test_vehicle.id,
            **sample_fuel_log_data
        )
        
        fuel_log = await fuel_service.create_fuel_log(fuel_log_data)
        
        assert fuel_log.vehicle_id == test_vehicle.id
        assert fuel_log.fuel_amount == 65.0
        assert fuel_log.fuel_cost == 845.0
        assert fuel_log.price_per_liter == 13.0
        assert fuel_log.station_name == "Total Marrakech"
        assert fuel_log.is_full_tank is True
    
    @pytest.mark.asyncio
    async def test_fuel_efficiency_calculation(self, session, create_test_vehicle, create_test_fuel_log):
        """Test fuel efficiency calculation"""
        fuel_service = FuelService(session)
        
        # Create test vehicle
        test_vehicle = create_test_vehicle(current_odometer=10000)
        
        # Create first fuel log (full tank)
        first_log = create_test_fuel_log(
            test_vehicle.id,
            odometer_reading=10000,
            fuel_amount=60.0,
            is_full_tank=True
        )
        
        # Create second fuel log (full tank) - should calculate efficiency
        second_log_data = FuelLogCreate(
            vehicle_id=test_vehicle.id,
            date=date.today() + timedelta(days=1),
            odometer_reading=10600,  # 600 km traveled
            fuel_amount=50.0,  # 50 liters consumed
            fuel_cost=650.0,
            price_per_liter=13.0,
            is_full_tank=True
        )
        
        second_log = await fuel_service.create_fuel_log(second_log_data)
        
        assert second_log.distance_since_last_fill == 600
        assert second_log.fuel_efficiency == 12.0  # 600 km / 50 liters
        assert second_log.cost_per_km == 650.0 / 600  # Cost per km
    
    @pytest.mark.asyncio
    async def test_fuel_log_updates_vehicle_odometer(self, session, create_test_vehicle):
        """Test that fuel log updates vehicle odometer"""
        from sqlmodel import select
        from models.vehicle import Vehicle
        
        fuel_service = FuelService(session)
        
        # Create test vehicle with lower odometer
        test_vehicle = create_test_vehicle(current_odometer=10000)
        
        # Create fuel log with higher odometer
        fuel_log_data = FuelLogCreate(
            vehicle_id=test_vehicle.id,
            date=date.today(),
            odometer_reading=10500,  # Higher than vehicle's current
            fuel_amount=40.0,
            fuel_cost=520.0,
            price_per_liter=13.0
        )
        
        await fuel_service.create_fuel_log(fuel_log_data)
        
        # Check that vehicle odometer was updated
        updated_vehicle = session.exec(select(Vehicle).where(Vehicle.id == test_vehicle.id)).first()
        assert updated_vehicle.current_odometer == 10500
    
    @pytest.mark.asyncio
    async def test_cannot_create_fuel_log_with_lower_odometer(self, session, create_test_vehicle):
        """Test that fuel log cannot be created with lower odometer reading"""
        fuel_service = FuelService(session)
        
        # Create test vehicle with higher odometer
        test_vehicle = create_test_vehicle(current_odometer=15000)
        
        # Try to create fuel log with lower odometer
        fuel_log_data = FuelLogCreate(
            vehicle_id=test_vehicle.id,
            date=date.today(),
            odometer_reading=14500,  # Lower than vehicle's current
            fuel_amount=40.0,
            fuel_cost=520.0,
            price_per_liter=13.0
        )
        
        with pytest.raises(Exception) as exc_info:
            await fuel_service.create_fuel_log(fuel_log_data)
        
        assert "cannot be less than current vehicle odometer" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_vehicle_fuel_history(self, session, create_test_vehicle, create_test_fuel_log):
        """Test getting fuel history for a vehicle"""
        from utils.pagination import PaginationParams
        
        fuel_service = FuelService(session)
        
        # Create test vehicle
        test_vehicle = create_test_vehicle()
        
        # Create multiple fuel logs
        create_test_fuel_log(
            test_vehicle.id,
            date=date.today() - timedelta(days=10),
            fuel_amount=50.0
        )
        create_test_fuel_log(
            test_vehicle.id,
            date=date.today() - timedelta(days=5),
            fuel_amount=45.0
        )
        create_test_fuel_log(
            test_vehicle.id,
            date=date.today(),
            fuel_amount=55.0
        )
        
        # Get fuel history
        pagination = PaginationParams(page=1, size=10)
        logs, total = await fuel_service.get_vehicle_fuel_history(test_vehicle.id, pagination)
        
        assert total == 3
        assert len(logs) == 3
        assert all(log.vehicle_id == test_vehicle.id for log in logs)
        # Should be ordered by date (newest first)
        assert logs[0].fuel_amount == 55.0
        assert logs[1].fuel_amount == 45.0
        assert logs[2].fuel_amount == 50.0
    
    @pytest.mark.asyncio
    async def test_get_fuel_stats(self, session, create_test_vehicle, create_test_fuel_log):
        """Test getting fuel consumption statistics"""
        fuel_service = FuelService(session)
        
        # Create test vehicle
        test_vehicle = create_test_vehicle()
        
        # Create fuel logs with efficiency data
        create_test_fuel_log(
            test_vehicle.id,
            fuel_amount=50.0,
            fuel_cost=650.0,
            distance_since_last_fill=600,
            fuel_efficiency=12.0
        )
        create_test_fuel_log(
            test_vehicle.id,
            fuel_amount=45.0,
            fuel_cost=585.0,
            distance_since_last_fill=540,
            fuel_efficiency=12.0
        )
        
        # Get fuel statistics
        stats = await fuel_service.get_fuel_stats(days=365, vehicle_id=test_vehicle.id)
        
        assert stats.total_fuel_consumed == 95.0  # 50 + 45
        assert stats.total_fuel_cost == 1235.0  # 650 + 585
        assert stats.average_price_per_liter == 1235.0 / 95.0
        assert stats.average_fuel_efficiency == 12.0
        assert stats.total_distance == 1140  # 600 + 540
        assert stats.cost_per_km == 1235.0 / 1140
    
    @pytest.mark.asyncio
    async def test_update_fuel_log(self, session, create_test_vehicle, create_test_fuel_log):
        """Test updating fuel log"""
        from schemas.fuel_log import FuelLogUpdate
        
        fuel_service = FuelService(session)
        
        # Create test vehicle and fuel log
        test_vehicle = create_test_vehicle()
        test_log = create_test_fuel_log(
            test_vehicle.id,
            fuel_amount=50.0,
            fuel_cost=650.0,
            station_name="Original Station"
        )
        
        # Update fuel log
        update_data = FuelLogUpdate(
            fuel_amount=55.0,
            fuel_cost=715.0,
            station_name="Updated Station",
            notes="Updated fuel log"
        )
        
        updated_log = await fuel_service.update_fuel_log(test_log.id, update_data)
        
        assert updated_log.fuel_amount == 55.0
        assert updated_log.fuel_cost == 715.0
        assert updated_log.station_name == "Updated Station"
        assert updated_log.notes == "Updated fuel log"
    
    @pytest.mark.asyncio
    async def test_delete_fuel_log(self, session, create_test_vehicle, create_test_fuel_log):
        """Test deleting fuel log"""
        fuel_service = FuelService(session)
        
        # Create test vehicle and fuel log
        test_vehicle = create_test_vehicle()
        test_log = create_test_fuel_log(test_vehicle.id)
        
        # Delete fuel log
        result = await fuel_service.delete_fuel_log(test_log.id)
        
        assert "deleted successfully" in result["message"]
        
        # Verify log is deleted
        with pytest.raises(Exception) as exc_info:
            await fuel_service.get_fuel_log(test_log.id)
        
        assert "not found" in str(exc_info.value)