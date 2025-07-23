"""
Quality audit model for QA management
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
import uuid
import json


class EntityType(str, Enum):
    """Entity type enumeration for audits"""
    TOUR = "Tour"
    FLEET = "Fleet"
    BOOKING = "Booking"
    OFFICE = "Office"
    DRIVER = "Driver"
    GUIDE = "Guide"
    CUSTOMER_SERVICE = "Customer Service"
    SAFETY = "Safety"


class AuditStatus(str, Enum):
    """Audit status enumeration"""
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    OVERDUE = "Overdue"


class AuditType(str, Enum):
    """Audit type enumeration"""
    INTERNAL = "Internal"
    EXTERNAL = "External"
    CUSTOMER_FEEDBACK = "Customer Feedback"
    REGULATORY = "Regulatory"
    FOLLOW_UP = "Follow-up"


class QualityAudit(SQLModel, table=True):
    """Quality audit model for tracking quality assessments"""
    __tablename__ = "quality_audits"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Audit Identification
    audit_number: str = Field(unique=True, max_length=50, index=True)
    title: str = Field(max_length=255)
    
    # Entity Being Audited
    entity_type: EntityType = Field(index=True)
    entity_id: Optional[str] = Field(default=None, max_length=100, index=True)
    entity_name: Optional[str] = Field(default=None, max_length=255)
    
    # Audit Details
    audit_type: AuditType = Field(index=True)
    status: AuditStatus = Field(default=AuditStatus.SCHEDULED, index=True)
    
    # Auditor Information
    auditor_id: uuid.UUID = Field(index=True)
    auditor_name: str = Field(max_length=255)
    external_auditor: Optional[str] = Field(default=None, max_length=255)
    
    # Checklist and Scoring
    checklist: str = Field()  # JSON string containing checklist items
    checklist_responses: Optional[str] = Field(default=None)  # JSON responses
    total_score: Optional[float] = Field(default=None, ge=0, le=100)
    pass_score: float = Field(default=80.0, ge=0, le=100)
    
    # Dates and Scheduling
    scheduled_date: date = Field(index=True)
    start_date: Optional[datetime] = Field(default=None)
    completion_date: Optional[datetime] = Field(default=None)
    
    # Outcomes
    outcome: Optional[str] = Field(default=None, max_length=20)  # Pass, Fail, Conditional
    summary: Optional[str] = Field(default=None, max_length=2000)
    recommendations: Optional[str] = Field(default=None, max_length=2000)
    
    # Follow-up
    requires_follow_up: bool = Field(default=False)
    follow_up_date: Optional[date] = Field(default=None)
    follow_up_audit_id: Optional[uuid.UUID] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    nonconformities: List["NonConformity"] = Relationship(back_populates="audit")
    
    def get_checklist_dict(self) -> Dict[str, Any]:
        """Parse checklist from JSON string"""
        try:
            return json.loads(self.checklist)
        except:
            return {}
    
    def set_checklist_dict(self, checklist: Dict[str, Any]):
        """Set checklist as JSON string"""
        self.checklist = json.dumps(checklist)
    
    def get_responses_dict(self) -> Dict[str, Any]:
        """Parse checklist responses from JSON string"""
        if not self.checklist_responses:
            return {}
        try:
            return json.loads(self.checklist_responses)
        except:
            return {}
    
    def set_responses_dict(self, responses: Dict[str, Any]):
        """Set checklist responses as JSON string"""
        self.checklist_responses = json.dumps(responses) if responses else None
    
    def calculate_score(self) -> float:
        """Calculate audit score from checklist responses"""
        responses = self.get_responses_dict()
        checklist = self.get_checklist_dict()
        
        if not responses or not checklist:
            return 0.0
        
        total_points = 0
        earned_points = 0
        
        for item_id, item_data in checklist.items():
            weight = item_data.get("weight", 1)
            total_points += weight
            
            response = responses.get(item_id, {})
            if response.get("compliant", False):
                earned_points += weight
        
        if total_points == 0:
            return 0.0
        
        return (earned_points / total_points) * 100
    
    def is_passed(self) -> bool:
        """Check if audit passed based on score"""
        if self.total_score is None:
            return False
        return self.total_score >= self.pass_score
    
    def is_overdue(self) -> bool:
        """Check if audit is overdue"""
        if self.status in [AuditStatus.COMPLETED, AuditStatus.CANCELLED]:
            return False
        return date.today() > self.scheduled_date
    
    def get_days_overdue(self) -> int:
        """Get number of days overdue"""
        if not self.is_overdue():
            return 0
        return (date.today() - self.scheduled_date).days