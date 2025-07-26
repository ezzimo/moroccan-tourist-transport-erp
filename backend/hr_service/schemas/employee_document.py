"""
Employee document-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime, date
from models.employee_document import DocumentType, DocumentStatus
import uuid


class EmployeeDocumentBase(BaseModel):
    document_type: DocumentType
    title: str
    description: Optional[str] = None
    document_number: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    issuing_authority: Optional[str] = None
    is_confidential: bool = False
    is_required: bool = False


class EmployeeDocumentCreate(EmployeeDocumentBase):
    employee_id: uuid.UUID
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    uploaded_by: Optional[uuid.UUID] = None
    upload_notes: Optional[str] = None
    
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


class EmployeeDocumentUpdate(BaseModel):
    document_type: Optional[DocumentType] = None
    title: Optional[str] = None
    description: Optional[str] = None
    document_number: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    issuing_authority: Optional[str] = None
    status: Optional[DocumentStatus] = None
    is_confidential: Optional[bool] = None
    is_required: Optional[bool] = None
    reviewed_by: Optional[uuid.UUID] = None
    approved_by: Optional[uuid.UUID] = None
    review_notes: Optional[str] = None
    rejection_reason: Optional[str] = None


class EmployeeDocumentResponse(EmployeeDocumentBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    status: DocumentStatus
    uploaded_by: Optional[uuid.UUID]
    reviewed_by: Optional[uuid.UUID]
    approved_by: Optional[uuid.UUID]
    upload_notes: Optional[str]
    review_notes: Optional[str]
    rejection_reason: Optional[str]
    uploaded_at: datetime
    reviewed_at: Optional[datetime]
    approved_at: Optional[datetime]
    is_expired: bool
    days_until_expiry: Optional[int]
    needs_renewal: bool
    file_size_mb: float


class DocumentUploadResponse(BaseModel):
    """Response for document upload"""
    document_id: uuid.UUID
    message: str
    file_name: str
    file_size_mb: float
    status: DocumentStatus


class DocumentApproval(BaseModel):
    """Schema for document approval/rejection"""
    status: DocumentStatus
    review_notes: Optional[str] = None
    rejection_reason: Optional[str] = None