"""
Training service for driver training management operations
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status, UploadFile
from models.driver_training import DriverTrainingRecord, TrainingType, TrainingStatus
from models.driver import Driver
from schemas.driver_training import (
    DriverTrainingCreate, DriverTrainingUpdate, DriverTrainingResponse
)
from utils.upload import process_upload
from utils.notifications import send_training_notification
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)


class TrainingService:
    """Service for handling driver training operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_training_record(
        self, 
        training_data: DriverTrainingCreate
    ) -> DriverTrainingResponse:
        """Create a new training record
        
        Args:
            training_data: Training creation data
            
        Returns:
            Created training record
            
        Raises:
            HTTPException: If validation fails or driver not found
        """
        # Verify driver exists
        driver = self.session.get(Driver, training_data.driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # Create training record
        training = DriverTrainingRecord(**training_data.model_dump())
        
        self.session.add(training)
        self.session.commit()
        self.session.refresh(training)
        
        # Send notification to driver
        try:
            await send_training_notification(
                driver_id=str(training.driver_id),
                training_data={
                    "driver_name": driver.full_name,
                    "training_title": training.training_title,
                    "training_type": training.training_type.value,
                    "scheduled_date": training.scheduled_date.isoformat(),
                    "location": training.location,
                    "trainer_name": training.trainer_name
                },
                notification_type="training_scheduled"
            )
        except Exception as e:
            logger.error(f"Failed to send training notification: {str(e)}")
        
        logger.info(f"Created training record {training.id} for driver {driver.full_name}")
        return self._to_response(training)
    
    async def get_training_record(self, training_id: uuid.UUID) -> DriverTrainingResponse:
        """Get training record by ID
        
        Args:
            training_id: Training UUID
            
        Returns:
            Training record details
            
        Raises:
            HTTPException: If training record not found
        """
        training = self.session.get(DriverTrainingRecord, training_id)
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training record not found"
            )
        
        return self._to_response(training)
    
    async def get_training_records(
        self,
        skip: int = 0,
        limit: int = 100,
        driver_id: Optional[uuid.UUID] = None,
        training_type: Optional[TrainingType] = None,
        status: Optional[TrainingStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        expiring_soon: bool = False
    ) -> List[DriverTrainingResponse]:
        """Get training records with filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            driver_id: Filter by driver ID
            training_type: Filter by training type
            status: Filter by training status
            start_date: Filter training from this date
            end_date: Filter training until this date
            expiring_soon: Show certificates expiring within 30 days
            
        Returns:
            List of training records
        """
        query = select(DriverTrainingRecord)
        
        # Apply filters
        conditions = []
        
        if driver_id:
            conditions.append(DriverTrainingRecord.driver_id == driver_id)
        
        if training_type:
            conditions.append(DriverTrainingRecord.training_type == training_type)
        
        if status:
            conditions.append(DriverTrainingRecord.status == status)
        
        if start_date:
            conditions.append(DriverTrainingRecord.scheduled_date >= start_date)
        
        if end_date:
            conditions.append(DriverTrainingRecord.scheduled_date <= end_date)
        
        if expiring_soon:
            alert_date = date.today() + timedelta(days=30)
            conditions.extend([
                DriverTrainingRecord.certificate_valid_until.is_not(None),
                DriverTrainingRecord.certificate_valid_until <= alert_date,
                DriverTrainingRecord.certificate_valid_until > date.today(),
                DriverTrainingRecord.certificate_issued == True
            ])
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(DriverTrainingRecord.scheduled_date.desc()).offset(skip).limit(limit)
        training_records = self.session.exec(query).all()
        
        return [self._to_response(record) for record in training_records]
    
    async def get_driver_training_history(
        self,
        driver_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        training_type: Optional[TrainingType] = None
    ) -> List[DriverTrainingResponse]:
        """Get training history for a specific driver
        
        Args:
            driver_id: Driver UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            training_type: Filter by training type
            
        Returns:
            List of driver training records
        """
        return await self.get_training_records(
            skip=skip,
            limit=limit,
            driver_id=driver_id,
            training_type=training_type
        )
    
    async def update_training_record(
        self, 
        training_id: uuid.UUID, 
        training_data: DriverTrainingUpdate
    ) -> DriverTrainingResponse:
        """Update training record
        
        Args:
            training_id: Training UUID
            training_data: Update data
            
        Returns:
            Updated training record
            
        Raises:
            HTTPException: If training record not found
        """
        training = self.session.get(DriverTrainingRecord, training_id)
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training record not found"
            )
        
        # Update fields
        update_data = training_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(training, field, value)
        
        training.updated_at = datetime.utcnow()
        
        self.session.add(training)
        self.session.commit()
        self.session.refresh(training)
        
        logger.info(f"Updated training record {training_id}")
        return self._to_response(training)
    
    async def complete_training(
        self,
        training_id: uuid.UUID,
        score: float,
        trainer_feedback: Optional[str] = None
    ) -> dict:
        """Mark training as completed with score
        
        Args:
            training_id: Training UUID
            score: Training score (0-100)
            trainer_feedback: Trainer's feedback
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If training not found or cannot be completed
        """
        training = self.session.get(DriverTrainingRecord, training_id)
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training record not found"
            )
        
        if training.status not in [TrainingStatus.SCHEDULED, TrainingStatus.IN_PROGRESS]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot complete training with status {training.status}"
            )
        
        if not (0 <= score <= 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Score must be between 0 and 100"
            )
        
        training.status = TrainingStatus.COMPLETED
        training.score = score
        training.trainer_feedback = trainer_feedback
        training.attendance_confirmed = True
        training.end_time = datetime.utcnow()
        training.updated_at = datetime.utcnow()
        
        # Issue certificate if passed
        if training.has_passed():
            training.certificate_issued = True
            # Set certificate validity (default 24 months)
            from config import settings
            validity_months = getattr(settings, 'training_validity_months', 24)
            training.certificate_valid_until = date.today() + timedelta(days=validity_months * 30)
        
        self.session.add(training)
        self.session.commit()
        
        logger.info(f"Completed training {training_id} with score {score}")
        return {
            "message": "Training completed successfully",
            "passed": training.has_passed(),
            "certificate_issued": training.certificate_issued
        }
    
    async def fail_training(
        self,
        training_id: uuid.UUID,
        trainer_feedback: Optional[str] = None
    ) -> dict:
        """Mark training as failed
        
        Args:
            training_id: Training UUID
            trainer_feedback: Trainer's feedback
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If training not found or cannot be failed
        """
        training = self.session.get(DriverTrainingRecord, training_id)
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training record not found"
            )
        
        if training.status not in [TrainingStatus.SCHEDULED, TrainingStatus.IN_PROGRESS]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot fail training with status {training.status}"
            )
        
        training.status = TrainingStatus.FAILED
        training.trainer_feedback = trainer_feedback
        training.attendance_confirmed = True
        training.end_time = datetime.utcnow()
        training.updated_at = datetime.utcnow()
        
        self.session.add(training)
        self.session.commit()
        
        logger.info(f"Failed training {training_id}")
        return {"message": "Training marked as failed"}
    
    async def upload_certificate(
        self,
        training_id: uuid.UUID,
        certificate_file: UploadFile,
        certificate_number: Optional[str] = None,
        valid_until: Optional[date] = None
    ) -> dict:
        """Upload training certificate
        
        Args:
            training_id: Training UUID
            certificate_file: Certificate file
            certificate_number: Certificate number
            valid_until: Certificate validity date
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If training not found or file upload fails
        """
        training = self.session.get(DriverTrainingRecord, training_id)
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training record not found"
            )
        
        if training.status != TrainingStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only upload certificate for completed training"
            )
        
        # Process file upload
        try:
            upload_result = await process_upload(certificate_file, training.driver_id)
        except Exception as e:
            logger.error(f"Certificate upload failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Certificate upload failed: {str(e)}"
            )
        
        # Update training record
        training.certificate_issued = True
        training.certificate_file_path = upload_result["file_path"]
        training.certificate_number = certificate_number
        training.certificate_valid_until = valid_until
        training.updated_at = datetime.utcnow()
        
        self.session.add(training)
        self.session.commit()
        
        logger.info(f"Uploaded certificate for training {training_id}")
        return {
            "message": "Certificate uploaded successfully",
            "file_path": upload_result["file_path"]
        }
    
    async def get_expiring_certificates(
        self, 
        days: int = 30, 
        training_type: Optional[TrainingType] = None
    ) -> List[DriverTrainingResponse]:
        """Get training certificates expiring within specified days
        
        Args:
            days: Number of days to look ahead
            training_type: Filter by training type
            
        Returns:
            List of expiring certificates
        """
        return await self.get_training_records(
            expiring_soon=True,
            training_type=training_type,
            limit=1000  # Get all expiring certificates
        )
    
    async def get_compliance_report(
        self, 
        training_type: Optional[TrainingType] = None
    ) -> Dict[str, Any]:
        """Get training compliance report
        
        Args:
            training_type: Filter by training type
            
        Returns:
            Compliance report data
        """
        query = select(DriverTrainingRecord)
        
        if training_type:
            query = query.where(DriverTrainingRecord.training_type == training_type)
        
        training_records = self.session.exec(query).all()
        
        # Calculate compliance metrics
        total_trainings = len(training_records)
        completed_trainings = len([t for t in training_records if t.status == TrainingStatus.COMPLETED])
        failed_trainings = len([t for t in training_records if t.status == TrainingStatus.FAILED])
        certificates_issued = len([t for t in training_records if t.certificate_issued])
        
        # Expiring certificates
        alert_date = date.today() + timedelta(days=30)
        expiring_certificates = len([
            t for t in training_records 
            if t.certificate_valid_until and t.certificate_valid_until <= alert_date and t.certificate_valid_until > date.today()
        ])
        
        # Calculate rates
        completion_rate = completed_trainings / total_trainings * 100 if total_trainings > 0 else 0
        pass_rate = len([t for t in training_records if t.has_passed()]) / total_trainings * 100 if total_trainings > 0 else 0
        
        # Average score
        scores = [t.score for t in training_records if t.score is not None]
        average_score = sum(scores) / len(scores) if scores else None
        
        # By training type
        by_training_type = {}
        for record in training_records:
            training_type_name = record.training_type.value
            if training_type_name not in by_training_type:
                by_training_type[training_type_name] = {
                    "total": 0,
                    "completed": 0,
                    "failed": 0,
                    "certificates_issued": 0
                }
            
            by_training_type[training_type_name]["total"] += 1
            if record.status == TrainingStatus.COMPLETED:
                by_training_type[training_type_name]["completed"] += 1
            elif record.status == TrainingStatus.FAILED:
                by_training_type[training_type_name]["failed"] += 1
            if record.certificate_issued:
                by_training_type[training_type_name]["certificates_issued"] += 1
        
        return {
            "total_trainings": total_trainings,
            "completed_trainings": completed_trainings,
            "failed_trainings": failed_trainings,
            "certificates_issued": certificates_issued,
            "expiring_certificates": expiring_certificates,
            "completion_rate": completion_rate,
            "pass_rate": pass_rate,
            "average_score": average_score,
            "by_training_type": by_training_type,
            "compliance_summary": {
                "compliant_drivers": certificates_issued,
                "non_compliant_drivers": total_trainings - certificates_issued,
                "compliance_percentage": certificates_issued / total_trainings * 100 if total_trainings > 0 else 0
            }
        }
    
    async def delete_training_record(self, training_id: uuid.UUID) -> dict:
        """Delete training record
        
        Args:
            training_id: Training UUID
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If training record not found
        """
        training = self.session.get(DriverTrainingRecord, training_id)
        if not training:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training record not found"
            )
        
        # Delete certificate file if exists
        if training.certificate_file_path:
            from utils.upload import FileUploadHandler
            handler = FileUploadHandler()
            handler.delete_file(training.certificate_file_path)
        
        self.session.delete(training)
        self.session.commit()
        
        logger.info(f"Deleted training record {training_id}")
        return {"message": "Training record deleted successfully"}
    
    async def get_training_effectiveness(
        self,
        training_type: Optional[TrainingType] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get training effectiveness analytics
        
        Args:
            training_type: Filter by training type
            start_date: Analytics start date
            end_date: Analytics end date
            
        Returns:
            Training effectiveness data
        """
        query = select(DriverTrainingRecord)
        
        conditions = []
        if training_type:
            conditions.append(DriverTrainingRecord.training_type == training_type)
        if start_date:
            conditions.append(DriverTrainingRecord.scheduled_date >= start_date)
        if end_date:
            conditions.append(DriverTrainingRecord.scheduled_date <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        training_records = self.session.exec(query).all()
        
        # Calculate effectiveness metrics
        total_trainings = len(training_records)
        completed_trainings = len([t for t in training_records if t.status == TrainingStatus.COMPLETED])
        
        # Score analysis
        scores = [t.score for t in training_records if t.score is not None]
        if scores:
            average_score = sum(scores) / len(scores)
            min_score = min(scores)
            max_score = max(scores)
            
            # Score distribution
            score_ranges = {
                "90-100": len([s for s in scores if 90 <= s <= 100]),
                "80-89": len([s for s in scores if 80 <= s < 90]),
                "70-79": len([s for s in scores if 70 <= s < 80]),
                "60-69": len([s for s in scores if 60 <= s < 70]),
                "Below 60": len([s for s in scores if s < 60])
            }
        else:
            average_score = min_score = max_score = None
            score_ranges = {}
        
        # Effectiveness by training type
        effectiveness_by_type = {}
        for record in training_records:
            type_name = record.training_type.value
            if type_name not in effectiveness_by_type:
                effectiveness_by_type[type_name] = {
                    "total": 0,
                    "completed": 0,
                    "average_score": 0,
                    "pass_rate": 0
                }
            
            effectiveness_by_type[type_name]["total"] += 1
            if record.status == TrainingStatus.COMPLETED:
                effectiveness_by_type[type_name]["completed"] += 1
        
        # Calculate rates for each type
        for type_data in effectiveness_by_type.values():
            if type_data["total"] > 0:
                type_data["completion_rate"] = type_data["completed"] / type_data["total"] * 100
                
                # Calculate average score for this type
                type_scores = [
                    t.score for t in training_records 
                    if t.training_type.value == type_name and t.score is not None
                ]
                if type_scores:
                    type_data["average_score"] = sum(type_scores) / len(type_scores)
                    type_data["pass_rate"] = len([s for s in type_scores if s >= 70]) / len(type_scores) * 100
        
        return {
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "overall_metrics": {
                "total_trainings": total_trainings,
                "completed_trainings": completed_trainings,
                "completion_rate": completed_trainings / total_trainings * 100 if total_trainings > 0 else 0,
                "average_score": average_score,
                "min_score": min_score,
                "max_score": max_score
            },
            "score_distribution": score_ranges,
            "effectiveness_by_type": effectiveness_by_type,
            "recommendations": self._generate_training_recommendations(training_records)
        }
    
    def _generate_training_recommendations(self, training_records: List[DriverTrainingRecord]) -> List[str]:
        """Generate training recommendations based on data analysis
        
        Args:
            training_records: List of training records
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if not training_records:
            return ["No training data available for analysis"]
        
        # Analyze completion rates
        total_trainings = len(training_records)
        completed_trainings = len([t for t in training_records if t.status == TrainingStatus.COMPLETED])
        completion_rate = completed_trainings / total_trainings * 100 if total_trainings > 0 else 0
        
        if completion_rate < 80:
            recommendations.append("Consider reviewing training scheduling and attendance policies")
        
        # Analyze scores
        scores = [t.score for t in training_records if t.score is not None]
        if scores:
            average_score = sum(scores) / len(scores)
            if average_score < 75:
                recommendations.append("Training content may need improvement - average scores are below target")
            
            low_scores = len([s for s in scores if s < 60])
            if low_scores / len(scores) > 0.2:
                recommendations.append("High failure rate detected - consider additional support for struggling drivers")
        
        # Analyze by training type
        type_performance = {}
        for record in training_records:
            type_name = record.training_type.value
            if type_name not in type_performance:
                type_performance[type_name] = []
            if record.score is not None:
                type_performance[type_name].append(record.score)
        
        for training_type, scores in type_performance.items():
            if scores and sum(scores) / len(scores) < 70:
                recommendations.append(f"{training_type} training shows low performance - review curriculum")
        
        if not recommendations:
            recommendations.append("Training performance is meeting targets - continue current approach")
        
        return recommendations
    
    def _to_response(self, training: DriverTrainingRecord) -> DriverTrainingResponse:
        """Convert training model to response schema
        
        Args:
            training: Training model
            
        Returns:
            Training response schema
        """
        return DriverTrainingResponse(
            id=training.id,
            driver_id=training.driver_id,
            training_type=training.training_type,
            training_title=training.training_title,
            description=training.description,
            scheduled_date=training.scheduled_date,
            start_time=training.start_time,
            end_time=training.end_time,
            duration_hours=training.duration_hours,
            trainer_name=training.trainer_name,
            training_provider=training.training_provider,
            location=training.location,
            status=training.status,
            attendance_confirmed=training.attendance_confirmed,
            score=training.score,
            pass_score=training.pass_score,
            certificate_issued=training.certificate_issued,
            certificate_number=training.certificate_number,
            certificate_valid_until=training.certificate_valid_until,
            certificate_file_path=training.certificate_file_path,
            cost=training.cost,
            currency=training.currency,
            mandatory=training.mandatory,
            trainer_feedback=training.trainer_feedback,
            driver_feedback=training.driver_feedback,
            notes=training.notes,
            created_at=training.created_at,
            updated_at=training.updated_at,
            has_passed=training.has_passed(),
            is_certificate_valid=training.is_certificate_valid(),
            days_until_certificate_expiry=training.days_until_certificate_expiry(),
            training_effectiveness=training.get_training_effectiveness()
        )