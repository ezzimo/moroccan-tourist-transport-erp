"""
Employee document model for document management
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, date
from enum import Enum
import uuid


class DocumentType(str, Enum):
    """Document type enumeration"""
    CONTRACT = "Contract"
    ID_COPY = "ID Copy"
    DIPLOMA = "Diploma"
    CERTIFICATE = "Certificate"
    MEDICAL_CERTIFICATE = "Medical Certificate"
    DRIVING_LICENSE = "Driving License"
    BACKGROUND_CHECK = "Background Check"
    REFERENCE_LETTER = "Reference Letter"
    PHOTO = "Photo"
    BANK_DETAILS = "Bank Details"
    TAX_DOCUMENTS = "Tax Documents"
    INSURANCE = "Insurance"
    OTHER = "Other"


class DocumentStatus(str, Enum):
    """Document status enumeration"""
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    EXPIRED = "Expired"
    UNDER_REVIEW = "Under Review"


class EmployeeDocument(SQLModel, table=True):
    """Employee document model for document management"""
    __tablename__ = "employee_documents"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Foreign Keys
    employee_id: uuid.UUID = Field(foreign_key="employees.id", index=True)
    
    # Document Information
    document_type: DocumentType = Field(index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    
    # File Information
    file_name: str = Field(max_length=255)
    file_path: str = Field(max_length=500)
    file_size: int = Field(ge=0)
    mime_type: str = Field(max_length=100)
    
    # Document Metadata
    document_number: Optional[str] = Field(default=None, max_length=100)
    issue_date: Optional[date] = Field(default=None)
    expiry_date: Optional[date] = Field(default=None, index=True)
    issuing_authority: Optional[str] = Field(default=None, max_length=255)
    
    # Status and Approval
    status: DocumentStatus = Field(default=DocumentStatus.PENDING, index=True)
    is_confidential: bool = Field(default=False)
    is_required: bool = Field(default=False)
    
    # Approval Workflow
    uploaded_by: Optional[uuid.UUID] = Field(default=None)
    reviewed_by: Optional[uuid.UUID] = Field(default=None)
    approved_by: Optional[uuid.UUID] = Field(default=None)
    
    # Notes and Comments
    upload_notes: Optional[str] = Field(default=None, max_length=500)
    review_notes: Optional[str] = Field(default=None, max_length=500)
    rejection_reason: Optional[str] = Field(default=None, max_length=500)
    
    # Timestamps
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = Field(default=None)
    approved_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    employee: Optional["Employee"] = Relationship(back_populates="documents")
    
    def is_expired(self) -> bool:
        """Check if document is expired"""
        if not self.expiry_date:
            return False
        return date.today() > self.expiry_date
    
    def days_until_expiry(self) -> Optional[int]:
        """Get days until document expires"""
        if not self.expiry_date:
            return None
        return (self.expiry_date - date.today()).days
    
    def needs_renewal(self, alert_days: int = 30) -> bool:
        """Check if document needs renewal within alert period"""
        days_left = self.days_until_expiry()
        if days_left is None:
            return False
        return days_left <= alert_days
    
    def get_file_size_mb(self) -> float:
        """Get file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)