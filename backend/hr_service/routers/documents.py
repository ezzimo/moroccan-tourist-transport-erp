"""
Employee document management routes
"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException, status
from sqlmodel import Session
from database import get_session
from services.document_service import DocumentService
from schemas.employee_document import (
    EmployeeDocumentUpdate, EmployeeDocumentResponse, DocumentUploadResponse, DocumentApproval
)
from models.employee_document import DocumentType, DocumentStatus
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional, Dict, Any
import uuid
from datetime import date


router = APIRouter(prefix="/documents", tags=["Document Management"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_employee_document(
    employee_id: uuid.UUID = Form(...),
    document_type: DocumentType = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    document_number: Optional[str] = Form(None),
    issue_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    issuing_authority: Optional[str] = Form(None),
    is_confidential: bool = Form(False),
    is_required: bool = Form(False),
    upload_notes: Optional[str] = Form(None),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("hr", "create", "documents"))
):
    """Upload a document for an employee"""
    document_service = DocumentService(session)
    
    # Parse dates
    issue_date_parsed = None
    expiry_date_parsed = None
    
    if issue_date:
        try:
            issue_date_parsed = date.fromisoformat(issue_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid issue_date format. Use YYYY-MM-DD"
            )
    
    if expiry_date:
        try:
            expiry_date_parsed = date.fromisoformat(expiry_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid expiry_date format. Use YYYY-MM-DD"
            )
    
    return await document_service.upload_document(
        employee_id=employee_id,
        document_type=document_type,
        title=title,
        file=file,
        description=description,
        document_number=document_number,
        issue_date=issue_date_parsed,
        expiry_date=expiry_date_parsed,
        issuing_authority=issuing_authority,
        is_confidential=is_confidential,
        is_required=is_required,
        upload_notes=upload_notes,
        uploaded_by=current_user.user_id
    )


@router.get("/", response_model=PaginatedResponse[EmployeeDocumentResponse])
async def get_documents(
    pagination: PaginationParams = Depends(),
    employee_id: Optional[uuid.UUID] = Query(None, description="Filter by employee ID"),
    document_type: Optional[DocumentType] = Query(None, description="Filter by document type"),
    status: Optional[DocumentStatus] = Query(None, description="Filter by status"),
    is_confidential: Optional[bool] = Query(None, description="Filter by confidential status"),
    expiring_soon: Optional[bool] = Query(None, description="Filter documents expiring within 30 days"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "documents"))
):
    """Get list of employee documents with optional filters"""
    document_service = DocumentService(session)
    
    documents, total = await document_service.get_documents(
        pagination=pagination,
        employee_id=employee_id,
        document_type=document_type,
        status=status,
        is_confidential=is_confidential,
        expiring_soon=expiring_soon
    )
    
    return PaginatedResponse.create(
        items=documents,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/expiring", response_model=List[EmployeeDocumentResponse])
async def get_expiring_documents(
    days_ahead: int = Query(30, ge=1, le=365, description="Days ahead to check"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "documents"))
):
    """Get documents expiring within specified days"""
    document_service = DocumentService(session)
    return await document_service.get_expiring_documents(days_ahead)


@router.get("/{document_id}", response_model=EmployeeDocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "documents"))
):
    """Get document by ID"""
    document_service = DocumentService(session)
    return await document_service.get_document(document_id)


@router.put("/{document_id}", response_model=EmployeeDocumentResponse)
async def update_document(
    document_id: uuid.UUID,
    document_data: EmployeeDocumentUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("hr", "update", "documents"))
):
    """Update document information"""
    # Set reviewed_by to current user if reviewing
    if document_data.status and not document_data.reviewed_by:
        document_data.reviewed_by = current_user.user_id
    
    document_service = DocumentService(session)
    return await document_service.update_document(document_id, document_data)


@router.post("/{document_id}/approve", response_model=EmployeeDocumentResponse)
async def approve_document(
    document_id: uuid.UUID,
    approval: DocumentApproval,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("hr", "approve", "documents"))
):
    """Approve or reject a document"""
    document_service = DocumentService(session)
    return await document_service.approve_document(document_id, approval, current_user.user_id)


@router.delete("/{document_id}")
async def delete_document(
    document_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("hr", "delete", "documents"))
):
    """Delete document"""
    document_service = DocumentService(session)
    return await document_service.delete_document(document_id)


@router.get("/employee/{employee_id}", response_model=PaginatedResponse[EmployeeDocumentResponse])
async def get_employee_documents(
    employee_id: uuid.UUID,
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "documents"))
):
    """Get all documents for a specific employee"""
    document_service = DocumentService(session)
    
    documents, total = await document_service.get_employee_documents(employee_id, pagination)
    
    return PaginatedResponse.create(
        items=documents,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/type/{document_type}", response_model=List[EmployeeDocumentResponse])
async def get_documents_by_type(
    document_type: DocumentType,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "documents"))
):
    """Get all documents of a specific type"""
    document_service = DocumentService(session)
    return await document_service.get_documents_by_type(document_type)