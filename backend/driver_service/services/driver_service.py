"""
Driver service for driver management operations
"""
from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException, status
from models.driver import Driver, DriverStatus, LicenseType, EmploymentType
from schemas.driver import (
    DriverCreate, DriverUpdate, DriverResponse, DriverSummary, 
    DriverSearch, DriverPerformance
)
from typing import List, Optional
from datetime import datetime, date, timedelta
import uuid


class DriverService:
    """Service for handling driver operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_driver(self, driver_data: DriverCreate) -> DriverResponse:
        """Create a new driver"""
        # Check if license number already exists
        statement = select(Driver).where(Driver.license_number == driver_data.license_number)
        existing_driver = self.session.exec(statement).first()
        
        if existing_driver:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="License number already exists"
            )
        
        # Check if national ID already exists
        statement = select(Driver).where(Driver.national_id == driver_data.national_id)
        existing_driver = self.session.exec(statement).first()
        
        if existing_driver:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="National ID already exists"
            )
        
        # Create driver
        driver_dict = driver_data.model_dump()
        languages = driver_dict.pop("languages_spoken", [])
        
        driver = Driver(**driver_dict)
        driver.set_languages_list(languages)
        
        self.session.add(driver)
        self.session.commit()
        self.session.refresh(driver)
        
        return self._to_response(driver)
    
    async def get_driver(self, driver_id: uuid.UUID) -> DriverResponse:
        """Get driver by ID"""
        statement = select(Driver).where(Driver.id == driver_id)
        driver = self.session.exec(statement).first()
        
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        return self._to_response(driver)
    
    async def search_drivers(
        self, 
        search_criteria: DriverSearch, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[DriverResponse]:
        """Search drivers with multiple criteria"""
        statement = select(Driver)
        
        # Apply filters
        conditions = []
        
        if search_criteria.query:
            query_filter = or_(
                Driver.full_name.ilike(f"%{search_criteria.query}%"),
                Driver.license_number.ilike(f"%{search_criteria.query}%"),
                Driver.employee_id.ilike(f"%{search_criteria.query}%")
            )
            conditions.append(query_filter)
        
        if search_criteria.status:
            conditions.append(Driver.status == search_criteria.status)
        
        if search_criteria.employment_type:
            conditions.append(Driver.employment_type == search_criteria.employment_type)
        
        if search_criteria.license_type:
            conditions.append(Driver.license_type == search_criteria.license_type)
        
        if search_criteria.tour_guide_certified is not None:
            conditions.append(Driver.tour_guide_certified == search_criteria.tour_guide_certified)
        
        if search_criteria.first_aid_certified is not None:
            conditions.append(Driver.first_aid_certified == search_criteria.first_aid_certified)
        
        if search_criteria.available_for_assignment:
            conditions.extend([
                Driver.status == DriverStatus.ACTIVE,
                Driver.license_expiry_date > date.today(),
                or_(
                    Driver.health_certificate_expiry.is_(None),
                    Driver.health_certificate_expiry > date.today()
                )
            ])
        
        if search_criteria.license_expiring_soon:
            alert_date = date.today() + timedelta(days=30)
            conditions.append(Driver.license_expiry_date <= alert_date)
        
        if search_criteria.health_cert_expiring_soon:
            alert_date = date.today() + timedelta(days=60)
            conditions.append(
                and_(
                    Driver.health_certificate_expiry.is_not(None),
                    Driver.health_certificate_expiry <= alert_date
                )
            )
        
        if conditions:
            statement = statement.where(and_(*conditions))
        
        # Apply language filter if specified
        if search_criteria.languages:
            # This would require a more complex query for JSON field
            # For now, we'll filter in Python after the query
            pass
        
        statement = statement.offset(skip).limit(limit)
        drivers = self.session.exec(statement).all()
        
        # Filter by languages if specified
        if search_criteria.languages:
            filtered_drivers = []
            for driver in drivers:
                driver_languages = driver.get_languages_list()
                if any(lang.lower() in [dl.lower() for dl in driver_languages] for lang in search_criteria.languages):
                    filtered_drivers.append(driver)
            drivers = filtered_drivers
        
        return [self._to_response(driver) for driver in drivers]
    
    async def update_driver(self, driver_id: uuid.UUID, driver_data: DriverUpdate) -> DriverResponse:
        """Update driver information"""
        statement = select(Driver).where(Driver.id == driver_id)
        driver = self.session.exec(statement).first()
        
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # Update fields
        update_data = driver_data.model_dump(exclude_unset=True)
        languages = update_data.pop("languages_spoken", None)
        
        for field, value in update_data.items():
            setattr(driver, field, value)
        
        if languages is not None:
            driver.set_languages_list(languages)
        
        driver.updated_at = datetime.utcnow()
        
        self.session.add(driver)
        self.session.commit()
        self.session.refresh(driver)
        
        return self._to_response(driver)
    
    async def delete_driver(self, driver_id: uuid.UUID) -> dict:
        """Delete driver (soft delete by changing status)"""
        statement = select(Driver).where(Driver.id == driver_id)
        driver = self.session.exec(statement).first()
        
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        driver.status = DriverStatus.TERMINATED
        driver.updated_at = datetime.utcnow()
        
        self.session.add(driver)
        self.session.commit()
        
        return {"message": "Driver deleted successfully"}
    
    async def get_drivers_summary(self) -> DriverSummary:
        """Get driver statistics and summary"""
        # Total drivers
        total_drivers = self.session.exec(select(func.count(Driver.id))).first()
        
        # Active drivers
        active_drivers = self.session.exec(
            select(func.count(Driver.id)).where(Driver.status == DriverStatus.ACTIVE)
        ).first()
        
        # Drivers on leave
        drivers_on_leave = self.session.exec(
            select(func.count(Driver.id)).where(Driver.status == DriverStatus.ON_LEAVE)
        ).first()
        
        # Suspended drivers
        suspended_drivers = self.session.exec(
            select(func.count(Driver.id)).where(Driver.status == DriverStatus.SUSPENDED)
        ).first()
        
        # License expiring soon (30 days)
        alert_date = date.today() + timedelta(days=30)
        license_expiring_soon = self.session.exec(
            select(func.count(Driver.id)).where(Driver.license_expiry_date <= alert_date)
        ).first()
        
        # Health cert expiring soon (60 days)
        health_alert_date = date.today() + timedelta(days=60)
        health_cert_expiring_soon = self.session.exec(
            select(func.count(Driver.id)).where(
                and_(
                    Driver.health_certificate_expiry.is_not(None),
                    Driver.health_certificate_expiry <= health_alert_date
                )
            )
        ).first()
        
        # By employment type
        employment_types = self.session.exec(
            select(Driver.employment_type, func.count(Driver.id)).group_by(Driver.employment_type)
        ).all()
        by_employment_type = {et[0].value: et[1] for et in employment_types}
        
        # By license type
        license_types = self.session.exec(
            select(Driver.license_type, func.count(Driver.id)).group_by(Driver.license_type)
        ).all()
        by_license_type = {lt[0].value: lt[1] for lt in license_types}
        
        # Average performance rating
        avg_rating = self.session.exec(
            select(func.avg(Driver.performance_rating)).where(Driver.performance_rating.is_not(None))
        ).first()
        
        # Total tours and incidents
        total_tours = self.session.exec(select(func.sum(Driver.total_tours_completed))).first() or 0
        total_incidents = self.session.exec(select(func.sum(Driver.total_incidents))).first() or 0
        
        return DriverSummary(
            total_drivers=total_drivers or 0,
            active_drivers=active_drivers or 0,
            drivers_on_leave=drivers_on_leave or 0,
            suspended_drivers=suspended_drivers or 0,
            license_expiring_soon=license_expiring_soon or 0,
            health_cert_expiring_soon=health_cert_expiring_soon or 0,
            by_employment_type=by_employment_type,
            by_license_type=by_license_type,
            average_performance_rating=float(avg_rating) if avg_rating else 0.0,
            total_tours_completed=total_tours,
            total_incidents=total_incidents
        )
    
    async def get_expiring_licenses(self, days: int) -> List[DriverResponse]:
        """Get drivers with licenses expiring within specified days"""
        alert_date = date.today() + timedelta(days=days)
        statement = select(Driver).where(
            and_(
                Driver.license_expiry_date <= alert_date,
                Driver.license_expiry_date > date.today()
            )
        ).order_by(Driver.license_expiry_date)
        
        drivers = self.session.exec(statement).all()
        return [self._to_response(driver) for driver in drivers]
    
    async def get_expiring_health_certificates(self, days: int) -> List[DriverResponse]:
        """Get drivers with health certificates expiring within specified days"""
        alert_date = date.today() + timedelta(days=days)
        statement = select(Driver).where(
            and_(
                Driver.health_certificate_expiry.is_not(None),
                Driver.health_certificate_expiry <= alert_date,
                Driver.health_certificate_expiry > date.today()
            )
        ).order_by(Driver.health_certificate_expiry)
        
        drivers = self.session.exec(statement).all()
        return [self._to_response(driver) for driver in drivers]
    
    async def get_driver_performance(self, driver_id: uuid.UUID) -> DriverPerformance:
        """Get driver performance metrics"""
        driver = await self.get_driver(driver_id)
        
        # This would typically involve complex queries across assignments, incidents, etc.
        # For now, we'll return basic metrics from the driver record
        return DriverPerformance(
            driver_id=driver_id,
            driver_name=driver.full_name,
            total_assignments=driver.total_tours_completed,
            completed_assignments=driver.total_tours_completed,
            completion_rate=100.0 if driver.total_tours_completed > 0 else 0.0,
            average_customer_rating=driver.performance_rating,
            total_incidents=driver.total_incidents,
            incident_rate=driver.total_incidents / max(driver.total_tours_completed, 1),
            on_time_rate=95.0,  # This would be calculated from assignment data
            performance_score=driver.performance_score,
            last_assignment_date=None  # This would come from assignment data
        )
    
    def _to_response(self, driver: Driver) -> DriverResponse:
        """Convert driver model to response schema"""
        return DriverResponse(
            id=driver.id,
            full_name=driver.full_name,
            date_of_birth=driver.date_of_birth,
            gender=driver.gender,
            nationality=driver.nationality,
            national_id=driver.national_id,
            phone=driver.phone,
            email=driver.email,
            address=driver.address,
            emergency_contact_name=driver.emergency_contact_name,
            emergency_contact_phone=driver.emergency_contact_phone,
            employee_id=driver.employee_id,
            employment_type=driver.employment_type,
            hire_date=driver.hire_date,
            license_number=driver.license_number,
            license_type=driver.license_type,
            license_issue_date=driver.license_issue_date,
            license_expiry_date=driver.license_expiry_date,
            license_issuing_authority=driver.license_issuing_authority,
            languages_spoken=driver.get_languages_list(),
            health_certificate_expiry=driver.health_certificate_expiry,
            medical_restrictions=driver.medical_restrictions,
            tour_guide_certified=driver.tour_guide_certified,
            first_aid_certified=driver.first_aid_certified,
            status=driver.status,
            performance_rating=driver.performance_rating,
            total_tours_completed=driver.total_tours_completed,
            total_incidents=driver.total_incidents,
            profile_photo_path=driver.profile_photo_path,
            notes=driver.notes,
            created_at=driver.created_at,
            updated_at=driver.updated_at,
            age=driver.get_age(),
            years_of_service=driver.get_years_of_service(),
            is_license_expired=driver.is_license_expired(),
            days_until_license_expiry=driver.days_until_license_expiry(),
            is_health_cert_expired=driver.is_health_cert_expired(),
            days_until_health_cert_expiry=driver.days_until_health_cert_expiry(),
            performance_score=driver.calculate_performance_score(),
            is_available_for_assignment=driver.is_available_for_assignment()
        )