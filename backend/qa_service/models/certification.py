"""
Certification model – QA service
"""
from __future__ import annotations

import uuid
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


# ──────────────────────────────── ENUMS ────────────────────────────────
class CertificationType(str, Enum):
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
    ACTIVE = "Active"
    EXPIRED = "Expired"
    SUSPENDED = "Suspended"
    PENDING_RENEWAL = "Pending Renewal"
    PENDING = "Pending"  # ↞ needed by service.create_certification


class CertificationScope(str, Enum):
    COMPANY_WIDE = "Company-wide"
    DEPARTMENT = "Department"
    INDIVIDUAL = "Individual"
    VEHICLE = "Vehicle"
    LOCATION = "Location"


class EntityType(str, Enum):
    """What object does the certificate bind to?"""
    COMPANY = "Company"
    DEPARTMENT = "Department"
    EMPLOYEE = "Employee"
    DRIVER = "Driver"
    VEHICLE = "Vehicle"
    LOCATION = "Location"
    OTHER = "Other"


# ──────────────────────────────── MODEL ────────────────────────────────
class Certification(SQLModel, table=True):
    __tablename__ = "certifications"

    # Keys
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    certificate_number: str = Field(unique=True, max_length=100, index=True)

    # Core data
    name: str = Field(max_length=255, index=True)
    type: CertificationType = Field(index=True)
    scope: CertificationScope = Field(index=True)

    # Binding
    entity_type: Optional[EntityType] = Field(default=None, index=True)
    entity_id: Optional[str] = Field(default=None, max_length=100, index=True)
    entity_name: Optional[str] = Field(default=None, max_length=255)

    # Issuing bodies
    issuing_body: str = Field(max_length=255)
    issuing_authority: Optional[str] = Field(default=None, max_length=255)
    accreditation_body: Optional[str] = Field(default=None, max_length=255)

    # Validity
    issue_date: date = Field(index=True)
    expiry_date: Optional[date] = Field(default=None, index=True)
    effective_date: Optional[date] = Field(default=None)
    status: CertificationStatus = Field(default=CertificationStatus.ACTIVE, index=True)

    # Docs
    document_path: Optional[str] = Field(default=None, max_length=500)
    document_url: Optional[str] = Field(default=None, max_length=500)
    verification_url: Optional[str] = Field(default=None, max_length=500)

    # Renewal / audit
    renewable: bool = Field(default=True)
    renewal_process: Optional[str] = Field(default=None, max_length=1000)
    renewal_cost: Optional[float] = Field(default=None, ge=0)
    renewal_lead_time_days: Optional[int] = Field(default=None, ge=0)
    renewal_notes: Optional[str] = Field(default=None, max_length=1000)
    last_audit_date: Optional[date] = Field(default=None)
    next_audit_date: Optional[date] = Field(default=None)

    # Suspension
    suspension_reason: Optional[str] = Field(default=None, max_length=1000)

    # Book-keeping
    compliance_verified: bool = Field(default=True)
    created_by: Optional[uuid.UUID] = Field(default=None, index=True)
    responsible_manager: Optional[uuid.UUID] = Field(default=None)
    description: Optional[str] = Field(default=None, max_length=1000)
    notes: Optional[str] = Field(default=None, max_length=2000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # ─────────────── Helper methods ───────────────
    def is_expired(self) -> bool:
        return bool(self.expiry_date and date.today() > self.expiry_date)

    def days_until_expiry(self) -> Optional[int]:
        return None if not self.expiry_date else (self.expiry_date - date.today()).days

    def needs_renewal(self, alert_days: int = 60) -> bool:
        return self.renewable and self.days_until_expiry() is not None and \
            self.days_until_expiry() <= alert_days

    def is_valid(self) -> bool:
        return self.status == CertificationStatus.ACTIVE and \
            not self.is_expired() and self.compliance_verified

    def get_validity_period_days(self) -> Optional[int]:
        if not self.expiry_date:
            return None
        start = self.effective_date or self.issue_date
        return (self.expiry_date - start).days

    def calculate_renewal_start_date(self) -> Optional[date]:
        if not (self.renewable and self.expiry_date and self.renewal_lead_time_days):
            return None
        return self.expiry_date - timedelta(days=self.renewal_lead_time_days)
