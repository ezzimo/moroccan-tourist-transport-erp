"""
Document service for driver document management
"""
from sqlmodel import Session, select, and_
from fastapi import HTTPException, status, UploadFile
from models.driver_document import DriverDocument, DocumentType, DocumentStatus
from models.driver import Driver
from schemas.driver_document import (
    DriverDocumentCreate, DriverDocumentUpdate, DriverDocumentResponse
)
from utils.upload import process_upload, get_file_info
from utils.validation import validate_driver_data
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uuid
import logging

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for handling driver document operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def upload_document(
        self,
        driver_id: uuid.UUID,
        document_type: DocumentType,
        title: str,
        file: UploadFile,
        description: Optional[str] = None,
        document_number: Optional[str] = None,
        issue_date: Optional[date] = None,
        expiry_date: Optional[date] = None,
        issuing_authority: Optional[str] = None,
        uploaded_by: uuid.UUID = None
    ) -> DriverDocumentResponse:
        """Upload a document for a driver
        
        Args:
            driver_id: Driver UUID
            document_type: Type of document
            title: Document title
            file: Uploaded file
            description: Document description
            document_number: Document number
            issue_date: Document issue date
            expiry_date: Document expiry date
            issuing_authority: Issuing authority
            uploaded_by: User who uploaded the document
            
        Returns:
            Created document record
            
        Raises:
            HTTPException: If validation fails or driver not found
        """
        # Verify driver exists
        driver = self.session.get(Driver, driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # Process file upload
        try:
            upload_result = await process_upload(file, driver_id)
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File upload failed: {str(e)}"
            )
        
        # Create document record
        document = DriverDocument(
            driver_id=driver_id,
            document_type=document_type,
            title=title,
            description=description,
            file_name=upload_result["original_filename"],
            file_path=upload_result["file_path"],
            file_size=upload_result["file_size"],
            mime_type=upload_result["mime_type"],
            document_number=document_number,
            issue_date=issue_date,
            expiry_date=expiry_date,
            issuing_authority=issuing_authority,
            uploaded_by=uploaded_by,
            status=DocumentStatus.PENDING
        )
        
        self.session.add(document)
        self.session.commit()
        self.session.refresh(document)
        
        logger.info(f"Uploaded document {document.id} for driver {driver.full_name}")
        return self._to_response(document)
    
    async def get_driver_documents(
        self,
        driver_id: uuid.UUID,
        document_type: Optional[DocumentType] = None
    ) -> List[DriverDocumentResponse]:
        """Get documents for a driver
        
        Args:
            driver_id: Driver UUID
            document_type: Filter by document type
            
        Returns:
            List of driver documents
        """
        query = select(DriverDocument).where(DriverDocument.driver_id == driver_id)
        
        if document_type:
            query = query.where(DriverDocument.document_type == document_type)
        
        query = query.order_by(DriverDocument.uploaded_at.desc())
        documents = self.session.exec(query).all()
        
        return [self._to_response(doc) for doc in documents]
    
    async def get_document(self, document_id: uuid.UUID) -> DriverDocumentResponse:
        """Get document by ID
        
        Args:
            document_id: Document UUID
            
        Returns:
            Document details
            
        Raises:
            HTTPException: If document not found
        """
        document = self.session.get(DriverDocument, document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return self._to_response(document)
    
    async def update_document(
        self,
        document_id: uuid.UUID,
        document_data: DriverDocumentUpdate
    ) -> DriverDocumentResponse:
        """Update document information
        
        Args:
            document_id: Document UUID
            document_data: Update data
            
        Returns:
            Updated document
            
        Raises:
            HTTPException: If document not found
        """
        document = self.session.get(DriverDocument, document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Update fields
        update_data = document_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(document, field, value)
        
        self.session.add(document)
        self.session.commit()
        self.session.refresh(document)
        
        logger.info(f"Updated document {document_id}")
        return self._to_response(document)
    
    async def approve_document(self, document_id: uuid.UUID, approved_by: uuid.UUID) -> dict:
        """Approve a document
        
        Args:
            document_id: Document UUID
            approved_by: User who approved the document
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If document not found or cannot be approved
        """
        document = self.session.get(DriverDocument, document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        if document.status != DocumentStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot approve document with status {document.status}"
            )
        
        document.status = DocumentStatus.APPROVED
        document.approved_by = approved_by
        document.approved_at = datetime.utcnow()
        
        self.session.add(document)
        self.session.commit()
        
        logger.info(f"Approved document {document_id}")
        return {"message": "Document approved successfully"}
    
    async def reject_document(
        self,
        document_id: uuid.UUID,
        rejection_reason: str,
        reviewed_by: uuid.UUID
    ) -> dict:
        """Reject a document
        
        Args:
            document_id: Document UUID
            rejection_reason: Reason for rejection
            reviewed_by: User who reviewed the document
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If document not found or cannot be rejected
        """
        document = self.session.get(DriverDocument, document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        if document.status != DocumentStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reject document with status {document.status}"
            )
        
        document.status = DocumentStatus.REJECTED
        document.rejection_reason = rejection_reason
        document.reviewed_by = reviewed_by
        document.reviewed_at = datetime.utcnow()
        
        self.session.add(document)
        self.session.commit()
        
        logger.info(f"Rejected document {document_id}: {rejection_reason}")
        return {"message": "Document rejected successfully"}
    
    async def delete_document(self, document_id: uuid.UUID) -> dict:
        """Delete a document
        
        Args:
            document_id: Document UUID
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If document not found
        """
        document = self.session.get(DriverDocument, document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Delete file from storage
        from utils.upload import FileUploadHandler
        handler = FileUploadHandler()
        handler.delete_file(document.file_path)
        
        # Delete database record
        self.session.delete(document)
        self.session.commit()
        
        logger.info(f"Deleted document {document_id}")
        return {"message": "Document deleted successfully"}
    
    async def get_expiring_documents(self, days: int = 30) -> List[DriverDocumentResponse]:
        """Get documents expiring within specified days
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of expiring documents
        """
        from datetime import timedelta
        alert_date = date.today() + timedelta(days=days)
        
        query = select(DriverDocument).where(
            and_(
                DriverDocument.expiry_date.is_not(None),
                DriverDocument.expiry_date <= alert_date,
                DriverDocument.expiry_date > date.today(),
                DriverDocument.status == DocumentStatus.APPROVED
            )
        ).order_by(DriverDocument.expiry_date)
        
        documents = self.session.exec(query).all()
        return [self._to_response(doc) for doc in documents]
    
    async def get_documents_by_status(self, status: DocumentStatus) -> List[DriverDocumentResponse]:
        """Get documents by status
        
        Args:
            status: Document status
            
        Returns:
            List of documents with specified status
        """
        query = select(DriverDocument).where(DriverDocument.status == status)
        query = query.order_by(DriverDocument.uploaded_at.desc())
        
        documents = self.session.exec(query).all()
        return [self._to_response(doc) for doc in documents]
    
    def _to_response(self, document: DriverDocument) -> DriverDocumentResponse:
        """Convert document model to response schema
        
        Args:
            document: Document model
            
        Returns:
            Document response schema
        """
        return DriverDocumentResponse(
            id=document.id,
            driver_id=document.driver_id,
            document_type=document.document_type,
            title=document.title,
            description=document.description,
            file_name=document.file_name,
            file_path=document.file_path,
            file_size=document.file_size,
            mime_type=document.mime_type,
            document_number=document.document_number,
            issue_date=document.issue_date,
            expiry_date=document.expiry_date,
            issuing_authority=document.issuing_authority,
            is_required=document.is_required,
            status=document.status,
            uploaded_by=document.uploaded_by,
            reviewed_by=document.reviewed_by,
            approved_by=document.approved_by,
            upload_notes=document.upload_notes,
            review_notes=document.review_notes,
            rejection_reason=document.rejection_reason,
            uploaded_at=document.uploaded_at,
            reviewed_at=document.reviewed_at,
            approved_at=document.approved_at,
            is_expired=document.is_expired(),
            days_until_expiry=document.days_until_expiry(),
            needs_renewal=document.needs_renewal(),
            file_size_mb=document.get_file_size_mb()
        )