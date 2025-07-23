"""
Driver training record model
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, date
from enum import Enum
import uuid


class TrainingType(str, Enum):
    """Training type enumeration"""
    FIRST_AID = "First Aid"
    DEFENSIVE_DRIVING = "Defensive Driving"
    CUSTOMER_SERVICE = "Customer Service"
    LANGUAGE = "Language"
    TOURISM_LAW = "Tourism Law"
    SAFETY_PROCEDURES = "Safety Procedures"
    VEHICLE_MAINTENANCE = "Vehicle Maintenance"
    EMERGENCY_RESPONSE = "Emergency Response"
    CULTURAL_AWARENESS = "Cultural Awareness"
    PROFESSIONAL_DEVELOPMENT = "Professional Development"


class TrainingStatus(str, Enum):
    """Training status enumeration"""
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


class DriverTrainingRecord(SQLModel, table=True):
    """Driver training record model"""
    __tablename__ = "driver_training_records"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Foreign Keys
    driver_id: uuid.UUID = Field(foreign_key="drivers.id", index=True)
    
    # Training Details
    training_type: TrainingType = Field(index=True)
    training_title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    
    # Scheduling
    scheduled_date: date = Field(index=True)
    start_time: Optional[datetime] = Field(default=None)
    end_time: Optional[datetime] = Field(default=None)
    duration_hours: Optional[float] = Field(default=None, ge=0)
    
    # Training Provider
    trainer_name: Optional[str] = Field(default=None, max_length=255)
    training_provider: Optional[str] = Field(default=None, max_length=255)
    location: Optional[str] = Field(default=None, max_length=255)
    
    # Status and Results
    status: TrainingStatus = Field(default=TrainingStatus.SCHEDULED, index=True)
    attendance_confirmed: bool = Field(default=False)
    score: Optional[float] = Field(default=None, ge=0, le=100)
    pass_score: float = Field(default=70.0, ge=0, le=100)
    
    # Certification
    certificate_issued: bool = Field(default=False)
    certificate_number: Optional[str] = Field(default=None, max_length=100)
    certificate_valid_until: Optional[date] = Field(default=None, index=True)
    certificate_file_path: Optional[str] = Field(default=None, max_length=500)
    
    # Cost and Administration
    cost: Optional[float] = Field(default=None, ge=0)
    currency: str = Field(default="MAD", max_length=3)
    mandatory: bool = Field(default=False)
    
    # Feedback and Notes
    trainer_feedback: Optional[str] = Field(default=None, max_length=1000)
    driver_feedback: Optional[str] = Field(default=None, max_length=1000)
    notes: Optional[str] = Field(default=None, max_length=1000)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    driver: Optional["Driver"] = Relationship(back_populates="training_records")
    
    def has_passed(self) -> bool:
        """Check if driver passed the training"""
        return self.score is not None and self.score >= self.pass_score
    
    def is_certificate_valid(self) -> bool:
        """Check if certificate is still valid"""
        if not self.certificate_issued or not self.certificate_valid_until:
            return self.certificate_issued
        return date.today() <= self.certificate_valid_until
    
    def days_until_certificate_expiry(self) -> Optional[int]:
        """Get days until certificate expires"""
        if not self.certificate_valid_until:
            return None
        return (self.certificate_valid_until - date.today()).days
    
    def get_training_effectiveness(self) -> Optional[str]:
        """Get training effectiveness rating"""
        if not self.has_passed():
            return "Ineffective"
        
        if self.score >= 90:
            return "Highly Effective"
        elif self.score >= 80:
            return "Effective"
        else:
            return "Moderately Effective"