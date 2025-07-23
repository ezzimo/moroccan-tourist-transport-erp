"""
Template management routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session
from services.template_service import TemplateService
from schemas.template import (
    TemplateCreate, TemplateUpdate, TemplateResponse,
    TemplatePreview, TemplatePreviewResponse, TemplateValidation, TemplateSearch
)
from models.template import TemplateType
from models.notification import NotificationChannel
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import uuid


router = APIRouter(prefix="/templates", tags=["Template Management"])


@router.post("/", response_model=TemplateResponse)
async def create_template(
    template_data: TemplateCreate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("notification", "create", "templates"))
):
    """Create a new notification template"""
    template_service = TemplateService(session)
    return await template_service.create_template(template_data, current_user.user_id)


@router.get("/", response_model=PaginatedResponse[TemplateResponse])
async def get_templates(
    pagination: PaginationParams = Depends(),
    query: Optional[str] = Query(None, description="Search query"),
    type: Optional[TemplateType] = Query(None, description="Filter by template type"),
    channel: Optional[NotificationChannel] = Query(None, description="Filter by channel"),
    language: Optional[str] = Query(None, description="Filter by language"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    created_by: Optional[uuid.UUID] = Query(None, description="Filter by creator"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("notification", "read", "templates"))
):
    """Get list of templates with optional search and filters"""
    template_service = TemplateService(session)
    
    # Build search criteria
    search = None
    if any([query, type, channel, language, is_active is not None, created_by]):
        search = TemplateSearch(
            query=query,
            type=type,
            channel=channel,
            language=language,
            is_active=is_active,
            created_by=created_by
        )
    
    templates, total = await template_service.get_templates(pagination, search)
    
    return PaginatedResponse.create(
        items=templates,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/channel/{channel}", response_model=List[TemplateResponse])
async def get_templates_by_channel(
    channel: NotificationChannel,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("notification", "read", "templates"))
):
    """Get all active templates for a specific channel"""
    template_service = TemplateService(session)
    return await template_service.get_templates_by_channel(channel)


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("notification", "read", "templates"))
):
    """Get template by ID"""
    template_service = TemplateService(session)
    return await template_service.get_template(template_id)


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: uuid.UUID,
    template_data: TemplateUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("notification", "update", "templates"))
):
    """Update template information"""
    template_service = TemplateService(session)
    return await template_service.update_template(template_id, template_data, current_user.user_id)


@router.delete("/{template_id}")
async def delete_template(
    template_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("notification", "delete", "templates"))
):
    """Delete template"""
    template_service = TemplateService(session)
    return await template_service.delete_template(template_id)


@router.post("/preview", response_model=TemplatePreviewResponse)
async def preview_template(
    preview_data: TemplatePreview,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("notification", "read", "templates"))
):
    """Preview template with variables"""
    template_service = TemplateService(session)
    return await template_service.preview_template(preview_data)


@router.get("/{template_id}/validate", response_model=TemplateValidation)
async def validate_template(
    template_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("notification", "read", "templates"))
):
    """Validate template syntax and variables"""
    template_service = TemplateService(session)
    return await template_service.validate_template(template_id)


@router.post("/{template_id}/duplicate", response_model=TemplateResponse)
async def duplicate_template(
    template_id: uuid.UUID,
    new_name: str = Query(..., description="Name for the duplicated template"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("notification", "create", "templates"))
):
    """Duplicate an existing template"""
    template_service = TemplateService(session)
    return await template_service.duplicate_template(template_id, new_name, current_user.user_id)