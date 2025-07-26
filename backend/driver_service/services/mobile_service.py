"""
Mobile service for driver mobile app operations
"""
from sqlmodel import Session, select, and_, or_
from fastapi import HTTPException, status
from models.driver import Driver
from models.driver_assignment import DriverAssignment, AssignmentStatus
from models.driver_training import DriverTrainingRecord
from models.driver_document import DriverDocument
from models.driver_incident import DriverIncident
from schemas.mobile import (
    DriverDashboard, AssignmentDetails, OfflineDataBundle,
    StatusUpdate, IncidentReport, NotificationItem, PerformanceMetrics
)
from schemas.driver_assignment import DriverAssignmentResponse
from schemas.driver import DriverResponse
from services.driver_service import DriverService
from services.assignment_service import AssignmentService
from services.incident_service import IncidentService
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)


class MobileService:
    """Service for handling mobile app operations"""
    
    def __init__(self, session: Session):
        self.session = session
        self.driver_service = DriverService(session)
        self.assignment_service = AssignmentService(session)
        self.incident_service = IncidentService(session)
    
    async def get_driver_dashboard(self, driver_user_id: uuid.UUID) -> DriverDashboard:
        """Get driver dashboard data for mobile app
        
        Args:
            driver_user_id: User ID of the driver
            
        Returns:
            Driver dashboard data
            
        Raises:
            HTTPException: If driver not found
        """
        # Find driver by user ID (assuming there's a user_id field or relationship)
        # For now, we'll use the driver_id directly
        driver = self.session.get(Driver, driver_user_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # Get today's assignments
        today = date.today()
        today_assignments = await self.assignment_service.get_assignments(
            driver_id=driver.id,
            start_date=today,
            end_date=today,
            limit=10
        )
        
        # Get upcoming assignments (next 7 days)
        upcoming_assignments = await self.assignment_service.get_assignments(
            driver_id=driver.id,
            start_date=today + timedelta(days=1),
            end_date=today + timedelta(days=7),
            limit=10
        )
        
        # Get unread notifications count (mock for now)
        unread_notifications = 0  # This would come from notification service
        
        # Generate alerts
        alerts = []
        
        # License expiry alert
        if driver.days_until_license_expiry() <= 30:
            alerts.append(f"License expires in {driver.days_until_license_expiry()} days")
        
        # Health certificate expiry alert
        if driver.days_until_health_cert_expiry() and driver.days_until_health_cert_expiry() <= 60:
            alerts.append(f"Health certificate expires in {driver.days_until_health_cert_expiry()} days")
        
        return DriverDashboard(
            driver=self.driver_service._to_response(driver),
            today_assignments=today_assignments,
            upcoming_assignments=upcoming_assignments,
            unread_notifications=unread_notifications,
            performance_score=driver.calculate_performance_score(),
            total_tours_completed=driver.total_tours_completed,
            license_expiry_days=driver.days_until_license_expiry(),
            health_cert_expiry_days=driver.days_until_health_cert_expiry(),
            alerts=alerts
        )
    
    async def get_driver_assignments(
        self,
        driver_user_id: uuid.UUID,
        status: Optional[AssignmentStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[DriverAssignmentResponse]:
        """Get assignments for a driver
        
        Args:
            driver_user_id: User ID of the driver
            status: Filter by assignment status
            start_date: Filter from this date
            end_date: Filter until this date
            
        Returns:
            List of driver assignments
        """
        return await self.assignment_service.get_assignments(
            driver_id=driver_user_id,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
    
    async def get_assignment_details(
        self,
        assignment_id: uuid.UUID,
        driver_user_id: uuid.UUID
    ) -> AssignmentDetails:
        """Get detailed assignment information with itinerary
        
        Args:
            assignment_id: Assignment UUID
            driver_user_id: User ID of the driver
            
        Returns:
            Detailed assignment information
            
        Raises:
            HTTPException: If assignment not found or not authorized
        """
        assignment = await self.assignment_service.get_assignment(assignment_id)
        
        # Verify assignment belongs to the driver
        if assignment.driver_id != driver_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this assignment"
            )
        
        # Mock itinerary data (would come from tour service)
        itinerary = [
            {
                "time": "09:00",
                "activity": "Pick up from hotel",
                "location": assignment.pickup_location or "Hotel Pickup",
                "duration": 30,
                "notes": "Check guest list and luggage"
            },
            {
                "time": "10:00",
                "activity": "Tour start",
                "location": "Main attraction",
                "duration": 180,
                "notes": "Provide commentary in requested languages"
            },
            {
                "time": "13:00",
                "activity": "Lunch break",
                "location": "Restaurant",
                "duration": 60,
                "notes": "Traditional Moroccan cuisine"
            },
            {
                "time": "16:00",
                "activity": "Drop off",
                "location": assignment.dropoff_location or "Hotel Drop-off",
                "duration": 30,
                "notes": "Collect feedback and tips"
            }
        ]
        
        # Mock vehicle info (would come from fleet service)
        vehicle_info = {
            "vehicle_id": str(assignment.vehicle_id) if assignment.vehicle_id else None,
            "make": "Mercedes",
            "model": "Sprinter",
            "license_plate": "123-ABC-45",
            "capacity": 16
        } if assignment.vehicle_id else None
        
        # Mock customer info (would come from booking service)
        customer_info = {
            "name": "John Smith",
            "phone": "+1234567890",
            "email": "john@example.com",
            "group_size": 4,
            "languages": ["English", "French"]
        }
        
        # Emergency contacts
        emergency_contacts = [
            {"name": "Dispatch Center", "phone": "+212-123-456-789"},
            {"name": "Tour Manager", "phone": "+212-987-654-321"},
            {"name": "Emergency Services", "phone": "15"}
        ]
        
        # Special requirements
        special_requirements = []
        if assignment.special_instructions:
            special_requirements.append(assignment.special_instructions)
        
        return AssignmentDetails(
            assignment=assignment,
            itinerary=itinerary,
            vehicle_info=vehicle_info,
            customer_info=customer_info,
            emergency_contacts=emergency_contacts,
            special_requirements=special_requirements
        )
    
    async def update_assignment_status(
        self,
        assignment_id: uuid.UUID,
        status: AssignmentStatus,
        notes: Optional[str] = None,
        location: Optional[str] = None,
        driver_user_id: uuid.UUID = None
    ) -> dict:
        """Update assignment status from mobile app
        
        Args:
            assignment_id: Assignment UUID
            status: New assignment status
            notes: Status update notes
            location: Current location
            driver_user_id: User ID of the driver
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If assignment not found or not authorized
        """
        assignment = await self.assignment_service.get_assignment(assignment_id)
        
        # Verify assignment belongs to the driver
        if assignment.driver_id != driver_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this assignment"
            )
        
        # Update assignment based on status
        if status == AssignmentStatus.CONFIRMED:
            return await self.assignment_service.confirm_assignment(assignment_id)
        elif status == AssignmentStatus.IN_PROGRESS:
            return await self.assignment_service.start_assignment(assignment_id)
        elif status == AssignmentStatus.COMPLETED:
            return await self.assignment_service.complete_assignment(assignment_id)
        elif status == AssignmentStatus.CANCELLED:
            return await self.assignment_service.cancel_assignment(assignment_id, notes)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update to status {status} from mobile app"
            )
    
    async def get_today_assignments(self, driver_user_id: uuid.UUID) -> List[DriverAssignmentResponse]:
        """Get today's assignments for the driver
        
        Args:
            driver_user_id: User ID of the driver
            
        Returns:
            List of today's assignments
        """
        today = date.today()
        return await self.assignment_service.get_assignments(
            driver_id=driver_user_id,
            start_date=today,
            end_date=today
        )
    
    async def get_upcoming_assignments(
        self,
        driver_user_id: uuid.UUID,
        days: int = 7
    ) -> List[DriverAssignmentResponse]:
        """Get upcoming assignments for the driver
        
        Args:
            driver_user_id: User ID of the driver
            days: Number of days to look ahead
            
        Returns:
            List of upcoming assignments
        """
        start_date = date.today() + timedelta(days=1)
        end_date = date.today() + timedelta(days=days)
        
        return await self.assignment_service.get_assignments(
            driver_id=driver_user_id,
            start_date=start_date,
            end_date=end_date
        )
    
    async def report_incident(
        self,
        incident_report: IncidentReport,
        driver_user_id: uuid.UUID
    ) -> dict:
        """Report an incident from mobile app
        
        Args:
            incident_report: Incident report data
            driver_user_id: User ID of the driver
            
        Returns:
            Success message with incident ID
        """
        from schemas.driver_incident import DriverIncidentCreate
        
        incident_data = DriverIncidentCreate(
            driver_id=driver_user_id,
            assignment_id=incident_report.assignment_id,
            incident_type=incident_report.incident_type,
            severity=incident_report.severity,
            title=incident_report.title,
            description=incident_report.description,
            incident_date=date.today(),
            incident_time=datetime.now(),
            location=incident_report.location,
            witness_names=incident_report.witness_names,
            customer_involved=incident_report.customer_involved,
            customer_name=incident_report.customer_name,
            customer_contact=incident_report.customer_contact,
            photos_taken=incident_report.photos_taken
        )
        
        incident = await self.incident_service.create_incident(incident_data, driver_user_id)
        
        return {
            "message": "Incident reported successfully",
            "incident_id": str(incident.id)
        }
    
    async def get_driver_profile(self, driver_user_id: uuid.UUID) -> DriverResponse:
        """Get current driver's profile information
        
        Args:
            driver_user_id: User ID of the driver
            
        Returns:
            Driver profile information
        """
        return await self.driver_service.get_driver(driver_user_id)
    
    async def get_driver_documents(self, driver_user_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get current driver's documents and certificates
        
        Args:
            driver_user_id: User ID of the driver
            
        Returns:
            List of driver documents
        """
        from services.document_service import DocumentService
        
        document_service = DocumentService(self.session)
        documents = await document_service.get_driver_documents(driver_user_id)
        
        return [
            {
                "id": str(doc.id),
                "type": doc.document_type,
                "title": doc.title,
                "status": doc.status,
                "expiry_date": doc.expiry_date.isoformat() if doc.expiry_date else None,
                "days_until_expiry": doc.days_until_expiry,
                "is_expired": doc.is_expired
            }
            for doc in documents
        ]
    
    async def get_driver_training(self, driver_user_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get current driver's training records
        
        Args:
            driver_user_id: User ID of the driver
            
        Returns:
            List of training records
        """
        query = select(DriverTrainingRecord).where(
            DriverTrainingRecord.driver_id == driver_user_id
        ).order_by(DriverTrainingRecord.scheduled_date.desc())
        
        training_records = self.session.exec(query).all()
        
        return [
            {
                "id": str(record.id),
                "type": record.training_type,
                "title": record.training_title,
                "date": record.scheduled_date.isoformat(),
                "status": record.status,
                "score": record.score,
                "certificate_valid_until": record.certificate_valid_until.isoformat() if record.certificate_valid_until else None,
                "has_passed": record.has_passed(),
                "is_certificate_valid": record.is_certificate_valid()
            }
            for record in training_records
        ]
    
    async def get_offline_data_bundle(
        self,
        driver_user_id: uuid.UUID,
        days: int = 7
    ) -> OfflineDataBundle:
        """Get offline data bundle for mobile app
        
        Args:
            driver_user_id: User ID of the driver
            days: Number of days of data to include
            
        Returns:
            Offline data bundle
        """
        # Get driver profile
        driver_profile = await self.get_driver_profile(driver_user_id)
        
        # Get assignments for the specified period
        start_date = date.today()
        end_date = date.today() + timedelta(days=days)
        assignments = await self.assignment_service.get_assignments(
            driver_id=driver_user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Get documents
        documents = await self.get_driver_documents(driver_user_id)
        
        # Get training records
        training_records = await self.get_driver_training(driver_user_id)
        
        # Emergency contacts
        emergency_contacts = [
            {"name": "Dispatch Center", "phone": "+212-123-456-789"},
            {"name": "Emergency Services", "phone": "15"},
            {"name": "Company Support", "phone": "+212-987-654-321"}
        ]
        
        # Company policies (mock data)
        company_policies = [
            {"title": "Safety Guidelines", "content": "Always prioritize passenger safety..."},
            {"title": "Customer Service", "content": "Provide excellent service to all guests..."},
            {"title": "Emergency Procedures", "content": "In case of emergency, follow these steps..."}
        ]
        
        expires_at = datetime.now() + timedelta(hours=24)  # Bundle expires in 24 hours
        
        return OfflineDataBundle(
            driver_profile=driver_profile,
            assignments=assignments,
            documents=documents,
            training_records=training_records,
            emergency_contacts=emergency_contacts,
            company_policies=company_policies,
            last_sync=datetime.now(),
            expires_at=expires_at
        )
    
    async def sync_offline_data(
        self,
        sync_data: Dict[str, Any],
        driver_user_id: uuid.UUID
    ) -> dict:
        """Sync offline data changes back to server
        
        Args:
            sync_data: Offline data changes
            driver_user_id: User ID of the driver
            
        Returns:
            Sync results
        """
        results = {
            "synced_items": 0,
            "failed_items": 0,
            "errors": []
        }
        
        # Process assignment status updates
        if "assignment_updates" in sync_data:
            for update in sync_data["assignment_updates"]:
                try:
                    await self.update_assignment_status(
                        assignment_id=uuid.UUID(update["assignment_id"]),
                        status=AssignmentStatus(update["status"]),
                        notes=update.get("notes"),
                        location=update.get("location"),
                        driver_user_id=driver_user_id
                    )
                    results["synced_items"] += 1
                except Exception as e:
                    results["failed_items"] += 1
                    results["errors"].append(f"Assignment update failed: {str(e)}")
        
        # Process incident reports
        if "incident_reports" in sync_data:
            for report_data in sync_data["incident_reports"]:
                try:
                    incident_report = IncidentReport(**report_data)
                    await self.report_incident(incident_report, driver_user_id)
                    results["synced_items"] += 1
                except Exception as e:
                    results["failed_items"] += 1
                    results["errors"].append(f"Incident report failed: {str(e)}")
        
        logger.info(f"Synced {results['synced_items']} items for driver {driver_user_id}")
        return results
    
    async def get_driver_notifications(
        self,
        driver_user_id: uuid.UUID,
        unread_only: bool = False,
        limit: int = 20
    ) -> List[NotificationItem]:
        """Get driver notifications
        
        Args:
            driver_user_id: User ID of the driver
            unread_only: Show only unread notifications
            limit: Maximum number of notifications
            
        Returns:
            List of notifications
        """
        # Mock notifications (would come from notification service)
        notifications = [
            NotificationItem(
                id=uuid.uuid4(),
                title="New Assignment",
                message="You have been assigned to Tour ABC123",
                type="assignment",
                priority="high",
                is_read=False,
                created_at=datetime.now() - timedelta(hours=2)
            ),
            NotificationItem(
                id=uuid.uuid4(),
                title="License Expiry Reminder",
                message="Your license expires in 15 days",
                type="compliance",
                priority="medium",
                is_read=True,
                created_at=datetime.now() - timedelta(days=1)
            )
        ]
        
        if unread_only:
            notifications = [n for n in notifications if not n.is_read]
        
        return notifications[:limit]
    
    async def mark_notification_read(
        self,
        notification_id: uuid.UUID,
        driver_user_id: uuid.UUID
    ) -> dict:
        """Mark notification as read
        
        Args:
            notification_id: Notification UUID
            driver_user_id: User ID of the driver
            
        Returns:
            Success message
        """
        # This would update the notification service
        logger.info(f"Marked notification {notification_id} as read for driver {driver_user_id}")
        return {"message": "Notification marked as read"}
    
    async def get_driver_performance_metrics(
        self,
        driver_user_id: uuid.UUID,
        months: int = 6
    ) -> PerformanceMetrics:
        """Get current driver's performance metrics
        
        Args:
            driver_user_id: User ID of the driver
            months: Number of months to analyze
            
        Returns:
            Performance metrics
        """
        driver = self.session.get(Driver, driver_user_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # Get assignments for the period
        start_date = date.today() - timedelta(days=months * 30)
        assignments = await self.assignment_service.get_assignments(
            driver_id=driver_user_id,
            start_date=start_date
        )
        
        # Calculate metrics
        total_assignments = len(assignments)
        completed_assignments = len([a for a in assignments if a.status == AssignmentStatus.COMPLETED])
        completion_rate = completed_assignments / total_assignments * 100 if total_assignments > 0 else 0
        
        # Calculate average rating
        rated_assignments = [a for a in assignments if a.customer_rating is not None]
        average_rating = sum(a.customer_rating for a in rated_assignments) / len(rated_assignments) if rated_assignments else None
        
        # Calculate on-time rate
        on_time_assignments = [a for a in assignments if a.is_on_time == True]
        on_time_rate = len(on_time_assignments) / total_assignments * 100 if total_assignments > 0 else 0
        
        # Get training info
        last_training = self.session.exec(
            select(DriverTrainingRecord)
            .where(DriverTrainingRecord.driver_id == driver_user_id)
            .order_by(DriverTrainingRecord.scheduled_date.desc())
        ).first()
        
        # Count expiring certificates
        expiring_certs = len(await self.get_driver_documents(driver_user_id))  # Simplified
        
        # Mock monthly trends
        monthly_trends = [
            {"month": "2024-01", "assignments": 12, "rating": 4.5, "on_time_rate": 95},
            {"month": "2024-02", "assignments": 15, "rating": 4.7, "on_time_rate": 98},
            {"month": "2024-03", "assignments": 18, "rating": 4.6, "on_time_rate": 92}
        ]
        
        return PerformanceMetrics(
            overall_score=driver.calculate_performance_score(),
            total_assignments=total_assignments,
            completed_assignments=completed_assignments,
            completion_rate=completion_rate,
            average_rating=average_rating,
            on_time_rate=on_time_rate,
            incident_count=driver.total_incidents,
            last_training_date=last_training.scheduled_date if last_training else None,
            certificates_expiring=expiring_certs,
            monthly_trends=monthly_trends
        )