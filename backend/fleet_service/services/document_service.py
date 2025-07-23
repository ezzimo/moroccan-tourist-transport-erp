"""
Document service for vehicle documentation management
"""
from sqlmodel import Session, select, and_
from fastapi import HTTPException, status, UploadFile
from models.document import Document, DocumentType
from models.vehicle import Vehicle
from schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentResponse
)
from utils.pagination import PaginationParams, paginate_query
from typing import List, Optional, Tuple
from datetime import datetime, date
import uuid
import os
import shutil


class DocumentService:
    """Service for handling vehicle document operations"""
    
    def __init__(self, session: Session):
        self.session = session
        self.upload_directory = "uploads/documents"
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_directory, exist_ok=True)
    
    async def upload_document(
        self, 
        vehicle_id: uuid.UUID,
        document_type: DocumentType,
        title: str,
        file: UploadFile,
        description: Optional[str] = None,
        issue_date: Optional[date] = None,
        expiry_date: Optional[date] = None,
        issuing_authority: Optional[str] = None,
        document_number: Optional[str] = None,
        uploaded_by: Optional[uuid.UUID] = None
    ) -> DocumentResponse:
        """Upload a document for a vehicle"""
        # Verify vehicle exists
        vehicle_stmt = select(Vehicle).where(Vehicle.id == vehicle_id)
        vehicle = self.session.exec(vehicle_stmt).first()
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(self.upload_directory, unique_filename)
        
        # Save file
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create document record
        document_data = DocumentCreate(
            vehicle_id=vehicle_id,
            document_type=document_type,
            title=title,
            description=description,
            file_name=file.filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=file.content_type or "application/octet-stream",
            issue_date=issue_date,
            expiry_date=expiry_date,
            issuing_authority=issuing_authority,
            document_number=document_number,
            uploaded_by=uploaded_by
        )
        
        document = Document(**document_data.model_dump())
        
        self.session.add(document)
        self.session.commit()
        self.session.refresh(document)
        
        return self._create_document_response(document)
    
    async def get_document(self, document_id: uuid.UUID) -> DocumentResponse:
        """Get document by ID"""
        statement = select(Document).where(Document.id == document_id)
        document = self.session.exec(statement).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return self._create_document_response(document)
    
    async def get_documents(
        self, 
        pagination: PaginationParams,
        vehicle_id: Optional[uuid.UUID] = None,
        document_type: Optional[DocumentType] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        expiring_soon: Optional[bool] = None
    ) -> Tuple[List[DocumentResponse], int]:
        """Get list of documents with optional filters"""
        query = select(Document)
        
        # Apply filters
        conditions = []
        
        if vehicle_id:
            conditions.append(Document.vehicle_id == vehicle_id)
        
        if document_type:
            conditions.append(Document.document_type == document_type)
        
        if is_active is not None:
            conditions.append(Document.is_active == is_active)
        
        if is_verified is not None:
            conditions.append(Document.is_verified == is_verified)
        
        if expiring_soon:
            # Documents expiring within 30 days
            expiry_threshold = date.today() + timedelta(days=30)
            conditions.append(
                and_(
                    Document.expiry_date.is_not(None),
                    Document.expiry_date <= expiry_threshold
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Order by upload date (newest first)
        query = query.order_by(Document.uploaded_at.desc())
        
        documents, total = paginate_query(self.session, query, pagination)
        
        return [self._create_document_response(document) for document in documents], total
    
    async def update_document(self, document_id: uuid.UUID, document_data: DocumentUpdate) -> DocumentResponse:
        """Update document information"""
        statement = select(Document).where(Document.id == document_id)
        document = self.session.exec(statement).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Update fields
        update_data = document_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(document, field, value)
        
        # Set verification timestamp if being verified
        if document_data.is_verified and not document.is_verified:
            document.verified_at = datetime.utcnow()
            if document_data.verified_by:
                document.verified_by = document_data.verified_by
        
        self.session.add(document)
        self.session.commit()
        self.session.refresh(document)
        
        return self._create_document_response(document)
    
    async def delete_document(self, document_id: uuid.UUID) -> dict:
        """Delete document and associated file"""
        statement = select(Document).where(Document.id == document_id)
        document = self.session.exec(statement).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Delete file from filesystem
        try:
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
        except Exception:
            # Log error but don't fail the operation
            pass
        
        # Delete database record
        self.session.delete(document)
        self.session.commit()
        
        return {"message": "Document deleted successfully"}
    
    async def get_vehicle_documents(
        self, 
        vehicle_id: uuid.UUID, 
        pagination: PaginationParams
    ) -> Tuple[List[DocumentResponse], int]:
        """Get all documents for a specific vehicle"""
        # Verify vehicle exists
        vehicle_stmt = select(Vehicle).where(Vehicle.id == vehicle_id)
        vehicle = self.session.exec(vehicle_stmt).first()
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        return await self.get_documents(pagination, vehicle_id=vehicle_id)
    
    async def get_expiring_documents(self, days_ahead: int = 30) -> List[DocumentResponse]:
        """Get documents expiring within specified days"""
        expiry_threshold = date.today() + timedelta(days=days_ahead)
        
        statement = select(Document).where(
            Document.is_active == True,
            Document.expiry_date.is_not(None),
            Document.expiry_date <= expiry_threshold,
            Document.expiry_date >= date.today()
        ).order_by(Document.expiry_date)
        
        documents = self.session.exec(statement).all()
        
        return [self._create_document_response(document) for document in documents]
    
    def _create_document_response(self, document: Document) -> DocumentResponse:
        """Create document response with calculated fields"""
        return DocumentResponse(
            id=document.id,
            vehicle_id=document.vehicle_id,
            document_type=document.document_type,
            title=document.title,
            description=document.description,
            file_name=document.file_name,
            file_path=document.file_path,
            file_size=document.file_size,
            mime_type=document.mime_type,
            issue_date=document.issue_date,
            expiry_date=document.expiry_date,
            issuing_authority=document.issuing_authority,
            document_number=document.document_number,
            is_active=document.is_active,
            is_verified=document.is_verified,
            uploaded_at=document.uploaded_at,
            uploaded_by=document.uploaded_by,
            verified_at=document.verified_at,
            verified_by=document.verified_by,
            is_expired=document.is_expired(),
            days_until_expiry=document.days_until_expiry(),
            needs_renewal=document.needs_renewal()
        )