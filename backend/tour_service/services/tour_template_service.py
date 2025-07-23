"""
Tour template service for managing reusable tour definitions
"""
from sqlmodel import Session, select, and_, or_
from fastapi import HTTPException, status
from models.tour_template import TourTemplate
from schemas.tour_template import (
    TourTemplateCreate, TourTemplateUpdate, TourTemplateResponse, TourTemplateSearch
)
from utils.pagination import PaginationParams, paginate_query
from typing import List, Optional, Tuple
from datetime import datetime
import uuid


class TourTemplateService:
    """Service for handling tour template operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_template(self, template_data: TourTemplateCreate) -> TourTemplateResponse:
        """Create a new tour template"""
        # Check if template title already exists
        statement = select(TourTemplate).where(TourTemplate.title == template_data.title)
        existing_template = self.session.exec(statement).first()
        
        if existing_template:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tour template with this title already exists"
            )
        
        # Create template
        template = TourTemplate(**template_data.model_dump(exclude={"highlights", "inclusions", "exclusions"}))
        
        # Set lists
        if template_data.highlights:
            template.set_highlights_list(template_data.highlights)
        if template_data.inclusions:
            template.set_inclusions_list(template_data.inclusions)
        if template_data.exclusions:
            template.set_exclusions_list(template_data.exclusions)
        
        self.session.add(template)
        self.session.commit()
        self.session.refresh(template)
        
        return TourTemplateResponse.from_model(template)
    
    async def get_template(self, template_id: uuid.UUID) -> TourTemplateResponse:
        """Get tour template by ID"""
        statement = select(TourTemplate).where(TourTemplate.id == template_id)
        template = self.session.exec(statement).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tour template not found"
            )
        
        return TourTemplateResponse.from_model(template)
    
    async def get_templates(
        self, 
        pagination: PaginationParams,
        search: Optional[TourTemplateSearch] = None
    ) -> Tuple[List[TourTemplateResponse], int]:
        """Get list of tour templates with optional search"""
        query = select(TourTemplate)
        
        # Apply search filters
        if search:
            conditions = []
            
            if search.query:
                search_term = f"%{search.query}%"
                conditions.append(
                    or_(
                        TourTemplate.title.ilike(search_term),
                        TourTemplate.description.ilike(search_term),
                        TourTemplate.short_description.ilike(search_term)
                    )
                )
            
            if search.category:
                conditions.append(TourTemplate.category == search.category)
            
            if search.difficulty_level:
                conditions.append(TourTemplate.difficulty_level == search.difficulty_level)
            
            if search.region:
                conditions.append(TourTemplate.default_region.ilike(f"%{search.region}%"))
            
            if search.min_duration:
                conditions.append(TourTemplate.duration_days >= search.min_duration)
            
            if search.max_duration:
                conditions.append(TourTemplate.duration_days <= search.max_duration)
            
            if search.min_participants:
                conditions.append(TourTemplate.max_participants >= search.min_participants)
            
            if search.max_participants:
                conditions.append(TourTemplate.min_participants <= search.max_participants)
            
            if search.is_active is not None:
                conditions.append(TourTemplate.is_active == search.is_active)
            
            if search.is_featured is not None:
                conditions.append(TourTemplate.is_featured == search.is_featured)
            
            if conditions:
                query = query.where(and_(*conditions))
        
        # Order by featured first, then by creation date
        query = query.order_by(TourTemplate.is_featured.desc(), TourTemplate.created_at.desc())
        
        templates, total = paginate_query(self.session, query, pagination)
        
        return [TourTemplateResponse.from_model(template) for template in templates], total
    
    async def update_template(self, template_id: uuid.UUID, template_data: TourTemplateUpdate) -> TourTemplateResponse:
        """Update tour template information"""
        statement = select(TourTemplate).where(TourTemplate.id == template_id)
        template = self.session.exec(statement).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tour template not found"
            )
        
        # Update fields
        update_data = template_data.model_dump(exclude_unset=True, exclude={"highlights", "inclusions", "exclusions"})
        
        for field, value in update_data.items():
            setattr(template, field, value)
        
        # Handle lists separately
        if template_data.highlights is not None:
            template.set_highlights_list(template_data.highlights)
        if template_data.inclusions is not None:
            template.set_inclusions_list(template_data.inclusions)
        if template_data.exclusions is not None:
            template.set_exclusions_list(template_data.exclusions)
        
        template.updated_at = datetime.utcnow()
        
        self.session.add(template)
        self.session.commit()
        self.session.refresh(template)
        
        return TourTemplateResponse.from_model(template)
    
    async def delete_template(self, template_id: uuid.UUID) -> dict:
        """Delete tour template (soft delete by marking inactive)"""
        statement = select(TourTemplate).where(TourTemplate.id == template_id)
        template = self.session.exec(statement).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tour template not found"
            )
        
        # Check if template is being used by any tour instances
        from models.tour_instance import TourInstance
        instances_stmt = select(TourInstance).where(TourInstance.template_id == template_id)
        instances = self.session.exec(instances_stmt).all()
        
        if instances:
            # Soft delete - mark as inactive
            template.is_active = False
            template.updated_at = datetime.utcnow()
            
            self.session.add(template)
            self.session.commit()
            
            return {"message": "Tour template deactivated successfully (has associated tour instances)"}
        else:
            # Hard delete if no instances
            self.session.delete(template)
            self.session.commit()
            
            return {"message": "Tour template deleted successfully"}
    
    async def duplicate_template(self, template_id: uuid.UUID, new_title: str) -> TourTemplateResponse:
        """Duplicate an existing tour template"""
        statement = select(TourTemplate).where(TourTemplate.id == template_id)
        original_template = self.session.exec(statement).first()
        
        if not original_template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tour template not found"
            )
        
        # Check if new title already exists
        title_stmt = select(TourTemplate).where(TourTemplate.title == new_title)
        existing_title = self.session.exec(title_stmt).first()
        
        if existing_title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tour template with this title already exists"
            )
        
        # Create duplicate
        new_template = TourTemplate(
            title=new_title,
            description=original_template.description,
            short_description=original_template.short_description,
            category=original_template.category,
            duration_days=original_template.duration_days,
            difficulty_level=original_template.difficulty_level,
            default_language=original_template.default_language,
            default_region=original_template.default_region,
            starting_location=original_template.starting_location,
            ending_location=original_template.ending_location,
            min_participants=original_template.min_participants,
            max_participants=original_template.max_participants,
            base_price=original_template.base_price,
            highlights=original_template.highlights,
            inclusions=original_template.inclusions,
            exclusions=original_template.exclusions,
            requirements=original_template.requirements,
            is_active=True,
            is_featured=False
        )
        
        self.session.add(new_template)
        self.session.commit()
        self.session.refresh(new_template)
        
        return TourTemplateResponse.from_model(new_template)
    
    async def get_featured_templates(self, limit: int = 10) -> List[TourTemplateResponse]:
        """Get featured tour templates"""
        statement = select(TourTemplate).where(
            TourTemplate.is_featured == True,
            TourTemplate.is_active == True
        ).order_by(TourTemplate.created_at.desc()).limit(limit)
        
        templates = self.session.exec(statement).all()
        
        return [TourTemplateResponse.from_model(template) for template in templates]
    
    async def get_templates_by_category(self, category: str, limit: int = 20) -> List[TourTemplateResponse]:
        """Get tour templates by category"""
        statement = select(TourTemplate).where(
            TourTemplate.category == category,
            TourTemplate.is_active == True
        ).order_by(TourTemplate.created_at.desc()).limit(limit)
        
        templates = self.session.exec(statement).all()
        
        return [TourTemplateResponse.from_model(template) for template in templates]