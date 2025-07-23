"""
Training program model for employee development
"""
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Numeric
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
import uuid


class TrainingCategory(str, Enum):
    """Training category enumeration"""
    SAFETY = "Safety"
    TECHNICAL = "Technical"
    CUSTOMER_SERVICE = "Customer Service"
    LEADERSHIP = "Leadership"
    COMPLIANCE = "Compliance"
    LANGUAGE = "Language"
    DRIVING = "Driving"
    FIRST_AID = "First Aid"
    ORIENTATION = "Orientation"
    PROFESSIONAL_DEVELOPMENT = "Professional Development"


class TrainingStatus(str, Enum):
    """Training status enumeration"""
    PLANNED = "Planned"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    POSTPONED = "Postponed"


class DeliveryMethod(str, Enum):
    """Training delivery method enumeration"""
    IN_PERSON = "In-Person"
    ONLINE = "Online"
    HYBRID = "Hybrid"
    ON_THE_JOB = "On-the-Job"
    EXTERNAL = "External"


class TrainingProgram(SQLModel, table=True):
    """Training program model for employee development"""
    __tablename__ = "training_programs"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Program Information
    title: str = Field(max_length=255, index=True)
    description: Optional[str] = Field(default=None, max_length=2000)
    category: TrainingCategory = Field(index=True)
    
    # Training Details
    trainer_name: Optional[str] = Field(default=None, max_length=255)
    trainer_contact: Optional[str] = Field(default=None, max_length=100)
    delivery_method: DeliveryMethod = Field(default=DeliveryMethod.IN_PERSON)
    
    # Schedule
    start_date: date = Field(index=True)
    end_date: date = Field(index=True)
    duration_hours: int = Field(ge=1)
    
    # Location and Logistics
    location: Optional[str] = Field(default=None, max_length=255)
    max_participants: int = Field(default=20, ge=1)
    
    # Cost and Budget
    cost_per_participant: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    total_budget: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    currency: str = Field(default="MAD", max_length=3)
    
    # Requirements
    is_mandatory: bool = Field(default=False)
    prerequisites: Optional[str] = Field(default=None, max_length=500)
    target_departments: Optional[str] = Field(default=None, max_length=200)  # JSON string
    target_positions: Optional[str] = Field(default=None, max_length=200)    # JSON string
    
    # Evaluation
    pass_score: float = Field(default=70.0, ge=0, le=100)
    certificate_template: Optional[str] = Field(default=None, max_length=500)
    
    # Status and Metadata
    status: TrainingStatus = Field(default=TrainingStatus.PLANNED, index=True)
    is_active: bool = Field(default=True, index=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    employee_trainings: List["EmployeeTraining"] = Relationship(back_populates="training_program")
    
    def get_target_departments_list(self) -> List[str]:
        """Parse target departments from JSON string"""
        if not self.target_departments:
            return []
        try:
            import json
            return json.loads(self.target_departments)
        except:
            return []
    
    def set_target_departments_list(self, departments: List[str]):
        """Set target departments as JSON string"""
        import json
        self.target_departments = json.dumps(departments) if departments else None
    
    def get_target_positions_list(self) -> List[str]:
        """Parse target positions from JSON string"""
        if not self.target_positions:
            return []
        try:
            import json
            return json.loads(self.target_positions)
        except:
            return []
    
    def set_target_positions_list(self, positions: List[str]):
        """Set target positions as JSON string"""
        import json
        self.target_positions = json.dumps(positions) if positions else None
    
    def get_duration_days(self) -> int:
        """Get training duration in days"""
        return (self.end_date - self.start_date).days + 1
    
    def calculate_cost_per_hour(self) -> Optional[Decimal]:
        """Calculate cost per hour"""
        if self.cost_per_participant and self.duration_hours > 0:
            return self.cost_per_participant / self.duration_hours
        return None
    
    def is_upcoming(self) -> bool:
        """Check if training is upcoming"""
        return self.start_date > date.today()
    
    def is_ongoing(self) -> bool:
        """Check if training is currently ongoing"""
        today = date.today()
        return self.start_date <= today <= self.end_date