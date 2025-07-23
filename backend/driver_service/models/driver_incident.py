"""
Driver incident model for tracking incidents involving drivers
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, date
from enum import Enum
import uuid


class IncidentType(str, Enum):
    """Incident type enumeration"""
    ACCIDENT = "Accident"
    COMPLAINT = "Complaint"
    DELAY = "Delay"
    MISCONDUCT = "Misconduct"
    VEHICLE_BREAKDOWN = "Vehicle Breakdown"
    CUSTOMER_DISPUTE = "Customer Dispute"
    SAFETY_VIOLATION = "Safety Violation"
    POLICY_VIOLATION = "Policy Violation"
    MEDICAL_EMERGENCY = "Medical Emergency"
    OTHER = "Other"


class IncidentSeverity(str, Enum):
    """Incident severity enumeration"""
    MINOR = "Minor"
    MODERATE = "Moderate"
    MAJOR = "Major"
    CRITICAL = "Critical"


class IncidentStatus(str, Enum):
    """Incident status enumeration"""
    REPORTED = "Reported"
    UNDER_INVESTIGATION = "Under Investigation"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    ESCALATED = "Escalated"


class DriverIncident(SQLModel, table=True):
    """Driver incident model for tracking incidents involving drivers"""
    __tablename__ = "driver_incidents"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Foreign Keys
    driver_id: uuid.UUID = Field(foreign_key="drivers.id", index=True)
    assignment_id: Optional[uuid.UUID] = Field(default=None, index=True)
    
    # Incident Details
    incident_type: IncidentType = Field(index=True)
    severity: IncidentSeverity = Field(index=True)
    title: str = Field(max_length=255)
    description: str = Field(max_length=2000)
    
    # Location and Time
    incident_date: date = Field(index=True)
    incident_time: Optional[datetime] = Field(default=None)
    location: Optional[str] = Field(default=None, max_length=255)
    
    # Reporting Information
    reported_by: uuid.UUID = Field(index=True)  # User who reported the incident
    reported_at: datetime = Field(default_factory=datetime.utcnow)
    witness_names: Optional[str] = Field(default=None, max_length=500)
    
    # Customer Information (if applicable)
    customer_involved: bool = Field(default=False)
    customer_name: Optional[str] = Field(default=None, max_length=255)
    customer_contact: Optional[str] = Field(default=None, max_length=100)
    
    # Investigation and Resolution
    status: IncidentStatus = Field(default=IncidentStatus.REPORTED, index=True)
    investigated_by: Optional[uuid.UUID] = Field(default=None)
    investigation_notes: Optional[str] = Field(default=None, max_length=2000)
    
    # Resolution Details
    resolution_description: Optional[str] = Field(default=None, max_length=2000)
    corrective_action: Optional[str] = Field(default=None, max_length=1000)
    preventive_measures: Optional[str] = Field(default=None, max_length=1000)
    
    # Financial Impact
    estimated_cost: Optional[float] = Field(default=None, ge=0)
    actual_cost: Optional[float] = Field(default=None, ge=0)
    insurance_claim: bool = Field(default=False)
    claim_number: Optional[str] = Field(default=None, max_length=100)
    
    # Follow-up
    follow_up_required: bool = Field(default=False)
    follow_up_date: Optional[date] = Field(default=None)
    follow_up_notes: Optional[str] = Field(default=None, max_length=1000)
    
    # Documentation
    police_report_filed: bool = Field(default=False)
    police_report_number: Optional[str] = Field(default=None, max_length=100)
    photos_taken: bool = Field(default=False)
    
    # Resolution Tracking
    resolved_at: Optional[datetime] = Field(default=None)
    resolved_by: Optional[uuid.UUID] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    driver: Optional["Driver"] = Relationship(back_populates="incidents")
    
    def get_age_days(self) -> int:
        """Get incident age in days"""
        return (date.today() - self.incident_date).days
    
    def is_overdue(self) -> bool:
        """Check if incident resolution is overdue"""
        if self.status in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]:
            return False
        
        # Critical incidents should be resolved within 24 hours
        if self.severity == IncidentSeverity.CRITICAL:
            return self.get_age_days() > 1
        
        # Major incidents within 3 days
        if self.severity == IncidentSeverity.MAJOR:
            return self.get_age_days() > 3
        
        # Others within 7 days
        return self.get_age_days() > 7
    
    def get_severity_weight(self) -> int:
        """Get numeric weight for severity"""
        weights = {
            IncidentSeverity.MINOR: 1,
            IncidentSeverity.MODERATE: 3,
            IncidentSeverity.MAJOR: 5,
            IncidentSeverity.CRITICAL: 10
        }
        return weights.get(self.severity, 1)
    
    def requires_immediate_attention(self) -> bool:
        """Check if incident requires immediate attention"""
        return (
            self.severity in [IncidentSeverity.MAJOR, IncidentSeverity.CRITICAL] or
            self.incident_type in [IncidentType.ACCIDENT, IncidentType.MEDICAL_EMERGENCY, IncidentType.SAFETY_VIOLATION]
        )