"""
Driver document-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime, date
from models.driver_document import DocumentType, DocumentStatus
import uuid


class DriverDocumentBase(BaseModel):
    document_type: DocumentType
    title: str
    description: Optional[str] = None
    document_number: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    issuing_authority: Optional[str] = None
    is_required: bool = False
    upload_notes: Optional[str] = None


class DriverDocumentCreate(DriverDocumentBase):
    pass


class DriverDocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    document_number: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    issuing_authority: Optional[str] = None
    is_required: Optional[bool] = None
    upload_notes: Optional[str] = None
    review_notes: Optional[str] = None


class DriverDocumentResponse(DriverDocumentBase):
    id: uuid.UUID
    driver_id: uuid.UUID
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    status: DocumentStatus
    uploaded_by: Optional[uuid.UUID]
    reviewed_by: Optional[uuid.UUID]
    approved_by: Optional[uuid.UUID]
    review_notes: Optional[str]
    rejection_reason: Optional[str]
    uploaded_at: datetime
    reviewed_at: Optional[datetime]
    approved_at: Optional[datetime]
    
    # Computed fields
    is_expired: bool
    days_until_expiry: Optional[int]
    needs_renewal: bool
    file_size_mb: float


class DocumentSummary(BaseModel):
    """Document summary for dashboard"""
    total_documents: int
    pending_documents: int
    approved_documents: int
    rejected_documents: int
    expired_documents: int
    expiring_soon: int
    by_document_type: dict