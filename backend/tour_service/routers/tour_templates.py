"""
Tour template management routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session
from services.tour_template_service import TourTemplateService
from schemas.tour_template import (
    TourTemplateCreate, TourTemplateUpdate, TourTemplateResponse, TourTemplateSearch
)
from models.tour_template import TourCategory, DifficultyLevel
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import uuid


router = APIRouter(prefix="/tour-templates", tags=["Tour Templates"])


@router.post("/", response_model=TourTemplateResponse)
async def create_tour_template(
    template_data: TourTemplateCreate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("tours", "create", "templates"))
):
    """Create a new tour template"""
    template_service = TourTemplateService(session)
    return await template_service.create_template(template_data)


@router.get("/", response_model=PaginatedResponse[TourTemplateResponse])
async def get_tour_templates(
    pagination: PaginationParams = Depends(),
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[TourCategory] = Query(None, description="Filter by category"),
    difficulty_level: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty"),
    region: Optional[str] = Query(None, description="Filter by region"),
    min_duration: Optional[int] = Query(None, description="Minimum duration in days"),
    max_duration: Optional[int] = Query(None, description="Maximum duration in days"),
    min_participants: Optional[int] = Query(None, description="Minimum participants"),
    max_participants: Optional[int] = Query(None, description="Maximum participants"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    is_featured: Optional[bool] = Query(None, description="Filter by featured status"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("tours", "read", "templates"))
):
    """Get list of tour templates with optional search and filters"""
    template_service = TourTemplateService(session)
    
    # Build search criteria
    search = None
    if any([query, category, difficulty_level, region, min_duration, max_duration, 
            min_participants, max_participants, is_active is not None, is_featured is not None]):
        search = TourTemplateSearch(
            query=query,
            category=category,
            difficulty_level=difficulty_level,
            region=region,
            min_duration=min_duration,
            max_duration=max_duration,
            min_participants=min_participants,
            max_participants=max_participants,
            is_active=is_active,
            is_featured=is_featured
        )
    
    templates, total = await template_service.get_templates(pagination, search)
    
    return PaginatedResponse.create(
        items=templates,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/featured", response_model=List[TourTemplateResponse])
async def get_featured_templates(
    limit: int = Query(10, ge=1, le=50, description="Number of featured templates to return"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("tours", "read", "templates"))
):
    """Get featured tour templates"""
    template_service = TourTemplateService(session)
    return await template_service.get_featured_templates(limit)


@router.get("/category/{category}", response_model=List[TourTemplateResponse])
async def get_templates_by_category(
    category: TourCategory,
    limit: int = Query(20, ge=1, le=100, description="Number of templates to return"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("tours", "read", "templates"))
):
    """Get tour templates by category"""
    template_service = TourTemplateService(session)
    return await template_service.get_templates_by_category(category.value, limit)


@router.get("/{template_id}", response_model=TourTemplateResponse)
async def get_tour_template(
    template_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("tours", "read", "templates"))
):
    """Get tour template by ID"""
    template_service = TourTemplateService(session)
    return await template_service.get_template(template_id)


@router.put("/{template_id}", response_model=TourTemplateResponse)
async def update_tour_template(
    template_id: uuid.UUID,
    template_data: TourTemplateUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("tours", "update", "templates"))
):
    """Update tour template information"""
    template_service = TourTemplateService(session)
    return await template_service.update_template(template_id, template_data)


@router.delete("/{template_id}")
async def delete_tour_template(
    template_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("tours", "delete", "templates"))
):
    """Delete tour template"""
    template_service = TourTemplateService(session)
    return await template_service.delete_template(template_id)


@router.post("/{template_id}/duplicate", response_model=TourTemplateResponse)
async def duplicate_tour_template(
    template_id: uuid.UUID,
    new_title: str = Query(..., description="Title for the duplicated template"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("tours", "create", "templates"))
):
    """Duplicate an existing tour template"""
    template_service = TourTemplateService(session)
    return await template_service.duplicate_template(template_id, new_title)