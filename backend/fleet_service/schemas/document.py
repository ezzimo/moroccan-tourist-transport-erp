"""
Document-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime, date
from models.document import DocumentType
import uuid


class DocumentBase(BaseModel):
    document_type: DocumentType
    title: str
    description: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    issuing_authority: Optional[str] = None
    document_number: Optional[str] = None


class DocumentCreate(DocumentBase):
    vehicle_id: uuid.UUID
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    uploaded_by: Optional[uuid.UUID] = None
    
    @validator('file_size')
    def validate_file_size(cls, v):
        max_size = 10 * 1024 * 1024  # 10MB
        if v > max_size:
            raise ValueError(f'File size must not exceed {max_size} bytes')
        return v
    
    @validator('expiry_date')
    def validate_expiry_date(cls, v, values):
        if v and 'issue_date' in values and values['issue_date'] and v <= values['issue_date']:
            raise ValueError('Expiry date must be after issue date')
        return v


class DocumentUpdate(BaseModel):
    document_type: Optional[DocumentType] = None
    title: Optional[str] = None
    description: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    issuing_authority: Optional[str] = None
    document_number: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    verified_by: Optional[uuid.UUID] = None


class DocumentResponse(DocumentBase):
    id: uuid.UUID
    vehicle_id: uuid.UUID
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    is_active: bool
    is_verified: bool
    uploaded_at: datetime
    uploaded_by: Optional[uuid.UUID]
    verified_at: Optional[datetime]
    verified_by: Optional[uuid.UUID]
    is_expired: bool
    days_until_expiry: Optional[int]
    needs_renewal: bool