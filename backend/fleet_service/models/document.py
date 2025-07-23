"""
Document model for vehicle documentation
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, date
from enum import Enum
import uuid


class DocumentType(str, Enum):
    """Document type enumeration"""
    REGISTRATION = "Registration"
    INSURANCE = "Insurance"
    INSPECTION = "Inspection"
    MAINTENANCE = "Maintenance"
    PURCHASE = "Purchase"
    OTHER = "Other"


class Document(SQLModel, table=True):
    """Document model for vehicle documentation storage"""
    __tablename__ = "documents"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Foreign Keys
    vehicle_id: uuid.UUID = Field(foreign_key="vehicles.id", index=True)
    
    # Document Information
    document_type: DocumentType = Field(index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    
    # File Information
    file_name: str = Field(max_length=255)
    file_path: str = Field(max_length=500)
    file_size: int = Field(ge=0)
    mime_type: str = Field(max_length=100)
    
    # Document Dates
    issue_date: Optional[date] = Field(default=None)
    expiry_date: Optional[date] = Field(default=None, index=True)
    
    # Additional Information
    issuing_authority: Optional[str] = Field(default=None, max_length=255)
    document_number: Optional[str] = Field(default=None, max_length=100)
    
    # Status
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    
    # Timestamps
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    uploaded_by: Optional[uuid.UUID] = Field(default=None)
    verified_at: Optional[datetime] = Field(default=None)
    verified_by: Optional[uuid.UUID] = Field(default=None)
    
    # Relationships
    vehicle: Optional["Vehicle"] = Relationship(back_populates="documents")
    
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