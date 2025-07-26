"""
Training service for managing training programs and employee training records
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status, UploadFile
from models.training_program import TrainingProgram, TrainingCategory, TrainingStatus
from models.employee_training import EmployeeTraining, AttendanceStatus
from models.employee import Employee
from schemas.training_program import (
    TrainingProgramCreate, TrainingProgramUpdate, TrainingProgramResponse
)
from schemas.employee_training import (
    EmployeeTrainingCreate, EmployeeTrainingUpdate, EmployeeTrainingResponse
)
from utils.upload import process_upload
from utils.notifications import send_training_notification
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)


class TrainingService:
    """Service for handling training programs and employee training operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    # Training Program Management
    
    async def create_training_program(
        self, 
        program_data: TrainingProgramCreate
    ) -> TrainingProgramResponse:
        """Create a new training program
        
        Args:
            program_data: Training program creation data
            
        Returns:
            Created training program
            
        Raises:
            HTTPException: If validation fails
        """
        # Check for duplicate program names
        existing_program = self.session.exec(
            select(TrainingProgram).where(TrainingProgram.title == program_data.title)
        ).first()
        
        if existing_program:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Training program with this title already exists"
            )
        
        # Create training program
        program = TrainingProgram(**program_data.model_dump())
        
        self.session.add(program)
        self.session.commit()
        self.session.refresh(program)
        
        logger.info(f"Created training program {program.id}: {program.title}")
        return self._program_to_response(program)
    
    async def get_training_program(self, program_id: uuid.UUID) -> TrainingProgramResponse:
        """Get training program by ID
        
        Args:
            program_id: Training program UUID
            
        Returns:
            Training program details
            
        Raises:
            HTTPException: If program not found
        """
        program = self.session.get(TrainingProgram, program_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training program not found"
            )
        
        return self._program_to_response(program)
    
    async def get_training_programs(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[TrainingCategory] = None,
        mandatory_only: bool = False,
        active_only: bool = False
    ) -> List[TrainingProgramResponse]:
        """Get training programs with filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            category: Filter by training category
            mandatory_only: Show only mandatory training
            active_only: Show only active training programs
            
        Returns:
            List of training programs
        """
        query = select(TrainingProgram)
        
        # Apply filters
        conditions = []
        
        if category:
            conditions.append(TrainingProgram.category == category)
        
        if mandatory_only:
            conditions.append(TrainingProgram.mandatory == True)
        
        if active_only:
            today = date.today()
            conditions.append(
                and_(
                    TrainingProgram.start_date <= today,
                    TrainingProgram.end_date >= today
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(TrainingProgram.start_date.desc()).offset(skip).limit(limit)
        programs = self.session.exec(query).all()
        
        return [self._program_to_response(program) for program in programs]
    
    async def update_training_program(
        self, 
        program_id: uuid.UUID, 
        program_data: TrainingProgramUpdate
    ) -> TrainingProgramResponse:
        """Update training program
        
        Args:
            program_id: Training program UUID
            program_data: Update data
            
        Returns:
            Updated training program
            
        Raises:
            HTTPException: If program not found
        """
        program = self.session.get(TrainingProgram, program_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training program not found"
            )
        
        # Update fields
        update_data = program_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(program, field, value)
        
        program.updated_at = datetime.utcnow()
        
        self.session.add(program)
        self.session.commit()
        self.session.refresh(program)
        
        logger.info(f"Updated training program {program_id}")
        return self._program_to_response(program)
    
    async def delete_training_program(self, program_id: uuid.UUID) -> dict:
        """Delete training program
        
        Args:
            program_id: Training program UUID
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If program not found or has associated training records
        """
        program = self.session.get(TrainingProgram, program_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training program not found"
            )
        
        # Check for associated employee training records
        training_records = self.session.exec(
            select(EmployeeTraining).where(EmployeeTraining.training_program_id == program_id)
        ).all()
        
        if training_records:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete training program with associated training records"
            )
        
        self.session.delete(program)
        self.session.commit()
        
        logger.info(f"Deleted training program {program_id}")
        return {"message": "Training program deleted successfully"}
    
    # Employee Training Management
    
    async def assign_training(
        self, 
        training_data: EmployeeTrainingCreate
    ) -> EmployeeTrainingResponse:
        """Assign employee to training program
        
        Args:
            training_data: Employee training assignment data
            
        Returns:
            Created employee training record
            
        Raises:
            HTTPException: If validation fails
        """
        # Verify employee exists
        employee = self.session.get(Employee, training_data.employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Verify training program exists
        program = self.session.get(TrainingProgram, training_data.training_program_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training program not found"
            )
        
        # Check for duplicate assignment
        existing_training = self.session.exec(
            select(EmployeeTraining).where(
                and_(
                    EmployeeTraining.employee_id == training_data.employee_id,
                    EmployeeTraining.training_program_id == training_data.training_program_id
                )
            )
        ).first()
        
        if existing_training:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee already assigned to this training program"
            )
        
        # Create employee training record
        employee_training = EmployeeTraining(**training_data.model_dump())
        
        self.session.add(employee_training)
        self.session.commit()
        self.session.refresh(employee_training)
        
        # Send notification to employee
        try:
            await send_training_notification(
                employee_id=str(employee.id),
                training_data={
                    "employee_name": employee.full_name,
                    "training_title": program.title,
                    "start_date": program.start_date.isoformat(),
                    "location": program.location,
                    "trainer": program.trainer
                },
                notification_type="training_assigned"
            )
        except Exception as e:
            logger.error(f"Failed to send training notification: {str(e)}")
        
        logger.info(f"Assigned employee {employee.id} to training {program.id}")
        return self._training_to_response(employee_training)
    
    async def get_employee_training(self, training_id: uuid.UUID) -> EmployeeTrainingResponse:
        """Get employee training record by ID
        
        Args:
            training_id: Employee training UUID
            
        Returns:
            Employee training details
            
        Raises:
            HTTPException: If training record not found
        """
        training = self.session.get(EmployeeTraining, training_id)
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee training record not found"
            )
        
        return self._training_to_response(training)
    
    async def get_employee_trainings(
        self,
        skip: int = 0,
        limit: int = 100,
        employee_id: Optional[uuid.UUID] = None,
        program_id: Optional[uuid.UUID] = None,
        status: Optional[TrainingStatus] = None,
        attendance: Optional[AttendanceStatus] = None
    ) -> List[EmployeeTrainingResponse]:
        """Get employee training records with filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            employee_id: Filter by employee ID
            program_id: Filter by training program ID
            status: Filter by training status
            attendance: Filter by attendance status
            
        Returns:
            List of employee training records
        """
        query = select(EmployeeTraining)
        
        # Apply filters
        conditions = []
        
        if employee_id:
            conditions.append(EmployeeTraining.employee_id == employee_id)
        
        if program_id:
            conditions.append(EmployeeTraining.training_program_id == program_id)
        
        if status:
            conditions.append(EmployeeTraining.status == status)
        
        if attendance:
            conditions.append(EmployeeTraining.attendance_status == attendance)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(EmployeeTraining.created_at.desc()).offset(skip).limit(limit)
        trainings = self.session.exec(query).all()
        
        return [self._training_to_response(training) for training in trainings]
    
    async def update_employee_training(
        self, 
        training_id: uuid.UUID, 
        training_data: EmployeeTrainingUpdate
    ) -> EmployeeTrainingResponse:
        """Update employee training record
        
        Args:
            training_id: Employee training UUID
            training_data: Update data
            
        Returns:
            Updated employee training record
            
        Raises:
            HTTPException: If training record not found
        """
        training = self.session.get(EmployeeTraining, training_id)
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee training record not found"
            )
        
        # Update fields
        update_data = training_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(training, field, value)
        
        training.updated_at = datetime.utcnow()
        
        self.session.add(training)
        self.session.commit()
        self.session.refresh(training)
        
        logger.info(f"Updated employee training {training_id}")
        return self._training_to_response(training)
    
    async def mark_attendance(
        self, 
        training_id: uuid.UUID, 
        attendance_status: AttendanceStatus,
        notes: Optional[str] = None
    ) -> dict:
        """Mark attendance for employee training
        
        Args:
            training_id: Employee training UUID
            attendance_status: Attendance status
            notes: Optional attendance notes
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If training record not found
        """
        training = self.session.get(EmployeeTraining, training_id)
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee training record not found"
            )
        
        training.attendance_status = attendance_status
        training.updated_at = datetime.utcnow()
        
        if notes:
            training.notes = f"{training.notes or ''}\n[{datetime.now()}] Attendance: {attendance_status.value} - {notes}"
        
        # Update status based on attendance
        if attendance_status == AttendanceStatus.PRESENT:
            training.status = TrainingStatus.IN_PROGRESS
        elif attendance_status == AttendanceStatus.ABSENT:
            training.status = TrainingStatus.INCOMPLETE
        
        self.session.add(training)
        self.session.commit()
        
        logger.info(f"Marked attendance for training {training_id}: {attendance_status}")
        return {"message": f"Attendance marked as {attendance_status}"}
    
    async def complete_training(
        self, 
        training_id: uuid.UUID, 
        evaluation_score: float,
        trainer_feedback: Optional[str] = None
    ) -> dict:
        """Complete employee training with evaluation
        
        Args:
            training_id: Employee training UUID
            evaluation_score: Training evaluation score (0-100)
            trainer_feedback: Optional trainer feedback
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If training record not found or invalid score
        """
        training = self.session.get(EmployeeTraining, training_id)
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee training record not found"
            )
        
        if not (0 <= evaluation_score <= 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Evaluation score must be between 0 and 100"
            )
        
        training.evaluation_score = evaluation_score
        training.status = TrainingStatus.COMPLETED
        training.completion_date = date.today()
        training.updated_at = datetime.utcnow()
        
        if trainer_feedback:
            training.notes = f"{training.notes or ''}\n[{datetime.now()}] Trainer feedback: {trainer_feedback}"
        
        self.session.add(training)
        self.session.commit()
        
        logger.info(f"Completed training {training_id} with score {evaluation_score}")
        return {
            "message": "Training completed successfully",
            "evaluation_score": evaluation_score,
            "passed": evaluation_score >= 70  # Assuming 70% is passing grade
        }
    
    async def upload_certificate(
        self, 
        training_id: uuid.UUID, 
        certificate_file: UploadFile
    ) -> dict:
        """Upload training certificate
        
        Args:
            training_id: Employee training UUID
            certificate_file: Certificate file
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If training record not found or upload fails
        """
        training = self.session.get(EmployeeTraining, training_id)
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee training record not found"
            )
        
        if training.status != TrainingStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only upload certificate for completed training"
            )
        
        # Process certificate upload
        try:
            upload_result = await process_upload(certificate_file, "certificates")
            training.certificate_file_path = upload_result["file_path"]
            training.updated_at = datetime.utcnow()
            
            self.session.add(training)
            self.session.commit()
            
            logger.info(f"Uploaded certificate for training {training_id}")
            return {
                "message": "Certificate uploaded successfully",
                "file_path": upload_result["file_path"]
            }
            
        except Exception as e:
            logger.error(f"Certificate upload failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Certificate upload failed: {str(e)}"
            )
    
    async def get_training_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        program_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get training analytics
        
        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            program_id: Filter by specific training program
            
        Returns:
            Training analytics data
        """
        query = select(EmployeeTraining)
        
        # Apply filters
        conditions = []
        if start_date:
            conditions.append(EmployeeTraining.created_at >= start_date)
        if end_date:
            conditions.append(EmployeeTraining.created_at <= end_date)
        if program_id:
            conditions.append(EmployeeTraining.training_program_id == program_id)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        trainings = self.session.exec(query).all()
        
        # Calculate metrics
        total_trainings = len(trainings)
        completed_trainings = len([t for t in trainings if t.status == TrainingStatus.COMPLETED])
        in_progress_trainings = len([t for t in trainings if t.status == TrainingStatus.IN_PROGRESS])
        
        # Completion rate
        completion_rate = completed_trainings / total_trainings * 100 if total_trainings > 0 else 0
        
        # Average score
        completed_with_scores = [t for t in trainings if t.evaluation_score is not None]
        average_score = sum(t.evaluation_score for t in completed_with_scores) / len(completed_with_scores) if completed_with_scores else 0
        
        # Attendance analysis
        attendance_stats = {}
        for status in AttendanceStatus:
            count = len([t for t in trainings if t.attendance_status == status])
            attendance_stats[status.value] = count
        
        # By training program
        program_stats = {}
        for training in trainings:
            program_id = str(training.training_program_id)
            if program_id not in program_stats:
                program_stats[program_id] = {
                    "total": 0,
                    "completed": 0,
                    "average_score": 0
                }
            
            program_stats[program_id]["total"] += 1
            if training.status == TrainingStatus.COMPLETED:
                program_stats[program_id]["completed"] += 1
        
        # Calculate completion rates for each program
        for stats in program_stats.values():
            if stats["total"] > 0:
                stats["completion_rate"] = stats["completed"] / stats["total"] * 100
        
        return {
            "total_trainings": total_trainings,
            "completed_trainings": completed_trainings,
            "in_progress_trainings": in_progress_trainings,
            "completion_rate": completion_rate,
            "average_score": average_score,
            "attendance_stats": attendance_stats,
            "program_stats": program_stats,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    def _program_to_response(self, program: TrainingProgram) -> TrainingProgramResponse:
        """Convert training program model to response schema"""
        return TrainingProgramResponse(
            id=program.id,
            title=program.title,
            description=program.description,
            category=program.category,
            trainer=program.trainer,
            location=program.location,
            start_date=program.start_date,
            end_date=program.end_date,
            cost=program.cost,
            currency=program.currency,
            mandatory=program.mandatory,
            max_participants=program.max_participants,
            created_at=program.created_at,
            updated_at=program.updated_at
        )
    
    def _training_to_response(self, training: EmployeeTraining) -> EmployeeTrainingResponse:
        """Convert employee training model to response schema"""
        return EmployeeTrainingResponse(
            id=training.id,
            employee_id=training.employee_id,
            training_program_id=training.training_program_id,
            attendance_status=training.attendance_status,
            status=training.status,
            evaluation_score=training.evaluation_score,
            completion_date=training.completion_date,
            certificate_file_path=training.certificate_file_path,
            notes=training.notes,
            created_at=training.created_at,
            updated_at=training.updated_at
        )