"""
Recruitment service for managing job applications and hiring process
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status, UploadFile
from models.job_application import JobApplication, ApplicationStage, ApplicationSource
from models.employee import Employee
from schemas.job_application import (
    JobApplicationCreate, JobApplicationUpdate, JobApplicationResponse
)
from utils.upload import process_upload
from utils.notifications import send_recruitment_notification
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)


class RecruitmentService:
    """Service for handling recruitment and job application operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_application(
        self, 
        application_data: JobApplicationCreate,
        resume_file: Optional[UploadFile] = None
    ) -> JobApplicationResponse:
        """Create a new job application
        
        Args:
            application_data: Application creation data
            resume_file: Optional resume file upload
            
        Returns:
            Created job application
            
        Raises:
            HTTPException: If validation fails
        """
        # Check for duplicate applications (same email + position within 30 days)
        thirty_days_ago = date.today() - timedelta(days=30)
        existing_app = self.session.exec(
            select(JobApplication).where(
                and_(
                    JobApplication.email == application_data.email,
                    JobApplication.position_applied == application_data.position_applied,
                    JobApplication.created_at >= thirty_days_ago,
                    JobApplication.stage != ApplicationStage.REJECTED
                )
            )
        ).first()
        
        if existing_app:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate application found within 30 days"
            )
        
        # Process resume upload if provided
        resume_path = None
        if resume_file:
            try:
                upload_result = await process_upload(resume_file, "resumes")
                resume_path = upload_result["file_path"]
            except Exception as e:
                logger.error(f"Resume upload failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Resume upload failed: {str(e)}"
                )
        
        # Create application
        application = JobApplication(
            **application_data.model_dump(),
            resume_file_path=resume_path,
            stage=ApplicationStage.SCREENING
        )
        
        self.session.add(application)
        self.session.commit()
        self.session.refresh(application)
        
        # Send notification to recruiters
        try:
            await send_recruitment_notification(
                application_data={
                    "applicant_name": application.full_name,
                    "position": application.position_applied,
                    "source": application.source.value,
                    "email": application.email
                },
                notification_type="new_application"
            )
        except Exception as e:
            logger.error(f"Failed to send recruitment notification: {str(e)}")
        
        logger.info(f"Created job application {application.id} for {application.full_name}")
        return self._to_response(application)
    
    async def get_application(self, application_id: uuid.UUID) -> JobApplicationResponse:
        """Get job application by ID
        
        Args:
            application_id: Application UUID
            
        Returns:
            Job application details
            
        Raises:
            HTTPException: If application not found
        """
        application = self.session.get(JobApplication, application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found"
            )
        
        return self._to_response(application)
    
    async def get_applications(
        self,
        skip: int = 0,
        limit: int = 100,
        position: Optional[str] = None,
        stage: Optional[ApplicationStage] = None,
        source: Optional[ApplicationSource] = None,
        recruiter_id: Optional[uuid.UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[JobApplicationResponse]:
        """Get job applications with filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            position: Filter by position
            stage: Filter by application stage
            source: Filter by application source
            recruiter_id: Filter by assigned recruiter
            start_date: Filter applications from this date
            end_date: Filter applications until this date
            
        Returns:
            List of job applications
        """
        query = select(JobApplication)
        
        # Apply filters
        conditions = []
        
        if position:
            conditions.append(JobApplication.position_applied.ilike(f"%{position}%"))
        
        if stage:
            conditions.append(JobApplication.stage == stage)
        
        if source:
            conditions.append(JobApplication.source == source)
        
        if recruiter_id:
            conditions.append(JobApplication.assigned_recruiter == recruiter_id)
        
        if start_date:
            conditions.append(JobApplication.created_at >= start_date)
        
        if end_date:
            conditions.append(JobApplication.created_at <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(JobApplication.created_at.desc()).offset(skip).limit(limit)
        applications = self.session.exec(query).all()
        
        return [self._to_response(app) for app in applications]
    
    async def update_application(
        self, 
        application_id: uuid.UUID, 
        application_data: JobApplicationUpdate
    ) -> JobApplicationResponse:
        """Update job application
        
        Args:
            application_id: Application UUID
            application_data: Update data
            
        Returns:
            Updated job application
            
        Raises:
            HTTPException: If application not found
        """
        application = self.session.get(JobApplication, application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found"
            )
        
        # Update fields
        update_data = application_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(application, field, value)
        
        application.updated_at = datetime.utcnow()
        
        self.session.add(application)
        self.session.commit()
        self.session.refresh(application)
        
        logger.info(f"Updated job application {application_id}")
        return self._to_response(application)
    
    async def advance_stage(
        self, 
        application_id: uuid.UUID, 
        new_stage: ApplicationStage,
        notes: Optional[str] = None
    ) -> dict:
        """Advance application to next stage
        
        Args:
            application_id: Application UUID
            new_stage: New application stage
            notes: Optional notes about the stage change
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If application not found or invalid stage transition
        """
        application = self.session.get(JobApplication, application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found"
            )
        
        # Validate stage transition
        valid_transitions = {
            ApplicationStage.SCREENING: [ApplicationStage.INTERVIEW, ApplicationStage.REJECTED],
            ApplicationStage.INTERVIEW: [ApplicationStage.OFFER, ApplicationStage.REJECTED],
            ApplicationStage.OFFER: [ApplicationStage.HIRED, ApplicationStage.REJECTED],
            ApplicationStage.HIRED: [],  # Final stage
            ApplicationStage.REJECTED: []  # Final stage
        }
        
        if new_stage not in valid_transitions.get(application.stage, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid stage transition from {application.stage} to {new_stage}"
            )
        
        old_stage = application.stage
        application.stage = new_stage
        application.updated_at = datetime.utcnow()
        
        if notes:
            application.notes = f"{application.notes or ''}\n[{datetime.now()}] Stage changed from {old_stage} to {new_stage}: {notes}"
        
        self.session.add(application)
        self.session.commit()
        
        # Send notification for important stage changes
        if new_stage in [ApplicationStage.INTERVIEW, ApplicationStage.OFFER, ApplicationStage.HIRED]:
            try:
                await send_recruitment_notification(
                    application_data={
                        "applicant_name": application.full_name,
                        "position": application.position_applied,
                        "stage": new_stage.value,
                        "email": application.email
                    },
                    notification_type="stage_change"
                )
            except Exception as e:
                logger.error(f"Failed to send stage change notification: {str(e)}")
        
        logger.info(f"Advanced application {application_id} from {old_stage} to {new_stage}")
        return {"message": f"Application advanced to {new_stage}"}
    
    async def hire_applicant(
        self, 
        application_id: uuid.UUID,
        employee_data: Dict[str, Any]
    ) -> dict:
        """Hire applicant and create employee record
        
        Args:
            application_id: Application UUID
            employee_data: Employee creation data
            
        Returns:
            Success message with employee ID
            
        Raises:
            HTTPException: If application not found or cannot be hired
        """
        application = self.session.get(JobApplication, application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found"
            )
        
        if application.stage != ApplicationStage.OFFER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Application must be in OFFER stage to hire"
            )
        
        # Create employee record
        from services.employee_service import EmployeeService
        employee_service = EmployeeService(self.session)
        
        # Merge application data with employee data
        employee_create_data = {
            "full_name": application.full_name,
            "email": application.email,
            "phone": application.phone,
            "position": application.position_applied,
            **employee_data
        }
        
        try:
            employee = await employee_service.create_employee(employee_create_data)
            
            # Update application stage
            application.stage = ApplicationStage.HIRED
            application.updated_at = datetime.utcnow()
            application.notes = f"{application.notes or ''}\n[{datetime.now()}] Hired as employee {employee.id}"
            
            self.session.add(application)
            self.session.commit()
            
            logger.info(f"Hired applicant {application_id} as employee {employee.id}")
            return {
                "message": "Applicant hired successfully",
                "employee_id": str(employee.id)
            }
            
        except Exception as e:
            logger.error(f"Failed to hire applicant {application_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create employee record: {str(e)}"
            )
    
    async def reject_application(
        self, 
        application_id: uuid.UUID,
        rejection_reason: str
    ) -> dict:
        """Reject job application
        
        Args:
            application_id: Application UUID
            rejection_reason: Reason for rejection
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If application not found
        """
        application = self.session.get(JobApplication, application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found"
            )
        
        if application.stage in [ApplicationStage.HIRED, ApplicationStage.REJECTED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reject application in {application.stage} stage"
            )
        
        application.stage = ApplicationStage.REJECTED
        application.updated_at = datetime.utcnow()
        application.notes = f"{application.notes or ''}\n[{datetime.now()}] Rejected: {rejection_reason}"
        
        self.session.add(application)
        self.session.commit()
        
        # Send rejection notification
        try:
            await send_recruitment_notification(
                application_data={
                    "applicant_name": application.full_name,
                    "position": application.position_applied,
                    "email": application.email,
                    "rejection_reason": rejection_reason
                },
                notification_type="application_rejected"
            )
        except Exception as e:
            logger.error(f"Failed to send rejection notification: {str(e)}")
        
        logger.info(f"Rejected application {application_id}: {rejection_reason}")
        return {"message": "Application rejected successfully"}
    
    async def get_recruitment_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get recruitment analytics
        
        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            
        Returns:
            Recruitment analytics data
        """
        query = select(JobApplication)
        
        # Apply date filters
        conditions = []
        if start_date:
            conditions.append(JobApplication.created_at >= start_date)
        if end_date:
            conditions.append(JobApplication.created_at <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        applications = self.session.exec(query).all()
        
        # Calculate metrics
        total_applications = len(applications)
        hired_count = len([a for a in applications if a.stage == ApplicationStage.HIRED])
        rejected_count = len([a for a in applications if a.stage == ApplicationStage.REJECTED])
        
        # Conversion rates
        hire_rate = hired_count / total_applications * 100 if total_applications > 0 else 0
        rejection_rate = rejected_count / total_applications * 100 if total_applications > 0 else 0
        
        # By stage
        by_stage = {}
        for stage in ApplicationStage:
            count = len([a for a in applications if a.stage == stage])
            by_stage[stage.value] = count
        
        # By source
        by_source = {}
        for source in ApplicationSource:
            count = len([a for a in applications if a.source == source])
            by_source[source.value] = count
        
        # By position
        positions = {}
        for app in applications:
            positions[app.position_applied] = positions.get(app.position_applied, 0) + 1
        
        # Time to hire (for hired applications)
        hired_apps = [a for a in applications if a.stage == ApplicationStage.HIRED]
        if hired_apps:
            time_to_hire_days = []
            for app in hired_apps:
                if app.updated_at:
                    days = (app.updated_at.date() - app.created_at.date()).days
                    time_to_hire_days.append(days)
            
            avg_time_to_hire = sum(time_to_hire_days) / len(time_to_hire_days) if time_to_hire_days else 0
        else:
            avg_time_to_hire = 0
        
        return {
            "total_applications": total_applications,
            "hired_count": hired_count,
            "rejected_count": rejected_count,
            "hire_rate": hire_rate,
            "rejection_rate": rejection_rate,
            "avg_time_to_hire_days": avg_time_to_hire,
            "by_stage": by_stage,
            "by_source": by_source,
            "by_position": positions,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    async def delete_application(self, application_id: uuid.UUID) -> dict:
        """Delete job application
        
        Args:
            application_id: Application UUID
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If application not found
        """
        application = self.session.get(JobApplication, application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found"
            )
        
        # Delete resume file if exists
        if application.resume_file_path:
            from utils.upload import FileUploadHandler
            handler = FileUploadHandler()
            handler.delete_file(application.resume_file_path)
        
        self.session.delete(application)
        self.session.commit()
        
        logger.info(f"Deleted job application {application_id}")
        return {"message": "Job application deleted successfully"}
    
    def _to_response(self, application: JobApplication) -> JobApplicationResponse:
        """Convert application model to response schema
        
        Args:
            application: Application model
            
        Returns:
            Application response schema
        """
        return JobApplicationResponse(
            id=application.id,
            full_name=application.full_name,
            email=application.email,
            phone=application.phone,
            position_applied=application.position_applied,
            source=application.source,
            stage=application.stage,
            assigned_recruiter=application.assigned_recruiter,
            resume_file_path=application.resume_file_path,
            cover_letter=application.cover_letter,
            expected_salary=application.expected_salary,
            availability_date=application.availability_date,
            notes=application.notes,
            created_at=application.created_at,
            updated_at=application.updated_at
        )