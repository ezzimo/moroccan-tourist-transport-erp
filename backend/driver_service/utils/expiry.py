"""
Expiry tracking and alert utilities
"""
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from sqlmodel import Session, select
from models.driver import Driver
from models.driver_training import DriverTrainingRecord
from models.driver_document import DriverDocument
import logging

logger = logging.getLogger(__name__)


class ExpiryTracker:
    """Utility class for tracking and alerting on expiring items"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def check_license_expiry(self, alert_days: int = 30) -> List[Dict[str, Any]]:
        """Check for drivers with expiring licenses
        
        Args:
            alert_days: Number of days before expiry to alert
            
        Returns:
            List of drivers with expiring licenses
        """
        alert_date = date.today() + timedelta(days=alert_days)
        
        statement = select(Driver).where(
            Driver.license_expiry_date <= alert_date,
            Driver.license_expiry_date > date.today(),
            Driver.status.in_(["Active", "On Leave"])
        )
        
        expiring_drivers = self.session.exec(statement).all()
        
        alerts = []
        for driver in expiring_drivers:
            days_left = (driver.license_expiry_date - date.today()).days
            alerts.append({
                "driver_id": driver.id,
                "driver_name": driver.full_name,
                "license_number": driver.license_number,
                "expiry_date": driver.license_expiry_date,
                "days_remaining": days_left,
                "alert_type": "license_expiry",
                "severity": "critical" if days_left <= 7 else "warning"
            })
        
        return alerts
    
    def check_health_certificate_expiry(self, alert_days: int = 60) -> List[Dict[str, Any]]:
        """Check for drivers with expiring health certificates"""
        alert_date = date.today() + timedelta(days=alert_days)
        
        statement = select(Driver).where(
            Driver.health_certificate_expiry.is_not(None),
            Driver.health_certificate_expiry <= alert_date,
            Driver.health_certificate_expiry > date.today(),
            Driver.status.in_(["Active", "On Leave"])
        )
        
        expiring_drivers = self.session.exec(statement).all()
        
        alerts = []
        for driver in expiring_drivers:
            days_left = (driver.health_certificate_expiry - date.today()).days
            alerts.append({
                "driver_id": driver.id,
                "driver_name": driver.full_name,
                "expiry_date": driver.health_certificate_expiry,
                "days_remaining": days_left,
                "alert_type": "health_certificate_expiry",
                "severity": "high" if days_left <= 14 else "medium"
            })
        
        return alerts
    
    def check_training_certificate_expiry(self, alert_days: int = 30) -> List[Dict[str, Any]]:
        """Check for expiring training certificates"""
        alert_date = date.today() + timedelta(days=alert_days)
        
        statement = select(DriverTrainingRecord).where(
            DriverTrainingRecord.certificate_valid_until.is_not(None),
            DriverTrainingRecord.certificate_valid_until <= alert_date,
            DriverTrainingRecord.certificate_valid_until > date.today(),
            DriverTrainingRecord.certificate_issued == True
        )
        
        expiring_training = self.session.exec(statement).all()
        
        alerts = []
        for training in expiring_training:
            days_left = (training.certificate_valid_until - date.today()).days
            alerts.append({
                "training_id": training.id,
                "driver_id": training.driver_id,
                "training_type": training.training_type,
                "expiry_date": training.certificate_valid_until,
                "days_remaining": days_left,
                "alert_type": "training_certificate_expiry",
                "severity": "medium" if days_left <= 7 else "low"
            })
        
        return alerts
    
    def check_document_expiry(self, alert_days: int = 30) -> List[Dict[str, Any]]:
        """Check for expiring documents"""
        alert_date = date.today() + timedelta(days=alert_days)
        
        statement = select(DriverDocument).where(
            DriverDocument.expiry_date.is_not(None),
            DriverDocument.expiry_date <= alert_date,
            DriverDocument.expiry_date > date.today(),
            DriverDocument.status == "Approved"
        )
        
        expiring_documents = self.session.exec(statement).all()
        
        alerts = []
        for document in expiring_documents:
            days_left = (document.expiry_date - date.today()).days
            alerts.append({
                "document_id": document.id,
                "driver_id": document.driver_id,
                "document_type": document.document_type,
                "title": document.title,
                "expiry_date": document.expiry_date,
                "days_remaining": days_left,
                "alert_type": "document_expiry",
                "severity": "high" if days_left <= 7 else "medium"
            })
        
        return alerts
    
    def get_all_expiry_alerts(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all expiry alerts categorized by type"""
        return {
            "license_expiry": self.check_license_expiry(),
            "health_certificate_expiry": self.check_health_certificate_expiry(),
            "training_certificate_expiry": self.check_training_certificate_expiry(),
            "document_expiry": self.check_document_expiry()
        }


def check_expiry_alerts(session: Session) -> Dict[str, List[Dict[str, Any]]]:
    """Convenience function to check all expiry alerts"""
    tracker = ExpiryTracker(session)
    return tracker.get_all_expiry_alerts()


def get_expiring_items(session: Session, item_type: str, alert_days: int = 30) -> List[Dict[str, Any]]:
    """Get expiring items of a specific type
    
    Args:
        session: Database session
        item_type: Type of item ('license', 'health_cert', 'training', 'document')
        alert_days: Days before expiry to alert
    """
    tracker = ExpiryTracker(session)
    
    if item_type == "license":
        return tracker.check_license_expiry(alert_days)
    elif item_type == "health_cert":
        return tracker.check_health_certificate_expiry(alert_days)
    elif item_type == "training":
        return tracker.check_training_certificate_expiry(alert_days)
    elif item_type == "document":
        return tracker.check_document_expiry(alert_days)
    else:
        raise ValueError(f"Unknown item type: {item_type}")