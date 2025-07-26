"""
Employee training-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from models.employee_training import AttendanceStatus, CompletionStatus
import uuid


class EmployeeTrainingBase(BaseModel):
    employee_id: uuid.UUID
    training_program_id: uuid.UUID
    enrollment_date: date = date.today()
    enrolled_by: Optional[uuid.UUID] = None


class EmployeeTrainingCreate(EmployeeTrainingBase):
    pass


class EmployeeTrainingUpdate(BaseModel):
    attendance_status: Optional[AttendanceStatus] = None
    attendance_percentage: Optional[float] = None
    pre_assessment_score: Optional[float] = None
    post_assessment_score: Optional[float] = None
    practical_score: Optional[float] = None
    final_score: Optional[float] = None
    completion_status: Optional[CompletionStatus] = None
    completion_date: Optional[date] = None
    certificate_issued: Optional[bool] = None
    certificate_number: Optional[str] = None
    certificate_expiry_date: Optional[date] = None
    trainer_feedback: Optional[str] = None
    employee_feedback: Optional[str] = None
    employee_rating: Optional[float] = None
    cost_charged: Optional[float] = None
    
    @validator('attendance_percentage', 'pre_assessment_score', 'post_assessment_score', 
              'practical_score', 'final_score')
    def validate_scores(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Scores must be between 0 and 100')
        return v
    
    @validator('employee_rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Employee rating must be between 1 and 5')
        return v


class EmployeeTrainingResponse(EmployeeTrainingBase):
    id: uuid.UUID
    attendance_status: AttendanceStatus
    attendance_percentage: Optional[float]
    pre_assessment_score: Optional[float]
    post_assessment_score: Optional[float]
    practical_score: Optional[float]
    final_score: Optional[float]
    completion_status: CompletionStatus
    completion_date: Optional[date]
    certificate_issued: bool
    certificate_number: Optional[str]
    certificate_file_path: Optional[str]
    certificate_expiry_date: Optional[date]
    trainer_feedback: Optional[str]
    employee_feedback: Optional[str]
    employee_rating: Optional[float]
    cost_charged: Optional[float]
    currency: str
    created_at: datetime
    updated_at: Optional[datetime]
    calculated_final_score: Optional[float]
    has_passed: bool
    is_certificate_valid: bool
    training_effectiveness: Optional[float]


class EmployeeTrainingWithDetails(EmployeeTrainingResponse):
    """Employee training response with employee and program details"""
    employee_name: str
    employee_id_number: str
    training_title: str
    training_category: str
    training_duration_hours: int
    training_start_date: date
    training_end_date: date


class TrainingEnrollment(BaseModel):
    """Schema for enrolling employees in training"""
    employee_ids: List[uuid.UUID]
    training_program_id: uuid.UUID
    enrollment_date: date = date.today()
    notes: Optional[str] = None


class TrainingCompletion(BaseModel):
    """Schema for marking training as completed"""
    completion_date: date
    final_score: Optional[float] = None
    attendance_percentage: Optional[float] = None
    trainer_feedback: Optional[str] = None
    issue_certificate: bool = True
    certificate_expiry_months: Optional[int] = None


class CertificateRequest(BaseModel):
    """Schema for certificate generation"""
    employee_training_id: uuid.UUID
    certificate_template: Optional[str] = None
    expiry_months: Optional[int] = 24  # Default 2 years
    notes: Optional[str] = None