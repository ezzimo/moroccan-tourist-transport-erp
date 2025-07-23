"""
Quality audit management routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session, get_redis
from services.audit_service import AuditService
from schemas.quality_audit import (
    QualityAuditCreate, QualityAuditUpdate, QualityAuditResponse,
    AuditSummary, AuditSearch, AuditChecklist, AuditResponse
)
from models.quality_audit import EntityType, AuditStatus, AuditType
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import redis
import uuid
from datetime import date


router = APIRouter(prefix="/audits", tags=["Quality Audit Management"])


@router.post("/", response_model=QualityAuditResponse)
async def create_audit(
    audit_data: QualityAuditCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "create", "audits"))
):
    """Create a new quality audit"""
    audit_service = AuditService(session, redis_client)
    return await audit_service.create_audit(audit_data)


@router.get("/", response_model=PaginatedResponse[QualityAuditResponse])
async def get_audits(
    pagination: PaginationParams = Depends(),
    query: Optional[str] = Query(None, description="Search query"),
    entity_type: Optional[EntityType] = Query(None, description="Filter by entity type"),
    audit_type: Optional[AuditType] = Query(None, description="Filter by audit type"),
    status: Optional[AuditStatus] = Query(None, description="Filter by status"),
    auditor_id: Optional[uuid.UUID] = Query(None, description="Filter by auditor"),
    scheduled_from: Optional[str] = Query(None, description="Filter by scheduled date from (YYYY-MM-DD)"),
    scheduled_to: Optional[str] = Query(None, description="Filter by scheduled date to (YYYY-MM-DD)"),
    outcome: Optional[str] = Query(None, description="Filter by outcome"),
    requires_follow_up: Optional[bool] = Query(None, description="Filter by follow-up requirement"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "audits"))
):
    """Get list of audits with optional search and filters"""
    audit_service = AuditService(session, redis_client)
    
    # Build search criteria
    search = None
    if any([query, entity_type, audit_type, status, auditor_id, 
            scheduled_from, scheduled_to, outcome, requires_follow_up is not None]):
        from datetime import datetime
        from fastapi import HTTPException, status as http_status
        
        scheduled_from_parsed = None
        scheduled_to_parsed = None
        
        if scheduled_from:
            try:
                scheduled_from_parsed = datetime.strptime(scheduled_from, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="Invalid scheduled_from format. Use YYYY-MM-DD"
                )
        
        if scheduled_to:
            try:
                scheduled_to_parsed = datetime.strptime(scheduled_to, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="Invalid scheduled_to format. Use YYYY-MM-DD"
                )
        
        search = AuditSearch(
            query=query,
            entity_type=entity_type,
            audit_type=audit_type,
            status=status,
            auditor_id=auditor_id,
            scheduled_from=scheduled_from_parsed,
            scheduled_to=scheduled_to_parsed,
            outcome=outcome,
            requires_follow_up=requires_follow_up
        )
    
    audits, total = await audit_service.get_audits(pagination, search)
    
    return PaginatedResponse.create(
        items=audits,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/summary", response_model=AuditSummary)
async def get_audit_summary(
    days: int = Query(90, ge=1, le=365, description="Number of days for summary"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "audits"))
):
    """Get audit summary statistics"""
    audit_service = AuditService(session, redis_client)
    return await audit_service.get_audit_summary(days)


@router.get("/overdue", response_model=List[QualityAuditResponse])
async def get_overdue_audits(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "audits"))
):
    """Get all overdue audits"""
    audit_service = AuditService(session, redis_client)
    return await audit_service.get_overdue_audits()


@router.get("/{audit_id}", response_model=QualityAuditResponse)
async def get_audit(
    audit_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "audits"))
):
    """Get audit by ID"""
    audit_service = AuditService(session, redis_client)
    return await audit_service.get_audit(audit_id)


@router.put("/{audit_id}", response_model=QualityAuditResponse)
async def update_audit(
    audit_id: uuid.UUID,
    audit_data: QualityAuditUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "update", "audits"))
):
    """Update audit information"""
    audit_service = AuditService(session, redis_client)
    return await audit_service.update_audit(audit_id, audit_data)


@router.post("/{audit_id}/start", response_model=QualityAuditResponse)
async def start_audit(
    audit_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "update", "audits"))
):
    """Start an audit"""
    audit_service = AuditService(session, redis_client)
    return await audit_service.start_audit(audit_id, current_user.user_id)


@router.post("/{audit_id}/complete", response_model=QualityAuditResponse)
async def complete_audit(
    audit_id: uuid.UUID,
    responses: AuditResponse,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "update", "audits"))
):
    """Complete an audit with responses"""
    audit_service = AuditService(session, redis_client)
    return await audit_service.complete_audit(audit_id, responses, current_user.user_id)


@router.delete("/{audit_id}")
async def delete_audit(
    audit_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "delete", "audits"))
):
    """Delete audit"""
    audit_service = AuditService(session, redis_client)
    return await audit_service.delete_audit(audit_id)