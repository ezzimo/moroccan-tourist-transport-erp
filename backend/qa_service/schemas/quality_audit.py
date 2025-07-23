"""
Quality audit-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from models.quality_audit import EntityType, AuditStatus, AuditType
import uuid


class QualityAuditBase(BaseModel):
    title: str
    entity_type: EntityType
    entity_id: Optional[str] = None
    entity_name: Optional[str] = None
    audit_type: AuditType
    auditor_name: str
    external_auditor: Optional[str] = None
    scheduled_date: date
    pass_score: float = 80.0


class QualityAuditCreate(QualityAuditBase):
    auditor_id: uuid.UUID
    checklist: Dict[str, Any]
    
    @validator('pass_score')
    def validate_pass_score(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Pass score must be between 0 and 100')
        return v
    
    @validator('scheduled_date')
    def validate_scheduled_date(cls, v):
        if v < date.today():
            raise ValueError('Scheduled date cannot be in the past')
        return v


class QualityAuditUpdate(BaseModel):
    title: Optional[str] = None
    entity_name: Optional[str] = None
    status: Optional[AuditStatus] = None
    auditor_name: Optional[str] = None
    external_auditor: Optional[str] = None
    scheduled_date: Optional[date] = None
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    checklist_responses: Optional[Dict[str, Any]] = None
    total_score: Optional[float] = None
    outcome: Optional[str] = None
    summary: Optional[str] = None
    recommendations: Optional[str] = None
    requires_follow_up: Optional[bool] = None
    follow_up_date: Optional[date] = None


class QualityAuditResponse(QualityAuditBase):
    id: uuid.UUID
    audit_number: str
    auditor_id: uuid.UUID
    status: AuditStatus
    checklist: Dict[str, Any] = {}
    checklist_responses: Dict[str, Any] = {}
    total_score: Optional[float]
    outcome: Optional[str]
    summary: Optional[str]
    recommendations: Optional[str]
    start_date: Optional[datetime]
    completion_date: Optional[datetime]
    requires_follow_up: bool
    follow_up_date: Optional[date]
    follow_up_audit_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: Optional[datetime]
    is_passed: bool
    is_overdue: bool
    days_overdue: int


class AuditChecklist(BaseModel):
    """Schema for audit checklist"""
    items: Dict[str, Dict[str, Any]]
    
    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('Checklist must have at least one item')
        
        for item_id, item_data in v.items():
            if 'question' not in item_data:
                raise ValueError(f'Item {item_id} must have a question')
            if 'weight' not in item_data:
                item_data['weight'] = 1
        
        return v


class AuditResponse(BaseModel):
    """Schema for audit responses"""
    responses: Dict[str, Dict[str, Any]]
    
    @validator('responses')
    def validate_responses(cls, v):
        for item_id, response in v.items():
            if 'compliant' not in response:
                raise ValueError(f'Response for {item_id} must include compliant field')
            if not isinstance(response['compliant'], bool):
                raise ValueError(f'Compliant field for {item_id} must be boolean')
        
        return v


class AuditSummary(BaseModel):
    """Audit summary for dashboard"""
    total_audits: int
    by_status: Dict[str, int]
    by_entity_type: Dict[str, int]
    by_outcome: Dict[str, int]
    average_score: float
    pass_rate: float
    overdue_audits: int
    upcoming_audits: int


class AuditSearch(BaseModel):
    """Audit search criteria"""
    query: Optional[str] = None
    entity_type: Optional[EntityType] = None
    audit_type: Optional[AuditType] = None
    status: Optional[AuditStatus] = None
    auditor_id: Optional[uuid.UUID] = None
    scheduled_from: Optional[date] = None
    scheduled_to: Optional[date] = None
    outcome: Optional[str] = None
    requires_follow_up: Optional[bool] = None