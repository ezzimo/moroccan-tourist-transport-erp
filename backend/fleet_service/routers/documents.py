"""
Document management routes
"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException, status
from sqlmodel import Session
from database import get_session
from services.document_service import DocumentService
from schemas.document import (
    DocumentUpdate, DocumentResponse
)
from models.document import DocumentType
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import uuid
from datetime import date


router = APIRouter(prefix="/documents", tags=["Document Management"])


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    vehicle_id: uuid.UUID = Form(...),
    document_type: DocumentType = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    issue_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    issuing_authority: Optional[str] = Form(None),
    document_number: Optional[str] = Form(None),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("fleet", "create", "documents"))
):
    """Upload a document for a vehicle"""
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
        vehicle_id=vehicle_id,
        document_type=document_type,
        title=title,
        file=file,
        description=description,
        issue_date=issue_date_parsed,
        expiry_date=expiry_date_parsed,
        issuing_authority=issuing_authority,
        document_number=document_number,
        uploaded_by=current_user.user_id
    )


@router.get("/", response_model=PaginatedResponse[DocumentResponse])
async def get_documents(
    pagination: PaginationParams = Depends(),
    vehicle_id: Optional[uuid.UUID] = Query(None, description="Filter by vehicle ID"),
    document_type: Optional[DocumentType] = Query(None, description="Filter by document type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    expiring_soon: Optional[bool] = Query(None, description="Filter documents expiring within 30 days"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "documents"))
):
    """Get list of documents with optional filters"""
    document_service = DocumentService(session)
    
    documents, total = await document_service.get_documents(
        pagination=pagination,
        vehicle_id=vehicle_id,
        document_type=document_type,
        is_active=is_active,
        is_verified=is_verified,
        expiring_soon=expiring_soon
    )
    
    return PaginatedResponse.create(
        items=documents,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/expiring", response_model=List[DocumentResponse])
async def get_expiring_documents(
    days_ahead: int = Query(30, ge=1, le=365, description="Days ahead to check"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "documents"))
):
    """Get documents expiring within specified days"""
    document_service = DocumentService(session)
    return await document_service.get_expiring_documents(days_ahead)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "documents"))
):
    """Get document by ID"""
    document_service = DocumentService(session)
    return await document_service.get_document(document_id)


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: uuid.UUID,
    document_data: DocumentUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("fleet", "update", "documents"))
):
    """Update document information"""
    # Set verified_by to current user if marking as verified
    if document_data.is_verified and not document_data.verified_by:
        document_data.verified_by = current_user.user_id
    
    document_service = DocumentService(session)
    return await document_service.update_document(document_id, document_data)


@router.delete("/{document_id}")
async def delete_document(
    document_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("fleet", "delete", "documents"))
):
    """Delete document"""
    document_service = DocumentService(session)
    return await document_service.delete_document(document_id)


@router.get("/vehicle/{vehicle_id}", response_model=PaginatedResponse[DocumentResponse])
async def get_vehicle_documents(
    vehicle_id: uuid.UUID,
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "documents"))
):
    """Get all documents for a specific vehicle"""
    document_service = DocumentService(session)
    
    documents, total = await document_service.get_vehicle_documents(vehicle_id, pagination)
    
    return PaginatedResponse.create(
        items=documents,
        total=total,
        page=pagination.page,
        size=pagination.size
    )