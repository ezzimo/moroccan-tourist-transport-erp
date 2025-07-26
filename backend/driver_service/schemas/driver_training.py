"""
Driver training-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime, date
from models.driver_training import TrainingType, TrainingStatus
import uuid


class DriverTrainingBase(BaseModel):
    training_type: TrainingType
    training_title: str
    description: Optional[str] = None
    scheduled_date: date
    trainer_name: Optional[str] = None
    training_provider: Optional[str] = None
    location: Optional[str] = None
    duration_hours: Optional[float] = None
    pass_score: float = 70.0
    cost: Optional[float] = None
    currency: str = "MAD"
    mandatory: bool = False


class DriverTrainingCreate(DriverTrainingBase):
    driver_id: uuid.UUID


class DriverTrainingUpdate(BaseModel):
    training_title: Optional[str] = None
    description: Optional[str] = None
    scheduled_date: Optional[date] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_hours: Optional[float] = None
    trainer_name: Optional[str] = None
    training_provider: Optional[str] = None
    location: Optional[str] = None
    status: Optional[TrainingStatus] = None
    attendance_confirmed: Optional[bool] = None
    score: Optional[float] = None
    pass_score: Optional[float] = None
    certificate_number: Optional[str] = None
    certificate_valid_until: Optional[date] = None
    cost: Optional[float] = None
    trainer_feedback: Optional[str] = None
    driver_feedback: Optional[str] = None
    notes: Optional[str] = None


class DriverTrainingResponse(DriverTrainingBase):
    id: uuid.UUID
    driver_id: uuid.UUID
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    status: TrainingStatus
    attendance_confirmed: bool
    score: Optional[float]
    certificate_issued: bool
    certificate_number: Optional[str]
    certificate_valid_until: Optional[date]
    certificate_file_path: Optional[str]
    trainer_feedback: Optional[str]
    driver_feedback: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Computed fields
    has_passed: bool
    is_certificate_valid: bool
    days_until_certificate_expiry: Optional[int]
    training_effectiveness: Optional[str]


class TrainingSummary(BaseModel):
    """Training summary for dashboard"""
    total_trainings: int
    completed_trainings: int
    failed_trainings: int
    scheduled_trainings: int
    certificates_expiring_soon: int
    average_score: Optional[float]
    pass_rate: float
    by_training_type: dict
    compliance_rate: float


class TrainingComplianceReport(BaseModel):
    """Training compliance report"""
    driver_id: uuid.UUID
    driver_name: str
    required_trainings: List[str]
    completed_trainings: List[str]
    missing_trainings: List[str]
    expiring_certificates: List[str]
    compliance_percentage: float
    last_training_date: Optional[date]