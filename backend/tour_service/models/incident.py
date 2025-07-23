"""
Incident model for tour issue tracking
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class IncidentType(str, Enum):
    """Incident type enumeration"""
    DELAY = "Delay"
    MEDICAL = "Medical"
    COMPLAINT = "Complaint"
    BREAKDOWN = "Breakdown"
    WEATHER = "Weather"
    SAFETY = "Safety"
    ACCOMMODATION = "Accommodation"
    TRANSPORT = "Transport"
    GUIDE_ISSUE = "Guide Issue"
    CUSTOMER_ISSUE = "Customer Issue"
    OTHER = "Other"


class SeverityLevel(str, Enum):
    """Incident severity level enumeration"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class Incident(SQLModel, table=True):
    """Incident model for tracking tour issues and problems"""
    __tablename__ = "incidents"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Foreign Keys
    tour_instance_id: uuid.UUID = Field(foreign_key="tour_instances.id", index=True)
    reporter_id: uuid.UUID = Field(index=True)  # Staff member who reported
    
    # Incident Details
    incident_type: IncidentType = Field(index=True)
    severity: SeverityLevel = Field(index=True)
    title: str = Field(max_length=255)
    description: str = Field(max_length=2000)
    
    # Location & Time
    location: Optional[str] = Field(default=None, max_length=255)
    day_number: Optional[int] = Field(default=None, ge=1)
    
    # Impact Assessment
    affected_participants: Optional[int] = Field(default=None, ge=0)
    estimated_delay_minutes: Optional[int] = Field(default=None, ge=0)
    financial_impact: Optional[float] = Field(default=None, ge=0)
    
    # Resolution Tracking
    is_resolved: bool = Field(default=False, index=True)
    resolution_description: Optional[str] = Field(default=None, max_length=2000)
    resolved_by: Optional[uuid.UUID] = Field(default=None)
    resolved_at: Optional[datetime] = Field(default=None)
    
    # Follow-up
    requires_follow_up: bool = Field(default=False)
    follow_up_notes: Optional[str] = Field(default=None, max_length=1000)
    escalated_to: Optional[uuid.UUID] = Field(default=None)
    
    # Timestamps
    reported_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    tour_instance: Optional["TourInstance"] = Relationship(back_populates="incidents")
    
    def get_priority_score(self) -> int:
        """Calculate priority score based on severity and type"""
        severity_scores = {
            SeverityLevel.LOW: 1,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.HIGH: 3,
            SeverityLevel.CRITICAL: 4
        }
        
        type_multipliers = {
            IncidentType.MEDICAL: 2,
            IncidentType.SAFETY: 2,
            IncidentType.BREAKDOWN: 1.5,
            IncidentType.COMPLAINT: 1,
            IncidentType.DELAY: 1,
            IncidentType.WEATHER: 1.5,
            IncidentType.ACCOMMODATION: 1,
            IncidentType.TRANSPORT: 1.5,
            IncidentType.GUIDE_ISSUE: 1,
            IncidentType.CUSTOMER_ISSUE: 1,
            IncidentType.OTHER: 1
        }
        
        base_score = severity_scores.get(self.severity, 1)
        multiplier = type_multipliers.get(self.incident_type, 1)
        
        return int(base_score * multiplier)
    
    def is_urgent(self) -> bool:
        """Check if incident requires urgent attention"""
        return (
            self.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL] or
            self.incident_type in [IncidentType.MEDICAL, IncidentType.SAFETY, IncidentType.BREAKDOWN]
        )