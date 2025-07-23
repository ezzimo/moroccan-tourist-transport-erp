"""
Employee training model for tracking training participation
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, date
from enum import Enum
import uuid


class AttendanceStatus(str, Enum):
    """Attendance status enumeration"""
    ENROLLED = "Enrolled"
    ATTENDED = "Attended"
    PARTIALLY_ATTENDED = "Partially Attended"
    ABSENT = "Absent"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"


class CompletionStatus(str, Enum):
    """Completion status enumeration"""
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"
    EXEMPTED = "Exempted"


class EmployeeTraining(SQLModel, table=True):
    """Employee training model for tracking training participation and results"""
    __tablename__ = "employee_trainings"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Foreign Keys
    employee_id: uuid.UUID = Field(foreign_key="employees.id", index=True)
    training_program_id: uuid.UUID = Field(foreign_key="training_programs.id", index=True)
    
    # Enrollment
    enrollment_date: date = Field(default_factory=date.today, index=True)
    enrolled_by: Optional[uuid.UUID] = Field(default=None)  # HR staff who enrolled
    
    # Attendance
    attendance_status: AttendanceStatus = Field(default=AttendanceStatus.ENROLLED, index=True)
    attendance_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    
    # Evaluation and Scores
    pre_assessment_score: Optional[float] = Field(default=None, ge=0, le=100)
    post_assessment_score: Optional[float] = Field(default=None, ge=0, le=100)
    practical_score: Optional[float] = Field(default=None, ge=0, le=100)
    final_score: Optional[float] = Field(default=None, ge=0, le=100)
    
    # Completion
    completion_status: CompletionStatus = Field(default=CompletionStatus.NOT_STARTED, index=True)
    completion_date: Optional[date] = Field(default=None)
    
    # Certification
    certificate_issued: bool = Field(default=False)
    certificate_number: Optional[str] = Field(default=None, max_length=50)
    certificate_file_path: Optional[str] = Field(default=None, max_length=500)
    certificate_expiry_date: Optional[date] = Field(default=None)
    
    # Feedback and Notes
    trainer_feedback: Optional[str] = Field(default=None, max_length=1000)
    employee_feedback: Optional[str] = Field(default=None, max_length=1000)
    employee_rating: Optional[float] = Field(default=None, ge=1, le=5)  # Training rating by employee
    
    # Administrative
    cost_charged: Optional[float] = Field(default=None, ge=0)
    currency: str = Field(default="MAD", max_length=3)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    employee: Optional["Employee"] = Relationship(back_populates="training_records")
    training_program: Optional["TrainingProgram"] = Relationship(back_populates="employee_trainings")
    
    def calculate_final_score(self) -> Optional[float]:
        """Calculate final score from available assessment scores"""
        scores = []
        
        if self.post_assessment_score is not None:
            scores.append(self.post_assessment_score * 0.6)  # 60% weight
        
        if self.practical_score is not None:
            scores.append(self.practical_score * 0.4)  # 40% weight
        
        if not scores:
            return None
        
        return round(sum(scores), 2)
    
    def has_passed(self, pass_score: float = 70.0) -> bool:
        """Check if employee passed the training"""
        if self.final_score is None:
            return False
        return self.final_score >= pass_score
    
    def is_certificate_valid(self) -> bool:
        """Check if certificate is still valid"""
        if not self.certificate_issued or not self.certificate_expiry_date:
            return self.certificate_issued
        return date.today() <= self.certificate_expiry_date
    
    def get_training_effectiveness(self) -> Optional[float]:
        """Calculate training effectiveness (improvement from pre to post)"""
        if self.pre_assessment_score is None or self.post_assessment_score is None:
            return None
        
        if self.pre_assessment_score == 0:
            return 100.0 if self.post_assessment_score > 0 else 0.0
        
        improvement = ((self.post_assessment_score - self.pre_assessment_score) / self.pre_assessment_score) * 100
        return round(improvement, 2)