"""
Driver training routes
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status, UploadFile, File
from sqlmodel import Session
from database import get_session
from models.driver_training import DriverTrainingRecord, TrainingType, TrainingStatus
from schemas.driver_training import (
    DriverTrainingCreate, DriverTrainingUpdate, DriverTrainingResponse
)
from utils.auth import get_current_user, require_permission, CurrentUser
from services.training_service import TrainingService
from typing import List, Optional
from datetime import date
import uuid


router = APIRouter(prefix="/training", tags=["Driver Training"])


@router.post("/", response_model=DriverTrainingResponse)
async def create_training_record(
    training_data: DriverTrainingCreate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("training", "create", "all"))
):
    """Create a new training record"""
    training_service = TrainingService(session)
    return await training_service.create_training_record(training_data)


@router.get("/", response_model=List[DriverTrainingResponse])
async def get_training_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    driver_id: Optional[uuid.UUID] = Query(None, description="Filter by driver ID"),
    training_type: Optional[TrainingType] = Query(None, description="Filter by training type"),
    status: Optional[TrainingStatus] = Query(None, description="Filter by training status"),
    start_date: Optional[date] = Query(None, description="Filter training from this date"),
    end_date: Optional[date] = Query(None, description="Filter training until this date"),
    expiring_soon: bool = Query(False, description="Show certificates expiring within 30 days"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("training", "read", "all"))
):
    """Get list of training records with filtering"""
    training_service = TrainingService(session)
    return await training_service.get_training_records(
        skip=skip,
        limit=limit,
        driver_id=driver_id,
        training_type=training_type,
        status=status,
        start_date=start_date,
        end_date=end_date,
        expiring_soon=expiring_soon
    )


@router.get("/driver/{driver_id}", response_model=List[DriverTrainingResponse])
async def get_driver_training_history(
    driver_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    training_type: Optional[TrainingType] = Query(None),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("training", "read", "all"))
):
    """Get training history for a specific driver"""
    training_service = TrainingService(session)
    return await training_service.get_driver_training_history(
        driver_id=driver_id,
        skip=skip,
        limit=limit,
        training_type=training_type
    )


@router.get("/expiring-certificates", response_model=List[DriverTrainingResponse])
async def get_expiring_certificates(
    days: int = Query(30, ge=1, le=365, description="Days ahead to check for expiring certificates"),
    training_type: Optional[TrainingType] = Query(None),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("training", "read", "all"))
):
    """Get training certificates expiring within specified days"""
    training_service = TrainingService(session)
    return await training_service.get_expiring_certificates(days, training_type)


@router.get("/compliance-report")
async def get_training_compliance_report(
    training_type: Optional[TrainingType] = Query(None),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("training", "read", "reports"))
):
    """Get training compliance report"""
    training_service = TrainingService(session)
    return await training_service.get_compliance_report(training_type)


@router.get("/{training_id}", response_model=DriverTrainingResponse)
async def get_training_record(
    training_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("training", "read", "all"))
):
    """Get training record by ID"""
    training_service = TrainingService(session)
    return await training_service.get_training_record(training_id)


@router.put("/{training_id}", response_model=DriverTrainingResponse)
async def update_training_record(
    training_id: uuid.UUID,
    training_data: DriverTrainingUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("training", "update", "all"))
):
    """Update training record"""
    training_service = TrainingService(session)
    return await training_service.update_training_record(training_id, training_data)


@router.put("/{training_id}/complete")
async def complete_training(
    training_id: uuid.UUID,
    score: float,
    trainer_feedback: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("training", "update", "all"))
):
    """Mark training as completed with score"""
    training_service = TrainingService(session)
    return await training_service.complete_training(training_id, score, trainer_feedback)


@router.put("/{training_id}/fail")
async def fail_training(
    training_id: uuid.UUID,
    trainer_feedback: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("training", "update", "all"))
):
    """Mark training as failed"""
    training_service = TrainingService(session)
    return await training_service.fail_training(training_id, trainer_feedback)


@router.post("/{training_id}/certificate")
async def upload_certificate(
    training_id: uuid.UUID,
    certificate_file: UploadFile = File(...),
    certificate_number: Optional[str] = None,
    valid_until: Optional[date] = None,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("training", "update", "certificates"))
):
    """Upload training certificate"""
    training_service = TrainingService(session)
    return await training_service.upload_certificate(
        training_id=training_id,
        certificate_file=certificate_file,
        certificate_number=certificate_number,
        valid_until=valid_until
    )


@router.delete("/{training_id}")
async def delete_training_record(
    training_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("training", "delete", "all"))
):
    """Delete training record"""
    training_service = TrainingService(session)
    return await training_service.delete_training_record(training_id)


@router.get("/analytics/effectiveness")
async def get_training_effectiveness(
    training_type: Optional[TrainingType] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("training", "read", "analytics"))
):
    """Get training effectiveness analytics"""
    training_service = TrainingService(session)
    return await training_service.get_training_effectiveness(
        training_type=training_type,
        start_date=start_date,
        end_date=end_date
    )