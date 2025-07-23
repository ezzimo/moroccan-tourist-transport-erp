"""
Template-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime
from models.template import TemplateType
from models.notification import NotificationChannel
import uuid


class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: TemplateType
    channel: NotificationChannel
    subject: Optional[str] = None
    body: str
    content_type: str = "text"
    language: str = "en"


class TemplateCreate(TemplateBase):
    variables: Optional[Dict[str, Any]] = None
    default_values: Optional[Dict[str, Any]] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Template name cannot be empty')
        return v.strip()
    
    @validator('body')
    def validate_body(cls, v):
        if not v.strip():
            raise ValueError('Template body cannot be empty')
        return v
    
    @validator('content_type')
    def validate_content_type(cls, v):
        allowed_types = ["text", "html", "markdown"]
        if v not in allowed_types:
            raise ValueError(f'Content type must be one of {allowed_types}')
        return v


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[TemplateType] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    default_values: Optional[Dict[str, Any]] = None
    content_type: Optional[str] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None


class TemplateResponse(TemplateBase):
    id: uuid.UUID
    variables: Dict[str, Any] = {}
    default_values: Dict[str, Any] = {}
    is_active: bool
    version: int
    usage_count: int
    last_used_at: Optional[datetime]
    is_validated: bool
    validation_errors: Optional[str]
    created_by: Optional[uuid.UUID]
    updated_by: Optional[uuid.UUID]
    created_at: datetime
    updated_at: Optional[datetime]


class TemplatePreview(BaseModel):
    """Schema for template preview"""
    template_id: uuid.UUID
    variables: Optional[Dict[str, Any]] = None
    recipient_info: Optional[Dict[str, str]] = None


class TemplatePreviewResponse(BaseModel):
    """Template preview response"""
    subject: Optional[str]
    body: str
    variables_used: Dict[str, Any]
    missing_variables: List[str] = []
    validation_errors: List[str] = []


class TemplateValidation(BaseModel):
    """Template validation response"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    variables_found: List[str] = []
    missing_required_variables: List[str] = []


class TemplateSearch(BaseModel):
    """Template search criteria"""
    query: Optional[str] = None
    type: Optional[TemplateType] = None
    channel: Optional[NotificationChannel] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None
    created_by: Optional[uuid.UUID] = None