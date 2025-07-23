"""
Training program and employee training routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session, get_redis
from services.training_service import TrainingService
from schemas.training_program import (
    TrainingProgramCreate, TrainingProgramUpdate, TrainingProgramResponse,
    TrainingProgramSummary, TrainingSearch, TrainingStats
)
from schemas.employee_training import (
    EmployeeTrainingCreate, EmployeeTrainingUpdate, EmployeeTrainingResponse,
    EmployeeTrainingWithDetails, TrainingEnrollment, TrainingCompletion, CertificateRequest
)
from models.training_program import TrainingCategory, TrainingStatus, DeliveryMethod
from models.employee_training import AttendanceStatus, CompletionStatus
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import redis
import uuid


router = APIRouter(prefix="/training", tags=["Training Management"])


# Training Program endpoints
@router.post("/programs", response_model=TrainingProgramResponse)
async def create_training_program(
    program_data: TrainingProgramCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "create", "training"))
):
    """Create a new training program"""
    training_service = TrainingService(session, redis_client)
    return await training_service.create_program(program_data)


@router.get("/programs", response_model=PaginatedResponse[TrainingProgramResponse])
async def get_training_programs(
    pagination: PaginationParams = Depends(),
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[TrainingCategory] = Query(None, description="Filter by category"),
    delivery_method: Optional[DeliveryMethod] = Query(None, description="Filter by delivery method"),
    status: Optional[TrainingStatus] = Query(None, description="Filter by status"),
    trainer_name: Optional[str] = Query(None, description="Filter by trainer"),
    start_date_from: Optional[str] = Query(None, description="Filter by start date from (YYYY-MM-DD)"),
    start_date_to: Optional[str] = Query(None, description="Filter by start date to (YYYY-MM-DD)"),
    is_mandatory: Optional[bool] = Query(None, description="Filter by mandatory status"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "training"))
):
    """Get list of training programs with optional search and filters"""
    training_service = TrainingService(session, redis_client)
    
    # Build search criteria
    search = None
    if any([query, category, delivery_method, status, trainer_name, 
            start_date_from, start_date_to, is_mandatory is not None, is_active is not None]):
        from datetime import datetime
        
        start_date_from_parsed = None
        start_date_to_parsed = None
        
        if start_date_from:
            try:
                start_date_from_parsed = datetime.strptime(start_date_from, "%Y-%m-%d").date()
            except ValueError:
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date_from format. Use YYYY-MM-DD"
                )
        
        if start_date_to:
            try:
                start_date_to_parsed = datetime.strptime(start_date_to, "%Y-%m-%d").date()
            except ValueError:
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date_to format. Use YYYY-MM-DD"
                )
        
        search = TrainingSearch(
            query=query,
            category=category,
            delivery_method=delivery_method,
            status=status,
            trainer_name=trainer_name,
            start_date_from=start_date_from_parsed,
            start_date_to=start_date_to_parsed,
            is_mandatory=is_mandatory,
            is_active=is_active
        )
    
    programs, total = await training_service.get_programs(pagination, search)
    
    return PaginatedResponse.create(
        items=programs,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/programs/{program_id}", response_model=TrainingProgramResponse)
async def get_training_program(
    program_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "training"))
):
    """Get training program by ID"""
    training_service = TrainingService(session, redis_client)
    return await training_service.get_program(program_id)


@router.get("/programs/{program_id}/summary", response_model=TrainingProgramSummary)
async def get_training_program_summary(
    program_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "training"))
):
    """Get comprehensive training program summary"""
    training_service = TrainingService(session, redis_client)
    return await training_service.get_program_summary(program_id)


@router.put("/programs/{program_id}", response_model=TrainingProgramResponse)
async def update_training_program(
    program_id: uuid.UUID,
    program_data: TrainingProgramUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "update", "training"))
):
    """Update training program information"""
    training_service = TrainingService(session, redis_client)
    return await training_service.update_program(program_id, program_data)


@router.delete("/programs/{program_id}")
async def delete_training_program(
    program_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "delete", "training"))
):
    """Delete training program"""
    training_service = TrainingService(session, redis_client)
    return await training_service.delete_program(program_id)


# Employee Training endpoints
@router.post("/enrollments", response_model=List[EmployeeTrainingResponse])
async def enroll_employees(
    enrollment: TrainingEnrollment,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "create", "training"))
):
    """Enroll employees in training program"""
    training_service = TrainingService(session, redis_client)
    return await training_service.enroll_employees(enrollment, current_user.user_id)


@router.get("/enrollments", response_model=PaginatedResponse[EmployeeTrainingWithDetails])
async def get_employee_trainings(
    pagination: PaginationParams = Depends(),
    employee_id: Optional[uuid.UUID] = Query(None, description="Filter by employee"),
    training_program_id: Optional[uuid.UUID] = Query(None, description="Filter by training program"),
    attendance_status: Optional[AttendanceStatus] = Query(None, description="Filter by attendance status"),
    completion_status: Optional[CompletionStatus] = Query(None, description="Filter by completion status"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "training"))
):
    """Get list of employee training records"""
    training_service = TrainingService(session, redis_client)
    
    trainings, total = await training_service.get_employee_trainings(
        pagination=pagination,
        employee_id=employee_id,
        training_program_id=training_program_id,
        attendance_status=attendance_status,
        completion_status=completion_status
    )
    
    return PaginatedResponse.create(
        items=trainings,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/enrollments/{training_id}", response_model=EmployeeTrainingResponse)
async def get_employee_training(
    training_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "training"))
):
    """Get employee training record by ID"""
    training_service = TrainingService(session, redis_client)
    return await training_service.get_employee_training(training_id)


@router.put("/enrollments/{training_id}", response_model=EmployeeTrainingResponse)
async def update_employee_training(
    training_id: uuid.UUID,
    training_data: EmployeeTrainingUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "update", "training"))
):
    """Update employee training record"""
    training_service = TrainingService(session, redis_client)
    return await training_service.update_employee_training(training_id, training_data)


@router.post("/enrollments/{training_id}/complete", response_model=EmployeeTrainingResponse)
async def complete_training(
    training_id: uuid.UUID,
    completion: TrainingCompletion,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "update", "training"))
):
    """Mark training as completed"""
    training_service = TrainingService(session, redis_client)
    return await training_service.complete_training(training_id, completion)


@router.post("/certificates/generate")
async def generate_certificate(
    certificate_request: CertificateRequest,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "create", "certificates"))
):
    """Generate training certificate"""
    training_service = TrainingService(session, redis_client)
    return await training_service.generate_certificate(certificate_request, current_user.user_id)


@router.get("/employee/{employee_id}", response_model=List[EmployeeTrainingWithDetails])
async def get_employee_training_history(
    employee_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "training"))
):
    """Get training history for an employee"""
    training_service = TrainingService(session, redis_client)
    return await training_service.get_employee_training_history(employee_id)


@router.get("/stats", response_model=TrainingStats)
async def get_training_stats(
    days: int = Query(365, ge=1, le=1095, description="Number of days for statistics"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "training"))
):
    """Get training statistics"""
    training_service = TrainingService(session, redis_client)
    return await training_service.get_training_stats(days)


@router.get("/upcoming", response_model=List[TrainingProgramResponse])
async def get_upcoming_trainings(
    days_ahead: int = Query(30, ge=1, le=365, description="Days ahead to check"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "training"))
):
    """Get upcoming training programs"""
    training_service = TrainingService(session, redis_client)
    return await training_service.get_upcoming_trainings(days_ahead)