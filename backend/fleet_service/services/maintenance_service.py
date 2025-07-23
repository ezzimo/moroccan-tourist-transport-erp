"""
Maintenance service for vehicle service tracking
"""
from sqlmodel import Session, select, and_, func
from fastapi import HTTPException, status
from models.maintenance_record import MaintenanceRecord, MaintenanceType
from models.vehicle import Vehicle
from schemas.maintenance_record import (
    MaintenanceRecordCreate, MaintenanceRecordUpdate, MaintenanceRecordResponse, MaintenanceStats
)
from utils.pagination import PaginationParams, paginate_query
from utils.notifications import send_maintenance_reminder
from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta
import redis
import uuid


class MaintenanceService:
    """Service for handling maintenance operations"""
    
    def __init__(self, session: Session, redis_client: redis.Redis):
        self.session = session
        self.redis = redis_client
    
    async def create_maintenance_record(self, record_data: MaintenanceRecordCreate) -> MaintenanceRecordResponse:
        """Create a new maintenance record"""
        # Verify vehicle exists
        vehicle_stmt = select(Vehicle).where(Vehicle.id == record_data.vehicle_id)
        vehicle = self.session.exec(vehicle_stmt).first()
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        # Create maintenance record
        record = MaintenanceRecord(**record_data.model_dump())
        
        self.session.add(record)
        
        # Update vehicle odometer if provided
        if record_data.odometer_reading and record_data.odometer_reading > vehicle.current_odometer:
            vehicle.current_odometer = record_data.odometer_reading
            vehicle.updated_at = datetime.utcnow()
            self.session.add(vehicle)
        
        self.session.commit()
        self.session.refresh(record)
        
        # Send notification for next service if scheduled
        if record.next_service_date:
            await send_maintenance_reminder(
                self.redis,
                record.vehicle_id,
                record.maintenance_type.value,
                {
                    "next_service_date": record.next_service_date.isoformat(),
                    "description": record.description,
                    "vehicle_license": vehicle.license_plate
                }
            )
        
        return self._create_maintenance_response(record)
    
    async def get_maintenance_record(self, record_id: uuid.UUID) -> MaintenanceRecordResponse:
        """Get maintenance record by ID"""
        statement = select(MaintenanceRecord).where(MaintenanceRecord.id == record_id)
        record = self.session.exec(statement).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Maintenance record not found"
            )
        
        return self._create_maintenance_response(record)
    
    async def get_maintenance_records(
        self, 
        pagination: PaginationParams,
        vehicle_id: Optional[uuid.UUID] = None,
        maintenance_type: Optional[MaintenanceType] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        is_completed: Optional[bool] = None
    ) -> Tuple[List[MaintenanceRecordResponse], int]:
        """Get list of maintenance records with optional filters"""
        query = select(MaintenanceRecord)
        
        # Apply filters
        conditions = []
        
        if vehicle_id:
            conditions.append(MaintenanceRecord.vehicle_id == vehicle_id)
        
        if maintenance_type:
            conditions.append(MaintenanceRecord.maintenance_type == maintenance_type)
        
        if date_from:
            conditions.append(MaintenanceRecord.date_performed >= date_from)
        
        if date_to:
            conditions.append(MaintenanceRecord.date_performed <= date_to)
        
        if is_completed is not None:
            conditions.append(MaintenanceRecord.is_completed == is_completed)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Order by date (newest first)
        query = query.order_by(MaintenanceRecord.date_performed.desc())
        
        records, total = paginate_query(self.session, query, pagination)
        
        return [self._create_maintenance_response(record) for record in records], total
    
    async def update_maintenance_record(
        self, 
        record_id: uuid.UUID, 
        record_data: MaintenanceRecordUpdate
    ) -> MaintenanceRecordResponse:
        """Update maintenance record information"""
        statement = select(MaintenanceRecord).where(MaintenanceRecord.id == record_id)
        record = self.session.exec(statement).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Maintenance record not found"
            )
        
        # Update fields
        update_data = record_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(record, field, value)
        
        record.updated_at = datetime.utcnow()
        
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        
        return self._create_maintenance_response(record)
    
    async def delete_maintenance_record(self, record_id: uuid.UUID) -> dict:
        """Delete maintenance record"""
        statement = select(MaintenanceRecord).where(MaintenanceRecord.id == record_id)
        record = self.session.exec(statement).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Maintenance record not found"
            )
        
        self.session.delete(record)
        self.session.commit()
        
        return {"message": "Maintenance record deleted successfully"}
    
    async def get_vehicle_maintenance_history(
        self, 
        vehicle_id: uuid.UUID, 
        pagination: PaginationParams
    ) -> Tuple[List[MaintenanceRecordResponse], int]:
        """Get maintenance history for a specific vehicle"""
        # Verify vehicle exists
        vehicle_stmt = select(Vehicle).where(Vehicle.id == vehicle_id)
        vehicle = self.session.exec(vehicle_stmt).first()
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        return await self.get_maintenance_records(pagination, vehicle_id=vehicle_id)
    
    async def get_upcoming_maintenance(self, days_ahead: int = 30) -> List[dict]:
        """Get vehicles with upcoming maintenance"""
        cutoff_date = date.today() + timedelta(days=days_ahead)
        
        statement = select(MaintenanceRecord).where(
            MaintenanceRecord.next_service_date <= cutoff_date,
            MaintenanceRecord.next_service_date >= date.today(),
            MaintenanceRecord.is_completed == True
        ).order_by(MaintenanceRecord.next_service_date)
        
        upcoming_records = self.session.exec(statement).all()
        
        upcoming_maintenance = []
        for record in upcoming_records:
            # Get vehicle info
            vehicle_stmt = select(Vehicle).where(Vehicle.id == record.vehicle_id)
            vehicle = self.session.exec(vehicle_stmt).first()
            
            if vehicle:
                days_until = (record.next_service_date - date.today()).days
                upcoming_maintenance.append({
                    "vehicle_id": str(record.vehicle_id),
                    "license_plate": vehicle.license_plate,
                    "vehicle_display_name": vehicle.get_display_name(),
                    "maintenance_type": record.maintenance_type.value,
                    "next_service_date": record.next_service_date.isoformat(),
                    "days_until_service": days_until,
                    "last_service_description": record.description,
                    "next_service_odometer": record.next_service_odometer
                })
        
        return upcoming_maintenance
    
    async def get_maintenance_stats(self, days: int = 365) -> MaintenanceStats:
        """Get maintenance statistics for the specified period"""
        start_date = date.today() - timedelta(days=days)
        
        # Total records and cost
        total_stmt = select(
            func.count(MaintenanceRecord.id),
            func.sum(MaintenanceRecord.cost)
        ).where(
            MaintenanceRecord.date_performed >= start_date,
            MaintenanceRecord.cost.is_not(None)
        )
        
        total_count, total_cost = self.session.exec(total_stmt).one()
        total_cost = total_cost or 0.0
        
        # By type
        type_stmt = select(
            MaintenanceRecord.maintenance_type,
            func.count(MaintenanceRecord.id),
            func.sum(MaintenanceRecord.cost)
        ).where(
            MaintenanceRecord.date_performed >= start_date
        ).group_by(MaintenanceRecord.maintenance_type)
        
        by_type = {}
        preventive_count = 0
        
        for maintenance_type, count, cost in self.session.exec(type_stmt):
            by_type[maintenance_type.value] = {
                "count": count,
                "total_cost": float(cost or 0)
            }
            if maintenance_type == MaintenanceType.PREVENTIVE:
                preventive_count = count
        
        # By month
        monthly_stmt = select(
            func.date_trunc('month', MaintenanceRecord.date_performed).label('month'),
            func.count(MaintenanceRecord.id),
            func.sum(MaintenanceRecord.cost)
        ).where(
            MaintenanceRecord.date_performed >= start_date
        ).group_by(func.date_trunc('month', MaintenanceRecord.date_performed))
        
        by_month = {}
        for month, count, cost in self.session.exec(monthly_stmt):
            by_month[month.strftime('%Y-%m')] = {
                "count": count,
                "total_cost": float(cost or 0)
            }
        
        # Calculate averages and percentages
        average_cost = total_cost / total_count if total_count > 0 else 0.0
        preventive_percentage = (preventive_count / total_count * 100) if total_count > 0 else 0.0
        
        # Vehicles needing service (based on next service date)
        vehicles_needing_service_stmt = select(func.count(func.distinct(MaintenanceRecord.vehicle_id))).where(
            MaintenanceRecord.next_service_date <= date.today() + timedelta(days=7),
            MaintenanceRecord.next_service_date >= date.today()
        )
        vehicles_needing_service = self.session.exec(vehicles_needing_service_stmt).one()
        
        return MaintenanceStats(
            total_records=total_count,
            total_cost=total_cost,
            by_type=by_type,
            by_month=by_month,
            average_cost=average_cost,
            preventive_percentage=preventive_percentage,
            vehicles_needing_service=vehicles_needing_service
        )
    
    def _create_maintenance_response(self, record: MaintenanceRecord) -> MaintenanceRecordResponse:
        """Create maintenance response with calculated fields"""
        return MaintenanceRecordResponse(
            id=record.id,
            vehicle_id=record.vehicle_id,
            maintenance_type=record.maintenance_type,
            description=record.description,
            date_performed=record.date_performed,
            provider_name=record.provider_name,
            provider_contact=record.provider_contact,
            cost=record.cost,
            currency=record.currency,
            odometer_reading=record.odometer_reading,
            parts_replaced=record.parts_replaced,
            labor_hours=record.labor_hours,
            next_service_date=record.next_service_date,
            next_service_odometer=record.next_service_odometer,
            is_completed=record.is_completed,
            warranty_until=record.warranty_until,
            notes=record.notes,
            performed_by=record.performed_by,
            approved_by=record.approved_by,
            created_at=record.created_at,
            updated_at=record.updated_at,
            is_under_warranty=record.is_under_warranty(),
            cost_per_hour=record.get_cost_per_hour()
        )