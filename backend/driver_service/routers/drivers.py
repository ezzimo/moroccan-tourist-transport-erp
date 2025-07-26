"""
Driver management routes
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status, UploadFile, File
from sqlmodel import Session, select, and_, or_
from database import get_session
from models.driver import Driver, DriverStatus, LicenseType, EmploymentType
from models.driver_document import DriverDocument, DocumentType
from schemas.driver import (
    DriverCreate, DriverUpdate, DriverResponse, DriverSummary, 
    DriverSearch, DriverPerformance
)
from schemas.driver_document import DriverDocumentResponse
from utils.auth import get_current_user, require_permission, CurrentUser
from services.driver_service import DriverService
from services.document_service import DocumentService
from typing import List, Optional
from datetime import date, datetime
import uuid


router = APIRouter(prefix="/drivers", tags=["Driver Management"])


@router.post("/", response_model=DriverResponse)
async def create_driver(
    driver_data: DriverCreate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("drivers", "create", "all"))
):
    """Create a new driver profile"""
    driver_service = DriverService(session)
    return await driver_service.create_driver(driver_data)


@router.get("/", response_model=List[DriverResponse])
async def get_drivers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    status: Optional[DriverStatus] = Query(None, description="Filter by driver status"),
    employment_type: Optional[EmploymentType] = Query(None, description="Filter by employment type"),
    license_type: Optional[LicenseType] = Query(None, description="Filter by license type"),
    available_only: bool = Query(False, description="Show only available drivers"),
    license_expiring_soon: bool = Query(False, description="Show drivers with expiring licenses"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("drivers", "read", "all"))
):
    """Get list of drivers with filtering options"""
    driver_service = DriverService(session)
    
    search_criteria = DriverSearch(
        status=status,
        employment_type=employment_type,
        license_type=license_type,
        available_for_assignment=available_only if available_only else None,
        license_expiring_soon=license_expiring_soon if license_expiring_soon else None
    )
    
    return await driver_service.search_drivers(search_criteria, skip=skip, limit=limit)


@router.get("/search", response_model=List[DriverResponse])
async def search_drivers(
    query: Optional[str] = Query(None, description="Search query for name, license, or employee ID"),
    languages: Optional[str] = Query(None, description="Comma-separated list of required languages"),
    tour_guide_certified: Optional[bool] = Query(None, description="Filter by tour guide certification"),
    first_aid_certified: Optional[bool] = Query(None, description="Filter by first aid certification"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("drivers", "read", "all"))
):
    """Advanced driver search with multiple criteria"""
    driver_service = DriverService(session)
    
    language_list = languages.split(",") if languages else None
    search_criteria = DriverSearch(
        query=query,
        languages=language_list,
        tour_guide_certified=tour_guide_certified,
        first_aid_certified=first_aid_certified
    )
    
    return await driver_service.search_drivers(search_criteria, skip=skip, limit=limit)


@router.get("/summary", response_model=DriverSummary)
async def get_drivers_summary(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("drivers", "read", "all"))
):
    """Get driver statistics and summary"""
    driver_service = DriverService(session)
    return await driver_service.get_drivers_summary()


@router.get("/expiring-licenses", response_model=List[DriverResponse])
async def get_expiring_licenses(
    days: int = Query(30, ge=1, le=365, description="Days ahead to check for expiring licenses"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("drivers", "read", "all"))
):
    """Get drivers with licenses expiring within specified days"""
    driver_service = DriverService(session)
    return await driver_service.get_expiring_licenses(days)


@router.get("/expiring-health-certificates", response_model=List[DriverResponse])
async def get_expiring_health_certificates(
    days: int = Query(60, ge=1, le=365, description="Days ahead to check for expiring health certificates"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("drivers", "read", "all"))
):
    """Get drivers with health certificates expiring within specified days"""
    driver_service = DriverService(session)
    return await driver_service.get_expiring_health_certificates(days)


@router.get("/{driver_id}", response_model=DriverResponse)
async def get_driver(
    driver_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("drivers", "read", "all"))
):
    """Get driver by ID"""
    driver_service = DriverService(session)
    return await driver_service.get_driver(driver_id)


@router.put("/{driver_id}", response_model=DriverResponse)
async def update_driver(
    driver_id: uuid.UUID,
    driver_data: DriverUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("drivers", "update", "all"))
):
    """Update driver information"""
    driver_service = DriverService(session)
    return await driver_service.update_driver(driver_id, driver_data)


@router.delete("/{driver_id}")
async def delete_driver(
    driver_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("drivers", "delete", "all"))
):
    """Delete driver (soft delete by changing status)"""
    driver_service = DriverService(session)
    return await driver_service.delete_driver(driver_id)


@router.get("/{driver_id}/performance", response_model=DriverPerformance)
async def get_driver_performance(
    driver_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("drivers", "read", "all"))
):
    """Get driver performance metrics"""
    driver_service = DriverService(session)
    return await driver_service.get_driver_performance(driver_id)


@router.get("/{driver_id}/documents", response_model=List[DriverDocumentResponse])
async def get_driver_documents(
    driver_id: uuid.UUID,
    document_type: Optional[DocumentType] = Query(None, description="Filter by document type"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("drivers", "read", "all"))
):
    """Get driver documents"""
    document_service = DocumentService(session)
    return await document_service.get_driver_documents(driver_id, document_type)


@router.post("/{driver_id}/documents", response_model=DriverDocumentResponse)
async def upload_driver_document(
    driver_id: uuid.UUID,
    document_type: DocumentType,
    title: str,
    file: UploadFile = File(...),
    description: Optional[str] = None,
    document_number: Optional[str] = None,
    issue_date: Optional[date] = None,
    expiry_date: Optional[date] = None,
    issuing_authority: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("drivers", "create", "documents"))
):
    """Upload a document for a driver"""
    document_service = DocumentService(session)
    return await document_service.upload_document(
        driver_id=driver_id,
        document_type=document_type,
        title=title,
        file=file,
        description=description,
        document_number=document_number,
        issue_date=issue_date,
        expiry_date=expiry_date,
        issuing_authority=issuing_authority,
        uploaded_by=current_user.user_id
    )


@router.put("/{driver_id}/documents/{document_id}/approve")
async def approve_document(
    driver_id: uuid.UUID,
    document_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("drivers", "approve", "documents"))
):
    """Approve a driver document"""
    document_service = DocumentService(session)
    return await document_service.approve_document(document_id, current_user.user_id)


@router.put("/{driver_id}/documents/{document_id}/reject")
async def reject_document(
    driver_id: uuid.UUID,
    document_id: uuid.UUID,
    rejection_reason: str,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("drivers", "approve", "documents"))
):
    """Reject a driver document"""
    document_service = DocumentService(session)
    return await document_service.reject_document(document_id, rejection_reason, current_user.user_id)


@router.delete("/{driver_id}/documents/{document_id}")
async def delete_document(
    driver_id: uuid.UUID,
    document_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("drivers", "delete", "documents"))
):
    """Delete a driver document"""
    document_service = DocumentService(session)
    return await document_service.delete_document(document_id)