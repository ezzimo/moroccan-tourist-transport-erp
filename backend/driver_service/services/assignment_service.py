"""
Assignment service for driver assignment operations
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status
from models.driver_assignment import DriverAssignment, AssignmentStatus
from models.driver import Driver
from schemas.driver_assignment import (
    DriverAssignmentCreate, DriverAssignmentUpdate, DriverAssignmentResponse
)
from utils.validation import validate_assignment_conflict, validate_driver_availability
from utils.notifications import send_assignment_notification
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)


class AssignmentService:
    """Service for handling driver assignment operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_assignment(
        self, 
        assignment_data: DriverAssignmentCreate, 
        assigned_by: uuid.UUID
    ) -> DriverAssignmentResponse:
        """Create a new driver assignment
        
        Args:
            assignment_data: Assignment creation data
            assigned_by: User ID who created the assignment
            
        Returns:
            Created assignment
            
        Raises:
            HTTPException: If validation fails or conflicts exist
        """
        # Validate driver exists and is available
        driver = self.session.get(Driver, assignment_data.driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # Check driver availability
        availability = validate_driver_availability(
            self.session,
            str(assignment_data.driver_id),
            assignment_data.start_date,
            assignment_data.end_date
        )
        
        if not availability["available"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Driver not available: {availability['reason']}"
            )
        
        # Create assignment
        assignment = DriverAssignment(
            **assignment_data.model_dump(),
            assigned_by=assigned_by,
            status=AssignmentStatus.ASSIGNED
        )
        
        self.session.add(assignment)
        self.session.commit()
        self.session.refresh(assignment)
        
        # Send notification to driver
        try:
            await send_assignment_notification(
                driver_id=str(assignment.driver_id),
                assignment_data={
                    "driver_name": driver.full_name,
                    "tour_title": assignment.tour_title,
                    "start_date": assignment.start_date.strftime("%Y-%m-%d"),
                    "end_date": assignment.end_date.strftime("%Y-%m-%d"),
                    "pickup_location": assignment.pickup_location,
                    "special_instructions": assignment.special_instructions
                },
                notification_type="new_assignment"
            )
        except Exception as e:
            logger.error(f"Failed to send assignment notification: {str(e)}")
        
        logger.info(f"Created assignment {assignment.id} for driver {driver.full_name}")
        return self._to_response(assignment)
    
    async def get_assignment(self, assignment_id: uuid.UUID) -> DriverAssignmentResponse:
        """Get assignment by ID
        
        Args:
            assignment_id: Assignment UUID
            
        Returns:
            Assignment details
            
        Raises:
            HTTPException: If assignment not found
        """
        assignment = self.session.get(DriverAssignment, assignment_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        return self._to_response(assignment)
    
    async def get_assignments(
        self,
        skip: int = 0,
        limit: int = 100,
        driver_id: Optional[uuid.UUID] = None,
        status: Optional[AssignmentStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        active_only: bool = False
    ) -> List[DriverAssignmentResponse]:
        """Get assignments with filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            driver_id: Filter by driver ID
            status: Filter by assignment status
            start_date: Filter assignments starting from this date
            end_date: Filter assignments ending before this date
            active_only: Show only active assignments
            
        Returns:
            List of assignments
        """
        query = select(DriverAssignment)
        
        # Apply filters
        conditions = []
        
        if driver_id:
            conditions.append(DriverAssignment.driver_id == driver_id)
        
        if status:
            conditions.append(DriverAssignment.status == status)
        
        if start_date:
            conditions.append(DriverAssignment.start_date >= start_date)
        
        if end_date:
            conditions.append(DriverAssignment.end_date <= end_date)
        
        if active_only:
            today = date.today()
            conditions.extend([
                DriverAssignment.status.in_([
                    AssignmentStatus.ASSIGNED, 
                    AssignmentStatus.CONFIRMED, 
                    AssignmentStatus.IN_PROGRESS
                ]),
                DriverAssignment.start_date <= today,
                DriverAssignment.end_date >= today
            ])
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(DriverAssignment.start_date.desc()).offset(skip).limit(limit)
        assignments = self.session.exec(query).all()
        
        return [self._to_response(assignment) for assignment in assignments]
    
    async def get_driver_assignments(
        self,
        driver_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[AssignmentStatus] = None
    ) -> List[DriverAssignmentResponse]:
        """Get assignments for a specific driver
        
        Args:
            driver_id: Driver UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by assignment status
            
        Returns:
            List of driver assignments
        """
        return await self.get_assignments(
            skip=skip,
            limit=limit,
            driver_id=driver_id,
            status=status
        )
    
    async def update_assignment(
        self, 
        assignment_id: uuid.UUID, 
        assignment_data: DriverAssignmentUpdate
    ) -> DriverAssignmentResponse:
        """Update assignment information
        
        Args:
            assignment_id: Assignment UUID
            assignment_data: Update data
            
        Returns:
            Updated assignment
            
        Raises:
            HTTPException: If assignment not found or validation fails
        """
        assignment = self.session.get(DriverAssignment, assignment_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        # Check for date conflicts if dates are being updated
        update_data = assignment_data.model_dump(exclude_unset=True)
        
        if 'start_date' in update_data or 'end_date' in update_data:
            new_start = update_data.get('start_date', assignment.start_date)
            new_end = update_data.get('end_date', assignment.end_date)
            
            conflicts = validate_assignment_conflict(
                self.session,
                str(assignment.driver_id),
                new_start,
                new_end,
                exclude_assignment_id=str(assignment_id)
            )
            
            if conflicts:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "Assignment conflicts detected",
                        "conflicts": conflicts
                    }
                )
        
        # Update fields
        for field, value in update_data.items():
            setattr(assignment, field, value)
        
        assignment.updated_at = datetime.utcnow()
        
        self.session.add(assignment)
        self.session.commit()
        self.session.refresh(assignment)
        
        logger.info(f"Updated assignment {assignment_id}")
        return self._to_response(assignment)
    
    async def confirm_assignment(self, assignment_id: uuid.UUID) -> dict:
        """Confirm an assignment
        
        Args:
            assignment_id: Assignment UUID
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If assignment not found or cannot be confirmed
        """
        assignment = self.session.get(DriverAssignment, assignment_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        if assignment.status != AssignmentStatus.ASSIGNED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot confirm assignment with status {assignment.status}"
            )
        
        assignment.status = AssignmentStatus.CONFIRMED
        assignment.confirmed_at = datetime.utcnow()
        assignment.updated_at = datetime.utcnow()
        
        self.session.add(assignment)
        self.session.commit()
        
        logger.info(f"Confirmed assignment {assignment_id}")
        return {"message": "Assignment confirmed successfully"}
    
    async def start_assignment(self, assignment_id: uuid.UUID) -> dict:
        """Start an assignment
        
        Args:
            assignment_id: Assignment UUID
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If assignment not found or cannot be started
        """
        assignment = self.session.get(DriverAssignment, assignment_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        if assignment.status not in [AssignmentStatus.ASSIGNED, AssignmentStatus.CONFIRMED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot start assignment with status {assignment.status}"
            )
        
        assignment.status = AssignmentStatus.IN_PROGRESS
        assignment.started_at = datetime.utcnow()
        assignment.actual_start_time = datetime.utcnow()
        assignment.updated_at = datetime.utcnow()
        
        self.session.add(assignment)
        self.session.commit()
        
        logger.info(f"Started assignment {assignment_id}")
        return {"message": "Assignment started successfully"}
    
    async def complete_assignment(
        self,
        assignment_id: uuid.UUID,
        customer_rating: Optional[float] = None,
        customer_feedback: Optional[str] = None
    ) -> dict:
        """Complete an assignment
        
        Args:
            assignment_id: Assignment UUID
            customer_rating: Customer rating (1-5)
            customer_feedback: Customer feedback text
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If assignment not found or cannot be completed
        """
        assignment = self.session.get(DriverAssignment, assignment_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        if assignment.status != AssignmentStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot complete assignment with status {assignment.status}"
            )
        
        assignment.status = AssignmentStatus.COMPLETED
        assignment.completed_at = datetime.utcnow()
        assignment.actual_end_time = datetime.utcnow()
        assignment.updated_at = datetime.utcnow()
        
        if customer_rating is not None:
            if not (1 <= customer_rating <= 5):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Customer rating must be between 1 and 5"
                )
            assignment.customer_rating = customer_rating
        
        if customer_feedback:
            assignment.customer_feedback = customer_feedback
        
        self.session.add(assignment)
        
        # Update driver statistics
        driver = self.session.get(Driver, assignment.driver_id)
        if driver:
            driver.total_tours_completed += 1
            if customer_rating:
                # Update performance rating (simple moving average)
                if driver.performance_rating:
                    driver.performance_rating = (driver.performance_rating + customer_rating) / 2
                else:
                    driver.performance_rating = customer_rating
            self.session.add(driver)
        
        self.session.commit()
        
        logger.info(f"Completed assignment {assignment_id}")
        return {"message": "Assignment completed successfully"}
    
    async def cancel_assignment(self, assignment_id: uuid.UUID, reason: Optional[str] = None) -> dict:
        """Cancel an assignment
        
        Args:
            assignment_id: Assignment UUID
            reason: Cancellation reason
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If assignment not found or cannot be cancelled
        """
        assignment = self.session.get(DriverAssignment, assignment_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        if assignment.status in [AssignmentStatus.COMPLETED, AssignmentStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel assignment with status {assignment.status}"
            )
        
        assignment.status = AssignmentStatus.CANCELLED
        assignment.updated_at = datetime.utcnow()
        
        if reason:
            assignment.notes = f"Cancelled: {reason}"
        
        self.session.add(assignment)
        self.session.commit()
        
        logger.info(f"Cancelled assignment {assignment_id}")
        return {"message": "Assignment cancelled successfully"}
    
    async def delete_assignment(self, assignment_id: uuid.UUID) -> dict:
        """Delete an assignment
        
        Args:
            assignment_id: Assignment UUID
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If assignment not found
        """
        assignment = self.session.get(DriverAssignment, assignment_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        self.session.delete(assignment)
        self.session.commit()
        
        logger.info(f"Deleted assignment {assignment_id}")
        return {"message": "Assignment deleted successfully"}
    
    async def check_conflicts(
        self,
        driver_id: uuid.UUID,
        start_date: date,
        end_date: date,
        exclude_assignment_id: Optional[uuid.UUID] = None
    ) -> List[DriverAssignmentResponse]:
        """Check for assignment conflicts
        
        Args:
            driver_id: Driver UUID
            start_date: Assignment start date
            end_date: Assignment end date
            exclude_assignment_id: Assignment ID to exclude from check
            
        Returns:
            List of conflicting assignments
        """
        conflicts = validate_assignment_conflict(
            self.session,
            str(driver_id),
            start_date,
            end_date,
            exclude_assignment_id=str(exclude_assignment_id) if exclude_assignment_id else None
        )
        
        # Convert to full assignment objects
        conflict_assignments = []
        for conflict in conflicts:
            assignment = self.session.get(DriverAssignment, conflict["assignment_id"])
            if assignment:
                conflict_assignments.append(self._to_response(assignment))
        
        return conflict_assignments
    
    async def get_assignment_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        driver_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get assignment performance analytics
        
        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            driver_id: Filter by specific driver
            
        Returns:
            Analytics data
        """
        query = select(DriverAssignment)
        
        # Apply date filters
        conditions = []
        if start_date:
            conditions.append(DriverAssignment.start_date >= start_date)
        if end_date:
            conditions.append(DriverAssignment.end_date <= end_date)
        if driver_id:
            conditions.append(DriverAssignment.driver_id == driver_id)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        assignments = self.session.exec(query).all()
        
        # Calculate metrics
        total_assignments = len(assignments)
        completed_assignments = len([a for a in assignments if a.status == AssignmentStatus.COMPLETED])
        cancelled_assignments = len([a for a in assignments if a.status == AssignmentStatus.CANCELLED])
        
        # Calculate ratings
        rated_assignments = [a for a in assignments if a.customer_rating is not None]
        average_rating = sum(a.customer_rating for a in rated_assignments) / len(rated_assignments) if rated_assignments else None
        
        # Calculate on-time performance
        on_time_assignments = [a for a in assignments if a.is_on_time() == True]
        on_time_rate = len(on_time_assignments) / total_assignments * 100 if total_assignments > 0 else 0
        
        return {
            "total_assignments": total_assignments,
            "completed_assignments": completed_assignments,
            "cancelled_assignments": cancelled_assignments,
            "completion_rate": completed_assignments / total_assignments * 100 if total_assignments > 0 else 0,
            "cancellation_rate": cancelled_assignments / total_assignments * 100 if total_assignments > 0 else 0,
            "average_rating": average_rating,
            "on_time_rate": on_time_rate,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    def _to_response(self, assignment: DriverAssignment) -> DriverAssignmentResponse:
        """Convert assignment model to response schema
        
        Args:
            assignment: Assignment model
            
        Returns:
            Assignment response schema
        """
        return DriverAssignmentResponse(
            id=assignment.id,
            driver_id=assignment.driver_id,
            tour_instance_id=assignment.tour_instance_id,
            vehicle_id=assignment.vehicle_id,
            status=assignment.status,
            start_date=assignment.start_date,
            end_date=assignment.end_date,
            tour_title=assignment.tour_title,
            pickup_location=assignment.pickup_location,
            dropoff_location=assignment.dropoff_location,
            estimated_duration_hours=assignment.estimated_duration_hours,
            special_instructions=assignment.special_instructions,
            assigned_by=assignment.assigned_by,
            assigned_at=assignment.assigned_at,
            confirmed_at=assignment.confirmed_at,
            started_at=assignment.started_at,
            completed_at=assignment.completed_at,
            actual_start_time=assignment.actual_start_time,
            actual_end_time=assignment.actual_end_time,
            customer_rating=assignment.customer_rating,
            customer_feedback=assignment.customer_feedback,
            notes=assignment.notes,
            created_at=assignment.created_at,
            updated_at=assignment.updated_at,
            duration_days=assignment.get_duration_days(),
            is_active=assignment.is_active(),
            is_overdue=assignment.is_overdue(),
            actual_duration_hours=assignment.calculate_actual_duration_hours(),
            is_on_time=assignment.is_on_time()
        )