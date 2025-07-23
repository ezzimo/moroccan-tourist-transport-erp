"""
Template service for managing notification templates
"""
from sqlmodel import Session, select, and_, or_
from fastapi import HTTPException, status
from models.template import Template, TemplateType
from models.notification import NotificationChannel
from schemas.template import (
    TemplateCreate, TemplateUpdate, TemplateResponse,
    TemplatePreview, TemplatePreviewResponse, TemplateValidation, TemplateSearch
)
from utils.pagination import PaginationParams, paginate_query
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
import uuid
import re


class TemplateService:
    """Service for handling template operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_template(self, template_data: TemplateCreate, created_by: uuid.UUID) -> TemplateResponse:
        """Create a new template"""
        # Check if template name already exists
        statement = select(Template).where(Template.name == template_data.name)
        existing_template = self.session.exec(statement).first()
        
        if existing_template:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Template name already exists"
            )
        
        # Create template
        template = Template(
            name=template_data.name,
            description=template_data.description,
            type=template_data.type,
            channel=template_data.channel,
            subject=template_data.subject,
            body=template_data.body,
            content_type=template_data.content_type,
            language=template_data.language,
            created_by=created_by
        )
        
        # Set variables and defaults
        if template_data.variables:
            template.set_variables_schema(template_data.variables)
        if template_data.default_values:
            template.set_default_values_dict(template_data.default_values)
        
        # Validate template
        validation = await self._validate_template(template)
        template.is_validated = validation.is_valid
        if not validation.is_valid:
            template.validation_errors = "; ".join(validation.errors)
        
        self.session.add(template)
        self.session.commit()
        self.session.refresh(template)
        
        return self._create_template_response(template)
    
    async def get_template(self, template_id: uuid.UUID) -> TemplateResponse:
        """Get template by ID"""
        statement = select(Template).where(Template.id == template_id)
        template = self.session.exec(statement).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        return self._create_template_response(template)
    
    async def get_templates(
        self, 
        pagination: PaginationParams,
        search: Optional[TemplateSearch] = None
    ) -> Tuple[List[TemplateResponse], int]:
        """Get list of templates with optional search"""
        query = select(Template)
        
        # Apply search filters
        if search:
            conditions = []
            
            if search.query:
                search_term = f"%{search.query}%"
                conditions.append(
                    or_(
                        Template.name.ilike(search_term),
                        Template.description.ilike(search_term),
                        Template.body.ilike(search_term)
                    )
                )
            
            if search.type:
                conditions.append(Template.type == search.type)
            
            if search.channel:
                conditions.append(Template.channel == search.channel)
            
            if search.language:
                conditions.append(Template.language == search.language)
            
            if search.is_active is not None:
                conditions.append(Template.is_active == search.is_active)
            
            if search.created_by:
                conditions.append(Template.created_by == search.created_by)
            
            if conditions:
                query = query.where(and_(*conditions))
        
        # Order by usage and creation date
        query = query.order_by(Template.usage_count.desc(), Template.created_at.desc())
        
        templates, total = paginate_query(self.session, query, pagination)
        
        return [self._create_template_response(t) for t in templates], total
    
    async def update_template(
        self, 
        template_id: uuid.UUID, 
        template_data: TemplateUpdate,
        updated_by: uuid.UUID
    ) -> TemplateResponse:
        """Update template information"""
        statement = select(Template).where(Template.id == template_id)
        template = self.session.exec(statement).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Check name uniqueness if being updated
        if template_data.name and template_data.name != template.name:
            existing_stmt = select(Template).where(Template.name == template_data.name)
            existing_template = self.session.exec(existing_stmt).first()
            if existing_template:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Template name already exists"
                )
        
        # Update fields
        update_data = template_data.model_dump(exclude_unset=True, exclude={"variables", "default_values"})
        
        for field, value in update_data.items():
            setattr(template, field, value)
        
        # Handle variables and defaults separately
        if template_data.variables is not None:
            template.set_variables_schema(template_data.variables)
        if template_data.default_values is not None:
            template.set_default_values_dict(template_data.default_values)
        
        # Increment version and update metadata
        template.version += 1
        template.updated_by = updated_by
        template.updated_at = datetime.utcnow()
        
        # Re-validate template
        validation = await self._validate_template(template)
        template.is_validated = validation.is_valid
        if not validation.is_valid:
            template.validation_errors = "; ".join(validation.errors)
        else:
            template.validation_errors = None
        
        self.session.add(template)
        self.session.commit()
        self.session.refresh(template)
        
        return self._create_template_response(template)
    
    async def delete_template(self, template_id: uuid.UUID) -> dict:
        """Delete template (soft delete by marking inactive)"""
        statement = select(Template).where(Template.id == template_id)
        template = self.session.exec(statement).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Check if template is being used
        from models.notification import Notification
        usage_stmt = select(Notification).where(Notification.template_id == template_id).limit(1)
        usage = self.session.exec(usage_stmt).first()
        
        if usage:
            # Soft delete - mark as inactive
            template.is_active = False
            template.updated_at = datetime.utcnow()
            self.session.add(template)
            self.session.commit()
            
            return {"message": "Template deactivated successfully (has usage history)"}
        else:
            # Hard delete if no usage
            self.session.delete(template)
            self.session.commit()
            
            return {"message": "Template deleted successfully"}
    
    async def preview_template(self, preview_data: TemplatePreview) -> TemplatePreviewResponse:
        """Preview template with variables"""
        statement = select(Template).where(Template.id == preview_data.template_id)
        template = self.session.exec(statement).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Merge variables with recipient info
        variables = preview_data.variables or {}
        if preview_data.recipient_info:
            variables.update(preview_data.recipient_info)
        
        # Validate variables
        validation_errors = template.validate_variables(variables)
        
        # Render template
        try:
            rendered = template.render(variables)
            subject = rendered.get('subject')
            body = rendered.get('body')
        except Exception as e:
            validation_errors.append(f"Rendering error: {str(e)}")
            subject = template.subject
            body = template.body
        
        # Find missing variables
        schema = template.get_variables_schema()
        required_vars = [k for k, v in schema.items() if v.get("required", False)]
        missing_variables = [var for var in required_vars if var not in variables]
        
        return TemplatePreviewResponse(
            subject=subject,
            body=body,
            variables_used=variables,
            missing_variables=missing_variables,
            validation_errors=validation_errors
        )
    
    async def validate_template(self, template_id: uuid.UUID) -> TemplateValidation:
        """Validate template syntax and variables"""
        statement = select(Template).where(Template.id == template_id)
        template = self.session.exec(statement).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        return await self._validate_template(template)
    
    async def get_templates_by_channel(self, channel: NotificationChannel) -> List[TemplateResponse]:
        """Get all active templates for a specific channel"""
        statement = select(Template).where(
            and_(
                Template.channel == channel,
                Template.is_active == True
            )
        ).order_by(Template.name)
        
        templates = self.session.exec(statement).all()
        
        return [self._create_template_response(t) for t in templates]
    
    async def duplicate_template(
        self, 
        template_id: uuid.UUID, 
        new_name: str,
        created_by: uuid.UUID
    ) -> TemplateResponse:
        """Duplicate an existing template"""
        statement = select(Template).where(Template.id == template_id)
        original_template = self.session.exec(statement).first()
        
        if not original_template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Check if new name already exists
        name_stmt = select(Template).where(Template.name == new_name)
        existing_name = self.session.exec(name_stmt).first()
        
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Template name already exists"
            )
        
        # Create duplicate
        new_template = Template(
            name=new_name,
            description=f"Copy of {original_template.name}",
            type=original_template.type,
            channel=original_template.channel,
            subject=original_template.subject,
            body=original_template.body,
            variables=original_template.variables,
            default_values=original_template.default_values,
            content_type=original_template.content_type,
            language=original_template.language,
            created_by=created_by
        )
        
        self.session.add(new_template)
        self.session.commit()
        self.session.refresh(new_template)
        
        return self._create_template_response(new_template)
    
    async def _validate_template(self, template: Template) -> TemplateValidation:
        """Validate template syntax and structure"""
        errors = []
        warnings = []
        variables_found = []
        
        # Find variables in template
        variable_pattern = r'\{(\w+)\}'
        
        # Check subject for variables
        if template.subject:
            subject_vars = re.findall(variable_pattern, template.subject)
            variables_found.extend(subject_vars)
        
        # Check body for variables
        body_vars = re.findall(variable_pattern, template.body)
        variables_found.extend(body_vars)
        
        # Remove duplicates
        variables_found = list(set(variables_found))
        
        # Check against schema
        schema = template.get_variables_schema()
        schema_vars = list(schema.keys())
        
        # Find missing required variables
        required_vars = [k for k, v in schema.items() if v.get("required", False)]
        missing_required = [var for var in required_vars if var not in variables_found]
        
        # Find undefined variables
        undefined_vars = [var for var in variables_found if var not in schema_vars]
        if undefined_vars:
            warnings.append(f"Variables used but not defined in schema: {', '.join(undefined_vars)}")
        
        # Validate content type
        if template.content_type == "html":
            # Basic HTML validation
            if "<script" in template.body.lower():
                errors.append("Script tags are not allowed in HTML templates")
        
        # Check template size
        template_size = len(template.body.encode('utf-8'))
        if template_size > 1024 * 1024:  # 1MB
            errors.append("Template body is too large (max 1MB)")
        
        return TemplateValidation(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            variables_found=variables_found,
            missing_required_variables=missing_required
        )
    
    def _create_template_response(self, template: Template) -> TemplateResponse:
        """Create template response with calculated fields"""
        return TemplateResponse(
            id=template.id,
            name=template.name,
            description=template.description,
            type=template.type,
            channel=template.channel,
            subject=template.subject,
            body=template.body,
            variables=template.get_variables_schema(),
            default_values=template.get_default_values_dict(),
            content_type=template.content_type,
            language=template.language,
            is_active=template.is_active,
            version=template.version,
            usage_count=template.usage_count,
            last_used_at=template.last_used_at,
            is_validated=template.is_validated,
            validation_errors=template.validation_errors,
            created_by=template.created_by,
            updated_by=template.updated_by,
            created_at=template.created_at,
            updated_at=template.updated_at
        )