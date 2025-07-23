"""
Vehicle service for fleet management operations
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status
from models.vehicle import Vehicle, VehicleStatus
from models.assignment import Assignment
from models.maintenance_record import MaintenanceRecord
from models.fuel_log import FuelLog
from schemas.vehicle import (
    VehicleCreate, VehicleUpdate, VehicleResponse, VehicleSummary, 
    VehicleSearch, VehicleAvailability
)
from utils.pagination import PaginationParams, paginate_query
from utils.notifications import send_compliance_alert
from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta
import redis
import uuid


class VehicleService:
    """Service for handling vehicle operations"""
    
    def __init__(self, session: Session, redis_client: redis.Redis):
        self.session = session
        self.redis = redis_client
    
    async def create_vehicle(self, vehicle_data: VehicleCreate) -> VehicleResponse:
        """Create a new vehicle"""
        # Check if license plate already exists
        statement = select(Vehicle).where(Vehicle.license_plate == vehicle_data.license_plate)
        existing_vehicle = self.session.exec(statement).first()
        
        if existing_vehicle:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle with this license plate already exists"
            )
        
        # Create vehicle
        vehicle = Vehicle(**vehicle_data.model_dump())
        
        self.session.add(vehicle)
        self.session.commit()
        self.session.refresh(vehicle)
        
        return self._create_vehicle_response(vehicle)
    
    async def get_vehicle(self, vehicle_id: uuid.UUID) -> VehicleResponse:
        """Get vehicle by ID"""
        statement = select(Vehicle).where(Vehicle.id == vehicle_id)
        vehicle = self.session.exec(statement).first()
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        return self._create_vehicle_response(vehicle)
    
    async def get_vehicles(
        self, 
        pagination: PaginationParams,
        search: Optional[VehicleSearch] = None
    ) -> Tuple[List[VehicleResponse], int]:
        """Get list of vehicles with optional search"""
        query = select(Vehicle)
        
        # Apply search filters
        if search:
            conditions = []
            
            if search.query:
                search_term = f"%{search.query}%"
                conditions.append(
                    or_(
                        Vehicle.license_plate.ilike(search_term),
                        Vehicle.brand.ilike(search_term),
                        Vehicle.model.ilike(search_term),
                        Vehicle.vin_number.ilike(search_term)
                    )
                )
            
            if search.vehicle_type:
                conditions.append(Vehicle.vehicle_type == search.vehicle_type)
            
            if search.status:
                conditions.append(Vehicle.status == search.status)
            
            if search.fuel_type:
                conditions.append(Vehicle.fuel_type == search.fuel_type)
            
            if search.brand:
                conditions.append(Vehicle.brand.ilike(f"%{search.brand}%"))
            
            if search.min_seating_capacity:
                conditions.append(Vehicle.seating_capacity >= search.min_seating_capacity)
            
            if search.max_seating_capacity:
                conditions.append(Vehicle.seating_capacity <= search.max_seating_capacity)
            
            if search.min_year:
                conditions.append(Vehicle.year >= search.min_year)
            
            if search.max_year:
                conditions.append(Vehicle.year <= search.max_year)
            
            if search.is_active is not None:
                conditions.append(Vehicle.is_active == search.is_active)
            
            if conditions:
                query = query.where(and_(*conditions))
        
        # Order by creation date (newest first)
        query = query.order_by(Vehicle.created_at.desc())
        
        vehicles, total = paginate_query(self.session, query, pagination)
        
        return [self._create_vehicle_response(vehicle) for vehicle in vehicles], total
    
    async def update_vehicle(self, vehicle_id: uuid.UUID, vehicle_data: VehicleUpdate) -> VehicleResponse:
        """Update vehicle information"""
        statement = select(Vehicle).where(Vehicle.id == vehicle_id)
        vehicle = self.session.exec(statement).first()
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        # Check license plate uniqueness if being updated
        if vehicle_data.license_plate and vehicle_data.license_plate != vehicle.license_plate:
            existing_stmt = select(Vehicle).where(Vehicle.license_plate == vehicle_data.license_plate)
            existing_vehicle = self.session.exec(existing_stmt).first()
            if existing_vehicle:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Vehicle with this license plate already exists"
                )
        
        # Update fields
        update_data = vehicle_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(vehicle, field, value)
        
        vehicle.updated_at = datetime.utcnow()
        
        self.session.add(vehicle)
        self.session.commit()
        self.session.refresh(vehicle)
        
        return self._create_vehicle_response(vehicle)
    
    async def delete_vehicle(self, vehicle_id: uuid.UUID) -> dict:
        """Delete vehicle (soft delete by marking inactive)"""
        statement = select(Vehicle).where(Vehicle.id == vehicle_id)
        vehicle = self.session.exec(statement).first()
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        # Check for active assignments
        active_assignments = self.session.exec(
            select(Assignment).where(
                Assignment.vehicle_id == vehicle_id,
                Assignment.status == "Active"
            )
        ).all()
        
        if active_assignments:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete vehicle with active assignments"
            )
        
        vehicle.is_active = False
        vehicle.status = VehicleStatus.RETIRED
        vehicle.updated_at = datetime.utcnow()
        
        self.session.add(vehicle)
        self.session.commit()
        
        return {"message": "Vehicle deactivated successfully"}
    
    async def check_availability(
        self, 
        vehicle_id: uuid.UUID, 
        start_date: date, 
        end_date: date
    ) -> VehicleAvailability:
        """Check vehicle availability for a specific period"""
        statement = select(Vehicle).where(Vehicle.id == vehicle_id)
        vehicle = self.session.exec(statement).first()
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        # Check for conflicting assignments
        conflicts_stmt = select(Assignment).where(
            Assignment.vehicle_id == vehicle_id,
            Assignment.status.in_(["Scheduled", "Active"]),
            or_(
                and_(Assignment.start_date <= start_date, Assignment.end_date >= start_date),
                and_(Assignment.start_date <= end_date, Assignment.end_date >= end_date),
                and_(Assignment.start_date >= start_date, Assignment.end_date <= end_date)
            )
        )
        
        conflicting_assignments = self.session.exec(conflicts_stmt).all()
        
        is_available = (
            vehicle.status == VehicleStatus.AVAILABLE and
            len(conflicting_assignments) == 0
        )
        
        return VehicleAvailability(
            vehicle_id=vehicle_id,
            start_date=start_date,
            end_date=end_date,
            is_available=is_available,
            conflicting_assignments=[assignment.id for assignment in conflicting_assignments],
            status=vehicle.status,
            notes=f"Vehicle status: {vehicle.status.value}"
        )
    
    async def get_vehicle_summary(self, vehicle_id: uuid.UUID) -> VehicleSummary:
        """Get comprehensive vehicle summary with statistics"""
        statement = select(Vehicle).where(Vehicle.id == vehicle_id)
        vehicle = self.session.exec(statement).first()
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        # Get assignment statistics
        assignments_stmt = select(Assignment).where(Assignment.vehicle_id == vehicle_id)
        assignments = self.session.exec(assignments_stmt).all()
        
        active_assignments = [a for a in assignments if a.status == "Active"]
        
        # Get maintenance statistics
        maintenance_stmt = select(MaintenanceRecord).where(MaintenanceRecord.vehicle_id == vehicle_id)
        maintenance_records = self.session.exec(maintenance_stmt).all()
        
        total_maintenance_cost = sum(record.cost or 0 for record in maintenance_records)
        last_maintenance = max(maintenance_records, key=lambda x: x.date_performed, default=None)
        
        # Get fuel efficiency
        fuel_stmt = select(FuelLog).where(
            FuelLog.vehicle_id == vehicle_id,
            FuelLog.fuel_efficiency.is_not(None)
        )
        fuel_logs = self.session.exec(fuel_stmt).all()
        
        avg_fuel_efficiency = None
        if fuel_logs:
            avg_fuel_efficiency = sum(log.fuel_efficiency for log in fuel_logs) / len(fuel_logs)
        
        # Calculate total distance
        total_distance = sum(assignment.get_distance_traveled() or 0 for assignment in assignments)
        
        # Days since last service
        days_since_service = None
        if last_maintenance:
            days_since_service = (date.today() - last_maintenance.date_performed).days
        
        # Check compliance alerts
        compliance_status = vehicle.get_compliance_status()
        compliance_alerts = []
        
        for doc_type, status in compliance_status.items():
            if status.get("needs_attention"):
                compliance_alerts.append({
                    "type": doc_type,
                    "expiry_date": status["expiry_date"].isoformat(),
                    "days_until_expiry": status["days_until_expiry"],
                    "is_expired": status["is_expired"]
                })
        
        # Create base response
        base_response = self._create_vehicle_response(vehicle)
        
        return VehicleSummary(
            **base_response.model_dump(),
            total_assignments=len(assignments),
            active_assignments=len(active_assignments),
            total_maintenance_records=len(maintenance_records),
            last_maintenance_date=last_maintenance.date_performed if last_maintenance else None,
            total_maintenance_cost=total_maintenance_cost,
            average_fuel_efficiency=avg_fuel_efficiency,
            total_distance_traveled=total_distance,
            days_since_last_service=days_since_service,
            upcoming_maintenance=[],  # TODO: Implement based on maintenance schedule
            compliance_alerts=compliance_alerts
        )
    
    async def get_available_vehicles(
        self, 
        start_date: date, 
        end_date: date,
        vehicle_type: Optional[str] = None,
        min_seating_capacity: Optional[int] = None
    ) -> List[VehicleResponse]:
        """Get all available vehicles for a specific period"""
        query = select(Vehicle).where(
            Vehicle.status == VehicleStatus.AVAILABLE,
            Vehicle.is_active == True
        )
        
        # Apply filters
        if vehicle_type:
            query = query.where(Vehicle.vehicle_type == vehicle_type)
        
        if min_seating_capacity:
            query = query.where(Vehicle.seating_capacity >= min_seating_capacity)
        
        vehicles = self.session.exec(query).all()
        
        # Filter out vehicles with conflicting assignments
        available_vehicles = []
        for vehicle in vehicles:
            if vehicle.is_available_for_period(start_date, end_date):
                available_vehicles.append(self._create_vehicle_response(vehicle))
        
        return available_vehicles
    
    async def check_compliance_alerts(self) -> List[dict]:
        """Check for vehicles with upcoming compliance deadlines"""
        alert_date = date.today() + timedelta(days=settings.compliance_alert_days)
        
        vehicles_stmt = select(Vehicle).where(
            Vehicle.is_active == True,
            or_(
                Vehicle.registration_expiry <= alert_date,
                Vehicle.insurance_expiry <= alert_date,
                Vehicle.inspection_expiry <= alert_date
            )
        )
        
        vehicles = self.session.exec(vehicles_stmt).all()
        
        alerts = []
        for vehicle in vehicles:
            compliance_status = vehicle.get_compliance_status()
            for doc_type, status in compliance_status.items():
                if status.get("needs_attention"):
                    alerts.append({
                        "vehicle_id": str(vehicle.id),
                        "license_plate": vehicle.license_plate,
                        "document_type": doc_type,
                        "expiry_date": status["expiry_date"].isoformat(),
                        "days_until_expiry": status["days_until_expiry"],
                        "is_expired": status["is_expired"]
                    })
                    
                    # Send notification
                    await send_compliance_alert(
                        self.redis,
                        vehicle.id,
                        doc_type,
                        {
                            "license_plate": vehicle.license_plate,
                            "expiry_date": status["expiry_date"].isoformat(),
                            "days_until_expiry": status["days_until_expiry"]
                        }
                    )
        
        return alerts
    
    def _create_vehicle_response(self, vehicle: Vehicle) -> VehicleResponse:
        """Create vehicle response with calculated fields"""
        return VehicleResponse(
            id=vehicle.id,
            license_plate=vehicle.license_plate,
            vehicle_type=vehicle.vehicle_type,
            brand=vehicle.brand,
            model=vehicle.model,
            year=vehicle.year,
            color=vehicle.color,
            seating_capacity=vehicle.seating_capacity,
            fuel_type=vehicle.fuel_type,
            engine_size=vehicle.engine_size,
            transmission=vehicle.transmission,
            status=vehicle.status,
            current_odometer=vehicle.current_odometer,
            registration_expiry=vehicle.registration_expiry,
            insurance_expiry=vehicle.insurance_expiry,
            inspection_expiry=vehicle.inspection_expiry,
            purchase_date=vehicle.purchase_date,
            purchase_price=vehicle.purchase_price,
            vin_number=vehicle.vin_number,
            notes=vehicle.notes,
            is_active=vehicle.is_active,
            created_at=vehicle.created_at,
            updated_at=vehicle.updated_at,
            display_name=vehicle.get_display_name(),
            age_years=vehicle.calculate_age_years(),
            compliance_status=vehicle.get_compliance_status()
        )