"""
Fuel service for tracking vehicle fuel consumption
"""
from sqlmodel import Session, select, and_, func
from fastapi import HTTPException, status
from models.fuel_log import FuelLog
from models.vehicle import Vehicle
from schemas.fuel_log import (
    FuelLogCreate, FuelLogUpdate, FuelLogResponse, FuelStats
)
from utils.pagination import PaginationParams, paginate_query
from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta
import uuid


class FuelService:
    """Service for handling fuel consumption tracking"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_fuel_log(self, log_data: FuelLogCreate) -> FuelLogResponse:
        """Create a new fuel log entry"""
        # Verify vehicle exists
        vehicle_stmt = select(Vehicle).where(Vehicle.id == log_data.vehicle_id)
        vehicle = self.session.exec(vehicle_stmt).first()
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        # Validate odometer reading
        if log_data.odometer_reading < vehicle.current_odometer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Odometer reading cannot be less than current vehicle odometer"
            )
        
        # Calculate efficiency if this is a full tank
        distance_since_last_fill = None
        fuel_efficiency = None
        
        if log_data.is_full_tank:
            # Get last full tank entry
            last_full_tank_stmt = select(FuelLog).where(
                FuelLog.vehicle_id == log_data.vehicle_id,
                FuelLog.is_full_tank == True
            ).order_by(FuelLog.date.desc()).limit(1)
            
            last_full_tank = self.session.exec(last_full_tank_stmt).first()
            
            if last_full_tank:
                distance_since_last_fill = log_data.odometer_reading - last_full_tank.odometer_reading
                if distance_since_last_fill > 0:
                    fuel_efficiency = distance_since_last_fill / log_data.fuel_amount
        
        # Create fuel log
        fuel_log = FuelLog(
            **log_data.model_dump(),
            distance_since_last_fill=distance_since_last_fill,
            fuel_efficiency=fuel_efficiency
        )
        
        self.session.add(fuel_log)
        
        # Update vehicle odometer
        vehicle.current_odometer = log_data.odometer_reading
        vehicle.updated_at = datetime.utcnow()
        self.session.add(vehicle)
        
        self.session.commit()
        self.session.refresh(fuel_log)
        
        return self._create_fuel_log_response(fuel_log)
    
    async def get_fuel_log(self, log_id: uuid.UUID) -> FuelLogResponse:
        """Get fuel log by ID"""
        statement = select(FuelLog).where(FuelLog.id == log_id)
        fuel_log = self.session.exec(statement).first()
        
        if not fuel_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fuel log not found"
            )
        
        return self._create_fuel_log_response(fuel_log)
    
    async def get_fuel_logs(
        self, 
        pagination: PaginationParams,
        vehicle_id: Optional[uuid.UUID] = None,
        driver_id: Optional[uuid.UUID] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Tuple[List[FuelLogResponse], int]:
        """Get list of fuel logs with optional filters"""
        query = select(FuelLog)
        
        # Apply filters
        conditions = []
        
        if vehicle_id:
            conditions.append(FuelLog.vehicle_id == vehicle_id)
        
        if driver_id:
            conditions.append(FuelLog.driver_id == driver_id)
        
        if date_from:
            conditions.append(FuelLog.date >= date_from)
        
        if date_to:
            conditions.append(FuelLog.date <= date_to)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Order by date (newest first)
        query = query.order_by(FuelLog.date.desc())
        
        logs, total = paginate_query(self.session, query, pagination)
        
        return [self._create_fuel_log_response(log) for log in logs], total
    
    async def update_fuel_log(self, log_id: uuid.UUID, log_data: FuelLogUpdate) -> FuelLogResponse:
        """Update fuel log information"""
        statement = select(FuelLog).where(FuelLog.id == log_id)
        fuel_log = self.session.exec(statement).first()
        
        if not fuel_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fuel log not found"
            )
        
        # Update fields
        update_data = log_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(fuel_log, field, value)
        
        # Recalculate efficiency if relevant fields changed
        if any(field in update_data for field in ['fuel_amount', 'odometer_reading', 'is_full_tank']):
            if fuel_log.distance_since_last_fill and fuel_log.fuel_amount > 0:
                fuel_log.fuel_efficiency = fuel_log.distance_since_last_fill / fuel_log.fuel_amount
        
        self.session.add(fuel_log)
        self.session.commit()
        self.session.refresh(fuel_log)
        
        return self._create_fuel_log_response(fuel_log)
    
    async def delete_fuel_log(self, log_id: uuid.UUID) -> dict:
        """Delete fuel log"""
        statement = select(FuelLog).where(FuelLog.id == log_id)
        fuel_log = self.session.exec(statement).first()
        
        if not fuel_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fuel log not found"
            )
        
        self.session.delete(fuel_log)
        self.session.commit()
        
        return {"message": "Fuel log deleted successfully"}
    
    async def get_vehicle_fuel_history(
        self, 
        vehicle_id: uuid.UUID, 
        pagination: PaginationParams
    ) -> Tuple[List[FuelLogResponse], int]:
        """Get fuel history for a specific vehicle"""
        # Verify vehicle exists
        vehicle_stmt = select(Vehicle).where(Vehicle.id == vehicle_id)
        vehicle = self.session.exec(vehicle_stmt).first()
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        return await self.get_fuel_logs(pagination, vehicle_id=vehicle_id)
    
    async def get_fuel_stats(self, days: int = 365, vehicle_id: Optional[uuid.UUID] = None) -> FuelStats:
        """Get fuel consumption statistics"""
        start_date = date.today() - timedelta(days=days)
        
        query = select(FuelLog).where(FuelLog.date >= start_date)
        
        if vehicle_id:
            query = query.where(FuelLog.vehicle_id == vehicle_id)
        
        fuel_logs = self.session.exec(query).all()
        
        if not fuel_logs:
            return FuelStats(
                total_fuel_consumed=0.0,
                total_fuel_cost=0.0,
                average_price_per_liter=0.0,
                average_fuel_efficiency=None,
                total_distance=0,
                cost_per_km=None,
                by_month={},
                by_vehicle_type={}
            )
        
        # Calculate totals
        total_fuel = sum(log.fuel_amount for log in fuel_logs)
        total_cost = sum(log.fuel_cost for log in fuel_logs)
        total_distance = sum(log.distance_since_last_fill or 0 for log in fuel_logs)
        
        # Calculate averages
        avg_price_per_liter = total_cost / total_fuel if total_fuel > 0 else 0.0
        
        efficiency_logs = [log for log in fuel_logs if log.fuel_efficiency]
        avg_efficiency = sum(log.fuel_efficiency for log in efficiency_logs) / len(efficiency_logs) if efficiency_logs else None
        
        cost_per_km = total_cost / total_distance if total_distance > 0 else None
        
        # Group by month
        by_month = {}
        for log in fuel_logs:
            month_key = log.date.strftime('%Y-%m')
            if month_key not in by_month:
                by_month[month_key] = {
                    "fuel_consumed": 0.0,
                    "total_cost": 0.0,
                    "distance": 0
                }
            
            by_month[month_key]["fuel_consumed"] += log.fuel_amount
            by_month[month_key]["total_cost"] += log.fuel_cost
            by_month[month_key]["distance"] += log.distance_since_last_fill or 0
        
        # Group by vehicle type (need to join with vehicles)
        by_vehicle_type = {}
        for log in fuel_logs:
            vehicle_stmt = select(Vehicle).where(Vehicle.id == log.vehicle_id)
            vehicle = self.session.exec(vehicle_stmt).first()
            
            if vehicle:
                vehicle_type = vehicle.vehicle_type.value
                if vehicle_type not in by_vehicle_type:
                    by_vehicle_type[vehicle_type] = {
                        "fuel_consumed": 0.0,
                        "total_cost": 0.0,
                        "distance": 0
                    }
                
                by_vehicle_type[vehicle_type]["fuel_consumed"] += log.fuel_amount
                by_vehicle_type[vehicle_type]["total_cost"] += log.fuel_cost
                by_vehicle_type[vehicle_type]["distance"] += log.distance_since_last_fill or 0
        
        return FuelStats(
            total_fuel_consumed=total_fuel,
            total_fuel_cost=total_cost,
            average_price_per_liter=avg_price_per_liter,
            average_fuel_efficiency=avg_efficiency,
            total_distance=total_distance,
            cost_per_km=cost_per_km,
            by_month=by_month,
            by_vehicle_type=by_vehicle_type
        )
    
    def _create_fuel_log_response(self, fuel_log: FuelLog) -> FuelLogResponse:
        """Create fuel log response with calculated fields"""
        return FuelLogResponse(
            id=fuel_log.id,
            vehicle_id=fuel_log.vehicle_id,
            date=fuel_log.date,
            odometer_reading=fuel_log.odometer_reading,
            fuel_amount=fuel_log.fuel_amount,
            fuel_cost=fuel_log.fuel_cost,
            price_per_liter=fuel_log.price_per_liter,
            station_name=fuel_log.station_name,
            location=fuel_log.location,
            trip_purpose=fuel_log.trip_purpose,
            driver_id=fuel_log.driver_id,
            distance_since_last_fill=fuel_log.distance_since_last_fill,
            fuel_efficiency=fuel_log.fuel_efficiency,
            is_full_tank=fuel_log.is_full_tank,
            receipt_number=fuel_log.receipt_number,
            notes=fuel_log.notes,
            created_at=fuel_log.created_at,
            created_by=fuel_log.created_by,
            cost_per_km=fuel_log.calculate_cost_per_km()
        )