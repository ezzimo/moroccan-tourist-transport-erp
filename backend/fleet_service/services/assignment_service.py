"""
Assignment service for vehicle-tour allocation
"""
from sqlmodel import Session, select, and_, or_
from fastapi import HTTPException, status
from models.assignment import Assignment, AssignmentStatus
from models.vehicle import Vehicle, VehicleStatus
from schemas.assignment import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse, AssignmentConflict
)
from utils.pagination import PaginationParams, paginate_query
from utils.notifications import NotificationService
from typing import List, Optional, Tuple
from datetime import datetime, date
import redis
import uuid
import httpx


class AssignmentService:
    """Service for handling vehicle assignment operations"""
    
    def __init__(self, session: Session, redis_client: redis.Redis):
        self.session = session
        self.redis = redis_client
        self.notification_service = NotificationService(redis_client)
    
    async def create_assignment(self, assignment_data: AssignmentCreate) -> AssignmentResponse:
        """Create a new vehicle assignment"""
        # Verify vehicle exists and is available
        vehicle_stmt = select(Vehicle).where(Vehicle.id == assignment_data.vehicle_id)
        vehicle = self.session.exec(vehicle_stmt).first()
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        if not vehicle.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle is not active"
            )
        
        # Check for conflicts
        conflicts = await self._check_assignment_conflicts(
            assignment_data.vehicle_id,
            assignment_data.start_date,
            assignment_data.end_date
        )
        
        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Vehicle has conflicting assignments: {[str(c.conflicting_assignment_id) for c in conflicts]}"
            )
        
        # Verify tour instance exists (call tour service)
        await self._verify_tour_instance_exists(assignment_data.tour_instance_id)
        
        # Create assignment
        assignment = Assignment(**assignment_data.model_dump())
        
        self.session.add(assignment)
        
        # Update vehicle status if assignment starts today or is active
        today = date.today()
        if assignment.start_date <= today <= assignment.end_date:
            vehicle.status = VehicleStatus.IN_USE
            vehicle.updated_at = datetime.utcnow()
            self.session.add(vehicle)
        
        self.session.commit()
        self.session.refresh(assignment)
        
        # Send notification
        await self.notification_service.send_assignment_update(
            assignment.vehicle_id,
            assignment.id,
            "created"
        )
        
        return self._create_assignment_response(assignment)
    
    async def get_assignment(self, assignment_id: uuid.UUID) -> AssignmentResponse:
        """Get assignment by ID"""
        statement = select(Assignment).where(Assignment.id == assignment_id)
        assignment = self.session.exec(statement).first()
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        return self._create_assignment_response(assignment)
    
    async def get_assignments(
        self, 
        pagination: PaginationParams,
        vehicle_id: Optional[uuid.UUID] = None,
        tour_instance_id: Optional[uuid.UUID] = None,
        driver_id: Optional[uuid.UUID] = None,
        status: Optional[AssignmentStatus] = None,
        start_date_from: Optional[date] = None,
        start_date_to: Optional[date] = None
    ) -> Tuple[List[AssignmentResponse], int]:
        """Get list of assignments with optional filters"""
        query = select(Assignment)
        
        # Apply filters
        conditions = []
        
        if vehicle_id:
            conditions.append(Assignment.vehicle_id == vehicle_id)
        
        if tour_instance_id:
            conditions.append(Assignment.tour_instance_id == tour_instance_id)
        
        if driver_id:
            conditions.append(Assignment.driver_id == driver_id)
        
        if status:
            conditions.append(Assignment.status == status)
        
        if start_date_from:
            conditions.append(Assignment.start_date >= start_date_from)
        
        if start_date_to:
            conditions.append(Assignment.start_date <= start_date_to)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Order by start date (newest first)
        query = query.order_by(Assignment.start_date.desc())
        
        assignments, total = paginate_query(self.session, query, pagination)
        
        return [self._create_assignment_response(assignment) for assignment in assignments], total
    
    async def update_assignment(
        self, 
        assignment_id: uuid.UUID, 
        assignment_data: AssignmentUpdate
    ) -> AssignmentResponse:
        """Update assignment information"""
        statement = select(Assignment).where(Assignment.id == assignment_id)
        assignment = self.session.exec(statement).first()
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        # Check for conflicts if dates are being updated
        if assignment_data.start_date or assignment_data.end_date:
            new_start = assignment_data.start_date or assignment.start_date
            new_end = assignment_data.end_date or assignment.end_date
            
            conflicts = await self._check_assignment_conflicts(
                assignment.vehicle_id,
                new_start,
                new_end,
                exclude_assignment_id=assignment_id
            )
            
            if conflicts:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Assignment conflicts with existing assignments: {[str(c.conflicting_assignment_id) for c in conflicts]}"
                )
        
        # Update fields
        update_data = assignment_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(assignment, field, value)
        
        assignment.updated_at = datetime.utcnow()
        
        self.session.add(assignment)
        self.session.commit()
        self.session.refresh(assignment)
        
        # Send notification
        await self.notification_service.send_assignment_update(
            assignment.vehicle_id,
            assignment.id,
            "updated"
        )
        
        return self._create_assignment_response(assignment)
    
    async def cancel_assignment(self, assignment_id: uuid.UUID, reason: str) -> AssignmentResponse:
        """Cancel an assignment"""
        statement = select(Assignment).where(Assignment.id == assignment_id)
        assignment = self.session.exec(statement).first()
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        if assignment.status == AssignmentStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel completed assignment"
            )
        
        # Update assignment
        assignment.status = AssignmentStatus.CANCELLED
        assignment.notes = f"{assignment.notes or ''}\n\nCancellation reason: {reason}".strip()
        assignment.updated_at = datetime.utcnow()
        
        # Update vehicle status if it was in use for this assignment
        if assignment.status == AssignmentStatus.ACTIVE:
            vehicle_stmt = select(Vehicle).where(Vehicle.id == assignment.vehicle_id)
            vehicle = self.session.exec(vehicle_stmt).first()
            
            if vehicle:
                vehicle.status = VehicleStatus.AVAILABLE
                vehicle.updated_at = datetime.utcnow()
                self.session.add(vehicle)
        
        self.session.add(assignment)
        self.session.commit()
        self.session.refresh(assignment)
        
        # Send notification
        await self.notification_service.send_assignment_update(
            assignment.vehicle_id,
            assignment.id,
            "cancelled"
        )
        
        return self._create_assignment_response(assignment)
    
    async def start_assignment(self, assignment_id: uuid.UUID, start_odometer: int) -> AssignmentResponse:
        """Start an assignment (mark as active)"""
        statement = select(Assignment).where(Assignment.id == assignment_id)
        assignment = self.session.exec(statement).first()
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        if assignment.status != AssignmentStatus.SCHEDULED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only scheduled assignments can be started"
            )
        
        # Update assignment
        assignment.status = AssignmentStatus.ACTIVE
        assignment.actual_start_date = datetime.utcnow()
        assignment.start_odometer = start_odometer
        assignment.updated_at = datetime.utcnow()
        
        # Update vehicle status and odometer
        vehicle_stmt = select(Vehicle).where(Vehicle.id == assignment.vehicle_id)
        vehicle = self.session.exec(vehicle_stmt).first()
        
        if vehicle:
            vehicle.status = VehicleStatus.IN_USE
            vehicle.current_odometer = start_odometer
            vehicle.updated_at = datetime.utcnow()
            self.session.add(vehicle)
        
        self.session.add(assignment)
        self.session.commit()
        self.session.refresh(assignment)
        
        # Send notification
        await self.notification_service.send_assignment_update(
            assignment.vehicle_id,
            assignment.id,
            "started"
        )
        
        return self._create_assignment_response(assignment)
    
    async def complete_assignment(self, assignment_id: uuid.UUID, end_odometer: int) -> AssignmentResponse:
        """Complete an assignment"""
        statement = select(Assignment).where(Assignment.id == assignment_id)
        assignment = self.session.exec(statement).first()
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        if assignment.status != AssignmentStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only active assignments can be completed"
            )
        
        # Validate odometer reading
        if assignment.start_odometer and end_odometer < assignment.start_odometer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End odometer reading cannot be less than start reading"
            )
        
        # Update assignment
        assignment.status = AssignmentStatus.COMPLETED
        assignment.actual_end_date = datetime.utcnow()
        assignment.end_odometer = end_odometer
        assignment.updated_at = datetime.utcnow()
        
        # Update vehicle status and odometer
        vehicle_stmt = select(Vehicle).where(Vehicle.id == assignment.vehicle_id)
        vehicle = self.session.exec(vehicle_stmt).first()
        
        if vehicle:
            vehicle.status = VehicleStatus.AVAILABLE
            vehicle.current_odometer = end_odometer
            vehicle.updated_at = datetime.utcnow()
            self.session.add(vehicle)
        
        self.session.add(assignment)
        self.session.commit()
        self.session.refresh(assignment)
        
        # Send notification
        await self.notification_service.send_assignment_update(
            assignment.vehicle_id,
            assignment.id,
            "completed"
        )
        
        return self._create_assignment_response(assignment)
    
    async def get_vehicle_assignments(
        self, 
        vehicle_id: uuid.UUID, 
        pagination: PaginationParams
    ) -> Tuple[List[AssignmentResponse], int]:
        """Get all assignments for a specific vehicle"""
        # Verify vehicle exists
        vehicle_stmt = select(Vehicle).where(Vehicle.id == vehicle_id)
        vehicle = self.session.exec(vehicle_stmt).first()
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        return await self.get_assignments(pagination, vehicle_id=vehicle_id)
    
    async def _check_assignment_conflicts(
        self, 
        vehicle_id: uuid.UUID, 
        start_date: date, 
        end_date: date,
        exclude_assignment_id: Optional[uuid.UUID] = None
    ) -> List[AssignmentConflict]:
        """Check for assignment conflicts"""
        query = select(Assignment).where(
            Assignment.vehicle_id == vehicle_id,
            Assignment.status.in_([AssignmentStatus.SCHEDULED, AssignmentStatus.ACTIVE]),
            or_(
                and_(Assignment.start_date <= start_date, Assignment.end_date >= start_date),
                and_(Assignment.start_date <= end_date, Assignment.end_date >= end_date),
                and_(Assignment.start_date >= start_date, Assignment.end_date <= end_date)
            )
        )
        
        if exclude_assignment_id:
            query = query.where(Assignment.id != exclude_assignment_id)
        
        conflicting_assignments = self.session.exec(query).all()
        
        conflicts = []
        for assignment in conflicting_assignments:
            conflict_start = max(start_date, assignment.start_date)
            conflict_end = min(end_date, assignment.end_date)
            
            conflicts.append(AssignmentConflict(
                vehicle_id=vehicle_id,
                conflicting_assignment_id=assignment.id,
                conflict_start=conflict_start,
                conflict_end=conflict_end,
                message=f"Conflicts with assignment {assignment.id} from {assignment.start_date} to {assignment.end_date}"
            ))
        
        return conflicts
    
    async def _verify_tour_instance_exists(self, tour_instance_id: uuid.UUID) -> bool:
        """Verify tour instance exists in tour service"""
        try:
            from config import settings
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.tour_service_url}/api/v1/tour-instances/{tour_instance_id}"
                )
                return response.status_code == 200
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to verify tour instance information"
            )
    
    def _create_assignment_response(self, assignment: Assignment) -> AssignmentResponse:
        """Create assignment response with calculated fields"""
        return AssignmentResponse(
            id=assignment.id,
            vehicle_id=assignment.vehicle_id,
            tour_instance_id=assignment.tour_instance_id,
            driver_id=assignment.driver_id,
            status=assignment.status,
            start_date=assignment.start_date,
            end_date=assignment.end_date,
            start_odometer=assignment.start_odometer,
            end_odometer=assignment.end_odometer,
            pickup_location=assignment.pickup_location,
            dropoff_location=assignment.dropoff_location,
            estimated_distance=assignment.estimated_distance,
            notes=assignment.notes,
            special_instructions=assignment.special_instructions,
            actual_start_date=assignment.actual_start_date,
            actual_end_date=assignment.actual_end_date,
            assigned_by=assignment.assigned_by,
            created_at=assignment.created_at,
            updated_at=assignment.updated_at,
            duration_days=assignment.get_duration_days(),
            distance_traveled=assignment.get_distance_traveled(),
            is_active=assignment.is_active()
        )