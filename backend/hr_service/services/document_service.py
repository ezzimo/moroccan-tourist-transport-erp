"""
Document service for managing employee documents and HR files
"""
from sqlmodel import Session, select, and_
from fastapi import HTTPException, status, UploadFile
from models.employee_document import EmployeeDocument, DocumentType, DocumentStatus
from models.employee import Employee
from schemas.employee_document import (
    EmployeeDocumentCreate, EmployeeDocumentUpdate, EmployeeDocumentResponse
)
from utils.upload import process_upload, get_file_info
from utils.validation import validate_document
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for handling employee document operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def upload_document(
        self,
        employee_id: uuid.UUID,
        document_type: DocumentType,
        title: str,
        file: UploadFile,
        description: Optional[str] = None,
        expiry_date: Optional[date] = None,
        uploaded_by: uuid.UUID = None
    ) -> EmployeeDocumentResponse:
        """Upload a document for an employee
        
        Args:
            employee_id: Employee UUID
            document_type: Type of document
            title: Document title
            file: Uploaded file
            description: Document description
            expiry_date: Document expiry date
            uploaded_by: User who uploaded the document
            
        Returns:
            Created document record
            
        Raises:
            HTTPException: If validation fails or employee not found
        """
        # Verify employee exists
        employee = self.session.get(Employee, employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Validate document
        try:
            validation_result = await validate_document(file)
        except Exception as e:
            logger.error(f"Document validation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Document validation failed: {str(e)}"
            )
        
        # Process file upload
        try:
            upload_result = await process_upload(file, f"employees/{employee_id}/documents")
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File upload failed: {str(e)}"
            )
        
        # Create document record
        document = EmployeeDocument(
            employee_id=employee_id,
            document_type=document_type,
            title=title,
            description=description,
            file_name=upload_result["original_filename"],
            file_path=upload_result["file_path"],
            file_size=upload_result["file_size"],
            mime_type=upload_result["mime_type"],
            expiry_date=expiry_date,
            uploaded_by=uploaded_by,
            status=DocumentStatus.PENDING
        )
        
        self.session.add(document)
        self.session.commit()
        self.session.refresh(document)
        
        logger.info(f"Uploaded document {document.id} for employee {employee.full_name}")
        return self._to_response(document)
    
    async def get_employee_documents(
        self,
        employee_id: uuid.UUID,
        document_type: Optional[DocumentType] = None,
        status: Optional[DocumentStatus] = None
    ) -> List[EmployeeDocumentResponse]:
        """Get documents for an employee
        
        Args:
            employee_id: Employee UUID
            document_type: Filter by document type
            status: Filter by document status
            
        Returns:
            List of employee documents
        """
        query = select(EmployeeDocument).where(EmployeeDocument.employee_id == employee_id)
        
        conditions = []
        if document_type:
            conditions.append(EmployeeDocument.document_type == document_type)
        if status:
            conditions.append(EmployeeDocument.status == status)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(EmployeeDocument.uploaded_at.desc())
        documents = self.session.exec(query).all()
        
        return [self._to_response(doc) for doc in documents]
    
    async def get_document(self, document_id: uuid.UUID) -> EmployeeDocumentResponse:
        """Get document by ID
        
        Args:
            document_id: Document UUID
            
        Returns:
            Document details
            
        Raises:
            HTTPException: If document not found
        """
        document = self.session.get(EmployeeDocument, document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return self._to_response(document)
    
    async def update_document(
        self,
        document_id: uuid.UUID,
        document_data: EmployeeDocumentUpdate
    ) -> EmployeeDocumentResponse:
        """Update document information
        
        Args:
            document_id: Document UUID
            document_data: Update data
            
        Returns:
            Updated document
            
        Raises:
            HTTPException: If document not found
        """
        document = self.session.get(EmployeeDocument, document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Update fields
        update_data = document_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(document, field, value)
        
        document.updated_at = datetime.utcnow()
        
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
        document = self.session.get(EmployeeDocument, document_id)
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
        document.updated_at = datetime.utcnow()
        
        self.session.add(document)
        self.session.commit()
        
        logger.info(f"Approved document {document_id}")
        return {"message": "Document approved successfully"}
    
    async def reject_document(
        self,
        document_id: uuid.UUID,
        rejection_reason: str,
        rejected_by: uuid.UUID
    ) -> dict:
        """Reject a document
        
        Args:
            document_id: Document UUID
            rejection_reason: Reason for rejection
            rejected_by: User who rejected the document
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If document not found or cannot be rejected
        """
        document = self.session.get(EmployeeDocument, document_id)
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
        document.rejected_by = rejected_by
        document.rejected_at = datetime.utcnow()
        document.updated_at = datetime.utcnow()
        
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
        document = self.session.get(EmployeeDocument, document_id)
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
    
    async def get_expiring_documents(self, days: int = 30) -> List[EmployeeDocumentResponse]:
        """Get documents expiring within specified days
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of expiring documents
        """
        alert_date = date.today() + timedelta(days=days)
        
        query = select(EmployeeDocument).where(
            and_(
                EmployeeDocument.expiry_date.is_not(None),
                EmployeeDocument.expiry_date <= alert_date,
                EmployeeDocument.expiry_date > date.today(),
                EmployeeDocument.status == DocumentStatus.APPROVED
            )
        ).order_by(EmployeeDocument.expiry_date)
        
        documents = self.session.exec(query).all()
        return [self._to_response(doc) for doc in documents]
    
    async def get_documents_by_status(self, status: DocumentStatus) -> List[EmployeeDocumentResponse]:
        """Get documents by status
        
        Args:
            status: Document status
            
        Returns:
            List of documents with specified status
        """
        query = select(EmployeeDocument).where(EmployeeDocument.status == status)
        query = query.order_by(EmployeeDocument.uploaded_at.desc())
        
        documents = self.session.exec(query).all()
        return [self._to_response(doc) for doc in documents]
    
    async def get_document_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get document analytics
        
        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            
        Returns:
            Document analytics data
        """
        query = select(EmployeeDocument)
        
        # Apply date filters
        conditions = []
        if start_date:
            conditions.append(EmployeeDocument.uploaded_at >= start_date)
        if end_date:
            conditions.append(EmployeeDocument.uploaded_at <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        documents = self.session.exec(query).all()
        
        # Calculate metrics
        total_documents = len(documents)
        approved_documents = len([d for d in documents if d.status == DocumentStatus.APPROVED])
        pending_documents = len([d for d in documents if d.status == DocumentStatus.PENDING])
        rejected_documents = len([d for d in documents if d.status == DocumentStatus.REJECTED])
        
        # Expiring documents
        alert_date = date.today() + timedelta(days=30)
        expiring_documents = len([
            d for d in documents 
            if d.expiry_date and d.expiry_date <= alert_date and d.expiry_date > date.today()
        ])
        
        # By document type
        by_document_type = {}
        for doc_type in DocumentType:
            count = len([d for d in documents if d.document_type == doc_type])
            by_document_type[doc_type.value] = count
        
        # By status
        by_status = {}
        for status in DocumentStatus:
            count = len([d for d in documents if d.status == status])
            by_status[status.value] = count
        
        # Approval rate
        approval_rate = approved_documents / total_documents * 100 if total_documents > 0 else 0
        
        return {
            "total_documents": total_documents,
            "approved_documents": approved_documents,
            "pending_documents": pending_documents,
            "rejected_documents": rejected_documents,
            "expiring_documents": expiring_documents,
            "approval_rate": approval_rate,
            "by_document_type": by_document_type,
            "by_status": by_status,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    async def bulk_approve_documents(
        self,
        document_ids: List[uuid.UUID],
        approved_by: uuid.UUID
    ) -> Dict[str, Any]:
        """Bulk approve multiple documents
        
        Args:
            document_ids: List of document UUIDs
            approved_by: User who approved the documents
            
        Returns:
            Bulk operation results
        """
        results = {
            "approved": 0,
            "failed": 0,
            "errors": []
        }
        
        for document_id in document_ids:
            try:
                await self.approve_document(document_id, approved_by)
                results["approved"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "document_id": str(document_id),
                    "error": str(e)
                })
        
        logger.info(f"Bulk approved {results['approved']} documents, {results['failed']} failed")
        return results
    
    async def generate_document_report(
        self,
        employee_id: Optional[uuid.UUID] = None,
        document_type: Optional[DocumentType] = None
    ) -> Dict[str, Any]:
        """Generate document compliance report
        
        Args:
            employee_id: Filter by specific employee
            document_type: Filter by document type
            
        Returns:
            Document compliance report
        """
        query = select(EmployeeDocument)
        
        conditions = []
        if employee_id:
            conditions.append(EmployeeDocument.employee_id == employee_id)
        if document_type:
            conditions.append(EmployeeDocument.document_type == document_type)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        documents = self.session.exec(query).all()
        
        # Group by employee
        employee_compliance = {}
        for doc in documents:
            emp_id = str(doc.employee_id)
            if emp_id not in employee_compliance:
                employee_compliance[emp_id] = {
                    "total_documents": 0,
                    "approved_documents": 0,
                    "pending_documents": 0,
                    "expired_documents": 0,
                    "compliance_score": 0
                }
            
            employee_compliance[emp_id]["total_documents"] += 1
            
            if doc.status == DocumentStatus.APPROVED:
                employee_compliance[emp_id]["approved_documents"] += 1
            elif doc.status == DocumentStatus.PENDING:
                employee_compliance[emp_id]["pending_documents"] += 1
            
            if doc.expiry_date and doc.expiry_date < date.today():
                employee_compliance[emp_id]["expired_documents"] += 1
        
        # Calculate compliance scores
        for emp_data in employee_compliance.values():
            if emp_data["total_documents"] > 0:
                emp_data["compliance_score"] = (
                    emp_data["approved_documents"] / emp_data["total_documents"] * 100
                )
        
        return {
            "employee_compliance": employee_compliance,
            "summary": {
                "total_employees": len(employee_compliance),
                "average_compliance": sum(
                    emp["compliance_score"] for emp in employee_compliance.values()
                ) / len(employee_compliance) if employee_compliance else 0
            }
        }
    
    def _to_response(self, document: EmployeeDocument) -> EmployeeDocumentResponse:
        """Convert document model to response schema
        
        Args:
            document: Document model
            
        Returns:
            Document response schema
        """
        return EmployeeDocumentResponse(
            id=document.id,
            employee_id=document.employee_id,
            document_type=document.document_type,
            title=document.title,
            description=document.description,
            file_name=document.file_name,
            file_path=document.file_path,
            file_size=document.file_size,
            mime_type=document.mime_type,
            expiry_date=document.expiry_date,
            status=document.status,
            uploaded_by=document.uploaded_by,
            approved_by=document.approved_by,
            rejected_by=document.rejected_by,
            rejection_reason=document.rejection_reason,
            uploaded_at=document.uploaded_at,
            approved_at=document.approved_at,
            rejected_at=document.rejected_at,
            updated_at=document.updated_at,
            is_expired=document.is_expired(),
            days_until_expiry=document.days_until_expiry(),
            file_size_mb=document.get_file_size_mb()
        )