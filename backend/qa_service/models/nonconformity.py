"""
Non-conformity model for tracking quality issues
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum
import uuid


class Severity(str, Enum):
    """Non-conformity severity enumeration"""
    MINOR = "Minor"
    MAJOR = "Major"
    CRITICAL = "Critical"


class NCStatus(str, Enum):
    """Non-conformity status enumeration"""
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    VERIFIED = "Verified"
    CLOSED = "Closed"
    ESCALATED = "Escalated"


class NonConformity(SQLModel, table=True):
    """Non-conformity model for tracking quality issues and corrective actions"""
    __tablename__ = "nonconformities"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Reference Information
    audit_id: uuid.UUID = Field(foreign_key="quality_audits.id", index=True)
    nc_number: str = Field(unique=True, max_length=50, index=True)
    
    # Issue Description
    title: str = Field(max_length=255)
    description: str = Field(max_length=2000)
    severity: Severity = Field(index=True)
    
    # Root Cause Analysis
    root_cause: Optional[str] = Field(default=None, max_length=1000)
    contributing_factors: Optional[str] = Field(default=None, max_length=1000)
    
    # Corrective Action
    corrective_action: Optional[str] = Field(default=None, max_length=2000)
    preventive_action: Optional[str] = Field(default=None, max_length=2000)
    
    # Responsibility and Dates
    assigned_to: Optional[uuid.UUID] = Field(default=None, index=True)
    due_date: Optional[date] = Field(default=None, index=True)
    target_completion_date: Optional[date] = Field(default=None)
    actual_completion_date: Optional[date] = Field(default=None)
    
    # Status and Progress
    status: NCStatus = Field(default=NCStatus.OPEN, index=True)
    progress_notes: Optional[str] = Field(default=None, max_length=2000)
    
    # Verification
    verified_by: Optional[uuid.UUID] = Field(default=None)
    verification_date: Optional[date] = Field(default=None)
    verification_notes: Optional[str] = Field(default=None, max_length=1000)
    
    # Cost Impact
    estimated_cost: Optional[float] = Field(default=None, ge=0)
    actual_cost: Optional[float] = Field(default=None, ge=0)
    
    # Recurrence Prevention
    is_recurring: bool = Field(default=False)
    previous_nc_id: Optional[uuid.UUID] = Field(default=None)
    
    # Timestamps
    identified_date: date = Field(default_factory=date.today, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    audit: Optional["QualityAudit"] = Relationship(back_populates="nonconformities")
    
    def is_overdue(self) -> bool:
        """Check if corrective action is overdue"""
        if not self.due_date or self.status in [NCStatus.RESOLVED, NCStatus.VERIFIED, NCStatus.CLOSED]:
            return False
        return date.today() > self.due_date
    
    def get_days_overdue(self) -> int:
        """Get number of days overdue"""
        if not self.is_overdue():
            return 0
        return (date.today() - self.due_date).days
    
    def get_age_days(self) -> int:
        """Get age of non-conformity in days"""
        return (date.today() - self.identified_date).days
    
    def is_critical_overdue(self) -> bool:
        """Check if critical non-conformity is overdue"""
        return self.severity == Severity.CRITICAL and self.is_overdue()
    
    def calculate_resolution_time(self) -> Optional[int]:
        """Calculate resolution time in days"""
        if not self.actual_completion_date:
            return None
        return (self.actual_completion_date - self.identified_date).days