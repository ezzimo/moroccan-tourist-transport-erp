"""
Compliance requirement model for regulatory tracking
"""
from sqlmodel import SQLModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
import uuid


class ComplianceDomain(str, Enum):
    """Compliance domain enumeration"""
    SAFETY = "Safety"
    LABOR = "Labor"
    TAX = "Tax"
    TOURISM = "Tourism"
    TRANSPORT = "Transport"
    ENVIRONMENTAL = "Environmental"
    DATA_PROTECTION = "Data Protection"
    HEALTH = "Health"


class ComplianceStatus(str, Enum):
    """Compliance status enumeration"""
    COMPLIANT = "Compliant"
    NON_COMPLIANT = "Non-Compliant"
    PENDING = "Pending"
    EXPIRED = "Expired"
    NOT_APPLICABLE = "Not Applicable"


class RequirementType(str, Enum):
    """Requirement type enumeration"""
    LICENSE = "License"
    PERMIT = "Permit"
    CERTIFICATION = "Certification"
    INSPECTION = "Inspection"
    TRAINING = "Training"
    DOCUMENTATION = "Documentation"
    PROCEDURE = "Procedure"


class ComplianceRequirement(SQLModel, table=True):
    """Compliance requirement model for regulatory tracking"""
    __tablename__ = "compliance_requirements"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Requirement Identification
    requirement_code: str = Field(unique=True, max_length=50, index=True)
    title: str = Field(max_length=255, index=True)
    description: str = Field(max_length=2000)
    
    # Classification
    domain: ComplianceDomain = Field(index=True)
    requirement_type: RequirementType = Field(index=True)
    
    # Regulatory Information
    regulatory_body: str = Field(max_length=255)
    regulation_reference: Optional[str] = Field(default=None, max_length=255)
    legal_basis: Optional[str] = Field(default=None, max_length=500)
    
    # Applicability
    applies_to_entity: str = Field(max_length=100)  # Company, Fleet, Tours, etc.
    mandatory: bool = Field(default=True)
    
    # Compliance Tracking
    status: ComplianceStatus = Field(default=ComplianceStatus.PENDING, index=True)
    compliance_date: Optional[date] = Field(default=None)
    expiry_date: Optional[date] = Field(default=None, index=True)
    
    # Renewal and Frequency
    renewal_required: bool = Field(default=False)
    renewal_frequency_months: Optional[int] = Field(default=None, ge=1)
    next_review_date: Optional[date] = Field(default=None, index=True)
    
    # Responsibility
    responsible_person: Optional[uuid.UUID] = Field(default=None, index=True)
    responsible_department: Optional[str] = Field(default=None, max_length=100)
    
    # Documentation
    evidence_required: Optional[str] = Field(default=None, max_length=1000)
    document_links: Optional[str] = Field(default=None, max_length=2000)  # JSON array
    
    # Cost and Effort
    compliance_cost: Optional[float] = Field(default=None, ge=0)
    estimated_effort_hours: Optional[int] = Field(default=None, ge=0)
    
    # Risk Assessment
    risk_level: Optional[str] = Field(default=None, max_length=20)  # Low, Medium, High, Critical
    non_compliance_impact: Optional[str] = Field(default=None, max_length=1000)
    
    # Notes and Comments
    notes: Optional[str] = Field(default=None, max_length=2000)
    last_assessment_notes: Optional[str] = Field(default=None, max_length=1000)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    last_reviewed_at: Optional[datetime] = Field(default=None)
    
    def is_expired(self) -> bool:
        """Check if requirement has expired"""
        if not self.expiry_date:
            return False
        return date.today() > self.expiry_date
    
    def days_until_expiry(self) -> Optional[int]:
        """Get days until expiry"""
        if not self.expiry_date:
            return None
        return (self.expiry_date - date.today()).days
    
    def needs_renewal(self, alert_days: int = 60) -> bool:
        """Check if requirement needs renewal within alert period"""
        days_left = self.days_until_expiry()
        if days_left is None:
            return False
        return days_left <= alert_days
    
    def is_overdue_for_review(self) -> bool:
        """Check if requirement is overdue for review"""
        if not self.next_review_date:
            return False
        return date.today() > self.next_review_date
    
    def calculate_next_renewal_date(self) -> Optional[date]:
        """Calculate next renewal date based on frequency"""
        if not self.renewal_required or not self.renewal_frequency_months:
            return None
        
        base_date = self.compliance_date or date.today()
        
        # Add months to base date
        year = base_date.year
        month = base_date.month + self.renewal_frequency_months
        
        # Handle year overflow
        while month > 12:
            month -= 12
            year += 1
        
        try:
            return date(year, month, base_date.day)
        except ValueError:
            # Handle cases like Feb 29 in non-leap years
            return date(year, month, 28)
    
    def get_document_links_list(self) -> List[str]:
        """Parse document links from JSON string"""
        if not self.document_links:
            return []
        try:
            import json
            return json.loads(self.document_links)
        except:
            return []
    
    def set_document_links_list(self, links: List[str]):
        """Set document links as JSON string"""
        import json
        self.document_links = json.dumps(links) if links else None