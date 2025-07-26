"""
Certification management routes
"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from sqlmodel import Session
from database import get_session
from services.certification_service import CertificationService
from schemas.certification import (
    CertificationCreate, CertificationUpdate, CertificationResponse,
    CertificationSummary, CertificationSearch, CertificationRenewal
)
from models.certification import CertificationType, CertificationStatus, CertificationScope
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional, Dict, Any
import redis
import uuid
from datetime import date


router = APIRouter(prefix="/certifications", tags=["Certification Management"])


@router.post("/", response_model=CertificationResponse)
async def create_certification(
    certification_data: CertificationCreate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(
        require_permission(
            "qa", "create", "certifications"
        )
    )
):
    """Create a new certification"""
    certification_service = CertificationService(session)
    return await certification_service.create_certification(certification_data, current_user.id)


@router.post("/upload", response_model=CertificationResponse)
async def create_certification_with_upload(
    certificate_number: str = Form(...),
    name: str = Form(...),
    type: CertificationType = Form(...),
    issuing_body: str = Form(...),
    scope: CertificationScope = Form(...),
    issue_date: str = Form(...),
    expiry_date: Optional[str] = Form(None),
    entity_type: Optional[str] = Form(None),
    entity_id: Optional[str] = Form(None),
    entity_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    certificate_file: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("qa", "create", "certifications"))
):
    """Create certification with file upload"""
    certification_service = CertificationService(session)
    
    # Parse dates
    from datetime import datetime
    from fastapi import HTTPException, status
    
    try:
        issue_date_parsed = datetime.strptime(issue_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid issue_date format. Use YYYY-MM-DD"
        )
    
    expiry_date_parsed = None
    if expiry_date:
        try:
            expiry_date_parsed = datetime.strptime(expiry_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid expiry_date format. Use YYYY-MM-DD"
            )
    
    # Create certification data
    certification_data = CertificationCreate(
        certificate_number=certificate_number,
        name=name,
        type=type,
        issuing_body=issuing_body,
        scope=scope,
        issue_date=issue_date_parsed,
        expiry_date=expiry_date_parsed,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name,
        description=description
    )
    
    return await certification_service.create_certification_with_file(
        certification_data, certificate_file, current_user.id
    )


@router.get("/", response_model=PaginatedResponse[CertificationResponse])
async def get_certifications(
    pagination: PaginationParams = Depends(),
    query: Optional[str] = Query(None, description="Search query"),
    type: Optional[CertificationType] = Query(None, description="Filter by type"),
    status: Optional[CertificationStatus] = Query(None, description="Filter by status"),
    scope: Optional[CertificationScope] = Query(None, description="Filter by scope"),
    issuing_body: Optional[str] = Query(None, description="Filter by issuing body"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    certificate_holder: Optional[uuid.UUID] = Query(None, description="Filter by holder"),
    expiring_soon: Optional[bool] = Query(None, description="Show expiring certifications"),
    needs_renewal: Optional[bool] = Query(None, description="Show certifications needing renewal"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "certifications"))
):
    """Get list of certifications with optional search and filters"""
    certification_service = CertificationService(session)
    
    # Build search criteria
    search = None
    if any([query, type, status, scope, issuing_body, entity_type, entity_id, 
            certificate_holder, expiring_soon is not None, needs_renewal is not None]):
        search = CertificationSearch(
            query=query,
            type=type,
            status=status,
            scope=scope,
            issuing_body=issuing_body,
            entity_type=entity_type,
            entity_id=entity_id,
            certificate_holder=certificate_holder,
            expiring_soon=expiring_soon,
            needs_renewal=needs_renewal
        )

    certifications, total = await certification_service.get_certifications(
        pagination,
        search,
        current_user.id,
    )

    return PaginatedResponse.create(
        items=certifications,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/summary", response_model=CertificationSummary)
async def get_certification_summary(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "certifications"))
):
    """Get certification summary statistics"""
    certification_service = CertificationService(session)
    return await certification_service.get_certification_summary(current_user.id)


@router.get("/expiring", response_model=List[CertificationResponse])
async def get_expiring_certifications(
    days_ahead: int = Query(60, ge=1, le=365, description="Days ahead to check"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "certifications"))
):
    """Get certifications expiring within specified days"""
    certification_service = CertificationService(session)
    return await certification_service.get_expiring_certifications(days_ahead, current_user.id)


@router.get("/{certification_id}", response_model=CertificationResponse)
async def get_certification(
    certification_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "certifications"))
):
    """Get certification by ID"""
    certification_service = CertificationService(session)
    return await certification_service.get_certification(certification_id, current_user.id)


@router.put("/{certification_id}", response_model=CertificationResponse)
async def update_certification(
    certification_id: uuid.UUID,
    certification_data: CertificationUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("qa", "update", "certifications"))
):
    """Update certification information"""
    certification_service = CertificationService(sessiont)
    return await certification_service.update_certification(
        certification_id,
        certification_data,
        current_user.id,
    )


@router.post("/{certification_id}/renew", response_model=CertificationResponse)
async def renew_certification(
    certification_id: uuid.UUID,
    renewal_data: CertificationRenewal,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(
        require_permission(
            "qa",
            "update",
            "certifications",
        )
    )
):
    """Renew a certification"""
    certification_service = CertificationService(session)
    return await certification_service.renew_certification(
        certification_id,
        renewal_data,
        current_user.id
    )


@router.delete("/{certification_id}")
async def delete_certification(
    certification_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(
        require_permission(
            "qa",
            "delete",
            "certifications",
        )
    )
):
    """Delete certification"""
    certification_service = CertificationService(session)
    return await certification_service.delete_certification(
        certification_id, current_user.id
    )


@router.get(
    "/entity/{entity_type}/{entity_id}",
    response_model=List[CertificationResponse],
)
async def get_entity_certifications(
    entity_type: str,
    entity_id: str,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(
        require_permission(
            "qa",
            "read",
            "certifications",
        )
    )
):
    """Get all certifications for a specific entity"""
    certification_service = CertificationService(session)
    return await certification_service.get_entity_certifications(
        entity_type,
        entity_id,
        current_user.id,
    )
