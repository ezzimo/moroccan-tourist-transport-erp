"""
Compliance requirement-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from models.compliance_requirement import ComplianceDomain, ComplianceStatus, RequirementType
import uuid


class ComplianceRequirementBase(BaseModel):
    title: str
    description: str
    domain: ComplianceDomain
    requirement_type: RequirementType
    regulatory_body: str
    regulation_reference: Optional[str] = None
    legal_basis: Optional[str] = None
    applies_to_entity: str
    mandatory: bool = True
    responsible_person: Optional[uuid.UUID] = None
    responsible_department: Optional[str] = None
    evidence_required: Optional[str] = None
    compliance_cost: Optional[float] = None
    estimated_effort_hours: Optional[int] = None
    risk_level: Optional[str] = None
    non_compliance_impact: Optional[str] = None
    notes: Optional[str] = None


class ComplianceRequirementCreate(ComplianceRequirementBase):
    requirement_code: str
    renewal_required: bool = False
    renewal_frequency_months: Optional[int] = None
    document_links: Optional[List[str]] = []
    
    @validator('requirement_code')
    def validate_code(cls, v):
        if not v.strip():
            raise ValueError('Requirement code cannot be empty')
        return v.strip().upper()
    
    @validator('renewal_frequency_months')
    def validate_frequency(cls, v, values):
        if values.get('renewal_required') and not v:
            raise ValueError('Renewal frequency is required when renewal is required')
        if v is not None and v < 1:
            raise ValueError('Renewal frequency must be at least 1 month')
        return v


class ComplianceRequirementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[ComplianceDomain] = None
    requirement_type: Optional[RequirementType] = None
    regulatory_body: Optional[str] = None
    regulation_reference: Optional[str] = None
    legal_basis: Optional[str] = None
    applies_to_entity: Optional[str] = None
    mandatory: Optional[bool] = None
    status: Optional[ComplianceStatus] = None
    compliance_date: Optional[date] = None
    expiry_date: Optional[date] = None
    renewal_required: Optional[bool] = None
    renewal_frequency_months: Optional[int] = None
    next_review_date: Optional[date] = None
    responsible_person: Optional[uuid.UUID] = None
    responsible_department: Optional[str] = None
    evidence_required: Optional[str] = None
    document_links: Optional[List[str]] = None
    compliance_cost: Optional[float] = None
    estimated_effort_hours: Optional[int] = None
    risk_level: Optional[str] = None
    non_compliance_impact: Optional[str] = None
    notes: Optional[str] = None
    last_assessment_notes: Optional[str] = None


class ComplianceRequirementResponse(ComplianceRequirementBase):
    id: uuid.UUID
    requirement_code: str
    status: ComplianceStatus
    compliance_date: Optional[date]
    expiry_date: Optional[date]
    renewal_required: bool
    renewal_frequency_months: Optional[int]
    next_review_date: Optional[date]
    document_links: List[str] = []
    last_assessment_notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    last_reviewed_at: Optional[datetime]
    is_expired: bool
    days_until_expiry: Optional[int]
    needs_renewal: bool
    is_overdue_for_review: bool
    next_renewal_date: Optional[date]


class ComplianceAssessment(BaseModel):
    """Schema for compliance assessment"""
    status: ComplianceStatus
    compliance_date: Optional[date] = None
    assessment_notes: str
    evidence_provided: Optional[str] = None
    next_review_date: Optional[date] = None
    
    @validator('compliance_date')
    def validate_compliance_date(cls, v, values):
        if values.get('status') == ComplianceStatus.COMPLIANT and not v:
            raise ValueError('Compliance date is required when status is compliant')
        return v


class ComplianceSummary(BaseModel):
    """Compliance summary for dashboard"""
    total_requirements: int
    by_status: Dict[str, int]
    by_domain: Dict[str, int]
    by_risk_level: Dict[str, int]
    expiring_soon: int
    overdue_reviews: int
    compliance_rate: float


class ComplianceSearch(BaseModel):
    """Compliance search criteria"""
    query: Optional[str] = None
    domain: Optional[ComplianceDomain] = None
    requirement_type: Optional[RequirementType] = None
    status: Optional[ComplianceStatus] = None
    regulatory_body: Optional[str] = None
    responsible_person: Optional[uuid.UUID] = None
    risk_level: Optional[str] = None
    expiring_soon: Optional[bool] = None
    overdue_review: Optional[bool] = None