"""
Certification-related Pydantic schemas
"""
from __future__ import annotations
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from models.certification import (
    CertificationType,
    CertificationStatus,
    CertificationScope,
    EntityType,
)
import uuid


# ───────────────────────────── Base ─────────────────────────────
class CertificationBase(BaseModel):
    certificate_number: str
    name: str
    type: CertificationType
    issuing_body: str
    scope: CertificationScope
    issue_date: date

    # Optional
    issuing_authority: Optional[str] = None
    accreditation_body: Optional[str] = None
    entity_type: Optional[EntityType] = None
    entity_id: Optional[str] = None
    entity_name: Optional[str] = None
    expiry_date: Optional[date] = None
    effective_date: Optional[date] = None
    requirements_met: Optional[str] = None
    conditions: Optional[str] = None
    restrictions: Optional[str] = None
    renewable: bool = True
    renewal_process: Optional[str] = None
    renewal_cost: Optional[float] = None
    renewal_lead_time_days: Optional[int] = None
    certificate_holder: Optional[uuid.UUID] = None
    responsible_manager: Optional[uuid.UUID] = None
    description: Optional[str] = None
    notes: Optional[str] = None


# ───────────────────────────── Create ─────────────────────────────
class CertificationCreate(CertificationBase):
    document_path: Optional[str] = None
    document_url: Optional[str] = None
    verification_url: Optional[str] = None

    @validator("certificate_number")
    def _non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Certificate number cannot be empty.")
        return v.strip()

    @validator("expiry_date")
    def _expiry_gt_issue(cls, v: Optional[date], values):
        if v and v <= values["issue_date"]:
            raise ValueError("Expiry date must be after issue date.")
        return v

    @validator("renewal_cost")
    def _renewal_cost_positive(cls, v: Optional[float]):
        if v is not None and v < 0:
            raise ValueError("Renewal cost cannot be negative.")
        return v


# ───────────────────────────── Update ─────────────────────────────
class CertificationUpdate(BaseModel):
    # every field optional
    name: Optional[str] = None
    type: Optional[CertificationType] = None
    issuing_body: Optional[str] = None
    issuing_authority: Optional[str] = None
    accreditation_body: Optional[str] = None
    scope: Optional[CertificationScope] = None
    entity_type: Optional[EntityType] = None
    entity_id: Optional[str] = None
    entity_name: Optional[str] = None
    expiry_date: Optional[date] = None
    effective_date: Optional[date] = None
    status: Optional[CertificationStatus] = None
    document_path: Optional[str] = None
    document_url: Optional[str] = None
    verification_url: Optional[str] = None
    requirements_met: Optional[str] = None
    conditions: Optional[str] = None
    restrictions: Optional[str] = None
    renewable: Optional[bool] = None
    renewal_process: Optional[str] = None
    renewal_cost: Optional[float] = None
    renewal_lead_time_days: Optional[int] = None
    last_audit_date: Optional[date] = None
    next_audit_date: Optional[date] = None
    compliance_verified: Optional[bool] = None
    certificate_holder: Optional[uuid.UUID] = None
    responsible_manager: Optional[uuid.UUID] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    suspension_reason: Optional[str] = None
    renewal_notes: Optional[str] = None


# ───────────────────────────── Read / Response ─────────────────────────────
class CertificationResponse(CertificationBase):
    id: uuid.UUID
    status: CertificationStatus
    document_path: Optional[str]
    document_url: Optional[str]
    verification_url: Optional[str]
    last_audit_date: Optional[date]
    next_audit_date: Optional[date]
    compliance_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]
    is_expired: bool
    days_until_expiry: Optional[int]
    needs_renewal: bool
    is_valid: bool
    validity_period_days: Optional[int]
    renewal_start_date: Optional[date]
    suspension_reason: Optional[str]
    renewal_notes: Optional[str]


class CertificationRenewal(BaseModel):
    """Schema for certification renewal"""
    new_certificate_number: str
    new_issue_date: date
    new_expiry_date: Optional[date] = None
    renewal_cost: Optional[float] = None
    renewal_notes: Optional[str] = None
    document_path: Optional[str] = None
    
    @validator('new_issue_date')
    def validate_issue_date(cls, v):
        if v > date.today():
            raise ValueError('Issue date cannot be in the future')
        return v


class CertificationSummary(BaseModel):
    """Certification summary for dashboard"""
    total_certifications: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    by_scope: Dict[str, int]
    expiring_soon: int
    expired_count: int
    renewal_due: int
    compliance_rate: float


class CertificationSearch(BaseModel):
    """Certification search criteria"""
    query: Optional[str] = None
    type: Optional[CertificationType] = None
    status: Optional[CertificationStatus] = None
    scope: Optional[CertificationScope] = None
    issuing_body: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    certificate_holder: Optional[uuid.UUID] = None
    expiring_soon: Optional[bool] = None
    needs_renewal: Optional[bool] = None