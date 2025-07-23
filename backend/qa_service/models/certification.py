"""
Certification model for tracking organizational certifications
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, date
from enum import Enum
import uuid


class CertificationType(str, Enum):
    """Certification type enumeration"""
    ISO_9001 = "ISO 9001"
    ISO_14001 = "ISO 14001"
    ISO_45001 = "ISO 45001"
    TOURISM_QUALITY = "Tourism Quality"
    SAFETY_CERTIFICATION = "Safety Certification"
    DRIVER_LICENSE = "Driver License"
    GUIDE_LICENSE = "Guide License"
    BUSINESS_LICENSE = "Business License"
    TRANSPORT_PERMIT = "Transport Permit"
    OTHER = "Other"


class CertificationStatus(str, Enum):
    """Certification status enumeration"""
    ACTIVE = "Active"
    EXPIRED = "Expired"
    SUSPENDED = "Suspended"
    PENDING_RENEWAL = "Pending Renewal"
    CANCELLED = "Cancelled"


class CertificationScope(str, Enum):
    """Certification scope enumeration"""
    COMPANY_WIDE = "Company-wide"
    DEPARTMENT = "Department"
    INDIVIDUAL = "Individual"
    VEHICLE = "Vehicle"
    LOCATION = "Location"


class Certification(SQLModel, table=True):
    """Certification model for tracking organizational and individual certifications"""
    __tablename__ = "certifications"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Certification Identification
    certificate_number: str = Field(unique=True, max_length=100, index=True)
    name: str = Field(max_length=255, index=True)
    type: CertificationType = Field(index=True)
    
    # Issuing Information
    issuing_body: str = Field(max_length=255)
    issuing_authority: Optional[str] = Field(default=None, max_length=255)
    accreditation_body: Optional[str] = Field(default=None, max_length=255)
    
    # Scope and Applicability
    scope: CertificationScope = Field(index=True)
    entity_type: Optional[str] = Field(default=None, max_length=50)  # Employee, Vehicle, etc.
    entity_id: Optional[str] = Field(default=None, max_length=100, index=True)
    entity_name: Optional[str] = Field(default=None, max_length=255)
    
    # Dates and Validity
    issue_date: date = Field(index=True)
    expiry_date: Optional[date] = Field(default=None, index=True)
    effective_date: Optional[date] = Field(default=None)
    
    # Status and Tracking
    status: CertificationStatus = Field(default=CertificationStatus.ACTIVE, index=True)
    
    # Documentation
    document_path: Optional[str] = Field(default=None, max_length=500)
    document_url: Optional[str] = Field(default=None, max_length=500)
    verification_url: Optional[str] = Field(default=None, max_length=500)
    
    # Requirements and Conditions
    requirements_met: Optional[str] = Field(default=None, max_length=2000)
    conditions: Optional[str] = Field(default=None, max_length=1000)
    restrictions: Optional[str] = Field(default=None, max_length=1000)
    
    # Renewal Information
    renewable: bool = Field(default=True)
    renewal_process: Optional[str] = Field(default=None, max_length=1000)
    renewal_cost: Optional[float] = Field(default=None, ge=0)
    renewal_lead_time_days: Optional[int] = Field(default=None, ge=0)
    
    # Audit and Compliance
    last_audit_date: Optional[date] = Field(default=None)
    next_audit_date: Optional[date] = Field(default=None)
    compliance_verified: bool = Field(default=True)
    
    # Responsible Parties
    certificate_holder: Optional[uuid.UUID] = Field(default=None, index=True)
    responsible_manager: Optional[uuid.UUID] = Field(default=None)
    
    # Additional Information
    description: Optional[str] = Field(default=None, max_length=1000)
    notes: Optional[str] = Field(default=None, max_length=2000)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    def is_expired(self) -> bool:
        """Check if certification has expired"""
        if not self.expiry_date:
            return False
        return date.today() > self.expiry_date
    
    def days_until_expiry(self) -> Optional[int]:
        """Get days until expiry"""
        if not self.expiry_date:
            return None
        return (self.expiry_date - date.today()).days
    
    def needs_renewal(self, alert_days: int = 60) -> bool:
        """Check if certification needs renewal within alert period"""
        if not self.renewable:
            return False
        
        days_left = self.days_until_expiry()
        if days_left is None:
            return False
        return days_left <= alert_days
    
    def is_valid(self) -> bool:
        """Check if certification is currently valid"""
        return (
            self.status == CertificationStatus.ACTIVE and
            not self.is_expired() and
            self.compliance_verified
        )
    
    def get_validity_period_days(self) -> Optional[int]:
        """Get total validity period in days"""
        if not self.expiry_date:
            return None
        
        start_date = self.effective_date or self.issue_date
        return (self.expiry_date - start_date).days
    
    def calculate_renewal_start_date(self) -> Optional[date]:
        """Calculate when renewal process should start"""
        if not self.renewable or not self.expiry_date or not self.renewal_lead_time_days:
            return None
        
        from datetime import timedelta
        return self.expiry_date - timedelta(days=self.renewal_lead_time_days)