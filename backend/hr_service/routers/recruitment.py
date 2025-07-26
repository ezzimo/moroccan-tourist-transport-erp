"""
Recruitment and job application routes
"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException, status
from sqlmodel import Session
from database import get_session, get_redis
from services.recruitment_service import RecruitmentService
from schemas.job_application import (
    JobApplicationCreate, JobApplicationUpdate, JobApplicationResponse,
    ApplicationStageUpdate, ApplicationEvaluation, ApplicationSearch, RecruitmentStats
)
from models.job_application import ApplicationSource, ApplicationStage, Priority
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional, Dict, Any
import redis
import uuid


router = APIRouter(prefix="/recruitment", tags=["Recruitment Management"])


@router.post("/applications", response_model=JobApplicationResponse)
async def create_job_application(
    application_data: JobApplicationCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "create", "applications"))
):
    """Create a new job application"""
    recruitment_service = RecruitmentService(session, redis_client)
    return await recruitment_service.create_application(application_data)


@router.post("/applications/upload", response_model=JobApplicationResponse)
async def create_application_with_files(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    position_applied: str = Form(...),
    department: str = Form(...),
    source: ApplicationSource = Form(...),
    national_id: Optional[str] = Form(None),
    years_of_experience: Optional[int] = Form(None),
    education_level: Optional[str] = Form(None),
    expected_salary: Optional[float] = Form(None),
    languages: Optional[str] = Form(None),  # JSON string
    skills: Optional[str] = Form(None),     # JSON string
    resume_file: Optional[UploadFile] = File(None),
    cover_letter_file: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "create", "applications"))
):
    """Create job application with file uploads"""
    recruitment_service = RecruitmentService(session, redis_client)
    
    # Parse JSON fields
    languages_list = []
    skills_list = []
    
    if languages:
        try:
            import json
            languages_list = json.loads(languages)
        except:
            pass
    
    if skills:
        try:
            import json
            skills_list = json.loads(skills)
        except:
            pass
    
    # Create application data
    application_data = JobApplicationCreate(
        full_name=full_name,
        email=email,
        phone=phone,
        national_id=national_id,
        position_applied=position_applied,
        department=department,
        source=source,
        years_of_experience=years_of_experience,
        education_level=education_level,
        expected_salary=expected_salary,
        languages=languages_list,
        skills=skills_list
    )
    
    return await recruitment_service.create_application_with_files(
        application_data, resume_file, cover_letter_file
    )


@router.get("/applications", response_model=PaginatedResponse[JobApplicationResponse])
async def get_job_applications(
    pagination: PaginationParams = Depends(),
    query: Optional[str] = Query(None, description="Search query"),
    position_applied: Optional[str] = Query(None, description="Filter by position"),
    department: Optional[str] = Query(None, description="Filter by department"),
    stage: Optional[ApplicationStage] = Query(None, description="Filter by stage"),
    source: Optional[ApplicationSource] = Query(None, description="Filter by source"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    assigned_recruiter_id: Optional[uuid.UUID] = Query(None, description="Filter by recruiter"),
    application_date_from: Optional[str] = Query(None, description="Filter by date from (YYYY-MM-DD)"),
    application_date_to: Optional[str] = Query(None, description="Filter by date to (YYYY-MM-DD)"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "applications"))
):
    """Get list of job applications with optional search and filters"""
    recruitment_service = RecruitmentService(session, redis_client)
    
    # Build search criteria
    search = None
    if any([query, position_applied, department, stage, source, priority, 
            assigned_recruiter_id, application_date_from, application_date_to, is_active is not None]):
        from datetime import datetime
        
        application_date_from_parsed = None
        application_date_to_parsed = None
        
        if application_date_from:
            try:
                application_date_from_parsed = datetime.strptime(application_date_from, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid application_date_from format. Use YYYY-MM-DD"
                )
        
        if application_date_to:
            try:
                application_date_to_parsed = datetime.strptime(application_date_to, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid application_date_to format. Use YYYY-MM-DD"
                )
        
        search = ApplicationSearch(
            query=query,
            position_applied=position_applied,
            department=department,
            stage=stage,
            source=source,
            priority=priority,
            assigned_recruiter_id=assigned_recruiter_id,
            application_date_from=application_date_from_parsed,
            application_date_to=application_date_to_parsed,
            is_active=is_active
        )
    
    applications, total = await recruitment_service.get_applications(pagination, search)
    
    return PaginatedResponse.create(
        items=applications,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/applications/{application_id}", response_model=JobApplicationResponse)
async def get_job_application(
    application_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "applications"))
):
    """Get job application by ID"""
    recruitment_service = RecruitmentService(session, redis_client)
    return await recruitment_service.get_application(application_id)


@router.put("/applications/{application_id}", response_model=JobApplicationResponse)
async def update_job_application(
    application_id: uuid.UUID,
    application_data: JobApplicationUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "update", "applications"))
):
    """Update job application information"""
    recruitment_service = RecruitmentService(session, redis_client)
    return await recruitment_service.update_application(application_id, application_data)


@router.post("/applications/{application_id}/stage", response_model=JobApplicationResponse)
async def update_application_stage(
    application_id: uuid.UUID,
    stage_update: ApplicationStageUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "update", "applications"))
):
    """Update application stage"""
    recruitment_service = RecruitmentService(session, redis_client)
    return await recruitment_service.update_stage(application_id, stage_update)


@router.post("/applications/{application_id}/evaluate", response_model=JobApplicationResponse)
async def evaluate_application(
    application_id: uuid.UUID,
    evaluation: ApplicationEvaluation,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "update", "applications"))
):
    """Evaluate job application"""
    recruitment_service = RecruitmentService(session, redis_client)
    return await recruitment_service.evaluate_application(application_id, evaluation)


@router.post("/applications/{application_id}/assign")
async def assign_recruiter(
    application_id: uuid.UUID,
    recruiter_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "update", "applications"))
):
    """Assign recruiter to application"""
    recruitment_service = RecruitmentService(session, redis_client)
    return await recruitment_service.assign_recruiter(application_id, recruiter_id)


@router.post("/applications/{application_id}/hire")
async def hire_applicant(
    application_id: uuid.UUID,
    employee_data: dict,  # Employee creation data
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "create", "employees"))
):
    """Hire applicant and create employee record"""
    recruitment_service = RecruitmentService(session, redis_client)
    return await recruitment_service.hire_applicant(application_id, employee_data, current_user.user_id)


@router.delete("/applications/{application_id}")
async def delete_job_application(
    application_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "delete", "applications"))
):
    """Delete job application"""
    recruitment_service = RecruitmentService(session, redis_client)
    return await recruitment_service.delete_application(application_id)


@router.get("/stats", response_model=RecruitmentStats)
async def get_recruitment_stats(
    days: int = Query(90, ge=1, le=365, description="Number of days for statistics"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "applications"))
):
    """Get recruitment statistics"""
    recruitment_service = RecruitmentService(session, redis_client)
    return await recruitment_service.get_recruitment_stats(days)


@router.get("/pipeline", response_model=List[dict])
async def get_recruitment_pipeline(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("hr", "read", "applications"))
):
    """Get recruitment pipeline overview"""
    recruitment_service = RecruitmentService(session, redis_client)
    return await recruitment_service.get_recruitment_pipeline()