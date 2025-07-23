"""
Compliance requirement management routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session, get_redis
from services.compliance_service import ComplianceService
from schemas.compliance_requirement import (
    ComplianceRequirementCreate, ComplianceRequirementUpdate, ComplianceRequirementResponse,
    ComplianceSummary, ComplianceSearch, ComplianceAssessment
)
from models.compliance_requirement import ComplianceDomain, ComplianceStatus, RequirementType
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import redis
import uuid


router = APIRouter(prefix="/compliance", tags=["Compliance Management"])


@router.post("/", response_model=ComplianceRequirementResponse)
async def create_compliance_requirement(
    requirement_data: ComplianceRequirementCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "create", "compliance"))
):
    """Create a new compliance requirement"""
    compliance_service = ComplianceService(session, redis_client)
    return await compliance_service.create_requirement(requirement_data)


@router.get("/", response_model=PaginatedResponse[ComplianceRequirementResponse])
async def get_compliance_requirements(
    pagination: PaginationParams = Depends(),
    query: Optional[str] = Query(None, description="Search query"),
    domain: Optional[ComplianceDomain] = Query(None, description="Filter by domain"),
    requirement_type: Optional[RequirementType] = Query(None, description="Filter by type"),
    status: Optional[ComplianceStatus] = Query(None, description="Filter by status"),
    regulatory_body: Optional[str] = Query(None, description="Filter by regulatory body"),
    responsible_person: Optional[uuid.UUID] = Query(None, description="Filter by responsible person"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    expiring_soon: Optional[bool] = Query(None, description="Show expiring requirements"),
    overdue_review: Optional[bool] = Query(None, description="Show overdue reviews"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "compliance"))
):
    """Get list of compliance requirements with optional search and filters"""
    compliance_service = ComplianceService(session, redis_client)
    
    # Build search criteria
    search = None
    if any([query, domain, requirement_type, status, regulatory_body, 
            responsible_person, risk_level, expiring_soon is not None, overdue_review is not None]):
        search = ComplianceSearch(
            query=query,
            domain=domain,
            requirement_type=requirement_type,
            status=status,
            regulatory_body=regulatory_body,
            responsible_person=responsible_person,
            risk_level=risk_level,
            expiring_soon=expiring_soon,
            overdue_review=overdue_review
        )
    
    requirements, total = await compliance_service.get_requirements(pagination, search)
    
    return PaginatedResponse.create(
        items=requirements,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/summary", response_model=ComplianceSummary)
async def get_compliance_summary(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "compliance"))
):
    """Get compliance summary statistics"""
    compliance_service = ComplianceService(session, redis_client)
    return await compliance_service.get_compliance_summary()


@router.get("/expiring", response_model=List[ComplianceRequirementResponse])
async def get_expiring_requirements(
    days_ahead: int = Query(60, ge=1, le=365, description="Days ahead to check"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "compliance"))
):
    """Get requirements expiring within specified days"""
    compliance_service = ComplianceService(session, redis_client)
    return await compliance_service.get_expiring_requirements(days_ahead)


@router.get("/{requirement_id}", response_model=ComplianceRequirementResponse)
async def get_compliance_requirement(
    requirement_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "compliance"))
):
    """Get compliance requirement by ID"""
    compliance_service = ComplianceService(session, redis_client)
    return await compliance_service.get_requirement(requirement_id)


@router.put("/{requirement_id}", response_model=ComplianceRequirementResponse)
async def update_compliance_requirement(
    requirement_id: uuid.UUID,
    requirement_data: ComplianceRequirementUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "update", "compliance"))
):
    """Update compliance requirement information"""
    compliance_service = ComplianceService(session, redis_client)
    return await compliance_service.update_requirement(requirement_id, requirement_data)


@router.post("/{requirement_id}/assess", response_model=ComplianceRequirementResponse)
async def assess_compliance(
    requirement_id: uuid.UUID,
    assessment: ComplianceAssessment,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "assess", "compliance"))
):
    """Assess compliance status for a requirement"""
    compliance_service = ComplianceService(session, redis_client)
    return await compliance_service.assess_compliance(requirement_id, assessment, current_user.user_id)


@router.delete("/{requirement_id}")
async def delete_compliance_requirement(
    requirement_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "delete", "compliance"))
):
    """Delete compliance requirement"""
    compliance_service = ComplianceService(session, redis_client)
    return await compliance_service.delete_requirement(requirement_id)


@router.get("/domain/{domain}", response_model=List[ComplianceRequirementResponse])
async def get_requirements_by_domain(
    domain: ComplianceDomain,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "compliance"))
):
    """Get all requirements for a specific domain"""
    compliance_service = ComplianceService(session, redis_client)
    return await compliance_service.get_requirements_by_domain(domain)